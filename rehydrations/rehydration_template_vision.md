---
thread_id: e1eae2f9-f949-417a-ad7d-9b3b122780bb
snapshot_id: 3b56b292-28e2-42cc-afda-f49e6df471b3
version: 1
created_at: 2025-09-06T13:39:25.545995Z
repo: copidock
branch: main
goal: "Test thread creation"
context_tags: ["infra","aws","dynamodb","lambda","apigw"]
related_paths:
  - infra/main.tf
  - modules/dynamo_db/main.tf
  - modules/compute_lambda/main.tf
token_budget_hint: 6k   # ~6k tokens target for this whole context
---

# Rehydrate: Test thread creation (v1)

## Operator Instructions (paste into model before sources)
You are a senior backend engineer helping me continue this thread.  
**Goal:** Test thread creation & baseline operations.  
**Do:**
- Read Decisions & Constraints.
- Read Sources. Use them as the single source of truth.
- Propose next steps and produce concrete code edits.
**Don’t:** re-architect infra, add services, or change AWS region.

**Primary Tasks**
1. Verify DynamoDB and S3 flows; suggest minimal hardening (retry, size guards).
2. Produce a Makefile target to zip and deploy lambdas.
3. Draft API key protection for API Gateway (usage plan + header).

**Expected Outputs**
- A Makefile snippet.
- Terraform HCL patch for API key usage plan.
- Brief checklist for negative tests.

## Current State (summary)
- Phase 1 infra live (S3, DDB, Lambda, API GW).
- Phase 2 lambdas now real, curls validated (thread, notes, snapshot, rehydrate).
- Rehydrate URL returns the latest MD.

## Decisions & Constraints
- **Region:** eu-central-1
- **Storage:** DynamoDB pay-per-request, S3 private.
- **No VPC**. Pure serverless.
- **Keep cost low** (no OpenSearch, no Aurora).
- **Interfaces now:** HTTP API only.

## Open Questions
1. Add API keys now or after VS Code client?
2. PITR for DDB tables needed during POC?
3. Snapshot payload cap (e.g., 8 MB) acceptable?

## Sources
### Source 1: modules/dynamo_db/main.tf (excerpt)
```hcl
# ... paste real snippet here (~100-200 lines max) ...


## Personal Notes

# Minimal changes to your Lambda to emit this
- Add YAML front-matter and the **Operator Instructions** section to your `generate_rehydratable_markdown()` output.
- Replace placeholder file blocks with **actual snippets** (the VS Code client will send them soon; for now you can paste small real excerpts).

# “A+ Snapshot” quick rubric
- **< 6–8k tokens total** (models stay sharp; Copilot behaves better).
- **1–3 clear tasks** + **explicit outputs**.
- **Decisions/constraints listed** (saves pointless debate).
- **Real code snippets** relevant to those tasks.
- **Dates & versions explicit** (you already do this).

# Near-term polish (fast wins)
- Add **note size guard** in `notes_handler`.
- In `rehydrate`, support explicit version fetch:  
  `GET /rehydrate/{thread_id}/{date}/v{NNN}`.
- In `/snapshot`, include `ISO Timestamp` in the MD (you already do—nice).
- CLI/VS Code button that:
  - collects changed files + open editors,
  - builds the **Sources** sections automatically,
  - opens the presigned URL.

If you want, I can hand you a tiny **Makefile** target to package and update all 4 Lambdas (zip + `aws lambda update-function-code`), and a one-page **“How to paste into Copilot/Claude”** cheat—both tailored to this snapshot format.
::contentReference[oaicite:0]{index=0}
