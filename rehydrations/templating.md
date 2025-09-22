artin.drotar@CVX-1065 copidock % copidock snapshot create --comprehensive --persona senior-backend-dev

======================================================================
🧠 INTELLIGENT TEMPLATE SYSTEM OUTPUT
======================================================================

📋 Operator Instructions
--------------------------------------------------
## Operator Instructions

You are a **Senior Backend Developer** working on: **development task**

**Primary Focus**: infrastructure and deployment  
**File Focus**: Terraform and configuration files  
**Repository**:  (branch: main)

### Guidelines

**Do:**
- Focus on infrastructure and deployment implementation
- Review Terraform and configuration files changes carefully  
- Consider production stability and rollback plans
- Follow established patterns in the codebase

**Don't:**
- Break existing running services and dependent infrastructure
- Add unnecessary complexity or dependencies
- Ignore service outages and deployment failures
- Skip testing for critical paths

### Tasks for This Session

- Review infrastructure changes for breaking changes
- Validate resource dependencies
- Plan deployment sequence

### Expected Outputs

Tested infrastructure changes with deployment plan

**Multi-area changes detected** - review cross-component impacts carefully.

---



📋 Current State
--------------------------------------------------
## Recent Progress
**Activity Pattern**: 3 features

**Recent Commits:**
- `76b32a2b`: rehydration for smart templating (3 hours ago by Droshow)
- `e2ede0e3`: templating (3 hours ago by Droshow)
- `d6e84d0f`: snapshot_backend, - [x] **Day 3**: Add question mining and commit analysis (24 hours ago by Droshow)
- `62116204`: smart synthetic features added (6 days ago by Droshow)

## Current Changes
- **13 files** modified across **5 categories**
- **Infrastructure**: 4 files ⚠️
  - `infra/providers.tf`
  - `infra/outputs.tf`
  - `infra/variables.tf`
  - ... and 1 more
- **Backend/Lambda**: 4 files 🚀
  - `setup.py`
  - `lambdas/thread_start_handler.py`
  - `lambdas/rehydrate_handler.py`
  - ... and 1 more
- **Frontend**: 1 files 
  - `.copidock/state.json`
- **Configuration**: 2 files 
  - `requirements.txt`
  - `copidock/config/config.toml`
- **Documentation**: 2 files 
  - `rehydrations/open-flows.md`
  - `readme.md`

## Development Velocity
- **5 commits** in recent history
- **Focus areas**: rehydration, smart, templating


📋 Decisions Constraints
--------------------------------------------------
## Decisions & Constraints

- **Infrastructure**: Using Terraform for IaC management
- **Deployment**: Serverless architecture with AWS Lambda
- **Backend**: Python-based Lambda functions
- **API**: RESTful API design with proper error handling
- **Cost**: Optimize for serverless cost efficiency
- **Performance**: Target sub-second response times
- **Security**: Follow AWS security best practices

## Technical Constraints
- **Platform**: AWS serverless architecture
- **Runtime**: Python 3.9+ for Lambda functions
- **Budget**: Development/testing environment
- **Timeline**: Iterative development with working increments


📋 Open Questions
--------------------------------------------------
## Open Questions

### QUESTIONs

1. **mining and commit analysis**
   - *Commit d6e84d0f:0*
   - Context: `snapshot_backend, - [x] **Day 3**: Add question mining and commit analysis`

### NOTEs

2. **s - Store new notes**
   - *lambdas/notes_handler.py:13*
   - Context: `POST /notes - Store new notes`

3. **s - Retrieve notes**
   - *lambdas/notes_handler.py:14*
   - Context: `GET /notes - Retrieve notes`

4. **(event)**
   - *lambdas/notes_handler.py:19*
   - Context: `return create_note(event)`

5. **s(event)**
   - *lambdas/notes_handler.py:21*
   - Context: `return get_notes(event)`

*... and 29 more questions found*