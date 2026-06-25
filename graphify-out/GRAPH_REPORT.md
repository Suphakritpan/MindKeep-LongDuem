# Graph Report - .  (2026-06-25)

## Corpus Check
- Corpus is ~15,335 words - fits in a single context window. You may not need a graph.

## Summary
- 94 nodes · 118 edges · 30 communities (10 shown, 20 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 6 edges (avg confidence: 0.84)
- Token cost: 100,000 input · 8,546 output

## Community Hubs (Navigation)
- [[_COMMUNITY_Old LongRian Reference & Migration|Old LongRian Reference & Migration]]
- [[_COMMUNITY_Privacy & Permission-Aware RAG|Privacy & Permission-Aware RAG]]
- [[_COMMUNITY_Work Memory Core (pgvector)|Work Memory Core (pgvector)]]
- [[_COMMUNITY_Documents & Review Flow|Documents & Review Flow]]
- [[_COMMUNITY_Finance & Background Jobs|Finance & Background Jobs]]
- [[_COMMUNITY_Field & Production Mobile|Field & Production Mobile]]
- [[_COMMUNITY_Audit & Owner Access|Audit & Owner Access]]
- [[_COMMUNITY_Handover  Continuity|Handover / Continuity]]
- [[_COMMUNITY_File Storage Layer|File Storage Layer]]
- [[_COMMUNITY_AI Module|AI Module]]
- [[_COMMUNITY_Auth Module|Auth Module]]
- [[_COMMUNITY_Chat Module|Chat Module]]
- [[_COMMUNITY_Memory Module|Memory Module]]
- [[_COMMUNITY_Audit Module|Audit Module]]
- [[_COMMUNITY_Admin Command Center|Admin Command Center]]
- [[_COMMUNITY_Public vs Shared Visibility|Public vs Shared Visibility]]
- [[_COMMUNITY_FastAPI Backend|FastAPI Backend]]
- [[_COMMUNITY_Next.js Frontend|Next.js Frontend]]
- [[_COMMUNITY_Private Visibility|Private Visibility]]
- [[_COMMUNITY_Department Visibility|Department Visibility]]
- [[_COMMUNITY_Restricted Visibility|Restricted Visibility]]
- [[_COMMUNITY_Users Module|Users Module]]
- [[_COMMUNITY_Departments Module|Departments Module]]
- [[_COMMUNITY_Permissions Module|Permissions Module]]
- [[_COMMUNITY_Files Module|Files Module]]
- [[_COMMUNITY_Department Workspace (Phase 4)|Department Workspace (Phase 4)]]
- [[_COMMUNITY_Full AI Chat (Phase 5)|Full AI Chat (Phase 5)]]
- [[_COMMUNITY_Departments Table|Departments Table]]
- [[_COMMUNITY_Chat Sessions Table|Chat Sessions Table]]

## God Nodes (most connected - your core abstractions)
1. `MindKeep (product)` - 7 edges
2. `Work Memory` - 7 edges
3. `Permission-Aware RAG` - 7 edges
4. `Finance Workspace Flow` - 6 edges
5. `LongRian Department Workspace Spec v1 (old)` - 5 edges
6. `MindKeep AI Workspace Core Spec v0.1` - 5 edges
7. `Old Project Problem Report` - 5 edges
8. `Review Before Memory` - 5 edges
9. `pgvector` - 5 edges
10. `Old Project Freeze Note` - 4 edges

## Surprising Connections (you probably didn't know these)
- `LongRian Department Workspace Spec v1 (old)` --semantically_similar_to--> `Finance Workspace Flow`  [INFERRED] [semantically similar]
  docs/product/LongRian_Department_Workspace_Spec_v1.md → docs/SYSTEM_SPEC.md
- `MindKeep AI Workspace Core Spec v0.1` --semantically_similar_to--> `Work Memory`  [INFERRED] [semantically similar]
  docs/product/MindKeep_AI_Workspace_Core_Spec_v0.1.md → docs/REQUIREMENTS.md
- `MindKeep (product)` --semantically_similar_to--> `LongRian (old repo / reference)`  [INFERRED] [semantically similar]
  docs/REQUIREMENTS.md → docs/DECISIONS.md
- `pgvector` --semantically_similar_to--> `ChromaDB (old vector store)`  [INFERRED] [semantically similar]
  docs/ARCHITECTURE.md → docs/reports/OLD_PROJECT_PROBLEM_REPORT.md
- `LongRian Department Workspace Spec v1 (old)` --references--> `Department Boundary by Default`  [EXTRACTED]
  docs/product/LongRian_Department_Workspace_Spec_v1.md → docs/ARCHITECTURE.md

## Hyperedges (group relationships)
- **Document Visibility Model (5 levels)** — visibility_private, visibility_department, visibility_public_internal, visibility_restricted, visibility_shared_knowledge [EXTRACTED 1.00]
- **Permission-Aware RAG Flow (7 steps)** — service_permission, concept_department_boundary, tech_pgvector, concept_permission_before_retrieval, tech_ollama, concept_source_citation, entity_ai_retrieval_logs [EXTRACTED 1.00]
- **Phase 1 Active Module Set** — module_auth, module_users, module_departments, module_permissions, module_documents, module_files, module_memory, module_ai, module_chat, module_audit [EXTRACTED 1.00]

## Communities (30 total, 20 thin omitted)

### Community 0 - "Old LongRian Reference & Migration"
Cohesion: 0.24
Nodes (10): Department Boundary by Default, LongRian API Spec (old), LongRian Department Workspace Spec v1 (old), MindKeep AI Workspace Core Spec v0.1, Old Project Freeze Note, Old Project Problem Report, Old Repo Drift / Fragmentation, LongRian (old repo / reference) (+2 more)

### Community 1 - "Privacy & Permission-Aware RAG"
Cohesion: 0.22
Nodes (11): Non-Negotiable Data Privacy Rule, Local-First / On-Premise, Permission-Aware RAG, Permission Before Retrieval, RAG (Retrieval-Augmented Generation), Source Citation, ai_retrieval_logs (table), permission_grants (table) (+3 more)

### Community 3 - "Work Memory Core (pgvector)"
Cohesion: 0.25
Nodes (8): Work Memory, /api/v1/documents, memory_chunks (table), memory_entries (table), documents module, Phase 1 — Document + Work Memory Core, pgvector, PostgreSQL

### Community 4 - "Documents & Review Flow"
Cohesion: 0.29
Nodes (7): Activity Timeline, Review Before Memory, documents (table), users (table), work_activities (table), department_lead, employee

### Community 5 - "Finance & Background Jobs"
Cohesion: 0.29
Nodes (7): Background Jobs (durable queue), Deterministic Finance Calculation (no LLM), Finance Workspace Flow, OCR / Bill Scanner, jobs (table), finance module, Phase 2 — Finance Workspace

### Community 6 - "Field & Production Mobile"
Cohesion: 0.67
Nodes (3): Field & Production Mobile Capture, field module, Phase 6 — Field & Production Mobile

### Community 7 - "Audit & Owner Access"
Cohesion: 0.67
Nodes (3): Audit Logs (sensitive actions), audit_logs (table), owner_manager

### Community 8 - "Handover / Continuity"
Cohesion: 0.67
Nodes (3): Handover / Continuity, handover module, Phase 3 — Handover / Continuity

### Community 9 - "File Storage Layer"
Cohesion: 0.67
Nodes (3): files (table), uploads/ must be gitignored (sensitive PDF leak), StorageService

## Knowledge Gaps
- **20 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Review Before Memory` connect `Documents & Review Flow` to `Canonical Spec Docs`, `Work Memory Core (pgvector)`?**
  _High betweenness centrality (0.078) - this node is a cross-community bridge._
- **Why does `Work Memory` connect `Work Memory Core (pgvector)` to `Old LongRian Reference & Migration`, `Privacy & Permission-Aware RAG`, `Documents & Review Flow`, `Finance & Background Jobs`?**
  _High betweenness centrality (0.065) - this node is a cross-community bridge._
- **Why does `Permission-Aware RAG` connect `Privacy & Permission-Aware RAG` to `Work Memory Core (pgvector)`?**
  _High betweenness centrality (0.051) - this node is a cross-community bridge._
- **What connects `Source Citation`, `Handover / Continuity`, `PostgreSQL` to the rest of the system?**
  _46 weakly-connected nodes found - possible documentation gaps or missing edges._