import json
import boto3
import uuid
from datetime import datetime
import os

dynamodb = boto3.resource('dynamodb')
threads_table = dynamodb.Table(os.environ['DDB_THREADS'])

def handler(event, context):
    """
    POST /thread/start
    Input: { goal, repo?, branch? }
    Write to copidock-threads; return { thread_id, thread_name }
    """
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        goal = body.get('goal', '').strip()
        repo = body.get('repo', '').strip()
        branch = body.get('branch', 'main').strip()
        
        if not goal:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Goal is required'})
            }
        
        # Generate thread ID and name
        thread_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        # Create descriptive thread name from goal (first 50 chars, safe for filenames)
        thread_name = ''.join(c for c in goal[:50] if c.isalnum() or c in (' ', '-', '_')).strip()
        if not thread_name:
            thread_name = f"thread-{datetime.utcnow().strftime('%Y%m%d-%H%M')}"
        
        # Create thread record
        thread_item = {
            'thread_id': thread_id,
            'thread_name': thread_name,
            'goal': goal,
            'repo': repo,
            'branch': branch,
            'created_at': timestamp,
            'updated_at': timestamp,
            'status': 'active',
            'snapshot_count': 0
        }
        
        # Save to DynamoDB
        threads_table.put_item(Item=thread_item)
        
        # Return success response
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key'
            },
            'body': json.dumps({
                'thread_id': thread_id,
                'thread_name': thread_name,
                'goal': goal,
                'repo': repo,
                'branch': branch,
                'created_at': timestamp
            })
        }
        
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Invalid JSON in request body'})
        }
    except Exception as e:
        print(f"Error creating thread: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }