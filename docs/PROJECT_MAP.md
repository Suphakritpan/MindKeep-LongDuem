# PROJECT_MAP.md

> **หน้าที่ของไฟล์นี้:** repo ใหม่วาง folder / module ยังไง
> ถ้า module เปลี่ยน ต้องอัปเดตที่นี่ (docs rule: "If module changes, update PROJECT_MAP.md")

---

## 1. Monorepo Structure

MindKeep ใช้ **monorepo** เพื่อแยก frontend / backend / future mobile / infra / docs ให้ชัดตั้งแต่ต้น ไม่ปนกันเหมือน repo เก่า

```text
mindkeep/
├── apps/
│   ├── web/          # Next.js frontend
│   ├── api/          # FastAPI backend
│   └── mobile/       # future field/mobile app, PWA, LINE Mini App, or wrapper
├── packages/
│   ├── shared/       # shared types/constants
│   ├── ui/           # shared UI components
│   └── config/       # shared config/schema
├── infra/            # docker, deployment, env examples
├── docs/             # requirements, specs, architecture, scope (source of truth)
├── scripts/          # seed, backup, maintenance
└── data/             # demo/sample data only
```

> `apps/mobile/` = future-ready placeholder. **ไม่ build ใน Phase 1** (ดู [SCOPE.md](SCOPE.md))

---

## 2. Backend Module Boundary

Backend ใช้ **FastAPI** และแยก module ตาม bounded context:

```text
apps/api/app/
├── core/             # config, security, error codes, base utilities
├── db/               # session, base model, migrations wiring
├── modules/
│   ├── auth/
│   ├── users/
│   ├── departments/
│   ├── permissions/
│   ├── documents/
│   ├── files/
│   ├── memory/
│   ├── ai/
│   ├── chat/
│   ├── finance/      # Phase 2
│   ├── handover/     # Phase 3
│   ├── field/        # Phase 6
│   ├── audit/
│   └── admin/        # Phase 7
└── main.py
```

### 2.1 Per-module file convention

แต่ละ module ควรมี boundary ของตัวเอง:

```text
modules/<name>/
├── routes.py        # HTTP layer only — thin
├── service.py       # business logic
├── models.py        # SQLAlchemy / DB models
├── schemas.py       # Pydantic request/response
├── permissions.py   # permission checks for this module
└── tests/
```

### 2.2 Phase 1 active modules

```text
✅ Phase 1: core, db, auth, users, departments, permissions,
            documents, files, memory, ai, chat, audit
🔜 Later  : finance(P2), handover(P3), field(P6), admin(P7)
```

> **Step 3 scaffolding rule:** สร้าง folder ของ **ทุก module** ตามรายการข้างบนเพื่อให้ tree ตรง doc นี้ —
> Phase 1 ได้ `__init__.py` + docstring, later modules ได้ folder + `__init__.py` ที่ mark `# Phase N — placeholder`.
> **ไม่ implement** routes/services/models ของ module ใดทั้งสิ้นในรอบ skeleton (ดู [MASTER_PROMPT.md](MASTER_PROMPT.md) §2)

---

## 3. Module Boundary Rules

```text
- Route handler ไม่ควรมี business logic หนัก (thin routes)
- Permission ต้องเช็กใน backend service ไม่ใช่ frontend
- AI/RAG ต้องเรียกผ่าน permission service ก่อนเสมอ
- Document, Memory, AI, Finance, Field ต้องไม่ผูกกันแบบมั่ว ๆ
- module ห้าม import ข้ามกันมั่ว — shared logic ใส่ core หรือ shared service ที่ตั้งใจออกแบบไว้เท่านั้น
```

---

## 4. Frontend (apps/web) — high level

```text
apps/web/
├── app/              # Next.js routes (Home dashboard, documents, memory, chat, profile)
├── components/       # feature + ui components (ใช้ร่วมกับ packages/ui)
├── lib/              # api client, auth, helpers
└── ...
```

> รายละเอียด route/page ของ Phase 1 จะถูกแตกเป็น implementation batches (Step 4) — ยังไม่ scaffold ในรอบเอกสารนี้

---

## 5. Docs as Source of Truth

```text
docs/
├── REQUIREMENTS.md          # ระบบต้องการอะไร ใครใช้ ทำไป
├── SYSTEM_SPEC.md           # ระบบทำงานยังไง ฟีเจอร์หลัก + journeys
├── SCOPE.md                 # in scope / out of scope (Phase 1)
├── PROJECT_MAP.md           # โครงสร้าง repo และ module (ไฟล์นี้)
├── ARCHITECTURE.md          # architecture, data flow, deployment
├── DATA_MODEL.md            # entity/table หลัก
├── API_SPEC.md              # endpoint หลัก Phase 1
├── ROADMAP.md               # phase, Done / In Progress / Planned
├── DECISIONS.md             # decision log สำคัญ
├── ACCEPTANCE_CRITERIA.md   # เงื่อนไขว่าระบบสำเร็จเมื่อไร
├── MASTER_PROMPT.md         # Claude Code bootstrap prompt สำหรับเริ่ม repo ใหม่
├── _source/                 # raw requirement collection (Round 1–5 + Spec v0.1) — archive
├── product/  api/  reports/ # old LongRian reference material (do not treat as current truth)
```

```text
Feature is not done until code, tests, docs, and roadmap status are updated.
No empty placeholder docs.
No duplicate source of truth.
If a decision changes → update DECISIONS.md.
If scope changes     → update SCOPE.md.
If module changes    → update PROJECT_MAP.md.
```
