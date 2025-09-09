import typer
from typing import Optional
from rich import print as rprint

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
    profile: str = typer.Option(DEFAULT_PROFILE, "--profile", help="Config profile"),
    api: Optional[str] = typer.Option(None, "--api", help="API base URL"),
    json_out: bool = typer.Option(False, "--json", help="JSON output"),
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
    
    try:
        data = client.create_snapshot(thread_id, message)
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
        data = client.restore_snapshot(snapshot_id)
        
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