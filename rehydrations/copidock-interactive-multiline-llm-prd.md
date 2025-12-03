# PRD: Enhanced Interactive Mode for Copidock
**Product Requirements Document**  
*Feature: Multiline Input Support & LLM-Assisted Prompt Generation*

---

## 🎯 Executive Summary

Enhance Copidock's `--interactive` mode to support natural multiline input and optional LLM-assisted prompt generation, making it easier for developers to express complex project requirements and goals without being constrained by single-line input limitations.

---

## 📋 Problem Statement

### Current Pain Points
1. **Single-line Input Limitation**: Users trying to enter detailed project requirements or multi-point constraints hit Enter and lose their flow
2. **Lost Context**: Complex requirements (like "beautiful lean design, PWA portability, auth, fast and reliable...") require awkward formatting in a single line
3. **Unnatural UX**: Bullet-style thinking doesn't map to single-line prompts
4. **No LLM Assistance**: Interactive mode could benefit from LLM help in refining/structuring user inputs

### User Story
> "As a developer starting a new project, I want to enter my project vision using natural bullet points and have the system help me structure my thoughts, so that I can capture comprehensive requirements without friction."

---

## 🎨 Proposed Solution

### Feature 1: Multiline Input Support

**Technical Approach**: Replace `typer.prompt()` with custom `prompt_multiline()` function

**User Experience**:
```
🎯 What are you building? (Project vision) [New application]:
> (Enter your vision below. Use multiple lines if needed. Submit with blank line)
| Advent-calendar joyous PWA application
| - Research and guide family activities during advent
| - Bring family members closer together
| - Focus on meaningful traditions and quality time
|
✓ Captured 4 lines

🏆 What does success look like? (Expected outcomes) [Working MVP]:
> (Enter expected outcomes. Submit with blank line)
| Beautiful lean design
| PWA portability (works offline, installable)
| Authentication system
| Fast and reliable performance
| Interactive UX flow that's joyful to use
|
✓ Captured 5 lines
```

**Technical Requirements**:
- Detect when user presses Enter without content → submit input
- Detect when user presses Enter with content → add line and continue
- Support Ctrl+D or double-Enter as alternative submission methods
- Preserve indentation and formatting
- Show line counter during input
- Allow easy editing (backspace, arrow keys)

### Feature 2: LLM-Assisted Prompt Generation (Optional)

**Trigger**: Add `--llm-assist` flag to interactive mode

**User Experience**:p
```
🎯 What are you building? (Project vision) [New application]:
> (Enter your vision. Type /help for AI assistance)
| family advent calendar app
|
✓ Captured input

🤖 AI Suggestion (press Enter to accept, 'e' to edit, 's' to skip):
───────────────────────────────────────────────────────
📱 Advent Calendar Family Activities PWA

A progressive web application that helps families discover 
and plan meaningful activities during the advent season, 
fostering connection and creating lasting holiday traditions.

Key Features:
• Daily activity suggestions tailored to family preferences
• Offline-first design for reliability
• Simple, joyful user interface
• Progress tracking and memory creation
───────────────────────────────────────────────────────

[Accept / Edit / Skip]? a
✓ Using AI-enhanced description
```

**Technical Requirements**:
- Optional `--llm-assist` flag (default: off, respects user preference)
- Integration point for LLM API (OpenAI, Anthropic, or local models)
- Structured prompt engineering for each interactive field type
- Fallback to raw input if LLM unavailable
- Cache LLM responses to avoid redundant calls
- Show cost/token usage if using paid APIs

---

## 🔧 Technical Design

### Architecture

```
┌─────────────────────────────────────────┐
│  CLI Entry Point                        │
│  (copidock snapshot create --interactive│
│   [--llm-assist])                       │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  Interactive Flow Controller            │
│  (copidock/interactive/flow.py)         │
│  - Orchestrates prompt sequence         │
│  - Determines which prompts use         │
│    multiline vs. single-line            │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│  Prompt Input Layer                     │
│  (copidock/interactive/prompts.py)      │
│                                          │
│  prompt_multiline()                     │
│  - Handles multi-line input capture     │
│  - Blank line submission                │
│  - Visual feedback                      │
│                                          │
│  prompt_single()                        │
│  - Fallback to typer.prompt()           │
│  - For simple fields (persona select)   │
└───────────────┬─────────────────────────┘
                │
                ▼ (if --llm-assist)
┌─────────────────────────────────────────┐
│  LLM Assistant Layer                    │
│  (copidock/interactive/llm_assist.py)   │
│                                          │
│  enhance_prompt()                       │
│  - Takes raw user input                 │
│  - Returns structured enhancement       │
│  - Handles API errors gracefully        │
│                                          │
│  format_for_field_type()                │
│  - Vision prompts → structured overview │
│  - Constraints → bullet list            │
│  - Outcomes → acceptance criteria       │
└─────────────────────────────────────────┘
```

### Implementation Plan

#### Phase 1: Multiline Input (MVP)
**Files to Create/Modify**:
1. `copidock/interactive/prompts.py` (NEW)
   - `prompt_multiline()` function
   - `prompt_single()` wrapper
   - Line buffer management
   - Submission detection logic

2. `copidock/interactive/flow.py` (MODIFY)
   - Replace `typer.prompt()` calls with `prompt_multiline()`
   - Update for fields: focus, output, constraints
   - Keep single-line for: persona selection

**Technical Specifications**:
```python
def prompt_multiline(
    prompt_text: str,
    default: Optional[str] = None,
    show_line_numbers: bool = False,
    submit_on_blank: bool = True,
    allow_ctrl_d: bool = True
) -> str:
    """
    Capture multiline input from user.
    
    Args:
        prompt_text: Display text for prompt
        default: Default value if user submits empty
        show_line_numbers: Display line numbers during input
        submit_on_blank: Submit when blank line entered
        allow_ctrl_d: Allow Ctrl+D as submission method
    
    Returns:
        Combined multiline string (lines joined with \n)
    
    Behavior:
        - Press Enter on blank line → submit
        - Ctrl+D → submit
        - Type normally → add line and continue
        - Shows "✓ Captured N lines" on completion
    """
```

#### Phase 2: LLM Assistance (Optional Enhancement)
**Files to Create**:
1. `copidock/interactive/llm_assist.py` (NEW)
   - `enhance_input()` - main enhancement function
   - `format_vision_prompt()` - for project vision
   - `format_constraints_prompt()` - for requirements
   - `format_outcomes_prompt()` - for success criteria
   - API client abstraction (supports multiple LLM providers)

2. `copidock/config/llm_config.yml` (NEW)
   - LLM provider configuration
   - API key management (env vars)
   - Model selection
   - Token limits
   - Cost tracking

**Configuration Example**:
```yaml
llm:
  enabled: false  # Opt-in feature
  provider: "openai"  # openai | anthropic | local
  model: "gpt-4-turbo-preview"
  max_tokens: 500
  temperature: 0.7
  
  prompts:
    vision:
      system: "You are a product designer helping structure project vision..."
      user_template: "Enhance this project vision: {user_input}"
    
    constraints:
      system: "You are a technical advisor helping identify key requirements..."
      user_template: "Structure these constraints: {user_input}"
    
    outcomes:
      system: "You are a project manager defining success criteria..."
      user_template: "Define measurable outcomes for: {user_input}"
```

---

## 📊 Success Metrics

### User Experience Metrics
- **Time to Complete Interactive Flow**: Target <3 minutes (currently ~5 minutes with editing)
- **Input Revision Rate**: Reduce by 50% (fewer back-and-forth edits)
- **Feature Adoption**: 70%+ of users try multiline input within first week
- **LLM Assist Adoption**: 30%+ of power users enable `--llm-assist`

### Technical Metrics
- **Input Accuracy**: 95%+ of multiline inputs captured correctly
- **LLM Response Time**: <2 seconds for enhancement generation
- **Error Rate**: <1% for LLM API failures (with graceful fallbacks)

---

## 🚀 Implementation Timeline

### Sprint 1: Multiline MVP (3-5 days)
- [ ] Day 1-2: Implement `prompt_multiline()` function
- [ ] Day 2-3: Integrate into `flow.py` (focus, output, constraints)
- [ ] Day 3-4: Manual testing & UX polish
- [ ] Day 4-5: Unit tests & documentation

### Sprint 2: LLM Integration (5-7 days)
- [ ] Day 1-2: Design LLM prompt templates
- [ ] Day 2-3: Implement `llm_assist.py` module
- [ ] Day 3-4: Add `--llm-assist` flag & configuration
- [ ] Day 4-5: Integration testing with OpenAI API
- [ ] Day 5-6: Error handling & fallbacks
- [ ] Day 6-7: Documentation & examples

### Sprint 3: Polish & Rollout (2-3 days)
- [ ] Add inline help (`/help` command during input)
- [ ] Cost/token tracking for LLM usage
- [ ] Release notes & user guide
- [ ] Beta testing with early adopters

---

## 🎓 User Education

### Documentation Additions

**Quick Start Example**:
```bash
# Basic multiline input
$ copidock snapshot create --comprehensive --interactive

# With LLM assistance
$ copidock snapshot create --comprehensive --interactive --llm-assist
```

**Interactive Prompts Guide**:
```markdown
## Multiline Input Tips

1. **Press Enter to add new lines**
   - Keep typing naturally across multiple lines
   
2. **Submit with blank line**
   - Press Enter on empty line to finish
   - Or use Ctrl+D as alternative

3. **Use bullet points naturally**
   - Start lines with `-` or `•` for lists
   - Formatting is preserved

4. **LLM Assistance (optional)**
   - Add `--llm-assist` flag
   - Get structured suggestions for your inputs
   - Accept, edit, or skip AI enhancements
```

---

## ⚠️ Risks & Mitigations

### Risk 1: Confusion About Submission
**Impact**: Medium  
**Mitigation**: 
- Clear inline instructions: "(Submit with blank line)"
- Visual indicator showing input mode
- Escape hatch: always allow Ctrl+C to cancel

### Risk 2: LLM API Costs
**Impact**: Medium  
**Mitigation**:
- Opt-in only (`--llm-assist` required)
- Token usage display after each call
- Configurable model selection (cheaper options)
- Local LLM support (free alternative)

### Risk 3: Terminal Compatibility
**Impact**: Low  
**Mitigation**:
- Test on Windows, macOS, Linux terminals
- Fallback to single-line if terminal doesn't support advanced input
- Document minimum terminal requirements

---

## 🔮 Future Enhancements

### Phase 3 Ideas (Post-MVP)
1. **Template Library**: Pre-built prompts for common project types
   - "New PWA", "API Service", "CLI Tool", etc.
   - One-command start: `copidock init --template pwa`

2. **Smart Suggestions**: Learn from user's previous inputs
   - "You usually work on React projects. Use those patterns?"
   - Context-aware defaults based on repo history

3. **Collaborative Mode**: Share interactive sessions
   - Generate shareable session links
   - Multiple team members contribute to snapshot creation

4. **Voice Input**: Speak your requirements
   - Natural language → structured prompts
   - Hands-free workflow for brainstorming

---

## ✅ Acceptance Criteria

### Multiline Input
- [ ] User can enter multiple lines without interruption
- [ ] Blank line submission works reliably
- [ ] Ctrl+D submission works on Unix systems
- [ ] Line count feedback is shown
- [ ] Formatting/indentation is preserved
- [ ] Works on Windows, macOS, Linux terminals

### LLM Assistance
- [ ] `--llm-assist` flag activates LLM features
- [ ] User can accept/edit/skip AI suggestions
- [ ] Graceful fallback when API unavailable
- [ ] Configuration file supports multiple providers
- [ ] Token usage is displayed to user
- [ ] Works without internet (local LLM option)

### Developer Experience
- [ ] Clear documentation with examples
- [ ] Unit tests cover edge cases
- [ ] Error messages are helpful
- [ ] Performance impact <200ms for non-LLM mode
- [ ] Backward compatible (old commands still work)

---

## 📚 References

### Related Issues
- TODO.txt line 112: "Replace typer.prompt() with custom prompt_multiline()"
- User feedback: "I need better experience in multiline inputs"

### Technical Dependencies
- `typer`: CLI framework (existing)
- `rich`: Terminal formatting (existing)
- `openai` or `anthropic`: LLM API clients (new, optional)
- `prompt_toolkit`: Advanced terminal input (optional, for future)

### Inspiration
- Git commit message editors (multiline with submission)
- Poetry's interactive init (`poetry init`)
- GitHub CLI's PR creation (`gh pr create`)
- Inquirer.js prompt library (JavaScript)

---

## 🤝 Stakeholders

**Primary**: Copidock CLI users (developers starting new projects)  
**Secondary**: DevOps teams using Copidock for documentation  
**Approver**: Project maintainer (@Droshow)

---

*Last Updated: December 2, 2025*  
*Status: Draft - Ready for Review*  
*Version: 1.0*
