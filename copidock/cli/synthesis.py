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
    
    # Load the YML template - MAKE THIS DYNAMIC
    try:
        template_name = f"{persona}-initial"
        persona_config = template_loader.load_persona(template_name)
        rprint(f"[dim]Loaded YML template: {template_name}[/dim]")
    except Exception as e:
        rprint(f"[dim]Could not load initial template: {template_name} - {e}[/dim]")
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

def synthesize_initial_decisions_constraints(enhanced_context, persona):
    """Generate decisions and constraints for initial stage using YML template"""
    
    # Load the YML template for additional context - MAKE THIS DYNAMIC
    try:
        template_name = f"{persona}-initial"
        persona_config = template_loader.load_persona(template_name)
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
    
    # DEBUGGING: Print what stage we detected
    rprint(f"[dim]🔍 Detected stage: {stage}[/dim]")
    rprint(f"[dim]🔍 Input persona: {persona}[/dim]")
    
    # For initial stage, ignore git analysis
    if stage == "initial":
        rprint(f"[dim]→ Using initial stage logic[/dim]")
        return generate_initial_stage_snapshot(thread_data, enhanced_context, persona)
    else:
        rprint(f"[dim]→ Using development stage logic[/dim]")
        return generate_development_stage_snapshot(thread_data, file_paths, recent_commits, repo_root, persona, enhanced_context)

def generate_initial_stage_snapshot(thread_data, enhanced_context, persona, comprehensive=True):
    """Generate snapshot for initial/greenfield stage - no git analysis"""
    
    if comprehensive:
        # WITH YML template - rich guidance
        rprint(f"[dim]Using comprehensive YML template guidance[/dim]")
        sections = {
            'operator_instructions': synthesize_initial_operator_instructions_with_template(enhanced_context, persona),
            'current_state': "This is a greenfield project - comprehensive template guidance provided.",
            'decisions_constraints': synthesize_initial_decisions_constraints_with_template(enhanced_context, persona),
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

def synthesize_initial_operator_instructions_with_template(enhanced_context, persona):
    """Rich YML template guidance - COMPREHENSIVE"""
    
    # Load the YML template - MAKE THIS DYNAMIC
    try:
        template_name = f"{persona}-initial"
        persona_config = template_loader.load_persona(template_name)
        rprint(f"[dim]✓ Loaded comprehensive YML template: {template_name}[/dim]")
        
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
        rprint(f"[red] Could not load YML template: {template_name} - {e}[/red]")
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

def synthesize_initial_decisions_constraints_with_template(enhanced_context, persona):
    """Rich decisions section WITH template guidance"""
    
    constraints = enhanced_context.get('constraints', 'best practices')
    
    # Load template for additional context - MAKE THIS DYNAMIC
    try:
        template_name = f"{persona}-initial"
        persona_config = template_loader.load_persona(template_name)
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
    """Generate comprehensive development stage snapshot with git analysis"""
    
    if enhanced_context is None:
        enhanced_context = {}
    
    # Analyze development context from git changes
    dev_context = analyze_development_context(file_paths, recent_commits, repo_root)
    
    # Load development-specific template
    try:
        from ..templates.loader import template_loader
        rprint(f"[dim]🔍 Loading development template for: {persona}[/dim]")
        
        persona_config = template_loader.load_persona(f"{persona}-development")
        rprint(f"[green]✓ Successfully loaded development YML template[/green]")
        
        # DEBUG: Print development context analysis
        rprint(f"[dim]Detected work area: {dev_context.get('work_area', 'general')}[/dim]")
        rprint(f"[dim]Change impact: {dev_context.get('change_impact', 'medium')}[/dim]")
        rprint(f"[dim]Modified files: {len(file_paths)} files[/dim]")
        rprint(f"[dim]Recent commits: {len(recent_commits)} commits[/dim]")
        
        sections = {
            'operator_instructions': synthesize_development_operator_instructions_with_template(
                enhanced_context, persona, persona_config, dev_context
            ),
            'current_state': synthesize_development_current_state(
                file_paths, recent_commits, dev_context, repo_root
            ),
            'decisions_constraints': synthesize_development_decisions_constraints_with_template(
                enhanced_context, persona_config, dev_context
            ),
            'open_questions': synthesize_development_open_questions(
                dev_context, file_paths, recent_commits
            )
        }
        
        rprint(f"[green]✓ Development synthesis completed successfully[/green]")
        return sections
        
    except Exception as e:
        rprint(f"[red]❌ Could not load development template: {e}[/red]")
        rprint(f"[red]Falling back to basic development synthesis[/red]")
        
        # Fallback to basic development synthesis
        return generate_basic_development_snapshot(thread_data, file_paths, recent_commits, enhanced_context)

def analyze_development_context(file_paths, recent_commits, repo_root):
    """Analyze what type of development work is happening"""
    
    # Analyze file types and patterns
    file_analysis = analyze_file_patterns(file_paths)
    
    # Analyze commit messages for intent
    commit_analysis = analyze_commit_patterns(recent_commits)
    
    # Determine primary work area
    work_area = determine_work_area(file_analysis)
    
    # Assess change impact
    change_impact = assess_change_impact(file_analysis, commit_analysis)
    
    # Generate specific recommendations
    recommendations = generate_development_recommendations(work_area, file_analysis, commit_analysis)
    
    return {
        'work_area': work_area,
        'change_impact': change_impact,
        'file_analysis': file_analysis,
        'commit_analysis': commit_analysis,
        'recommendations': recommendations,
        'risk_areas': identify_risk_areas(work_area, file_analysis)
    }

def analyze_file_patterns(file_paths):
    """Analyze the types of files being modified"""
    patterns = {
        'api': 0,
        'frontend': 0,
        'database': 0,
        'tests': 0,
        'config': 0,
        'docs': 0,
        'other': 0
    }
    
    file_details = []
    
    for file_path in file_paths:
        path_lower = file_path.lower()
        file_type = 'other'
        
        if any(keyword in path_lower for keyword in ['api/', 'endpoints/', 'routes/', 'controllers/']):
            file_type = 'api'
        elif any(keyword in path_lower for keyword in ['frontend/', 'ui/', 'components/', 'views/', '.vue', '.jsx', '.tsx']):
            file_type = 'frontend'  
        elif any(keyword in path_lower for keyword in ['migration', 'schema', 'models/', 'database/']):
            file_type = 'database'
        elif any(keyword in path_lower for keyword in ['test', 'spec', '__tests__']):
            file_type = 'tests'
        elif any(keyword in path_lower for keyword in ['config', 'settings', '.env', 'docker', 'deploy']):
            file_type = 'config'
        elif any(keyword in path_lower for keyword in ['readme', 'docs/', '.md', 'documentation']):
            file_type = 'docs'
        
        patterns[file_type] += 1
        file_details.append({
            'path': file_path,
            'type': file_type
        })
    
    return {
        'patterns': patterns,
        'details': file_details,
        'total_files': len(file_paths)
    }

def analyze_commit_patterns(recent_commits):
    """Analyze commit messages to understand development intent"""
    if not recent_commits:
        return {'intent': 'unknown', 'patterns': [], 'urgency': 'normal'}
    
    commit_messages = [commit.get('message', '').lower() for commit in recent_commits]
    combined_text = ' '.join(commit_messages)
    
    # Detect intent patterns
    intent_patterns = {
        'feature': ['add', 'implement', 'create', 'new'],
        'bugfix': ['fix', 'bug', 'issue', 'resolve', 'correct'],
        'refactor': ['refactor', 'clean', 'improve', 'optimize'],
        'docs': ['docs', 'documentation', 'readme', 'comment'],
        'test': ['test', 'testing', 'spec', 'coverage'],
        'config': ['config', 'setup', 'deploy', 'ci', 'build']
    }
    
    detected_intent = 'general'
    max_matches = 0
    
    for intent, keywords in intent_patterns.items():
        matches = sum(1 for keyword in keywords if keyword in combined_text)
        if matches > max_matches:
            max_matches = matches
            detected_intent = intent
    
    # Detect urgency
    urgency = 'normal'
    urgent_keywords = ['urgent', 'critical', 'hotfix', 'emergency', 'asap']
    if any(keyword in combined_text for keyword in urgent_keywords):
        urgency = 'high'
    
    return {
        'intent': detected_intent,
        'urgency': urgency,
        'commit_count': len(recent_commits),
        'keywords_found': max_matches
    }

def determine_work_area(file_analysis):
    """Determine the primary area of development work"""
    patterns = file_analysis['patterns']
    
    # Find the area with the most file changes
    max_files = max(patterns.values())
    if max_files == 0:
        return 'general'
    
    for area, count in patterns.items():
        if count == max_files and area != 'other':
            return area
    
    return 'general'

def assess_change_impact(file_analysis, commit_analysis):
    """Assess the potential impact of changes"""
    file_count = file_analysis['total_files']
    commit_count = commit_analysis['commit_count']
    urgency = commit_analysis['urgency']
    
    if urgency == 'high' or file_count > 10 or commit_count > 5:
        return 'high'
    elif file_count > 5 or commit_count > 3:
        return 'medium'
    else:
        return 'low'

def generate_development_recommendations(work_area, file_analysis, commit_analysis):
    """Generate specific recommendations based on the development context"""
    recommendations = []
    
    intent = commit_analysis['intent']
    
    if work_area == 'api':
        recommendations.extend([
            "Test all modified API endpoints thoroughly",
            "Verify authentication and authorization still work",
            "Update API documentation (OpenAPI/Swagger)",
            "Check for breaking changes in API contracts"
        ])
    
    elif work_area == 'frontend':
        recommendations.extend([
            "Test across different browsers and screen sizes", 
            "Check mobile responsiveness",
            "Verify accessibility compliance",
            "Test user interactions and workflows"
        ])
    
    elif work_area == 'database':
        recommendations.extend([
            "Create reversible database migrations",
            "Test migrations on staging data first",
            "Backup production data before deployment",
            "Monitor query performance impact"
        ])
    
    elif work_area == 'tests':
        recommendations.extend([
            "Run full test suite to ensure no regressions",
            "Check test coverage metrics",
            "Verify tests are not flaky or interdependent",
            "Update test documentation if needed"
        ])
    
    # Add intent-specific recommendations
    if intent == 'feature':
        recommendations.extend([
            "Document the new feature functionality",
            "Add comprehensive tests for the new feature",
            "Consider feature flags for gradual rollout"
        ])
    elif intent == 'bugfix':
        recommendations.extend([
            "Add regression tests to prevent future occurrences",
            "Verify the fix doesn't introduce new issues",
            "Document the root cause and solution"
        ])
    
    return recommendations

def identify_risk_areas(work_area, file_analysis):
    """Identify potential risk areas based on development context"""
    risks = []
    
    if work_area == 'api':
        risks.extend([
            "Breaking API contracts for existing clients",
            "Authentication or authorization bypass",
            "Performance impact on high-traffic endpoints"
        ])
    elif work_area == 'database':
        risks.extend([
            "Data loss during migration",
            "Performance degradation of existing queries",
            "Constraint violations with existing data"
        ])
    elif work_area == 'frontend':
        risks.extend([
            "Cross-browser compatibility issues",
            "Mobile device performance problems",
            "Accessibility regressions"
        ])
    
    # General risks based on file count
    if file_analysis['total_files'] > 5:
        risks.append("High number of file changes increases integration risk")
    
    return risks

def synthesize_development_operator_instructions_with_template(enhanced_context, persona, persona_config, dev_context):
    """Generate development-focused operator instructions"""
    
    focus = enhanced_context.get('focus', 'development work')
    output = enhanced_context.get('output', 'working implementation')
    work_area = dev_context.get('work_area', 'general')
    
    # Get base guidelines
    guidelines_do = persona_config.get('guidelines_do', [])
    guidelines_dont = persona_config.get('guidelines_dont', [])
    task_priorities = persona_config.get('task_priorities', [])
    risk_factors = persona_config.get('risk_factors', [])
    
    # Add context-specific guidelines
    dev_contexts = persona_config.get('development_contexts', {})
    if work_area in dev_contexts:
        context_specific = dev_contexts[work_area]
        guidelines_do.extend(context_specific.get('specific_guidelines', []))
        risk_factors.extend(context_specific.get('risk_factors', []))
    
    # Add recommendations from analysis
    recommendations = dev_context.get('recommendations', [])
    
    # Build sections
    do_section = '\n'.join([f"- {item}" for item in guidelines_do])
    dont_section = '\n'.join([f"- {item}" for item in guidelines_dont])
    tasks_section = '\n'.join([f"- {item}" for item in task_priorities])
    risks_section = '\n'.join([f"- {item}" for item in risk_factors])
    recommendations_section = '\n'.join([f"- {item}" for item in recommendations])
    
    return f"""## Operator Instructions

You are a **{persona_config.get('role', 'Senior Backend Developer')}** {persona_config.get('context', 'working on development tasks')}.

**Primary Focus**: {focus}
**Development Area**: {work_area.title()} Development
**Change Impact**: {dev_context.get('change_impact', 'medium').title()}

### Guidelines

**Do:**
{do_section}

**Don't:**
{dont_section}

### Development Tasks for This Session
{tasks_section}

### Context-Specific Recommendations
{recommendations_section}

### Expected Outputs
{output}

### Risk Factors
{risks_section}

---
"""

def synthesize_development_current_state(file_paths, recent_commits, dev_context, repo_root):
    """Generate current state analysis for development work"""
    
    work_area = dev_context.get('work_area', 'general')
    file_analysis = dev_context.get('file_analysis', {})
    commit_analysis = dev_context.get('commit_analysis', {})
    
    # File summary
    file_summary = f"**Modified Files**: {len(file_paths)} files across {work_area} area"
    
    # Recent work summary
    intent = commit_analysis.get('intent', 'general')
    commit_count = commit_analysis.get('commit_count', 0)
    work_summary = f"**Recent Work**: {commit_count} commits focused on {intent} work"
    
    # File breakdown
    patterns = file_analysis.get('patterns', {})
    breakdown_items = []
    for area, count in patterns.items():
        if count > 0 and area != 'other':
            breakdown_items.append(f"- **{area.title()}**: {count} files")
    
    breakdown = '\n'.join(breakdown_items) if breakdown_items else "- General development work"
    
    return f"""## Current Development State

{file_summary}
{work_summary}

### File Breakdown
{breakdown}

### Development Context
- **Primary Area**: {work_area.title()} development
- **Change Impact**: {dev_context.get('change_impact', 'medium').title()}
- **Work Intent**: {intent.title()} implementation

### Recent Activity
- Last {commit_count} commits show {intent} work
- {len(file_paths)} files modified in current session
- Focus area: {work_area} development

"""

def synthesize_development_decisions_constraints_with_template(enhanced_context, persona_config, dev_context):
    """Generate development-focused decisions and constraints"""
    
    constraints = enhanced_context.get('constraints', 'best practices')
    work_area = dev_context.get('work_area', 'general')
    
    # Load focus areas from template
    focus_areas = persona_config.get('focus_areas', [])
    
    # Build technical approach from context
    approach_items = []
    for area in focus_areas:
        if 'quality' in area.lower():
            approach_items.append("- **Code Quality**: Maintain consistency with existing codebase")
        elif 'testing' in area.lower():
            approach_items.append("- **Testing**: Comprehensive testing for all modifications")
        elif 'documentation' in area.lower():
            approach_items.append("- **Documentation**: Update docs to reflect changes")
        elif 'integration' in area.lower():
            approach_items.append("- **Integration**: Ensure compatibility with existing systems")
        elif 'performance' in area.lower():
            approach_items.append("- **Performance**: Monitor and optimize performance impact")
        elif 'security' in area.lower():
            approach_items.append("- **Security**: Review security implications of changes")
    
    approach_section = '\n'.join(approach_items)
    
    # Development priorities based on context
    priorities = []
    if work_area == 'api':
        priorities = [
            "**API Compatibility**: Maintain backwards compatibility",
            "**Testing**: Test all endpoints and edge cases", 
            "**Documentation**: Update API documentation",
            "**Performance**: Monitor response times and throughput"
        ]
    elif work_area == 'frontend':
        priorities = [
            "**User Experience**: Maintain consistent UI patterns",
            "**Cross-Browser**: Test across different browsers",
            "**Performance**: Optimize for mobile and desktop",
            "**Accessibility**: Ensure accessibility compliance"
        ]
    elif work_area == 'database':
        priorities = [
            "**Data Integrity**: Ensure migration safety",
            "**Performance**: Monitor query performance impact", 
            "**Rollback**: Plan rollback strategies",
            "**Testing**: Test migrations on staging data"
        ]
    else:
        priorities = [
            "**Code Quality**: Follow established patterns",
            "**Testing**: Add comprehensive test coverage",
            "**Integration**: Verify system integration",
            "**Documentation**: Update relevant documentation"
        ]
    
    priorities_section = '\n'.join([f"{i+1}. {priority}" for i, priority in enumerate(priorities)])
    
    return f"""## Decisions & Constraints

**Project Requirements**: {constraints}

## Technical Approach
{approach_section}

## Development Priorities
{priorities_section}"""

def synthesize_development_open_questions(dev_context, file_paths, recent_commits):
    """Generate context-aware open questions for development work"""
    
    work_area = dev_context.get('work_area', 'general')
    change_impact = dev_context.get('change_impact', 'medium')
    recommendations = dev_context.get('recommendations', [])
    risks = dev_context.get('risk_areas', [])
    
    questions = []
    
    # Add area-specific questions
    if work_area == 'api':
        questions.extend([
            "Are there any breaking changes in the API modifications?",
            "Do we need to version these API changes?",
            "Have all authentication scenarios been tested?",
            "Is the API documentation up to date?"
        ])
    elif work_area == 'database':
        questions.extend([
            "Can these database changes be rolled back safely?",
            "Have migrations been tested with production-like data?",
            "Will these changes impact query performance?",
            "Are there any data integrity concerns?"
        ])
    elif work_area == 'frontend':
        questions.extend([
            "Have these changes been tested on mobile devices?",
            "Are there any accessibility concerns with the UI changes?",
            "Do these changes impact page load performance?",
            "Are the UI patterns consistent with the rest of the application?"
        ])
    
    # Add risk-based questions
    if change_impact == 'high':
        questions.extend([
            "Should these high-impact changes be deployed gradually?",
            "Do we have adequate monitoring for these changes?",
            "Is there a rollback plan if issues arise?"
        ])
    
    # Add recommendation-based questions
    if len(recommendations) > 3:
        questions.append("Are there too many changes being made at once?")
    
    if len(file_paths) > 8:
        questions.append("Should this work be broken into smaller, more focused changes?")
    
    # Default questions if none specific
    if not questions:
        questions = [
            "Are there any potential integration issues with existing code?",
            "Have all edge cases been considered and tested?", 
            "Is additional documentation needed for these changes?",
            "Are there performance implications to consider?"
        ]
    
    questions_section = '\n'.join([f"- {question}" for question in questions])
    
    return f"""## Open Questions & Considerations

### Development Questions
{questions_section}

### Risk Assessment
{chr(10).join([f"- {risk}" for risk in risks]) if risks else "- Standard development risks apply"}

### Next Steps
- Review and address the questions above
- Complete testing based on recommendations
- Update documentation as needed
- Plan deployment and monitoring strategy"""

def generate_basic_development_snapshot(thread_data, file_paths, recent_commits, enhanced_context):
    """Fallback development synthesis without YML template"""
    
    focus = enhanced_context.get('focus', 'development work')
    output = enhanced_context.get('output', 'working implementation')
    constraints = enhanced_context.get('constraints', 'best practices')
    
    return {
        'operator_instructions': f"""## Operator Instructions

You are a **Senior Backend Developer** working on ongoing development tasks.

**Primary Focus**: {focus}

### Development Guidelines
- Follow existing code patterns and conventions
- Write comprehensive tests for all changes
- Update documentation to reflect modifications
- Consider backwards compatibility and integration impact

### Expected Outputs
{output}

---
""",
        'current_state': f"""## Current Development State

**Active Development Session**
- {len(file_paths)} files modified
- {len(recent_commits)} recent commits
- Focus: {focus}

### Recent Changes
{chr(10).join([f"- {path}" for path in file_paths[:5]])}
{"- ... and more files" if len(file_paths) > 5 else ""}

""",
        'decisions_constraints': f"""## Decisions & Constraints

**Project Requirements**: {constraints}

## Development Approach
- Maintain code quality and consistency
- Ensure comprehensive testing
- Update documentation as needed
- Consider performance and security implications

""",
        'open_questions': """## Open Questions

- Are there any integration concerns with existing systems?
- Have all edge cases been tested?
- Is additional documentation needed?
- Are there performance implications to consider?

"""
    }