# SYSTEM_SPEC.md

> **หน้าที่ของไฟล์นี้:** ระบบต้องทำงานยังไง ฟีเจอร์หลักต้องมีอะไร และผู้ใช้เดินทางผ่านระบบยังไง (user journeys)
> ไฟล์นี้คือ *behavior spec* — REQUIREMENTS บอกว่า "ทำไป", ไฟล์นี้บอกว่า "ทำงานยังไง"

> 🔖 **Phase 1 focus** = สิ่งที่ต้องมีในรอบแรก (ดู [SCOPE.md](SCOPE.md)). ฟีเจอร์ที่ไม่ติด tag คือ later phase (ดู [ROADMAP.md](ROADMAP.md))

---

## 1. Permission & Visibility Model (กฎกลางที่ทุกฟีเจอร์ต้องเคารพ)

### 1.1 Visibility Levels

```text
private          เห็นเฉพาะเจ้าของเอกสาร และผู้มีสิทธิ์ตรวจสอบตาม policy
department       เห็นในแผนกเดียวกันตาม role/permission
public_internal  ทุกคนในองค์กรเห็นได้ — แต่ไม่ได้แปลว่า AI ทุกแผนกใช้เป็น memory ได้ทันที
restricted       จำกัดเฉพาะคน/role ที่กำหนด (Phase แรกทำงานใกล้ private ถ้ายังไม่มี explicit grant)
shared_knowledge ความรู้กลางที่ผ่าน approval แล้ว และ AI ทุกแผนกใช้ได้ — memory เท่านั้น (ดูด้านล่าง)
```

> **ขอบเขตการใช้ค่า:**
> - **documents / files** ใช้ได้เฉพาะ `private · department · public_internal · restricted` (`doc_visibility`)
> - **`shared_knowledge` เป็นค่าของ memory เท่านั้น** — เกิดบน `memory_entries`/`memory_chunks` (`mem_visibility`)
>   หลังผ่าน approval. เอกสารดิบจะถูกตั้งเป็น `shared_knowledge` ตรง ๆ ไม่ได้
> - **Naming rule:** ใช้ `public_internal` (ไม่ใช่ `shared_internal`) เพราะชัดกว่าและสอดคล้องระบบเดิม
> - enum ที่ตรงกับโค้ด → [DATA_MODEL.md](DATA_MODEL.md) §0; decision → ADR-010 ใน [DECISIONS.md](DECISIONS.md)

### 1.2 public_internal ≠ shared_knowledge

```text
มองเห็นได้ทั้งองค์กร  ≠  เข้า AI memory กลางทันที
ต้องมี approval ก่อนกลายเป็น shared_knowledge
```

### 1.3 AI / RAG Permission Rule

AI ต้องใช้ **permission เดียวกับ backend** ไม่ใช่สิทธิ์พิเศษ

```text
Employee in Finance asks AI
  allowed   = shared_knowledge + approved Finance Work Memory + allowed Finance documents
  NOT allowed = Field memory, Marketing memory, private docs of others, restricted w/o permission

owner_manager
  ข้ามแผนกได้ตาม policy · ต้องเลือก scope ชัดเจน · ต้องมี audit log · AI ต้องไม่ default เป็นค้นทุกแผนก
```

```text
Permission before retrieval.
Vector search is not permission authority.
Returned sources must be rechecked before AI uses them.
```

### 1.4 Document State & Flags

**Lifecycle state** (`doc_state` — มีค่าเดียวต่อเอกสาร):

```text
draft              ร่าง ยังไม่ส่งตรวจ
pending_review     ส่ง review แล้ว รอ approve
approved_to_memory ถูกอนุมัติเข้า Work Memory แล้ว — แก้ไขต้องสร้าง version ใหม่ ไม่แก้ทับ
rejected           ถูกปฏิเสธ คงเป็น file แต่ AI ค้นไม่ได้
```

**Flags ที่เป็นอิสระจาก state** (เอกสาร `approved_to_memory` ก็ lock หรือ soft-delete ได้):

```text
locked  (is_locked)  ห้ามลบ/แก้ไขโดยพนักงานทั่วไป — เป็น flag ไม่ใช่ state
deleted (deleted_at) soft-delete — ไม่ควรแก้ไขหรือค้นโดยทั่วไป, ไม่ hard delete by default
```

พนักงานทั่วไปลบได้เฉพาะเอกสารที่ตัวเองสร้างและยังไม่ lock

> เหตุผลที่แยก lock/delete ออกจาก state: เอกสารหนึ่งอาจเป็น `approved_to_memory` **และ** ถูก lock พร้อมกันได้
> ดู [DATA_MODEL.md](DATA_MODEL.md) §0 (`doc_state` + flag fields)

---

## 2. Feature Catalog

### 2.1 Home / Workplace Dashboard 🔖 Phase 1 (shell)

หลัง login ผู้ใช้เข้า **Home / Workplace Dashboard** รวมก่อน ไม่เข้าแชทหรือแผนกใดทันที

```text
Home / Dashboard
├── Sidebar
├── Top bar
├── Recent work
├── Recent documents
├── Pending reviews
├── Department shortcuts
├── AI quick access
└── User profile menu
```

เป้าหมาย: MindKeep ต้องรู้สึกเป็น "สถานที่ทำงาน" ไม่ใช่แค่หน้าแชทหรือระบบเอกสารหน้าเดียว

### 2.2 Profile / User Menu 🔖 Phase 1 (basic)

```text
Account & Profile  ดู/แก้โปรไฟล์ · ชื่อ-สกุล · รูป · เบอร์ · อีเมลหลัก · รหัสผ่าน ·
                   ดู role/department · เปลี่ยน active department (ถ้ามี >1 แผนก)
Security           2FA · ดู session/device · logout · logout all devices
Preferences        ภาษา · theme light/dark · notification preferences · privacy settings
Support            Help Center/FAQ · คู่มือ · ติดต่อผู้ดูแล · Terms/Privacy
```

> Linked social accounts, subscription, wallet, payment cards, KYC เต็มระบบ = future/optional เฉพาะกรณีจำเป็น (ไม่ใช่ core ของ on-prem)

### 2.3 Documents 🔖 Phase 1 (แกนหลัก)

Documents คือแกนหลักของ MindKeep เพราะเอกสาร/ไฟล์คือจุดเริ่มของ Work Memory

```text
upload file · preview all supported files · create simple note/document · metadata ·
tag/category · owner · department · visibility · version history · lock/unlock ·
delete/restore · submit for memory review · approve to Work Memory · AI summarize ·
AI suggest title/tags · AI suggest edit · use as template · comments(later) · export PDF/DOCX(later)
```

**🔖 Phase 1 focus:** upload · preview · simple note · extraction · summary · review before memory · approve to Work Memory · source citation

Supported file types + preview/extraction behavior → ดู [SCOPE.md](SCOPE.md) §File Support

### 2.4 Work Memory 🔖 Phase 1

ข้อมูลที่ผ่าน approval แล้ว และ AI ใช้ค้นตอบได้

```text
Memory page: memory entry · source document · summary · tags · department ·
created by · approved by · created date · visibility · search/filter · open source
```

```text
Uploaded file does not become Work Memory automatically. Human approval is required.
```

### 2.5 Activity Timeline 🔖 Phase 1

ประวัติการทำงานที่เกิดขึ้นจริง (≠ Memory)

```text
ใครทำอะไร · ทำในแผนกไหน · เกิดจาก document/chat/OCR/finance/field อะไร ·
สถานะ pending/approved/rejected/locked · link กลับไป source
```

```text
Activity = ประวัติการทำงานที่เกิดขึ้นจริง
Memory   = ข้อมูลที่ผ่าน approval แล้วและ AI ใช้ค้นตอบได้
```

### 2.6 AI Chat 🔖 Phase 1 (basic)

คล้าย ChatGPT แต่เป็น AI ภายในองค์กรที่ตอบจากข้อมูลจริงตามสิทธิ์

```text
new chat · chat history · rename · delete/archive · active department scope ·
attach document/file · source citation · preview cited source · model status ·
streaming response · regenerate · copy · save answer as note · create task/activity · clear chat
```

**🔖 Phase 1 focus:** new chat · history · department scope · source citation · model status · basic attachment

```text
AI Chat ต้องไม่ค้นทุกแผนกโดย default
AI ต้องตอบจาก shared_knowledge + department memory ที่ user มีสิทธิ์เท่านั้น
ถ้าไม่มี source ที่เข้าถึงได้ → บอกว่าไม่พบข้อมูลที่มีสิทธิ์เข้าถึง
chat history ต้องไม่หาย
```

### 2.7 Finance Workspace — Phase 2

Finance เชื่อมเป็น flow เดียว ไม่แยกกระจัดกระจาย

```text
Receipt/Bill → OCR Extraction → Human Review → Finance Record →
Vendor/Category → Monthly Summary → VAT/Tax Summary → Work Memory → AI Finance Answer
```

modules: finance dashboard · receipt/bill OCR · OCR review · income/expense records · vendor mgmt ·
category mgmt · VAT/tax summary · monthly summary · cash flow summary · CSV/XLSX import · export report ·
approval queue · duplicate receipt detection · AI finance explanation

```text
- AI/OCR ห้าม post record อัตโนมัติ — ต้อง human confirmation
- ตัวเลขการเงินคำนวณด้วย deterministic code ไม่ใช่ LLM เดา
- finance record ต้อง link กลับ source receipt
- finance data อยู่ใน Finance department โดย default
```

### 2.8 Field & Production Workspace — Phase 6

สำหรับงานสวน / ผลิต / หน้างาน

```text
มอบหมายงาน → ออกหน้างาน → บันทึก/ถ่ายรูปจากมือถือ (offline/local) →
กลับบริษัท/เชื่อม LAN → sync เข้า server → หัวหน้าแผนก review → approve เข้า Work Memory
```

functions: field task assignment · mobile capture · offline/local draft · photo capture · field note ·
harvest record · production batch record · raw material record · quantity/yield record · damaged/waste record ·
issue/problem report · timestamp · assigned staff · sync status · review after sync · approve to Work Memory

```text
ข้อมูลจากมือถือยังไม่เข้า Work Memory ทันที — ต้อง sync + review ก่อน
Mobile implementation = open decision (PWA / LINE Chatbot / LINE Mini App / wrapper) — ดู DECISIONS.md
```

### 2.9 Handover — Phase 3

ใช้เมื่อมีพนักงานใหม่หรือส่งต่องาน (แนวทาง: หัวหน้าแผนกสร้าง Handover Report ก่อน แล้วพนักงานใหม่อ่าน + ถาม AI ต่อ)

Report ควรมี: งานที่เคยทำ · เอกสารสำคัญ · decision history · งานค้าง · pattern การทำงาน · สิ่งที่คนใหม่ควรรู้ · source links

```text
พนักงานใหม่เห็นเฉพาะข้อมูลที่มีสิทธิ์
Handover ห้ามเป็นช่องทางข้าม permission
```

### 2.10 Admin / Owner Command Center — Phase 7

สำหรับ owner/manager: company overview · users · departments · roles/permissions · pending reviews ·
audit logs · activity overview · Work Memory overview · system health · AI model status · storage status ·
backup status · handover management

```text
owner/manager เห็นภาพรวมได้ — แต่การเข้าถึงข้อมูล sensitive ข้ามแผนกต้องถูก audit
```

### 2.11 Department Workspace — Phase 4 (pattern กลาง)

ทุกแผนกใช้ pattern เดียวกัน แต่มี tools เฉพาะของตัวเอง

```text
Department Workspace: Dashboard · Documents · Files · Notes · Work Memory ·
Activity Timeline · AI Assistant Panel · Pending Reviews · Approvals · Department Settings
```

---

## 3. Review Before Memory (กฎกลางของ Phase 1)

MindKeep **ต้องไม่** เปลี่ยนไฟล์ที่อัปโหลดเป็น searchable memory โดยอัตโนมัติ

```text
1. User uploads file or creates note
2. System stores original file/document
3. System extracts text or structured content
4. System generates summary and metadata
5. System shows review screen
6. Authorized reviewer checks: extracted text, summary, tags, department, visibility, sensitivity
7. Reviewer approves or rejects
8. Approved content is embedded into Work Memory
9. Rejected content stays as document/file but is NOT searchable by AI/RAG
```

ผู้ที่ approve content เข้า Work Memory ได้: `department_lead`, `owner_manager` (+ capability `memory:approve`)
พนักงานทั่วไป upload/create/preview/submit ได้ แต่ **อนุมัติเองไม่ได้**

---

## 4. Main User Journeys

### 4.1 Employee — Create Work into Memory 🔖 Phase 1

```text
Login → Home/Department Workspace → Create work (upload file / create note / attach image-doc-table)
→ System stores source → previews → extracts text/data → generates summary+tags+metadata
→ Employee reviews basic info → submits for review → status = pending_review
→ Department Lead reviews → approved: becomes Work Memory / rejected: stays as file, not AI-searchable
```

> UX principle: พนักงานไม่ควรรู้สึกว่ากำลังทำงานเพิ่มเพื่อป้อนข้อมูลให้ AI — ควรรู้สึกว่าทำงานปกติแล้ว MindKeep เก็บให้เป็นความรู้องค์กร

### 4.2 Department Lead — Review & Protect Department Memory 🔖 Phase 1

```text
Login → See Pending Reviews → Open submitted item → Compare original vs extracted summary
→ Check title/summary/tags/department/visibility/sensitivity/source → Approve / Reject / Request changes

approved → embed into department Work Memory · searchable by dept AI · source citation preserved
         · activity event + audit event created · status = approved_to_memory
rejected → stays in file library · not embedded · not AI-searchable · rejection reason saved · employee can resubmit
```

### 4.3 New Employee / Handover — Phase 3

```text
Department Lead opens Handover → select previous employee → dept scope → time range
→ Generate Handover Report → system retrieves approved Work Memory + docs + activities
→ AI summarizes → Lead reviews → new employee reads → asks AI follow-up from allowed sources
```

### 4.4 Finance — Receipt → Record → Memory — Phase 2

```text
Upload receipt → OCR extracts fields → system suggests vendor/category/amount/VAT/duplicate
→ user reviews+edits → finance lead confirms → create finance record (links to source receipt)
→ dashboard updates → approved finance info → Work Memory → AI answers with source
```

### 4.5 Field & Production — Mobile Capture → Server — Phase 6

```text
Assign field task → staff records data/photo/quantity/issue on mobile → save local/offline
→ return to office / connect LAN → sync to server → Dept Lead reviews → approved → Work Memory
```

### 4.6 AI Chat — Ask with Sources & Permission 🔖 Phase 1

```text
Open AI Chat → select/confirm active department scope → ask question
→ system resolves user permissions → retrieves shared_knowledge + allowed dept memory + allowed docs
→ AI answers with source citations → user opens cited source → may save answer as note/activity
```

> UX principle: คุ้นเคยแบบ ChatGPT แต่ปลอดภัยกว่า เพราะตอบเฉพาะข้อมูลบริษัทที่ user มีสิทธิ์เข้าถึง

---

## 5. Cross-Journey Rule (Activity & Audit)

ทุก journey ต้องสร้าง/เชื่อมกับ activity และ audit ตามความสำคัญ

```text
Document action            → Activity
Memory approval            → Activity + Audit
Finance confirmation       → Activity + Audit
Field sync                 → Activity
AI answer from company src  → Chat log + retrieval log
Cross-department owner access → Audit
```

MindKeep ต้องทำให้ผู้ใช้เห็นความต่อเนื่องของงาน ไม่ใช่แค่เก็บข้อมูลเงียบ ๆ
