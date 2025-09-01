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