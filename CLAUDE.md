# CLAUDE.md

This file provides guidance to Claude Code when working in this repository.

## Project Overview

This project is a Local/Internal AI Workspace for SME organizations. The system is designed to help departments preserve work knowledge, manage documents, search internal memory, and reduce repetitive operational work.

The product is not a generic chatbot. It is an internal workspace where users interact with AI through department-scoped workflows such as finance records, document OCR, permission-aware RAG search, handover memory, and internal knowledge retrieval.

The system should prioritize privacy, maintainability, and clear boundaries between departments. Core data, documents, vector memory, database, and local AI services are intended to run inside the organization’s environment.

## Core Principles

Work in small, safe, reviewable changes. Do not rewrite large parts of the system unless explicitly requested.

Prefer simple, direct implementation over abstraction. Avoid creating frameworks, generic engines, or unnecessary layers before the project actually needs them.

Respect the existing project structure. Do not move files, rename folders, or introduce new architectural patterns without checking the current repo layout first.

Do not implement future phases fully unless requested. For later departments or future modules, create only minimal placeholders when needed.

Permission and department scope are mandatory. Any feature that reads documents, records, memory, finance data, or user content must respect role-based access and department boundaries.

Local/Internal mode is a product constraint. Do not add external AI APIs, cloud storage, telemetry, or third-party processing unless explicitly requested.

## Repository Structure

Expected high-level structure:

```text
.
├── apps/
│   ├── web/                  # Frontend application
│   └── api/                  # Backend API service
├── infra/                    # Docker, database, Ollama, deployment config
├── docs/                     # Project documentation and source-of-truth specs
├── scripts/                  # Developer automation scripts
├── data/                     # Local development data only
├── private/                  # Sensitive local-only files, never commit
├── .gitignore
├── README.md
└── CLAUDE.md
```

Do not add generated folders to git, including `node_modules`, `.venv`, `__pycache__`, `.next`, `dist`, `build`, coverage output, or temporary files.

## Main Tech Stack

Frontend:

* Next.js
* React
* TypeScript
* Tailwind CSS or existing styling system
* Domain-based API clients under `lib/api`

Backend:

* FastAPI
* Python
* SQLAlchemy
* PostgreSQL
* pgvector
* JWT authentication
* Role-based and department-based permission control

AI and RAG:

* Ollama for local model serving
* pgvector for vector search
* Permission-aware retrieval
* Document ingestion, chunking, embedding, and search logs

Infrastructure:

* Docker Compose
* PostgreSQL
* Ollama
* Local development environment via `.env`

## Source of Truth

Before making changes, check these files when they exist:

```text
docs/PROJECT_MAP.md
docs/ROADMAP.md
docs/ACCEPTANCE_CRITERIA.md
docs/ARCHITECTURE.md
docs/API.md
README.md
```

If documentation conflicts with implemented code, inspect the code before changing anything. Do not assume the docs are always current.

When a change affects architecture, folder structure, API behavior, permission logic, or developer workflow, update the relevant docs in the same task.

## Backend Guidelines

Backend code should be organized by clear responsibility:

```text
apps/api/
├── main.py                   # FastAPI app and router registration
├── core/                     # Settings, config, security, shared constants
├── db/                       # Database session, migrations, base models
├── auth/                     # Authentication and current-user logic
├── models/                   # SQLAlchemy models
├── schemas/                  # Pydantic request/response schemas
├── routes/                   # FastAPI route handlers
├── services/                 # Business logic
├── repositories/             # Database query logic when needed
├── permissions/              # RBAC and department-scope checks
├── rag/                      # RAG, retrieval, embedding, chunk search
├── documents/                # Upload, OCR, ingestion, document lifecycle
├── finance/                  # Finance workspace domain
└── tests/                    # Backend tests
```

Route handlers should stay thin. Put business logic in services. Put reusable database access in repositories only when it reduces duplication.

Do not bypass permission checks. Any query involving user data must be scoped by user role, department, or explicit permission rule.

Do not use raw SQL unless necessary. Prefer SQLAlchemy query builders and bound parameters.

Do not introduce global state for request-specific data.

## Frontend Guidelines

Frontend code should be organized by feature and shared UI responsibility:

```text
apps/web/
├── app/                      # Next.js app routes
├── components/               # Shared UI components
│   ├── ui/                   # Generic UI primitives
│   └── layout/               # App shell, sidebar, navbar
├── features/                 # Domain-specific frontend features
│   ├── finance/
│   ├── documents/
│   ├── rag/
│   ├── auth/
│   └── dashboard/
├── lib/
│   ├── api/                  # API clients by domain
│   └── utils/                # Shared helpers
├── hooks/                    # Reusable React hooks
├── types/                    # Shared TypeScript types
├── styles/                   # Global styles
└── tests/                    # Frontend tests
```

Keep API calls out of UI components when possible. Use `lib/api` for backend communication and keep feature components focused on rendering and interaction.

Do not create large global state unless the data is actually shared across unrelated pages. Prefer local state, server state, or small hooks before adding complex state management.

Use existing components and styling conventions before creating new ones.

## Permission and RBAC Rules

Permission is part of the product, not an optional security layer.

Every protected backend feature must answer these questions:

* Who is the current user?
* What role does the user have?
* Which department does the user belong to?
* Is this action allowed for this role and department?
* Does the database query enforce the same boundary?

Never rely only on frontend hiding. The backend must enforce access control.

Finance data, uploaded documents, OCR results, RAG chunks, embeddings, and workspace summaries must not leak across departments.

## RAG and Document Rules

RAG must be permission-aware.

A user should only retrieve chunks from documents they are allowed to access. Search quality must never override access control.

Document flow should follow a clear lifecycle:

```text
upload → extract → chunk → embed → index → permission-aware search
```

Do not store embeddings or chunks without a link back to the source document and permission scope.

When adding RAG features, include tests for:

* normal retrieval
* no-result behavior
* cross-department isolation
* unauthorized access
* disabled feature flags when applicable

## Finance Workspace Rules

Finance is the current MVP focus.

Finance features may include:

* income and expense records
* OCR receipt review
* transaction type
* vendor/category filters
* dashboard summary
* document linkage
* approval or review flow

Finance records must always be department-scoped.

Do not mix finance logic into generic document or RAG logic unless it is truly reusable.

## API Rules

Prefer RESTful endpoints with clear domain boundaries.

Use predictable route grouping:

```text
/auth
/users
/departments
/finance
/documents
/rag
/permissions
/dashboard
/admin
```

Use Pydantic schemas for request and response bodies.

Return clear error messages, but do not expose internal stack traces, filesystem paths, secrets, or private configuration.

## Testing Rules

Add or update tests when changing behavior.

Backend tests should cover:

* route behavior
* service behavior
* permission boundaries
* tenant or department isolation
* error cases

Frontend tests should cover:

* important UI states
* form behavior
* API integration boundaries
* permission-based rendering where relevant

Before claiming a task is complete, run the smallest relevant validation command. If unsure, run the broader project validation.

Common validation commands may include:

```bash
# Backend
pytest

# Frontend
npm run lint
npm run typecheck
npm run test
npm run build

# Docker
docker compose -f infra/docker-compose.yml config
```

If commands differ in the actual repo, inspect `package.json`, `pyproject.toml`, `Makefile`, or project docs before running.

## Documentation Rules

Update documentation when changing:

* folder structure
* API routes
* environment variables
* database schema
* Docker setup
* permission behavior
* RAG flow
* user workflow
* roadmap status

Do not leave outdated documentation that contradicts the code.

If a document is obsolete, mark it clearly or remove it when requested.

## Git and Change Safety

Before editing, inspect the current files.

Do not assume paths exist.

Do not delete files unless the user explicitly asks or the file is clearly generated/cache output.

Keep commits focused by task. Do not mix unrelated refactors, formatting, feature work, and documentation cleanup in one change.

Before finishing, summarize:

* files changed
* behavior changed
* tests or validations run
* risks or follow-up work

## Environment and Secrets

Never commit secrets.

Files that should stay local:

* `.env`
* `.env.local`
* private documents
* company data
* local database dumps
* API keys
* model files
* generated OCR files containing real business data

Use `.env.example` for safe placeholder configuration.

## Do Not Do

Do not add external SaaS AI dependencies unless explicitly requested.

Do not bypass RBAC or department checks.

Do not create duplicated folders like `src/src`, repeated `api/api`, or parallel structures that confuse ownership.

Do not add new architecture documents that duplicate existing docs.

Do not create generic abstractions before at least two real use cases exist.

Do not rewrite working code just to match personal style.

Do not silently change public API behavior.

Do not commit generated files or local private data.

## Working Style for Claude Code

For each task:

1. Read the relevant docs and files first.
2. Identify the smallest safe change.
3. Make the change.
4. Run relevant validation.
5. Update docs if needed.
6. Report clearly what changed and what remains.

When uncertain, ask before making irreversible changes.

When the user requests a plan, produce a bounded plan with clear tasks and stopping point.

When the user requests implementation, implement only the requested scope.

## Current Product Priority

The project should prioritize a clean MVP over broad unfinished features.

Priority order:

1. Stable authentication and permission boundaries
2. Finance workspace MVP
3. Document OCR and review flow
4. Permission-aware RAG
5. Workspace dashboard
6. Department expansion as later phases
7. Admin and advanced automation after core flows are stable

The goal is not to build every possible feature. The goal is to make the core workflow reliable, understandable, and easy to continue.
