# Copidock Enhancement: Domain Templates & 80/20 AI-Human PRD Generation

**Date**: December 3, 2025  
**Status**: Planning / Design Phase  
**Goal**: Enable 80% AI automation with 20% human expertise for complex PRD generation

---

## 🎯 Core Vision

Transform Copidock's `--interactive --stage initial` mode into a **Business Context → AI-Generated PRD pipeline** where:

- **Humans provide**: Vision, constraints, success criteria (business context)
- **AI generates**: Technical architecture, risks, implementation tasks (technical scaffolding)

### Key Principle: Pareto 80/20
> "80% automation with 20% human expertise where it matters most"

---

## ✅ What's Working Now (MVP Complete)

1. **Multiline input support** using Click's `click.edit()`
2. **Clean YAML frontmatter** with proper literal block scalars (`|`)
3. **Stage-aware prompts** (initial vs development)
4. **Three core questions**:
   - 🎯 What are you building?
   - 🏆 What does success look like?
   - ⚡ What are your constraints?

### Current Strengths
- Fast input (5-10 minutes vs 2-4 hours manual PRD)
- Consistent structure across all PRDs
- Reduced cognitive load for PMs/founders
- Works well for **greenfield projects, MVPs, small teams**

---

## 🚀 Recommended Enhancements (Priority Order)

### **Phase 2A: Domain Templates** 🔥 **HIGHEST PRIORITY**

**Problem**: Generic AI lacks domain-specific patterns and best practices

**Solution**: Domain-specific question sets and synthesis hints

```bash
# Usage
copidock snapshot create --interactive --stage initial --domain pwa --hydrate
copidock snapshot create --interactive --stage initial --domain healthcare --hydrate
copidock snapshot create --interactive --stage initial --domain fintech --hydrate
```

**Implementation**:
- Create `copidock/templates/domains/` directory
- Each domain has `.yml` file with:
  - Additional specialized questions
  - Synthesis hints for AI
  - Common patterns/anti-patterns
  - Technology recommendations

**Example Domains**:
1. **PWA** (Progressive Web Apps)
   - Offline capabilities, service workers, sync strategy
2. **Healthcare**
   - HIPAA compliance, PHI handling, audit logging
3. **Fintech**
   - PCI-DSS, transaction integrity, regulatory compliance
4. **API Service**
   - Rate limiting, versioning, authentication patterns
5. **ML Pipeline**
   - Data versioning, model monitoring, retraining strategy

---

### **Phase 2B: Architecture Style Selection**

**Problem**: Different projects need different architectural patterns

**Solution**: Let users select architecture style

```bash
copidock snapshot create --interactive --stage initial \
  --domain pwa \
  --architecture serverless \
  --hydrate
```

**Architecture Options**:
- Monolith
- Microservices
- Serverless (Lambda/Cloud Functions)
- JAMstack
- Event-driven
- CQRS/Event Sourcing

AI adapts recommendations based on selection.

---

### **Phase 2C: Iterative Refinement**

**Problem**: First-pass AI output might miss nuances

**Solution**: Allow human review → AI refinement loop

```bash
# Step 1: Generate initial PRD
copidock snapshot create --interactive --stage initial --hydrate

# Step 2: Human reviews and adds notes to LATEST file

# Step 3: Refine with AI
copidock prd refine --input LATEST --focus "add security requirements"
copidock prd refine --input LATEST --focus "expand risk analysis"
```

---

### **Phase 2D: Reference Architecture Injection**

**Problem**: AI doesn't know about existing systems/past decisions

**Solution**: Allow referencing existing docs

```bash
copidock snapshot create --interactive --stage initial \
  --reference "existing-services.yaml" \
  --reference "architecture-decisions.md" \
  --hydrate
```

AI considers existing context when generating recommendations.

---

### **Phase 2E: Enhanced NFRs (Non-Functional Requirements)**

**Problem**: Missing performance/scale expectations

**Solution**: Add 4th question

```
⚙️ Performance & Scale Expectations
   (e.g., "10K concurrent users", "API <200ms", "99.9% uptime")
```

---

## 📊 When This Approach Works Best

### ✅ **Sweet Spot Use Cases**
- New greenfield projects
- Early-stage startups (speed > perfection)
- Solo founders / small teams
- Prototypes & MVPs
- Internal tools

### ⚠️ **Requires Augmentation For**
- Enterprise projects → Add compliance review
- Regulated industries → Domain templates mandatory
- Large teams → Collaborative mode needed
- Complex integrations → Reference existing architecture

### ❌ **Not Sufficient Alone For**
- Safety-critical systems (medical devices, aerospace)
- High-security contexts (banking backend, government)
- Heavy regulatory burden without domain templates

---

## 🏗️ Technical Implementation: Domain Template Example

**File**: `copidock/templates/domains/pwa.yml`

```yaml
domain: pwa
display_name: "Progressive Web App"
description: "Offline-capable, installable web applications"

additional_questions:
  - prompt: "🔌 Offline capabilities needed?"
    help_text: "Should app work without internet? What features offline?"
    key: offline_strategy
    default: "Full offline support with background sync"
  
  - prompt: "📱 Installation requirements?"
    help_text: "Add to home screen? Push notifications? App icon?"
    key: installation_features
    default: "Installable with push notifications"
  
  - prompt: "🔄 Data sync strategy?"
    help_text: "How does data sync when back online?"
    key: sync_approach
    default: "Background sync with conflict resolution"

  - prompt: "📦 Asset caching strategy?"
    help_text: "What should be cached? Cache-first or network-first?"
    key: caching_strategy
    default: "Cache-first for assets, network-first for data"

synthesis_hints:
  technical_approach: |
    **PWA Architecture Recommendations**:
    - Service Worker for offline functionality
    - IndexedDB for local data storage
    - Background Sync API for data synchronization
    - Push Notification API for engagement
    - Web App Manifest for installation
    - Cache API for asset management
    
  technology_stack: |
    **Recommended Stack**:
    - Framework: React/Vue/Svelte with PWA plugin
    - State Management: Redux/Zustand with persistence
    - Offline DB: Dexie.js (IndexedDB wrapper)
    - Build Tool: Vite/Webpack with Workbox
    - Backend: RESTful API or GraphQL with subscriptions
    
  risks: |
    **PWA-Specific Risks**:
    - iOS Safari limitations (push notifications, storage limits)
    - Service Worker update complexity
    - Cache invalidation strategy
    - Storage quota management (5-50MB varies by browser)
    - Network/cache race conditions
    
  best_practices: |
    - Implement stale-while-revalidate pattern
    - Use versioned cache names for updates
    - Handle offline errors gracefully with user feedback
    - Test on low-end devices and slow networks
    - Provide manual sync trigger for users

anti_patterns:
  - "Caching everything (storage limits)"
  - "Not handling offline state in UI"
  - "Ignoring iOS Safari differences"
  - "No cache eviction strategy"
```

---

## 📋 Implementation Checklist

### Phase 2A: Domain Templates (Week 1-2)
- [ ] Create `copidock/templates/domains/` directory
- [ ] Implement domain template loader
- [ ] Add `--domain` flag to CLI
- [ ] Create 5 initial domain templates:
  - [ ] PWA
  - [ ] API Service
  - [ ] Healthcare
  - [ ] Fintech
  - [ ] ML Pipeline
- [ ] Update synthesis generator to merge domain hints
- [ ] Test with real projects
- [ ] Document domain template creation guide

### Phase 2B: Architecture Selection (Week 3)
- [ ] Add `--architecture` flag
- [ ] Create architecture pattern hints
- [ ] Integrate with synthesis generation

### Phase 2C: Iterative Refinement (Week 4)
- [ ] Implement `copidock prd refine` command
- [ ] Add focused section regeneration
- [ ] LLM integration for refinement

---

## 🎓 Success Metrics

**Target Outcomes**:
- ⏱️ **Time to PRD**: <10 minutes (from 2-4 hours)
- 📊 **Completeness**: 80%+ sections filled automatically
- ✅ **Accuracy**: 90%+ of AI suggestions accepted without edits
- 🔄 **Adoption**: 70%+ of new projects use interactive mode
- 🎯 **Domain Coverage**: Support 10+ domains within 3 months

---

## 💡 Key Insights

1. **Separation of Concerns Works**: Business people provide vision, AI provides technical structure
2. **Domain Context is Critical**: Generic AI is good, domain-aware AI is great
3. **Iteration > Perfection**: First pass doesn't need to be perfect if refinement is easy
4. **Standards Emerge**: Consistent PRD structure enables team velocity
5. **Pareto Rules**: 80% automation captures most value, 20% human input adds critical context

---

## 🔮 Future Possibilities (Phase 3+)

- **Collaborative mode**: Multiple stakeholders contribute
- **Learning from history**: Analyze past PRDs to improve suggestions
- **Integration with project management**: Auto-create tickets from PRD tasks
- **Voice input**: Speak your vision, AI structures it
- **Visual architecture diagrams**: Generate C4 or system diagrams from PRD
- **Cost estimation**: AI suggests infrastructure costs based on requirements

---

## 📚 Related Work

- **Existing PRD**: `/rehydrations/copidock-interactive-multiline-llm-prd.md`
- **Implementation**: 
  - `copidock/interactive/flow.py`
  - `copidock/interactive/prompts.py`
  - `copidock/cli/main.py`
- **Templates**: `copidock/templates/personas/`

---

## 🤝 Next Actions

1. **Immediate**: Review and approve domain template approach
2. **Week 1**: Design 3-5 priority domain templates (PWA, API, Healthcare)
3. **Week 2**: Implement domain template system
4. **Week 3**: Beta test with real projects
5. **Week 4**: Iterate based on feedback

---

*Generated by human analysis of Copidock's evolution*  
*Focus: 80% AI automation, 20% human expertise*  
*Goal: Make complex PRD generation accessible to everyone*
