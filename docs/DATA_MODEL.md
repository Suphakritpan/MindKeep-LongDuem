# DATA_MODEL.md

> **หน้าที่ของไฟล์นี้:** table / entity สำคัญ — users, documents, memory, chunks, audit ฯลฯ
> เป็น **conceptual data model** (ไม่ใช่ migration จริง — ดู [SCOPE.md](SCOPE.md): Phase นี้ไม่สร้าง migration)
> field names เป็น *แนวทาง* ที่จะ lock จริงตอน implement Phase 1

ใช้ **PostgreSQL + pgvector** เป็นทั้ง source of truth และ vector index (ดู [ARCHITECTURE.md](ARCHITECTURE.md) §3)

---

## 0. Shared Enums (ต้องตรงกันทุก doc/โค้ด)

```text
role           : employee | department_lead | owner_manager
doc_visibility : private | department | public_internal | restricted
mem_visibility : private | department | public_internal | restricted | shared_knowledge
doc_state      : draft | pending_review | approved_to_memory | rejected
job_status     : queued | running | succeeded | failed
job_type       : extract | ocr | preview | summary | embed | reembed | ai_postprocess
activity_status: pending | approved | rejected | locked
```

> **Naming rule:** `public_internal` (ไม่ใช่ `shared_internal`) — ดู [SYSTEM_SPEC.md](SYSTEM_SPEC.md) §1.1
>
> **`shared_knowledge` = memory-only.** `documents`/`files` ใช้ `doc_visibility` (4 ค่า) เท่านั้น —
> เอกสารดิบจะเป็น `shared_knowledge` เองไม่ได้. ค่า `shared_knowledge` มีได้เฉพาะ `memory_entries`/
> `memory_chunks` (`mem_visibility`) **หลังผ่าน approval** เท่านั้น. สอดคล้อง [SYSTEM_SPEC.md](SYSTEM_SPEC.md) §1.2
> (public_internal ≠ shared_knowledge) และ ADR-010 ใน [DECISIONS.md](DECISIONS.md)
>
> **Lock & delete = flags ไม่ใช่ state.** `doc_state` คุมเฉพาะ review-lifecycle. การ lock/delete เป็น
> field แยก (`is_locked`/`locked_by`/`locked_at`, `deleted_at`) เพื่อให้เอกสาร `approved_to_memory`
> ถูก lock หรือ soft-delete ได้พร้อมกันโดยไม่เสีย lifecycle state เดิม

---

## 1. Phase 1 Core Tables

ตารางที่ต้องมีใน Phase 1 (✅) — ที่เหลือเป็น later phase

### Identity & Access

**users** ✅
```text
id (uuid, pk) · email (unique) · password_hash · full_name · phone · avatar_url ·
role (role enum, base) · is_active · created_at · updated_at
```

**departments** ✅
```text
id (uuid, pk) · key (e.g. finance, marketing, field, admin) · name · description · created_at
```

**user_departments** ✅  (พนักงานอยู่ได้หลายแผนก + active department)
```text
id (uuid, pk) · user_id (fk users) · department_id (fk departments) ·
role_in_department (role enum) · is_active_default (bool) · created_at
```

**permission_grants** ✅  (capability ย่อย เช่น finance:ocr_use, memory:approve, users:manage)
```text
id (uuid, pk) · user_id (fk users) · capability (text) · department_id (fk, nullable) ·
granted_by (fk users) · created_at
```
> capabilities (ตัวอย่าง): `memory:approve`, `shared_knowledge:approve`, `users:manage`,
> `departments:manage`, `roles:manage`, `system:settings`, `audit:view`,
> `finance:ocr_use`, `finance:record_submit`, `finance:record_confirm`, `finance:record_post`,
> `finance:summary_view`, `finance:settings_manage`

### Documents & Files

**documents** ✅  (แกนหลัก — note/uploaded doc)
```text
id (uuid, pk) · title · doc_type (note | uploaded) · owner_id (fk users) ·
department_id (fk departments) · visibility (doc_visibility) · state (doc_state) ·
extracted_text (nullable) · summary (nullable) · is_locked (bool) · locked_by (fk users, nullable) ·
locked_at (nullable) · deleted_at (nullable) · created_at · updated_at
```
> `state` = review-lifecycle เท่านั้น. lock = `is_locked`/`locked_by`/`locked_at`; delete = `deleted_at`
> (soft). เอกสาร `approved_to_memory` จึงถูก lock/soft-delete ได้โดยไม่เปลี่ยน `state`

**document_versions** ✅  (แก้ approved doc = สร้าง version ใหม่ ไม่ทับของเดิม)
```text
id (uuid, pk) · document_id (fk documents) · version_no (int) · content (text, for notes) ·
created_by (fk users) · created_at
```

**files** ✅  (binary จริง ผ่าน StorageService)
```text
id (uuid, pk) · document_id (fk documents, nullable) · storage_path · original_filename ·
mime_type · size_bytes · checksum · uploaded_by (fk users) · created_at · deleted_at (nullable)
```

### Work Memory & Retrieval

**work_activities** ✅  (Activity Timeline — ประวัติงานจริง)
```text
id (uuid, pk) · actor_id (fk users) · department_id (fk departments) · action (text) ·
source_type (document | chat | ocr | finance | field) · source_id (uuid) ·
status (activity_status enum) · created_at
```

**memory_entries** ✅  (ข้อมูลที่ approved แล้ว, AI ค้นได้)
```text
id (uuid, pk) · source_document_id (fk documents) · department_id (fk departments) ·
summary · tags (text[]) · visibility (mem_visibility) · created_by (fk users) ·
approved_by (fk users) · created_at · approved_at
```
> เฉพาะที่นี่ (และ `memory_chunks`) ที่ `visibility` เป็น `shared_knowledge` ได้ — และเฉพาะเมื่อ
> reviewer ที่มี `shared_knowledge:approve` เลื่อนขึ้นเป็นความรู้กลางหลัง approval

**memory_chunks** ✅  (ก้อนข้อความ + embedding สำหรับ RAG)
```text
id (uuid, pk) · memory_entry_id (fk memory_entries) · department_id (denormalized for filter) ·
visibility (mem_visibility, denormalized for filter) · chunk_index (int) · content (text) ·
embedding (vector — pgvector column) · created_at
```
> `embeddings` ไม่ใช่ตารางแยก แต่เป็น **pgvector column** ใน `memory_chunks`
> department_id + visibility ถูก denormalize เพื่อ permission-filter ก่อน vector search

**ai_retrieval_logs** ✅  (log ว่า AI ดึง source อะไรไปตอบ)
```text
id (uuid, pk) · user_id (fk users) · chat_message_id (fk, nullable) · query · scope_department_id ·
retrieved_chunk_ids (uuid[]) · allowed (bool) · created_at
```

### Chat

**chat_sessions** ✅
```text
id (uuid, pk) · user_id (fk users) · title · active_department_id (fk departments) ·
archived (bool) · created_at · updated_at
```

**chat_messages** ✅
```text
id (uuid, pk) · session_id (fk chat_sessions) · role (user | assistant) · content ·
citations (jsonb — source refs) · created_at
```

### Jobs & Audit

**jobs** ✅  (background job records — durable; Batch D)
```text
id (uuid, pk) · type (job_type) · status (job_status) · target_type · target_id ·
payload (jsonb, nullable) · attempts (int) · max_attempts (int, default 3) · error (text, nullable) ·
created_by (fk users, nullable) · created_at · updated_at
```
> worker อ้าง status (index) + `FOR UPDATE SKIP LOCKED` เพื่อ claim งานแบบ concurrency-safe;
> `created_by` ให้ user เห็น job ของตัวเอง (owner_manager/`audit:view` เห็นทั้งหมด)

**audit_logs** ✅  (sensitive actions: approval, cross-dept access, finance confirm)
```text
id (uuid, pk) · actor_id (fk users) · action · target_type · target_id ·
department_id (nullable) · metadata (jsonb) · created_at
```

---

## 2. Relationships (high level)

```text
users ──< user_departments >── departments
users ──< permission_grants
documents ──< document_versions
documents ──< files
documents ──1:1?── memory_entries (after approval)
memory_entries ──< memory_chunks (embedding each)
chat_sessions ──< chat_messages
chat_messages ──< ai_retrieval_logs
(any sensitive action) ──> audit_logs
(any work event) ──> work_activities
```

---

## 3. Later-Phase Tables (placeholder — ไม่ทำ Phase 1)

```text
Phase 2 Finance : finance_records · vendors · categories · ocr_jobs · ocr_documents ·
                  vat_periods · finance_summaries
Phase 3 Handover: handover_reports
Phase 6 Field   : field_tasks · field_records · sync_batches
Phase 7 Admin   : system_settings · backups (หรือ derive จาก jobs/audit)
```

> ออกแบบ Phase 1 ให้ data model/API **ยืดหยุ่นพอ** รองรับ field capture + finance ในอนาคต โดยไม่ต้องรื้อ core

---

## 4. Data Rules

```text
- Uploaded file ≠ Work Memory. ต้องผ่าน human approval ก่อนจึงสร้าง memory_entries + memory_chunks
- pgvector (memory_chunks.embedding) = retrieval index เท่านั้น ไม่ใช่ permission authority
- permission ต้อง resolve ก่อน query memory_chunks (filter ด้วย department_id + visibility)
- finance numbers (later) คำนวณด้วย deterministic code ไม่ใช่ LLM
- approved_to_memory document แก้ไข = สร้าง document_versions ใหม่
- soft-delete (deleted_at) สำหรับ documents/files — ไม่ hard delete by default
```
