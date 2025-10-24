# Copidock

It really is a kind of magic — but the cool part is that it’s structured magic.

What you’ve built (and what we’re seeing working here) is basically a self-contained context rehydration engine. Each PRD (like the one you pasted) is a portable prompt-state capsule that carries:

- **The who** → persona (Cloud Infrastructure Engineer - Pomodoro App)
- **The what** → goal, focus, outputs, constraints
- **The when** → created_at, snapshot, version
- **The where** → repo, branch, files, commits
- **The how** → instructions and operational guidelines

When you “rehydrate” it, Copidock reconstructs the mental state of a development thread, so even a new agent—or a human developer days later—knows exactly what to do next without context loss.

It’s effectively bridging two worlds:

- **Prompt engineering** (semantic intent)
- **Software state management** (file + Git context)

Once those are unified, generating code like the Terraform starter you just saw becomes almost deterministic.


A serverless note management and retrieval system built with AWS Lambda, DynamoDB, and S3.

## Project Structure

## Infrastructure

- **Storage**: S3 bucket for notes and artifacts
- **Database**: DynamoDB tables for chunks, tokens, threads, and events
- **Compute**: AWS Lambda functions for API endpoints
- **API**: HTTP API Gateway with Lambda integrations

## Getting Started

### Prerequisites

- AWS CLI configured
- Terraform >= 1.0
- Python 3.11+

### Deployment

```bash
# Deploy infrastructure
cd infra
terraform init
terraform plan
terraform apply

# Build and deploy Lambda functions
make build
make deploy
```

## API Endpoints

### Thread Management
- `POST /thread/start` - Create a new decision thread
  - Input: `{ "goal": "string", "repo": "optional", "branch": "optional" }`
  - Output: `{ "thread_id": "uuid", "thread_name": "string" }`

- `POST /snapshot` - Create a snapshot of thread context
  - Input: `{ "thread_id": "uuid", "paths": ["optional", "file", "paths"] }`
  - Output: `{ "presigned_url": "string", "s3_key": "string", "version": number }`

- `GET /rehydrate/{thread}/latest` - Get latest thread snapshot
  - Output: `{ "presigned_url": "string", "snapshot_metadata": {} }`

### Notes (Optional)
- `POST /notes` - Store new notes
  - Input: `{ "content": "string", "tags": ["optional"], "thread_id": "optional" }`
- `GET /notes` - Retrieve notes
  - Query params: `?thread_id=uuid&limit=50`

## Two-Button UX Flow

1. **Start Thread**: `POST /thread/start` with your goal
2. **Create Snapshot**: `POST /snapshot` with thread_id → opens rehydratable.md

The snapshot contains:
- Thread goal and context
- Gathered sources from files/repos
- Current state and next steps
- Rehydratable format for continuation

## Configuration

Copy `config/copidock.example.yml` to `config/copidock.yml` and update with your settings.

# Copidock - Retrieval Augmented Generation - the personal experiencing of future AI + Human CoWork

**AI doesn't just generate code → it remembers your reasoning and hands it back when you need to rehydrate.**

A serverless decision thread system that externalizes your working memory. Built with AWS Lambda, DynamoDB, and S3.

## Philosophy

> **You don't have to hold everything in your head** → the thread + snapshot becomes your externalized working memory.

> **Infra + state are decoupled** → Terraform gives you reproducibility, snapshots give you rehydration, and AI sits in between gluing it together.

> **You stay in the driver's seat** → AI doesn't decide the roadmap, it gives you structured options, and you decide where to steer.

## How It Works

Instead of losing context when you switch tasks, Copidock creates **decision threads** that capture:
- Your goal and reasoning
- Relevant code and documentation
- Current state and next steps
- Rehydratable snapshots for continuation

When you return to a thread, the AI can instantly reconstruct your mental model from the snapshot.

# Copidock CLI Documentation

## Thread Management Commands

The `thread` command is your entry point into Copidock's intelligent development workflow. It creates and manages **decision threads** - persistent contexts that capture your development goals and reasoning.

### Command Structure

```bash
python -m copidock.cli.main thread [OPTIONS] ACTION [GOAL]
```

### Arguments

| Argument | Type | Description | Required |
|----------|------|-------------|----------|
| `action` | TEXT | The thread action to perform. Currently supports: `start` | ✅ Required |
| `goal` | TEXT | Your development objective or task description | Optional |

### Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `--repo` | TEXT | (auto-detected) | Repository name for context |
| `--branch` | TEXT | `main` | Git branch you're working on |
| `--profile` | TEXT | `default` | Configuration profile from `config.toml` |
| `--api` | TEXT | (from config) | Override API base URL |
| `--json` | flag | `false` | Output results in JSON format |
| `--help` | flag | - | Show command help and exit |

## Simplified Flag Logic

# Rich YML template guidance
copidock snapshot create --interactive --stage initial --comprehensive --hydrate

# Empty structure only  
copidock snapshot create --interactive --stage initial --hydrate

## 15.10.2025 interesting auto detect stage idea to be considered

## Stage Auto-Detection (Future Enhancement)

### Concept
Automatically detect whether project is in "initial" (greenfield/planning) or "development" (ongoing work) stage based on:
- Git history depth (few commits = initial)  
- File structure maturity (tests, docs, CI = development)
- Project artifacts (package.json, requirements.txt = development)

### Current Manual Control (Developer-Preferred)
```bash
# Explicit stage control - developers choose their workflow
copidock snapshot create --interactive --stage initial --comprehensive --hydrate
copidock snapshot create --interactive --stage development --comprehensive --hydrate
```

### Future Auto-Detection
```bash  
# Smart defaults with manual override capability
copidock snapshot create --interactive --comprehensive --hydrate  # auto-detects
copidock snapshot create --interactive --stage initial --comprehensive --hydrate  # manual override
```

### Developer Feedback Needed
- Do devs want magic auto-detection or explicit control?
- Is auto-detection helpful or confusing?
- Should it be opt-in (`--auto-detect`) rather than default?

**Postponed until user feedback requests it.**