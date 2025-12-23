# Implementation Plan: FastAPI RAG Backend with Docusaurus Frontend Integration

**Branch**: `004-fastapi-docusaurus-integration` | **Date**: 2025-12-11 (Updated: 2025-12-17) | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-fastapi-docusaurus-integration/spec.md`
**Spec Clarifications**: Session 2025-12-17 (5 UX/API clarifications integrated - see VERIFICATION-2025-12-17.md)

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Connect the existing Docusaurus static site to a FastAPI RAG backend, enabling an embedded chatbot that queries the textbook content. The integration must support both local development (localhost) and production deployment (GitHub Pages → external API), with CORS configuration, streaming responses, and text-selection context mode.

## Technical Context

### Backend
**Language/Version**: Python 3.11+ (FastAPI requirement)
**Primary Dependencies**: FastAPI 0.100+, Uvicorn (ASGI server), fastapi-cors-middleware, python-dotenv
**Storage**: N/A (backend already has Qdrant vector DB from Specs 1-2, this feature only connects frontend)
**Testing**: pytest (backend integration tests), manual E2E testing
**Target Platform**: Linux/Docker server with HTTPS (production), localhost:8000 (development)

### Frontend
**Language/Version**: JavaScript/TypeScript, Node.js 20+ (Docusaurus 3.x requirement)
**Primary Dependencies**: React 19, Docusaurus 3.9.2, Fetch API/Axios for HTTP, EventSource for SSE
**Storage**: N/A (ephemeral session state in browser memory, no persistence)
**Testing**: Manual integration testing, browser DevTools validation
**Target Platform**: Static site on GitHub Pages (production), localhost:3000 (development)

**Project Type**: Web (frontend + backend integration)
**Performance Goals**: <10s response time for 95% of queries, <500ms chatbot UI load impact, smooth streaming display
**Constraints**: Static frontend (no SSR), CORS required, HTTPS in production, <100KB chatbot JS bundle
**Scale/Scope**: Single-page chatbot component, ~5-10 frontend files, 2-3 backend endpoint modifications for CORS

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Note**: The constitution file is a template without specific gates. Applying standard web integration principles:

| Gate | Status | Notes |
|------|--------|-------|
| Minimal Complexity | ✅ PASS | Single chatbot component, minimal backend changes (CORS only) |
| Clear Separation | ✅ PASS | Frontend static (Docusaurus), backend separate (FastAPI) |
| Testing Strategy | ✅ PASS | Manual E2E + browser validation sufficient for UI integration |
| Security | ⚠️ REVIEW | CORS must be restrictive (GitHub Pages domain + localhost only), HTTPS required in prod |
| Observability | ✅ PASS | Browser DevTools + backend logs provide visibility |

**No violations requiring justification.**

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
# Backend (NEW - to be created)
backend/
├── src/
│   ├── main.py              # FastAPI app entry point with CORS
│   ├── routers/
│   │   └── chat.py          # /ask endpoint (from Spec-3)
│   ├── services/
│   │   └── rag_agent.py     # RAG agent (from Spec-3)
│   └── config.py            # Environment config
├── .env                      # FRONTEND_API_URL, existing keys
├── requirements.txt
└── tests/
    └── test_cors.py         # CORS integration test

# Frontend (EXISTING - Docusaurus site in /docs)
docs/
├── src/
│   ├── components/
│   │   ├── ChatBot/
│   │   │   ├── ChatBot.tsx          # Main chatbot component (NEW)
│   │   │   ├── ChatMessage.tsx      # Message display (NEW)
│   │   │   ├── ChatInput.tsx        # Input field (NEW)
│   │   │   └── ChatBot.module.css   # Styling (NEW)
│   │   └── TextSelectionContext/
│   │       └── TextSelectionProvider.tsx  # Context capture (NEW)
│   ├── pages/                        # Existing pages
│   └── theme/
│       └── Root.tsx                  # Docusaurus theme wrapper (MODIFY)
├── docusaurus.config.js              # Add chatbot config (MODIFY)
├── package.json                       # Add dependencies (MODIFY)
└── .env.local                         # REACT_APP_API_URL (NEW)
```

**Structure Decision**: Web application with separate backend and frontend directories. Backend is new (Spec-3 dependency), frontend extends existing Docusaurus site in `/docs`. Changes are minimal and isolated to chatbot components.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations detected. No complexity justification required.

---

## Phase 0 Completion: Research

✅ **Status**: Complete
- **File**: [research.md](./research.md)
- **Key Decisions**:
  1. CORS: FastAPI CORSMiddleware with explicit origin allowlist
  2. Streaming: Server-Sent Events (SSE) via EventSource API
  3. Text Selection: window.getSelection() + React Context
  4. Environment Config: Build-time vars (Docusaurus) + runtime vars (FastAPI)
  5. Chatbot Embedding: Docusaurus Root swizzling
  6. Request Cancellation: AbortController with fetch API

All technical unknowns resolved. Research phase complete.

---

## Phase 1 Completion: Data Model & Contracts

✅ **Status**: Complete

### Generated Artifacts

1. **[data-model.md](./data-model.md)** - Frontend data structures
   - Message entity (user/assistant messages)
   - Citation entity (source references)
   - ChatbotState (UI state management)
   - APIRequest/APIResponse schemas

2. **[contracts/chatbot-api.openapi.yaml](./contracts/chatbot-api.openapi.yaml)** - API contract
   - POST /ask endpoint specification
   - SSE streaming format
   - Error response schemas
   - CORS headers documentation

3. **[quickstart.md](./quickstart.md)** - Development setup guide
   - Prerequisites and dependencies
   - Local development workflow
   - Environment configuration
   - Testing procedures

### Agent Context Update

✅ **Updated**: CLAUDE.md with current technologies
- Added: Python 3.11+, FastAPI, Docusaurus 3.9.2, React 19
- Added: Backend/Frontend separation pattern
- Updated: Active Technologies section

---

## Post-Phase 1 Constitution Re-evaluation

**Initial Evaluation**: 2025-12-11
**Re-verified**: 2025-12-17 (post-spec clarification)

| Gate | Status | Notes |
|------|--------|-------|
| Minimal Complexity | ✅ PASS | Design confirms single chatbot component, no additional complexity |
| Clear Separation | ✅ PASS | Contracts clearly define frontend/backend interface boundaries |
| Testing Strategy | ✅ PASS | Manual E2E sufficient for UI; backend CORS tests added |
| Security | ✅ PASS | CORS restricted to specific origins, no secrets in frontend |
| Observability | ✅ PASS | EventSource provides clear streaming visibility |

**Post-Design Evaluation**: All gates pass. No new risks introduced.
**Post-Clarification Evaluation**: All gates remain PASS. Clarifications refined parameters (2000-char context limit, 30s timeout, inline text selection button) without architectural changes. See VERIFICATION-2025-12-17.md for details.

---

## Next Steps

This command completes at Phase 1. To continue implementation:

1. **Generate Tasks**: Run `/sp.tasks` to create actionable task list from plan
2. **Implementation**: Execute tasks in dependency order (backend CORS → frontend components)
3. **Testing**: Follow quickstart.md for local testing workflow
4. **Deployment**: Configure production environment variables per quickstart.md

**Planning Phase Complete** ✅

**Branch**: `004-fastapi-docusaurus-integration`
**Plan Document**: `/mnt/e/Junaid/Book-Wr-Claude/specs/004-fastapi-docusaurus-integration/plan.md`
**Generated Artifacts**:
- ✅ research.md
- ✅ data-model.md
- ✅ quickstart.md
- ✅ contracts/chatbot-api.openapi.yaml
