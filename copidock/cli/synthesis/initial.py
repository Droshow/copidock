"""
Initial stage synthesis - template-driven project foundation
No git analysis, pure YML template guidance
"""
from typing import Dict, Any
from rich import print as rprint
from ...templates.loader import template_loader

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
    
    # Load the YML template - NO HARDCODING
    try:
        template_name = f"{persona}"
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
        rprint(f"[red]❌ Could not load YML template: {template_name} - {e}[/red]")
        rprint(f"[red]❌ NO FALLBACK - Template file must exist![/red]")
        # NO HARDCODED FALLBACK - FAIL EXPLICITLY
        raise ValueError(f"Missing required template file: {template_name}.yml")

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
    
    # Load template for additional context - NO HARDCODING
    try:
        template_name = f"{persona}"
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
        
    except Exception as e:
        rprint(f"[red]❌ Could not load template for decisions: {persona} - {e}[/red]")
        raise ValueError(f"Missing required template file: {persona}.yml")
    
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