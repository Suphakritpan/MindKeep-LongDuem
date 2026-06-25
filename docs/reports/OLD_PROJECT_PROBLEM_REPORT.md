# Old Project Problem Report — MindKeep / LongRian AI Workspace

**Date:** 2026-06-23
**Type:** Pre-rebuild audit (investigation only — no code changed)
**Scope:** Full repository as it stands at branch `main`, commit `dceae3e`.
**Method:** Direct inspection of source, `main.py` router wiring, `config.py`, compose,
dependency manifests, git history, and grep/glob over the tree. Claims cite file paths.
Where a fact could not be verified, it is marked **unverified**.

---

## 1. Executive summary

The project is a real, working on-premise AI knowledge workspace for a Thai SME (demo
tenant LongDuem), with a genuinely functional Finance MVP. The **code is in better shape
than the documentation**: the backend is coherent and the Finance + Auth + OCR + AI-search
paths are implemented and tested.

The core problem is **drift and fragmentation**, not broken code:

- Docs described an `app/modules/<domain>/` backend that no longer exists (it was built then
  deleted). The real backend is flat.
- Multiple naming systems (MindKeep / LongRian / LongDuem) were used interchangeably.
- "Done" claims in status docs did not match reality (e.g. mock fallbacks that don't exist,
  an "action required" that was already completed, a removed directory that still exists).
- Several parallel efforts (monorepo migration, RAG Phase 1, UX redesign) were layered on top
  of each other without a single source of truth, and a large amount of work is **uncommitted**.

Most active doc conflicts were corrected in the 2026-06-23 documentation pass (see git diff).
This report records the underlying problems and the lessons for a rebuild.

---

## 2. Current system reality

**Product.** On-prem platform ("MindKeep") that turns employee actions into permission-scoped,
searchable Work Memory so knowledge survives staff turnover. All AI runs locally (Ollama); no
data leaves the network. Demo tenant **LongDuem** (coconut-water SME), four departments. MVP
focus = **Finance & Accounting** (primary user ป้าต้อย). Source of intent:
`docs/product/MindKeep_AI_Workspace_Core_Spec_v0.1.md`.

**Stack.**
- Backend: FastAPI (Python 3.12), entry `apps/backend/app/main.py`; **flat** layout
  (`routes/ services/ models/ schemas/ agents/ core/ middleware/ db/ alembic/`).
- Frontend: Next.js 14 App Router, TypeScript, Tailwind (`apps/frontend/src/`).
- Data: PostgreSQL (`pgvector/pgvector:pg16`), ChromaDB (active vector store), Ollama
  (`qwen2.5:7b` + `nomic-embed-text`), local filesystem for files/OCR.

**Names refer to different things** (now documented, was a source of confusion):
MindKeep = product · LongRian = this repo · LongDuem = demo tenant.

---

## 3. Repository structure

Root (`git`-tracked unless noted):

```
apps/            backend + frontend (canonical source)
infra/           docker-compose.yml (+ .ollama overlay), .env(.example)
docs/            specs, technical, api, product, superpowers, technical/restructure
scripts/db/      seed + knowledge-load scripts
data/            mock / samples / seed fixtures
private/         business-sensitive (gitignored, 0 tracked files — OK)
graphify-out/    generated knowledge graph (gitignored)
longrian-ai/     EMPTY, UNTRACKED leftover from pre-monorepo layout
longduem Doc/    company files (gitignored, 0 tracked files — OK)
```

Structural problems:

- **`longrian-ai/` (root)** — empty stray directory; `PROJECT_STATUS.md` previously claimed it
  was "removed". It is untracked and safe to delete. (Evidence: `git ls-files longrian-ai` empty;
  directory present.)
- **`apps/backend/app/modules/`** — empty directory shell may remain on disk; there are **no
  Python files** in it. The modules layer was deleted in commit `fd90141`. Docs still pointed at
  it until the 2026-06-23 fix.
- **Multiple seed entrypoints** in `scripts/db/`: `seed.py`, `longduem_seed.py`,
  `seed_finance_docs.py`, `load_knowledge.py` — overlapping responsibilities, unclear which is
  canonical. `scripts/db/seed_finance_docs.py:5` still hardcodes the old path
  `longrian-ai/backend/scripts/seed_finance_docs.py`.
- **Lingering old name** "longrian-ai" appears in `infra/docker-compose.yml:2` (comment),
  `scripts/db/seed_finance_docs.py`, `.claude/settings.local.json`, and historical docs.

---

## 4. Product purpose (real vs shallow)

| Aspect | State |
|---|---|
| Problem solved | Institutional knowledge loss on staff turnover — **real intent, consistently expressed** |
| Intended users | SME staff by department; admin/owner sees all (`scripts/db/longduem_seed.py`) |
| Workflow | action → record → activity log → Work Memory → vector/RAG → permission-scoped AI |
| MVP focus | Finance & Accounting — **real and deepest** |
| Other departments (farm/legal/marketing) | **shallow by design** — hub page + a few agent endpoints; not full tools |

---

## 5. Backend audit

- **Entrypoint:** `apps/backend/app/main.py` — registers 26 routers, runs `CREATE EXTENSION
  vector` + `create_all` in lifespan, marks OCR jobs stuck >5 min as failed.
- **Routers / prefixes** (from `main.py`; full list in `docs/api/LongRian_API_Spec.md`): auth,
  dashboard, documents (+ ingestion + doc_permissions all under `/api/v1/documents`), approvals,
  finance / finance_summary / finance_advanced (**all three share `/api/v1/finance`**),
  finance_workspace, finance_records (`/api/v1/finance-records`), ocr, ai_workspace (`/api/v1/ai`),
  chat, librarian, tasks, events, activities, audit, files, tables, workspaces, admin +
  admin_data_studio (both `/api/v1/admin`), legal, marketing.
- **Services:** `apps/backend/app/services/` — permission, audit, document, approval,
  finance_record/summary/calculator, tax_estimate, insight, vat, memory, ai_workspace, rag,
  ingestion, ocr (+worker, +cash_log), pdf, file, llm, ai_health, `task_event_service` (stub).
- **Models / schemas:** `apps/backend/app/models/` (22) + `schemas/` (20) — flat, per-domain.
- **Auth/JWT/permission:** `middleware/auth.py` decodes JWT per request; `services/permission_service.py`
  is the single gate (department access, approval rights, RAG chunk filter).
- **AI/RAG/memory:** `agents/` (finance/legal/marketing + `router.get_agent()`),
  `services/memory_service.py` (`scrub_credentials`, retrieval, ChromaDB indexing),
  `services/rag_service.py` (RouteClassifier + ChunkQueryBuilder), `db/chroma.py`.
- **Finance:** records state machine + categories/vendors (`finance_records`), summary/VAT/reports
  (`finance_summary`), CSV insight + tax estimate (`finance_advanced`), workspace overview
  (`finance_workspace`), pricing/P&L/cost helpers (`finance`).
- **Config/env:** `apps/backend/app/config.py` — defaults DB `longrian`, Chroma `localhost:8001`,
  Ollama `localhost:11434` / `qwen2.5:7b`, JWT 480 min, RAG flags `False`.
- **Tests:** 25 test files in `apps/backend/tests/` (auth, finance×4, rag×5, ai×2, permission×2,
  ingestion×2, llm, chat, pdf×2, my_work, may_onboarding, base_agent). **Not executed this
  session.** Docs report 82/82 new tests pass with known pre-existing failures in
  `test_auth_routes.py`, `test_permission_service.py`, `test_document_service.py` (stale
  `HTTPException` vs current `AppError`; missing `x-device-type` header).

Backend problems:
- **`/api/v1/finance` prefix shared by 3 routers** — works, but the endpoint namespace is split
  across `finance.py`, `finance_summary.py`, `finance_advanced.py`; easy to collide / hard to reason about.
- **RAG ingestion + permissions under `/api/v1/documents`** rather than their own prefix — non-obvious.
- **`task_event_service.py` is a stub no-op** — notifications silently do nothing.

---

## 6. Frontend audit

- **Routing:** 43 `page.tsx` files (App Router). Finance is the deepest surface.
- **API client:** `apps/frontend/src/lib/api/` — `client.ts` (core fetch/auth/error, `ApiError`,
  `isForbidden()`) + per-domain modules (`finance.ts`, `documents.ts`, …) + `index.ts` barrel.
- **Components:** `components/{ui,finance,layout,documents,chat,auth,memory}` + `Providers.tsx`;
  shared primitives `ui/PageHeader.tsx`, `ui/KpiCard.tsx`, `ui/ForbiddenState.tsx`, `ui/AIStatusBanner.tsx`.
- **Real workflows:** login → dashboard → finance (records/summary/VAT/insights/tax/receipts/vendors),
  documents + approvals, AI chat + librarian, admin (users/data-studio/audit).

Frontend problems (evidence):
- **Dead route:** `app/chat/page.tsx` exists but is **not linked in nav**; only `/ai/chat` is
  (`components/layout/Sidebar.tsx:162`). `/chat` is orphaned/duplicate.
- **Duplicate nav entry:** `/ai/chat` is added twice in `Sidebar.tsx:162-163` (general + admin).
- **Stale doc claim, not code:** `PROJECT_STATUS.md` says `/calendar` and `/tasks` fall back to
  `MOCK_EVENTS`/`MOCK_TASKS`; grep finds **no such constants** in `apps/frontend/src`. Either
  removed or never existed — the claim is unverified/misleading.
- **Possibly shallow pages:** `finance/calculators`, `finance/tools`, `finance/documents` exist and
  **are** sidebar-linked (`Sidebar.tsx:175,187-188`); depth not verified.
- **Large uncommitted UI churn:** ~17 frontend files modified + `ui/KpiCard.tsx`, `ui/PageHeader.tsx`,
  `lib/labels.ts` untracked (UX redesign in flight) — see §9.

---

## 7. AI / RAG audit

- **Local AI:** Ollama only; `config.py` + `.env.example` (`OLLAMA_BASE_URL`). No cloud LLM calls.
- **Agents:** `agents/base.py` (BaseAgent, stream/invoke, `ModelUnavailableError`),
  `agents/router.py`, `agents/{finance,legal,marketing}.py`.
- **Vector stores:** ChromaDB is the **active** path (per-department collections, `db/chroma.py`).
  pgvector is **committed but flag-off**.
- **Ingestion/search:** `services/ingestion_service.py` (queued→extracting→chunking→embedding→completed,
  OCR gate, atomic stale-swap); `services/rag_service.py` (RouteClassifier + ChunkQueryBuilder);
  `routes/ingestion.py`, `routes/librarian.py` (`POST /search` + `/search/pgvector`).
- **Permission-scoped retrieval:** AI uses the same permission gate as REST
  (`build_chunk_permission_filter` / `build_ai_permission_filter` in `permission_service.py`).

Status clarity (this is the key risk): RAG Phase 1 is **wired in code but not active**.
`use_pgvector_indexing=False`, `use_pgvector_retrieval=False` (`config.py`), migrations
`20260609_0001..0008` written but **not run on a live DB**. ChromaDB remains the real path.
- **Client/server version skew:** `requirements.txt` pins `chromadb==0.5.18`; compose runs server
  `chromadb/chroma:0.5.23` (`infra/docker-compose.yml`). Potential protocol mismatch.

---

## 8. Finance MVP audit

| Feature | Backend | Frontend | State |
|---|---|---|---|
| Records + state machine | `finance_records.py` / `finance_record_service.py` | `finance/records` | Usable |
| Categories + vendors | `finance_records.py` | `finance/vendors` | Usable |
| Income & expense summary | `finance_summary.py` | `finance/summary`, `finance/dashboard` | Usable |
| VAT calc + alerts | `finance_summary.py` / `vat_service.py` / `finance_calculator.py` | `finance/vat` | Usable |
| CSV insights (stdlib) | `finance_advanced.py` / `insight_service.py` | `finance/insights` | Usable |
| Tax estimate (configurable rules) | `finance_advanced.py` / `tax_estimate_service.py` | `finance/tax` | Usable |
| OCR / Bill Scanner | `ocr.py` + `ocr_service/worker/cash_log` | `finance/receipts`, `/[ocrDocumentId]`, `/job/[jobId]` | Usable; review-before-confirm |
| Pricing / P&L helpers | `finance.py` | `finance/tools`, `finance/calculators` | Present; depth unverified |

Problems:
- **OCR jobs are not durable** — FastAPI `BackgroundTasks`, not a queue; jobs lost on restart
  (startup sweeps stuck jobs to `failed`, `main.py`).
- **Finance logic split across 4–5 routers/services** under one prefix — maintainability risk.

---

## 9. Permission / RBAC audit

- **Model:** `models/department.py` — `Department`, `Role`, `UserDepartmentRole`. Single tenant
  (no `organizations` table); `organization_id` implicit.
- **Rules:** regular user sees own department; admin/owner sees all (`longduem_seed.py`).
- **REST checks:** centralized in `services/permission_service.py`; `middleware/auth.py` resolves user.
- **AI/RAG checks:** same gate reused for retrieval — good design (no separate AI permission path).
- **Known gap (documented):** `build_ai_permission_filter` resolves dept from the user's own
  assignments; an admin querying a department they're not directly assigned to passes the gate but
  may return empty results (noted in prior status notes — verify against current code before relying on it).

---

## 10. Documentation audit

| Doc | State (pre-2026-06-23) |
|---|---|
| `README.md`, `docs/PROJECT_MAP.md`, `CLAUDE.md`, `PROJECT_STATUS.md` | Described deleted `app/modules/`; **stale** — now corrected |
| `docs/api/LongRian_API_Spec.md` | 3-line placeholder ("Original spec moved here") — now factual |
| `docs/technical/{backend,frontend}.md` | thin/stale (modules refs) — now factual |
| `docs/technical/instructions.md` | empty placeholder (duplicated the vibe-coding stub) — now factual |
| `docs/product/LongRian_Department_Workspace_Spec_v1.md` | empty placeholder — now factual |
| `docs/LONGRIAN_VIBE_CODE_INSTRUCTIONS.md` | empty placeholder — now a redirect/delete-candidate |
| `docs/technical/restructure/*` | "Planning phase — no execution yet" but migration is **done** — historical |
| `docs/superpowers/{plans,specs}/*`, `docs/PONYTAIL_REVIEW.md` | one-off / historical decision records |

Specific misleading "done"/broken items found:
- `PROJECT_STATUS.md` (pre-fix): "Batch 5 modules created ✅" (actually reverted),
  "longrian-ai removed" (still present), `MOCK_EVENTS`/`MOCK_TASKS` fallback (no such constants).
- `PROJECT_MAP.md` (pre-fix): cited `apps/backend/app/load_knowledge.py` (real path is
  `scripts/db/load_knowledge.py`) and wrong endpoint prefixes for ingestion/doc_permissions.
- Repeated **"Action required: `git rm -r --cached 'longduem Doc'`"** — already done
  (`git ls-files "longduem Doc"` returns 0). Obsolete instruction.
- `docs/QA_CHECKLIST_FINANCE_MVP.md` referenced but **never existed**.

---

## 11. Deployment / local setup audit

- **Canonical compose:** `infra/docker-compose.yml` — postgres (5432), chromadb (8001→8000),
  backend (8080, builds `apps/backend/Dockerfile`), frontend (3000, builds `apps/frontend/Dockerfile`).
  Dockerfiles exist.
- **Ollama is NOT a compose service** — backend points at `host.docker.internal:11434` (host Ollama).
  `infra/docker-compose.ollama.yml` is an optional overlay that adds an `ollama` container **with no
  host port mapping** — so it appears unused by the current backend config.
- **Volumes are external/named** (`longrian_postgres_data`, `longrian_chroma_data`,
  `longrian_uploads_data`) — must be pre-created or the stack won't boot.
- **Env assumptions are mixed/inconsistent** (`infra/.env.example`): `DATABASE_URL` + `CHROMA_HOST`
  use `localhost`, but `OLLAMA_BASE_URL` uses `host.docker.internal`. `JWT_EXPIRE_MINUTES=60` here
  vs `config.py` default `480`.
- **Seed/demo:** real, idempotent (`scripts/db/longduem_seed.py`), 6 demo users. But multiple seed
  scripts exist (see §3) and docs disagreed on the path (`python longduem_seed.py` vs `scripts/db/...`).
- **Two verified-but-different run paths**: host dev (uvicorn + host Ollama, `create_all`, no alembic)
  vs full Docker (alembic in image). The docs historically mixed these.
- **`next@14.2.18`** (`apps/frontend/package.json`) — known CVE; upgrade before production.

---

## 12. Fragmentation analysis — why it became hard to understand

1. **Docs not updated with code.** The biggest issue. Three high-traffic docs described an
   architecture (`app/modules/`) that had been deleted.
2. **No single source of truth.** README, PROJECT_MAP, PROJECT_STATUS, CLAUDE.md, and a
   `restructure/` guide each told a partial, sometimes contradictory story.
3. **Three overlapping initiatives layered without reconciliation**: monorepo migration, RAG
   Phase 1, UX redesign — each added docs/claims without retiring the previous state.
4. **Planned mixed with done.** RAG Phase 1 (flag-off, no live migration) was described alongside
   shipped features; status flags lived only inside prose.
5. **Old folders/names left behind.** `longrian-ai/`, empty `modules/`, old paths in scripts,
   "longrian-ai" in comments.
6. **Over-scaffolding / placeholders.** Several docs were stubs containing only
   "(Original content moved here.)"; some finance helper pages exist with unverified depth.
7. **Route/page duplication.** `/chat` vs `/ai/chat`; duplicate sidebar entry.
8. **Work left uncommitted.** ~1,330 insertions across 32 files unstaged + untracked primitives —
   the on-disk state is ahead of git history, so git history alone misrepresents the project.

---

## 13. Feature / module status table

| Module | Status | Evidence |
|---|---|---|
| Auth + JWT | Done | `middleware/auth.py`, `routes/auth.py` |
| Department RBAC | Done | `permission_service.py`, `models/department.py` |
| Finance MVP (records/summary/VAT/insight/tax) | Done | `routes/finance_*`, `services/finance_*` |
| OCR / Bill Scanner | Done (non-durable jobs) | `routes/ocr.py`, `ocr_service.py` |
| Documents + approvals | Done | `routes/documents.py`, `approvals.py` |
| Audit trail | Done | `services/audit_service.py`, `routes/audit.py` |
| AI chat + search (ChromaDB) | Done | `routes/ai_workspace.py`, `chat.py`, `librarian.py` |
| Work Memory + scrubbing | Done | `services/memory_service.py` |
| Admin + Data Studio | Done | `routes/admin.py`, `admin_data_studio.py` |
| Department agents (legal/marketing/farm) | Partial (shallow) | `agents/*`, hub pages |
| RAG pgvector (Phase 1) | Partial — flag-off, no live migration | `config.py`, `models/rag.py`, migrations 0001–0008 |
| Notifications | Planned (stub) | `services/task_event_service.py` |
| Multi-tenant | Planned | no `organizations` table |
| `/chat` page | Dead/duplicate | `app/chat/page.tsx` not in nav |

---

## 14. Documentation problems (summary)

Stale architecture refs (fixed), empty stub specs (fixed), historical docs presented as current
(`restructure/`), broken references (`QA_CHECKLIST`, wrong `load_knowledge.py` path), obsolete
"action required", and status that lived only in prose rather than a machine-checkable place.

---

## 15. Technical risks

| Risk | Impact | Evidence |
|---|---|---|
| ChromaDB client 0.5.18 vs server 0.5.23 | Possible protocol breakage | `requirements.txt` vs `docker-compose.yml` |
| RAG flags flipped before live migration verified | Unauthorized chunks / runtime errors | `config.py`, migrations not run |
| OCR jobs non-durable | Lost jobs on restart | `main.py` BackgroundTasks sweep |
| `next@14.2.18` CVE | Security | `package.json` |
| Large uncommitted working set | Work loss / unreproducible state | `git status` (32 modified + untracked) |
| Mixed env assumptions (localhost vs host.docker.internal; JWT 60 vs 480) | Boot/auth surprises | `.env.example` vs `config.py` |
| External named volumes required | Stack won't boot if absent | `docker-compose.yml` |
| Permission gate for cross-dept admin RAG | Empty/again-unclear results | `permission_service.py` (verify) |

---

## 16. Keep / Redesign / Discard table

| Part | Verdict | Reason |
|---|---|---|
| Finance MVP (models, services, flows) | **Keep** | Real, tested, the proven value |
| Permission service as single REST+AI gate | **Keep** | Sound design; reuse the pattern |
| Local-AI / Ollama + per-dept memory model | **Keep** | Matches product intent |
| Audit trail + credential scrubbing | **Keep** | Compliance-relevant, working |
| Backend layout (one flat dir, finance split across 5 routers) | **Redesign** | Hard to navigate; needs clear module boundaries with stable prefixes |
| RAG dual-store (Chroma active, pgvector flag-off) | **Redesign / decide** | Carrying two vector stores; pick one go-forward |
| Frontend nav + finance helper pages | **Redesign** | Dead `/chat`, duplicate entries, unverified-depth pages |
| Seed scripts (4 overlapping in `scripts/db/`) | **Redesign** | Consolidate to one canonical, idempotent seeder |
| `longrian-ai/`, empty `modules/`, stub docs, old-path strings | **Discard** | Pure noise; mislead readers |
| `docs/technical/restructure/`, `superpowers/`, `PONYTAIL_REVIEW.md` | **Discard from active set / archive** | Historical; not current state |
| Notifications (`task_event_service`) | **Unknown** | Owner decision: build now or defer |
| Multi-tenant | **Unknown** | Owner decision: is this ever needed? |

---

## 17. Recommended rebuild principles

1. **Single source of truth.** One README + one status doc + one code map; every other doc links
   to them. Status flags live next to code (config + a generated API doc), not only in prose.
2. **Docs are part of "done".** A feature isn't done until its doc and status row are updated in
   the same change. Treat stale docs as bugs.
3. **No placeholder docs.** A file either has real content or doesn't exist.
4. **Pick one of each.** One vector store, one chat page, one seed script, one run path documented
   as canonical (others explicitly marked optional/experimental).
5. **Stable API boundaries.** Don't share one prefix across many routers; give each domain its own
   prefix and keep it.
6. **Flags are honest.** Anything flag-off or not-migrated is labelled clearly and never described
   as shipped.
7. **Commit discipline.** Don't let the on-disk state drift far ahead of git; small, committed steps.
8. **Delete leftovers immediately** when a migration completes (no empty dirs, no old-name strings).
9. **Pin versions that must agree** (e.g. Chroma client/server) and check them in CI.
10. **Build order:** prove the spine first (auth → RBAC → one department's data flow → Work Memory →
    permission-scoped retrieval), then add departments. Defer notifications, multi-tenant, and
    pgvector activation until the spine is verified on a live DB.

---

## 18. Questions for owner before new build

1. **Vector store:** go-forward with ChromaDB, migrate fully to pgvector, or keep both? (Today both
   exist; pgvector is flag-off.)
2. **Scope of departments:** should farm/legal/marketing stay shallow hubs, or become full tools in
   the rebuild?
3. **Notifications:** build real delivery now (`task_event_service`) or explicitly defer?
4. **Multi-tenant:** is more than one tenant ever in scope, or is single-tenant (LongDuem) final?
5. **Deployment target:** is the canonical run path host-dev (host Ollama) or full Docker? Should
   Ollama be containerized (fix the overlay) or stay on the host?
6. **Chat UX:** keep `/ai/chat` only and remove `/chat`? Confirm.
7. **Uncommitted work:** the current UX redesign + doc changes are unstaged — commit them as the new
   baseline before the rebuild, or discard?
8. **Carry-over:** which existing code should the rebuild reuse as-is (Finance MVP, permission
   service) vs reimplement?

---

---

## Current Validation Baseline

**Run at:** 2026-06-23 · branch `main` · commit `dceae3e` (working tree has uncommitted changes — see below).
**Host environment caveat:** this machine runs **Python 3.14.5 / pytest 9.0.3 / Node v24.15.0**.
The project documents a **Python 3.12** target. Some failures below may be amplified or masked by
the newer runtime (async-mock behaviour, `datetime.utcnow()` deprecation). Treat counts as
indicative for this host, not the canonical 3.12 environment. No Ollama was running during the run.

### Commands run
- `git status --short`, `git diff --stat`, `git diff --check`, `git log --oneline -10`
- Backend: `cd apps/backend && python -m pytest tests/`
- Frontend: `cd apps/frontend && npx tsc --noEmit`
- Frontend: `cd apps/frontend && node scripts/route_smoke.mjs`
- Stale-path grep (ripgrep) for the agreed term list

### Pass/fail summary

| Check | Result |
|---|---|
| `git diff --check` | Clean (no conflict markers / whitespace errors) |
| Working tree | **Dirty** — 32 files modified + untracked (`docs/reports/`, `ui/KpiCard.tsx`, `ui/PageHeader.tsx`, `lib/labels.ts`, `infra/docker-compose.ollama.yml`, `apps/backend/app/uploads/`); diff = 1330 insertions / 925 deletions |
| Backend pytest | **14 failed, 276 passed**, 70 warnings, ~119s (290 collected) |
| Frontend `tsc --noEmit` | **Pass** (exit 0, no type errors) |
| Frontend route smoke | **Pass** — 26/26 sidebar routes resolve (exit 0) |

### Exact backend failures (14)

**Group A — documented, pre-existing (10): test/code contract drift.**
Cause confirmed by traceback: login test omits the now-required `x-device-type` header (→ 400 via
`RequestHeaderMiddleware`); permission/document tests assert the old `HTTPException` but code raises
`core.errors.AppError`.
- `test_auth_routes.py::TestLogin` ×4 (valid/wrong-password/unknown-email/inactive)
- `test_permission_service.py` ×4 (member_blocked, marketing_blocked, doc_blocked, admin_all_collections)
- `test_document_service.py::TestEditDocumentPermission` ×2 (approved/archived not editable)

**Group B — NOT previously documented (4): pre-existing in committed code, mixed causes.**
(These backend modules are unchanged in the working tree — only `main.py` has a +1-line diff — so
they are not introduced by the uncommitted work.)
- `test_ai_health.py::test_health_endpoint_returns_200_envelope` — endpoint returns **500** ("Internal
  server error") instead of a 200 envelope. Likely **environment**: no Ollama running and the health
  route does not degrade gracefully under the test client. Verify with Ollama up.
- `test_finance_workspace.py::test_ocr_confirm_with_income_type_appears_in_overview` — assertion
  `total_income == 17500` but got **15000**. **Environment-independent → genuine logic/test
  discrepancy** in income aggregation. Most worth investigating.
- `test_llm_service.py::test_classify_returns_matching_category` — async Ollama client mock not
  intercepting; raises "connection refused" → `ModelUnavailableError`. Likely **environment/version**
  (Python 3.14 `AsyncMock` / ollama client). 
- `test_llm_service.py::test_chat_raises_model_unavailable_on_error` — **flaky / order-dependent**:
  fails in the full run, **passes in isolation**. Test-isolation (shared mock state) defect.

### Stale references still found (after the 2026-06-23 doc pass)

Confirmed clean (no longer present in active code/docs):
- `apps/backend/app/modules` — **0 hits in `apps/`** (code is fully flat).
- `lib/api.ts` — gone from active docs (README/PROJECT_MAP/PROJECT_STATUS/technical).

Still present (findings only — not fixed, per scope):
- **`PROJECT_STATUS.md:125`** still states `/calendar` and `/tasks` use `MOCK_EVENTS`/`MOCK_TASKS`
  fallback — **no such constants exist** in `apps/frontend/src`. Remaining misleading claim to clean.
- **`package.json:2` / `package-lock.json`** — package name still `"longrian-ai-frontend"`.
- **`scripts/db/seed_finance_docs.py:5`** — docstring hardcodes old path `longrian-ai/backend/scripts/...`.
- **`.claude/settings.local.json`** — old `longrian-ai/...` paths in permission entries (machine-local, not source).
- **`infra/docker-compose.yml:2`** — comment references "legacy longrian-ai/" (benign/historical).
- **Historical docs** (`docs/superpowers/**`, `docs/technical/restructure/**`, `docs/PONYTAIL_REVIEW.md`)
  still contain `lib/api.ts`, `app/modules`, `longrian-ai` — expected; these are archive/delete candidates.

Current/expected usage (NOT stale — present and correct): `pgvector`, `ChromaDB`/`chromadb`,
`host.docker.internal`, `docker-compose.ollama` all appear where intended (config, services,
migrations, infra). `QA_CHECKLIST_FINANCE_MVP` now appears only as an explicit "does not exist" note.

### Verdicts

- **Safe to freeze as reference?** **Yes, with one prerequisite.** Frontend is green (types + routes);
  backend is 276/290 with all 14 failures pre-existing (test-contract drift + environment + one real
  finance-aggregation discrepancy) — none are new regressions. **Before freezing, commit or branch the
  current uncommitted working set** (1330+ insertions are unstaged) so the frozen reference is a clean,
  reproducible commit. A re-run on the documented **Python 3.12** environment is recommended to get the
  canonical failure count.
- **Graphify refresh safe, or wait?** Safe to run anytime — it only writes to gitignored `graphify-out/`
  and does not touch source. **Recommendation: wait until the working set is committed**, so the graph
  reflects a stable committed state rather than mid-flight edits.

---

*Audit only. Running the test/typecheck/smoke commands and the grep did not modify any source code,
migrations, configs, or runtime files. The only file written is this report.*
