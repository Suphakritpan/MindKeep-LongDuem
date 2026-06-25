# DECISIONS.md

> **หน้าที่ของไฟล์นี้:** บันทึก decision สำคัญ (ADR-style) — เช่น ใช้ PostgreSQL + pgvector, local-first
> ถ้า decision เปลี่ยน → อัปเดตที่นี่ (docs rule: "If a decision changes, update DECISIONS.md")

Format: แต่ละข้อ = **Decision · Context · Consequence**
สถานะ: ✅ Accepted · 🟡 Open (ยังไม่ตัดสิน)

---

## ADR-001 ✅ Greenfield rebuild, not fix the old repo

- **Decision:** เริ่ม repo ใหม่ (MindKeep) ไม่ต่อยอดบน repo เก่า (LongRian)
- **Context:** repo เก่ามี accumulated drift, dead/duplicate routes, split prefixes, flag-off RAG, undocumented test failures (ดู `docs/reports/OLD_PROJECT_FREEZE_NOTE.md`)
- **Consequence:** ใช้ repo เก่าเป็น **reference + proven logic to port** เท่านั้น (permission gate, finance calculators, OCR flow) — ไม่ใช่ foundation

## ADR-002 ✅ Product = MindKeep, Demo company = LongDuem

- **Decision:** `MindKeep` = product/system; `LongDuem / ลองดื่ม` = demo company/case (สวนมะพร้าว + น้ำมะพร้าว)
- **Consequence:** ห้ามใช้ชื่อ LongRian/longrian ใน code/package ใหม่

## ADR-003 ✅ Local-first / on-premise per company (ไม่ใช่ multi-tenant SaaS ใน Phase 1)

- **Decision:** แต่ละบริษัทรัน instance ของตัวเอง ข้อมูลอยู่ใน environment บริษัทนั้น
- **Context:** ข้อมูล sensitive ต้องไม่ออกนอกบริษัทโดย default; ลูกค้าเป็น SME
- **Consequence:** Phase 1 ไม่มี shared backend/database ข้ามบริษัท; ระบบต้องทำงานได้บน LAN เมื่อไม่มีอินเทอร์เน็ต

## ADR-004 ✅ Sensitive company data must not leave the company by default

- **Decision:** ข้อมูลบริษัท (customer/finance/supplier/docs/Work Memory/OCR/chat) อยู่ในระบบบริษัท
- **Consequence:** AI core ใช้ local model; external AI APIs ไม่ใช่ default path และห้ามใช้กับข้อมูลภายในเว้นแต่เจ้าของอนุญาตชัดเจน

## ADR-005 ✅ AI runtime = Ollama local model (model เปลี่ยนได้)

- **Decision:** MVP ใช้ Ollama local model; ไม่ fix model เดียวตลอดไป
- **Context:** hardware แต่ละบริษัทไม่เท่ากัน
- **Consequence:** model เลือกผ่าน config ก่อน, Admin UI ทีหลัง; demo ใช้ model เบา

## ADR-006 ✅ PostgreSQL + pgvector เป็น single data/RAG store (ไม่ใช้ dual ChromaDB)

- **Decision:** PostgreSQL เป็น source of truth + vector index (pgvector)
- **Context:** repo เก่าใช้ Chroma active + pgvector flag-off → version skew, dual store สับสน
- **Consequence:** ลด service ที่ต้องติดตั้ง, backup ง่าย, permission filter ผูกกับ data ได้ชัด
- **Rule:** `pgvector = retrieval index, not permission authority`

## ADR-007 ✅ Permission before retrieval

- **Decision:** resolve permission → กำหนด allowed collections → query → recheck → ส่งให้ LLM
- **Consequence:** AI ใช้ permission เดียวกับ backend; vector search ไม่ใช่ผู้ตัดสินสิทธิ์; ทุก retrieval log

## ADR-008 ✅ Human review before Work Memory

- **Decision:** ไฟล์/โน้ตที่อัปโหลดไม่กลายเป็น searchable memory อัตโนมัติ — ต้อง approve ก่อน
- **Who approves:** `department_lead`, `owner_manager` (หรือ capability `memory:approve`)
- **Consequence:** rejected content คงอยู่เป็น file แต่ AI ค้นไม่ได้; approval สร้าง activity + audit

## ADR-009 ✅ Minimal base roles + capability permissions

- **Decision:** base roles = `employee` · `department_lead` · `owner_manager` เท่านั้น
- **Context:** เลี่ยง role ซับซ้อน (ไม่มี reviewer/finance_staff/admin เป็น role หลัก)
- **Consequence:** ฟีเจอร์เฉพาะใช้ capability ย่อย (เช่น `finance:ocr_use`, `users:manage`) แทน role ใหม่

## ADR-010 ✅ Visibility: `public_internal` naming + `shared_knowledge` เป็น memory-only

- **Decision:**
  - ใช้ชื่อ `public_internal` (ไม่ใช่ `shared_internal`)
  - แยกขอบเขตค่า: **documents/files** ใช้ `doc_visibility` = `private · department · public_internal · restricted`;
    **memory_entries/memory_chunks** ใช้ `mem_visibility` = 4 ค่าข้างต้น **+ `shared_knowledge`**
- **Context:** `public_internal` (เห็นทั้งองค์กร) ≠ `shared_knowledge` (AI memory กลาง). ถ้าให้ documents
  ตั้ง `shared_knowledge` ได้ตรง ๆ จะข้าม approval gate และทำให้สองความหมายปนกัน
- **Consequence:** `shared_knowledge` เกิดได้เฉพาะตอน promote memory หลัง approval (ต้องมี `shared_knowledge:approve`);
  restricted Phase แรกทำงานใกล้ private ถ้ายังไม่มี explicit grant. ดู [DATA_MODEL.md](DATA_MODEL.md) §0

## ADR-011 ✅ StorageService abstraction (local filesystem first)

- **Decision:** ไฟล์เก็บใน local FS ก่อน แต่ code ผ่าน `StorageService` เสมอ
- **Consequence:** อนาคตเปลี่ยนเป็น MinIO/S3 ได้โดยไม่รื้อ; `uploads/` ต้อง gitignore (lesson จาก repo เก่า)

## ADR-012 ✅ Background queue สำหรับงานหนัก (durable jobs)

- **Decision:** extraction/OCR/preview/summary/embed ทำใน background ไม่ block request
- **Context:** repo เก่าใช้ FastAPI `BackgroundTasks` → jobs ไม่ durable, หายเมื่อ restart
- **Consequence:** job record เก็บใน DB, มี status + retry; implementation (RQ/Celery/DB-queue) เลือกภายหลัง

## ADR-013 ✅ Finance numbers by deterministic code, never LLM (Phase 2)

- **Decision:** ตัวเลขการเงินคำนวณด้วยโค้ด; LLM อธิบายได้ แต่ไม่คำนวณ/ไม่ post record
- **Consequence:** finance record ต้อง human confirm + link source receipt

## ADR-014 ✅ Docs are part of "done"

- **Decision:** feature ไม่นับว่าเสร็จจนกว่า code + tests + docs + roadmap status อัปเดต
- **Consequence:** no duplicate source of truth; no empty placeholder docs; raw requirement เก็บใน `docs/_source/`

## ADR-015 ✅ Build order: docs → skeleton → core modules (อย่าทำพร้อมกัน)

- **Decision:** ทำตามลำดับ Step 1 (docs) → Step 2 (Master Prompt) → Step 3 (skeleton+config) → Step 4 (Phase 1 batches)
- **Consequence:** รอบนี้ (Step 1–2) **ห้าม** สร้าง feature/endpoint/migration/frontend page ลึก ๆ

## ADR-016 🟡 Field / Mobile implementation = OPEN

- **Decision:** ยังไม่ล็อก — ตัวเลือก: **PWA · LINE Chatbot · LINE Mini App · future mobile wrapper**
- **Context:** PWA เหมาะ local-first สุด; LINE ใช้ง่ายแต่ข้อมูลผ่าน LINE infra (ระวัง sensitive)
- **Consequence:** Phase 1 ไม่ build — แค่เก็บ data model/API ให้ยืดหยุ่นรองรับ field capture (Phase 6)

---

## Open Decisions to Revisit (assumptions ไม่ใช่มติสุดท้าย)

```text
- Phase 1 demo departments: Finance, Marketing, Field/Production, Admin
- Legal เริ่มเป็น shared compliance knowledge ไม่ใช่ full workspace
- Shared Knowledge มีอยู่ แต่ต้อง approval
- restricted visibility ทำงานใกล้ private ก่อน ถ้ายังไม่มี explicit grant system
- background job engine ตัวจริง (RQ / Celery / DB-backed)
```
