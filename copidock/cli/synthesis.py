import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from ..templates.loader import template_loader
from rich import print as rprint

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

def derive_template_vars(thread_data: Dict[str, Any], file_categories: Dict[str, List[str]], 
                        persona: str = "senior-backend-dev", enhanced_context: Optional[Dict] = None) -> Dict[str, Any]:
    """Derive template variables using persona templates"""

    return template_loader.resolve_template_vars(persona, thread_data, file_categories, enhanced_context)

def synthesize_operator_instructions(thread_data: Dict[str, Any], file_categories: Dict[str, List[str]], 
                                   persona: str = "senior-backend-dev", enhanced_context: Optional[Dict] = None) -> str:
    """Generate operator instructions using persona templates"""

    if enhanced_context is None:
        enhanced_context = {}

    # Initialize template_vars
    template_vars = derive_template_vars(thread_data, file_categories, persona, enhanced_context) 

    # Extract enhanced parameters
    user_focus = enhanced_context.get('focus')
    user_output = enhanced_context.get('output') 
    user_constraints = enhanced_context.get('constraints')

    # Add enhanced context to template vars
    if user_focus:
        template_vars['primary_focus'] = user_focus
    if user_output:
        template_vars['expected_outputs'] = user_output
    if user_constraints:
        template_vars['constraints'] = user_constraints
    
    template_vars['existing_systems'] = template_vars.get('existing_systems', 'functionality')
    template_vars['risk_factors'] = template_vars.get('risk_factors', 'potential issues')
    template_vars['file_focus'] = template_vars.get('file_focus', 'relevant files')
    template_vars['task_list'] = template_vars.get('task_list', '- Review and implement changes\n- Test functionality\n- Update documentation')

    # Add complexity detection
    category_count = len([cat for cat, files in file_categories.items() if files])
    if category_count > 2:
        template_vars['complexity_note'] = "\n\n**Multi-area changes detected** - review cross-component impacts carefully."
    else:
        template_vars['complexity_note'] = ""
    
    # Template rendering using the persona system
    template = """## Operator Instructions

You are a **{persona_name}** working on: **{goal}**

**Primary Focus**: {primary_focus}  
**File Focus**: {file_focus}  
**Repository**: {repo} (branch: {branch})

### Guidelines

**Do:**
- Focus on {primary_focus} implementation
- Review {file_focus} changes carefully  
- Consider {constraints}
- Follow established patterns in the codebase

**Don't:**
- Break existing {existing_systems}
- Add unnecessary complexity or dependencies
- Ignore {risk_factors}
- Skip testing for critical paths

### Tasks for This Session

{task_list}

### Expected Outputs

{expected_outputs}{complexity_note}

---
"""
    
    return template.format(**template_vars)

def synthesize_initial_operator_instructions(enhanced_context, persona):
    """Generate operator instructions for initial stage using YML template"""
    
    # Load the YML template
    try:
        persona_config = template_loader.load_persona("senior-backend-dev-initial")
        rprint(f"[dim]Loaded YML template: senior-backend-dev-initial[/dim]")
    except Exception as e:
        rprint(f"[dim]Could not load initial template: {e}[/dim]")
        # Fallback to basic template
        persona_config = {
            'role': 'Senior Backend Developer',
            'context': 'You are setting up a new project from scratch',
            'guidelines_do': ['Focus on architectural decisions and project setup'],
            'guidelines_dont': ['Over-engineer for current requirements'],
            'task_priorities': ['Design system architecture and component boundaries'],
            'risk_factors': ['Technology choice paralysis']
        }
    
    # Extract CLI context
    focus = enhanced_context.get('focus', 'project setup')
    output = enhanced_context.get('output', 'working foundation')
    constraints = enhanced_context.get('constraints', 'best practices')
    
    # Build template from YML data
    role = persona_config.get('role', 'Senior Backend Developer')
    context_desc = persona_config.get('context', 'setting up a new project')
    
    # Format guidelines from YML
    guidelines_do = persona_config.get('guidelines_do', [])
    guidelines_dont = persona_config.get('guidelines_dont', [])
    task_priorities = persona_config.get('task_priorities', [])
    risk_factors = persona_config.get('risk_factors', [])
    
    # Build the sections
    do_section = '\n'.join([f"- {item}" for item in guidelines_do])
    dont_section = '\n'.join([f"- {item}" for item in guidelines_dont])
    tasks_section = '\n'.join([f"- {item}" for item in task_priorities])
    risks_section = '\n'.join([f"- {item}" for item in risk_factors])
    
    return f"""## Operator Instructions

You are a **{role}** {context_desc}.

**Primary Focus**: {focus}

### Guidelines

**Do:**
{do_section}

**Don't:**
{dont_section}

### Tasks for This Session
{tasks_section}

### Expected Outputs
{output}

### Risk Factors
{risks_section}

---
"""

def synthesize_initial_decisions_constraints(enhanced_context):
    """Generate decisions and constraints for initial stage using YML template"""
    
    # Load the YML template for additional context
    try:
        persona_config = template_loader.load_persona("senior-backend-dev-initial")
        focus_areas = persona_config.get('focus_areas', [])
    except Exception:
        focus_areas = ['Architecture and design decisions', 'Technology stack selection', 'Project structure and setup', 'Development environment configuration']
    
    constraints = enhanced_context.get('constraints', 'best practices')
    
    # Build technical approach from YML focus areas
    approach_items = []
    for area in focus_areas:
        if 'architecture' in area.lower():
            approach_items.append("- **Architecture**: Design for scalability and maintainability")
        elif 'technology' in area.lower():
            approach_items.append("- **Technology**: Select proven, well-supported technologies")
        elif 'development' in area.lower() or 'environment' in area.lower():
            approach_items.append("- **Development**: Set up proper development and testing environment")
        elif 'project structure' in area.lower() or 'setup' in area.lower():
            approach_items.append("- **Documentation**: Document key architectural decisions")
    
    # Fallback if no items
    if not approach_items:
        approach_items = [
            "- **Architecture**: Design for scalability and maintainability",
            "- **Technology**: Select proven, well-supported technologies",
            "- **Development**: Set up proper development and testing environment",
            "- **Documentation**: Document key architectural decisions"
        ]
    
    approach_section = '\n'.join(approach_items)
    
    return f"""## Decisions & Constraints

**Project Requirements**: {constraints}

## Technical Approach
{approach_section}

## Initial Setup Priorities
1. **Architecture Design**: Define system boundaries and component interactions
2. **Technology Selection**: Choose appropriate frameworks and databases
3. **Environment Setup**: Configure development and deployment environments
4. **Foundation Code**: Create project structure and basic scaffolding"""

def synthesize_current_state(recent_commits: List[Dict[str, Any]], file_categories: Dict[str, List[str]]) -> str:
    """Generate current state from git data with enhanced analysis"""
    
    state_parts = []
    
    # Analyze commit patterns
    commit_analysis = analyze_commit_patterns(recent_commits)
    
    # Recent commits summary with enhanced details
    if recent_commits:
        state_parts.append("## Recent Progress")
        
        # Show commit pattern summary
        if commit_analysis:
            patterns = []
            if commit_analysis['fix_commits']:
                patterns.append(f"{commit_analysis['fix_commits']} fixes")
            if commit_analysis['feature_commits']:
                patterns.append(f"{commit_analysis['feature_commits']} features")
            if commit_analysis['refactor_commits']:
                patterns.append(f"{commit_analysis['refactor_commits']} refactors")
            
            if patterns:
                state_parts.append(f"**Activity Pattern**: {', '.join(patterns)}")
            
            # Show urgency indicators
            if commit_analysis['urgency_indicators']:
                state_parts.append("**Urgent commits detected:**")
                for indicator in commit_analysis['urgency_indicators'][:2]:
                    state_parts.append(f"- `{indicator['commit']}`: {indicator['subject']}")
        
        state_parts.append("")
        state_parts.append("**Recent Commits:**")
        for commit in recent_commits[:4]:  # Show more commits
            # Add author info if available
            author_info = f" by {commit['author']}" if commit.get('author') else ""
            state_parts.append(f"- `{commit['hash'][:8]}`: {commit['subject']} ({commit['time_ago']}{author_info})")
    
    # Enhanced file changes summary  
    total_files = sum(len(files) for files in file_categories.values())
    state_parts.append(f"\n## Current Changes")
    state_parts.append(f"- **{total_files} files** modified across **{len(file_categories)} categories**")
    
    # File type breakdown with impact assessment
    for category, files in file_categories.items():
        impact_indicator = get_category_impact(category, len(files))
        state_parts.append(f"- **{category}**: {len(files)} files {impact_indicator}")
        
        # Show first few files as examples
        for file_path in files[:3]:  # Show more examples
            state_parts.append(f"  - `{file_path}`")
        if len(files) > 3:
            state_parts.append(f"  - ... and {len(files) - 3} more")
    
    # Add development velocity insights
    if recent_commits and len(recent_commits) >= 3:
        state_parts.append(f"\n## Development Velocity")
        state_parts.append(f"- **{len(recent_commits)} commits** in recent history")
        
        # Show most common words from commits
        if commit_analysis.get('common_words'):
            top_words = sorted(commit_analysis['common_words'].items(), 
                             key=lambda x: x[1], reverse=True)[:3]
            focus_words = [word for word, count in top_words if count > 1]
            if focus_words:
                state_parts.append(f"- **Focus areas**: {', '.join(focus_words)}")
    
    return "\n".join(state_parts)

def get_category_impact(category: str, file_count: int) -> str:
    """Get impact indicator for file category"""
    if category == "Infrastructure" and file_count > 0:
        return "🔧" if file_count == 1 else "⚠️"
    elif category == "Backend/Lambda" and file_count > 2:
        return "🚀"
    elif category == "Tests" and file_count > 0:
        return "✅"
    elif file_count > 5:
        return "📦"
    else:
        return ""

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
    
    # Enhanced file scanning with size limits and error handling
    for file_path in file_paths[:15]:  # Reasonable limit
        try:
            full_path = Path(repo_root) / file_path
            if not full_path.exists() or not full_path.is_file():
                continue
                
            # Skip very large files to avoid memory issues
            file_size = full_path.stat().st_size
            if file_size > 2 * 1024 * 1024:  # Skip files > 2MB
                continue
                
            # Safe file reading with encoding fallback
            try:
                content = full_path.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    content = full_path.read_text(encoding='latin-1', errors='ignore')
                except:
                    continue  # Skip if can't read
                    
            lines = content.split('\n')
            
            for line_num, line in enumerate(lines, 1):
                # Skip very long lines to avoid regex performance issues
                if len(line) > 200:
                    line = line[:200] + "..."
                    
                for pattern_type, pattern in patterns.items():
                    try:
                        matches = re.findall(pattern, line, re.IGNORECASE)
                        for match in matches:
                            clean_match = match.strip().rstrip('.,;:')
                            if len(clean_match) > 5:  # Filter very short matches
                                questions_by_type[pattern_type].append({
                                    'text': clean_match,
                                    'file': file_path,
                                    'line': line_num,
                                    'context': line.strip()[:80] + ('...' if len(line.strip()) > 80 else '')
                                })
                    except re.error:
                        # Skip malformed regex patterns
                        continue
                        
        except Exception as e:
            # Log but continue with other files
            continue
    
    # Enhanced commit message analysis
    for commit in recent_commits:
        try:
            commit_text = f"{commit.get('subject', '')} {commit.get('body', '')}"
            for pattern_type, pattern in patterns.items():
                try:
                    matches = re.findall(pattern, commit_text, re.IGNORECASE)
                    for match in matches:
                        clean_match = match.strip().rstrip('.,;:')
                        if len(clean_match) > 5:
                            questions_by_type[pattern_type].append({
                                'text': clean_match,
                                'file': f"Commit {commit.get('hash', 'unknown')[:8]}",
                                'line': 0,
                                'context': commit.get('subject', 'No subject')
                            })
                except re.error:
                    continue
        except Exception as e:
            continue
    
    # Format output with better organization
    if not any(questions_by_type.values()):
        return "## Open Questions\n\nNo open questions found in recent changes."
    
    output = ["## Open Questions\n"]
    
    # Prioritize critical question types
    priority_types = ['FIXME', 'TODO', 'QUESTION', 'REVIEW', 'HACK', 'TBD', 'XXX', 'NOTE']
    
    question_count = 0
    total_limit = 12  # Global limit to prevent huge sections
    
    for qtype in priority_types:
        questions = questions_by_type[qtype]
        if questions and question_count < total_limit:
            output.append(f"### {qtype}s\n")
            
            # Sort by file path for better organization
            questions.sort(key=lambda x: x['file'])
            
            type_limit = min(4, total_limit - question_count)  # Max 4 per type
            for q in questions[:type_limit]:
                if question_count >= total_limit:
                    break
                    
                output.append(f"{question_count + 1}. **{q['text']}**")
                output.append(f"   - *{q['file']}:{q['line']}*")
                if q['context'] != q['text'] and q['context'].strip():
                    output.append(f"   - Context: `{q['context']}`")
                output.append("")
                question_count += 1
    
    # Add summary if we hit limits
    total_questions = sum(len(questions) for questions in questions_by_type.values())
    if total_questions > question_count:
        output.append(f"*... and {total_questions - question_count} more questions found*")
    
    return "\n".join(output)

def analyze_commit_patterns(recent_commits: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Enhanced commit analysis with error handling"""
    if not recent_commits:
        return {
            'fix_commits': 0,
            'feature_commits': 0,
            'refactor_commits': 0,
            'test_commits': 0,
            'docs_commits': 0,
            'config_commits': 0,
            'common_words': {},
            'urgency_indicators': []
        }
    
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
        try:
            subject = commit.get('subject', '').lower()
            if not subject:
                continue
                
            # Categorize commits with better pattern matching
            if any(word in subject for word in ['fix', 'bug', 'error', 'issue', 'resolve']):
                patterns['fix_commits'] += 1
            elif any(word in subject for word in ['feat', 'feature', 'add', 'implement', 'new']):
                patterns['feature_commits'] += 1
            elif any(word in subject for word in ['refactor', 'cleanup', 'improve', 'optimize']):
                patterns['refactor_commits'] += 1
            elif any(word in subject for word in ['test', 'spec', 'coverage', 'unit', 'integration']):
                patterns['test_commits'] += 1
            elif any(word in subject for word in ['doc', 'readme', 'comment', 'documentation']):
                patterns['docs_commits'] += 1
            elif any(word in subject for word in ['config', 'setup', 'env', 'deploy', 'build']):
                patterns['config_commits'] += 1
            
            # Check for urgency with context
            for word in urgency_words:
                if word in subject:
                    patterns['urgency_indicators'].append({
                        'commit': commit.get('hash', 'unknown')[:8],
                        'word': word,
                        'subject': commit.get('subject', 'No subject')
                    })
            
            # Enhanced word counting with better filtering
            stopwords = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
            words = re.findall(r'\b\w{3,}\b', subject.lower())
            for word in words:
                if word not in stopwords and len(word) > 2:
                    patterns['common_words'][word] = patterns['common_words'].get(word, 0) + 1
                    
        except Exception as e:
            # Log error but continue processing other commits
            continue
    
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

def generate_comprehensive_snapshot(thread_data, file_paths, recent_commits, repo_root, persona, enhanced_context):
    """Generate all synthesis sections using persona templates"""
    
    # Handle enhanced context safely
    if enhanced_context is None:
        enhanced_context = {}
    
    # Get stage and template strategy
    stage = enhanced_context.get('stage', 'development')
    
    # For initial stage, ignore git analysis
    if stage == "initial":
        return generate_initial_stage_snapshot(thread_data, enhanced_context, persona)
    else:
        return generate_development_stage_snapshot(thread_data, file_paths, recent_commits, repo_root, persona, enhanced_context)

def generate_initial_stage_snapshot(thread_data, enhanced_context, persona, comprehensive=False):
    """Generate snapshot for initial/greenfield stage - no git analysis"""
    
    if comprehensive:
        # WITH YML template - rich guidance
        rprint(f"[dim]Using comprehensive YML template guidance[/dim]")
        sections = {
            'operator_instructions': synthesize_initial_operator_instructions_with_template(enhanced_context, persona),
            'current_state': "This is a greenfield project - comprehensive template guidance provided.",
            'decisions_constraints': synthesize_initial_decisions_constraints_with_template(enhanced_context),
            'open_questions': "Template-based questions and considerations provided."
        }
    else:
        # WITHOUT template - empty structure only
        rprint(f"[dim]Using empty structure for manual customization[/dim]")
        sections = {
            'operator_instructions': synthesize_initial_operator_instructions_empty(enhanced_context, persona),
            'current_state': "This is a greenfield project - empty structure provided for customization.",
            'decisions_constraints': synthesize_initial_decisions_constraints_empty(enhanced_context),
            'open_questions': "No predefined questions - customize as needed."
        }
    
    return sections

# ADD THESE NEW FUNCTIONS:

def synthesize_initial_operator_instructions_with_template(enhanced_context, persona):
    """Rich YML template guidance - COMPREHENSIVE"""
    
    # Load the YML template
    try:
        persona_config = template_loader.load_persona("senior-backend-dev-initial")
        rprint(f"[dim]✓ Loaded comprehensive YML template: senior-backend-dev-initial[/dim]")
        
        # Extract CLI context
        focus = enhanced_context.get('focus', 'project setup')
        output = enhanced_context.get('output', 'working foundation')
        constraints = enhanced_context.get('constraints', 'best practices')
        
        # Build template from YML data
        role = persona_config.get('role', 'Senior Backend Developer')
        context_desc = persona_config.get('context', 'setting up a new project')
        
        # Format guidelines from YML
        guidelines_do = persona_config.get('guidelines_do', [])
        guidelines_dont = persona_config.get('guidelines_dont', [])
        task_priorities = persona_config.get('task_priorities', [])
        risk_factors = persona_config.get('risk_factors', [])
        
        # Build rich sections
        do_section = '\n'.join([f"- {item}" for item in guidelines_do])
        dont_section = '\n'.join([f"- {item}" for item in guidelines_dont])
        tasks_section = '\n'.join([f"- {item}" for item in task_priorities])
        risks_section = '\n'.join([f"- {item}" for item in risk_factors])
        
        return f"""## Operator Instructions

You are a **{role}** {context_desc}.

**Primary Focus**: {focus}

### Guidelines

**Do:**
{do_section}

**Don't:**
{dont_section}

### Tasks for This Session
{tasks_section}

### Expected Outputs
{output}

### Risk Factors
{risks_section}

---
"""
        
    except Exception as e:
        rprint(f"[red] Could not load YML template: {e}[/red]")
        rprint(f"[red]Exception type: {type(e).__name__}[/red]")
        rprint(f"[red]Falling back to empty structure[/red]")
        # Fallback to empty structure
        return synthesize_initial_operator_instructions_empty(enhanced_context, persona)

def synthesize_initial_operator_instructions_empty(enhanced_context, persona):
    """Empty structure for manual customization - NO TEMPLATE"""
    
    focus = enhanced_context.get('focus', 'project setup')
    output = enhanced_context.get('output', 'working foundation')
    
    return f"""## Operator Instructions

You are a **Senior Backend Developer** setting up a new project from scratch.

**Primary Focus**: {focus}

### Guidelines

**Do:**

**Don't:**

### Tasks for This Session

### Expected Outputs
{output}

### Risk Factors

---
"""

def synthesize_initial_decisions_constraints_with_template(enhanced_context):
    """Rich decisions section WITH template guidance"""
    
    constraints = enhanced_context.get('constraints', 'best practices')
    
    # Load template for additional context
    try:
        persona_config = template_loader.load_persona("senior-backend-dev-initial")
        focus_areas = persona_config.get('focus_areas', [])
        
        # Build technical approach from YML focus areas
        approach_items = []
        for area in focus_areas:
            if 'architecture' in area.lower():
                approach_items.append("- **Architecture**: Design for scalability and maintainability")
            elif 'technology' in area.lower():
                approach_items.append("- **Technology**: Select proven, well-supported technologies")
            elif 'development' in area.lower() or 'environment' in area.lower():
                approach_items.append("- **Development**: Set up proper development and testing environment")
            elif 'project structure' in area.lower() or 'setup' in area.lower():
                approach_items.append("- **Documentation**: Document key architectural decisions")
        
        approach_section = '\n'.join(approach_items)
        
    except Exception:
        approach_section = "- **Architecture**: Design for scalability and maintainability\n- **Technology**: Select proven, well-supported technologies"
    
    return f"""## Decisions & Constraints

**Project Requirements**: {constraints}

## Technical Approach
{approach_section}

## Initial Setup Priorities
1. **Architecture Design**: Define system boundaries and component interactions
2. **Technology Selection**: Choose appropriate frameworks and databases
3. **Environment Setup**: Configure development and deployment environments
4. **Foundation Code**: Create project structure and basic scaffolding"""

def synthesize_initial_decisions_constraints_empty(enhanced_context):
    """Empty decisions section for manual customization"""
    
    constraints = enhanced_context.get('constraints', 'best practices')
    
    return f"""## Decisions & Constraints

**Project Requirements**: {constraints}

## Technical Approach

## Initial Setup Priorities
1. 
2. 
3. 
4. """

def generate_development_stage_snapshot(thread_data, file_paths, recent_commits, repo_root, persona, enhanced_context):
    """Generate snapshot for development/maintenance stage - full git analysis"""
    
    # Categorize files
    file_categories = categorize_files(file_paths)
    
    # Create context for template loading
    context = {
        'repo_root': repo_root,
        'file_categories': file_categories,
        'thread_data': thread_data
    }
    
    # Use stage-aware template loading
    try:
        template_content = template_loader.load_template_with_stage(
            persona, enhanced_context.get('stage', 'development'), context, enhanced_context
        )
        rprint(f"[dim]Loaded template for {enhanced_context.get('stage', 'development')} stage[/dim]")
    except Exception as e:
        rprint(f"[dim]Template loading failed: {e}[/dim]")
    
    # Generate all sections (including git analysis)
    sections = {
        'operator_instructions': synthesize_operator_instructions(thread_data, file_categories, persona, enhanced_context),
        'current_state': synthesize_current_state(recent_commits, file_categories),
        'decisions_constraints': synthesize_decisions_constraints(thread_data, file_categories),
        'open_questions': mine_open_questions(file_paths, repo_root, recent_commits)
    }
    
    return sections