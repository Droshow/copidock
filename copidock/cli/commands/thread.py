from typing import Optional
import typer
from rich import print as rprint
from ..api import CopidockAPI, resolve_api
from ...config.config import find_repo_root, load_state, save_state, DEFAULT_PROFILE

def thread_start(
    goal: str,
    repo: Optional[str] = None,
    branch: str = "main",
    profile: str = DEFAULT_PROFILE,
    api: Optional[str] = None,
    json_out: bool = False,
):
    """Start a new thread"""
    repo_root = find_repo_root()
    api_base, api_key, timeout = resolve_api(profile, api)
    client = CopidockAPI(api_base, api_key, timeout)
    
    try:
        data = client.create_thread(goal, repo or "", branch)
        
        # Save thread state
        state = load_state(repo_root)
        state["thread_id"] = data["thread_id"]
        state["profile"] = profile
        save_state(repo_root, state)
        
        if json_out:
            rprint(data)
        else:
            rprint(f"[green]Thread started[/green]: {data['thread_name']}")
            rprint(f"ID: [cyan]{data['thread_id']}[/cyan]")
            rprint(f"Repo: {repo or 'n/a'} | Branch: {branch}")
            
    except Exception as e:
        rprint(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)