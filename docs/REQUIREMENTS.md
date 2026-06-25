# REQUIREMENTS.md

> **หน้าที่ของไฟล์นี้:** ระบบนี้ต้องการอะไร ใครใช้ และทำไปเพื่ออะไร
> Source of truth สำหรับ *เป้าหมายและผู้ใช้* ของ MindKeep — ถ้าจะรู้ว่า "ทำระบบนี้ไปทำไม" อ่านไฟล์นี้

---

## 1. Product Name & Naming Rule

Product ใหม่ใช้ชื่อว่า **MindKeep**

MindKeep คือระบบ **AI workplace memory** สำหรับองค์กร ไม่ใช่ LongRian เวอร์ชันใหม่ และไม่ใช่การซ่อม repo เก่า

ชื่อ **LongDuem / ลองดื่ม** ใช้เป็น demo company / case study โดยจำลองว่าเป็นบริษัทสวนมะพร้าวและขายน้ำมะพร้าวที่นำ MindKeep ไปใช้จริงภายในองค์กร

```text
MindKeep = product / system
LongDuem = demo company / customer case
```

---

## 2. One-Sentence Definition

```text
MindKeep is a local-first AI workplace memory system that turns real employee work
into searchable organizational knowledge while preserving department-level privacy.
```

MindKeep คือสถานที่ทำงานภายในองค์กรที่ใช้ AI ช่วย **จัดเก็บ จัดการ เรียบเรียง ค้นคืน และสรุป** ความรู้จากงานที่เกิดขึ้นจริงของพนักงาน เช่น เอกสาร ไฟล์ โน้ต การแก้ไขงาน การอนุมัติ activity การตัดสินใจ และบริบทของงาน

ข้อมูลเหล่านี้จะถูกจัดเก็บเป็น **Work Memory** เพื่อให้พนักงานคนใหม่หรือคนในแผนกเดียวกันสามารถค้นคืนและทำงานต่อได้ผ่าน AI/RAG ตามสิทธิ์ที่ได้รับ

---

## 3. What MindKeep Is

```text
- Internal AI workplace
- Document and file workspace
- Work Memory system
- Permission-aware RAG system
- Department-based knowledge assistant
- Handover and continuity support system
- Local-first / on-premise AI system for SMEs
```

MindKeep ควรช่วยให้องค์กร:

```text
- Keep knowledge when employees leave
- Let new employees understand previous work faster
- Organize documents and work history
- Search old work through AI
- Summarize documents and activities
- Reuse old work safely
- Keep sensitive company data inside the company
```

---

## 4. What MindKeep Is Not

```text
- A normal chatbot
- A public SaaS AI tool
- A Google Docs replacement in Phase 1
- A full ERP / accounting system in Phase 1
- A system that lets AI decide permissions
- A system that sends internal company data to external AI APIs
- A system that automatically trusts AI output without human review
```

---

## 5. Who Uses It — Users & Roles

MindKeep ใช้ role หลักให้น้อยที่สุด เพื่อไม่ให้ระบบซับซ้อนเกินจำเป็น

### Base roles

```text
employee
department_lead
owner_manager
```

| Role | ความหมาย | อำนาจหลัก |
|---|---|---|
| `employee` | พนักงานทั่วไป แยกตามแผนกที่สังกัด | ทำงานพื้นฐานเฉพาะในแผนกตัวเอง |
| `department_lead` | หัวหน้าแผนก | อำนาจสูงสุด **เฉพาะภายในแผนกตัวเอง** (อนุมัติ Work Memory ได้) |
| `owner_manager` | เจ้าของ / ผู้จัดการบริษัท | เห็นภาพรวมและบริหารระดับองค์กร, ข้ามแผนกได้ตาม policy + audit |

> รายละเอียด permission ต่อ role + permission ย่อย (finance access, OCR access, memory approval ฯลฯ)
> และ visibility levels อยู่ใน [SYSTEM_SPEC.md](SYSTEM_SPEC.md) §Permission และ [DATA_MODEL.md](DATA_MODEL.md)

permission ย่อยตามฟีเจอร์ (เช่น `finance:ocr_use`, `memory:approve`, `users:manage`) เป็น **capability** ภายใน role ไม่ใช่ role หลักใหม่ — Phase แรกเลี่ยง role ที่ซับซ้อนเกินจำเป็น

---

## 6. Why — Problem & Outcome

ปัญหาที่ MindKeep แก้:

```text
- ความรู้กระจุกอยู่กับคนเดียว พอลาออกแล้วความรู้หาย
- พนักงานใหม่รับงานต่อช้า ไม่รู้ว่าของเก่าทำไว้ยังไง
- เอกสาร/ไฟล์/งานเก่า ค้นยาก ไม่มีที่รวม
- อยากใช้ AI ช่วยค้น/สรุป แต่กลัวข้อมูลบริษัทรั่วออก cloud
```

ผลลัพธ์ที่ต้องการ: ทำให้ **งานประจำวันของพนักงานกลายเป็นความรู้ขององค์กร** อย่างปลอดภัย ค้นได้ ส่งต่อได้ โดยข้อมูลไม่หลุดออกนอกบริษัท

---

## 7. Deployment Direction

MindKeep เวอร์ชันแรกเป็นระบบแบบ **local-first / on-premise per company**

แต่ละบริษัทมี instance ของตัวเอง เช่น:

```text
- Company server
- Mini server
- Local workstation
- Notebook used as internal server
```

ข้อมูลของแต่ละบริษัทอยู่ใน environment ของบริษัทนั้นเอง

> **Phase 1 ไม่ใช่ multi-tenant SaaS** ที่หลายบริษัทใช้ database / shared backend เดียวกัน
> (ดู decision ใน [DECISIONS.md](DECISIONS.md))

---

## 8. Non-Negotiable Data Privacy Rule

หลักที่สำคัญที่สุดของ MindKeep:

```text
Sensitive company data must not leave the company by default.
```

ข้อมูลที่ต้องอยู่ภายในระบบของบริษัท:

```text
Customer data · Finance data · Supplier data · Internal documents · Confidential files ·
Employee work history · Work Memory · RAG context · Uploaded files · OCR extracted text · Chat history
```

- AI core ต้องใช้ **local model ผ่าน local runtime เช่น Ollama**
- External AI APIs (OpenAI, Anthropic, Gemini, cloud LLM อื่น) **ไม่ใช่ default path** และห้ามใช้กับข้อมูลภายในบริษัท เว้นแต่เจ้าของระบบอนุญาตชัดเจนเป็นกรณีพิเศษ

---

## 9. AI Constraints

AI ต้องทำงานภายใต้ข้อจำกัดเหล่านี้:

```text
- AI must obey backend permissions
- AI must retrieve only allowed documents and memory
- AI must cite or link sources when answering from company data
- AI must not silently modify approved work
- AI must not approve its own output
- AI must not expose cross-department confidential data
```

AI runtime หลักใน MVP คือ **Ollama local model** — ระบบไม่ fix model เดียวตลอดไป (แต่ละบริษัท hardware ไม่เท่ากัน) แต่ demo phase ใช้ model เบาเพื่อให้รันได้จริง

---

## 10. Related Docs

| ต้องการรู้ | อ่านที่ |
|---|---|
| ฟีเจอร์ทำงานยังไง / journeys | [SYSTEM_SPEC.md](SYSTEM_SPEC.md) |
| Phase 1 ทำ/ไม่ทำอะไร | [SCOPE.md](SCOPE.md) |
| โครง repo / module | [PROJECT_MAP.md](PROJECT_MAP.md) |
| สถาปัตยกรรม / data flow | [ARCHITECTURE.md](ARCHITECTURE.md) |
| ตาราง / entity | [DATA_MODEL.md](DATA_MODEL.md) |
| endpoint หลัก | [API_SPEC.md](API_SPEC.md) |
| ลำดับ phase | [ROADMAP.md](ROADMAP.md) |
| decision สำคัญ | [DECISIONS.md](DECISIONS.md) |
| เกณฑ์ว่าสำเร็จ | [ACCEPTANCE_CRITERIA.md](ACCEPTANCE_CRITERIA.md) |
