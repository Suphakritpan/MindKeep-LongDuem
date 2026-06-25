# ARCHITECTURE.md

> **หน้าที่ของไฟล์นี้:** web, api, database, AI, storage, background job เชื่อมกันยังไง + deployment
> ถ้าจะรู้ว่า "ข้อมูลไหลยังไง" หรือ "ทำไม AI ถึงปลอดภัย" อ่านไฟล์นี้

---

## 1. Architecture Principles (ยึด 10 ข้อนี้)

```text
1.  Local-first by default
2.  PostgreSQL + pgvector as core data/RAG layer
3.  Permission before retrieval
4.  Human review before Work Memory
5.  Background jobs for heavy processing
6.  Source citation for AI answers
7.  Department boundary by default
8.  Shared Knowledge must be approved
9.  Field/mobile is future-ready but not Phase 1 core
10. Docs are part of done
```

---

## 2. Component Diagram (Phase 1)

```text
                          ┌─────────────────────────────┐
                          │   frontend  (Next.js)        │
                          │   Home · Documents · Memory  │
                          │   AI Chat · Profile          │
                          └──────────────┬──────────────┘
                                         │ HTTPS / JWT bearer (/api/v1/...)
                          ┌──────────────▼──────────────┐
                          │   backend   (FastAPI)        │
                          │  routes → service → models   │
                          │  ┌────────────────────────┐  │
                          │  │ Permission Service     │  │ ◀── permission before retrieval
                          │  └────────────────────────┘  │
                          └───┬─────────┬─────────┬──────┘
                              │         │         │
              ┌───────────────▼─┐  ┌────▼──────┐  ┌▼──────────────────┐
              │ PostgreSQL +    │  │ Storage   │  │ Background Job     │
              │ pgvector        │  │ Service   │  │ Queue (workers)    │
              │ (source of      │  │ (local FS │  │ extract·OCR·       │
              │  truth + vector │  │  first →  │  │ summary·embed      │
              │  index)         │  │  MinIO)   │  └───┬───────────────┘
              └─────────────────┘  └───────────┘     │
                              ▲                       │
                              │                       ▼
                              │              ┌────────────────────┐
                              └──────────────│ Local LLM runtime  │
                                  retrieval  │ (Ollama)           │ ◀── no external AI by default
                                  + answer   └────────────────────┘
```

ทุกบริษัทรัน stack นี้ใน environment ของตัวเอง (server / mini server / notebook) — **local-first / on-premise per company**

---

## 3. Database & RAG Direction

เลือกใช้ **PostgreSQL + pgvector** (ไม่ใช้ dual store แยก Chroma)

PostgreSQL เป็นทั้ง **source of truth** และ **vector search layer**

เหตุผล:

```text
- ลดจำนวน service ที่ต้องติดตั้งในบริษัทลูกค้า
- เหมาะกับ local/on-prem deployment
- backup ง่ายกว่าแยก PostgreSQL + ChromaDB
- permission/filter ผูกกับข้อมูลจริงใน database ได้ชัดกว่า
- ลดความสับสนเรื่อง dual vector store
```

กฎหลัก:

```text
PostgreSQL is source of truth.
pgvector is retrieval index, not permission authority.
Permission must be resolved before vector search.
Returned sources must be rechecked before being sent to AI.
```

RAG-ready concepts ที่ต้องมีตั้งแต่ต้น → ดูตารางเต็มใน [DATA_MODEL.md](DATA_MODEL.md)

---

## 4. Permission-Aware RAG Flow (7 steps)

ทุกครั้งที่ AI ตอบจากข้อมูลบริษัท:

```text
1. Resolve user permission
2. Determine allowed departments / collections
3. Query only allowed memory chunks (pgvector)
4. Recheck returned sources against permission
5. Send allowed context to local LLM (Ollama)
6. Return answer with source citations
7. Log retrieval (ai_retrieval_logs)
```

```text
employee query AI ในแผนก finance
  allowed collections = shared_knowledge + memory_finance
  ห้ามเห็น memory_farm, memory_legal, memory_marketing
```

---

## 5. File Storage

Phase 1: **Local filesystem first + StorageService abstraction**

ไฟล์จริงเก็บใน server/local machine ของบริษัท แต่ code ต้องผ่าน `StorageService` เสมอ เพื่ออนาคตเปลี่ยนเป็น MinIO / S3-compatible ได้

StorageService responsibilities:

```text
- save original file
- generate storage path
- calculate checksum
- read file for preview/extraction
- delete/soft-delete file when allowed
- support future MinIO/S3-compatible backend
```

> ⚠️ Lesson from old project: path เก็บไฟล์ (`uploads/`) **ต้อง gitignore** — เคยมี runtime PDF ที่มีข้อมูลธุรกิจ sensitive หลุดเข้า working tree

---

## 6. Background Jobs

งานหนักต้องใช้ **background queue ตั้งแต่แรก** ห้ามผูกไว้ใน request/response โดยตรง

ใช้กับ:

```text
text extraction · OCR · file preview generation · document summary ·
table summary · embedding · AI post-processing · re-embedding failed memory
```

Requirement:

```text
- Upload request should not block until all processing is finished
- System should create a job record
- User should see processing status
- Failed jobs must be visible and retryable
- Job status ต้องเก็บใน database (durable — ไม่ใช่ in-memory BackgroundTasks ที่หายเมื่อ restart)
```

Implementation เลือกได้ภายหลัง (local worker, Redis/RQ, Celery, หรือ simple DB-backed queue) แต่ architecture ต้องแยกงานหนักออกจาก request เสมอ

---

## 7. AI Runtime

```text
- AI core ใช้ local model ผ่าน Ollama (หรือ local runtime อื่นในอนาคต)
- model เปลี่ยนได้ตาม hardware ของแต่ละบริษัท (config ก่อน, Admin UI ทีหลัง)
- demo phase ใช้ model เบาเพื่อให้รันได้จริง
- External AI APIs ไม่ใช่ default path และห้ามใช้กับข้อมูลภายในบริษัทโดยไม่ได้รับอนุญาตชัดเจน
- System should work over LAN when internet is unavailable
```

---

## 8. Deployment Direction

```text
- local-first / on-premise per company
- แต่ละบริษัทมี instance แยก: company server / mini server / local workstation / notebook
- ข้อมูลของแต่ละบริษัทอยู่ใน environment ของบริษัทนั้นเอง
- Phase 1 ไม่ใช่ multi-tenant SaaS (ไม่ใช้ shared backend/database ข้ามบริษัท)
- infra/ เก็บ docker-compose (postgres = pgvector/pgvector:pg16), env examples, optional Ollama overlay
```

---

## 9. Non-Negotiable Architecture Rules

```text
- No AI retrieval without permission filter
- No Work Memory without human approval
- No sensitive company data to external AI by default
- No finance posting by LLM
- No hidden cross-department access
- No vector store acting as permission authority
- No route-level business logic overload
- No heavy work inside request/response
```

> รายละเอียด decision เบื้องหลัง → [DECISIONS.md](DECISIONS.md)
