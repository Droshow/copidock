import typer
from typing import Optional, List
from rich import print as rprint

from commands.thread import thread_start
from api import CopidockAPI, resolve_api
from copidock.config import find_repo_root, load_state, save_state, DEFAULT_PROFILE

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

# Add snapshot and rehydrate commands similarly...

if __name__ == "__main__":
    app()