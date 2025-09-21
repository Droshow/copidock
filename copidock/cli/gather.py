import subprocess
import os
import glob
import re
from pathlib import Path
from typing import List, Tuple, Dict, Any
from datetime import datetime, timedelta

# File filtering constants
SKIP_EXTENSIONS = {'.log', '.cache', '.tmp', '.lock', '.pyc', '.pyo', '.pyd', '.so'}
SKIP_DIRECTORIES = {'node_modules', '.git', '__pycache__', '.pytest_cache', 'venv', '.venv', 'dist', 'build'}

def is_binary_file(filepath: str) -> bool:
    """Simple binary detection - check for null bytes"""
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(1024)
            return b'\0' in chunk
    except:
        return True  # Assume binary if can't read

def should_skip_file(path: str) -> bool:
    """Simple file filtering"""
    # Skip directories
    if any(skip_dir in path for skip_dir in SKIP_DIRECTORIES):
        return True
    
    # Skip file extensions
    if Path(path).suffix.lower() in SKIP_EXTENSIONS:
        return True
        
    return False

def safe_git_command(cmd: List[str], cwd: str, timeout: int = 10) -> str:
    """Execute git command safely"""
    try:
        result = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, 
            timeout=timeout, check=False
        )
        return result.stdout if result.returncode == 0 else ""
    except (subprocess.TimeoutExpired, OSError):
        return ""

def estimate_tokens(text: str) -> int:
    """Rough estimate: ~4 chars per token"""
    return len(text) // 4

def get_file_size_estimate(filepath: str, repo_root: str) -> int:
    """Get rough token estimate for a file without reading full content"""
    try:
        full_path = Path(repo_root) / filepath
        file_size = full_path.stat().st_size
        return file_size // 4  # Very rough token estimate from file size
    except:
        return 0

def list_changed_files(repo_root: str) -> List[str]:
    """Get list of changed files from git"""
    changed_files = []
    
    # Get staged files
    staged = safe_git_command(["git", "diff", "--cached", "--name-only"], repo_root)
    if staged:
        changed_files.extend(staged.strip().split('\n'))
    
    # Get modified files (unstaged)
    modified = safe_git_command(["git", "diff", "--name-only"], repo_root)
    if modified:
        changed_files.extend(modified.strip().split('\n'))
    
    # Get untracked files
    untracked = safe_git_command(["git", "ls-files", "--others", "--exclude-standard"], repo_root)
    if untracked:
        changed_files.extend(untracked.strip().split('\n'))
    
    # Remove duplicates and empty strings
    unique_files = list(set(f for f in changed_files if f.strip()))
    
    return unique_files

def filter_relevant_files(file_paths: List[str], repo_root: str) -> List[str]:
    """Filter files to only include relevant ones"""
    filtered = []
    
    for path in file_paths:
        # Skip based on path/extension rules
        if should_skip_file(path):
            continue
            
        full_path = Path(repo_root) / path
        
        # Skip if file doesn't exist
        if not full_path.exists():
            continue
            
        # Skip binary files
        if is_binary_file(str(full_path)):
            continue
            
        filtered.append(path)
    
    return filtered

def enforce_budget(file_paths: List[str], repo_root: str, max_tokens: int = 6000) -> List[str]:
    """Keep under token budget by limiting files"""
    total_tokens = 0
    filtered_paths = []
    
    # Sort by file size (smaller first) to include more files
    paths_with_size = [(path, get_file_size_estimate(path, repo_root)) for path in file_paths]
    paths_with_size.sort(key=lambda x: x[1])
    
    for path, estimated_tokens in paths_with_size:
        if total_tokens + estimated_tokens <= max_tokens:
            filtered_paths.append(path)
            total_tokens += estimated_tokens
        else:
            break  # Stop adding files once budget is reached
            
    return filtered_paths

def build_smart_paths(repo_root: str, max_tokens: int = 6000) -> Tuple[List[str], dict]:
    """Build list of relevant file paths from git changes with stats"""
    # Get changed files
    changed_files = list_changed_files(repo_root)
    
    # Filter relevant files
    relevant_files = filter_relevant_files(changed_files, repo_root)
    
    # Enforce token budget
    final_files = enforce_budget(relevant_files, repo_root, max_tokens)
    
    # Build stats
    stats = {
        "total_changed": len(changed_files),
        "after_filtering": len(relevant_files),
        "final_count": len(final_files),
        "skipped_binary": len([f for f in changed_files if is_binary_file(str(Path(repo_root) / f))]),
        "skipped_irrelevant": len(changed_files) - len(relevant_files)
    }
    
    return final_files, stats

def get_recent_commits(repo_root: str, limit: int = 5) -> List[Dict[str, Any]]:
    """Enhanced commit fetching with more metadata"""
    try:
        # Get commits with more detailed format
        result = subprocess.run(
            ["git", "log", f"--max-count={limit}", 
             "--pretty=format:%H|%s|%ar|%an|%ae|%B"],
            cwd=repo_root, capture_output=True, text=True, timeout=15
        )
        
        if result.returncode != 0:
            return []
        
        commits = []
        commit_entries = result.stdout.strip().split('\n\n')  # Split by empty lines
        
        for entry in commit_entries:
            if not entry.strip():
                continue
                
            lines = entry.split('\n')
            if not lines:
                continue
                
            # Parse the first line with commit info
            first_line = lines[0]
            parts = first_line.split('|')
            
            if len(parts) >= 4:
                # Get commit body (everything after first line)
                body_lines = lines[1:] if len(lines) > 1 else []
                body = '\n'.join(body_lines).strip()
                
                commit_data = {
                    'hash': parts[0],
                    'subject': parts[1],
                    'time_ago': parts[2],
                    'author': parts[3],
                    'email': parts[4] if len(parts) > 4 else '',
                    'body': body
                }
                
                # Add commit analysis
                commit_data.update(analyze_single_commit(commit_data))
                commits.append(commit_data)
        
        return commits[:limit]
        
    except Exception as e:
        print(f"Error fetching commits: {e}")
        return []

def analyze_single_commit(commit: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze a single commit for additional metadata"""
    subject = commit['subject'].lower()
    full_text = f"{commit['subject']} {commit.get('body', '')}".lower()
    
    analysis = {
        'type': 'other',
        'scope': [],
        'breaking_change': False,
        'closes_issue': False
    }
    
    # Determine commit type
    if any(word in subject for word in ['fix', 'bug', 'error', 'issue']):
        analysis['type'] = 'fix'
    elif any(word in subject for word in ['feat', 'feature', 'add', 'implement']):
        analysis['type'] = 'feat'
    elif any(word in subject for word in ['refactor', 'cleanup', 'improve']):
        analysis['type'] = 'refactor'
    elif any(word in subject for word in ['test', 'spec', 'coverage']):
        analysis['type'] = 'test'
    elif any(word in subject for word in ['doc', 'readme', 'comment']):
        analysis['type'] = 'docs'
    elif any(word in subject for word in ['config', 'setup', 'env', 'deploy']):
        analysis['type'] = 'config'
    
    # Check for scope indicators
    scope_patterns = {
        'api': ['api', 'endpoint', 'route', 'server'],
        'ui': ['ui', 'frontend', 'component', 'css', 'html'],
        'db': ['database', 'db', 'migration', 'schema'],
        'auth': ['auth', 'login', 'security', 'token'],
        'infra': ['infra', 'deploy', 'terraform', 'aws', 'docker']
    }
    
    for scope, keywords in scope_patterns.items():
        if any(keyword in full_text for keyword in keywords):
            analysis['scope'].append(scope)
    
    # Check for breaking changes
    analysis['breaking_change'] = any(indicator in full_text for indicator in 
                                    ['breaking', 'breaking change', 'major', '!'])
    
    # Check for issue closure
    analysis['closes_issue'] = bool(re.search(r'(?:close|closes|fix|fixes|resolve|resolves)\s+#?\d+', 
                                            full_text, re.IGNORECASE))
    
    return analysis

def find_important_files(repo_root: str) -> List[str]:
    """Find always-important files using glob patterns"""
    patterns = [
        "infra/*.tf", "infra/*.yml", "infra/*.yaml",
        "lambdas/*", "lambda/*",
        "package.json", "requirements.txt", "setup.py", "pyproject.toml",
        "Makefile", "Dockerfile", "docker-compose.yml",
        ".github/workflows/*", "*.md"
    ]
    
    important_files = []
    repo_path = Path(repo_root)
    
    for pattern in patterns:
        matches = glob.glob(str(repo_path / pattern), recursive=True)
        for match in matches:
            # Convert to relative path
            rel_path = Path(match).relative_to(repo_path)
            important_files.append(str(rel_path))
    
    # Remove duplicates and filter existing files
    unique_files = []
    for file_path in set(important_files):
        full_path = repo_path / file_path
        if full_path.exists() and full_path.is_file():
            unique_files.append(file_path)
    
    return unique_files

def gather_comprehensive(repo_root: str, thread_id: str, max_tokens: int = 6000) -> Tuple[List[str], List[Dict[str, Any]], List[str]]:
    """Extended gathering for comprehensive snapshots"""
    # 1. Git changes (existing MVP logic)
    changed_files, _ = build_smart_paths(repo_root, max_tokens // 2)
    
    # 2. Important files (always include if not already in changed_files)
    important_files = find_important_files(repo_root)
    
    # Combine and deduplicate
    all_candidates = list(set(changed_files + important_files))
    
    # Apply filtering and budget to combined list
    filtered_candidates = filter_relevant_files(all_candidates, repo_root)
    final_files = enforce_budget(filtered_candidates, repo_root, max_tokens)
    
    # 3. Recent commits (for context)
    recent_commits = get_recent_commits(repo_root, limit=5)
    
    # 4. Thread notes (placeholder for now - will integrate with backend later)
    notes = []  # TODO: fetch_thread_notes(thread_id)
    
    return final_files, recent_commits, notes