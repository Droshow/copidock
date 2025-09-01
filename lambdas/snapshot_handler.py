import json
import boto3
import os
import uuid
from datetime import datetime
from botocore.exceptions import ClientError

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

bucket_name = os.environ['BUCKET_NAME']
threads_table = dynamodb.Table(os.environ['DDB_THREADS'])
chunks_table = dynamodb.Table(os.environ['DDB_CHUNKS_TABLE'])

def handler(event, context):
    """
    POST /snapshot
    Input: { thread_id, paths? }
    Gather sources, create rehydratable.md, save to S3, return presigned URL
    """
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        thread_id = body.get('thread_id', '').strip()
        paths = body.get('paths', [])
        
        if not thread_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'thread_id is required'})
            }
        
        # Get thread details
        thread_response = threads_table.get_item(Key={'thread_id': thread_id})
        if 'Item' not in thread_response:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Thread not found'})
            }
        
        thread = thread_response['Item']
        
        # Generate snapshot metadata
        snapshot_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        date_str = timestamp.strftime('%Y-%m-%d')
        
        # Atomically increment snapshot_count and get the new version
        try:
            update_response = threads_table.update_item(
                Key={'thread_id': thread_id},
                UpdateExpression='ADD snapshot_count :inc SET updated_at = :updated',
                ExpressionAttributeValues={
                    ':inc': 1,
                    ':updated': timestamp.isoformat() + 'Z'
                },
                ReturnValues='ALL_NEW'
            )
            version = int(update_response['Attributes']['snapshot_count'])
        except Exception as e:
            print(f"Error incrementing snapshot count: {e}")
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Failed to create snapshot version'})
            }
        
        # Create S3 key for snapshot
        s3_key = f"threads/{thread_id}/{date_str}/v{version:03d}.md"
        
        # Gather source content
        sources_content = gather_sources(thread_id, paths)
        
        # Generate rehydratable markdown
        markdown_content = generate_rehydratable_markdown(
            thread=thread,
            sources=sources_content,
            snapshot_id=snapshot_id,
            timestamp=timestamp,
            version=version
        )
        
        # Save to S3
        s3.put_object(
            Bucket=bucket_name,
            Key=s3_key,
            Body=markdown_content.encode('utf-8'),
            ContentType='text/markdown',
            Metadata={
                'thread-id': thread_id,
                'snapshot-id': snapshot_id,
                'version': str(version),
                'created-at': timestamp.isoformat()
            }
        )
        
        # Update thread with latest snapshot key
        threads_table.update_item(
            Key={'thread_id': thread_id},
            UpdateExpression='SET latest_snapshot_key = :key',
            ExpressionAttributeValues={
                ':key': s3_key
            }
        )
        
        # Generate presigned URL (valid for 30 minutes)
        presigned_url = s3.generate_presigned_url(
            'get_object',
            Params={'Bucket': bucket_name, 'Key': s3_key},
            ExpiresIn=1800
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key'
            },
            'body': json.dumps({
                'snapshot_id': snapshot_id,
                'thread_id': thread_id,
                'version': version,
                's3_key': s3_key,
                'presigned_url': presigned_url,
                'created_at': timestamp.isoformat() + 'Z'
            })
        }
        
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Invalid JSON in request body'})
        }
    except Exception as e:
        print(f"Error creating snapshot: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }

def gather_sources(thread_id, paths):
    """Gather source content from various sources"""
    sources = []
    
    # Query chunks related to this thread or general context
    try:
        # Look for chunks in DynamoDB (simplified example)
        response = chunks_table.scan(
            FilterExpression='contains(#content, :thread_id) OR #ns = :general',
            ExpressionAttributeNames={
                '#content': 'content',
                '#ns': 'ns'
            },
            ExpressionAttributeValues={
                ':thread_id': thread_id,
                ':general': 'general'
            },
            Limit=20  # Limit to prevent timeout
        )
        
        for item in response.get('Items', []):
            sources.append({
                'type': 'chunk',
                'source': item.get('source', 'unknown'),
                'content': item.get('content', '')[:1000]  # Truncate for snapshot
            })
    except Exception as e:
        print(f"Error gathering chunks: {e}")
    
    # Add provided paths as sources
    for path in paths:
        sources.append({
            'type': 'file',
            'source': path,
            'content': f"// File: {path}\n// Content would be loaded from actual file system"
        })
    
    return sources

def generate_rehydratable_markdown(thread, sources, snapshot_id, timestamp, version):
    """Generate the rehydratable markdown content"""
    
    content = f"""# {thread['thread_name']} - Snapshot v{version}

**Thread ID:** `{thread['thread_id']}`  
**Snapshot ID:** `{snapshot_id}`  
**Created:** {timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}  
**Goal:** {thread['goal']}

## Context

**Repository:** {thread.get('repo', 'Not specified')}  
**Branch:** {thread.get('branch', 'main')}  

## Decision Thread Goal

{thread['goal']}

## Sources and Context

"""

    # Add sources to the markdown
    for i, source in enumerate(sources, 1):
        content += f"### Source {i}: {source['source']}\n\n"
        content += f"**Type:** {source['type']}\n\n"
        content += "```\n"
        content += source['content']
        content += "\n```\n\n"
    
    content += """## Current State

<!-- Add current analysis, decisions, or progress here -->

## Next Steps

<!-- Add planned next steps or decisions to make -->

## Notes

<!-- Add any additional notes or context -->

---

*This is a rehydratable snapshot. It contains the context and state needed to continue this decision thread.*
"""

    return content