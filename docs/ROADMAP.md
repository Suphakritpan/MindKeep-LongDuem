# ROADMAP.md

> **หน้าที่ของไฟล์นี้:** Phase 1–7 ทำอะไรก่อนหลัง + สถานะ Done / In Progress / Planned
> docs rule: "Feature is not done until code, tests, docs, and roadmap status are updated."

**Status legend:** ✅ Done · 🔄 In Progress · 📋 Planned

ลำดับนี้มีเป้าหมายเพื่อ **สร้างแกนระบบให้แข็งก่อน** แล้วค่อยขยายไปเป็น workspace ของแต่ละแผนก
อย่ากระโดดทำทุกอย่างพร้อมกัน

---

## Phase Overview

| Phase | ชื่อ | สถานะ |
|---|---|---|
| 1 | Document + Work Memory Core | 🔄 In Progress |
| 2 | Finance Workspace | 📋 Planned |
| 3 | Handover / New Employee Continuity | 📋 Planned |
| 4 | Department Workspace Expansion | 📋 Planned |
| 5 | Full AI Chat Experience | 📋 Planned |
| 6 | Field & Production Mobile / Mini App / LINE | 📋 Planned |
| 7 | Admin / Owner Command Center | 📋 Planned |

> สถานะปัจจุบัน: **Step 1–3 ✅ DONE** (docs + Master Prompt + monorepo skeleton ที่ boot ได้).
> **Step 4 กำลังทำ:**
> - **Batch A (DB foundation) ✅ DONE** — Alembic + shared enums + base/mixins + pgvector migration 0001
> - **Batch B (auth + users + departments + permissions) ✅ DONE** — JWT login, bcrypt, central PermissionService,
>   models + migration 0002, `/auth /users /departments /permissions` ต่อเข้า `/api/v1`, dev seed
> - **Batch C (documents + files + StorageService) ✅ DONE** — Document/DocumentVersion/File models + migration 0003,
>   StorageService (local FS, sha256), upload/preview-download/CRUD/submit/lock/delete, permission-aware list, `/documents /files`
> - **Batch D (background job system) ✅ DONE** — `jobs` table + migration 0004, DB-backed worker (FOR UPDATE SKIP LOCKED),
>   handler registry, retry/max_attempts, `/jobs` (list/get/retry) per-user scoped, compose `worker` service
> งานถัดไป = **Batch E** (extraction + summary pipeline — handlers ตัวจริง)

---

## Phase 1 — Document + Work Memory Core 📋

แกนระบบ. รายละเอียด in/out scope → [SCOPE.md](SCOPE.md), เกณฑ์สำเร็จ → [ACCEPTANCE_CRITERIA.md](ACCEPTANCE_CRITERIA.md)

```text
- Home / Dashboard shell
- Profile basic
- Auth / users / departments / basic permissions
- Documents (upload, preview, simple note, metadata/tag/visibility)
- Text extraction + AI summary
- Review before memory
- Work Memory (pgvector embedding)
- Permission-aware RAG
- Basic AI Chat with source citation
- Activity Timeline
- Audit logs for sensitive actions
- StorageService (local filesystem first)
- Background jobs (status + retry)
- Docs source of truth
```

**Phase 1 build order** (จาก MASTER_PROMPT / Spec §17 — อย่าข้าม):

```text
1.  Create repo structure              ◀── ✅ DONE (frontend/ backend/ data/ flat monorepo)
2.  Create docs source of truth        ◀── ✅ DONE (10 docs + MASTER_PROMPT)
3.  Setup backend FastAPI skeleton     ◀── ✅ DONE (health + /api/v1 mount)
4.  Setup frontend Next.js skeleton    ◀── ✅ DONE (placeholder Home)
5.  Setup PostgreSQL + migrations      ◀── 🔄 Batch A DONE (Alembic + enums + pgvector mig); tables per batch
6.  Create auth/users/departments/permissions   ◀── ✅ DONE (Batch B — migration 0002)
7.  Create documents/files module      ◀── ✅ DONE (Batch C — migration 0003)
8.  Create StorageService              ◀── ✅ DONE (Batch C — local FS + sha256)
9.  Create background job system       ◀── ✅ DONE (Batch D — DB worker, migration 0004)
10. Create extraction/summary pipeline ◀── ⏭ NEXT (Batch E)
7.  Create documents/files module
8.  Create StorageService
9.  Create background job system
10. Create extraction/summary pipeline
11. Create memory_entries/memory_chunks/pgvector
12. Create review-before-memory flow
13. Create basic AI Chat with source citation
14. Create Activity Timeline + Audit logs
15. Validate Phase 1 acceptance criteria
```

---

## Phase 2 — Finance Workspace 📋

```text
Receipt/Bill → OCR → Human Review → Finance Record → Vendor/Category →
Monthly Summary → VAT/Tax → Work Memory → AI Finance Answer
```
finance dashboard · receipt/bill OCR · OCR review · income/expense records · vendor/category mgmt ·
VAT/tax summary · monthly/cash-flow summary · CSV/XLSX import · export report · approval queue ·
duplicate receipt detection · AI finance explanation

> กฎ: ไม่มี finance posting โดย LLM · ตัวเลขคำนวณด้วย deterministic code · record link source receipt

---

## Phase 3 — Handover / New Employee Continuity 📋

Department Lead สร้าง Handover Report (จาก approved memory + activity + documents) → พนักงานใหม่อ่าน + ถาม AI ต่อ ตามสิทธิ์
> Handover ห้ามเป็นช่องทางข้าม permission

---

## Phase 4 — Department Workspace Expansion 📋

ทุกแผนกใช้ pattern เดียวกัน (Dashboard · Documents · Files · Notes · Work Memory · Activity · AI Assistant Panel · Pending Reviews · Approvals · Settings) + tools เฉพาะแผนก · AI Assistant Panel per workspace

---

## Phase 5 — Full AI Chat Experience 📋

ขยาย AI Chat จาก basic (Phase 1) → เต็มรูปแบบ: rename/archive · regenerate · attach · save answer as note ·
create task/activity from answer · preview cited source · ฯลฯ (ดู [SYSTEM_SPEC.md](SYSTEM_SPEC.md) §2.6)

---

## Phase 6 — Field & Production Mobile / Mini App / LINE 📋

mobile mini app (offline/local capture) → sync เข้า server → review → Work Memory
> Mobile implementation = **open decision** (PWA / LINE Chatbot / LINE Mini App / wrapper) — ดู [DECISIONS.md](DECISIONS.md)
> Phase 1 แค่เก็บ data model/API ให้ยืดหยุ่น ไม่ build

---

## Phase 7 — Admin / Owner Command Center 📋

company overview · users · departments · roles/permissions · pending reviews · audit logs ·
activity overview · Work Memory overview · system health · AI model status · storage status ·
backup status · handover management
> เข้าถึงข้อมูล sensitive ข้ามแผนกต้องถูก audit

---

## Out of the 7 Phases (deferred / maybe never in core)

```text
multi-tenant SaaS · full Google Docs editor · real-time collaboration · full spreadsheet editor ·
subscription/payment · KYC · social publishing · complex notification system · external cloud AI for company data
```
