# Department Workspace — model and current state

How MindKeep organizes work by department for the LongDuem tenant. Reconciled with code
(`models/department.py`, `routes/workspaces.py`, `db/chroma.py`) and the core spec.

## Departments (LongDuem)

Single tenant, four real departments; each has its own ChromaDB memory collection and a primary owner.

| Department | Memory collection | Primary owner | MVP depth |
|---|---|---|---|
| Farm & Production | `memory_farm` | ตาชัย มั่นคง | seeded knowledge + activity + hub |
| Finance & Accounting | `memory_finance` | ป้าต้อย สุขสม | **full Finance MVP** |
| Legal & Procurement | `memory_legal` | ลุงศักดิ์ วงศ์ใหญ่ | hub + 3 agent endpoints |
| Marketing & Delivery | `memory_marketing` | หนูดี รักไทย | hub + 3 agent endpoints |

The admin/owner account sees all departments (used to test cross-department access).

## Data model

- `models/department.py` — `Department`, `Role`, `UserDepartmentRole` (a user's role within a department).
- All domain records carry `department_id` (and `user_id` / `owner_user_id`) so REST and RAG can filter by permission.
- `services/permission_service.py` is the single gate: regular users see only their department; AI/RAG retrieval uses the **same** rule (no permission to see Finance memory ⇒ AI cannot retrieve it either).

## Workspace API — `/api/v1/workspaces`

- `GET /{department_id}` — department workspace overview.
- `GET /{department_id}/work-records` — list work records.
- `POST /{department_id}/work-records` — add a work record.

Department-specific AI is exposed per hub: `/api/v1/legal/*`, `/api/v1/marketing/*`,
and the finance routers (`/api/v1/finance*`). Each agent (`agents/finance|legal|marketing.py`)
is selected by `agents/router.get_agent()`.

## Core data flow (per the spec)

`User action → backend service → structured record → activity log → Work Memory →
vector/RAG metadata → AI query source.` Example: ป้าต้อย uploads a bill → file asset →
OCR extract → categorize + VAT → user review → confirm → finance transaction + activity log +
`memory_finance` entry → vector store (retrievable under the correct permission).

## Status

- **Done:** department model, RBAC gate, per-department memory collections, workspace routes, Finance MVP.
- **Partial:** Farm/Legal/Marketing hubs are intentionally shallow (seeded knowledge + a few agent endpoints), not full tool suites.
- **Planned:** multi-tenant (`organizations` table) — currently single-tenant with implicit org.

See `docs/product/MindKeep_AI_Workspace_Core_Spec_v0.1.md` for the full product intent.
