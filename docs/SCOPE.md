# SCOPE.md

> **หน้าที่ของไฟล์นี้:** รอบแรก (Phase 1) ทำอะไร / ยังไม่ทำอะไร
> ถ้าจะรู้ว่า "อันนี้อยู่ใน Phase 1 ไหม" อ่านไฟล์นี้ — scope เปลี่ยนต้องอัปเดตที่นี่

Phase 1 = **Document + Work Memory Core** (ดูลำดับ phase ทั้งหมดที่ [ROADMAP.md](ROADMAP.md))

---

## 1. Phase 1 — In Scope ✅

แกนระบบที่ต้องทำให้ใช้ได้ก่อน:

```text
- auth / login
- users / departments / basic permissions
- Home dashboard shell
- Profile basic
- Documents (core)
- file upload
- file preview
- simple note / document (in-app, editable)
- metadata / tag / visibility
- text extraction
- AI summary
- review before memory
- Work Memory
- pgvector embedding
- permission-aware RAG
- AI Chat basic
- source citation
- Activity Timeline
- Audit logs for sensitive actions
- local filesystem via StorageService
- background jobs (with status + retry)
- docs source of truth
```

### Phase 1 — Hybrid Document approach

```text
- File library
- File upload
- File preview
- Simple note/document editor
- Metadata/tag/department ownership
- Extraction
- AI summarization
- Review before memory
- Work Memory approval
- Permission-aware RAG
- Source citation
- Simple version history
```

> Phase 1 **ยังไม่ทำ** full Google Docs-like editor

---

## 2. Phase 1 — Out of Scope ❌

```text
- Full Google Docs-level editor
- Real-time collaborative editing
- Full spreadsheet editor
- Complex comments workflow
- Notification delivery system
- Multi-tenant SaaS
- Mobile app (production)
- LINE integration (production)
- Social publishing
- Full ERP / accounting replacement
- Automatic accounting / tax filing / finance posting by LLM
- Cross-department unrestricted AI search
- External cloud AI processing of internal documents
- Subscription / payment system
- KYC full system
```

> ฟีเจอร์ใหญ่เหล่านี้ส่วนมากอยู่ใน Phase 2–7 (Finance, Handover, Dept Workspace, AI Chat เต็ม, Field/Mobile, Admin) — ดู [ROADMAP.md](ROADMAP.md)

---

## 3. Phase 1 — File Support

ต้องรองรับไฟล์เหล่านี้ และ **ทุกไฟล์ที่รองรับต้องมี preview screen**:

```text
PDF · JPG · JPEG · PNG · WEBP · DOCX · XLSX · CSV · in-app simple note/document
```

### 3.1 Preview behavior

```text
PDF                  = PDF preview
Images (JPG/PNG/...) = image preview
DOCX                 = read-only document preview
CSV                  = table preview
XLSX                 = sheet/table preview
In-app note/document = native preview/edit screen
```

### 3.2 Editing scope (Phase 1)

```text
- Edit in-app simple note/document (editable)
- Uploaded PDF/DOCX/XLSX/CSV/images = read-only preview
- Full editor and spreadsheet editor = later phases
```

### 3.3 Extraction / RAG behavior per type

```text
PDF    : extract text → summarize → embed after approval
DOCX   : extract text → summarize → embed after approval
CSV    : parse headers/sample rows → summarize dataset → embed summary after approval
XLSX   : parse sheets/headers/sample rows → summarize workbook → embed summary after approval
Images : OCR if text/receipt/form/label/note → summarize extracted text →
         store image metadata even if OCR empty → embed OCR summary after approval
Note   : summarize directly → embed text/summary after approval
```

> AI answers ที่ใช้ document/memory data ต้องมี **source citation หรือ source link** เสมอ

---

## 4. Boundary Rules (กันงานบานปลาย)

```text
- ไม่มี Work Memory โดยไม่ผ่าน human approval
- ไม่มี AI retrieval โดยไม่ผ่าน permission filter
- ไม่ส่ง sensitive company data ไป external AI โดย default
- field/mobile = future-ready แต่ "Do not build in Phase 1" — แค่เก็บ data model/API ให้ยืดหยุ่น
- restricted visibility อาจทำงานใกล้ private ก่อน ถ้ายังไม่มี explicit grant system
```

> เกณฑ์ว่า Phase 1 สำเร็จเมื่อไร → [ACCEPTANCE_CRITERIA.md](ACCEPTANCE_CRITERIA.md)
