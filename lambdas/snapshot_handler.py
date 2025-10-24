import json, os, uuid
from datetime import datetime
import boto3

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

BUCKET = os.environ['BUCKET_NAME']
THREADS = dynamodb.Table(os.environ['DDB_THREADS'])

def handler(event, context):
    try:
        path = (event.get('rawPath') or event.get('path') or '').lower()
        if path.endswith('/comprehensive'):
            return _handle_comprehensive(event)
        return _handle_regular(event)
    except Exception as e:
        print(f"Error in snapshot handler: {e}")
        return _bad(500, "Internal server error")


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

def _s3_key(stage: str, repo: str, ts: datetime, snap_id: str, kind: str) -> str:
    short = snap_id[:8]
    stamp = ts.strftime('%Y%m%d-%H%M%S')
    if kind == 'comprehensive':
        return f"rehydrations/{stage}/{repo}/{stamp}-comprehensive-{short}.md"
    return f"rehydrations/{stage}/{repo}/{stamp}-{short}.md"

def handler(event, context):
    path = (event.get('rawPath') or event.get('path') or '').lower()
    if path.endswith('/comprehensive'):
        return _handle_comprehensive(event)
    return _handle_regular(event)

def _handle_regular(event):
    body = json.loads(event.get('body') or '{}')
    thread_id = (body.get('thread_id') or '').strip()
    if not thread_id:
        return _bad(400, "thread_id is required")

    # Fetch thread (for fallback values)
    t = THREADS.get_item(Key={'thread_id': thread_id}).get('Item', {})
    stage = _stage(body.get('stage') or t.get('stage'))
    repo  = _clean_repo(body.get('repo') or t.get('repo'))

    snap_id = str(uuid.uuid4())
    now = datetime.utcnow()
    md = _minimal_markdown(thread=t, snapshot_id=snap_id, created_at=now, message=body.get('message', ''))

    key = _s3_key(stage, repo, now, snap_id, 'regular')
    s3.put_object(
        Bucket=BUCKET, Key=key, Body=md.encode('utf-8'),
        ContentType='text/markdown',
        Metadata={'thread-id': thread_id, 'snapshot-id': snap_id, 'type': 'regular', 'stage': stage, 'repo': repo}
    )

    # optional: update thread latest key
    THREADS.update_item(
        Key={'thread_id': thread_id},
        UpdateExpression='SET latest_snapshot_key = :k, updated_at = :u, stage = :s, repo = :r',
        ExpressionAttributeValues={':k': key, ':u': now.isoformat()+'Z', ':s': stage, ':r': repo}
    )

    url = s3.generate_presigned_url('get_object', Params={'Bucket': BUCKET, 'Key': key}, ExpiresIn=1800)
    return _ok({
        'snapshot_id': snap_id,
        'thread_id': thread_id,
        's3_key': key,
        'presigned_url': url,
        'type': 'regular',
        'stage': stage,
        'repo': repo
    })

def _handle_comprehensive(event):
    body = json.loads(event.get('body') or '{}')
    thread_id = (body.get('thread_id') or '').strip()
    if not thread_id:
        return _bad(400, "thread_id is required")

    t = THREADS.get_item(Key={'thread_id': thread_id}).get('Item', {})
    stage = _stage(body.get('stage') or t.get('stage'))
    repo  = _clean_repo(body.get('repo') or t.get('repo'))

    snap_id = str(uuid.uuid4())
    now = datetime.utcnow()

    # Build comprehensive markdown: synth + sources (simplified)
    synth = body.get('synth') or {}
    sources = body.get('inline_sources') or []
    md = _comprehensive_markdown(t, synth, sources, snap_id, now, body.get('message', ''))

    key = _s3_key(stage, repo, now, snap_id, 'comprehensive')
    s3.put_object(
        Bucket=BUCKET, Key=key, Body=md.encode('utf-8'),
        ContentType='text/markdown',
        Metadata={'thread-id': thread_id, 'snapshot-id': snap_id, 'type': 'comprehensive', 'stage': stage, 'repo': repo}
    )

    THREADS.update_item(
        Key={'thread_id': thread_id},
        UpdateExpression='SET latest_snapshot_key = :k, updated_at = :u, stage = :s, repo = :r',
        ExpressionAttributeValues={':k': key, ':u': now.isoformat()+'Z', ':s': stage, ':r': repo}
    )

    url = s3.generate_presigned_url('get_object', Params={'Bucket': BUCKET, 'Key': key}, ExpiresIn=1800)
    return _ok({
        'snapshot_id': snap_id,
        'thread_id': thread_id,
        's3_key': key,
        'presigned_url': url,
        'type': 'comprehensive',
        'stage': stage,
        'repo': repo,
        'sources_count': len(sources),
        'synth_keys': list(synth.keys())
    })

def _minimal_markdown(thread, snapshot_id, created_at, message):
    return f"""---
thread_id: {thread.get('thread_id','')}
snapshot_id: {snapshot_id}
version: 1
created_at: {created_at.isoformat()}Z
repo: {thread.get('repo','')}
branch: {thread.get('branch','main')}
goal: "{thread.get('goal','')}"
---

# Rehydrate: {thread.get('thread_name','Thread')}

{f"**Message:** {message}" if message else ""}
"""

def _comprehensive_markdown(thread, synth, sources, snapshot_id, created_at, message):
    header = _minimal_markdown(thread, snapshot_id, created_at, message)
    parts = [header]
    if synth.get('operator_instructions'): parts.append(synth['operator_instructions'])
    if synth.get('current_state'): parts.append(synth['current_state'])
    if synth.get('decisions_constraints'): parts.append(synth['decisions_constraints'])
    if synth.get('open_questions'): parts.append(synth['open_questions'])
    parts.append("## Sources\n")
    for i, s in enumerate(sources, 1):
        path = s.get('path', f'source-{i}')
        lang = s.get('language', 'text')
        content = s.get('content', '')
        parts.append(f"### Source {i}: {path}\n\n````{lang}\n// filepath: {path}\n{content}\n````\n")
    return "\n".join(parts)

def _ok(body: dict):
    return {'statusCode': 200, 'headers': _h(), 'body': json.dumps(body)}

def _bad(code: int, msg: str):
    return {'statusCode': code, 'headers': _h(), 'body': json.dumps({'error': msg})}

def _h():
    return {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key'
    }
