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
    MAX_NOTE_LEN = 200 * 1024  # 200KB limit
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
    
# Add this function after create_note()
def get_notes(event):
    """Retrieve notes with optional filtering"""
    try:
        # Parse query parameters
        query_params = event.get('queryStringParameters') or {}
        thread_id = query_params.get('thread_id', '')
        limit = int(query_params.get('limit', '50'))
        
        # Limit the number of results
        if limit > 100:
            limit = 100
        
        try:
            if thread_id:
                # Query notes for specific thread
                response = chunks_table.query(
                    IndexName='ThreadIndex',  # Assumes you have a GSI on thread_id
                    KeyConditionExpression=Key('thread_id').eq(thread_id) & Key('ns').eq('notes'),
                    Limit=limit,
                    ScanIndexForward=False  # Most recent first
                )
            else:
                # Get all notes (scan operation)
                response = chunks_table.scan(
                    FilterExpression=Key('ns').eq('notes'),
                    Limit=limit
                )
            
            notes = []
            for item in response.get('Items', []):
                notes.append({
                    'note_id': item.get('id'),
                    'content': item.get('content'),
                    'tags': item.get('tags', []),
                    'thread_id': item.get('thread_id'),
                    'created_at': item.get('created_at'),
                    'type': item.get('type')
                })
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key'
                },
                'body': json.dumps({
                    'notes': notes,
                    'count': len(notes),
                    'has_more': len(response.get('Items', [])) == limit
                })
            }
            
        except Exception as db_error:
            # If GSI doesn't exist, fall back to scan
            print(f"Database query error (falling back to scan): {str(db_error)}")
            response = chunks_table.scan(
                FilterExpression=Key('ns').eq('notes'),
                Limit=limit
            )
            
            notes = []
            for item in response.get('Items', []):
                if not thread_id or item.get('thread_id') == thread_id:
                    notes.append({
                        'note_id': item.get('id'),
                        'content': item.get('content'),
                        'tags': item.get('tags', []),
                        'thread_id': item.get('thread_id'),
                        'created_at': item.get('created_at'),
                        'type': item.get('type')
                    })
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key'
                },
                'body': json.dumps({
                    'notes': notes,
                    'count': len(notes)
                })
            }
        
    except Exception as e:
        print(f"Error retrieving notes: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }