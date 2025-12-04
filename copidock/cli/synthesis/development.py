"""
Development stage synthesis - git-aware continuous development
Combines YML templates with real-time git analysis
"""
from typing import List, Dict, Any
from rich import print as rprint
from ...templates.loader import template_loader
from .analysis import analyze_development_context
from .base import get_category_impact

def generate_development_stage_snapshot(thread_data, file_paths, recent_commits, repo_root, persona, enhanced_context):
    """Generate comprehensive development stage snapshot with git analysis"""
    
    if enhanced_context is None:
        enhanced_context = {}
    
    # Analyze development context from git changes
    dev_context = analyze_development_context(file_paths, recent_commits, repo_root)
    
    # Load development-specific template
    try:
        rprint(f"[dim]🔍 Loading development template for: {persona}[/dim]")
        
        persona_config = template_loader.load_persona(f"{persona}")
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
        
        # Merge domain-specific synthesis hints if domain is specified
        domain = enhanced_context.get('domain')
        if domain:
            from ...interactive.domains import get_domain_synthesis_hints, merge_synthesis_hints
            domain_hints = get_domain_synthesis_hints(domain)
            if domain_hints:
                rprint(f"[dim]✓ Merging domain-specific guidance for: {domain}[/dim]")
                sections = merge_synthesis_hints(sections, domain_hints)
        
        rprint(f"[green]✓ Development synthesis completed successfully[/green]")
        return sections
        
    except Exception as e:
        rprint(f"[red]❌ Could not load development template: {e}[/red]")
        rprint(f"[red]❌ NO FALLBACK - Template file must exist![/red]")
        raise ValueError(f"Missing required template file: {persona}")

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