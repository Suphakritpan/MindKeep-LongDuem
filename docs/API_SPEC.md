# API_SPEC.md

> **หน้าที่ของไฟล์นี้:** endpoint หลักที่ต้องมีใน Phase 1
> เป็น *แผน endpoint* (ยังไม่ใช่โค้ดจริง — Phase นี้ไม่ implement) request/response shape จะ lock ตอน implement
> naming pattern อิงของเดิมที่พิสูจน์แล้ว (`docs/api/LongRian_API_Spec.md`) แต่ตัดให้เหลือเฉพาะ Phase 1

---

## Conventions

```text
Base URL (host dev) : http://localhost:8080
Versioning          : ทุก route อยู่ใต้ /api/v1/...
Auth                : JWT bearer — Authorization: Bearer <token> จาก POST /api/v1/auth/login
Errors              : unified error envelope (โค้ด error กลาง)
Health              : GET /health (unversioned) · GET /api/v1/ai/health (AI/Ollama status)
Permission          : ทุก endpoint เช็ก permission ใน backend service ก่อนเสมอ (ดู SYSTEM_SPEC §1.3)
```

---

## Phase 1 Endpoints ✅

### Auth — `/api/v1/auth`
```text
POST /login        # email+password → JWT
GET  /me           # current user + role + departments
PATCH /me          # update own profile
POST /logout
```

### Users — `/api/v1/users`
```text
GET  /             # list (scoped by permission)
POST /             # create user        [requires users:manage]
GET  /{id}
PATCH /{id}        # update / role      [requires users:manage]
POST /{id}/deactivate                  [requires users:manage]
```

### Departments — `/api/v1/departments`
```text
GET  /             # list departments user can see
GET  /{id}
POST /             # create             [requires departments:manage]
PATCH /{id}        #                    [requires departments:manage]
```

### Documents — `/api/v1/documents`
```text
# CRUD
POST   /                 # create note/document
GET    /                 # list (permission + visibility filtered)
GET    /{id}
PATCH  /{id}             # edit own unlocked doc (approved → new version)
DELETE /{id}             # soft-delete own unlocked doc

# Files / versions / preview
POST /upload             # upload supported file (PDF/JPG/JPEG/PNG/WEBP/DOCX/XLSX/CSV)
GET  /{id}/download
GET  /{id}/versions

# Lifecycle (review before memory)
POST /{id}/submit        # → pending_review
POST /{id}/approve       # → approved_to_memory   [department_lead / memory:approve]
POST /{id}/lock          # [department_lead]
POST /{id}/unlock        # [department_lead]

# RAG ingestion
POST /ingest             # queue extract→summarize→embed (after approval)
GET  /ingest/{document_id}/jobs   # ingestion job status
```

### Memory — `/api/v1/memory`
```text
GET  /              # list approved memory entries (permission scoped)
GET  /{id}          # entry + source link + summary + tags
GET  /pending       # items awaiting review     [department_lead]
```

### AI — `/api/v1/ai`
```text
GET  /health        # Ollama / model status
POST /search        # permission-aware retrieval over allowed memory
POST /summarize     # summarize a document/content
POST /ask           # RAG answer with source citations
```

### Chat — `/api/v1/chat`
```text
POST /stream                 # streaming answer (RAG, permission-scoped)
POST /sessions               # new chat session
GET  /sessions               # chat history (must not disappear)
GET  /sessions/{id}/messages
```

### Activities — `/api/v1/activities`
```text
GET  /              # activity timeline (own / department scoped)
```

### Files — `/api/v1/files`
```text
POST   /upload
GET    /
GET    /{id}/download
DELETE /{id}
```

### Jobs — `/api/v1/jobs`
```text
GET  /              # background job list + status
GET  /{id}          # job detail (status, attempts, error)
POST /{id}/retry    # retry failed job
```

### Audit — `/api/v1/audit`
```text
GET  /              # sensitive-action audit log   [audit:view / owner_manager]
```

### Health (unversioned)
```text
GET /health
```

---

## Phase 2+ Endpoints — placeholder (ไม่ทำรอบนี้)

> ใส่ไว้เพื่อให้เห็นทิศทาง — endpoint จริงจะ spec ตอนถึง phase นั้น (ดู [ROADMAP.md](ROADMAP.md))

```text
Phase 2 Finance  : /api/v1/finance/...            (records, summary, VAT, dashboard)
                   /api/v1/finance-records/...     (categories, vendors, records lifecycle)
                   /api/v1/ocr/...                 (receipt upload, jobs, confirm)
Phase 3 Handover : /api/v1/handover/...            (generate report, read)
Phase 6 Field    : /api/v1/field/...               (tasks, records, sync)
Phase 7 Admin    : /api/v1/admin/...               (overview, users, audit, system health, backup)
```

---

## Endpoint ↔ Module Map

| Prefix | Backend module ([PROJECT_MAP.md](PROJECT_MAP.md)) | Phase |
|---|---|---|
| `/auth` | `modules/auth` | 1 ✅ |
| `/users` | `modules/users` | 1 ✅ |
| `/departments` | `modules/departments` | 1 ✅ |
| `/documents`, `/files` | `modules/documents`, `modules/files` | 1 ✅ |
| `/memory` | `modules/memory` | 1 ✅ |
| `/ai`, `/chat` | `modules/ai`, `modules/chat` | 1 ✅ |
| `/activities`, `/jobs` | `modules/audit` / core jobs | 1 ✅ |
| `/audit` | `modules/audit` | 1 ✅ |
| `/finance*`, `/ocr` | `modules/finance` | 2 🔜 |
| `/handover` | `modules/handover` | 3 🔜 |
| `/field` | `modules/field` | 6 🔜 |
| `/admin` | `modules/admin` | 7 🔜 |
