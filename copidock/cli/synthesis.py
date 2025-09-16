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
    """Extract TODOs, FIXMEs, and questions from files and commits"""
    patterns = [
        r"TODO:?\s*(.+)", r"FIXME:?\s*(.+)", r"QUESTION:?\s*(.+)", 
        r"TBD:?\s*(.+)", r"XXX:?\s*(.+)", r"HACK:?\s*(.+)"
    ]
    
    questions = []
    
    # Scan files for TODO/FIXME comments
    for file_path in file_paths[:10]:  # Limit to first 10 files to avoid performance issues
        try:
            full_path = Path(repo_root) / file_path
            if full_path.exists() and full_path.is_file():
                content = full_path.read_text(errors='ignore')
                for pattern in patterns:
                    matches = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
                    for match in matches:
                        questions.append(f"**{file_path}**: {match.strip()}")
        except Exception:
            continue
    
    # Also check commit messages
    for commit in recent_commits:
        for pattern in patterns:
            matches = re.findall(pattern, commit['subject'], re.IGNORECASE)
            for match in matches:
                questions.append(f"**Commit {commit['hash'][:8]}**: {match.strip()}")
    
    # Format questions
    if questions:
        formatted = "## Open Questions\n\n"
        for i, question in enumerate(questions[:10], 1):  # Limit to top 10
            formatted += f"{i}. {question}\n"
        return formatted
    else:
        return "## Open Questions\n\nNo open questions found in recent changes."

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