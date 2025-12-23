# Data Model: FastAPI RAG Backend with Docusaurus Frontend Integration

**Feature**: 004-fastapi-docusaurus-integration
**Date**: 2025-12-11
**Phase**: 1 - Data Model Design

## Overview

This document defines the data structures and entities used in the Docusaurus chatbot frontend for communicating with the FastAPI RAG backend. These models represent client-side state, API request/response schemas, and UI component data.

## Entity Definitions

### 1. Message

Represents a single message in the chatbot conversation (user query or AI response).

**Purpose**: Display conversation history, manage message state, enable citation linking

**Attributes**:

| Attribute | Type | Required | Description | Validation |
|-----------|------|----------|-------------|------------|
| id | string | Yes | Unique message identifier (UUID v4) | Non-empty, UUID format |
| role | enum | Yes | Message sender: "user" or "assistant" | Must be "user" \| "assistant" |
| content | string | Yes | Message text content | Non-empty, max 10,000 chars |
| citations | Citation[] | No | Source references (only for assistant) | Empty for user messages |
| timestamp | Date | Yes | Message creation time | Valid ISO 8601 timestamp |
| status | enum | No | Message status: "sending", "sent", "error" | Default: "sent" |

**Relationships**:
- A Message (role="assistant") has 0-N Citations
- Messages are ordered chronologically in Conversation

**State Transitions**:
```
User Message: [draft] -> sending -> sent
                            ↓
                          error

Assistant Message: [draft] -> streaming -> sent
                                 ↓
                               error
```

**Example**:
```typescript
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
  timestamp: Date;
  status?: 'sending' | 'sent' | 'error' | 'streaming';
}

// User message example
{
  id: "550e8400-e29b-41d4-a716-446655440000",
  role: "user",
  content: "What are the key components of a humanoid robot?",
  timestamp: new Date("2025-12-11T10:30:00Z"),
  status: "sent"
}

// Assistant message example
{
  id: "660e8400-e29b-41d4-a716-446655440001",
  role: "assistant",
  content: "Humanoid robots consist of three main components: sensors...",
  citations: [
    {
      chunkId: "ch3-sec2-p5",
      title: "Chapter 3: Sensor Systems",
      url: "/docs/module-3/sensors",
      excerpt: "Humanoid robots utilize multiple sensor modalities...",
      score: 0.89
    }
  ],
  timestamp: new Date("2025-12-11T10:30:05Z"),
  status: "sent"
}
```

---

### 2. Citation

Represents a source reference to textbook content retrieved from the backend.

**Purpose**: Provide traceable references, enable navigation to source content, display relevance

**Note**: Per spec clarification (2025-12-17), the backend MUST return at minimum `{url, title, excerpt}`. The fields `chunkId` and `score` are optional frontend enhancements for debugging and relevance display.

**Attributes**:

| Attribute | Type | Required | Description | Validation |
|-----------|------|----------|-------------|------------|
| chunkId | string | Yes | Unique identifier for source chunk | Non-empty |
| title | string | Yes | Human-readable section title | Non-empty, max 200 chars |
| url | string | Yes | Relative or absolute URL to source | Valid URL format |
| excerpt | string | No | Brief text excerpt from source | Max 500 chars |
| score | number | No | Relevance score (0.0 - 1.0) | 0 ≤ score ≤ 1 |

**Relationships**:
- Citations belong to a Message (role="assistant")
- A Citation references a specific chunk in the textbook

**Example**:
```typescript
interface Citation {
  chunkId: string;
  title: string;
  url: string;
  excerpt?: string;
  score?: number;
}

{
  chunkId: "ch4-sec1-p12",
  title: "Chapter 4: Actuator Control",
  url: "/docs/module-4/actuators#control-systems",
  excerpt: "Actuator control in humanoid robotics requires precise...",
  score: 0.92
}
```

---

### 3. ChatbotState

Represents the global state of the chatbot UI.

**Purpose**: Manage conversation flow, UI visibility, error states, loading indicators

**Attributes**:

| Attribute | Type | Required | Description | Validation |
|-----------|------|----------|-------------|------------|
| isOpen | boolean | Yes | Chatbot widget visibility | Default: false |
| messages | Message[] | Yes | Conversation history | Ordered chronologically |
| isLoading | boolean | Yes | Loading/processing indicator | Default: false |
| error | string \| null | Yes | Current error message | null when no error |
| selectedContext | string \| null | No | Pre-selected text from page | Max 2000 chars (per spec FR-015a) |
| inputValue | string | Yes | Current input field value | Max 1000 chars |

**State Transitions**:
```
Chatbot Lifecycle:
closed -> open -> (user query) -> loading -> response received -> open
                                    ↓
                                  error -> open (with error message)

Message Submission:
idle -> loading (isLoading=true) -> response -> idle (isLoading=false)
         ↓
       error (isLoading=false, error set)
```

**Example**:
```typescript
interface ChatbotState {
  isOpen: boolean;
  messages: Message[];
  isLoading: boolean;
  error: string | null;
  selectedContext: string | null;
  inputValue: string;
}

// Initial state
{
  isOpen: false,
  messages: [],
  isLoading: false,
  error: null,
  selectedContext: null,
  inputValue: ""
}

// Active conversation state
{
  isOpen: true,
  messages: [
    { id: "1", role: "user", content: "What is inverse kinematics?", ... },
    { id: "2", role: "assistant", content: "Inverse kinematics is...", ... }
  ],
  isLoading: false,
  error: null,
  selectedContext: null,
  inputValue: "Can you explain forward kinematics?"
}
```

---

### 4. APIRequest

Represents a query request sent to the FastAPI backend.

**Purpose**: Structure API calls, pass query parameters, include context

**Attributes**:

| Attribute | Type | Required | Description | Validation |
|-----------|------|----------|-------------|------------|
| query | string | Yes | User's question or search phrase | Non-empty, max 1000 chars |
| context | string | No | Selected text context from page | Max 2000 chars (per spec FR-015a) |
| topK | number | No | Number of chunks to retrieve | 1 ≤ topK ≤ 20, default: 5 |
| temperature | number | No | Agent response temperature | 0 ≤ temp ≤ 0.2, default: 0.1 |
| stream | boolean | No | Enable streaming responses | Default: true |

**Request Format** (HTTP POST to `/ask`):
```typescript
interface APIRequest {
  query: string;
  context?: string;
  topK?: number;
  temperature?: number;
  stream?: boolean;
}

// Example request body
{
  "query": "What are the key components of a humanoid robot?",
  "context": "In this section, we discuss the fundamental architecture...",
  "topK": 5,
  "temperature": 0.1,
  "stream": true
}
```

---

### 5. APIResponse

Represents the structured response from the FastAPI backend.

**Purpose**: Deserialize API responses, extract answer and citations, handle metadata

**Attributes**:

| Attribute | Type | Required | Description | Validation |
|-----------|------|----------|-------------|------------|
| answer | string | Yes | AI-generated response text | Non-empty |
| citations | Citation[] | Yes | Source references | Can be empty array |
| reasoning | string[] | No | Agent reasoning steps | Optional for transparency |
| metadata | ResponseMetadata | Yes | Performance and usage info | - |

**ResponseMetadata**:

| Attribute | Type | Required | Description |
|-----------|------|----------|-------------|
| promptTokens | number | Yes | Input token count |
| completionTokens | number | Yes | Output token count |
| totalTokens | number | Yes | Total token usage |
| retrievalTime | number | Yes | Retrieval latency (ms) |
| agentTime | number | Yes | Agent processing time (ms) |
| totalTime | number | Yes | Total response time (ms) |
| chunksRetrieved | number | Yes | Number of chunks used |

**Example**:
```typescript
interface ResponseMetadata {
  promptTokens: number;
  completionTokens: number;
  totalTokens: number;
  retrievalTime: number;
  agentTime: number;
  totalTime: number;
  chunksRetrieved: number;
}

interface APIResponse {
  answer: string;
  citations: Citation[];
  reasoning?: string[];
  metadata: ResponseMetadata;
}

// Example response
{
  "answer": "Humanoid robots consist of three main components: sensory systems...",
  "citations": [
    {
      "chunkId": "ch3-sec2-p5",
      "title": "Chapter 3: Sensor Systems",
      "url": "/docs/module-3/sensors",
      "excerpt": "Humanoid robots utilize multiple sensor modalities...",
      "score": 0.89
    },
    {
      "chunkId": "ch4-sec1-p12",
      "title": "Chapter 4: Actuator Control",
      "url": "/docs/module-4/actuators",
      "excerpt": "Actuator systems provide movement and manipulation...",
      "score": 0.87
    }
  ],
  "reasoning": [
    "Query interpreted as: Components of humanoid robots",
    "Retrieved 5 chunks with avg score 0.85",
    "Answer synthesized from top 3 chunks"
  ],
  "metadata": {
    "promptTokens": 1200,
    "completionTokens": 350,
    "totalTokens": 1550,
    "retrievalTime": 450,
    "agentTime": 3200,
    "totalTime": 3650,
    "chunksRetrieved": 5
  }
}
```

---

### 6. StreamChunk

Represents a single chunk of data received via Server-Sent Events (SSE) streaming.

**Purpose**: Handle incremental response updates, display streaming text

**Attributes**:

| Attribute | Type | Required | Description | Validation |
|-----------|------|----------|-------------|------------|
| type | enum | Yes | Chunk type: "content", "citation", "done", "error" | Enum validation |
| data | string \| Citation | Yes | Chunk payload (type-dependent) | - |
| messageId | string | Yes | Associated message ID | UUID format |

**Stream Event Types**:

1. **content**: Incremental text content
   ```json
   { "type": "content", "data": "Humanoid robots consist of...", "messageId": "msg-123" }
   ```

2. **citation**: Source reference
   ```json
   {
     "type": "citation",
     "data": {
       "chunkId": "ch3-sec2-p5",
       "title": "Chapter 3: Sensor Systems",
       "url": "/docs/module-3/sensors",
       "score": 0.89
     },
     "messageId": "msg-123"
   }
   ```

3. **done**: Stream completion
   ```json
   { "type": "done", "data": "", "messageId": "msg-123" }
   ```

4. **error**: Error occurred
   ```json
   { "type": "error", "data": "Retrieval timeout", "messageId": "msg-123" }
   ```

**Example**:
```typescript
interface StreamChunk {
  type: 'content' | 'citation' | 'done' | 'error';
  data: string | Citation;
  messageId: string;
}

// Processing stream chunks
eventSource.onmessage = (event) => {
  const chunk: StreamChunk = JSON.parse(event.data);

  switch (chunk.type) {
    case 'content':
      appendToMessage(chunk.messageId, chunk.data);
      break;
    case 'citation':
      addCitation(chunk.messageId, chunk.data);
      break;
    case 'done':
      finalizeMessage(chunk.messageId);
      eventSource.close();
      break;
    case 'error':
      handleStreamError(chunk.messageId, chunk.data);
      eventSource.close();
      break;
  }
};
```

---

### 7. APIConfiguration

Represents environment-specific API configuration.

**Purpose**: Manage API endpoint URLs, enable environment switching, support deployments

**Attributes**:

| Attribute | Type | Required | Description | Validation |
|-----------|------|----------|-------------|------------|
| environment | enum | Yes | Current environment: "development" or "production" | Enum validation |
| apiBaseUrl | string | Yes | Base URL for FastAPI backend | Valid URL format |
| timeout | number | No | Request timeout (ms) | Default: 30000 |
| retryAttempts | number | No | Max retry attempts | Default: 3 |

**Configuration Sources** (Priority Order):
1. Runtime config file (`/config/api-config.json`)
2. Build-time custom fields (`docusaurus.config.js`)
3. Hardcoded defaults (localhost)

**Example**:
```typescript
interface APIConfiguration {
  environment: 'development' | 'production';
  apiBaseUrl: string;
  timeout?: number;
  retryAttempts?: number;
}

// Development configuration
{
  "environment": "development",
  "apiBaseUrl": "http://localhost:8000",
  "timeout": 30000,
  "retryAttempts": 3
}

// Production configuration
{
  "environment": "production",
  "apiBaseUrl": "https://api.yourproject.com",
  "timeout": 30000,
  "retryAttempts": 3
}
```

---

## Data Flow Diagrams

### User Query Flow

```
User Input → Validation → APIRequest
                              ↓
                      HTTP POST /ask (with SSE)
                              ↓
                     [Backend Processing]
                              ↓
                      StreamChunk events
                              ↓
                      Update ChatbotState
                              ↓
                      Render Message with Citations
```

### Text Selection Context Flow

```
Text Selection → window.getSelection()
                         ↓
                  selectedContext (ChatbotState)
                         ↓
                  User clicks "Ask AI"
                         ↓
                  APIRequest (with context)
                         ↓
                  [Backend includes context in prompt]
                         ↓
                  Response with context-aware answer
```

### Error Handling Flow

```
API Call → Network Error / HTTP Error / Parsing Error
              ↓
        Error Detection
              ↓
        Update ChatbotState.error
              ↓
        Display ErrorMessage component
              ↓
        User clicks Retry → Clear error → Retry API Call
```

---

## Validation Rules

### Input Validation (Client-Side)

1. **Query Length**: 1 - 1000 characters
   - Empty queries rejected
   - Queries > 1000 chars truncated with warning

2. **Selected Context**: 0 - 2000 characters (per spec FR-015a)
   - Auto-truncate if exceeds limit with user notification
   - Preserve semantic boundaries (complete sentences when possible)

3. **Configuration Values**:
   - topK: 1 ≤ value ≤ 20
   - temperature: 0 ≤ value ≤ 0.2
   - timeout: 1000 ≤ value ≤ 60000

### Response Validation (Client-Side)

1. **Required Fields**: Reject responses missing required fields (answer, citations, metadata)
2. **Type Checking**: Validate data types match schema
3. **Citation URLs**: Validate URL format before rendering links
4. **Score Range**: Ensure citation scores are 0 ≤ score ≤ 1

---

## Storage Strategy

### Session Storage (Optional Enhancement)

```typescript
// Persist conversation across page reloads (same session)
sessionStorage.setItem('chatbot-messages', JSON.stringify(messages));

// Restore on component mount
const savedMessages = sessionStorage.getItem('chatbot-messages');
if (savedMessages) {
  setMessages(JSON.parse(savedMessages));
}
```

### No Long-Term Persistence
- No localStorage usage (per spec requirements)
- No cookies for conversation history
- State resets on browser close or session end

---

## API Contract References

See `contracts/chatbot-api.openapi.yaml` for complete API endpoint specifications.

---

**Data Model Completed**: 2025-12-11
**Status**: ✅ All entities defined with validation rules
**Ready for Implementation**: Yes
