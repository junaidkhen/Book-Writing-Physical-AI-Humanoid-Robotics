# Research: FastAPI RAG Backend with Docusaurus Frontend Integration

**Feature**: 004-fastapi-docusaurus-integration
**Date**: 2025-12-11
**Phase**: 0 - Research & Design Decisions

## Overview

This document consolidates research findings and design decisions for integrating a FastAPI RAG backend with a Docusaurus static frontend, enabling an embedded chatbot component for querying textbook content.

## Research Areas

### 1. Docusaurus Component Integration

**Decision**: Use Docusaurus theme swizzling with Root.tsx wrapper for global chatbot availability

**Rationale**:
- Docusaurus 3.x supports theme component swizzling for customization
- The Root.tsx component wraps the entire site, ideal for persistent UI elements
- Avoids modifying every page individually
- Maintains Docusaurus build and deployment pipeline compatibility

**Alternatives Considered**:
1. **Manual component import on every page**: Rejected - requires modifying all existing pages, not maintainable
2. **Custom Docusaurus plugin**: Rejected - overcomplicated for a single component, adds maintenance burden
3. **Script injection via docusaurus.config.js**: Rejected - poor React integration, harder to maintain state

**Implementation Approach**:
- Create `src/theme/Root.tsx` to wrap site with chatbot component
- Use React Context for chatbot state management (open/closed, messages)
- Component will be a floating button/widget that expands to chat interface
- CSS modules for scoped styling to avoid conflicts with existing theme

**References**:
- Docusaurus Swizzling: https://docusaurus.io/docs/swizzling
- React Context API for global state

---

### 2. API Communication Pattern

**Decision**: Use Fetch API with EventSource for SSE streaming responses

**Rationale**:
- Fetch API is native, well-supported in all modern browsers, no dependencies needed
- EventSource API provides standard SSE support for streaming responses
- FastAPI natively supports SSE via `StreamingResponse` with `text/event-stream`
- Simpler than WebSockets for unidirectional server-to-client streaming

**Alternatives Considered**:
1. **Axios library**: Rejected - adds dependency, Fetch API is sufficient for our needs
2. **WebSockets**: Rejected - bidirectional streaming not needed, more complex setup
3. **Polling**: Rejected - inefficient, poor user experience for long responses

**Implementation Approach**:
- Standard Fetch for non-streaming endpoints (health, metadata, retrieve)
- EventSource for `/ask` endpoint streaming responses
- Fallback to non-streaming if SSE fails or unsupported
- Error handling with exponential backoff for retries
- Request cancellation on component unmount or navigation

**Technical Details**:
```javascript
// Streaming with EventSource
const eventSource = new EventSource(`${API_URL}/ask?query=${encodedQuery}`);
eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Append to message display
};
eventSource.onerror = () => {
  eventSource.close();
  // Handle error
};
```

**References**:
- EventSource API: https://developer.mozilla.org/en-US/docs/Web/API/EventSource
- FastAPI SSE: https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse

---

### 3. Environment Configuration Strategy

**Decision**: Use docusaurus.config.js custom fields + runtime config file for API endpoints

**Rationale**:
- docusaurus.config.js supports custom fields accessible in components
- Build-time configuration for compile-time optimizations
- Runtime config file (`static/config/api-config.json`) for deployment flexibility
- Supports both local development and production without code changes

**Alternatives Considered**:
1. **Environment variables only**: Rejected - requires rebuild for endpoint changes, not suitable for static GitHub Pages
2. **Hardcoded endpoints**: Rejected - violates security and maintainability principles
3. **Server-side configuration**: Rejected - not possible with static GitHub Pages deployment

**Implementation Approach**:
```javascript
// docusaurus.config.js
module.exports = {
  customFields: {
    apiBaseUrl: process.env.API_BASE_URL || 'http://localhost:8000',
  },
};

// Runtime config fallback
// static/config/api-config.json
{
  "development": {
    "apiBaseUrl": "http://localhost:8000"
  },
  "production": {
    "apiBaseUrl": "https://api.yourproject.com"
  }
}
```

**Configuration Priority**:
1. Runtime config file (highest priority, for production deployments)
2. docusaurus.config.js custom fields (build-time default)
3. Hardcoded localhost fallback (development safety net)

**References**:
- Docusaurus custom fields: https://docusaurus.io/docs/configuration#custom-configurations

---

### 4. CORS Configuration

**Decision**: Backend FastAPI adds CORS middleware with configurable allowed origins

**Rationale**:
- FastAPI provides built-in CORS middleware via `fastapi.middleware.cors`
- Required for static frontend on different origin to call API
- Environment-based origin whitelist for security (localhost + production domains)
- Preflight request handling for complex requests (POST, custom headers)

**Implementation Approach** (Backend - Spec-3 extension):
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Docusaurus dev server
        "https://yourproject.github.io",  # GitHub Pages
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)
```

**Security Considerations**:
- Never use `allow_origins=["*"]` in production
- Validate and whitelist specific domains
- Use environment variables for origin configuration
- Monitor and log CORS violations

**References**:
- FastAPI CORS: https://fastapi.tiangolo.com/tutorial/cors/

---

### 5. Text Selection Context Feature

**Decision**: Use native browser Selection API with custom context menu or button

**Rationale**:
- window.getSelection() provides standard text selection access
- No dependencies needed for core functionality
- Cross-browser compatible (Chrome, Firefox, Safari, Edge)
- Can trigger chatbot with selected text as context parameter

**Alternatives Considered**:
1. **Browser extension for text selection**: Rejected - requires user installation, out of scope
2. **Third-party selection library**: Rejected - unnecessary dependency
3. **Copy-paste only**: Rejected - poor UX, doesn't capture text automatically

**Implementation Approach**:
```javascript
// On text selection
document.addEventListener('mouseup', () => {
  const selection = window.getSelection();
  const selectedText = selection.toString().trim();

  if (selectedText.length > 0) {
    // Show "Ask AI about this" button near selection
    // Or auto-populate chatbot input with context
  }
});
```

**UX Design Options**:
1. Floating button near selection (preferred - non-intrusive)
2. Context menu item (browser compatibility concerns)
3. Automatic context injection (least intrusive)

**References**:
- Selection API: https://developer.mozilla.org/en-US/docs/Web/API/Selection

---

### 6. Error Handling Strategy

**Decision**: Implement tiered error handling with user-friendly messages and logging

**Rationale**:
- Multiple failure points: network, API, parsing, rendering
- Users should never see raw error messages or stack traces
- Developers need detailed logs for debugging
- Graceful degradation when backend unavailable

**Error Categories**:
1. **Network Errors**: Connection failure, timeout, DNS issues
   - User Message: "Unable to connect to the service. Please check your internet connection."
   - Action: Retry button, fallback to offline mode indicator

2. **API Errors**: 4xx/5xx HTTP responses
   - User Message: "Service temporarily unavailable. Please try again."
   - Action: Log detailed error, show retry option

3. **Parsing Errors**: Malformed JSON, unexpected response structure
   - User Message: "Received an unexpected response. Please try again."
   - Action: Log response for debugging

4. **Validation Errors**: Query too long, empty input
   - User Message: "Please enter a valid question (max 1000 characters)."
   - Action: Input field validation feedback

**Implementation Pattern**:
```javascript
try {
  const response = await fetch(API_URL);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  const data = await response.json();
  // Process data
} catch (error) {
  console.error('API Error:', error);
  setErrorMessage(getUserFriendlyMessage(error));
}
```

**Logging Strategy**:
- Console logs for development (not in production)
- Error boundaries in React components
- Request/response logging for debugging
- No sensitive data in logs

---

### 7. Component State Management

**Decision**: Use React Context + useReducer for chatbot state, local useState for component-specific state

**Rationale**:
- Chatbot state needs to be accessible across multiple components
- React Context avoids prop drilling through Docusaurus theme layers
- useReducer for complex state transitions (sending, receiving, error states)
- No need for Redux or external state management library (overkill for single feature)

**State Structure**:
```typescript
interface ChatbotState {
  isOpen: boolean;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  selectedContext: string | null;
}

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  timestamp: Date;
}
```

**Context Scope**:
- Global context for chatbot open/closed state
- Local component state for input field, message rendering
- Session storage for conversation persistence (optional)

**References**:
- React Context: https://react.dev/learn/passing-data-deeply-with-context
- useReducer: https://react.dev/reference/react/useReducer

---

### 8. Mobile Responsiveness

**Decision**: Use CSS media queries with bottom-sheet style modal for mobile, floating widget for desktop

**Rationale**:
- Different UX patterns optimize for screen size
- Bottom sheet is mobile-native pattern for overlays
- Floating widget works well on desktop without obscuring content
- Maintains accessibility and usability across devices

**Breakpoints**:
- Mobile: < 768px (bottom sheet, full-width)
- Tablet: 768px - 1024px (responsive modal)
- Desktop: > 1024px (floating widget, fixed size)

**Mobile UX Considerations**:
- Touch-friendly button sizes (minimum 44x44px)
- Keyboard management (auto-focus input, close on keyboard dismiss)
- Scrollable message list with proper touch handling
- Avoid fixed positioning conflicts with browser chrome

**Implementation Approach**:
```css
/* Mobile-first approach */
.chatbot-container {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 80vh;
  /* Bottom sheet styling */
}

@media (min-width: 1024px) {
  .chatbot-container {
    bottom: 20px;
    right: 20px;
    left: auto;
    width: 400px;
    height: 600px;
    /* Floating widget styling */
  }
}
```

---

## Resolved Clarifications

### Originally Marked "NEEDS CLARIFICATION" in Technical Context

1. **Streaming Response Mechanism**: ✅ Resolved - Using EventSource API for SSE from FastAPI
2. **API Endpoint URLs**: ✅ Resolved - Environment-based configuration via docusaurus.config.js + runtime JSON
3. **CORS Configuration**: ✅ Resolved - FastAPI CORS middleware with whitelist approach
4. **Text Selection Implementation**: ✅ Resolved - Native Selection API with floating button UX
5. **Mobile UI Pattern**: ✅ Resolved - Bottom sheet for mobile, floating widget for desktop
6. **State Management Approach**: ✅ Resolved - React Context + useReducer, no external library needed

---

## Technology Stack Summary

### Frontend
- **Framework**: Docusaurus 3.9.2 (React 19.0.0)
- **Language**: JavaScript/TypeScript (TypeScript preferred for type safety)
- **Styling**: CSS Modules (Docusaurus standard)
- **State Management**: React Context + useReducer
- **HTTP Client**: Native Fetch API
- **Streaming**: EventSource API (SSE)
- **Build Tool**: Docusaurus CLI (webpack under the hood)

### Backend (Existing - Spec-3)
- **Framework**: FastAPI
- **Language**: Python 3.9+
- **Agent**: OpenAI Agents SDK
- **Vector Store**: Qdrant
- **Middleware**: CORS for cross-origin requests

### Development & Deployment
- **Local Development**: Docusaurus dev server (localhost:3000) + FastAPI (localhost:8000)
- **Production Frontend**: GitHub Pages (static)
- **Production Backend**: Separate FastAPI hosting (HTTPS required)
- **Testing**: Jest + React Testing Library + manual E2E tests

---

## Best Practices Applied

1. **Progressive Enhancement**: Chatbot is an enhancement, core content remains accessible without it
2. **Graceful Degradation**: Clear error messages when backend unavailable
3. **Accessibility**: Keyboard navigation, ARIA labels, screen reader support
4. **Performance**: Lazy loading, code splitting for chatbot bundle
5. **Security**: No secrets in frontend, CORS whitelist, input validation
6. **Maintainability**: Component modularity, clear separation of concerns
7. **Testability**: Pure functions for API logic, component unit tests

---

## Risk Analysis

### Technical Risks

1. **SSE Browser Compatibility**
   - Risk: Older browsers may not support EventSource
   - Mitigation: Feature detection + fallback to polling or standard POST

2. **CORS Preflight Latency**
   - Risk: OPTIONS preflight adds latency to first request
   - Mitigation: FastAPI caching of CORS headers, minimal custom headers

3. **GitHub Pages Deployment Constraints**
   - Risk: Static site can't hide API endpoints or secrets
   - Mitigation: All sensitive config on backend, public API URLs acceptable

4. **Text Selection Conflicts**
   - Risk: May interfere with existing Docusaurus features (copy, search)
   - Mitigation: Opt-in activation (button click), non-intrusive UI placement

### Operational Risks

1. **Backend Availability**
   - Risk: Static frontend deployed but backend down
   - Mitigation: Health check indicator, graceful error messages, retry logic

2. **API URL Changes**
   - Risk: Hardcoded URLs require redeployment
   - Mitigation: Runtime config file for production URL updates without rebuild

---

## Next Steps (Phase 1)

1. Generate data-model.md for key frontend entities (Message, Citation, ChatState)
2. Create OpenAPI contract documentation for chatbot-specific endpoints
3. Write quickstart.md for local development setup
4. Proceed to Phase 2 (tasks.md generation) after design approval

---

**Research Completed**: 2025-12-11
**Status**: ✅ All NEEDS CLARIFICATION items resolved
**Ready for Phase 1**: Yes
