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
    Handle both:
    POST /snapshot (existing)
    POST /snapshot/comprehensive (new)
    """
    try:
        # Check the path to determine which handler to use
        path = event.get('path', '')
        
        if path.endswith('/comprehensive'):
            return handle_comprehensive_snapshot(event, context)
        else:
            return handle_regular_snapshot(event, context)
            
    except Exception as e:
        print(f"Error in snapshot handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }

def handle_regular_snapshot(event, context):
    """
    POST /snapshot (existing logic)
    Input: { thread_id, paths?, message? }
    """
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        thread_id = body.get('thread_id', '').strip()
        paths = body.get('paths', [])
        message = body.get('message', '')
        
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
        
        # Atomically increment snapshot_count
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
        
        # Gather sources from paths
        sources = gather_sources(thread_id, paths)
        
        # Create S3 key
        s3_key = f"threads/{thread_id}/{date_str}/snapshot-v{version:03d}.md"
        
        # Generate rehydratable markdown
        markdown_content = generate_rehydratable_markdown(
            thread=thread,
            sources=sources,
            snapshot_id=snapshot_id,
            timestamp=timestamp,
            version=version,
            message=message
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
                'created-at': timestamp.isoformat(),
                'type': 'regular'
            }
        )
        
        # Update thread with latest snapshot key
        threads_table.update_item(
            Key={'thread_id': thread_id},
            UpdateExpression='SET latest_snapshot_key = :key',
            ExpressionAttributeValues={':key': s3_key}
        )
        
        # Generate presigned URL
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
                'created_at': timestamp.isoformat() + 'Z',
                'type': 'regular',
                'sources_count': len(sources)
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

def handle_comprehensive_snapshot(event, context):
    """
    POST /snapshot/comprehensive (new)
    Input: { thread_id, inline_sources, synth, message? }
    """
    try:
        # Parse request body
        body = json.loads(event.get('body', '{}'))
        thread_id = body.get('thread_id', '').strip()
        inline_sources = body.get('inline_sources', [])
        synth_sections = body.get('synth', {})
        message = body.get('message', '')
        
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
        
        # Atomically increment snapshot_count
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
        
        # Create S3 key for comprehensive snapshot
        s3_key = f"threads/{thread_id}/{date_str}/comprehensive-v{version:03d}.md"
        
        # Generate comprehensive rehydratable markdown
        markdown_content = generate_comprehensive_markdown(
            thread=thread,
            inline_sources=inline_sources,
            synth_sections=synth_sections,
            snapshot_id=snapshot_id,
            timestamp=timestamp,
            version=version,
            message=message
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
                'created-at': timestamp.isoformat(),
                'type': 'comprehensive'
            }
        )
        
        # Update thread with latest snapshot key
        threads_table.update_item(
            Key={'thread_id': thread_id},
            UpdateExpression='SET latest_snapshot_key = :key',
            ExpressionAttributeValues={':key': s3_key}
        )
        
        # Generate presigned URL
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
                'created_at': timestamp.isoformat() + 'Z',
                'type': 'comprehensive',
                'sources_count': len(inline_sources),
                'synthesis_sections': list(synth_sections.keys())
            })
        }
        
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Invalid JSON in request body'})
        }
    except Exception as e:
        print(f"Error creating comprehensive snapshot: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Internal server error'})
        }

def gather_sources(thread_id, paths):
    """Gather source content from various sources"""
    sources = []
    
    if paths:
        # Handle file paths (existing functionality)
        for path in paths[:20]:  # Limit to prevent oversized payloads
            sources.append({
                'type': 'file_path',
                'path': path,
                'content': f"File path: {path}"
            })
    
    return sources

def generate_rehydratable_markdown(thread, sources, snapshot_id, timestamp, version, message=""):
    """Generate regular rehydratable markdown (existing functionality)"""
    iso_timestamp = timestamp.isoformat() + 'Z'
    
    goal = thread.get('goal', 'development task')
    repo = thread.get('repo', 'unknown')
    branch = thread.get('branch', 'main')
    
    content = f"""---
thread_id: {thread['thread_id']}
snapshot_id: {snapshot_id}
version: {version}
created_at: {iso_timestamp}
repo: {repo}
branch: {branch}
goal: "{goal}"
context_tags: ["snapshot"]
token_budget_hint: 4k
---

# Rehydrate: {thread.get('thread_name', 'Development Thread')} (v{version})

"""
    
    if message:
        content += f"**Message:** {message}\n\n"
    
    content += "## Operator Instructions\n\n"
    content += f"You are working on: {goal}\n\n"
    
    content += "## Current State\n\n"
    content += f"Thread: {thread['thread_id']}\n"
    content += f"Repository: {repo}\n"
    content += f"Branch: {branch}\n\n"
    
    if sources:
        content += "## Sources\n\n"
        for i, source in enumerate(sources, 1):
            content += f"### Source {i}: {source.get('path', 'unknown')}\n\n"
            content += f"{source.get('content', 'No content available')}\n\n"
    
    return content

def generate_comprehensive_markdown(thread, inline_sources, synth_sections, snapshot_id, timestamp, version, message=""):
    """Generate comprehensive rehydratable markdown with synthesis sections"""
    
    iso_timestamp = timestamp.isoformat() + 'Z'
    
    goal = thread.get('goal', 'development task')
    repo = thread.get('repo', 'unknown')
    branch = thread.get('branch', 'main')
    
    # Extract file paths for related_paths
    related_paths = [source['path'] for source in inline_sources[:10]]  # Limit to first 10
    
    content = f"""---
thread_id: {thread['thread_id']}
snapshot_id: {snapshot_id}
version: {version}
created_at: {iso_timestamp}
repo: {repo}
branch: {branch}
goal: "{goal}"
context_tags: ["snapshot","rehydration","comprehensive"]
related_paths:"""

    # Add related paths as YAML list
    for path in related_paths:
        content += f"\n  - {path}"
    
    content += f"""
token_budget_hint: 6k
---

# Rehydrate: {thread.get('thread_name', 'Development Thread')} (v{version})

"""

    # Add message if provided
    if message:
        content += f"**Message:** {message}\n\n"
    
    # Add synthesized sections
    if synth_sections.get('operator_instructions'):
        content += synth_sections['operator_instructions'] + "\n\n"
    
    if synth_sections.get('current_state'):
        content += synth_sections['current_state'] + "\n\n"
    
    if synth_sections.get('decisions_constraints'):
        content += synth_sections['decisions_constraints'] + "\n\n"
    
    if synth_sections.get('open_questions'):
        content += synth_sections['open_questions'] + "\n\n"
    
    # Add sources section
    content += "## Sources\n\n"
    
    for i, source in enumerate(inline_sources, 1):
        path = source.get('path', f'source-{i}')
        language = source.get('language', 'text')
        source_content = source.get('content', '')
        
        content += f"### Source {i}: {path}\n\n"
        content += f"````{language}\n"
        content += f"// filepath: {path}\n"
        content += source_content
        content += "\n````\n\n"
    
    # Add footer
    content += """---

*This is a comprehensive rehydratable snapshot with auto-generated synthesis sections. It contains the context, analysis, and state needed to continue this development thread.*
"""

    return content