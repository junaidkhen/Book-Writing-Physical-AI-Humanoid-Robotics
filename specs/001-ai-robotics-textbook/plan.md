# Implementation Plan: Physical AI & Humanoid Robotics Textbook

**Branch**: `001-ai-robotics-textbook` | **Date**: 2025-12-10 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-ai-robotics-textbook/spec.md`

## Summary

Build a comprehensive educational textbook on Physical AI and Humanoid Robotics using Docusaurus v3 as a static site generator. The textbook will contain 4 modules with 15,000-20,000 total words, 20 runnable code examples (5 per module), and 12 diagrams. All content must meet WCAG 2.1 AA accessibility standards and deploy exclusively to Vercel. This is a documentation and educational content project with no backend, database, or physical hardware components.

## Technical Context

**Language/Version**: Node.js 18+, Python 3.8+ (for code examples and validation scripts)
**Primary Dependencies**: Docusaurus 3.x (static site generator), React (Docusaurus uses React), Markdown/MDX (content format)
**Storage**: File-based content (Markdown files in docs/ directory, no database)
**Testing**: Bash scripts (test.sh for examples), Python scripts (check-wordcount.py), Shell scripts (verify.sh, link-check.sh)
**Target Platform**: Web browsers (Chrome, Firefox, Safari, Edge) via Vercel deployment
**Project Type**: Single-project documentation site (Docusaurus static site)
**Performance Goals**: Fast static site build (<5 minutes), page load <2 seconds, accessible to screen readers
**Constraints**:
- Total word count 15,000-20,000 words distributed across 4 modules
- Exactly 20 code examples (5 per module)
- Minimum 12 diagrams with alt text
- All examples must run on Ubuntu 22.04 headless
- WCAG 2.1 AA compliance mandatory
- Vercel-only deployment (GitHub Pages explicitly prohibited)
- No hardware, ROS, or physical robotics execution
**Scale/Scope**: 4 modules, 20 code examples, 12 diagrams, 15k-20k words, single deployment target

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: PASS (Constitution file is template - using spec requirements as constitution)

The constitution file `.specify/memory/constitution.md` is currently a template. For this project, we treat the specification requirements as the constitutional principles:

- ✅ **Content Structure**: 4 modules with specific word counts (FR-001 through FR-006)
- ✅ **Diagram Requirements**: Minimum 12 diagrams with alt text and captions (FR-007 through FR-012)
- ✅ **Code Example Standards**: Exactly 20 examples with environment.yaml, requirements.txt, test.sh (FR-013 through FR-020)
- ✅ **Accessibility**: WCAG 2.1 AA compliance for all content (FR-012, FR-036)
- ✅ **Verification**: Automated scripts for validation before release (FR-021 through FR-025, FR-034 through FR-038)
- ✅ **Safety Constraints**: No hardware, ROS, or physical robot operations (FR-039 through FR-048)
- ✅ **Deployment**: Vercel-only deployment (FR-026)

No violations or complexity overrides required.

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-robotics-textbook/
├── spec.md              # Feature specification (already created)
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output: research findings
├── data-model.md        # Phase 1 output: content entities and structure
├── quickstart.md        # Phase 1 output: getting started guide
├── contracts/           # Phase 1 output: content templates and schemas
│   ├── module-template.md
│   ├── example-template.md
│   └── diagram-schema.yaml
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

This is a Docusaurus-based documentation project with the following structure:

```text
/
├── docs/                       # All textbook content (Markdown/MDX)
│   ├── intro.md
│   ├── module-1/
│   │   ├── _category_.json
│   │   ├── introduction.md
│   │   ├── foundations.md
│   │   └── applications.md
│   ├── module-2/
│   │   ├── _category_.json
│   │   └── [similar structure]
│   ├── module-3/
│   │   └── [similar structure]
│   └── module-4/
│       └── [similar structure]
│
├── diagrams/                   # Visual assets for learning content
│   ├── module-1/
│   │   ├── ai-perception-pipeline.svg
│   │   ├── sensor-fusion.svg
│   │   └── control-architecture.svg
│   ├── module-2/
│   ├── module-3/
│   ├── module-4/
│   └── meta.yaml              # Diagram metadata: alt text, captions
│
├── code/                       # Runnable code examples
│   ├── module-1/
│   │   ├── example-01-basic-perception/
│   │   │   ├── main.py
│   │   │   ├── environment.yaml
│   │   │   ├── requirements.txt
│   │   │   └── test.sh
│   │   ├── example-02-sensor-fusion/
│   │   └── [3 more examples]
│   ├── module-2/
│   ├── module-3/
│   └── module-4/
│
├── examples/                   # Example metadata
│   └── meta.yaml              # gpu: true flags, descriptions
│
├── scripts/                    # Validation and verification
│   ├── verify.sh              # Comprehensive validation
│   ├── check-wordcount.py     # Word count checker
│   └── link-check.sh          # Link validator
│
├── static/                     # Docusaurus static assets
│   ├── img/
│   └── [other static files]
│
├── src/                        # Docusaurus React components (optional)
│   ├── components/
│   └── pages/
│
├── specs/                      # Feature specifications
│   └── 001-ai-robotics-textbook/
│
├── templates/                  # Content templates
│   ├── frontmatter.md
│   └── example-frontmatter.md
│
├── history/                    # Automation logs
│   ├── prompts/
│   │   ├── constitution/
│   │   ├── 001-ai-robotics-textbook/
│   │   └── general/
│   └── adr/
│
├── .specify/                   # SpecKit internal
│   ├── memory/
│   ├── scripts/
│   └── templates/
│
├── .claude/                    # Claude automation data
│
├── docusaurus.config.js        # Docusaurus configuration
├── sidebars.js                 # Sidebar navigation
├── package.json                # Node dependencies
├── README.md                   # Project documentation
├── CLAUDE.md                   # Claude Code rules
└── vercel.json                 # Vercel deployment config
```

**Structure Decision**: Single-project Docusaurus documentation site. No backend, frontend split, or mobile components. All content is static Markdown/MDX files processed by Docusaurus into a static website. Code examples are standalone Python scripts with dependency management but are not integrated into the web application.

## Implementation Phases

### Phase 0: Research & Requirements Clarification

**Objective**: Resolve all technical unknowns and document decisions

**Research Tasks**:
1. Docusaurus best practices for educational content
2. Markdown/MDX features for technical documentation
3. WCAG 2.1 AA compliance for diagrams and code examples
4. Python dependency management patterns (environment.yaml + requirements.txt)
5. Vercel deployment configuration for Docusaurus
6. Automated accessibility testing tools
7. Link checking and validation tools for static sites

**Output**: `research.md` with findings, decisions, and rationale for each area

### Phase 1: Design & Contracts

**Objective**: Define content structure, templates, and validation contracts

**Deliverables**:

1. **data-model.md**: Content entities
   - Module entity: structure, frontmatter, word count targets
   - Code Example entity: required files, metadata schema
   - Diagram entity: formats, alt text requirements, caption structure
   - Verification Script entity: inputs, outputs, success criteria

2. **contracts/**: Content templates and schemas
   - `module-template.md`: Markdown template with frontmatter
   - `example-template.md`: Code example structure
   - `diagram-schema.yaml`: Diagram metadata schema

3. **quickstart.md**: Developer onboarding
   - Docusaurus installation and setup
   - Running the development server
   - Creating new modules and examples
   - Running verification scripts
   - Building and deploying to Vercel

4. **Agent context update**: Run `.specify/scripts/bash/update-agent-context.sh claude` to add Docusaurus and Python tooling to agent context

### Phase 2: Task Breakdown (handled by /sp.tasks)

This phase is NOT executed by /sp.plan. After Phase 1 completes, user runs `/sp.tasks` to generate `tasks.md` with testable implementation tasks.

## Key Architectural Decisions

### Decision 1: Docusaurus v3 as Static Site Generator

**Rationale**:
- Optimized for technical documentation with MDX support
- Built-in sidebar navigation and dark mode
- React-based extensibility for custom components
- Strong SEO and performance out of the box
- Excellent accessibility support
- Native deployment support for Vercel

**Alternatives Considered**:
- VitePress: Rejected due to less mature ecosystem for educational content
- Nextra: Rejected due to tighter coupling with Next.js
- Plain HTML/CSS: Rejected due to maintenance burden and lack of navigation features

### Decision 2: Separate Code Examples Directory

**Rationale**:
- Code examples need independent execution environments
- Easier to test examples in isolation
- Students can download and run examples without Docusaurus
- Clear separation between documentation and runnable code

**Alternatives Considered**:
- Embedding code in MDX: Rejected due to inability to test execution
- Submodules: Rejected due to complexity for educational use case

### Decision 3: File-Based Validation Scripts

**Rationale**:
- No database or backend to manage
- Scripts can run in CI/CD pipelines
- Easy for contributors to run locally
- Clear pass/fail criteria

**Alternatives Considered**:
- GitHub Actions only: Rejected due to need for local validation
- Manual validation: Rejected due to error-prone nature

### Decision 4: YAML Metadata Files

**Rationale**:
- Structured data for diagrams and examples
- Easy to parse in validation scripts
- Human-readable and editable
- Supports hierarchical data (nested properties)

**Alternatives Considered**:
- JSON: Rejected due to lack of comments and stricter syntax
- TOML: Rejected due to less widespread Python support
- Frontmatter in MD: Rejected due to separation of concerns

## Non-Functional Requirements

### Performance
- Build time: <5 minutes for full site
- Page load: <2 seconds on 3G connection
- First contentful paint: <1 second
- Lighthouse score: >90 on all metrics

### Accessibility
- WCAG 2.1 AA compliance mandatory
- All diagrams have descriptive alt text
- Semantic HTML structure
- Keyboard navigation support
- Screen reader compatible

### Security
- No user authentication or data storage
- No external API calls from examples without explicit approval
- All dependencies pinned to specific versions
- Regular security audits of npm packages

### Reliability
- All verification scripts must pass before deployment
- Zero broken links in production
- All code examples must execute successfully in CI
- Automated accessibility testing in CI

## Risk Mitigation

| Risk | Impact | Likelihood | Mitigation |
|------|--------|-----------|------------|
| Content word count targets missed | High | Medium | Incremental word count tracking during development |
| Code examples fail on clean Ubuntu | High | Medium | Docker container testing matching production environment |
| Accessibility audit failures | High | Low | Automated axe-core testing in CI, manual testing with screen readers |
| Diagram creation bottleneck | Medium | Medium | Use automated diagram tools (Mermaid, draw.io) |
| Vercel deployment issues | High | Low | Test deployment early with minimal content |
| Link rot after deployment | Low | Medium | Automated link checking in CI, periodic manual review |

## Complexity Tracking

No violations. This project uses a standard Docusaurus static site structure appropriate for educational content. All complexity is justified by the specification requirements:

- Multiple modules: Required by spec (4 modules)
- Separate code directory: Required for independent execution and testing
- Validation scripts: Required by FR-021 through FR-025
- Metadata files: Required for structured diagram/example information

No additional abstraction layers or architectural patterns needed beyond Docusaurus conventions.

## Next Steps

1. ✅ **Phase 0 Complete**: This plan document is now ready
2. **Phase 0 Research**: Generate `research.md` with findings for Docusaurus, accessibility tools, and validation approaches
3. **Phase 1 Design**: Generate `data-model.md`, `contracts/`, and `quickstart.md`
4. **Phase 1 Agent Update**: Run `.specify/scripts/bash/update-agent-context.sh claude`
5. **Phase 2 Planning**: User runs `/sp.tasks` to generate implementation task breakdown

---

**Report**:
- Branch: `001-ai-robotics-textbook`
- Plan Path: `/mnt/e/Junaid/Book-Wr-Claude/specs/001-ai-robotics-textbook/plan.md`
- Status: Phase 0 planning complete, ready for research phase
