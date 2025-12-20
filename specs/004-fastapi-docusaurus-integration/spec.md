# Feature Specification: FastAPI RAG Backend with Docusaurus Frontend Integration

**Feature Branch**: `004-fastapi-docusaurus-integration`
**Created**: 2025-12-11
**Status**: Draft
**Input**: User description: "Spec-4: Integrate FastAPI RAG Backend with Docusaurus Frontend

Objective:
Connect the existing Docusaurus website to the FastAPI + Agent backend, enabling a fully functional embedded chatbot on the book's frontend with local and production compatibility.

## Clarifications

### Session 2025-12-17

- Q: How should users activate the "Ask AI about this" feature after selecting text? → A: Inline button/tooltip appearing near selected text when text is highlighted (similar to Medium's inline comment feature)
- Q: Where should the chatbot interface be positioned on the page? → A: Bottom-right floating widget (circular/pill button that expands to chat panel when clicked)
- Q: What is the maximum character length for selected text context before truncation? → A: 2000 characters
- Q: What is the maximum timeout for API requests before showing a timeout error? → A: 30 seconds
- Q: What format does the FastAPI backend return for source citations in the API response? → A: Array of objects: `{url: string, title: string, excerpt: string}`

Success criteria:
- Frontend sends user queries to FastAPI Agent endpoint
- Retrieved + grounded Agent responses display in the Docusaurus UI
- User can select specific text on a page and submit it to the Agent as context
- CORS, routing, and error-handling configured for both local (localhost) and GitHub Pages production
- Chatbox UI supports streaming or incremental message updates
- Integration validated with at least five full RAG queries

Constraints:
- Frontend must remain static (GitHub Pages) with external API calls only
- No server-side rendering or dynamic node backend inside Docusaurus
- Must support HTTPS in production
- Only minimal, self-contained React components added to the Docusaurus theme
- No redesigning of entire site layout beyond the chatbot module

Not building:
- Ingestion, retrieval, or embedding logic (Specs 1 & 2)
- New backend models or agents (Spec-3 already defines them)
- Advanced analytics dashboard or conversation history storage
- Mobile application or standalone web app"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Basic RAG Query Flow (Priority: P1)

A reader visits the online textbook website, clicks the bottom-right floating chat button to open the chatbot panel, types a question about a specific chapter topic into the chatbot interface, and receives an AI-generated answer grounded in the book's content along with relevant source references.

**Why this priority**: This is the core value proposition - enabling readers to ask questions and get contextual answers from the book content. Without this, the feature has no utility.

**Independent Test**: Can be fully tested by opening any book page, clicking the floating chat button in the bottom-right corner, typing "What is reinforcement learning?" into the chatbot, clicking submit, and verifying that a grounded response appears with book chapter references. Delivers immediate value for readers seeking quick answers.

**Acceptance Scenarios**:

1. **Given** a reader is on any page of the Docusaurus site, **When** they click the bottom-right floating chat button, **Then** the chat panel expands to show the input interface
2. **Given** the chat panel is open, **When** they type a question into the chatbot input field and press Enter or click Submit, **Then** the question is sent to the FastAPI backend and a loading indicator appears
3. **Given** the backend has processed the query, **When** the response is returned, **Then** the chatbot displays the AI-generated answer with visible source citations from the textbook
4. **Given** a reader receives an answer, **When** they click on a source citation, **Then** they are navigated to the relevant section of the book
5. **Given** the backend is unavailable, **When** the reader submits a query, **Then** a friendly error message is displayed indicating the service is temporarily unavailable

---

### User Story 2 - Context-Enhanced Query with Selected Text (Priority: P2)

A reader highlights a specific paragraph or formula on a textbook page, sees an inline "Ask AI" button or tooltip appear near the selected text, clicks it to open the chatbot with the selected content pre-populated as context, and receives an answer specifically related to the selected content.

**Why this priority**: This significantly enhances the user experience by allowing targeted questions about specific content, but the basic query flow must work first.

**Independent Test**: Can be tested by highlighting any paragraph of text on a book page, clicking the inline "Ask AI" button that appears, typing a follow-up question like "Can you explain this in simpler terms?", and verifying the response references the selected text. Provides immediate value for readers struggling with specific passages.

**Acceptance Scenarios**:

1. **Given** a reader has selected text on a page, **When** the selection is made, **Then** an inline button/tooltip appears near the selected text offering to "Ask AI about this"
2. **Given** the inline "Ask AI" button is visible, **When** the reader clicks it, **Then** the chatbot opens with the selected text pre-populated as context
3. **Given** the chatbot has received selected text as context, **When** the reader types a question, **Then** the AI response specifically references and builds upon the selected text
4. **Given** a reader selects text exceeding 2000 characters, **When** they click "Ask AI", **Then** the context is truncated to 2000 characters and a notification message is displayed
5. **Given** no text is selected, **When** the reader clicks elsewhere, **Then** the inline "Ask AI" button disappears and the chatbot remains in normal mode
6. **Given** a reader deselects text without clicking the button, **When** the text selection is cleared, **Then** the inline "Ask AI" button automatically disappears

---

### User Story 3 - Streaming Response Display (Priority: P3)

A reader submits a complex query, and instead of waiting for the complete answer, they see the response appear word-by-word or in chunks as the AI generates it, similar to ChatGPT's streaming interface.

**Why this priority**: Improves perceived performance and user engagement, but is not essential for core functionality. The feature works without streaming, just with longer wait times.

**Independent Test**: Can be tested by submitting a query that requires a lengthy response, then observing that text appears incrementally rather than all at once. Delivers enhanced UX but doesn't change fundamental functionality.

**Acceptance Scenarios**:

1. **Given** a reader submits a query, **When** the AI begins generating the response, **Then** text appears incrementally in the chatbot interface rather than all at once
2. **Given** a streaming response is in progress, **When** an error occurs mid-stream, **Then** the partial response is preserved and an error indicator is shown
3. **Given** a streaming response is in progress, **When** the reader submits a new query, **Then** the current stream is cancelled and the new query begins

---

### User Story 4 - Local Development Testing (Priority: P2)

A developer working on the textbook content can run both the Docusaurus frontend and FastAPI backend locally, and test the chatbot functionality without deploying to production.

**Why this priority**: Essential for development workflow and testing changes before deployment, but end users don't interact with this directly.

**Independent Test**: Can be tested by following local setup instructions, starting both services on localhost, and verifying the chatbot works with localhost URLs. Delivers value for the development team but not end users.

**Acceptance Scenarios**:

1. **Given** a developer has both services running locally, **When** they open the Docusaurus site at localhost, **Then** the chatbot connects to the local FastAPI instance
2. **Given** the developer is testing locally, **When** they submit a query, **Then** CORS is properly configured to allow the localhost frontend to communicate with the localhost backend
3. **Given** configuration is needed for different environments, **When** the developer switches between local and production modes, **Then** API endpoints are automatically updated based on environment variables or build configuration

---

### User Story 5 - Production Deployment (Priority: P1)

The integrated chatbot works seamlessly when the static Docusaurus site is deployed to GitHub Pages and the FastAPI backend is hosted on a separate server with HTTPS enabled.

**Why this priority**: This is essential for the feature to be usable by actual readers. Without production deployment, only developers can access the feature.

**Independent Test**: Can be tested by deploying the Docusaurus site to GitHub Pages, verifying the chatbot connects to the production API endpoint over HTTPS, and confirming queries work end-to-end. Delivers the feature to all users.

**Acceptance Scenarios**:

1. **Given** the site is deployed to GitHub Pages, **When** a reader visits the site, **Then** the chatbot automatically connects to the production API endpoint using HTTPS
2. **Given** the production API requires HTTPS, **When** the frontend attempts to connect, **Then** no mixed-content warnings or security errors occur
3. **Given** CORS is configured for production, **When** the GitHub Pages domain makes requests to the API, **Then** the requests are allowed and responses are received successfully
4. **Given** the API endpoint URL needs to be configurable, **When** deploying to different environments, **Then** the API URL can be set via environment variables during the build process

---

### Edge Cases

- What happens when the API takes longer than 30 seconds to respond? (Should abort the request, show timeout error message, and allow retry)
- How does the system handle malformed or extremely long queries (>10,000 characters)? (Should validate and truncate with user warning)
- What happens when the reader navigates to a different page while waiting for a response? (Should cancel pending request or maintain state)
- How does the chatbot behave when JavaScript is disabled in the browser? (Should show static message indicating JavaScript is required)
- What happens when the reader submits multiple queries in rapid succession? (Should queue or cancel previous requests)
- How does the system handle responses that contain no valid source citations? (Should clearly indicate this to the user)
- What happens when the selected text context exceeds 2000 characters? (Should truncate to 2000 characters and show a notification: "Selected text truncated to 2000 characters")
- How does the chatbot appear on mobile devices with limited screen space? (Should use responsive design, possibly as a modal or bottom sheet)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The chatbot interface MUST be implemented as a bottom-right floating widget (circular or pill-shaped button) that expands to a chat panel when clicked, without requiring major layout changes to the existing Docusaurus theme
- **FR-002**: Users MUST be able to type questions into a text input field and submit them via Enter key or submit button
- **FR-003**: The system MUST send user queries to the FastAPI Agent endpoint as HTTP requests
- **FR-004**: The system MUST display AI-generated responses with visible formatting (paragraphs, lists, code blocks as appropriate)
- **FR-005**: The system MUST display source citations alongside AI responses, showing which sections of the book were referenced
- **FR-006**: Users MUST be able to select text on a page and an inline button/tooltip MUST appear near the selection, allowing them to submit it as contextual input to the chatbot
- **FR-007**: The system MUST support both localhost development (http://localhost) and production deployment (HTTPS) with configurable API endpoints
- **FR-008**: The system MUST handle CORS configuration to allow the static frontend to communicate with the external API
- **FR-009**: The system MUST display loading indicators while waiting for API responses
- **FR-010**: The system MUST display user-friendly error messages when the API is unavailable, requests timeout, or other errors occur
- **FR-010a**: API requests MUST timeout after 30 seconds, aborting the request and displaying a timeout error message with a retry option
- **FR-011**: The system MUST support incremental/streaming display of responses as they are generated using Server-Sent Events (SSE)
- **FR-012**: The chatbot UI MUST be responsive and functional on desktop, tablet, and mobile devices
- **FR-013**: The chat panel MUST be closeable/collapsible back to the floating button to avoid obscuring book content
- **FR-014**: The system MUST maintain a conversation history within the current session (lost on page refresh)
- **FR-015**: Query input MUST validate and limit length to prevent abuse or performance issues
- **FR-015a**: Selected text context MUST be truncated to a maximum of 2000 characters with a notification displayed to the user when truncation occurs
- **FR-016**: The system MUST cancel pending API requests when the user navigates away from the page
- **FR-017**: Source citations MUST be clickable links that navigate to the relevant section of the textbook
- **FR-017a**: The system MUST parse and display citations from the API response in the format `{url: string, title: string, excerpt: string}`, rendering the title as a clickable link and showing the excerpt as supporting context

### Key Entities

- **Chat Message**: Represents a single query or response in the conversation, including text content, timestamp, role (user or assistant), and associated source citations
- **Source Citation**: Represents a reference to book content with structure `{url: string, title: string, excerpt: string}` where `url` is the clickable link to the textbook section, `title` is the section/chapter name, and `excerpt` is a snippet of the referenced text
- **API Request**: Represents a query sent to the backend, including user message, selected text context (if any), conversation history, and configuration parameters
- **API Response**: Represents the backend's reply, including generated answer text (string), source citations array (Citation[]), status indicators, and error information if applicable

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can submit a query and receive a response in under 10 seconds for 95% of queries
- **SC-002**: The chatbot successfully completes at least 5 different full RAG query flows (query → retrieval → response → citation display) during integration testing
- **SC-003**: The system handles errors gracefully with user-friendly messages in 100% of failure scenarios (network errors, API timeouts, malformed responses)
- **SC-004**: The chatbot interface is fully functional on desktop (1920x1080), tablet (768x1024), and mobile (375x667) screen sizes
- **SC-005**: CORS configuration allows successful communication between the GitHub Pages frontend and the production API endpoint without security warnings
- **SC-006**: Readers can successfully select text on a page and submit it as context to the chatbot with the context properly included in the query
- **SC-007**: The system correctly handles and displays streaming or incremental responses with text appearing progressively rather than all at once
- **SC-008**: Local development setup works on first attempt following documentation, with both frontend and backend communicating successfully at localhost URLs
- **SC-009**: Source citations are accurate and clickable, navigating users to the correct textbook section 100% of the time
- **SC-010**: The chatbot UI does not negatively impact page load time (adds less than 500ms to initial page load)

### Assumptions

- The FastAPI backend from Spec-3 is already deployed and operational with documented API endpoints
- The Docusaurus site has an existing theme that can be extended with custom React components
- GitHub Pages supports static site hosting with external API calls via JavaScript
- The FastAPI backend supports CORS configuration (can be enabled via middleware)
- Readers have modern browsers with JavaScript enabled (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
- The backend API returns responses in a consistent JSON format with message text (string) and citations array where each citation has the structure `{url: string, title: string, excerpt: string}`
- Selected text context will be passed as an additional field in the API request payload
- API authentication/authorization is either not required or handled separately (not specified in requirements)
- Conversation history is ephemeral and does not need to persist across browser sessions
- The backend streaming mechanism (if implemented) is compatible with browser fetch API or similar client-side technology

### Dependencies

- Spec-3 RAG Agent implementation must be complete with accessible API endpoints
- Spec-1 and Spec-2 (retrieval pipeline and document ingestion) must be operational for the backend to return grounded responses
- Docusaurus build system must support custom React components and environment variable configuration
- Production hosting for FastAPI backend must be configured with HTTPS and CORS headers
- GitHub Pages deployment pipeline must be configured for the Docusaurus site

### Out of Scope

- Backend development (retrieval, embedding, agent logic) - covered by Specs 1, 2, and 3
- User authentication or authorization for chatbot access
- Persistent conversation history or user accounts
- Analytics dashboard or usage tracking
- Advanced chatbot features like voice input, image analysis, or multi-modal interactions
- Redesigning the overall Docusaurus site layout or theme
- Mobile native applications
- Offline functionality or PWA features
- Admin interface for monitoring or managing chatbot interactions
- A/B testing infrastructure
- Rate limiting or quota management on the frontend (assumed to be handled by backend)
