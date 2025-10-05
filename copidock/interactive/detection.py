"""Auto-detection and context analysis for intelligent snapshots"""

import subprocess
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime, timedelta
import re

def auto_detect_context(repo_root: Path, since: Optional[str] = None) -> Dict[str, Any]:
    """Auto-detect repository context for smart defaults"""
    
    # Get git information
    repo_info = get_repo_info(repo_root)
    
    # Analyze recent changes
    time_filter = since or "3 days"
    recent_commits = get_recent_commits(repo_root, time_filter)
    modified_files = get_modified_files(repo_root)
    
    # Detect focus areas from file patterns
    detected_focus = detect_focus_from_changes(modified_files, recent_commits)
    
    # Suggest output based on change patterns
    suggested_output = suggest_output_from_patterns(modified_files, recent_commits)
    
    # Detect constraints from repo characteristics
    detected_constraints = detect_constraints_from_repo(repo_root, modified_files)
    
    return {
        'repo': repo_info.get('name', ''),
        'branch': repo_info.get('branch', 'main'),
        'recent_commits': recent_commits[:3],  # Last 3 for context
        'modified_files': modified_files[:10],  # Top 10 for display
        'detected_focus': detected_focus,
        'suggested_output': suggested_output,
        'detected_constraints': detected_constraints,
        'file_count': len(modified_files),
        'commit_count': len(recent_commits)
    }

def get_repo_info(repo_root: Path) -> Dict[str, str]:
    """Get basic repository information"""
    try:
        # Get repo name from remote origin or directory name
        result = subprocess.run(
            ['git', 'remote', 'get-url', 'origin'], 
            cwd=repo_root, 
            capture_output=True, 
            text=True
        )
        
        if result.returncode == 0:
            # Extract repo name from URL
            url = result.stdout.strip()
            repo_name = url.split('/')[-1].replace('.git', '')
        else:
            repo_name = repo_root.name
        
        # Get current branch
        result = subprocess.run(
            ['git', 'branch', '--show-current'], 
            cwd=repo_root, 
            capture_output=True, 
            text=True
        )
        branch = result.stdout.strip() if result.returncode == 0 else 'main'
        
        return {'name': repo_name, 'branch': branch}
    
    except Exception:
        return {'name': repo_root.name, 'branch': 'main'}

def get_recent_commits(repo_root: Path, since: str) -> List[Dict[str, str]]:
    """Get recent commits for context analysis"""
    try:
        result = subprocess.run([
            'git', 'log', f'--since={since}', 
            '--pretty=format:%H|%s|%an|%ar'
        ], cwd=repo_root, capture_output=True, text=True)
        
        if result.returncode != 0:
            return []
        
        commits = []
        for line in result.stdout.strip().split('\n'):
            if line:
                parts = line.split('|', 3)
                if len(parts) == 4:
                    commits.append({
                        'hash': parts[0][:8],
                        'message': parts[1],
                        'author': parts[2],
                        'time': parts[3]
                    })
        
        return commits
    
    except Exception:
        return []

def get_modified_files(repo_root: Path) -> List[str]:
    """Get list of modified files (staged + unstaged)"""
    try:
        # Get staged files
        result = subprocess.run([
            'git', 'diff', '--cached', '--name-only'
        ], cwd=repo_root, capture_output=True, text=True)
        
        staged_files = set(result.stdout.strip().split('\n')) if result.stdout.strip() else set()
        
        # Get unstaged files
        result = subprocess.run([
            'git', 'diff', '--name-only'
        ], cwd=repo_root, capture_output=True, text=True)
        
        unstaged_files = set(result.stdout.strip().split('\n')) if result.stdout.strip() else set()
        
        # Combine and filter
        all_files = staged_files.union(unstaged_files)
        return [f for f in all_files if f and f != '']
    
    except Exception:
        return []

def detect_focus_from_changes(modified_files: List[str], recent_commits: List[Dict]) -> str:
    """Intelligently detect focus area from file changes"""
    
    patterns = {
        'Infrastructure hardening': ['terraform', 'docker', 'deploy', '.tf', 'infra/', 'k8s/', 'helm/'],
        'API debugging': ['api', 'endpoint', 'handler', 'lambda', 'routes', 'controllers/'],
        'Database optimization': ['sql', 'database', 'db/', 'migration', 'schema', 'models/'],
        'Frontend polish': ['ui/', 'components/', 'css', 'js', 'react', 'vue', 'angular', 'src/'],
        'Testing improvements': ['test', 'spec', 'pytest', 'jest', 'coverage', '__tests__/'],
        'Security hardening': ['auth', 'security', 'permission', 'oauth', 'jwt', 'ssl', 'crypto'],
        'Performance optimization': ['cache', 'performance', 'optimization', 'benchmark', 'profiling'],
        'Documentation updates': ['readme', 'docs/', 'documentation', '.md', 'wiki/'],
        'Configuration management': ['config', 'settings', 'env', 'yaml', 'json', 'toml']
    }
    
    # Score each pattern based on file matches
    scores = {}
    for focus_area, keywords in patterns.items():
        score = 0
        
        # Check modified files
        for file_path in modified_files:
            for keyword in keywords:
                if keyword.lower() in file_path.lower():
                    score += 1
        
        # Check commit messages (weighted higher)
        for commit in recent_commits:
            message = commit.get('message', '').lower()
            for keyword in keywords:
                if keyword.lower() in message:
                    score += 2
        
        scores[focus_area] = score
    
    # Return highest scoring focus area, or default
    if scores and max(scores.values()) > 0:
        return max(scores.items(), key=lambda x: x[1])[0]
    return "Infrastructure hardening"

def suggest_output_from_patterns(modified_files: List[str], recent_commits: List[Dict]) -> str:
    """Suggest expected output based on change patterns"""
    
    # Analyze file patterns
    if any('test' in f.lower() for f in modified_files):
        return "Comprehensive test coverage"
    elif any(f.endswith('.tf') or 'deploy' in f.lower() for f in modified_files):
        return "Deployment plan"
    elif any('api' in f.lower() or 'handler' in f.lower() or 'lambda' in f.lower() for f in modified_files):
        return "Working API endpoint"
    elif any('doc' in f.lower() or 'readme' in f.lower() for f in modified_files):
        return "Updated documentation"
    elif any('db' in f.lower() or 'migration' in f.lower() for f in modified_files):
        return "Database migration"
    elif any('config' in f.lower() or f.endswith('.yml') or f.endswith('.yaml') for f in modified_files):
        return "Configuration update"
    
    # Analyze commit messages
    commit_text = ' '.join(commit.get('message', '') for commit in recent_commits).lower()
    if 'fix' in commit_text or 'bug' in commit_text:
        return "Bug fix"
    elif 'feature' in commit_text or 'add' in commit_text:
        return "New feature"
    elif 'refactor' in commit_text or 'cleanup' in commit_text:
        return "Code refactoring"
    
    return "Working implementation"

def detect_constraints_from_repo(repo_root: Path, modified_files: List[str]) -> List[str]:
    """Detect likely constraints from repository characteristics"""
    
    constraints = []
    
    # Check for production indicators
    if any(f in str(repo_root).lower() for f in ['prod', 'production', 'live']):
        constraints.append('production stability')
    
    # Check for infrastructure files
    if any(f.endswith('.tf') or 'docker' in f.lower() for f in modified_files):
        constraints.append('infrastructure safety')
    
    # Check for API files
    if any('api' in f.lower() or 'endpoint' in f.lower() for f in modified_files):
        constraints.append('backward compatibility')
    
    # Check for database files
    if any('db' in f.lower() or 'migration' in f.lower() for f in modified_files):
        constraints.append('data integrity')
    
    # Check for package files (cost sensitivity)
    if any(f in modified_files for f in ['requirements.txt', 'package.json', 'Dockerfile']):
        constraints.append('cost optimization')
    
    # Default constraints if none detected
    if not constraints:
        constraints = ['maintainability', 'performance']
    
    return constraints[:3]  # Limit to 3 most relevant