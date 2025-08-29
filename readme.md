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
│   ├── notes_handler.py      # POST /notes, GET /notes
│   ├── sync_handler.py       # POST /sync
│   ├── retrieve_handler.py   # POST /retrieve
│   └── rehydrate_handler.py  # POST /thread, POST /thread/{id}/rehydrate
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

- `POST /notes` - Store new notes
- `GET /notes` - Retrieve notes
- `POST /sync` - Sync repository data
- `POST /retrieve` - Search and retrieve content
- `POST /thread` - Create decision thread
- `POST /thread/{id}/rehydrate` - Rehydrate thread context

## Configuration

Copy `config/copidock.example.yml` to `config/copidock.yml` and update with your settings.