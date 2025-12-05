"""
PRD (Product Requirements Document) creation and management commands
Separates strategic PRD planning from tactical development snapshots
"""
import typer
from typing import Optional
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from pathlib import Path
from datetime import datetime
import json

from ..api import CopidockAPI, resolve_api
from ...config.config import find_repo_root, load_state, save_state, DEFAULT_PROFILE
from ...interactive.detection import auto_detect_context
from ...interactive.flow import run_interactive_flow
from ...interactive.domains import list_available_domains, display_domain_info, get_domain_display_name
from ..synthesis.initial import generate_initial_stage_snapshot
from ..gather import render_files_markdown

console = Console()
prd_app = typer.Typer(help="PRD creation and management")


def get_prds_directory(repo_root: Path) -> Path:
    """Get or create the prds directory"""
    prds_dir = repo_root / "copidock" / "prds"
    prds_dir.mkdir(parents=True, exist_ok=True)
    return prds_dir


def create_prd_markdown(thread_data: dict, synth_sections: dict, enhanced_context: dict, prd_id: str) -> str:
    """Create PRD markdown content"""
    created_at = datetime.utcnow().isoformat() + "Z"
    project_name = enhanced_context.get('project_name', thread_data.get('goal', 'New Project'))
    domain = enhanced_context.get('domain')
    
    # Format multiline values
    def format_yaml_multiline(text: str) -> str:
        if '\n' in text:
            lines = text.split('\n')
            formatted = '|\n  ' + '\n  '.join(lines)
            return formatted
        else:
            return f'"{text}"'
    
    # Format domain context
    def format_domain_context(ctx: dict) -> str:
        domain = ctx.get('domain')
        if not domain:
            return ''
        
        domain_context = ctx.get('domain_context', {})
        if not domain_context:
            return f'domain: {domain}'
        
        lines = [f'domain: {domain}', 'domain_context:']
        for key, value in domain_context.items():
            if '\n' in str(value):
                value_lines = str(value).split('\n')
                lines.append(f'  {key}: |')
                for vline in value_lines:
                    lines.append(f'    {vline}')
            else:
                lines.append(f'  {key}: "{value}"')
        return '\n'.join(lines)
    
    focus_text = enhanced_context.get('focus', '').strip()
    output_text = enhanced_context.get('output', '').strip()
    constraints_text = enhanced_context.get('constraints', '').strip()
    
    frontmatter = f"""---
prd_id: {prd_id}
version: v1
created_at: {created_at}
project_name: "{project_name}"
thread_id: {thread_data.get('thread_id', '')}
repo: {thread_data.get('repo', 'unknown')}
branch: {thread_data.get('branch', 'main')}
persona: {enhanced_context.get('persona', 'senior-backend-dev')}
focus: {format_yaml_multiline(focus_text)}
output: {format_yaml_multiline(output_text)}
constraints: {format_yaml_multiline(constraints_text)}
{format_domain_context(enhanced_context)}
---

# PRD: {project_name}

## Executive Summary
"""
    
    # Add domain context section if present
    if domain:
        domain_context = enhanced_context.get('domain_context', {})
        if domain_context:
            domain_display = get_domain_display_name(domain)
            frontmatter += f"\n\n## 🎯 Domain: {domain_display}\n\n"
            frontmatter += "**Domain-Specific Requirements:**\n\n"
            for key, value in domain_context.items():
                label = key.replace('_', ' ').title()
                frontmatter += f"- **{label}**: {value}\n"
            frontmatter += "\n"
    
    # Add sections in order
    ordered_keys = [
        'operator_instructions',
        'current_state',
        'decisions_constraints',
        'technical_approach',
        'technology_stack',
        'risks',
        'best_practices',
        'anti_patterns',
        'open_questions',
    ]
    
    parts = [frontmatter]
    seen = set()
    
    for k in ordered_keys:
        v = synth_sections.get(k)
        if isinstance(v, str) and v.strip():
            parts.append(v.strip())
            seen.add(k)
    
    for k, v in synth_sections.items():
        if k in seen:
            continue
        if isinstance(v, str) and v.strip():
            parts.append(v.strip())
    
    return '\n\n'.join(parts)


@prd_app.command("create")
def prd_create(
    domain: Optional[str] = typer.Option(None, "--domain", help="Domain template: pwa, healthcare, fintech, etc."),
    interactive: bool = typer.Option(True, "--interactive/--no-interactive", help="Interactive prompting mode"),
    architecture: Optional[str] = typer.Option(None, "--architecture", help="Architecture style hint"),
    based_on: Optional[str] = typer.Option(None, "--based-on", help="Base PRD on existing file (for pivots)"),
    persona: str = typer.Option("senior-backend-dev", "--persona", help="Persona template to use"),
    profile: str = typer.Option(DEFAULT_PROFILE, "--profile", help="Config profile"),
):
    """
    Create a new PRD (Product Requirements Document)
    
    Strategic planning tool for project kickoff with domain-specific guidance.
    Use this for NEW projects or MAJOR pivots.
    Interactive mode is default - you'll be guided through the process.
    
    Examples:
        copidock prd create                    # Interactive with domain selection
        copidock prd create --domain pwa       # Direct to PWA domain
        copidock prd create --no-interactive   # Skip prompts (generic PRD)
    """
    repo_root = find_repo_root()
    state = load_state(repo_root)
    
    # Show available domains if none specified and interactive
    if not domain and interactive:
        domains = list_available_domains()
        if domains:
            rprint("\n[bold cyan]📚 Available Domain Templates:[/bold cyan]")
            for i, d in enumerate(domains, 1):
                display_name = get_domain_display_name(d)
                rprint(f"  {i}. {d} - {display_name}")
            rprint("  0. None (generic PRD)")
            
            choice = typer.prompt("\nSelect domain (0 for none)", default="0")
            if choice != "0":
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < len(domains):
                        domain = domains[idx]
                except (ValueError, IndexError):
                    rprint("[yellow]Invalid choice, using generic PRD[/yellow]")
    
    rprint("\n[bold green]🚀 Creating New PRD[/bold green]\n")
    
    if domain:
        display_domain_info(domain)
    
    # Get thread ID
    thread_id = state.get("thread_id")
    if not thread_id:
        rprint("[yellow]No active thread. Creating one...[/yellow]")
        # Create thread
        api_base, api_key, timeout = resolve_api(profile, None)
        client = CopidockAPI(api_base, api_key, timeout)
        
        goal = typer.prompt("Project goal/name", default="New Project")
        response = client.start_thread(
            goal=goal,
            repo=state.get('repo', repo_root.name),
            branch=state.get('branch', 'main')
        )
        thread_id = response['thread_id']
        
        # Save thread ID
        state['thread_id'] = thread_id
        state['goal'] = goal
        save_state(repo_root, state)
        rprint(f"[green]✓ Thread created: {thread_id}[/green]\n")
    
    # Get project name first (for filename)
    if interactive:
        rprint("[bold blue]📝 Project Information[/bold blue]\n")
        project_name = typer.prompt("📛 Project name", default=state.get('goal', 'New Project'))
        rprint()
    else:
        project_name = typer.prompt("Project name", default="New Project")
    
    # Interactive flow for business context
    if interactive:
        rprint("[bold blue]📝 Business Context (3 core questions)[/bold blue]\n")
        
        context = auto_detect_context(repo_root)
        interactive_params = run_interactive_flow(
            context=context,
            default_persona=persona,
            default_focus=None,
            default_output=None,
            default_constraints=None,
            stage="initial",  # Always initial for PRD creation
            domain=domain
        )
        
        focus = interactive_params['focus']
        output = interactive_params['output']
        constraints = interactive_params['constraints']
        persona = interactive_params['persona']
        domain_context = interactive_params.get('domain_context', {})
    else:
        # Non-interactive defaults
        focus = typer.prompt("What are you building?", default="New application")
        output = typer.prompt("What does success look like?", default="Working MVP")
        constraints = typer.prompt("Constraints?", default="Best practices")
        domain_context = {}
    
    # Prepare context
    thread_data = {
        'thread_id': thread_id,
        'goal': project_name,
        'repo': state.get('repo', repo_root.name),
        'branch': state.get('branch', 'main'),
    }
    
    enhanced_context = {
        'focus': focus,
        'output': output,
        'constraints': constraints,
        'stage': 'initial',
        'persona': persona,
        'domain': domain,
        'domain_context': domain_context,
        'project_name': project_name,  # Add to enhanced context
    }
    
    # Generate PRD content
    rprint("\n[dim]✨ Generating PRD with AI...[/dim]\n")
    synth_sections = generate_initial_stage_snapshot(
        thread_data=thread_data,
        enhanced_context=enhanced_context,
        persona=persona,
        comprehensive=True
    )
    
    # Create PRD file with project name in filename
    prd_id = f"prd-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"
    project_slug = project_name[:30].lower().replace(' ', '-').replace('/', '-').replace('_', '-')
    filename = f"{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}-{project_slug}.md"
    
    prds_dir = get_prds_directory(repo_root)
    prd_path = prds_dir / filename
    
    prd_content = create_prd_markdown(thread_data, synth_sections, enhanced_context, prd_id)
    
    prd_path.write_text(prd_content)
    
    # Update CURRENT symlink (points to active PRD)
    current_link = prds_dir / "CURRENT"
    if current_link.exists() or current_link.is_symlink():
        current_link.unlink()
    current_link.symlink_to(filename)
    
    # Update state with active PRD
    state['active_prd'] = str(prd_path.relative_to(repo_root))
    state['prd_version'] = 'v1'
    state['goal'] = project_name  # Update goal with project name
    save_state(repo_root, state)
    
    # Upload to S3
    api_base, api_key, timeout = resolve_api(profile, None)
    client = CopidockAPI(api_base, api_key, timeout)
    
    try:
        result = client.hydrate_snapshot(thread_id, prd_content, {
            'type': 'prd',
            'version': 'v1',
            'prd_id': prd_id
        })
        s3_key = result.get('s3_key', 'unknown')
        
        rprint(f"\n[bold green]✅ PRD Created Successfully![/bold green]\n")
        rprint(f"📁 Saved to: {prd_path.relative_to(repo_root)}")
        rprint(f"🔗 Linked as: copidock/prds/CURRENT")
        rprint(f"☁️  Uploaded to S3: {s3_key}")
        rprint(f"\n[dim]💡 Next steps:[/dim]")
        rprint(f"[dim]  1. Review PRD: copidock prd show[/dim]")
        rprint(f"[dim]  2. Start development[/dim]")
        rprint(f"[dim]  3. Create snapshots: copidock snapshot create[/dim]")
        
    except Exception as e:
        rprint(f"\n[yellow]⚠️  PRD saved locally but upload failed: {e}[/yellow]")
        rprint(f"📁 Local file: {prd_path.relative_to(repo_root)}")


@prd_app.command("list")
def prd_list(
    profile: str = typer.Option(DEFAULT_PROFILE, "--profile", help="Config profile"),
):
    """List all PRDs in the project"""
    repo_root = find_repo_root()
    prds_dir = get_prds_directory(repo_root)
    
    prd_files = sorted(prds_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    
    if not prd_files:
        rprint("[yellow]No PRDs found. Create one with: copidock prd create[/yellow]")
        return
    
    state = load_state(repo_root)
    active_prd = state.get('active_prd', '')
    
    table = Table(title="📚 Project PRDs", show_header=True, header_style="bold cyan")
    table.add_column("Version", style="dim")
    table.add_column("File", style="cyan")
    table.add_column("Created", style="dim")
    table.add_column("Active", style="green")
    
    for prd_file in prd_files:
        # Read frontmatter to get version and date
        try:
            content = prd_file.read_text()
            lines = content.split('---')[1].strip().split('\n')
            version = "v1"
            created = prd_file.stat().st_mtime
            
            for line in lines:
                if line.startswith('version:'):
                    version = line.split(':', 1)[1].strip()
                elif line.startswith('created_at:'):
                    created_str = line.split(':', 1)[1].strip()
                    # Parse ISO timestamp
                    try:
                        created_dt = datetime.fromisoformat(created_str.replace('Z', '+00:00'))
                        created = created_dt.strftime('%Y-%m-%d %H:%M')
                    except:
                        created = datetime.fromtimestamp(created).strftime('%Y-%m-%d %H:%M')
            
            is_active = str(prd_file.relative_to(repo_root)) == active_prd
            active_marker = "✓" if is_active else ""
            
            table.add_row(
                version,
                prd_file.name,
                str(created),
                active_marker
            )
        except Exception as e:
            table.add_row("?", prd_file.name, "error", "")
    
    console.print(table)
    rprint(f"\n[dim]💡 View a PRD: copidock prd show <filename>[/dim]")
    rprint(f"[dim]💡 Current active: {Path(active_prd).name if active_prd else 'None'}[/dim]")


@prd_app.command("show")
def prd_show(
    filename: Optional[str] = typer.Argument(None, help="PRD filename (or use CURRENT)"),
    profile: str = typer.Option(DEFAULT_PROFILE, "--profile", help="Config profile"),
):
    """Show a specific PRD"""
    repo_root = find_repo_root()
    prds_dir = get_prds_directory(repo_root)
    
    if not filename or filename.upper() == "CURRENT":
        # Show active PRD
        state = load_state(repo_root)
        active_prd = state.get('active_prd')
        if not active_prd:
            rprint("[yellow]No active PRD. List PRDs with: copidock prd list[/yellow]")
            return
        prd_path = repo_root / active_prd
    else:
        prd_path = prds_dir / filename
    
    if not prd_path.exists():
        rprint(f"[red]PRD not found: {prd_path}[/red]")
        return
    
    content = prd_path.read_text()
    rprint(content)


if __name__ == "__main__":
    prd_app()
