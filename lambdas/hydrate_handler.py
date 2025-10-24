import json
import boto3
import uuid
import os
from datetime import datetime
from botocore.exceptions import ClientError

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

bucket_name = os.environ['BUCKET_NAME']
threads_table = dynamodb.Table(os.environ['DDB_THREADS'])

def handler(event, context):
    """
    POST /snapshots/{thread_id}/hydrate
    Save comprehensive snapshot markdown to S3 for rehydration
    """
    try:
        # Extract thread ID from path parameters
        path_params = event.get('pathParameters', {}) or {}
        thread_id = (path_params.get('thread_id') or '').strip()
        
        if not thread_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'thread_id parameter is required'})
            }
        
        # Parse request body
        try:
            body = json.loads(event.get('body', '{}'))
            markdown_content = body.get('markdown_content', '')
            metadata = body.get('metadata', {})
        except json.JSONDecodeError:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Invalid JSON in request body'})
            }
        
        if not markdown_content:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'markdown_content is required'})
            }
        
        # Generate rehydration ID
        rehydration_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().strftime('%Y%m%d-%H%M%S')
        
        # Create S3 key for the markdown file
        s3_key = f"rehydrations/{thread_id}/{rehydration_id}-{timestamp}.md"
        
        # Prepare S3 metadata
        s3_metadata = {
            'thread-id': thread_id,
            'rehydration-id': rehydration_id,
            'created-at': datetime.utcnow().isoformat(),
            'persona': metadata.get('persona', 'senior-backend-dev'),
            'focus': metadata.get('focus', ''),
            'output': metadata.get('output', ''),
            'constraints': metadata.get('constraints', ''),
            'file-count': str(metadata.get('file_count', 0)),
            'commit-count': str(metadata.get('commit_count', 0))
        }
        
        # Save markdown to S3
        s3.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=markdown_content,
            ContentType='text/markdown',
            Metadata=s3_metadata
        )
        
        # Update thread record with latest rehydration info
        try:
            threads_table.update_item(
                Key={'thread_id': thread_id},
                UpdateExpression='SET latest_rehydration_id = :rid, latest_rehydration_key = :key, updated_at = :updated',
                ExpressionAttributeValues={
                    ':rid': rehydration_id,
                    ':key': s3_key,
                    ':updated': datetime.utcnow().isoformat()
                }
            )
        except ClientError as e:
            print(f"Warning: Could not update thread record: {e}")
            # Don't fail the request if DynamoDB update fails
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key'
            },
            'body': json.dumps({
                'rehydration_id': rehydration_id,
                'thread_id': thread_id,
                's3_key': s3_key,
                'message': 'Snapshot hydrated successfully',
                'metadata': metadata
            })
        }
        
    except Exception as e:
        print(f"Error hydrating snapshot: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }
# hydrate_handler.py
import json, os, uuid
from datetime import datetime
import boto3

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

BUCKET = os.environ['BUCKET_NAME']
THREADS = dynamodb.Table(os.environ['DDB_THREADS'])

def _clean_repo(name: str) -> str:
    if not name:
        return "current-project"
    name = name.strip().lower().replace('.git', '')
    for ch in ('/', ' ', '\\'):
        name = name.replace(ch, '-')
    return name or "current-project"

def _stage(s: str) -> str:
    s = (s or '').strip().lower()
    return s if s in ('initial', 'development') else 'development'

def _s3_key(stage: str, repo: str, ts: datetime, rehyd_id: str) -> str:
    short = rehyd_id[:8]
    stamp = ts.strftime('%Y%m%d-%H%M%S')
    # Hydration always stores a full markdown artifact (comprehensive-like)
    return f"rehydrations/{stage}/{repo}/{stamp}-comprehensive-{short}.md"

def handler(event, context):
    # POST /snapshots/{thread_id}/hydrate
    body = json.loads(event.get('body') or '{}')
    path_params = event.get('pathParameters') or {}
    thread_id = (path_params.get('thread_id') or body.get('thread_id') or '').strip()

    if not thread_id:
        return _bad(400, "thread_id is required")

    # Fetch thread for fallback values
    t = THREADS.get_item(Key={'thread_id': thread_id}).get('Item', {}) or {}

    # Extract metadata from payload (preferred) or thread
    meta = body.get('metadata') or {}
    stage = _stage(meta.get('stage') or t.get('stage'))
    repo  = _clean_repo(meta.get('repo') or t.get('repo'))

    md = body.get('markdown_content') or ''
    if not md.strip():
        return _bad(400, "markdown_content is required")

    rehyd_id = str(uuid.uuid4())
    now = datetime.utcnow()
    key = _s3_key(stage, repo, now, rehyd_id)

    s3.put_object(
        Bucket=BUCKET,
        Key=key,
        Body=md.encode('utf-8'),
        ContentType='text/markdown',
        Metadata={
            'thread-id': thread_id,
            'rehydration-id': rehyd_id,
            'stage': stage,
            'repo': repo
        }
    )

    # Optionally store the last hydrated key on the thread
    THREADS.update_item(
        Key={'thread_id': thread_id},
        UpdateExpression='SET latest_snapshot_key = :k, updated_at = :u, stage = :s, repo = :r',
        ExpressionAttributeValues={
            ':k': key, ':u': now.isoformat()+'Z', ':s': stage, ':r': repo
        }
    )

    url = s3.generate_presigned_url('get_object', Params={'Bucket': BUCKET, 'Key': key}, ExpiresIn=1800)

    return _ok({
        'rehydration_id': rehyd_id,
        'thread_id': thread_id,
        's3_key': key,
        'presigned_url': url,
        'stage': stage,
        'repo': repo
    })

def _ok(body):  return {'statusCode': 200, 'headers': _h(), 'body': json.dumps(body)}
def _bad(c,m):  return {'statusCode': c,   'headers': _h(), 'body': json.dumps({'error': m})}
def _h():
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key'
    }
