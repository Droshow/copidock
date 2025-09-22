import typer
from typing import Optional
from rich import print as rprint
from pathlib import Path

from .commands.thread import thread_start
from .api import CopidockAPI, resolve_api
from ..config.config import find_repo_root, load_state, save_state, DEFAULT_PROFILE

# ...rest of your code stays the same...

# ^ if you keep config/ at repo root; make sure config/__init__.py exists


app = typer.Typer(add_completion=False, help="Copidock CLI - Serverless note management")

@app.command("thread")
def thread_cmd(
    action: str = typer.Argument(..., help="Action: start"),
    goal: Optional[str] = typer.Argument(None, help="Thread goal"),
    repo: Optional[str] = typer.Option(None, "--repo", help="Repository name"),
    branch: str = typer.Option("main", "--branch", help="Branch name"),
    profile: str = typer.Option(DEFAULT_PROFILE, "--profile", help="Config profile"),
    api: Optional[str] = typer.Option(None, "--api", help="API base URL"),
    json_out: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Thread management"""
    if action == "start":
        if not goal:
            rprint("[red]Goal is required for thread start[/red]")
            raise typer.Exit(1)
        thread_start(goal, repo, branch, profile, api, json_out)
    else:
        rprint(f"[red]Unknown action: {action}[/red]")
        raise typer.Exit(1)

@app.command("note")
def note_cmd(
    action: str = typer.Argument(..., help="Action: add"),
    text: Optional[str] = typer.Argument(None, help="Note text"),
    tags: Optional[str] = typer.Option("", "--tags", help="Comma-separated tags"),
    profile: str = typer.Option(DEFAULT_PROFILE, "--profile"),
    api: Optional[str] = typer.Option(None, "--api"),
    json_out: bool = typer.Option(False, "--json"),
):
    """Note management"""
    if action != "add":
        rprint("[red]Only 'add' action supported[/red]")
        raise typer.Exit(1)
        
    if not text:
        rprint("[red]Note text is required[/red]")
        raise typer.Exit(1)
    
    repo_root = find_repo_root()
    state = load_state(repo_root)
    thread_id = state.get("thread_id", "")
    
    api_base, api_key, timeout = resolve_api(profile, api)
    client = CopidockAPI(api_base, api_key, timeout)
    
    tag_list = [t.strip() for t in (tags or "").split(",") if t.strip()]
    
    try:
        data = client.create_note(text, tag_list, thread_id)
        if json_out:
            rprint(data)
        else:
            rprint(f"[green]Note added[/green]: {data['note_id']}")
    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

@app.command("snapshot")
def snapshot_cmd(
    action: str = typer.Argument(..., help="Action: create"),
    message: Optional[str] = typer.Option("", "--message", help="Snapshot message"),
    auto: bool = typer.Option(False, "--auto", help="Auto-gather git changes"),
    comprehensive: bool = typer.Option(False, "--comprehensive", help="Generate comprehensive rehydration"),
    profile: str = typer.Option(DEFAULT_PROFILE, "--profile", help="Config profile"),
    api: Optional[str] = typer.Option(None, "--api", help="API base URL"),
    json_out: bool = typer.Option(False, "--json", help="JSON output"),
    persona: str = typer.Option("senior-backend-dev", "--persona", help="Template persona to use"),
):
    """Snapshot management"""
    if action != "create":
        rprint("[red]Only 'create' action supported[/red]")
        raise typer.Exit(1)
    
    repo_root = find_repo_root()
    state = load_state(repo_root)
    thread_id = state.get("thread_id", "")
    
    if not thread_id:
        rprint("[red]No active thread found. Start a thread first.[/red]")
        raise typer.Exit(1)
    
    api_base, api_key, timeout = resolve_api(profile, api)
    client = CopidockAPI(api_base, api_key, timeout)

    # Handle comprehensive mode
    if comprehensive:
        from .gather import gather_comprehensive
        from .synthesis import generate_comprehensive_snapshot
        
        try:
            # Get thread data for synthesis
            thread_data = {
                'goal': state.get('goal', 'development task'),
                'repo': state.get('repo', ''),
                'branch': state.get('branch', 'main')
            }
            
            # Comprehensive gathering
            file_paths, recent_commits, notes = gather_comprehensive(str(repo_root), thread_id)
            
            if not file_paths:
                rprint("[yellow]No relevant files found for comprehensive snapshot[/yellow]")
                raise typer.Exit(0)
            
            # Generate synthesis sections
            synth_sections = generate_comprehensive_snapshot(thread_data, file_paths, recent_commits, str(repo_root),persona)
            
            # SHOW THE INTELLIGENT TEMPLATE OUTPUT
            print("\n" + "="*70)
            print("🧠 INTELLIGENT TEMPLATE SYSTEM OUTPUT")
            print("="*70)
            for section_name, content in synth_sections.items():
                print(f"\n📋 {section_name.replace('_', ' ').title()}")
                print("-" * 50)
                print(content)
                print("")
            print("="*70)
            print("✅ Template system working perfectly!")
            print("="*70 + "\n")
            # Show what we're including
            if not json_out:
                rprint(f"[green]Comprehensive snapshot with {len(file_paths)} files[/green]")


            # Create inline sources
            inline_sources = []
            for file_path in file_paths:
                try:
                    full_path = Path(repo_root) / file_path
                    if full_path.exists():
                        content = full_path.read_text(errors='ignore')
                        file_ext = full_path.suffix.lstrip('.')
                        
                        # Map extensions to languages
                        language_map = {
                            'py': 'python', 'js': 'javascript', 'ts': 'typescript',
                            'tf': 'hcl', 'yml': 'yaml', 'yaml': 'yaml',
                            'json': 'json', 'md': 'markdown', 'sh': 'bash'
                        }
                        language = language_map.get(file_ext, 'text')
                        
                        inline_sources.append({
                            'path': file_path,
                            'language': language,
                            'content': content
                        })
                except Exception:
                    continue
            
            # Show what we're including
            if not json_out:
                rprint(f"[green]Comprehensive snapshot with {len(file_paths)} files[/green]")
                rprint(f"[dim]Recent commits: {len(recent_commits)}[/dim]")
                rprint(f"[dim]Synthesis sections: {len(synth_sections)}[/dim]")
            
            # Create comprehensive snapshot
            data = client.create_comprehensive_snapshot(thread_id, inline_sources, synth_sections, message)
            
            # Comprehensive mode output
            if json_out:
                rprint(data)
            else:
                rprint(f"[green]Comprehensive snapshot created[/green]: {data['snapshot_id']}")
                rprint(f"[dim]Included {len(inline_sources)} files with full synthesis[/dim]")
                
        except Exception as e:
            rprint(f"[red]Error creating comprehensive snapshot:[/red] {e}")
            raise typer.Exit(1)
    
    # Handle auto mode
    elif auto:
        from .gather import build_smart_paths
        
        try:
            file_paths, stats = build_smart_paths(str(repo_root))
            
            if not file_paths:
                rprint("[yellow]No relevant changed files found[/yellow]")
                raise typer.Exit(0)
            
            # Show what we're including
            if not json_out:
                rprint(f"[green]Auto-detected {stats['final_count']} files[/green]")
                rprint(f"[dim]Filtered: {stats['total_changed']} → {stats['after_filtering']} → {stats['final_count']} files[/dim]")
                for path in file_paths[:5]:  # Show first 5
                    rprint(f"[dim]  • {path}[/dim]")
                if len(file_paths) > 5:
                    rprint(f"[dim]  ... and {len(file_paths) - 5} more[/dim]")
            
            # Create regular snapshot
            data = client.create_snapshot(thread_id, file_paths, message)
            
            if json_out:
                rprint(data)
            else:
                rprint(f"[green]Snapshot created[/green]: {data['snapshot_id']}")
                rprint(f"[dim]Included {len(file_paths)} files[/dim]")
        
        except Exception as e:
            rprint(f"[red]Error gathering files:[/red] {e}")
            raise typer.Exit(1)
    
    else:
        # Manual mode - use empty paths
        try:
            data = client.create_snapshot(thread_id, [], message)
            if json_out:
                rprint(data)
            else:
                rprint(f"[green]Snapshot created[/green]: {data['snapshot_id']}")
        except Exception as e:
            rprint(f"[red]Error:[/red] {e}")
            raise typer.Exit(1)
    
@app.command("rehydrate")
def rehydrate_cmd(
    action: str = typer.Argument(..., help="Action: restore"),
    snapshot_id: Optional[str] = typer.Argument(None, help="Snapshot ID"),
    profile: str = typer.Option(DEFAULT_PROFILE, "--profile", help="Config profile"),
    api: Optional[str] = typer.Option(None, "--api", help="API base URL"),
    json_out: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Rehydrate from snapshot"""
    if action != "restore":
        rprint("[red]Only 'restore' action supported[/red]")
        raise typer.Exit(1)
    
    if not snapshot_id:
        rprint("[red]Snapshot ID is required[/red]")
        raise typer.Exit(1)
    
    repo_root = find_repo_root()
    
    api_base, api_key, timeout = resolve_api(profile, api)
    client = CopidockAPI(api_base, api_key, timeout)
    
    try:
        data = client.get_latest_snapshot(snapshot_id)
        
        # Update local state with restored thread_id
        state = load_state(repo_root)
        state["thread_id"] = data.get("thread_id", "")
        save_state(repo_root, state)
        
        if json_out:
            rprint(data)
        else:
            rprint(f"[green]Thread restored from snapshot[/green]: {data.get('thread_id', 'N/A')}")
    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)
    
if __name__ == "__main__":
    app()