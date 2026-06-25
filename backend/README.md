# backend — Backend (FastAPI + Python 3.12)

Modular monolith แบ่งตาม bounded context. `app/core` `app/db` `app/shared` = infra กลาง ·
`app/rag` `app/jobs` `app/storage` = cross-cutting services · `app/modules/<name>` = domain
(แต่ละ module มี router/service/repository/models/schemas/permissions/tests).
ดู [PROJECT_MAP.md](../docs/PROJECT_MAP.md) · [ARCHITECTURE.md](../docs/ARCHITECTURE.md).
