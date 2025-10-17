"""Interactive prompting flow for guided snapshot creation"""

import typer
from rich import print as rprint
from typing import Dict, Optional, Any, List

def run_interactive_flow(
    context: Dict[str, Any], 
    default_persona: str, 
    default_focus: Optional[str], 
    default_output: Optional[str], 
    default_constraints: Optional[str],
    stage: str = "development"  # Added stage parameter
) -> Dict[str, str]:
    """Run interactive prompting flow with smart defaults"""
    
    # Display context (stage-aware)
    display_detected_context(context, stage)
    
    # Interactive prompts with smart defaults (stage-aware)
    if stage == "initial":
        # Initial stage - no git-based suggestions
        focus = typer.prompt(
            "🎯 What are you building? (Project vision)",
            default=default_focus or "New application"
        )
        
        output = typer.prompt(
            "🏆 What does success look like? (Expected outcomes)",
            default=default_output or "Working MVP"
        )
        
        constraints = typer.prompt(
            "⚡ Key requirements/constraints",
            default=default_constraints or "best practices"
        )
        
    else:
        # Development stage - use git analysis for suggestions
        focus = prompt_with_smart_default(
            "Focus", 
            default_focus or context['detected_focus'],
            context['detected_focus']
        )
        
        output = prompt_with_smart_default(
            "Expected output",
            default_output or context['suggested_output'],
            context['suggested_output']
        )
        
        constraints = prompt_with_smart_default(
            "Constraints",
            default_constraints or ", ".join(context['detected_constraints']),
            ", ".join(context['detected_constraints'])
        )
    
    # Show available personas
    available_personas = get_available_personas()
    rprint(f"[dim]Available personas: {', '.join(available_personas)}[/dim]")
    
    persona = typer.prompt(f"👤 Development persona", default=default_persona)
    
    return {
        'focus': focus,
        'output': output,
        'constraints': constraints,
        'persona': persona
    }

def display_detected_context(context: Dict[str, Any], stage: str = "development") -> None:
    """Display auto-detected context information - stage aware"""
    
    if stage == "initial":
        # Greenfield project - welcoming message
        rprint("[bold green]🌱 Welcome to Copidock![/bold green]")
        rprint("[dim]Let's plan your new project from scratch and create a solid foundation.[/dim]\n")
        
        # Show minimal repo info only
        rprint(f"[dim]> Starting fresh in: {context.get('repo', 'unknown')} (branch: {context.get('branch', 'main')})[/dim]")
        rprint("[dim]> This is a greenfield project - no existing code to analyze[/dim]")
        rprint("[dim]> Let's define your vision and create a solid foundation![/dim]\n")
        
        rprint("✨ Ready to build something amazing? Let's start with your project goals:\n")
        
    else:
        # Development stage - show git analysis
        rprint(f"[dim]> Detected repo: {context['repo']} (branch: {context['branch']})[/dim]")
        rprint(f"[dim]> Recent activity: {context['commit_count']} commits, {context['file_count']} files modified[/dim]")
        
        # Show recent commits for context
        if context['recent_commits']:
            rprint("[dim]> Recent commits:[/dim]")
            for commit in context['recent_commits'][:2]:  # Show top 2
                rprint(f"[dim]  • {commit['hash']}: {commit['message'][:50]}... ({commit['time']})[/dim]")
        
        # Show key modified files
        if context['modified_files']:
            rprint("[dim]> Key modified files:[/dim]")
            for file_path in context['modified_files'][:3]:  # Show top 3
                rprint(f"[dim]  • {file_path}[/dim]")
            
            if len(context['modified_files']) > 3:
                remaining = len(context['modified_files']) - 3
                rprint(f"[dim]  ... and {remaining} more files[/dim]")
        
        rprint()

def prompt_with_smart_default(
    prompt_text: str, 
    user_default: Optional[str], 
    detected_value: str
) -> str:
    """Prompt with smart default, showing detection reasoning"""
    
    if user_default and user_default != detected_value:
        # User provided different value than detected
        rprint(f"[dim]> Detected: \"{detected_value}\" | Using provided: \"{user_default}\"[/dim]")
        return typer.prompt(prompt_text, default=user_default)
    else:
        # Use detected value as default
        rprint(f"[dim]> Suggested {prompt_text.lower()}: \"{detected_value}\" (from recent changes)[/dim]")
        return typer.prompt(prompt_text, default=detected_value)

def confirm_snapshot_creation(stage: str,params: Dict[str, str], context: Dict[str, Any]) -> bool:
    """Show summary and confirm snapshot creation"""
    
    rprint("\n[blue]> Summary:[/blue]")
    rprint(f"  [bold]Focus:[/bold] {params['focus']}")
    rprint(f"  [bold]Output:[/bold] {params['output']}")
    rprint(f"  [bold]Constraints:[/bold] {params['constraints']}")
    rprint(f"  [bold]Persona:[/bold] {params['persona']}")
    
    if stage != "initial":
        rprint(f"  [bold]Auto-detected files:[/bold] {context['file_count']} (filtered, ≤6k tokens)")
    
    if stage != "initial" and context['recent_commits']:
        print(f"  [bold]Recent commits:[/bold] {len(context['recent_commits'])} included")
    
    rprint()
    return typer.confirm("Proceed with snapshot creation?", default=True)

def get_available_personas() -> List[str]:
    """Get list of available personas for selection"""
    # This integrates with your actual template directory
    try:
        from pathlib import Path
        personas_dir = Path("copidock/templates/personas")
        
        if personas_dir.exists():
            available_personas = []
            for yml_file in personas_dir.glob("*.yml"):
                # Extract base persona name (remove stage suffixes)
                name = yml_file.stem
                if not name.endswith(('-initial', '-development', '-maintenance')):
                    available_personas.append(name)
            return sorted(set(available_personas))
        return ["senior-backend-dev"]  # fallback
    except Exception:
        return ["senior-backend-dev"]  # fallback

def interactive_persona_selection(default_persona: str) -> str:
    """Interactive persona selection with descriptions"""
    
    personas = get_available_personas()
    
    rprint("[blue]Available personas:[/blue]")
    for i, persona in enumerate(personas, 1):
        marker = "[green]→[/green]" if persona == default_persona else " "
        rprint(f"{marker} {i}. {persona}")
    
    rprint()
    choice = typer.prompt(
        f"Select persona (1-{len(personas)}) or press Enter for default",
        default=str(personas.index(default_persona) + 1),
        type=str
    )
    
    try:
        index = int(choice) - 1
        if 0 <= index < len(personas):
            return personas[index]
    except ValueError:
        pass
    
    return default_persona