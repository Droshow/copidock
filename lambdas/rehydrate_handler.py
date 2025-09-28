import json
import boto3
import os
from botocore.exceptions import ClientError

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

bucket_name = os.environ['BUCKET_NAME']
threads_table = dynamodb.Table(os.environ['DDB_THREADS'])

def handler(event, context):
    """
    Handle both:
    - GET /rehydrate/{thread_id}/latest (existing presigned URL logic)
    - GET /snapshots/rehydrate/{rehydration_id} (new markdown content retrieval)
    """
    try:
        # DEBUG: Print the complete event to see what API Gateway sends
        print(f"DEBUG: Complete event received:")
        print(json.dumps(event, indent=2, default=str))
        
        path = event.get('path', '')
        path_params = event.get('pathParameters', {}) or {}
        route_key = event.get('routeKey', '')

        print(f"DEBUG: path = '{path}'")
        print(f"DEBUG: routeKey = '{route_key}'") 
        print(f"DEBUG: pathParameters = {path_params}")
        
        # Determine which endpoint is being called
        if '/snapshots/rehydrate/' in path or '/snapshots/rehydrate/' in route_key:
            print("DEBUG: Taking snapshots/rehydrate branch")
            return handle_rehydrate_by_id(path_params, event)
        else:
            print("DEBUG: Taking legacy rehydrate branch - THIS IS THE PROBLEM")
            return handle_rehydrate_latest(path_params, event)
            
    except Exception as e:
        print(f"Error in rehydrate handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }

def handle_rehydrate_by_id(path_params, event):
    """NEW: Get rehydration by specific rehydration_id - return markdown content"""
    rehydration_id = (path_params.get('rehydration_id') or '').strip()
    
    if not rehydration_id:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'rehydration_id parameter is required'})
        }
    
    # Search for the rehydration file in S3
    try:
        # List objects with the rehydration_id in the key
        response = s3.list_objects_v2(
            Bucket=bucket_name,
            Prefix=f"rehydrations/",
            MaxKeys=1000
        )
        
        # Find the matching file
        matching_key = None
        for obj in response.get('Contents', []):
            if rehydration_id in obj['Key']:
                matching_key = obj['Key']
                break
        
        if not matching_key:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Rehydration not found'})
            }
        
        # Get the markdown content and metadata
        obj_response = s3.get_object(Bucket=bucket_name, Key=matching_key)
        markdown_content = obj_response['Body'].read().decode('utf-8')
        metadata = obj_response.get('Metadata', {})
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key'
            },
            'body': json.dumps({
                'rehydration_id': rehydration_id,
                'thread_id': metadata.get('thread-id', ''),
                'markdown_content': markdown_content,
                'goal': metadata.get('goal', ''),
                'persona': metadata.get('persona', 'senior-backend-dev'),
                'focus': metadata.get('focus', ''),
                'output': metadata.get('output', ''),
                'constraints': metadata.get('constraints', ''),
                'created_at': metadata.get('created-at', ''),
                'file_count': int(metadata.get('file-count', 0)),
                'commit_count': int(metadata.get('commit-count', 0))
            })
        }
        
    except ClientError as e:
        if e.response['Error']['Code'] == 'NoSuchKey':
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Rehydration file not found'})
            }
        else:
            print(f"S3 error: {e}")
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Error retrieving rehydration file'})
            }

def handle_rehydrate_latest(path_params, event):
    """EXISTING: Get latest snapshot by thread_id - return presigned URL"""
    thread_id = (path_params.get('thread_id') or path_params.get('thread') or '').strip()
    
    if not thread_id:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'thread_id parameter is required'})
        }
    
    # Get thread details to find latest snapshot
    thread_response = threads_table.get_item(Key={'thread_id': thread_id})
    if 'Item' not in thread_response:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Thread not found'})
        }
    
    thread = thread_response['Item']
    latest_snapshot_key = thread.get('latest_snapshot_key')
    
    if not latest_snapshot_key:
        return {
            'statusCode': 404,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'No snapshots found for this thread'})
        }
    
    # Verify the file exists in S3
    try:
        s3.head_object(Bucket=bucket_name, Key=latest_snapshot_key)
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Latest snapshot file not found in S3'})
            }
        else:
            print(f"S3 error checking object: {e}")
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Error accessing snapshot file'})
            }
    
    # Generate presigned URL (valid for 30 minutes)
    presigned_url = s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': bucket_name, 'Key': latest_snapshot_key},
        ExpiresIn=1800
    )
    
    # Get file metadata
    try:
        metadata_response = s3.head_object(Bucket=bucket_name, Key=latest_snapshot_key)
        metadata = metadata_response.get('Metadata', {})
    except ClientError:
        metadata = {}
    
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key'
        },
        'body': json.dumps({
            'thread_id': thread_id,
            'thread_name': thread.get('thread_name', ''),
            'latest_snapshot_key': latest_snapshot_key,
            'presigned_url': presigned_url,
            'snapshot_metadata': {
                'version': metadata.get('version', 'unknown'),
                'created_at': metadata.get('created-at', 'unknown'),
                'snapshot_id': metadata.get('snapshot-id', 'unknown')
            },
            'expires_in': 1800
        })
    }