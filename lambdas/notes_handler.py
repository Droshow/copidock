import json
import boto3
import uuid
import os
from datetime import datetime
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
chunks_table = dynamodb.Table(os.environ['DDB_CHUNKS_TABLE'])

def handler(event, context):
    """
    POST /notes - Store new notes
    GET /notes - Retrieve notes
    """
    http_method = event.get('httpMethod', event.get('requestContext', {}).get('http', {}).get('method', ''))
    
    if http_method == 'POST':
        return create_note(event)
    elif http_method == 'GET':
        return get_notes(event)
    else:
        return {
            'statusCode': 405,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Method not allowed'})
        }

def create_note(event):
    """Create a new note"""
    try:
        body = json.loads(event.get('body', '{}'))
        content = body.get('content', '').strip()
        tags = body.get('tags', [])
        thread_id = body.get('thread_id', '')
        
        if not content:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Content is required'})
            }
        
        # Guard against oversized notes
        if len(content.encode("utf-8")) > MAX_NOTE_LEN:
            return {
                'statusCode': 413,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({'error': 'Note too large (max 200KB)'})
            }
        
        # Generate note ID and timestamp
        note_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat() + 'Z'
        
        # Store as a chunk in DynamoDB
        note_item = {
            'ns': 'notes',
            'sort': f"{timestamp}#{note_id}",
            'id': note_id,
            'content': content,
            'tags': tags,
            'thread_id': thread_id,
            'created_at': timestamp,
            'type': 'note',
            'source': 'manual_entry'
        }
        
        chunks_table.put_item(Item=note_item)
        
        return {
            'statusCode': 201,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key'
            },
            'body': json.dumps({
                'note_id': note_id,
                'content': content,
                'tags': tags,
                'thread_id': thread_id,
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
        print(f"Error creating note: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }