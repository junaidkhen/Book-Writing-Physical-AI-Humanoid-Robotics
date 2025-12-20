<!--
  SYNC IMPACT REPORT
  Version change: NONE → 1.0.0 (Initial constitution ratification)
  Modified principles: N/A (initial creation)
  Added sections: All (Core Principles I-VII, Technical Standards, Quality Gates, Governance)
  Removed sections: N/A
  Templates requiring updates:
    ✅ plan-template.md - Constitution Check section ready
    ✅ spec-template.md - Aligns with user story prioritization
    ✅ tasks-template.md - Aligns with TDD and user story organization
  Follow-up TODOs: None
-->

# Physical AI & Humanoid Robotics Textbook - Constitution

## Core Principles

### I. Data Integrity First (NON-NEGOTIABLE)

**Document ingestion and processing MUST preserve 100% data integrity. No data loss is acceptable.**

- All ingestion operations MUST be atomic or recoverable (partial failures do not corrupt existing data)
- Content hashing MUST be used for duplicate detection and integrity verification
- Chunking MUST preserve semantic boundaries and maintain bidirectional links to source documents
- Vector embeddings MUST be validated before storage (dimension checks, NaN detection)
- Failed ingestion attempts MUST be logged with full error context and MUST NOT affect successfully processed data
- Database operations MUST use transactions where applicable to ensure consistency

**Rationale**: Document loss or corruption undermines trust in the knowledge base and creates irrecoverable gaps in the educational content.

### II. API-First Design

**Every feature MUST expose well-defined, documented REST API endpoints before or alongside any UI implementation.**

- FastAPI endpoints MUST follow RESTful conventions (proper HTTP methods, status codes, resource naming)
- Request/response models MUST use Pydantic for validation and automatic OpenAPI documentation
- Error responses MUST include structured error messages with error codes, human-readable descriptions, and actionable guidance
- API versioning MUST be considered from the start (e.g., `/api/v1/` prefix for future compatibility)
- All endpoints MUST have explicit timeout and rate-limiting considerations documented

**Rationale**: API-first design enables independent frontend/backend development, facilitates testing, and allows multiple client interfaces (web, mobile, CLI) to consume the same backend services.

### III. Test-Driven Development (NON-NEGOTIABLE)

**Tests MUST be written before implementation code. Red-Green-Refactor cycle is mandatory.**

- **Contract tests**: For all API endpoints (request/response validation, status codes, error cases)
- **Integration tests**: For external services (Qdrant, Cohere, OpenAI) with mocked responses
- **Unit tests**: For business logic, chunking algorithms, data transformations
- Test coverage MUST be ≥80% for core business logic (ingestion, retrieval, chunking)
- Tests MUST run in CI/CD pipeline; failing tests MUST block merges
- Use pytest with fixtures for database/API mocking; avoid test interdependencies

**TDD Workflow**:
1. Write failing test that describes expected behavior
2. Get user approval on test cases
3. Run tests → verify RED (failing)
4. Implement minimal code to pass tests → GREEN
5. Refactor for clarity/performance while keeping tests GREEN

**Rationale**: TDD prevents rework, documents intended behavior, and ensures code meets specifications before implementation begins.

### IV. Security & Input Validation

**All external inputs MUST be validated, sanitized, and checked for malicious content.**

- **File uploads**: Validate MIME types, file extensions, size limits (max 500MB per spec)
- **URL inputs**: Prevent SSRF attacks by validating schemes (http/https only), blocking private IP ranges, and sanitizing redirect chains
- **Text extraction**: Sanitize HTML/markup to prevent XSS when displaying content
- **API inputs**: Pydantic validation for all request bodies; reject invalid requests with 400 Bad Request
- **Secrets management**: NEVER commit secrets; use `.env` files (gitignored) for API keys, database credentials
- **Dependencies**: Keep dependencies updated; monitor for CVEs using `pip-audit` or similar tools

**Rationale**: Educational content systems are targets for injection attacks, data exfiltration, and abuse. Proactive security prevents compromise.

### V. Performance & Scalability

**System MUST meet defined performance benchmarks and scale gracefully.**

Performance Targets (from spec):
- Single document (100 pages): <30 seconds processing time
- Batch processing: ≥50 documents per hour
- Memory usage: <2GB RAM per document
- API response times: <200ms p95 for retrieval endpoints

Scalability Requirements:
- Support up to 10,000 documents without degradation
- Chunk storage scales linearly with document count
- Use connection pooling for Qdrant and external APIs
- Implement pagination for large result sets (max 100 items per page)
- Monitor and log slow operations (>1s) for optimization

**Rationale**: Educational platforms must provide responsive experiences. Performance degradation frustrates users and limits adoption.

### VI. Observability & Structured Logging

**All operations MUST be observable through structured logging, metrics, and health checks.**

Logging Requirements:
- Use Python's `logging` module with structured JSON output (timestamp, level, component, message, context)
- Log levels: DEBUG (development), INFO (key operations), WARNING (recoverable issues), ERROR (failures)
- Include request IDs for tracing multi-step operations (ingestion → chunking → embedding → storage)
- Log all API requests/responses (sanitize sensitive data)
- Log ingestion job status: start time, end time, document count, success/failure counts, error details

Observability:
- Health check endpoint (`/health`) returning service status, dependency health (Qdrant, Cohere, OpenAI)
- Metrics endpoint (`/metrics`) for ingestion stats, document counts, average processing times
- Error aggregation: Track error types and frequencies to identify systemic issues

**Rationale**: Production issues are impossible to debug without comprehensive logging. Structured logs enable automated monitoring and alerting.

### VII. Simplicity & YAGNI (You Aren't Gonna Need It)

**Implement only what the specification requires. Avoid premature abstraction and over-engineering.**

- Start with the simplest solution that meets requirements
- No abstractions until the third use case demonstrates the pattern (Rule of Three)
- No feature flags, versioning, or backward-compatibility shims unless explicitly required
- Delete unused code completely; no commented-out code, no `_unused_var` patterns
- Prefer composition over inheritance; prefer functions over classes when state is unnecessary
- Avoid frameworks/libraries for one-off operations (e.g., don't add a task queue library for sequential batch processing)

**Anti-patterns to avoid**:
- Premature optimization (profile first, optimize bottlenecks second)
- Generic "helpers" or "utils" modules (context-specific names preferred)
- Design for hypothetical future requirements
- Complex configuration systems for simple toggles

**Rationale**: Complexity is a tax on velocity and maintainability. Simple code is easier to understand, test, and modify.

## Technical Standards

### Language & Framework Standards

**Python** (Backend - Ingestion Pipeline & FastAPI):
- Version: Python 3.11+ (required for FastAPI and type hints)
- Type hints MUST be used for all function signatures and class attributes
- Code style: Follow PEP 8; use `black` for formatting, `ruff` for linting
- Async/await for I/O-bound operations (HTTP requests, database queries)
- Virtual environments: Use `venv` or `uv` for dependency isolation

**JavaScript/TypeScript** (Frontend - Docusaurus):
- Version: Node.js 18+ for Docusaurus 3.x compatibility
- Use TypeScript for type safety in React components
- Code style: ESLint + Prettier with Airbnb config (or similar consistent ruleset)
- Component structure: Functional components with hooks (no class components)

### Dependency Management

- Pin exact versions in production (`==` in requirements.txt, exact versions in package.json)
- Use version ranges only in development (e.g., `>=4.0.0,<5.0.0` for Cohere)
- Document why each dependency is needed (no orphaned dependencies)
- Review licenses for compatibility (prefer MIT, Apache 2.0, BSD)

### Error Handling

- Use try-except blocks for all external I/O (file operations, HTTP requests, database queries)
- Never silently swallow exceptions; always log with context
- Raise specific exception types (ValueError, TypeError, HTTPException) not generic `Exception`
- Provide actionable error messages (e.g., "Qdrant collection 'documents' not found. Run ingestion pipeline first.")

## Quality Gates

### Before `/sp.plan` Completion
- [ ] All spec.md user stories have explicit priorities (P1, P2, P3...)
- [ ] Success criteria include measurable metrics (<30s, 95% accuracy, etc.)
- [ ] Security requirements specified (input validation, SSRF prevention)
- [ ] Performance benchmarks defined

### Before `/sp.tasks` Completion
- [ ] plan.md includes complete technical context (Python version, FastAPI, Qdrant, Cohere)
- [ ] data-model.md defines all entities (Document, Chunk, IngestionJob) with field types
- [ ] contracts/ directory has API endpoint specifications (if applicable)
- [ ] Project structure documented (single/web/mobile) with directory layout

### Before `/sp.implement` Execution
- [ ] All tasks have explicit file paths and acceptance criteria
- [ ] Test tasks precede implementation tasks (TDD order)
- [ ] Parallel tasks [P] marked correctly (no file conflicts)
- [ ] Constitution check passes (no principle violations)

### Before Code Merge
- [ ] All tests passing (pytest with ≥80% coverage)
- [ ] No linting errors (`ruff check`, `black --check`)
- [ ] Type checking passes (`mypy` for Python, `tsc` for TypeScript)
- [ ] API documentation auto-generated (FastAPI `/docs` endpoint accessible)
- [ ] No secrets committed (`.env` in `.gitignore`)
- [ ] Logging statements present for all major operations

## Governance

### Amendment Process

This constitution is a living document. Amendments require:

1. **Proposal**: Document the proposed change with rationale and impact analysis
2. **Review**: Assess impact on existing features and templates
3. **Approval**: Document decision (accepted/rejected with reasoning)
4. **Migration**: Update affected code, templates, and documentation
5. **Version Bump**: Increment CONSTITUTION_VERSION (MAJOR for breaking changes, MINOR for additions, PATCH for clarifications)

### Compliance & Enforcement

- All pull requests MUST reference this constitution in review
- `/sp.analyze` command validates spec/plan/tasks alignment with principles
- Constitution violations MUST be justified in plan.md "Complexity Tracking" table
- Unjustified violations MUST be resolved before implementation proceeds

### Versioning Policy

Constitution follows semantic versioning:
- **MAJOR** (X.0.0): Backward-incompatible changes (principle removal, redefinition)
- **MINOR** (0.X.0): New principles added, sections expanded
- **PATCH** (0.0.X): Clarifications, typo fixes, non-semantic refinements

### Exception Handling

Exceptions to principles are permitted ONLY when:
1. Explicitly documented in plan.md "Complexity Tracking" table
2. Justified with clear reasoning (why simpler alternatives are insufficient)
3. Approved by project stakeholders
4. Timeboxed with a plan to refactor/remove the exception

**Version**: 1.0.0 | **Ratified**: 2025-12-17 | **Last Amended**: 2025-12-17
