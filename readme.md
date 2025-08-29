rehydra/
├─ infra/
│  ├─ main.tf
│  ├─ variables.tf
│  ├─ outputs.tf
├─ db/
│  └─ schema.sql
├─ lambdas/
│  ├─ common/
│  │  ├─ db.py
│  │  └─ s3.py
│  ├─ notes_handler.py         # POST /notes, GET /notes
│  ├─ sync_handler.py          # POST /sync
│  ├─ retrieve_handler.py      # POST /retrieve
│  ├─ rehydrate_handler.py     # POST /thread, POST /thread/{id}/rehydrate
├─ cli/
│  └─ rehydra.py               # Typer CLI
├─ config/
│  └─ rehydra.example.yml
├─ Makefile
└─ README.md
