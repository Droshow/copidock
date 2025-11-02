# 🪄 Copidock — Context Rehydration CLI for Developers & AI Creators (Beta)

> **AI + Infra + Human Memory → One Flow**

In the era when AI develops code, we need to treat prompts like git.

Copidock turns your development state into something you can **save, rehydrate, and continue later** — like a snapshot of your mental model.  
When you run a snapshot command, it collects your goal, reasoning, and relevant code, and turns it into a structured **rehydratable document** (PRD-style).  
Later, you or another developer can "rehydrate" that snapshot and pick up where it left off — no lost context, no guessing.

---

## 🌍 Why This Scaffolding Exists

We're building a **serverless note and context management system** powered by:
- AWS **Lambda**, **DynamoDB**, and **S3**
- Terraform-based IaC deployment
- AI-guided context synthesis and rehydration

Each snapshot bridges **prompt engineering** and **software state management**.  
It captures:
- **Who** — persona (e.g., Cloud Infra Engineer, Backend Dev)
- **What** — goal, focus, expected outputs
- **When/Where** — commit, repo, branch
- **How** — reasoning and operator instructions

---

## ⚙️ Core Commands

### 1. Create a new snapshot

Generate a rehydratable snapshot of your current thread and codebase:

```bash
copidock snapshot create --comprehensive --hydrate
```

This will:
- Gather recent Git context
- Generate a PRD-style markdown file
- Upload it to S3 for future rehydration
- Save a local copy under `copidock/rehydrations/`

### 2. Interactive mode (recommended)

For structured guidance and persona loading:

```bash
copidock snapshot create --interactive --stage initial --comprehensive --hydrate
```

- `--stage initial` → Greenfield / PRD setup template
- `--stage development` → Ongoing implementation template
- `--comprehensive` → Includes Git diffs, file snippets, and commits
- `--hydrate` → Uploads snapshot + updates local index

**Note:** Use `--stage development` when continuing an existing project where you want to track git changes and file modifications. Use `--stage initial` for greenfield projects or when you want a clean template without git context.

### 3. Rehydrate from saved snapshots

```bash
# List available snapshots
copidock rehydrate list

# Restore latest snapshot
copidock rehydrate restore LATEST

# Restore specific snapshot
copidock rehydrate restore 20241102-143022-pomodoro-app
```

---

## 🧠 Two-Button Workflow

### Start a thread
```bash
copidock thread start "Implement Pomodoro App Infrastructure"
```

### Create a snapshot
```bash
copidock snapshot create --comprehensive --hydrate
```

**Result:** a portable `.md` snapshot that stores your entire development reasoning — rehydratable anytime.

---

## 🏗️ Infrastructure Overview

Built for reproducibility and scalability.

| Component | Description |
|-----------|-------------|
| **Storage** | S3 buckets for snapshots, logs, and assets |
| **Database** | DynamoDB tables for threads, events, and notes |
| **Compute** | AWS Lambda functions as stateless handlers |
| **API** | API Gateway fronting the serverless endpoints |
| **Infra** | Managed via Terraform for full IaC reproducibility |

Deploy with:
```bash
cd infra
terraform init
terraform apply
```

---

## 💬 Developer Notes

- Copidock is currently in **Beta** — expect structure changes.
- Focus for now: snapshot creation, hydration, and state integrity.
- Avoid checking in internal Copidock files.

Add this to your `.gitignore`:
```gitignore
# Copidock
copidock/rehydrations/
.copidock/state.json
```

---

## 🧩 Philosophy

> "AI doesn't replace reasoning — it remembers it."

Copidock externalizes your working memory so you can:

- **Pause** a task, switch context, and resume later without losing your train of thought.
- **Share** project reasoning with teammates through portable, rehydratable documents.
- **Combine** reproducible infrastructure with semantic intent — Terraform for systems, Copidock for minds.

---

## ⚡ Summary

- **Purpose** → Persistent context for human + AI collaboration
- **Core Command** → `copidock snapshot create --comprehensive --hydrate`
- **Infra** → Serverless (Lambda, S3, DynamoDB, API Gateway)
- **State** → Locally cached + S3 synchronized
- **Status** → Beta — focus on stability, snapshot logic, and rehydration accuracy

---

## 🤝 Contributing

For early collaborators testing snapshot and rehydrate flows locally:

1. **Clone the repository**
   ```bash
   git clone <repo-url>
   cd copidock
   ```

2. **Install dependencies**
   ```bash
   pip install -e .
   ```

3. **Test locally**
   ```bash
   copidock thread start "Test thread"
   copidock snapshot create --hydrate
   copidock rehydrate list
   ```

4. **Report issues**
   - Focus on snapshot accuracy and rehydration consistency
   - Test across different project stages and personas
   - Verify local artifact management works correctly

---

---

## 🌉 DevsBridge

**Built with structure, intent, and a bit of magic. ✨**

Copidock is a **productivity enhancement tool** designed to bridge the gap between human reasoning and AI development workflows. Part of the DevsBridge ecosystem — tools that connect developers, infrastructure, and intelligent automation.

---

## 📄 License

Copyright © 2025 DevsBridge

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

---

<div align="center">

🌉 **DevsBridge** — *Connecting Code, Context & Intelligence*

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Beta](https://img.shields.io/badge/Status-Beta-yellow.svg)]()

</div>