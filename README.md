# MindKeep

**MindKeep** is a local-first, on-premise **AI workplace-memory system for SMEs** — it turns real
employee work (documents, files, notes, approvals) into permission-aware, searchable organizational
knowledge, with a local LLM (Ollama) and human review before anything becomes Work Memory.
Demo tenant: **LongDuem (ลองดื่ม)**, a coconut farm + coconut-water business.

> Status: **greenfield rebuild**, Step 3 skeleton. No Phase 1 features implemented yet — this repo
> currently boots empty but is correctly structured. The old "LongRian" project is reference-only.

## Documentation (source of truth)

All product/system decisions live in [`docs/`](docs/):

| Doc | What |
|---|---|
| [REQUIREMENTS](docs/REQUIREMENTS.md) | what / who / why + roles |
| [SYSTEM_SPEC](docs/SYSTEM_SPEC.md) | features, journeys, permission model |
| [SCOPE](docs/SCOPE.md) | Phase 1 in/out scope |
| [PROJECT_MAP](docs/PROJECT_MAP.md) | monorepo + module layout |
| [ARCHITECTURE](docs/ARCHITECTURE.md) | web/api/pgvector/storage/jobs/LLM |
| [DATA_MODEL](docs/DATA_MODEL.md) · [API_SPEC](docs/API_SPEC.md) | entities/enums · endpoints |
| [ROADMAP](docs/ROADMAP.md) · [DECISIONS](docs/DECISIONS.md) | phases · ADRs |
| [ACCEPTANCE_CRITERIA](docs/ACCEPTANCE_CRITERIA.md) | Phase 1 pass checklist |
| [MASTER_PROMPT](docs/MASTER_PROMPT.md) | Claude Code bootstrap prompt |

## Stack

Next.js (web) · FastAPI (api) · PostgreSQL + pgvector · Ollama (local LLM) · Docker Compose.

## Run the skeleton (local)

```bash
cd infra
cp .env.example .env          # then edit secrets
docker compose --env-file .env up --build
# api:  http://localhost:8080/health
# web:  http://localhost:3000
# + local AI (optional):  add  -f docker-compose.ollama.yml
```

## Layout

```text
frontend/  Next.js frontend        backend/   FastAPI backend (modular monolith)
packages/  shared code (optional)  infra/     docker + env
docs/      source of truth         scripts/   dev automation
data/      sample data (committed) private/   local-only sensitive (gitignored)
```
