"""
Main synthesis entry point - now much cleaner!
Delegates to stage-specific modules for better organization.
"""
from typing import List, Dict, Any, Optional
from .synthesis import generate_comprehensive_snapshot
from .synthesis.base import categorize_files, derive_template_vars

# Re-export for backwards compatibility
def synthesize_operator_instructions(thread_data: Dict[str, Any], file_categories: Dict[str, List[str]], 
                                   persona: str = "senior-backend-dev", enhanced_context: Optional[Dict] = None) -> str:
    """Generate operator instructions using persona templates (legacy function)"""
    
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

# Legacy function exports for compatibility
from .synthesis.analysis import mine_open_questions, analyze_commit_patterns

def synthesize_current_state(recent_commits: List[Dict[str, Any]], file_categories: Dict[str, List[str]]) -> str:
    """Legacy function - moved to development module"""
    from .synthesis.development import synthesize_development_current_state
    from .synthesis.analysis import analyze_development_context
    
    # Create minimal dev_context for legacy compatibility
    dev_context = analyze_development_context([], recent_commits, "")
    return synthesize_development_current_state([], recent_commits, dev_context, "")

def synthesize_decisions_constraints(thread_data: Dict[str, Any], file_categories: Dict[str, List[str]]) -> str:
    """Legacy function - simplified fallback"""
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

# Re-export main function
__all__ = [
    'generate_comprehensive_snapshot',
    'categorize_files',
    'synthesize_operator_instructions',
    'synthesize_current_state', 
    'synthesize_decisions_constraints',
    'mine_open_questions',
    'analyze_commit_patterns'
]