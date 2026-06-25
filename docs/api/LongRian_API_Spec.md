# MindKeep API Overview

Generated from `apps/backend/app/main.py` and `apps/backend/app/routes/*.py`.
This lists the routers, their prefixes, and their endpoints as they exist in code.
For request/response shapes, read the matching `apps/backend/app/schemas/*.py`.

- **Base URL (host dev):** `http://localhost:8080`
- **Versioning:** all routes under `/api/v1/…`
- **Auth:** JWT bearer (`middleware/auth.py`). `Authorization: Bearer <token>` from `POST /api/v1/auth/login`.
- **Errors:** unified `AppError` envelope with 8-digit codes (`core/error_codes.py`).
- **Health:** `GET /health` (unversioned) and `GET /api/v1/ai/health` (AI/Ollama status).

## Auth — `/api/v1/auth`
`POST /login` · `POST /nfc` · `GET /me` · `PATCH /me` · `POST /logout`

## Dashboard — `/api/v1/dashboard`
`GET /summary`

## Documents — `/api/v1/documents`
CRUD: `POST /` · `GET /` · `GET /{id}` · `PATCH /{id}` · `DELETE /{id}`
Lifecycle: `POST /{id}/submit` · `POST /{id}/approve` · `POST /{id}/use-as-template` · `POST /{id}/lock` · `POST /{id}/unlock`
Files/versions: `POST /upload` · `GET /{id}/download` · `GET /{id}/versions` · `GET /{id}/layout` · `GET /{id}/layout-page/{n}`

### RAG ingestion (Phase 1, also under `/api/v1/documents`)
`POST /ingest` · `GET /ingest/{document_id}/jobs`
Document permission grants: `POST /permissions` · `DELETE /permissions/{id}`

## Approvals — `/api/v1/approvals`
`POST /` · `GET /pending` · `POST /{approval_request_id}/action`

## Finance
The `/api/v1/finance` prefix is shared by three routers:

- **finance.py** — `POST /chat/stream` · `POST /pricing` · `POST /vat` · `POST /cost-pricing` · `POST /pl`
- **finance_summary.py** — `GET /income-channels` · `POST /income` · `GET /income` · `GET /summary` · `POST /vat/calculate` · `GET /vat/periods` · `GET /notifications` · `GET /reports`
- **finance_advanced.py** — `POST /insights/upload-csv` · `GET /insights` · `GET /tax-rules` · `POST /tax-estimate` · `GET /tax-estimates`

### Finance workspace — `/api/v1/finance/workspace`
`GET /overview` · `GET /activity`

### Finance records — `/api/v1/finance-records`
Reference data: `GET /categories` · `GET /vendors` · `GET /vendors/lookup` · `POST /vendors` · `PATCH /vendors/{id}`
Records: `POST /records` · `GET /records` · `GET /records/{id}` · `PATCH /records/{id}` · `POST /records/{id}/submit` · `POST /records/{id}/approve` · `POST /records/{id}/post`

## OCR / Bill Scanner — `/api/v1/ocr`
`POST /receipts/upload` · `GET /jobs` · `GET /jobs/{job_id}` · `GET /documents/{id}` · `PATCH /documents/{id}/fields` · `POST /documents/{id}/confirm` · `GET /documents/{id}/preview` · `POST /documents/{id}/cash-log-preview` · `POST /documents/{id}/confirm-cash-log`

## AI workspace — `/api/v1/ai`
`GET /health` · `POST /search` · `POST /summarize` · `POST /suggest-edit` · `POST /suggestions/{id}/apply` · `POST /ask`

## Chat — `/api/v1/chat`
`POST /stream` · `POST /sessions` · `GET /sessions` · `GET /sessions/{id}/messages`

## Librarian (Knowledge Library) — `/api/v1/librarian`
`POST /search` · `POST /search/pgvector` (guarded by `use_pgvector_retrieval`)

## Tasks — `/api/v1/tasks`
`POST /` · `GET /` · `GET /{id}` · `PATCH /{id}` · `DELETE /{id}` · `POST /{id}/comments` · `GET /{id}/comments`

## Events (Calendar) — `/api/v1/events`
`POST /` · `GET /` · `GET /{id}` · `PATCH /{id}` · `DELETE /{id}`

## Activities — `/api/v1/activities`
`GET /`

## Audit — `/api/v1/audit`
`GET /` (admin only)

## Files — `/api/v1/files`
`POST /upload` · `GET /` · `GET /{id}/download` · `DELETE /{id}`

## Structured tables — `/api/v1/tables`
`POST /` · `GET /` · `GET /{id}` · `PATCH /{id}/rows/{row_id}` · `POST /{id}/rows`

## Workspaces — `/api/v1/workspaces`
`GET /{department_id}` · `GET /{department_id}/work-records` · `POST /{department_id}/work-records`

## Admin — `/api/v1/admin`
User mgmt (`admin.py`): `POST /users` · `GET /users` · `PATCH /users/{id}/deactivate` · `GET /activities` · `GET /activities/{user_id}` · `GET /audit-logs` · `POST /handover`
Data Studio (`admin_data_studio.py`, read-only inspector): `GET /data-studio/tables` · `GET /data-studio/tables/{key}/rows` · `GET /data-studio/tables/{key}/rows/{id}` · `PATCH /data-studio/tables/users/rows/{id}` · `POST /data-studio/tables/users/rows/{id}/reset-password`

## Legal — `/api/v1/legal`
`POST /chat/stream` · `POST /compliance-check` · `POST /contract-review`

## Marketing — `/api/v1/marketing`
`POST /chat/stream` · `POST /campaign-brief` · `POST /content-plan`
