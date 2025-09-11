---
thread_id: smart-copidock-2025-09-11
snapshot_id: consolidated-smart-snapshot-v3
version: 3
created_at: 2025-09-11T00:00:00Z
repo: copidock
branch: main
goal: "Complete smart snapshot implementation with robust git integration"
context_tags: ["cli","automation","git-integration","context-analysis","smart-features","snapshot","rehydration"]
related_paths:
  - copidock/cli/main.py
  - copidock/cli/commands/thread.py
  - copidock/cli/gather.py
  - copidock/cli/api.py
  - copidock/config/config.py
  - lambdas/snapshot_handler.py
  - setup.py
token_budget_hint: 8k
---

# Rehydrate: Smart Copidock Development - Consolidated (v3)

## Operator Instructions (paste into model before sources)
You are a senior Python developer finalizing intelligent automation features for a CLI tool.  
**Goal:** Complete the smart snapshot implementation and polish the git integration features.  

**Do:**
- Read Current State and build upon existing smart snapshot foundation.
- Focus on efficiency of code, error handling, and developer experience.
- Implement git integration features and file analysis logic.
- Ensure backward compatibility with existing CLI commands.

**Don't:** Rewrite core architecture, add heavy dependencies, or break existing workflows.

**Primary Tasks**
1. Polish and harden `cli/gather.py` with robust error handling and binary file detection
2. Complete `copidock snapshot smart` implementation with intelligent file filtering
3. Add comprehensive unit tests for git integration features
4. Implement branch-aware threading and commit message integration
5. Create file relevance scoring and token budget management

**Expected Outputs**
- Hardened Python code for smart snapshot collection
- Robust git integration with error handling
- Unit tests for file analysis and filtering logic
- Updated CLI commands with polished smart features
- Documentation for new developer workflows

## Current State (summary)
- **Working CLI**: `copidock` with thread, note, snapshot, rehydrate commands
- **Smart Snapshot Foundation**: Basic `--auto` mode implemented with `cli/gather.py`
- **Git Integration**: Initial diff parsing and changed file detection
- **API Integration**: Backend supports `/snapshot` with placeholder for inline sources
- **Package Structure**: Proper Python package with entry points
- **State Management**: Local `.copidock/state.json` tracks thread_id and profile

## Progress Since v1
- ✅ Added `cli/gather.py` with `list_changed_files`, `extract_hunks`, `build_inline_sources`
- ✅ Implemented basic `--auto` mode for snapshot collection
- ✅ Initial git diff parsing (needs hardening)
- ⚠️ File filtering logic partially implemented (needs binary detection)
- ❌ Unit tests missing
- ❌ Token budget management incomplete
- ❌ Branch-aware threading not implemented

## Decisions & Constraints
- **CLI-first approach**: Universal tool, not editor-specific
- **Token budget**: Keep snapshots ≤ 6-8k tokens for AI model compatibility
- **Git-native**: Leverage existing git workflows and metadata
- **Lightweight**: Minimal dependencies, fast execution
- **Cost sensitivity**: No external search index, keep logic lightweight
- **Backward compatible**: Don't break existing commands

## Smart Features Implementation Status

### 1. Auto-Context Collection ⚠️ Partial
- `copidock snapshot smart` - basic implementation exists
- File change detection via git - ✅ working
- Content extraction - ⚠️ needs binary detection and error handling
- Token budget management - ❌ missing
- Context tag auto-population - ❌ missing

### 2. Git Integration ⚠️ Partial  
- Diff parsing - ⚠️ needs hardening
- Changed file detection - ✅ working
- Branch-aware threading - ❌ missing
- Commit message extraction - ❌ missing

### 3. Intelligent Analysis ❌ Missing
- File relevance scoring - ❌ missing
- Binary file detection - ❌ missing  
- Code extraction priorities - ❌ missing
- Dependency analysis - ❌ missing

## Critical Issues to Address
1. **Binary file handling**: `gather.py` needs to skip binary files properly
2. **Error handling**: Git commands need robust exception handling
3. **Diff parsing**: Strip diff markers or keep for clarity?
4. **Token counting**: Implement budget management for 6-8k limit
5. **Unit tests**: No test coverage for git integration features

## Open Questions
1. Should we strip diff markers (`+/-`) or keep them for developer clarity?
2. Add keyword-based ranking (match thread goal words) now or later?
3. Per-thread config (max-files, max-lines) or global defaults?
4. Git hook approach - global config or per-repo `.git/hooks`?
5. Integration strategy for backend inline sources handling?

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

@app.command("snapshot")
def snapshot_cmd(
    action: str = typer.Argument(..., help="Action: create"),
    message: Optional[str] = typer.Option("", "--message", help="Snapshot message"),
    auto: bool = typer.Option(False, "--auto", help="Auto-gather git changes"),
    profile: str = typer.Option(DEFAULT_PROFILE, "--profile", help="Config profile"),
    json_out: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Snapshot management"""
    # Current implementation includes --auto flag
    # Needs integration with smart gathering logic
```

### Source 2: cli/gather.py (smart collection logic - needs hardening)
```python
def extract_hunks(repo_root: str, path: str, context: int, max_lines: int) -> str:
    """Extract git hunks or file content - NEEDS ERROR HANDLING"""
    try:
        diff = run(["git", "diff", "-U", str(context), "--", path], cwd=repo_root)
        if not diff.strip():
            diff = run(["git", "diff", "HEAD", "-U", str(context), "--", path], cwd=repo_root)
    except Exception:
        diff = ""

    fullp = Path(repo_root) / path
    if not diff.strip() and fullp.exists():
        # ISSUE: No binary file detection here
        text = fullp.read_text(errors="ignore")
        lines = text.splitlines()
        return "\n".join(lines[-max_lines:])
    
    snippet_lines = []
    for line in diff.splitlines():
        if line.startswith("@@"):
            snippet_lines.append(line)
            continue
        if line.startswith(("+","-"," ")):
            snippet_lines.append(line)
    # ISSUE: No token counting or budget management
    return "\n".join(snippet_lines)

def build_inline_sources(repo_root: str, max_files: int = 12) -> list:
    """Build sources from git changes - NEEDS UNIT TESTS"""
    changed_files = list_changed_files(repo_root)
    sources = []
    
    for path in changed_files[:max_files]:
        # ISSUE: No file filtering or relevance scoring
        content = extract_hunks(repo_root, path, context=3, max_lines=200)
        if content.strip():
            sources.append({
                "path": path,
                "content": content,
                "type": "git_change"
            })
    
    return sources
```

### Source 3: copidock/config/config.py (state management)
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
```

### Source 4: lambdas/snapshot_handler.py (backend integration)
```python
# Current backend - needs inline_sources handling
def create_snapshot(self, thread_id: str, message: str = "") -> dict:
    """Create snapshot of current thread"""
    # NEEDS: Accept and merge inline_sources from CLI requests
    # NEEDS: Handle rich context data from smart gathering
```

### Source 5: Project structure
```
copidock/
├── copidock/
│   ├── cli/
│   │   ├── main.py          # Main CLI with --auto flag
│   │   ├── gather.py        # Smart collection (needs hardening)
│   │   ├── api.py           # API client
│   │   └── commands/
│   │       └── thread.py    # Thread management
│   └── config/
│       └── config.py        # Config and state management
├── lambdas/
│   └── snapshot_handler.py  # Backend (needs inline_sources)
├── setup.py
└── requirements.txt         # typer[all], requests, rich
```

## Implementation Roadmap

### Phase 1: Harden Core (Week 1)
- [ ] Add binary file detection to `gather.py`
- [ ] Implement robust error handling for git commands
- [ ] Add token counting and budget management
- [ ] Create comprehensive unit tests

### Phase 2: Smart Features (Week 2)  
- [ ] Implement file relevance scoring
- [ ] Add context tag auto-population
- [ ] Create intelligent code snippet extraction
- [ ] Integrate backend inline_sources handling

### Phase 3: Git Integration (Week 3)
- [ ] Implement branch-aware threading
- [ ] Add commit message extraction features
- [ ] Create git hooks for auto-noting
- [ ] Polish developer experience

## Technical Debt
- Missing unit tests for git integration
- No binary file detection in content extraction
- Token budget management not implemented
- Error handling inconsistent across modules
- No file filtering or relevance scoring
- Backend doesn't handle inline_sources yet

## Success Criteria
- `copidock snapshot smart` works reliably with any git repo
- Stays under 6-8k token budget automatically
- Handles binary files and edge cases gracefully
- Comprehensive test coverage for git features
- Smooth developer experience with rich CLI feedback
- Backend properly processes inline_sources from CLI

The goal is completing a robust, production-ready smart snapshot system that transforms Copidock into an intelligent