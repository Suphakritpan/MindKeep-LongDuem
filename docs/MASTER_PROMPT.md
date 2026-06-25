# MASTER_PROMPT.md — Claude Code Bootstrap Prompt (MindKeep)

> **หน้าที่ของไฟล์นี้:** prompt ตั้งต้นสำหรับสั่ง Claude Code เริ่ม **repo ใหม่** ของ MindKeep
> วิธีใช้: คัดลอกส่วน **"PROMPT TO PASTE"** ด้านล่างไปวางใน Claude Code session ที่เปิดใน repo เปล่า
> ⚠️ Prompt นี้ออกแบบให้ "first run = Step 3 เท่านั้น" (skeleton + config) — **ไม่ implement Phase 1**

---

## How the 4-step program works

```text
Step 1  แยก requirement → docs/ (10 canonical docs)        ✅ DONE
Step 2  เขียน Master Prompt (ไฟล์นี้)                        ✅ DONE
Step 3  Claude Code สร้าง repo skeleton + docs + config     ◀── prompt ด้านล่างทำ "เฉพาะอันนี้"
Step 4  แตก Phase 1 เป็น implementation batches             ◀── prompt แยกทีหลัง (ดูท้ายไฟล์)
```

---

## PROMPT TO PASTE (Step 3 — Skeleton + Config only)

````text
You are bootstrapping a brand-new repository for **MindKeep** — a local-first, on-premise
AI workplace-memory system for SMEs. The demo company / case study is **LongDuem (ลองดื่ม)**,
a coconut farm + coconut-water business. This is a GREENFIELD rebuild; do NOT copy code from
any old "LongRian" project (reference only).

### Source of truth
The full requirements already exist as canonical docs. READ THEM FIRST and treat them as
authoritative; do not invent product decisions:
- docs/REQUIREMENTS.md        (what/who/why + roles)
- docs/SYSTEM_SPEC.md         (features + user journeys + permission model)
- docs/SCOPE.md               (Phase 1 in/out scope + file support)
- docs/PROJECT_MAP.md         (monorepo + backend module layout)  ◀── build the tree from this
- docs/ARCHITECTURE.md        (web/api/pgvector/storage/jobs/LLM)
- docs/DATA_MODEL.md          (entities + enums)
- docs/API_SPEC.md            (Phase 1 endpoints)
- docs/ROADMAP.md             (Phase 1–7 + build order)
- docs/DECISIONS.md           (ADR-001..016)
- docs/ACCEPTANCE_CRITERIA.md (Phase 1 pass checklist)

### YOUR TASK THIS RUN — Step 3 ONLY: repo skeleton + docs + base config
Create the project SKELETON and configuration only. Produce a repo that *boots empty* but is
correctly structured. Specifically:

1. **Monorepo tree** exactly as docs/PROJECT_MAP.md (flat layout):
   frontend/, backend/, packages/ (optional), infra/, docs/ (already exists),
   scripts/, data/, private/. Add a short README.md in each top-level folder describing its purpose.

2. **Backend skeleton** (backend/, FastAPI, Python 3.12):
   - app/main.py with a health route `GET /health` and `/api/v1` router mount only.
   - app/core/ (config via env, error envelope stub), app/db/ (session/base wiring, NO migrations).
   - Module folders under app/modules/ for ALL modules in PROJECT_MAP.md §2 (so the tree matches it):
       • Phase-1 modules (auth, users, departments, permissions, documents, files, memory, ai, chat,
         audit): create folder + placeholder __init__.py + a one-line docstring.
       • Later-phase modules (finance, handover, field, admin): create the folder + __init__.py only,
         with a one-line `# Phase N — placeholder, not implemented` marker.
     Do NOT implement routes/services/models/schemas for ANY module yet — placeholders only.
   - pyproject.toml (or requirements.txt) with FastAPI, uvicorn, SQLAlchemy, psycopg, pgvector,
     pydantic-settings — pinned, but no business deps beyond skeleton.

3. **Frontend skeleton** (frontend/, Next.js + TypeScript):
   - App Router with a single placeholder Home page only. No feature pages, no API wiring.
   - package.json named "mindkeep-web" (NEVER "longrian-*").

4. **Base config**:
   - `.gitignore` at repo root that INCLUDES `backend/app/uploads/`, `private/*`, `.env`, `node_modules/`,
     `__pycache__/`, `.venv/`, build dirs.
   - `.env.example` (DB url for postgres, OLLAMA host, storage path) — no real secrets.
   - infra/docker-compose.yml: postgres service on image `pgvector/pgvector:pg16`, api, web.
     Optional infra/docker-compose.ollama.yml overlay for local Ollama.
   - Root README.md: one-paragraph product line + pointer to docs/.

### HARD CONSTRAINTS — do NOT do these this run
- ❌ NO feature code (no real route handlers, services, or models).
- ❌ NO database migrations and NO schema creation.
- ❌ NO Phase 1 implementation (documents/memory/AI/chat logic).
- ❌ NO deep frontend pages beyond a single placeholder Home.
- ❌ NO new product decisions — if something is ambiguous, STOP and ask.

### Non-negotiable rules to honor in everything you scaffold (docs/ACCEPTANCE_CRITERIA.md §2)
- No AI retrieval without permission filter
- No Work Memory without human approval
- No sensitive company data to external AI by default
- No finance posting by LLM
- No hidden cross-department access
- No vector store acting as permission authority
- No route-level business logic overload
- pgvector is the retrieval index, never the permission authority
- Docs are part of "done"

### Definition of done for THIS run
- `backend/` boots and `GET /health` returns 200 with no business logic.
- `frontend/` builds and serves a placeholder Home.
- `docker compose up` brings up postgres (pgvector image) + api + web.
- Tree matches docs/PROJECT_MAP.md; no LongRian naming anywhere; uploads/ is gitignored.
- Then STOP and summarize what was created + propose the Step 4 batch plan (do not start it).
````

---

## Step 4 — Phase 1 implementation batches (สำหรับรอบถัดไป, ยังไม่รัน)

หลัง skeleton เสร็จ ค่อยแตก Phase 1 ตาม build order ใน [ROADMAP.md](ROADMAP.md) (Spec §17) เป็น batch ย่อย
สั่ง Claude Code ทำ **ทีละ batch** อย่ารวบ:

```text
Batch A  PostgreSQL + migrations + base models (enums จาก DATA_MODEL.md)
Batch B  auth + users + departments + permissions (capability grants)
Batch C  documents + files + StorageService (local FS)
Batch D  background job system (durable, status + retry)
Batch E  extraction + summary pipeline (per-type ตาม SCOPE.md §3.3)
Batch F  memory_entries + memory_chunks + pgvector embedding
Batch G  review-before-memory flow (submit → approve/reject → memory)
Batch H  permission-aware RAG + basic AI Chat + source citation
Batch I  Activity Timeline + Audit logs
Batch J  Validate Phase 1 acceptance criteria (docs/ACCEPTANCE_CRITERIA.md)
```

แต่ละ batch ต้องจบด้วย: code + tests + อัปเดต docs/roadmap status (docs rule: docs are part of done)

> เมื่อพร้อมเริ่ม Step 4 ค่อยเขียน prompt ต่อ batch (อ้าง docs + ระบุ "ทำเฉพาะ Batch X")
