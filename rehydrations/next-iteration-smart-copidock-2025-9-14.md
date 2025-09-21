---
thread_id: smart-copidock-2025-09-14
snapshot_id: intelligent-rehydration-v5
version: 5
created_at: 2025-09-14T12:00:00Z
repo: copidock
branch: main
goal: "Build intelligent rehydration templating system - comprehensive snapshots"
context_tags: ["cli","rehydration","templating","synthesis","automation"]
related_paths:
  - copidock/cli/gather.py
  - copidock/cli/synthesis.py
  - copidock/cli/main.py
  - lambdas/snapshot_handler.py
token_budget_hint: 6k
---

# Rehydrate: Intelligent Rehydration Creation (v5)

## Operator Instructions (paste into model before sources)
You are a senior Python developer building intelligent snapshot synthesis.  
**Goal:** Transform the working MVP smart snapshot into a comprehensive rehydration generator that creates rich, contextual snapshots automatically.

**Do:**
- Build upon the successful MVP smart snapshot foundation
- Implement the 4-stage pipeline: gather → analyze → synthesize → upload
- Focus on deterministic, offline synthesis (no LLM dependency for core features)
- Create templated sections with smart heuristics

**Don't:** 
- Break the working MVP functionality
- Add heavy dependencies or external API calls
- Over-engineer the scoring algorithms
- Make LLM assistance mandatory

**Pipeline Tasks**
1. **Extend gather.py**: Add note fetching, commit analysis, and "important files" logic
2. **Create synthesis.py**: Build templating system for operator instructions, current state, decisions
3. **Add ranking logic**: Simple relevance scoring (recency + changes + keywords)  not just yet
4. **Update backend**: Handle inline_sources + synthesized sections
5. **Add --comprehensive flag**: Generate full rehydration snapshots

**Expected Outputs**
- Rich rehydration snapshots with operator instructions, current state, decisions
<!-- - Smart file ranking and token budget management -->
- Deterministic synthesis without LLM dependency
- Optional LLM enhancement for summaries

## Current State (MVP Success ✅)
- ✅ **Smart Git Collection**: Working `copidock snapshot create --auto`
- ✅ **Binary Detection & Filtering**: Skips irrelevant files perfectly
- ✅ **Token Budget**: 6k limit enforcement working
- ✅ **File Paths API**: Backend accepts paths parameter
- ✅ **State Management**: Thread state tracking functional
- ✅ **Error Handling**: Robust git command execution

## Next Iteration Scope

### ✅ Extend (Build on MVP)
1. **Comprehensive Gathering**: Notes + commits + important files
2. **Intelligent Synthesis**: Auto-generate operator instructions, current state
3. **Smart Ranking**: Relevance scoring for file prioritization  
4. **Rich Snapshots**: Full rehydration format with all sections
5. **Backend Integration**: Handle synthesized sections

### 🔄 New Features
1. **Note Integration**: Fetch thread notes from backend
2. **Commit Analysis**: Parse recent commits for context
3. **Template System**: Generate operator instructions from metadata
4. **Relevance Scoring**: Rank files by recency + changes + keywords
5. **Question Mining**: Extract TODOs/FIXMEs automatically

### ⏸️ Optional (Behind Flags)
1. **LLM Summarization**: `--llm-summarize` for enhanced summaries
2. **Secret Redaction**: Regex-based secret filtering
3. **Custom Templates**: User-defined instruction templates

## Technical Implementation

### Enhanced File Structure
```
copidock/cli/
├── main.py           # Add --comprehensive flag
├── gather.py         # Extend with notes + commits + important files
├── synthesis.py      # NEW: Template generation and section synthesis
├── ranking.py        # NEW: File relevance scoring
└── api.py           # Update for inline_sources + synth sections
```

### Core Workflow (Extended)
```bash
# 1. Developer works and wants comprehensive snapshot
git add . && git commit -m "Fixed auth bug"

# 2. Create comprehensive rehydration
copidock snapshot create --comprehensive
# → Gathers: git changes + notes + commits + important files
# → Analyzes: ranks by relevance score  
# → Synthesizes: operator instructions + current state + decisions
# → Uploads: full rehydration with inline_sources + synth sections
```

### Pipeline Implementation

#### Stage 1: Extended Gathering
```python
# In gather.py - extend existing functions
def gather_comprehensive(repo_root: str, thread_id: str, max_tokens: int = 6000):
    """Extended gathering for comprehensive snapshots"""
    candidates = []
    
    # 1. Git changes (existing MVP logic)
    changed_files = list_changed_files(repo_root)
    candidates.extend([(f, "git_change") for f in changed_files])
    
    # 2. Important files (always include)
    important_files = find_important_files(repo_root)
    candidates.extend([(f, "important") for f in important_files])
    
    # 3. Recent commits (for context)
    recent_commits = get_recent_commits(repo_root, limit=5)
    
    # 4. Thread notes (fetch from backend)
    notes = fetch_thread_notes(thread_id)
    
    return candidates, recent_commits, notes

def find_important_files(repo_root: str) -> List[str]:
    """Find always-important files"""
    patterns = [
        "infra/*.tf", "lambdas/*", "package.json", "requirements.txt", 
        "Makefile", "Dockerfile", ".github/workflows/*", "setup.py"
    ]
    # Implementation using glob patterns
```

#### Stage 2: Relevance Ranking
```python
# New file: ranking.py
def calculate_relevance_score(file_path: str, repo_root: str, 
                            goal_keywords: List[str], recent_commits: List[dict]) -> float:
    """Calculate relevance score: recency + changes + keywords"""
    
    # Recency boost (exponential decay, 7-day half-life)
    recency_boost = calculate_recency_boost(file_path, recent_commits)
    
    # Change weight (staged > unstaged > historical)
    change_weight = calculate_change_weight(file_path, repo_root)
    
    # Goal keyword hits
    keyword_hit = calculate_keyword_score(file_path, repo_root, goal_keywords)
    
    # Weighted combination
    score = 0.45 * recency_boost + 0.35 * change_weight + 0.20 * keyword_hit
    return min(1.0, score)

def extract_goal_keywords(goal: str) -> List[str]:
    """Extract keywords from thread goal"""
    stopwords = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for"}
    words = goal.lower().split()
    keywords = [w for w in words if w not in stopwords and len(w) > 2]
    return keywords[:5]  # Limit to top 5 keywords
```

#### Stage 3: Synthesis Templates
```python
# New file: synthesis.py
def synthesize_operator_instructions(thread_data: dict, file_types: List[str]) -> str:
    """Generate operator instructions from thread metadata"""
    
    template = """You are a senior developer working on {goal}.
    
**Do:**
- Focus on {primary_focus} implementation
- Review {file_focus} changes carefully
- Consider {constraints}

**Don't:**
- Break existing {existing_systems}
- Add unnecessary complexity
- Ignore {risk_factors}

**Primary Tasks**
{task_list}

**Expected Outputs**
{expected_outputs}"""
    
    # Use heuristics to fill template based on file types and thread data
    return template.format(**derive_template_vars(thread_data, file_types))

def synthesize_current_state(recent_commits: List[dict], changed_files: List[str]) -> str:
    """Generate current state from git data"""
    
    state_parts = []
    
    # Recent commits summary
    if recent_commits:
        state_parts.append("## Recent Progress")
        for commit in recent_commits[:3]:
            state_parts.append(f"- {commit['hash'][:8]}: {commit['subject']} ({commit['time_ago']})")
    
    # Changed files summary  
    state_parts.append(f"\n## Current Changes")
    state_parts.append(f"- {len(changed_files)} files modified")
    
    # File type breakdown
    file_types = categorize_files(changed_files)
    for category, files in file_types.items():
        if files:
            state_parts.append(f"- {category}: {len(files)} files")
    
    return "\n".join(state_parts)

def mine_open_questions(file_contents: List[str], recent_commits: List[dict]) -> str:
    """Extract TODOs, FIXMEs, and questions"""
    patterns = [
        r"TODO:?\s*(.+)", r"FIXME:?\s*(.+)", r"QUESTION:?\s*(.+)", 
        r"TBD:?\s*(.+)", r"XXX:?\s*(.+)"
    ]
    
    questions = []
    for content in file_contents:
        for pattern in patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            questions.extend(matches)
    
    # Also check commit messages
    for commit in recent_commits:
        for pattern in patterns:
            matches = re.findall(pattern, commit['message'], re.IGNORECASE)
            questions.extend(matches)
    
    return format_questions(questions[:10])  # Limit to top 10
```

#### Stage 4: Backend Integration
```python
# Update in api.py
def create_comprehensive_snapshot(self, thread_id: str, inline_sources: List[dict], 
                                synth_sections: dict, message: str = "") -> Dict[str, Any]:
    """Create comprehensive snapshot with synthesized sections"""
    payload = {
        "thread_id": thread_id,
        "message": message,
        "inline_sources": inline_sources,
        "synth": synth_sections
    }
    response = requests.post(
        f"{self.api_base}/snapshot/comprehensive",
        headers=self._headers(),
        json=payload,
        timeout=self.timeout
    )
    response.raise_for_status()
    return response.json()
```

## Implementation Plan

### Week 1: Foundation
- [x] **Day 1-2**: Extend `gather.py` with notes fetching and important files
- [x] **Day 3**: Create `synthesis.py` with basic templating
- [WONT DO] **Day 4**: Add `ranking.py` with relevance scoring
- [x] **Day 5**: Integrate `--comprehensive` flag in main.py

### Week 2: Enhancement  
- [x] **Day 1-2**: Update backend to handle synthesized sections
- [x] **Day 3**: Add question mining and commit analysis
- [ ] **Day 4**: Polish templates and heuristics
- [ ] **Day 5**: Test comprehensive workflow end-to-end

### Week 3: Optional Features
- [ ] **Day 1-2**: Add `--llm-summarize` for enhanced summaries
- [ ] **Day 3**: Implement secret redaction
- [ ] **Day 4**: Add custom template support
- [ ] **Day 5**: Documentation and final polish

## Success Criteria

### Core Features
- [ ] `copidock snapshot create --comprehensive` generates full rehydrations
- [ ] Smart file ranking prioritizes relevant changes
- [ ] Auto-generated operator instructions match context
- [ ] Current state reflects actual git/project status
- [ ] Open questions extracted from code and commits
- [ ] Token budget respected with intelligent prioritization

### Quality Measures
- [ ] Generated rehydrations are immediately actionable
- [ ] Operator instructions guide developers effectively
- [ ] Current state accurately reflects project status
- [ ] Relevance scoring improves file selection vs random
- [ ] No performance regression from MVP functionality

## Technical Debt & Risks

### Manageable Complexity
- **Template maintenance**: Keep templates simple and data-driven
- **Scoring accuracy**: Start simple, iterate based on usage
- **Backend compatibility**: Maintain backward compatibility with MVP

### Mitigation Strategies
- **Fallback behavior**: Comprehensive mode falls back to MVP on errors
- **Gradual rollout**: Feature flag for comprehensive mode
- **Performance monitoring**: Track token usage and generation time

## Why This Approach?

1. **Builds on proven MVP**: Extends working smart snapshot functionality
2. **Deterministic synthesis**: No external dependencies for core features
3. **Incremental value**: Each stage adds value independently
4. **User choice**: `--auto` for quick, `--comprehensive` for rich snapshots
5. **Future-ready**: Foundation for LLM enhancement and custom templates

**Bottom Line**: Transform the working smart snapshot into an intelligent rehydration generator that creates rich, contextual snapshots automatically while maintaining MVP reliability.