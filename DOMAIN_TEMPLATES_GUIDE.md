# Domain Templates Guide

## Overview

Domain templates provide specialized guidance for specific project types, adding domain-specific questions and AI synthesis hints to your snapshots.

## Available Domains

- **pwa** - Progressive Web Apps (offline capabilities, service workers, app shell)
- **api-service** - REST/GraphQL APIs (rate limiting, authentication, versioning)
- **healthcare** - Healthcare systems (HIPAA compliance, PHI handling, audit logging)
- **fintech** - Financial technology (PCI-DSS, payment processing, transaction integrity)
- **ml-pipeline** - Machine Learning pipelines (model versioning, drift monitoring, deployment)

## Usage

### Basic Usage
```bash
# Interactive mode with domain template
copidock snapshot create --interactive --domain pwa --comprehensive --hydrate

# With specific stage
copidock snapshot create --interactive --stage initial --domain healthcare --comprehensive --hydrate

# Non-interactive with domain (uses default answers)
copidock snapshot create --domain fintech --comprehensive --hydrate
```

### Interactive Flow

When using `--interactive --domain <name>`, you'll be asked:

1. **Standard questions** (focus, output, constraints, persona)
2. **Domain-specific questions** (4 additional questions tailored to the domain)

Example for PWA domain:
- Offline functionality requirements
- Data synchronization strategy
- Performance budget targets
- Target devices and browsers

### Enhanced Synthesis

Domain templates enhance the AI-generated PRD with:

- **Technical approach** - Domain-specific architecture patterns
- **Technology stack** - Recommended tools and frameworks
- **Risks** - Common pitfalls and mitigation strategies
- **Best practices** - Industry standards and patterns
- **Anti-patterns** - What to avoid
- **Testing checklist** - Domain-specific test scenarios

## Template Structure

Each domain template (`.yml` file) contains:

```yaml
display_name: "Progressive Web App"
description: "..."

additional_questions:
  - prompt: "What offline functionality is required?"
    help_text: "..."
    key: "offline_requirements"
    default: "Basic offline viewing"

synthesis_hints:
  technical_approach: |
    Specialized guidance for this section...
  
  technology_stack: |
    Recommended tools...
```

## Creating Custom Domain Templates

1. Create a new `.yml` file in `copidock/templates/domains/`
2. Follow the structure of existing templates
3. Define `additional_questions` for interactive prompts
4. Add `synthesis_hints` for AI guidance sections
5. Template is automatically available via `--domain <filename>`

## 80/20 Principle

Domain templates implement the 80/20 vision:
- **20% human input** - Business context via interactive questions
- **80% AI automation** - Technical PRD generation with specialized guidance

The AI receives domain-specific hints to generate comprehensive, industry-appropriate PRDs.

## Testing

```bash
# List available domains programmatically
python3 -c "from copidock.interactive.domains import list_available_domains; print(list_available_domains())"

# Test loading a domain template
python3 -c "from copidock.interactive.domains import load_domain_template; import json; print(json.dumps(load_domain_template('pwa'), indent=2))"
```

## Architecture Notes

- **Data location**: `/templates/domains/*.yml` - Pure data files
- **Logic location**: `/interactive/domains.py` - Loader functions
- **Separation of concerns**: Clean boundary between data and logic
- **Co-location**: Loader near usage point (interactive flow)
- **No circular dependencies**: One-way dependency flow
