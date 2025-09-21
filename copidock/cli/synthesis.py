import re
from typing import List, Dict, Any
from pathlib import Path

def categorize_files(file_paths: List[str]) -> Dict[str, List[str]]:
    """Categorize files by type"""
    categories = {
        "Infrastructure": [],
        "Backend/Lambda": [],
        "Frontend": [],
        "Configuration": [],
        "Tests": [],
        "Documentation": [],
        "Other": []
    }
    
    for file_path in file_paths:
        path_lower = file_path.lower()
        
        if any(x in path_lower for x in ['infra/', '.tf', '.yml', '.yaml']):
            categories["Infrastructure"].append(file_path)
        elif any(x in path_lower for x in ['lambda/', 'lambdas/', '.py']) and 'test' not in path_lower:
            categories["Backend/Lambda"].append(file_path)
        elif any(x in path_lower for x in ['.js', '.jsx', '.ts', '.tsx', '.vue', '.react']):
            categories["Frontend"].append(file_path)
        elif any(x in path_lower for x in ['config', 'requirements.txt', 'package.json', 'setup.py']):
            categories["Configuration"].append(file_path)
        elif 'test' in path_lower:
            categories["Tests"].append(file_path)
        elif any(x in path_lower for x in ['.md', '.rst', '.txt', 'readme']):
            categories["Documentation"].append(file_path)
        else:
            categories["Other"].append(file_path)
    
    # Remove empty categories
    return {k: v for k, v in categories.items() if v}

def derive_template_vars(thread_data: Dict[str, Any], file_categories: Dict[str, List[str]]) -> Dict[str, str]:
    """Derive template variables from thread data and file analysis"""
    goal = thread_data.get('goal', 'development task')
    
    # Determine primary focus from goal and files
    goal_lower = goal.lower()
    if 'infra' in goal_lower or 'deploy' in goal_lower or file_categories.get("Infrastructure"):
        primary_focus = "infrastructure and deployment"
        file_focus = "Terraform/infrastructure"
        existing_systems = "deployed infrastructure"
        risk_factors = "service outages and deployment failures"
    elif 'api' in goal_lower or 'backend' in goal_lower or file_categories.get("Backend/Lambda"):
        primary_focus = "backend API development"
        file_focus = "Lambda functions and API"
        existing_systems = "API endpoints"
        risk_factors = "breaking changes and data loss"
    elif 'test' in goal_lower or file_categories.get("Tests"):
        primary_focus = "testing and quality assurance"
        file_focus = "test cases and coverage"
        existing_systems = "test suite"
        risk_factors = "false positives and test flakiness"
    else:
        primary_focus = "feature development"
        file_focus = "code changes"
        existing_systems = "working functionality"
        risk_factors = "regressions and bugs"
    
    # Generate task list based on file types
    tasks = []
    if file_categories.get("Infrastructure"):
        tasks.append("- Review infrastructure changes for security and cost implications")
    if file_categories.get("Backend/Lambda"):
        tasks.append("- Validate API changes and error handling")
    if file_categories.get("Tests"):
        tasks.append("- Ensure test coverage for new functionality")
    if file_categories.get("Configuration"):
        tasks.append("- Verify configuration changes don't break existing setups")
    
    if not tasks:
        tasks = ["- Implement the requested functionality", "- Test the changes thoroughly"]
    
    return {
        'goal': goal,
        'primary_focus': primary_focus,
        'file_focus': file_focus,
        'constraints': "existing architecture and performance requirements",
        'existing_systems': existing_systems,
        'risk_factors': risk_factors,
        'task_list': '\n'.join(tasks),
        'expected_outputs': f"Working {primary_focus} that meets the goal: {goal}"
    }

def synthesize_operator_instructions(thread_data: Dict[str, Any], file_categories: Dict[str, List[str]]) -> str:
    """Generate operator instructions from thread metadata"""
    
    template = """You are a senior developer working on: {goal}

**Do:**
- Focus on {primary_focus} implementation
- Review {file_focus} changes carefully
- Consider {constraints}

**Don't:**
- Break existing {existing_systems}
- Add unnecessary complexity
- Ignore {risk_factors}

**Primary Tasks**
{task_list}

**Expected Outputs**
{expected_outputs}"""
    
    template_vars = derive_template_vars(thread_data, file_categories)
    return template.format(**template_vars)

def synthesize_current_state(recent_commits: List[Dict[str, Any]], file_categories: Dict[str, List[str]]) -> str:
    """Generate current state from git data"""
    
    state_parts = []
    
    # Recent commits summary
    if recent_commits:
        state_parts.append("## Recent Progress")
        for commit in recent_commits[:3]:
            state_parts.append(f"- `{commit['hash'][:8]}`: {commit['subject']} ({commit['time_ago']})")
    
    # Changed files summary  
    total_files = sum(len(files) for files in file_categories.values())
    state_parts.append(f"\n## Current Changes")
    state_parts.append(f"- {total_files} files modified across {len(file_categories)} categories")
    
    # File type breakdown
    for category, files in file_categories.items():
        state_parts.append(f"- **{category}**: {len(files)} files")
        # Show first few files as examples
        for file_path in files[:2]:
            state_parts.append(f"  - {file_path}")
        if len(files) > 2:
            state_parts.append(f"  - ... and {len(files) - 2} more")
    
    return "\n".join(state_parts)

def mine_open_questions(file_paths: List[str], repo_root: str, recent_commits: List[Dict[str, Any]]) -> str:
    """Enhanced extraction of TODOs, FIXMEs, and questions from files and commits"""
    
    # Enhanced patterns with context capture
    patterns = {
        'TODO': r'(?:TODO|@todo):?\s*(.{3,100})',
        'FIXME': r'(?:FIXME|@fixme):?\s*(.{3,100})',
        'QUESTION': r'(?:QUESTION|@question|\?{2,}):?\s*(.{3,100})',
        'TBD': r'(?:TBD|@tbd):?\s*(.{3,100})',
        'HACK': r'(?:HACK|@hack):?\s*(.{3,100})',
        'XXX': r'(?:XXX|@xxx):?\s*(.{3,100})',
        'NOTE': r'(?:NOTE|@note):?\s*(.{3,100})',
        'REVIEW': r'(?:REVIEW|@review):?\s*(.{3,100})'
    }
    
    questions_by_type = {ptype: [] for ptype in patterns.keys()}
    
    # Scan files with better error handling and line numbers
    for file_path in file_paths[:15]:  # Increased limit but still reasonable
        try:
            full_path = Path(repo_root) / file_path
            if not full_path.exists() or not full_path.is_file():
                continue
                
            # Skip binary and large files
            if full_path.stat().st_size > 1024 * 1024:  # Skip files > 1MB
                continue
                
            content = full_path.read_text(errors='ignore')
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                for pattern_type, pattern in patterns.items():
                    matches = re.findall(pattern, line, re.IGNORECASE)
                    for match in matches:
                        clean_match = match.strip().rstrip('.,;:')
                        if len(clean_match) > 5:  # Filter out very short matches
                            questions_by_type[pattern_type].append({
                                'text': clean_match,
                                'file': file_path,
                                'line': line_num,
                                'context': line.strip()[:80] + '...' if len(line.strip()) > 80 else line.strip()
                            })
        except Exception as e:
            continue  # Skip problematic files
    
    # Enhanced commit message analysis
    for commit in recent_commits:
        commit_text = f"{commit['subject']} {commit.get('body', '')}"
        for pattern_type, pattern in patterns.items():
            matches = re.findall(pattern, commit_text, re.IGNORECASE)
            for match in matches:
                clean_match = match.strip().rstrip('.,;:')
                if len(clean_match) > 5:
                    questions_by_type[pattern_type].append({
                        'text': clean_match,
                        'file': f"Commit {commit['hash'][:8]}",
                        'line': 0,
                        'context': commit['subject']
                    })
    
    # Format enhanced output
    if not any(questions_by_type.values()):
        return "## Open Questions\n\nNo open questions found in recent changes."
    
    output = ["## Open Questions\n"]
    
    # Prioritize question types
    priority_types = ['FIXME', 'TODO', 'QUESTION', 'REVIEW', 'HACK', 'TBD', 'XXX', 'NOTE']
    
    question_count = 0
    for qtype in priority_types:
        questions = questions_by_type[qtype]
        if questions and question_count < 12:  # Limit total questions
            output.append(f"### {qtype}s\n")
            
            for q in questions[:4]:  # Max 4 per type
                if question_count >= 12:
                    break
                    
                output.append(f"{question_count + 1}. **{q['text']}**")
                output.append(f"   - *{q['file']}:{q['line']}*")
                if q['context'] != q['text']:
                    output.append(f"   - Context: `{q['context']}`")
                output.append("")
                question_count += 1
    
    return "\n".join(output)
def analyze_commit_patterns(recent_commits: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze commit patterns for insights"""
    if not recent_commits:
        return {}
    
    patterns = {
        'fix_commits': 0,
        'feature_commits': 0,
        'refactor_commits': 0,
        'test_commits': 0,
        'docs_commits': 0,
        'config_commits': 0,
        'common_words': {},
        'urgency_indicators': []
    }
    
    urgency_words = ['urgent', 'critical', 'hotfix', 'emergency', 'asap', 'breaking']
    
    for commit in recent_commits:
        subject = commit['subject'].lower()
        
        # Categorize commits
        if any(word in subject for word in ['fix', 'bug', 'error', 'issue']):
            patterns['fix_commits'] += 1
        elif any(word in subject for word in ['feat', 'feature', 'add', 'implement']):
            patterns['feature_commits'] += 1
        elif any(word in subject for word in ['refactor', 'cleanup', 'improve']):
            patterns['refactor_commits'] += 1
        elif any(word in subject for word in ['test', 'spec', 'coverage']):
            patterns['test_commits'] += 1
        elif any(word in subject for word in ['doc', 'readme', 'comment']):
            patterns['docs_commits'] += 1
        elif any(word in subject for word in ['config', 'setup', 'env']):
            patterns['config_commits'] += 1
        
        # Check for urgency
        for word in urgency_words:
            if word in subject:
                patterns['urgency_indicators'].append({
                    'commit': commit['hash'][:8],
                    'word': word,
                    'subject': commit['subject']
                })
        
        # Count common words (skip stopwords)
        stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        words = re.findall(r'\b\w{3,}\b', subject.lower())
        for word in words:
            if word not in stopwords:
                patterns['common_words'][word] = patterns['common_words'].get(word, 0) + 1
    
    return patterns

def synthesize_decisions_constraints(thread_data: Dict[str, Any], file_categories: Dict[str, List[str]]) -> str:
    """Generate decisions and constraints section"""
    decisions = []
    
    goal = thread_data.get('goal', '').lower()
    
    # Architecture decisions based on file types
    if file_categories.get("Infrastructure"):
        decisions.append("- **Infrastructure**: Using Terraform for IaC management")
        decisions.append("- **Deployment**: Serverless architecture with AWS Lambda")
    
    if file_categories.get("Backend/Lambda"):
        decisions.append("- **Backend**: Python-based Lambda functions")
        decisions.append("- **API**: RESTful API design with proper error handling")
    
    # Cost and performance constraints
    decisions.append("- **Cost**: Optimize for serverless cost efficiency")
    decisions.append("- **Performance**: Target sub-second response times")
    decisions.append("- **Security**: Follow AWS security best practices")
    
    # Goal-specific constraints
    if 'mvp' in goal or 'simple' in goal:
        decisions.append("- **Scope**: MVP approach - minimal viable implementation")
    if 'test' in goal:
        decisions.append("- **Quality**: Comprehensive test coverage required")
    
    decisions_text = "\n".join(decisions)
    
    return f"""## Decisions & Constraints

{decisions_text}

## Technical Constraints
- **Platform**: AWS serverless architecture
- **Runtime**: Python 3.9+ for Lambda functions
- **Budget**: Development/testing environment
- **Timeline**: Iterative development with working increments"""

def generate_comprehensive_snapshot(thread_data: Dict[str, Any], file_paths: List[str], 
                                  recent_commits: List[Dict[str, Any]], repo_root: str) -> Dict[str, str]:
    """Generate all synthesis sections for comprehensive snapshot"""
    
    # Categorize files
    file_categories = categorize_files(file_paths)
    
    # Generate all sections
    sections = {
        'operator_instructions': synthesize_operator_instructions(thread_data, file_categories),
        'current_state': synthesize_current_state(recent_commits, file_categories),
        'decisions_constraints': synthesize_decisions_constraints(thread_data, file_categories),
        'open_questions': mine_open_questions(file_paths, repo_root, recent_commits)
    }
    
    return sections