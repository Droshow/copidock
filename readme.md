# Copidock

A serverless note management and retrieval system built with AWS Lambda, DynamoDB, and S3.

## Project Structure

```
copidock/
├── infra/                     # Terraform infrastructure
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── modules/
│       ├── storage/           # S3 bucket configuration
│       ├── dynamo_db/         # DynamoDB tables
│       ├── compute_lambda/    # Lambda functions and IAM
│       └── api/               # API Gateway configuration
├── db/
│   └── schema.sql             # DynamoDB table schemas
├── lambdas/
│   ├── common/
│   │   ├── db.py             # DynamoDB utilities
│   │   └── s3.py             # S3 utilities
handlers/
    ├── thread_start_handler.py   # POST /thread/start
    ├── snapshot_handler.py       # POST /snapshot
    ├── rehydrate_handler.py      # GET /rehydrate/{thread}/latest
└── notes_handler.py (optional)  # POST /notes, GET /notesthread/{id}/rehydrate
├── cli/
│   └── copidock.py           # Typer CLI interface
├── config/
│   └── copidock.example.yml  # Configuration template
├── build/                    # Lambda deployment packages
├── Makefile                  # Build and deployment automation
└── README.md
```

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