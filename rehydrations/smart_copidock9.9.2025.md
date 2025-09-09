---
thread_id: smart-copidock-2025-09-09
snapshot_id: auto-context-collection-v1
version: 1
created_at: 2025-09-09T14:30:00Z
repo: copidock
branch: main
goal: "Build smart context collection and auto-snapshot features"
context_tags: ["cli","automation","git-integration","context-analysis","smart-features"]
related_paths:
  - copidock/cli/main.py
  - copidock/cli/commands/thread.py
  - copidock/cli/api.py
  - copidock/config/config.py
  - setup.py
token_budget_hint: 8k
---

# Rehydrate: Smart Copidock Development (v1)

## Operator Instructions (paste into model before sources)
You are a senior Python developer helping build intelligent automation features for a CLI tool.  
**Goal:** Transform basic CLI into smart context-aware development assistant.  
**Do:**
- Read Current State and analyze existing CLI architecture.
- Focus on git integration and intelligent file analysis.
- Build features that work universally (any editor, any workflow).
- Prioritize developer experience and automation over UI complexity.
**Don't:** Build VS Code extensions, add heavy dependencies, or over-engineer.

**Primary Tasks**
1. Design and implement `copidock snapshot smart` - auto-collect git changes, open files, generate contextual snapshots.
2. Add git integration features: branch-aware threading, commit message notes, diff analysis.
3. Create intelligent file filtering - skip generated files, focus on relevant code, extract meaningful snippets.

**Expected Outputs**
- Python code for smart snapshot collection
- Git integration commands and hooks
- File analysis and filtering logic
- Updated CLI commands with new smart features

## Current State (summary)
- **Working CLI**: `copidock` with thread, note, snapshot, rehydrate commands
- **Package structure**: Proper Python package with copidock.cli.main:app entry point
- **API integration**: CopidockAPI client handles serverless backend calls
- **State management**: Local .copidock/state.json tracks thread_id and profile
- **Configuration**: TOML-based config with profiles for API settings

## Decisions & Constraints
- **CLI-first approach**: Universal tool, not editor-specific
- **Shell-friendly**: Easy to script and compose with other tools
- **Git-native**: Leverage existing git workflows and metadata
- **Lightweight**: Minimal dependencies, fast execution
- **Backward compatible**: Don't break existing commands

## Smart Features Vision
1. **Auto-Context Collection**
   - `copidock snapshot smart` - analyzes workspace, builds Sources automatically
   - Detects changed files via git, reads relevant content
   - Generates intelligent code snippets (first 200 lines, key functions)
   - Auto-populates context_tags based on file types and imports

2. **Git Integration**
   - `copidock thread branch` - create/switch threads based on git branch
   - `copidock note commit <hash>` - extract commit message + diff as note
   - Git hooks for auto-noting on commits
   - Branch-aware state management

3. **Intelligent Analysis**
   - File relevance scoring (skip node_modules, .git, build artifacts)
   - Code extraction priorities (classes, functions, key configs)
   - Dependency analysis for better context_tags
   - Token budget management (stay under 6-8k total)

## Open Questions
1. How to detect "open files" in editor-agnostic way? File timestamps? LSP integration?
2. Git hook approach - global config or per-repo .git/hooks?
3. Context relevance scoring algorithm - AST analysis or simpler heuristics?
4. Integration with existing rehydration template format?

## Sources

### Source 1: copidock/cli/main.py (core CLI structure)
```python
import typer
from typing import Optional
from rich import print as rprint

from .commands.thread import thread_start
from .api import CopidockAPI, resolve_api
from ..config.config import find_repo_root, load_state, save_state, DEFAULT_PROFILE

app = typer.Typer(add_completion=False, help="Copidock CLI - Serverless note management")

@app.command("thread")
def thread_cmd(
    action: str = typer.Argument(..., help="Action: start"),
    goal: Optional[str] = typer.Argument(None, help="Thread goal"),
    repo: Optional[str] = typer.Option(None, "--repo", help="Repository name"),
    branch: str = typer.Option("main", "--branch", help="Branch name"),
    profile: str = typer.Option(DEFAULT_PROFILE, "--profile", help="Config profile"),
    json_out: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Thread management"""
    if action == "start":
        if not goal:
            rprint("[red]Goal is required for thread start[/red]")
            raise typer.Exit(1)
        thread_start(goal, repo, branch, profile, api, json_out)

@app.command("snapshot")
def snapshot_cmd(
    action: str = typer.Argument(..., help="Action: create"),
    message: Optional[str] = typer.Option("", "--message", help="Snapshot message"),
    profile: str = typer.Option(DEFAULT_PROFILE, "--profile", help="Config profile"),
    json_out: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Snapshot management"""
    # Current basic implementation - needs smart features
```

### Source 2: copidock/config/config.py (state and config management)
```python
def find_repo_root() -> Path:
    """Find git repository root"""
    current = Path.cwd()
    for path in [current] + list(current.parents):
        if (path / ".git").exists():
            return path
    return current

def load_state(repo_root: Path) -> Dict[str, Any]:
    """Load thread state"""
    state_file = get_state_path(repo_root)
    if state_file.exists():
        try:
            return json.loads(state_file.read_text())
        except (json.JSONDecodeError, OSError):
            return {}
    return {}

def save_state(repo_root: Path, data: Dict[str, Any]):
    """Save thread state"""
    state_file = get_state_path(repo_root)
    state_file.write_text(json.dumps(data, indent=2))
```

### Source 3: copidock/cli/api.py (API client structure)
```python
class CopidockAPI:
    def __init__(self, base_url: str, api_key: str, timeout: int = 30):
        self.base_url = base_url
        self.api_key = api_key
        self.timeout = timeout
        
    def create_snapshot(self, thread_id: str, message: str = "") -> dict:
        """Create snapshot of current thread"""
        # Current implementation - needs to accept rich context data
        
    def create_note(self, text: str, tags: list, thread_id: str) -> dict:
        """Create a note in thread"""
        # Current implementation works well
```

### Source 4: Project structure and dependencies
```
copidock/
├── copidock/
│   ├── cli/
│   │   ├── main.py          # Main CLI entry point
│   │   ├── api.py           # API client
│   │   └── commands/
│   │       └── thread.py    # Thread management
│   └── config/
│       └── config.py        # Config and state management
├── setup.py                 # Package definition
└── requirements.txt         # typer[all], requests, rich
```

## Personal Notes

# Implementation Priority
1. **Week 1**: `snapshot smart` command with git diff integration
2. **Week 2**: File analysis and intelligent snippet extraction  
3. **Week 3**: Git hooks and branch-aware threading

# Key Design Principles
- **Leverage existing patterns**: Use current state management and API client
- **Git as source of truth**: Build on git metadata rather than editor integration
- **Composable commands**: Each feature should work standalone and in pipes
- **Rich output**: Use existing rich formatting for developer-friendly feedback

# Technical Considerations
- Add subprocess/git integration utilities
- File type detection and filtering logic
- AST parsing for Python/JS code extraction (optional advanced feature)
- Token counting for budget management
- Template generation matching rehydration format

The goal is turning a basic CLI into an intelligent development assistant that understands your codebase and