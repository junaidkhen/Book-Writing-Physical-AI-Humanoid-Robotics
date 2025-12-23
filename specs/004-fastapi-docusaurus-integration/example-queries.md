# Example Queries for RAG Chatbot Testing

**Feature**: 004-fastapi-docusaurus-integration
**Purpose**: Test queries for validating RAG functionality across various scenarios
**Date**: 2025-12-17

## Overview

This document provides example queries to test the RAG chatbot's functionality across different complexity levels, content types, and edge cases.

---

## Category 1: Basic Factual Queries

### Simple Definition Queries
1. "What is reinforcement learning?"
2. "Define inverse kinematics"
3. "What are actuators?"
4. "Explain humanoid robots"

**Expected Behavior**:
- Quick response (<5 seconds)
- Clear, concise definitions
- 1-3 relevant citations from textbook chapters

---

## Category 2: Conceptual Understanding Queries

### Explain Concepts
1. "How does a humanoid robot maintain balance?"
2. "What are the key components of a humanoid robot?"
3. "Explain the difference between forward and inverse kinematics"
4. "How do sensors work in humanoid robotics?"

**Expected Behavior**:
- Detailed explanations with examples
- 3-5 citations from multiple chapters
- Structured response with clear sections

---

## Category 3: Comparative Queries

### Compare and Contrast
1. "What's the difference between DC motors and servo motors?"
2. "Compare centralized and decentralized control systems"
3. "Contrast supervised and unsupervised learning in robotics"
4. "How do bipedal and quadrupedal robots differ?"

**Expected Behavior**:
- Side-by-side comparison format
- Citations from relevant comparative sections
- Clear distinction between concepts

---

## Category 4: Application-Based Queries

### Practical Applications
1. "How is machine learning used in humanoid robotics?"
2. "What role do sensors play in obstacle avoidance?"
3. "How can I implement path planning for a robot?"
4. "What are the applications of computer vision in robotics?"

**Expected Behavior**:
- Practical examples and use cases
- Step-by-step explanations where applicable
- Real-world applications referenced

---

## Category 5: Mathematical/Technical Queries

### Technical Deep Dives
1. "Explain the Denavit-Hartenberg parameters"
2. "What is the Jacobian matrix in robotics?"
3. "How do you calculate torque requirements for joints?"
4. "Explain the mathematics behind PID controllers"

**Expected Behavior**:
- Mathematical formulas (if available in content)
- Detailed technical explanations
- Citations from technical chapters

---

## Category 6: Context-Enhanced Queries

### With Selected Text Context

**Scenario**: User selects text: "Humanoid robots must maintain stability through continuous sensor feedback and dynamic balance control."

**Example Queries**:
1. "Can you explain this in more detail?"
2. "What sensors are typically used for this?"
3. "How does dynamic balance control work?"
4. "Give me an example of this in practice"

**Expected Behavior**:
- Response directly references selected text
- Contextually relevant citations
- Builds upon the selected passage

---

## Category 7: Multi-Step Reasoning Queries

### Complex Queries Requiring Multiple Sources
1. "How do you design a complete control system for a humanoid robot from sensors to actuators?"
2. "What are the steps to implement autonomous navigation?"
3. "Explain the full pipeline for object recognition and manipulation"
4. "How would you integrate AI and mechanical systems in a humanoid?"

**Expected Behavior**:
- Comprehensive, structured responses
- Multiple citations across chapters
- Logical flow connecting concepts

---

## Category 8: Edge Cases and Error Handling

### Empty or Invalid Queries
1. "" (empty query)
2. "???"
3. "a" (single character)
4. "Tell me about quantum physics" (out of scope)

**Expected Behavior**:
- Validation errors for empty/invalid queries
- Polite "out of scope" message for irrelevant topics
- Suggestions to refine the query

### Very Long Queries
5. Query with 1000+ characters testing truncation

**Expected Behavior**:
- Proper truncation with warning
- Still functional response
- Context preserved where possible

---

## Category 9: Citation Navigation Testing

### Queries to Test Citation Clicks
1. "What are the main sensor types used in robotics?" (expect specific chapter citations)
2. "Explain actuator control systems" (expect links to actuator chapters)

**Test Steps**:
1. Submit query
2. Wait for response with citations
3. Click each citation link
4. Verify navigation to correct textbook section

**Expected Behavior**:
- Citations are clickable
- Links navigate to correct pages
- Page scrolls to relevant section (if anchors exist)

---

## Category 10: Streaming and Performance Testing

### Queries for Streaming Validation
1. "Explain the complete architecture of a humanoid robot in detail" (long response)
2. "List all the components of a robotic system with descriptions" (structured list)

**Test Steps**:
1. Submit query
2. Observe streaming behavior
3. Verify incremental text display
4. Test cancel button during streaming

**Expected Behavior**:
- Text appears incrementally
- "AI is typing..." indicator shows
- Cancel button functional
- Auto-scroll follows new content

---

## Test Execution Checklist

### Before Testing
- [ ] Backend is running (localhost:8000 or production URL)
- [ ] Frontend is running (localhost:3000)
- [ ] Health check endpoint returns 200 OK
- [ ] Vector store is populated with embeddings

### During Testing
- [ ] Test at least 2 queries from each category
- [ ] Verify response time (<10s for 95% of queries)
- [ ] Check citation quality and relevance
- [ ] Test streaming with cancel functionality
- [ ] Test context-enhanced queries with text selection
- [ ] Verify error handling for invalid inputs

### Success Criteria
- [ ] All categories produce relevant responses
- [ ] Citations are accurate and navigable
- [ ] Streaming works smoothly without lag
- [ ] Error messages are user-friendly
- [ ] Performance meets <10s response time goal
- [ ] No console errors during normal operation

---

## Troubleshooting Test Failures

### Slow Response Times (>10s)
- Check vector store connection
- Verify sufficient OpenAI API rate limits
- Monitor backend logs for bottlenecks

### Irrelevant Responses
- Verify embeddings quality in vector store
- Check topK parameter (default: 5)
- Review retrieval scores in citations

### Citation Links Not Working
- Verify URL format in vector store metadata
- Check Docusaurus routing configuration
- Test navigation with browser console open

### Streaming Not Working
- Check browser EventSource support
- Verify CORS headers in backend
- Monitor network tab for SSE connection

---

## Additional Testing Scenarios

### Concurrent Users (Load Testing)
1. Open multiple browser tabs
2. Submit queries simultaneously
3. Verify all receive responses
4. Check for race conditions or errors

### Network Conditions
1. Test with throttled connection (DevTools Network tab)
2. Verify timeout handling (30s)
3. Test retry logic on network failures

### Browser Compatibility
- [ ] Chrome/Chromium (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)

---

## Notes
- Save query/response pairs for regression testing
- Document any edge cases discovered during testing
- Update this document with new scenarios as needed
- Use browser DevTools Network/Console tabs for debugging
