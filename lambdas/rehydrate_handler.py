import json
import boto3
import os
from boto3.dynamodb.conditions import Key

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

bucket_name = os.environ['BUCKET_NAME']
threads_table = dynamodb.Table(os.environ['DDB_THREADS'])

def handler(event, context):
    """
    GET /rehydrate/{thread}/latest
    Look up latest version in S3; return presigned URL
    """
    try:
        # Extract thread ID from path parameters
        path_params = event.get('pathParameters', {})
        thread_id = path_params.get('thread', '').strip()
        
        if not thread_id:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'thread parameter is required'})
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
        except s3.exceptions.NoSuchKey:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Latest snapshot file not found in S3'})
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
        except Exception:
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
        
    except Exception as e:
        print(f"Error retrieving latest snapshot: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }