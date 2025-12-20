---
id: 0002
title: FastAPI Docusaurus Integration Plan
stage: plan
date: 2025-12-11
surface: agent
model: claude-sonnet-4-5
feature: 004-fastapi-docusaurus-integration
branch: 004-fastapi-docusaurus-integration
user: junaidkh84
command: /sp.plan
labels: ["planning", "architecture", "fastapi", "docusaurus", "rag", "chatbot", "integration"]
links:
  spec: /specs/004-fastapi-docusaurus-integration/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - specs/004-fastapi-docusaurus-integration/plan.md
 - specs/004-fastapi-docusaurus-integration/research.md
 - specs/004-fastapi-docusaurus-integration/data-model.md
 - specs/004-fastapi-docusaurus-integration/quickstart.md
 - specs/004-fastapi-docusaurus-integration/contracts/chatbot-api.openapi.yaml
tests:
 - No tests created (planning phase only)
---

## Prompt

```text
Spec-1 Execution Plan: URL Ingestion → Text Extraction → Embedding → Qdrant Storage

Modules:
1. URL Loader Module
   - Input: Base site URL or sitemap.xml
   - Output: List of resolved page URLs
   - Implement URL validation, deduplication, and content-fetching
   - Use static HTML extraction since Docusaurus outputs pre-rendered pages

2. Text Extraction & Chunking Module
   - Parse HTML → extract main content blocks only
   - Clean markdown artifacts, code blocks, and non-semantic sections
   - Chunk text using configurable size (e.g., 512–1024 tokens) with overlap
   - Produce structured payload: {url, chunk_id, chunk_text, metadata}

3. Embedding Generator Module (Cohere)
   - Load model via Cohere Embeddings API
   - Batch embeddings to optimize rate limits
   - Output: vector list + metadata references

4. Qdrant Storage Module
   - Connect to Qdrant Cloud (API key + URL)
   - Create or update collection with defined schema
   - Insert vectors + metadata + payload
   - Validate insertions via random sampling and vector count checks

5. Validation & Logging
   - Generate ingestion summary report: total URLs, total chunks, embedding count
   - Create test query against Qdrant to verify vector similarity behavior

Deliverables:
- Fully automated ingestion/embedding pipeline (Python preferred, Node acceptable)
- Collection schema, config files, and reproducible scripts
- Execution logs and validation summary

Dependencies:
- Cohere API, Qdrant Cloud, site deployed on GitHub Pages
```

## Response snapshot

**Planning Workflow Completed Successfully**

I executed the complete `/sp.plan` workflow for Feature 004 (FastAPI RAG Backend with Docusaurus Frontend Integration):

**Phase 0: Research & Design Decisions**
- Created `research.md` with comprehensive technology stack decisions
- Resolved all "NEEDS CLARIFICATION" items from Technical Context
- Key decisions: EventSource API for SSE streaming, React Context for state management, Fetch API for HTTP, native Selection API for text selection, CSS media queries for responsive design

**Phase 1: Design & Contracts**
- Generated `data-model.md` defining 7 core entities: Message, Citation, ChatbotState, APIRequest, APIResponse, StreamChunk, APIConfiguration
- Created `contracts/chatbot-api.openapi.yaml` with complete OpenAPI 3.0 specification for all endpoints (/ask, /retrieve, /health, /metadata)
- Wrote `quickstart.md` with detailed local development setup instructions, troubleshooting guide, and environment configuration

**Key Architectural Decisions**:
1. **Component Integration**: Using Docusaurus Root.tsx theme swizzling for global chatbot availability
2. **Streaming**: EventSource API for SSE with fallback to standard POST
3. **CORS**: FastAPI middleware with whitelist approach (localhost + GitHub Pages)
4. **Configuration**: Multi-tier config strategy (runtime JSON → build-time → hardcoded defaults)
5. **State Management**: React Context + useReducer (no Redux needed)
6. **Mobile UX**: Bottom sheet for mobile, floating widget for desktop

**Deliverables Created**:
- `plan.md`: Updated with Technical Context, Constitution Check, Project Structure, Complexity Tracking
- `research.md`: 8 research areas with decisions, rationale, alternatives, implementation approaches
- `data-model.md`: 7 entities with complete schemas, validation rules, state transitions, examples
- `contracts/chatbot-api.openapi.yaml`: OpenAPI 3.0 spec with 4 endpoints, comprehensive examples
- `quickstart.md`: Complete development setup guide with prerequisites, step-by-step instructions, troubleshooting

**Constitution Compliance**: ✅ All checks passed, no complexity violations detected

**Next Steps**: Phase 2 (`/sp.tasks`) to generate actionable, dependency-ordered tasks.md

## Outcome

- ✅ Impact: Complete implementation plan ready with research, data models, API contracts, and development setup
- 🧪 Tests: No tests created (planning phase only; integration tests will be defined in Phase 2)
- 📁 Files: 5 files created/modified (plan.md, research.md, data-model.md, quickstart.md, chatbot-api.openapi.yaml)
- 🔁 Next prompts: Run `/sp.tasks` to generate testable implementation tasks; Review plan artifacts before proceeding
- 🧠 Reflection: The plan successfully bridges Spec-3 (FastAPI backend) with Docusaurus frontend using minimal, focused components. All technical unknowns resolved through research phase.

## Evaluation notes (flywheel)

- Failure modes observed: None; all planning phases completed successfully
- Graders run and results (PASS/FAIL): Constitution Check: PASS, Technical Context: PASS, Research completeness: PASS
- Prompt variant (if applicable): Standard /sp.plan command with multi-module user input
- Next experiment (smallest change to try): Implement first component (ChatWidget skeleton) to validate React Context setup and theme integration approach
