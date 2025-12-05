---
title: "Copidock: PRD vs Snapshot Separation"
date: 2025-12-05
version: 1.0
status: Planning
type: Architecture Refinement
priority: High
impact: Breaking Changes
---

# PRD: Separate PRD Creation from Development Snapshots

## Executive Summary

**Problem**: Current architecture conflates two distinct workflows - strategic PRD creation and tactical development snapshots - leading to user confusion and feature bloat.

**Solution**: Split into two clear commands with distinct purposes:
- `copidock prd create` - Strategic planning, domain-aware, comprehensive (infrequent)
- `copidock snapshot create` - Tactical tracking, git-aware, focused (frequent)

**Impact**: 
- ✅ Clearer mental model for users
- ✅ Simpler command-line interface
- ✅ Better separation of concerns
- ⚠️ Breaking changes to existing CLI
- ⚠️ File structure reorganization

---

## 🎯 Vision

### Core Insight
There are **two fundamentally different use cases** that require different tools:

| Use Case | Frequency | Focus | Input | Output |
|----------|-----------|-------|-------|--------|
| **PRD Creation** | Once per project/milestone | Business vision → Technical plan | Human context + Domain template | Comprehensive PRD |
| **Development Snapshot** | Multiple times daily | Code changes → LLM context | Git diffs + File analysis | Focused snapshot |

**Current Problem**: We're trying to serve both with `copidock snapshot create --stage initial --interactive --domain pwa` (too many flags, unclear intent)

---

## 🏗️ Proposed Architecture

### 1. Command Structure

```bash
# === PRD Management (Strategic) ===
copidock prd create --domain <domain> --interactive
copidock prd update [--review-snapshots]
copidock prd list
copidock prd show <version>

# === Development Snapshots (Tactical) ===
copidock snapshot create [--hydrate] [--comprehensive]
copidock snapshot list
copidock rehydrate restore <snapshot-id>
```

### 2. File Structure

```
copidock/
  prds/                           # Strategic planning documents
    initial-20251205-pwa-app.md       # v1: Project kickoff
    updated-20251212-auth-added.md    # v2: After sprint 1
    pivot-20251220-mobile-native.md   # v3: Architecture change
    CURRENT -> updated-20251212-auth-added.md
  
  snapshots/                      # Tactical development history
    20251205-143022-auth-feature.md
    20251205-150033-database-schema.md
    20251206-091234-api-endpoints.md
    LATEST -> 20251206-091234-api-endpoints.md
  
  .copidock/
    state.json                    # Active thread, PRD reference
    config.yml                    # User preferences
```

### 3. State Management

```json
// .copidock/state.json
{
  "thread_id": "abc-123",
  "active_prd": "prds/updated-20251212-auth-added.md",
  "prd_version": "v2",
  "profile": "default",
  "last_snapshot": "snapshots/20251206-091234-api-endpoints.md"
}
```

---

## 📋 Detailed Design

### Feature 1: PRD Creation Command

**Command**: `copidock prd create`

**Flags**:
- `--domain <name>` - Load domain template (pwa, healthcare, fintech, etc.)
- `--interactive` - Prompt for business context (default: true)
- `--architecture <style>` - Architecture pattern hint (serverless, microservices, etc.)
- `--based-on <file>` - Migrate from existing PRD (for pivots)

**Interactive Flow**:
```
🚀 Creating New PRD

Select domain (optional):
  1. PWA (Progressive Web App)
  2. Healthcare (HIPAA compliance)
  3. Fintech (PCI-DSS)
  4. API Service (REST/GraphQL)
  5. ML Pipeline
  6. Generic (no domain template)
  
Choice: 1

📝 Business Context (3 questions)

🎯 What are you building?
   (Opens editor for multiline input)
   
🏆 What does success look like?
   (Opens editor)
   
⚡ What are your constraints?
   (Opens editor)

📱 Domain-Specific Questions (PWA)

🔌 Offline capabilities needed?
   [Full offline support with background sync]
   
📲 Installation requirements?
   [Installable with push notifications]
   
🔄 Data synchronization strategy?
   [Background sync with conflict resolution]
   
📦 Asset caching strategy?
   [Cache-first for assets, network-first for data]

✨ Generating PRD...

✅ PRD Created: prds/initial-20251205-pwa-app.md
📊 Sections generated: 8
💾 Saved locally and uploaded to S3
```

**Output Structure**:
```markdown
---
prd_id: prd-20251205-abc123
version: v1
created_at: 2025-12-05T14:30:22Z
domain: pwa
project_name: "Family Advent Calendar PWA"
---

# PRD: Family Advent Calendar PWA

## Executive Summary
[AI-generated from user's "What are you building" answer]

## Business Context
### Vision
[User's input]

### Success Criteria
[User's input]

### Constraints
[User's input]

## Technical Approach (Domain: PWA)
[AI-generated with domain template hints - CONCISE version]
- Service Worker for offline functionality
- IndexedDB for local storage (5-50MB)
- Background Sync API for data synchronization

## Technology Stack
[AI-recommended, domain-aware - TOP 3 ONLY]
- Framework: Next.js with PWA plugin
- State: Zustand with persistence
- Offline DB: Dexie.js

## Top 3 Risks
[Domain-specific, critical only]
1. iOS Safari limitations → Feature detection
2. Service Worker updates → Versioned caches  
3. Storage quotas → Monitor usage

## Architecture Decisions
[High-level only at this stage]

## Open Questions
[AI-generated based on missing context]
```

---

### Feature 2: Development Snapshot Command

**Command**: `copidock snapshot create`

**Flags**:
- `--hydrate` - Upload to S3 for rehydration (default: true)
- `--comprehensive` - Include file contents (default: true)
- `--message <msg>` - Snapshot description

**Auto-Detection Logic**:
```python
def create_snapshot(repo_root):
    # 1. Check for active PRD
    prd_ref = load_active_prd(repo_root)
    
    # 2. Analyze git changes
    git_context = analyze_git_changes(repo_root)
    
    # 3. Detect work area (from git paths)
    work_area = detect_work_area(git_context['file_paths'])
    
    # 4. Generate focused snapshot
    snapshot = generate_snapshot(
        prd_reference=prd_ref,
        git_context=git_context,
        work_area=work_area
    )
    
    # 5. Save and upload
    save_snapshot(snapshot)
    if hydrate:
        upload_to_s3(snapshot)
```

**Output Structure**:
```markdown
---
snapshot_id: snap-20251206-091234
prd_reference: prds/initial-20251205-pwa-app.md
prd_version: v1
created_at: 2025-12-06T09:12:34Z
thread_id: abc-123
work_area: authentication
change_impact: medium
files_modified: 5
commits_analyzed: 3
---

# Snapshot: Authentication Implementation

## Context
Working on: User authentication with JWT
PRD Reference: v1 (prds/initial-20251205-pwa-app.md)
Divergence: Adding OAuth providers (not in original PRD)

## Changes This Session
- Implemented JWT token generation
- Added OAuth2 Google provider
- Created user session middleware
- Updated API authentication endpoints
- Added auth integration tests

## Files Modified (5)
- src/auth/jwt.ts (new)
- src/auth/oauth.ts (new)
- src/middleware/session.ts (modified)
- src/api/routes/auth.ts (modified)
- tests/auth.test.ts (new)

## Git Analysis
[Recent commits, diffs, patterns detected]

## Next Steps (AI-suggested)
1. Add refresh token rotation
2. Implement rate limiting on auth endpoints
3. Add password reset flow
4. Update PRD to reflect OAuth addition

## Embedded Source Files
[File contents for LLM context]
```

---

### Feature 3: PRD Update Command

**Command**: `copidock prd update`

**Purpose**: Evolve PRD based on development reality

**Flags**:
- `--review-snapshots` - Analyze recent snapshots for divergence (default: true)
- `--interactive` - Prompt for changes (default: true)

**Flow**:
```
🔄 Updating PRD

Current PRD: v1 (prds/initial-20251205-pwa-app.md)

📊 Analyzing 12 recent snapshots...

🔍 Detected Divergences:
  1. OAuth authentication added (not in PRD)
  2. Real-time sync using WebSockets (PRD assumes polling)
  3. PostgreSQL used instead of suggested IndexedDB

💡 Suggested Updates:
  ✓ Add "Authentication" section with OAuth flow
  ✓ Update sync strategy to WebSocket-based
  ✓ Revise data layer architecture
  ✓ Add new risks: OAuth token management, WebSocket scaling

Review and approve changes? [Y/n]: Y

✨ Generating updated PRD...

✅ PRD Updated: prds/updated-20251206-auth-sync.md (v2)
📊 Changes: 4 sections added/modified
💾 Previous version archived
```

---

## 🎯 User Workflows

### Workflow 1: Starting a New Project

```bash
# Day 1: Create PRD
cd my-advent-calendar
git init
copidock prd create --domain pwa --interactive

# Answers 3 core questions + 4 PWA questions
# Gets: prds/initial-20251205-pwa-app.md

# Day 1-7: Development
git commit -m "Initial setup"
# ... code code code ...
git commit -m "Add calendar component"

# Day 2: Create snapshot for LLM context
copidock snapshot create --hydrate
# Gets: snapshots/20251206-calendar-component.md
# AI can now understand project context

# Day 7: More development
copidock snapshot create --hydrate
copidock snapshot create --hydrate

# Day 8: Review progress, update PRD
copidock prd update --review-snapshots
# AI suggests: "Add offline calendar caching section?"
# Gets: prds/updated-20251208-offline-caching.md (v2)
```

### Workflow 2: Ongoing Development (No PRD Changes)

```bash
# Daily workflow - just snapshots
copidock snapshot create --hydrate  # Multiple times per day

# When working with AI:
# 1. Create snapshot
# 2. Use: "copidock rehydrate restore LATEST"
# 3. AI gets full context from snapshot
```

### Workflow 3: Major Pivot

```bash
# Business decision: Move from PWA to native mobile
copidock prd create --domain mobile-app --based-on prds/initial-20251205-pwa-app.md

# Interactive flow:
# - AI migrates relevant sections
# - Asks mobile-specific questions
# - Generates: prds/pivot-20251215-native-mobile.md (v3)
```

---

## 🔧 Implementation Plan

### Phase 1: Command Separation (Week 1)

**Tasks**:
- [ ] Create `copidock/cli/commands/prd.py` module
- [ ] Implement `prd create` command
- [ ] Implement `prd list` command  
- [ ] Implement `prd show` command
- [ ] Move domain template logic to PRD creation only
- [ ] Update `snapshot create` to remove `--stage` and `--domain` flags

**Breaking Changes**:
- Remove: `copidock snapshot create --stage initial`
- Remove: `copidock snapshot create --domain pwa`
- Add: `copidock prd create --domain pwa`

### Phase 2: File Structure Migration (Week 1)

**Tasks**:
- [ ] Create `/prds/` directory structure
- [ ] Keep `/rehydrations/` → `/snapshots/` for now (rename later)
- [ ] Update state.json to include `active_prd` field
- [ ] Create CURRENT symlink for active PRD
- [ ] Migration script for existing users

### Phase 3: Simplified Domain Templates (Week 2)

**Tasks**:
- [ ] Update `pwa.yml` with concise synthesis hints
- [ ] Add `_short` and `_full` versions for each section
- [ ] Update `merge_synthesis_hints()` to use concise versions by default
- [ ] Add `--detail-level` flag: `concise`, `standard`, `comprehensive`

**Template Structure**:
```yaml
# Before (overwhelming)
synthesis_hints:
  technical_approach: |
    [1000 chars of detailed patterns]

# After (concise + expandable)
synthesis_hints:
  technical_approach_short: |
    - Service Worker for offline
    - IndexedDB for storage
    - Background Sync API
  
  technical_approach_full: |
    [Full detailed version for --detail-level comprehensive]
```

### Phase 4: PRD Update Command (Week 3)

**Tasks**:
- [ ] Implement `prd update` command
- [ ] Snapshot analysis for divergence detection
- [ ] Interactive update flow with AI suggestions
- [ ] PRD versioning system (v1, v2, v3...)
- [ ] Archive old PRD versions

### Phase 5: Auto-Detection Enhancement (Week 3)

**Tasks**:
- [ ] Smart detection: "No PRD? Suggest `copidock prd create`"
- [ ] Smart detection: "Has PRD? Default to `copidock snapshot create`"
- [ ] Remove need for manual stage selection
- [ ] Improve git analysis for work area detection

### Phase 6: Documentation & Migration (Week 4)

**Tasks**:
- [ ] Update README with new command structure
- [ ] Write migration guide for existing users
- [ ] Update domain template creation guide
- [ ] Create tutorial videos/examples
- [ ] Deprecation warnings for old flags

---

## 📊 Success Metrics

**User Experience**:
- ⏱️ Time to create PRD: <5 minutes (vs 10+ with confusing flags)
- 🎯 Command clarity: 95%+ users understand PRD vs Snapshot difference
- 🔄 Adoption: 80%+ new projects use `prd create` command
- 📉 Support questions: 50% reduction in "which command should I use?"

**Technical Quality**:
- 🏗️ Code separation: 100% separation of PRD and snapshot logic
- 📦 File organization: Clean /prds/ and /snapshots/ structure
- 🔌 Extension points: Easy to add new domains/architectures
- 🧪 Test coverage: 90%+ for new commands

**Output Quality**:
- 📄 PRD conciseness: 60% reduction in word count (focused content)
- ✅ PRD completeness: 90%+ sections filled appropriately
- 🎨 Snapshot focus: 80% relevant context, 20% noise ratio
- 🔄 PRD accuracy: 85%+ reflects actual project state after updates

---

## 🚨 Risks & Mitigations

### Risk 1: Breaking Changes for Existing Users
**Impact**: High  
**Probability**: Certain  
**Mitigation**:
- Provide deprecation warnings for 2 releases
- Auto-migration script for existing projects
- Clear migration documentation
- Backward compatibility shim for 1 release cycle

### Risk 2: User Confusion During Transition
**Impact**: Medium  
**Probability**: High  
**Mitigation**:
- Prominent changelog and migration guide
- Tutorial showing new workflow
- Helpful error messages: "Did you mean `copidock prd create`?"
- Community support / FAQ

### Risk 3: Increased Complexity (2 Commands vs 1)
**Impact**: Low  
**Probability**: Medium  
**Mitigation**:
- Two commands is actually SIMPLER (clear separation)
- Smart defaults reduce flag usage
- Auto-detection eliminates manual decisions
- Better naming makes intent obvious

### Risk 4: PRD Versioning Overhead
**Impact**: Low  
**Probability**: Low  
**Mitigation**:
- Optional feature (can ignore and just use latest)
- Automated by `prd update` command
- Archive old versions, don't require management
- Symlink CURRENT for easy reference

---

## 🔮 Future Enhancements (Post-MVP)

### Phase 2+ Features:
1. **Collaborative PRDs**: Multi-stakeholder input
2. **PRD Templates**: Beyond domain templates (startup PRD, enterprise PRD)
3. **Visual Diff**: Show PRD evolution over versions
4. **Integration**: Auto-create Jira/Linear tickets from PRD
5. **Learning**: Analyze past PRDs to improve suggestions
6. **Cost Estimation**: Infrastructure cost predictions from PRD
7. **Compliance Checker**: HIPAA/PCI-DSS validation for domain PRDs

---

## 📚 Technical Details

### Database Schema (state.json evolution)

```json
{
  "version": "2.0",
  "thread_id": "abc-123",
  "project": {
    "name": "Advent Calendar PWA",
    "domain": "pwa",
    "created_at": "2025-12-05T14:30:22Z"
  },
  "prd": {
    "active": "prds/updated-20251206-auth-sync.md",
    "version": "v2",
    "history": [
      "prds/initial-20251205-pwa-app.md",
      "prds/updated-20251206-auth-sync.md"
    ]
  },
  "snapshots": {
    "latest": "snapshots/20251206-091234-api-endpoints.md",
    "count": 23
  },
  "profile": "default"
}
```

### Command Routing Logic

```python
# copidock/cli/main.py
app = typer.Typer()

# PRD management
prd_app = typer.Typer()
app.add_typer(prd_app, name="prd", help="PRD creation and management")

@prd_app.command("create")
def prd_create(
    domain: Optional[str] = typer.Option(None, "--domain"),
    interactive: bool = typer.Option(True, "--interactive"),
    architecture: Optional[str] = typer.Option(None, "--architecture"),
    based_on: Optional[str] = typer.Option(None, "--based-on"),
):
    """Create new PRD with domain-specific guidance"""
    # Implementation

@prd_app.command("update")
def prd_update(
    review_snapshots: bool = typer.Option(True, "--review-snapshots"),
    interactive: bool = typer.Option(True, "--interactive"),
):
    """Update PRD based on development progress"""
    # Implementation

# Snapshot management (existing, simplified)
@app.command("snapshot")
def snapshot_create(
    action: str = typer.Argument("create"),
    hydrate: bool = typer.Option(True, "--hydrate"),
    comprehensive: bool = typer.Option(True, "--comprehensive"),
    message: Optional[str] = typer.Option(None, "--message"),
):
    """Create development snapshot (git-aware)"""
    # Remove: --stage, --domain, --interactive flags
    # Auto-detect everything
```

---

## ✅ Definition of Done

This PRD is complete when:

- [ ] **Commands work**: `copidock prd create` and simplified `copidock snapshot create` functional
- [ ] **File structure**: Clean `/prds/` and `/snapshots/` directories
- [ ] **Domain templates**: Simplified to concise versions (top 3 risks, essential tech stack)
- [ ] **Auto-detection**: No manual `--stage` needed, smart defaults work
- [ ] **Documentation**: README, migration guide, tutorials complete
- [ ] **Migration**: Existing users can upgrade with provided script
- [ ] **Tests**: 90%+ coverage for new commands
- [ ] **User testing**: 5+ users successfully create PRD and snapshots with new commands

---

## 📝 Open Questions

1. **Q**: Should old `/rehydrations/` be renamed to `/snapshots/` immediately?  
   **A**: Phase 2, with backward compatibility symlink

2. **Q**: How to handle projects without explicit PRD?  
   **A**: Allow snapshots without PRD reference (but suggest creating one)

3. **Q**: Should `prd update` be automatic or manual?  
   **A**: Manual with AI suggestions (human in the loop)

4. **Q**: What happens to domain context in snapshots after PRD separation?  
   **A**: Snapshots reference PRD domain but don't re-ask questions

5. **Q**: Versioning strategy for PRDs (semantic? date-based?)?  
   **A**: Simple v1, v2, v3... with descriptive filenames

---

## 🎯 Next Actions

**Immediate** (This Week):
1. Review and approve this PRD
2. Create GitHub issues for Phase 1 tasks
3. Begin implementation of `prd create` command
4. Design simplified domain template format

**Short-term** (Next 2 Weeks):
1. Complete Phase 1 & 2 implementation
2. Simplify domain templates (concise versions)
3. Write migration guide
4. Beta test with 3-5 users

**Medium-term** (Next Month):
1. Release v2.0 with new architecture
2. Complete Phase 3 & 4 (PRD update, auto-detection)
3. Gather feedback and iterate
4. Plan Phase 2+ enhancements

---

*This is a living PRD - version 1.0*  
*Created: 2025-12-05*  
*Next review: After Phase 1 implementation*
