# ACCEPTANCE_CRITERIA.md

> **หน้าที่ของไฟล์นี้:** เช็กยังไงว่าระบบทำสำเร็จจริง (Phase 1)
> ใช้เป็น checklist ตอน "Validate Phase 1 acceptance criteria" (build order step 15)

แต่ละข้อต้องพิสูจน์ได้ด้วยการใช้งานจริง/test — ไม่ใช่แค่ "มีโค้ด"

---

## 1. Phase 1 Pass Checklist

### Auth & Workspace
- [ ] user login เข้า MindKeep ได้
- [ ] user เข้า workspace/dashboard ที่ scoped ตามแผนกของตัวเองได้ (Home/Dashboard shell + department scope — **ไม่ใช่** full Department Workspace ซึ่งเป็น Phase 4)

### Documents & Files
- [ ] user upload supported files ได้ (PDF · JPG · JPEG · PNG · WEBP · DOCX · XLSX · CSV)
- [ ] user preview supported files ได้ (ทุกชนิดมี preview screen ตาม [SCOPE.md](SCOPE.md) §3.1)
- [ ] user create simple note/document (in-app, editable) ได้

### Extraction & Review before Memory
- [ ] system extract + summarize content ได้
- [ ] content **ต้องรอ review** ก่อนเข้า memory (ไม่เข้า memory อัตโนมัติ)
- [ ] department_lead approve/reject content ได้ (เฉพาะแผนกตัวเอง)
- [ ] approved content เข้า Work Memory ได้; rejected content คงเป็น file แต่ AI ค้นไม่ได้

### AI & RAG
- [ ] AI search เฉพาะ memory ที่ user มีสิทธิ์ (permission-aware)
- [ ] AI answer มี source citation
- [ ] user เปิด source citation ได้
- [ ] employee search ข้ามแผนก **ไม่ได้**
- [ ] ถ้าไม่มี source ที่เข้าถึงได้ → AI บอกว่าไม่พบข้อมูลที่มีสิทธิ์เข้าถึง

### Memory vs Activity
- [ ] shared_knowledge เป็นช่องทางกลางที่ผ่าน approval
- [ ] public_internal ไม่ได้แปลว่า AI ทุกแผนกใช้เป็น memory ได้ทันที
- [ ] Activity Timeline แสดงประวัติงานจริง แยกจาก Work Memory

### Infra & Safety
- [ ] background jobs มี status + retry (durable)
- [ ] sensitive action มี audit log (memory approval, cross-dept access)
- [ ] system run local/on-prem ได้
- [ ] **ไม่มี** sensitive company data ถูกส่งไป external AI โดย default
- [ ] file เก็บผ่าน StorageService (local filesystem)

### Docs
- [ ] docs / roadmap / status อัปเดตตรงกับ code

---

## 2. Non-Negotiable Rules (guardrails — ต้องไม่ละเมิด)

ถ้าข้อใดข้อหนึ่งถูกละเมิด ถือว่า Phase 1 **ไม่ผ่าน** แม้ checklist ด้านบนครบ:

```text
- No AI retrieval without permission filter
- No Work Memory without human approval
- No sensitive company data to external AI by default
- No finance posting by LLM
- No hidden cross-department access
- No duplicate docs source of truth
- No feature marked done without tests/docs/status
- No route-level business logic overload
- No vector store acting as permission authority
```

---

## 3. How to Verify (แนวทางทดสอบ end-to-end)

```text
1. Login เป็น employee (Finance) → upload ใบเสร็จ/PDF → เห็น preview → submit for review
2. Login เป็น department_lead (Finance) → เห็น pending → approve → ข้อมูลเข้า Work Memory
3. กลับเป็น employee (Finance) → ถาม AI Chat → ได้คำตอบ + source citation → เปิด source ได้
4. ถาม AI เรื่องข้อมูลของ Marketing/Field → AI ตอบว่าไม่พบข้อมูลที่มีสิทธิ์ (ค้นข้ามแผนกไม่ได้)
5. ตรวจ Activity Timeline + audit log ว่ามี event approval ถูกบันทึก
6. ตรวจ background job ของ extraction/embedding ว่ามี status; ลอง fail แล้ว retry ได้
7. รัน stack แบบ local (ไม่มีอินเทอร์เน็ต) → ยังตอบจาก local model ได้
```

> เมื่อทุก checklist ผ่าน + ไม่มี non-negotiable rule ถูกละเมิด → Phase 1 = Done (อัปเดต [ROADMAP.md](ROADMAP.md))
