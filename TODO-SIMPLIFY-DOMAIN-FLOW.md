# TODO: Simplify Domain Template Flow

## Current State (Too Complex)

The domain template system is **working** but the output is **overwhelming** for users:

### What We Have Now
```markdown
## 🎯 Domain: Progressive Web App
## Operator Instructions
## Technical Approach (1000+ chars)
## Technology Stack (800+ chars)
## Risks (1200+ chars)
## Best Practices (1100+ chars)  
## Anti Patterns (600+ chars)
```

**Problem**: Too much information dumped at once. User wanted clarity, got a textbook.

## What Users Actually Need

### Phase 1: Initial Stage (Greenfield)
**User Input** (20%):
- Focus, Output, Constraints
- 4 domain-specific answers (offline strategy, installation, sync, caching)

**AI Output** (80%):
- ✅ **Concise** technical approach (3-5 key points, not 10)
- ✅ **Top 3 risks** with mitigations (not 6)
- ✅ **Essential tech stack** (framework + 2-3 tools, not exhaustive list)
- ❌ Skip: Anti-patterns, detailed best practices, testing checklists

### Phase 2: Development Stage
**Keep it focused**:
- Git analysis (what changed)
- Domain context (if relevant to changes)
- Actionable next steps

## Simplification Strategy

### Option A: Tiered Information (Progressive Disclosure)
```markdown
## Technical Approach (Essential)
- Service Worker for offline
- IndexedDB for storage
- Background Sync API
[Show more: detailed patterns, caching strategies...]

## Risks (Top 3 Critical)
1. iOS Safari limitations → Feature detection
2. Service Worker updates → Versioned caches
3. Storage quotas → Monitor usage
[Show more: 3 additional risks...]
```

### Option B: Smart Filtering by Stage
**Initial Stage**: Only show high-level guidance
- Technical approach: Architecture overview only
- Risks: Top 3 critical risks
- Tech stack: Recommended framework only

**Development Stage**: Show relevant details
- Only include domain sections if files match domain (e.g., service-worker.js → show PWA patterns)

### Option C: Separate Reference Document
**In Snapshot** (Actionable):
- Concise technical approach (5 lines)
- Top 3 risks
- Recommended framework

**Reference File** (Optional):
- Generate `PWA_REFERENCE.md` alongside snapshot
- Full details: all risks, anti-patterns, testing checklist
- User can reference when needed

## Recommendation: Option B + Progressive Disclosure

1. **Simplify template content** (update `pwa.yml`):
   - `technical_approach_short`: 3-5 key bullets
   - `technical_approach_full`: Complete patterns
   - `risks_critical`: Top 3 only
   - `risks_complete`: All 6 risks

2. **Smart rendering logic**:
   - Initial stage: Use `_short` and `_critical` versions
   - Development stage: Use full versions only if domain-relevant files changed

3. **Progressive disclosure UI**:
   - Add `[▼ Show detailed guidance]` markers in markdown
   - Keep snapshot readable, detailed info available on demand

## Action Items

- [ ] Create `pwa-simplified.yml` with tiered content structure
- [ ] Update `merge_synthesis_hints()` to respect complexity level
- [ ] Add `--detail-level` CLI flag: `concise`, `standard`, `comprehensive`
- [ ] Test with real user flow (initial → development stages)
- [ ] Get user feedback on simplified output

## Current Output Analysis

**What's Good**:
- ✅ Domain answers captured correctly
- ✅ Frontmatter clean and structured
- ✅ All sections rendering

**What's Too Much**:
- ❌ 5 large sections (4000+ total chars of guidance)
- ❌ Exhaustive lists (every framework option, every risk)
- ❌ Information overload for greenfield projects
- ❌ Hard to find actionable next steps

## User Feedback Quote
> "this is something that I imagined more in the beginning. Oh boy we will need to simplify this a lot. to be the flow clearer"

**Translation**: Working great technically, but UX needs refinement. Less is more.

## Next Session Goals
1. Design simplified template structure
2. Implement tiered information rendering
3. Add detail-level control
4. Test with "just enough info" principle
