# Old Project Freeze Note — MindKeep / LongRian AI Workspace

**Prepared:** 2026-06-24 · **Validation baseline:** 2026-06-23
**Purpose:** Freeze the old repo as a stable *reference* snapshot before any rebuild.
**Status:** NOT yet committed — awaiting owner confirmation of the commit strategy below.
Companion: `docs/reports/OLD_PROJECT_PROBLEM_REPORT.md` (full audit + validation baseline).

---

## 1. Commit before freeze

`dceae3e` — *feat(frontend): dept hub pages for Farm, Legal, Marketing + sidebar sections*

The working tree is **ahead of this commit** by 32 modified + 7 untracked files
(1,330 insertions / 925 deletions). Nothing below is committed yet.

## 2. Working tree summary (dirty-file classification)

**A. Audit / report / docs (safe — the freeze artifacts)**
`README.md`, `CLAUDE.md`, `PROJECT_STATUS.md`, `docs/PROJECT_MAP.md`, `docs/README.md`,
`docs/api/LongRian_API_Spec.md`, `docs/product/LongRian_Department_Workspace_Spec_v1.md`,
`docs/technical/{backend,frontend,instructions}.md`, `docs/LONGRIAN_VIBE_CODE_INSTRUCTIONS.md`,
`docs/reports/OLD_PROJECT_PROBLEM_REPORT.md` (new), this file (new).
→ 2026-06-23/24 documentation reconciliation + audit. Docs only, no behavior.

**B. Source / UI (pre-existing WIP — "Coconut" UX redesign, not authored during the audit)**
Pages: `dashboard`, `farm`, `legal`, `marketing`, `finance/{page,compliance,records,reports,vendors}`,
`profile/{page,account,privacy}`. Components: `finance/DashboardOverviewCards`,
`finance/DashboardQuickActions`, `layout/Sidebar`, `ui/Button`, `ui/Input`. Styling:
`globals.css`, `tailwind.config.ts`. New: `ui/KpiCard.tsx`, `ui/PageHeader.tsx`, `lib/labels.ts`.
→ Real UI change. Frontend typechecks and route-smokes clean (see §3).

**C. Config / infra**
`infra/docker-compose.yml` (postgres → `pgvector/pgvector:pg16`, added backend env),
`apps/backend/app/main.py` (+1 line: `CREATE EXTENSION IF NOT EXISTS vector` on startup),
`infra/docker-compose.ollama.yml` (new optional Ollama overlay),
`apps/frontend/.dockerignore` (new build-context filter).
→ Infra-enablement so the stack boots on the pgvector image. The `main.py` line is additive
(extension creation), not feature behavior.

**D. Generated / runtime / local**
`apps/backend/app/uploads/admin/…ใบเสนอราคา…บริษัท เซ็นท….pdf` — a real uploaded company
quotation produced by running the app.

**E. SHOULD NOT be committed**
- The `uploads/…pdf` above — **runtime artifact containing sensitive business data**. The
  `apps/backend/app/uploads/` path is **not gitignored**; it should be added to `.gitignore`
  (do *not* commit the file). Flagged only — not changed under the freeze rules.

## 3. Validation baseline summary

| Check | Result |
|---|---|
| Backend `pytest tests/` | **14 failed / 276 passed** (290 collected) |
| Frontend `tsc --noEmit` | Pass (exit 0) |
| Frontend `route_smoke.mjs` | Pass — 26/26 routes |
| `git diff --check` | Clean |

Failures are **all pre-existing** (none introduced by the dirty working set): 10 are documented
test/code contract drift (`x-device-type` header; `HTTPException`→`AppError`); 4 were undocumented
(`ai_health` 500 w/o Ollama; `finance_workspace` income `15000≠17500` — a *real* discrepancy;
2× `llm_service` — async-mock/version + a flaky order-dependent test). Run on **Python 3.14.5**
(project targets **3.12**) with **no Ollama running**, so some failures are environment-driven.
Full detail: `OLD_PROJECT_PROBLEM_REPORT.md` → "Current Validation Baseline".

## 4. Unresolved risks (carried into freeze)

- `finance_workspace` income aggregation discrepancy (`15000` vs expected `17500`) — needs a real fix decision.
- ChromaDB client `0.5.18` vs server `0.5.23` version skew.
- RAG pgvector wired but flag-off; migrations not run on a live DB.
- OCR jobs non-durable (FastAPI `BackgroundTasks`).
- `next@14.2.18` known CVE.
- Large WIP UI redesign uncommitted; baseline run on a non-target Python.
- Lingering old name `longrian-ai-frontend` (`package.json`), old path in `scripts/db/seed_finance_docs.py:5`,
  stale `MOCK_EVENTS`/`MOCK_TASKS` claim in `PROJECT_STATUS.md:125`.

## 5. What this old repo SHOULD be used for

- A **reference** for product intent, domain model, and workflows (Finance MVP, RBAC, Work Memory, RAG design).
- A source of **proven logic to port** (permission gate, finance calculators, OCR flow, credential scrubbing).
- The **audit + freeze record** of what existed and why it drifted.

## 6. What it should NOT be used for

- **Not** a direct foundation to build the new project on top of (accumulated drift, dead/duplicate
  routes, split prefixes, flag-off RAG, undocumented test failures).
- **Not** a source of truth for *current* status from prose alone — trust code + the reconciled docs.
- **Not** a place to keep iterating the UX redesign — decide its fate first (see §7).

## 7. Before Rebuild Decisions (owner checklist)

1. **Vector store direction** — ChromaDB only, full pgvector migration, or dual? (today: Chroma active, pgvector flag-off)
2. **Canonical chat route** — keep `/ai/chat` and drop dead `/chat`? (and remove the duplicate sidebar entry)
3. **Deployment path** — canonical = host-dev (host Ollama) or full Docker? Containerize Ollama (fix overlay) or host?
4. **Finance MVP carry-over** — reuse *ideas only* (rewrite clean) or port the *code* (records/summary/VAT/insight/tax/OCR)?
5. **Other departments** (farm/legal/marketing) — stay shallow/planned, or promoted to full tools in the rebuild?
6. **Notifications & multi-tenant** — defer both (current: `task_event_service` stub; single-tenant), or in scope now?
7. **UX redesign** — is the uncommitted "Coconut" redesign worth carrying over, or restart the design system?

## 8. Recommendation

**Use this repo as a reference snapshot, not as the rebuild foundation.** Freeze it by committing the
current work (see chat for the recommended docs-first split), **excluding the `uploads/` PDF**, then
start the new project clean and port proven pieces deliberately. Defer graphify refresh until after the
freeze commit so the graph reflects a stable state.
