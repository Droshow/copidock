import subprocess
from pathlib import Path
from typing import List, Tuple

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