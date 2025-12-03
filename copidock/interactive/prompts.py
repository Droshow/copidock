"""Enhanced prompt input handlers for interactive CLI"""

import click
import os
from typing import Optional
from rich import print as rprint


def prompt_multiline(
    prompt_text: str,
    default: Optional[str] = None,
    use_editor: Optional[bool] = None,
    help_text: Optional[str] = None
) -> str:
    """
    Capture multiline input from user using their default editor or inline mode.
    
    Uses click.edit() by default to open the user's configured editor (vim, nano, VS Code, etc.)
    for a natural multiline editing experience. Can fall back to single-line prompt.
    
    Mode selection (in priority order):
    1. Explicit use_editor parameter (if provided)
    2. Environment variable COPIDOCK_EDITOR_MODE=inline (to disable editor)
    3. Default: use editor (True)
    
    Args:
        prompt_text: Display text for prompt (short label)
        default: Default value if user submits empty
        use_editor: Override editor mode (True=editor, False=inline, None=auto-detect)
        help_text: Optional helper text shown below prompt
    
    Returns:
        User's multiline input as a string
    
    Behavior:
        - Editor mode: Opens user's default $EDITOR
        - Inline mode: Single-line prompt with click.prompt()
    
    Environment:
        Set COPIDOCK_EDITOR_MODE=inline to disable editor globally
    """
    
    # Determine editor mode
    if use_editor is None:
        # Check environment variable
        editor_mode = os.environ.get('COPIDOCK_EDITOR_MODE', 'editor').lower()
        use_editor = editor_mode != 'inline'
    
    if use_editor:
        # Show prompt for editor mode
        default_hint = f" [{default}]" if default else ""
        rprint(f"\n[bold]{prompt_text}{default_hint}[/bold]")
        if help_text:
            rprint(f"[dim]{help_text}[/dim]")
        rprint("[dim]> Opening editor for multiline input... (save and close when done)[/dim]")
        
        # Prepare initial content with helpful comment
        initial_text = f"# {prompt_text}\n"
        if help_text:
            initial_text += f"# {help_text}\n"
        initial_text += "# Enter your text below. Lines starting with # will be ignored.\n"
        initial_text += "# Save and close the editor when done.\n\n"
        
        if default:
            initial_text += f"{default}\n"
        
        # Open editor
        result = click.edit(initial_text)
        
        # Process result
        if result is None or result.strip() == "":
            if default:
                rprint(f"[dim]✓ Using default: {default}[/dim]\n")
                return default
            else:
                rprint("[yellow]⚠ No input provided[/yellow]\n")
                return ""
        
        # Remove comment lines and clean up
        lines = [line for line in result.split('\n') if not line.strip().startswith('#')]
        cleaned = '\n'.join(lines).strip()
        
        line_count = len([l for l in lines if l.strip()])
        rprint(f"[green]✓ Captured {line_count} line{'s' if line_count != 1 else ''}[/green]\n")
        
        return cleaned
    
    else:
        # Inline mode - show help text separately, then prompt
        rprint(f"\n[bold]{prompt_text}[/bold]")
        if help_text:
            rprint(f"[dim]{help_text}[/dim]")
        return click.prompt("", default=default or "", show_default=True)


def prompt_single(
    prompt_text: str,
    default: Optional[str] = None
) -> str:
    """
    Simple single-line prompt using Click.
    
    Args:
        prompt_text: Display text for prompt
        default: Default value if user submits empty
    
    Returns:
        User input string
    """
    return click.prompt(prompt_text, default=default or "", show_default=True)
