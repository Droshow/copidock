---
thread_id: smart-copidock-2025-09-14
snapshot_id: mvp-smart-snapshot-v4
version: 4
created_at: 2025-09-14T00:00:00Z
repo: copidock
branch: main
goal: "Ship MVP smart snapshot with git integration - less is more"
context_tags: ["cli","git-integration","snapshot","mvp"]
related_paths:
  - copidock/cli/main.py
  - copidock/cli/gather.py
  - copidock/cli/api.py
token_budget_hint: 4k
---

# Rehydrate: Smart Copidock MVP - Less is More (v4)

## Operator Instructions (paste into model before sources)
You are a senior Python developer shipping a minimal but robust CLI feature.  
**Goal:** Complete MVP smart snapshot that works reliably - no over-engineering.

**Do:**
- Focus on ONE core workflow: `copidock snapshot create --auto`
- Implement only essential hardening: binary detection, error handling, token budget
- Keep it simple and ship it working

**Don't:** 
- Add complex file scoring, AST parsing, or ML features
- Implement git hooks, branch-aware threading, or auto-tags
- Create per-thread configs or advanced extraction logic
- Over-engineer the solution

**MVP Tasks (Ship This Week)**
1. Harden `gather.py` with binary file detection and error handling
2. Add simple token budget management (6k limit)
3. Integrate `--auto` flag in snapshot command
4. Basic file extension filtering (.log, .cache → skip)

**Expected Outputs**
- Working `copidock snapshot create --auto` command
- Robust error handling for git edge cases
- Binary file detection
- Simple token budget enforcement

## Current State (summary)
- ✅ Working CLI with basic commands
- ✅ `--auto` flag exists in snapshot command  
- ⚠️ `gather.py` needs hardening (binary detection, error handling)
- ❌ No token budget management
- ❌ `--auto` not integrated with gathering logic

## MVP Scope (Essential Only)

### ✅ Keep - Core Features
1. **Smart Git Collection**: Detect changed files via `git diff/status`
2. **Binary Detection**: Skip binary files to avoid garbage content
3. **Token Budget**: Simple 6k token limit enforcement
4. **Error Handling**: Robust git command execution
5. **Basic Filtering**: Skip common non-code files (.log, .cache, node_modules)

### ❌ Remove - Over-Engineering  
1. ~~File relevance scoring with algorithms~~
2. ~~AST parsing for function extraction~~
3. ~~Context tag auto-population~~
4. ~~Per-thread configuration~~
5. ~~Git hooks integration~~
6. ~~Branch-aware threading~~
7. ~~Advanced code snippet priorities~~
8. ~~Keyword-based ranking~~

### ⏸️ Defer - Future Versions
1. Comprehensive unit tests (manual testing for MVP)
2. Backend inline_sources integration (use existing paths API)
3. Advanced git features (commit message extraction)
4. Rich CLI feedback and progress bars

## Technical Implementation

### MVP File Structure
```
copidock/cli/
├── main.py       # Add --auto integration
├── gather.py     # Harden with binary detection, token budget
└── api.py        # Use existing create_snapshot API
```

### Core Workflow
```bash
# 1. Developer makes changes
git add . && git commit -m "Fixed bug"

# 2. Create smart snapshot 
copidock snapshot create --auto
# → Detects git changes
# → Filters binary/irrelevant files  
# → Stays under 6k tokens
# → Creates snapshot with file paths
```

## Sources

### Source 1: copidock/cli/main.py (needs --auto integration)
```python
@app.command("snapshot")
def snapshot_cmd(
    action: str = typer.Argument(..., help="Action: create"),
    message: Optional[str] = typer.Option("", "--message", help="Snapshot message"),
    auto: bool = typer.Option(False, "--auto", help="Auto-gather git changes"),
    profile: str = typer.Option(DEFAULT_PROFILE, "--profile", help="Config profile"),
    json_out: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Snapshot management"""
    # TODO: Integrate --auto with gather.py logic
    # TODO: Call build_smart_paths() when auto=True
```

### Source 2: cli/gather.py (needs MVP hardening)
```python
def extract_hunks(repo_root: str, path: str, context: int, max_lines: int) -> str:
    """Extract git hunks or file content - NEEDS HARDENING"""
    # TODO: Add binary file detection
    # TODO: Add robust error handling
    # TODO: Add token counting
    pass

def build_inline_sources(repo_root: str, max_files: int = 12) -> list:
    """Build sources from git changes - NEEDS SIMPLIFICATION"""
    # TODO: Simple file extension filtering
    # TODO: Token budget enforcement  
    # TODO: Return file paths (not inline content for MVP)
    pass
```

## MVP Implementation Plan

### Week 1: Ship MVP
- [ ] **Day 1-2**: Harden `gather.py` with binary detection and error handling
- [ ] **Day 3**: Add simple token budget management  
- [ ] **Day 4**: Integrate `--auto` flag in main.py
- [ ] **Day 5**: Test and polish core workflow

### Success Criteria (MVP)
- [ ] `copidock snapshot create --auto` works in any git repo
- [ ] Skips binary files automatically
- [ ] Stays under 6k token budget
- [ ] Handles git command errors gracefully
- [ ] Filters obvious non-code files (.log, .cache, node_modules)

## Key Design Decisions (MVP)

### 1. Simple Binary Detection
```python
def is_binary_file(filepath: str) -> bool:
    """Simple binary detection - check for null bytes"""
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(1024)
            return b'\0' in chunk
    except:
        return True  # Assume binary if can't read
```

### 2. Basic File Filtering
```python
SKIP_EXTENSIONS = {'.log', '.cache', '.tmp', '.lock'}
SKIP_DIRECTORIES = {'node_modules', '.git', '__pycache__', '.pytest_cache'}

def should_skip_file(path: str) -> bool:
    """Simple file filtering"""
    if any(skip_dir in path for skip_dir in SKIP_DIRECTORIES):
        return True
    if Path(path).suffix.lower() in SKIP_EXTENSIONS:
        return True
    return False
```

### 3. Token Budget (Rough Estimate)
```python
def estimate_tokens(text: str) -> int:
    """Rough estimate: ~4 chars per token"""
    return len(text) // 4

def enforce_budget(file_paths: list, repo_root: str, max_tokens: int = 6000) -> list:
    """Keep under token budget by limiting files"""
    total_tokens = 0
    filtered_paths = []
    
    for path in file_paths:
        try:
            content = Path(repo_root, path).read_text(errors='ignore')
            tokens = estimate_tokens(content)
            if total_tokens + tokens <= max_tokens:
                filtered_paths.append(path)
                total_tokens += tokens
        except:
            continue  # Skip problematic files
            
    return filtered_paths
```

### 4. Robust Git Commands
```python
def safe_git_command(cmd: list, cwd: str, timeout: int = 10) -> str:
    """Execute git command safely"""
    try:
        result = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True, 
            timeout=timeout, check=False
        )
        return result.stdout if result.returncode == 0 else ""
    except (subprocess.TimeoutExpired, OSError):
        return ""
```

## Why This MVP Approach?

1. **Ships in 1 week** instead of 3 weeks
2. **Solves core problem**: Auto-collect git changes for snapshots
3. **Minimal risk**: Simple, testable components
4. **User focused**: One clear workflow that works reliably
5. **Iterative**: Can add advanced features based on real usage

**Bottom Line**: Make `copidock snapshot create --auto` work perfectly with git changes. Everything else is scope creep for v1.