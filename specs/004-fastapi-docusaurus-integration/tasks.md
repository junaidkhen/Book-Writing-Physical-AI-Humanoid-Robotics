# Tasks: FastAPI RAG Backend with Docusaurus Frontend Integration

**Input**: Design documents from `/specs/004-fastapi-docusaurus-integration/`
**Prerequisites**: plan.md (✅), spec.md (✅), research.md (✅), data-model.md (✅), contracts/ (✅)

**Tests**: No tests explicitly requested in spec - tasks focus on implementation only

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4, US5)
- Include exact file paths in descriptions

## Path Conventions

This is a web application with:
- **Backend**: `backend/src/` (FastAPI - existing from Spec-3, minor CORS modifications)
- **Frontend**: `docs/src/` (Docusaurus - new chatbot components)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for chatbot integration

- [X] T001 Verify backend structure exists at backend/src/ with main.py, routers/, services/
- [X] T002 Verify Docusaurus structure exists at docs/src/ with components/, theme/ directories
- [X] T003 [P] Create docs/src/components/RAGChatbot/ directory for chatbot components
- [X] T004 [P] Create docs/src/utils/ directory for API client utilities
- [X] T005 [P] Create docs/static/config/ directory for runtime configuration

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Configure CORS middleware in backend/src/main.py with localhost:3000 and production origins
- [X] T007 [P] Create API configuration types in docs/src/utils/types.ts (APIConfiguration, APIRequest, APIResponse)
- [X] T008 [P] Create data model types in docs/src/utils/types.ts (Message, Citation, ChatbotState, StreamChunk)
- [X] T009 Create API client utility in docs/src/utils/apiClient.ts with fetch and EventSource wrappers
- [X] T010 Create docs/static/config/api-config.json for environment-specific API URLs
- [X] T011 Update docs/docusaurus.config.js to add customFields.apiBaseUrl configuration
- [X] T012 [P] Create base error handling utilities in docs/src/utils/errorHandler.ts
- [X] T013 [P] Create validation utilities in docs/src/utils/validators.ts for query length, context truncation

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Basic RAG Query Flow (Priority: P1) 🎯 MVP

**Goal**: Enable readers to ask questions and receive AI-generated answers with source citations

**Independent Test**: Open any book page, type "What is reinforcement learning?" into the chatbot, click submit, verify grounded response appears with book chapter references

### Implementation for User Story 1

- [X] T014 [P] [US1] Create ChatMessage component in docs/src/components/RAGChatbot/ChatMessage.tsx for displaying messages
- [X] T015 [P] [US1] Create CitationList component in docs/src/components/RAGChatbot/CitationList.tsx for displaying source references
- [X] T016 [P] [US1] Create ChatInput component in docs/src/components/RAGChatbot/ChatInput.tsx for query input field
- [X] T017 [US1] Create ChatbotWidget component in docs/src/components/RAGChatbot/ChatbotWidget.tsx integrating input, messages, and citations
- [X] T018 [US1] Create React Context in docs/src/components/RAGChatbot/ChatbotContext.tsx for state management (isOpen, messages, isLoading, error)
- [X] T019 [US1] Implement query submission logic in ChatbotWidget.tsx connecting to apiClient.ts
- [X] T020 [US1] Implement response display logic with message rendering and citation formatting
- [X] T021 [US1] Add loading indicator component in docs/src/components/RAGChatbot/LoadingIndicator.tsx
- [X] T022 [US1] Add error display component in docs/src/components/RAGChatbot/ErrorMessage.tsx with user-friendly messages
- [X] T023 [US1] Create CSS module docs/src/components/RAGChatbot/ChatbotWidget.module.css for widget styling
- [X] T024 [US1] Swizzle Root component in docs/src/theme/Root.tsx to wrap site with ChatbotContext provider
- [X] T025 [US1] Integrate ChatbotWidget into Root.tsx as global floating component
- [X] T026 [US1] Implement citation click handler to navigate to textbook sections
- [X] T027 [US1] Add validation for empty queries and length limits in ChatInput.tsx
- [X] T028 [US1] Test backend connectivity from frontend with sample queries

**Checkpoint**: At this point, User Story 1 should be fully functional - users can submit queries and receive responses with citations

---

## Phase 4: User Story 5 - Production Deployment (Priority: P1)

**Goal**: Enable production deployment with HTTPS and GitHub Pages compatibility

**Independent Test**: Deploy Docusaurus to GitHub Pages, verify chatbot connects to production API over HTTPS, confirm queries work end-to-end

**Note**: Prioritized as P1 because it's essential for production use, grouped with US1 for MVP

### Implementation for User Story 5

- [X] T029 [P] [US5] Add environment detection logic in docs/src/utils/apiClient.ts to switch between local and production URLs
- [X] T030 [P] [US5] Configure production API URL in docs/static/config/api-config.json
- [X] T031 [US5] Update backend/src/main.py CORS configuration to include GitHub Pages domain
- [X] T032 [US5] Add HTTPS validation in apiClient.ts to ensure secure connections in production
- [X] T033 [US5] Create production build script in docs/package.json with API_BASE_URL environment variable support
- [X] T034 [US5] Document deployment steps in specs/004-fastapi-docusaurus-integration/quickstart.md deployment section
- [X] T035 [US5] Test production build locally using npm run serve
- [X] T036 [US5] Validate CORS headers work for cross-origin requests from GitHub Pages domain

**Checkpoint**: Production deployment configuration complete - ready for live deployment

---

## Phase 5: User Story 2 - Context-Enhanced Query with Selected Text (Priority: P2)

**Goal**: Allow readers to highlight text and submit it as contextual input to the chatbot

**Independent Test**: Highlight a paragraph, click "Ask AI", type a follow-up question, verify response references the selected text

### Implementation for User Story 2

- [X] T037 [P] [US2] Create TextSelectionProvider component in docs/src/components/TextSelectionContext/TextSelectionProvider.tsx using window.getSelection()
- [X] T038 [US2] Add text selection event listeners in TextSelectionProvider.tsx for mouseup events
- [X] T039 [US2] Create floating "Ask AI" button component in docs/src/components/TextSelectionContext/AskAIButton.tsx
- [X] T040 [US2] Position AskAIButton near text selection using absolute positioning
- [X] T041 [US2] Add selectedContext field to ChatbotState in ChatbotContext.tsx
- [X] T042 [US2] Implement context injection in ChatInput.tsx to pre-populate with selected text
- [X] T043 [US2] Update API request in ChatbotWidget.tsx to include context field from APIRequest schema
- [X] T044 [US2] Add context truncation logic in validators.ts for max 5000 characters
- [X] T045 [US2] Display selected context in chat UI with visual indicator showing it's included
- [X] T046 [US2] Add "Clear context" button to remove pre-populated text
- [X] T047 [US2] Create CSS module docs/src/components/TextSelectionContext/AskAIButton.module.css for button styling
- [X] T048 [US2] Integrate TextSelectionProvider into Root.tsx wrapper
- [ ] T049 [US2] Test text selection on various page elements (paragraphs, code blocks, lists)

**Checkpoint**: Context-enhanced queries working - users can select text and ask targeted questions

---

## Phase 6: User Story 3 - Streaming Response Display (Priority: P3)

**Goal**: Display responses incrementally as they are generated using Server-Sent Events

**Independent Test**: Submit a query requiring a lengthy response, observe text appears incrementally rather than all at once

### Implementation for User Story 3

- [X] T050 [P] [US3] Implement SSE connection handler in docs/src/utils/apiClient.ts using EventSource API
- [X] T051 [US3] Add streaming endpoint support to backend/src/routers/chat.py with StreamingResponse
- [X] T052 [US3] Create stream chunk parser in apiClient.ts for content, citation, done, error event types
- [X] T053 [US3] Update ChatbotWidget.tsx to handle incremental message updates from stream chunks
- [X] T054 [US3] Add streaming status indicator in ChatMessage.tsx to show "AI is typing..."
- [X] T055 [US3] Implement stream cancellation logic in ChatbotWidget.tsx using EventSource.close()
- [X] T056 [US3] Add error recovery for mid-stream failures preserving partial responses
- [X] T057 [US3] Update ChatbotState to include streaming status field
- [X] T058 [US3] Implement auto-scroll in message list during streaming
- [X] T059 [US3] Add request cancellation on new query submission to stop current stream
- [X] T060 [US3] Handle SSE fallback for browsers that don't support EventSource
- [ ] T061 [US3] Test streaming with various query complexities and network conditions

**Checkpoint**: Streaming responses working - users see progressive text display for better UX

---

## Phase 7: User Story 4 - Local Development Testing (Priority: P2)

**Goal**: Enable developers to run both services locally and test chatbot functionality

**Independent Test**: Follow local setup instructions, start both services on localhost, verify chatbot works with localhost URLs

### Implementation for User Story 4

- [X] T062 [P] [US4] Create comprehensive development setup guide in specs/004-fastapi-docusaurus-integration/quickstart.md (already exists, verify completeness)
- [X] T063 [P] [US4] Add localhost CORS configuration to backend/src/main.py for ports 3000, 3001
- [X] T064 [US4] Create .env.example file in backend/ with required environment variables documented
- [X] T065 [US4] Add development scripts to docs/package.json for easy local startup
- [X] T066 [US4] Create health check endpoint documentation in contracts/chatbot-api.openapi.yaml
- [X] T067 [US4] Add connection test utility in docs/src/utils/apiClient.ts to verify backend availability
- [X] T068 [US4] Display connection status indicator in ChatbotWidget when backend is unavailable
- [X] T069 [US4] Document troubleshooting steps in quickstart.md for common local development issues
- [X] T070 [US4] Create example queries document for testing various RAG scenarios
- [ ] T071 [US4] Test complete local development workflow following quickstart.md

**Checkpoint**: Local development fully functional - developers can test changes without production dependencies

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [X] T072 [P] Add mobile responsive styles in ChatbotWidget.module.css for bottom-sheet on mobile (<768px)
- [X] T073 [P] Implement desktop floating widget styles for screens >1024px
- [X] T074 [P] Add tablet responsive styles for 768px-1024px breakpoint
- [X] T075 [P] Add keyboard navigation support (Enter to submit, Esc to close)
- [X] T076 [P] Add ARIA labels and screen reader support for accessibility
- [X] T077 [P] Implement focus management for input field when chatbot opens
- [ ] T078 [P] Add conversation history session storage (optional enhancement)
- [X] T079 Code cleanup and remove console.log statements for production
- [X] T080 Add request timeout configuration (30 seconds default) in apiClient.ts
- [ ] T081 Add retry logic with exponential backoff for failed requests
- [ ] T082 [P] Performance optimization: lazy load chatbot components until first interaction
- [ ] T083 [P] Add analytics events for chatbot usage (open, query submit, citation click)
- [ ] T084 Security review: validate no secrets exposed in frontend code
- [ ] T085 Add rate limiting documentation for backend API
- [X] T086 [P] Create end-to-end testing checklist for 5+ full RAG query flows
- [ ] T087 Validate page load time impact (<500ms per success criteria)
- [ ] T088 Test on multiple browsers (Chrome, Firefox, Safari, Edge)
- [ ] T089 Test on multiple devices (desktop, tablet, mobile)
- [ ] T090 Run complete quickstart.md validation from fresh clone

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 + 5 (Phase 3-4)**: Depends on Foundational - Forms MVP
  - US1: Basic query flow
  - US5: Production deployment (grouped with US1 for MVP)
- **User Story 2 (Phase 5)**: Depends on Foundational, integrates with US1
- **User Story 3 (Phase 6)**: Depends on Foundational, enhances US1
- **User Story 4 (Phase 7)**: Depends on Foundational, supports development workflow
- **Polish (Phase 8)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: MVP - Can start after Foundational (Phase 2) - No dependencies
- **User Story 5 (P1)**: MVP - Can start after Foundational (Phase 2) - Works with US1 for production
- **User Story 2 (P2)**: Integrates with US1 (requires ChatbotContext and ChatInput) but independently testable
- **User Story 3 (P3)**: Enhances US1 (requires apiClient and ChatbotWidget) but independently testable
- **User Story 4 (P2)**: Independent - Supports development workflow, no runtime dependencies

### Within Each User Story

- **US1**: Components [P] before integration → Widget assembly → Theme integration → Testing
- **US2**: Provider and button [P] before context injection → Integration with ChatbotWidget
- **US3**: SSE client [P] before streaming handler → Integration with ChatbotWidget
- **US4**: Documentation and configuration tasks [P] → Validation
- **US5**: Environment configuration [P] before deployment testing

### Parallel Opportunities

**Setup Phase**:
- T003, T004, T005 can run in parallel (different directories)

**Foundational Phase**:
- T007, T008 can run in parallel (type definitions)
- T012, T013 can run in parallel (utility functions)

**User Story 1**:
- T014, T015, T016 can run in parallel (independent components)
- T021, T022 can run in parallel (UI helper components)

**User Story 2**:
- T037, T039 can run in parallel (TextSelection components)

**User Story 3**:
- T050, T051 can run in parallel (frontend SSE client and backend streaming)

**User Story 4**:
- T062, T063, T064 can run in parallel (documentation and configuration)
- T066, T067 can run in parallel (health check docs and client)

**User Story 5**:
- T029, T030 can run in parallel (environment detection and config)

**Polish Phase**:
- T072, T073, T074 can run in parallel (responsive styles)
- T075, T076, T077 can run in parallel (accessibility features)
- T078, T079, T080, T081 can run in parallel (enhancements)
- T082, T083, T084, T085 can run in parallel (optimizations)
- T086, T087 can run in parallel (testing)
- T088, T089 can run in parallel (browser/device testing)

**Different user stories can be worked on in parallel after Foundational phase completes**

---

## Parallel Example: User Story 1 Core Components

```bash
# Launch all base components for User Story 1 together:
Task T014: "Create ChatMessage component in docs/src/components/RAGChatbot/ChatMessage.tsx"
Task T015: "Create CitationList component in docs/src/components/RAGChatbot/CitationList.tsx"
Task T016: "Create ChatInput component in docs/src/components/RAGChatbot/ChatInput.tsx"

# Then assemble widget (depends on above):
Task T017: "Create ChatbotWidget component integrating input, messages, and citations"

# UI helpers in parallel:
Task T021: "Add loading indicator component in docs/src/components/RAGChatbot/LoadingIndicator.tsx"
Task T022: "Add error display component in docs/src/components/RAGChatbot/ErrorMessage.tsx"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 5)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T013) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T014-T028) - Basic query flow
4. Complete Phase 4: User Story 5 (T029-T036) - Production deployment
5. **STOP and VALIDATE**: Test end-to-end on localhost AND production
6. Deploy MVP to production

**MVP Delivers**: Readers can ask questions and get grounded answers with citations, deployed on GitHub Pages

### Incremental Delivery

1. MVP (US1 + US5) → Deploy → Users can ask basic questions
2. Add US2 (Context) → Deploy → Users can ask about selected text
3. Add US3 (Streaming) → Deploy → Better UX with progressive responses
4. Add US4 (Local Dev) → No deploy needed → Better developer experience
5. Polish → Deploy → Production-ready with full accessibility and performance

### Parallel Team Strategy

With multiple developers after Foundational phase (T006-T013):

**MVP Track** (Priority 1):
- Developer A: US1 frontend components (T014-T028)
- Developer B: US5 deployment config (T029-T036)

**Enhancement Track** (Priority 2):
- Developer C: US2 text selection (T037-T049)
- Developer D: US4 local dev setup (T062-T071)

**Advanced Track** (Priority 3):
- Developer E: US3 streaming (T050-T061)

All tracks can work in parallel after Foundational phase complete

---

## Summary

- **Total Tasks**: 90
- **MVP Tasks (US1 + US5)**: 23 (T014-T036)
- **Enhancement Tasks (US2 + US4)**: 26 (T037-T049, T062-T071)
- **Advanced Tasks (US3)**: 12 (T050-T061)
- **Setup + Foundation**: 13 (T001-T013)
- **Polish**: 19 (T072-T090)

**Parallel Opportunities**: 39 tasks marked [P] can run in parallel within their phases

**Independent Test Criteria**:
- US1: Can query and receive responses with citations
- US2: Can select text and include as context
- US3: Responses stream progressively
- US4: Local development works per quickstart.md
- US5: Production deployment works on GitHub Pages

**MVP Scope**: Complete Phase 1, 2, 3, 4 for fully functional production chatbot (T001-T036)

---

## Notes

- [P] tasks = different files, no dependencies within same phase
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- No test tasks included (not requested in spec)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All file paths assume web app structure: backend/src/ and docs/src/
