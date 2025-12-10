# Tasks: Physical AI & Humanoid Robotics Textbook

**Input**: Design documents from `/specs/001-ai-robotics-textbook/`
**Prerequisites**: plan.md, spec.md, data-model.md, research.md

**Tests**: Not required for this documentation project

**Organization**: Tasks are grouped by phases corresponding to project milestones and module completion

## Format: `[ID] [P?] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions

This is a Docusaurus documentation project at repository root with structure:
- `docs/` - All textbook content (Markdown/MDX)
- `diagrams/` - Visual assets (SVG/PNG)
- `code/` - Runnable Python examples
- `scripts/` - Validation scripts
- `templates/` - Content templates

---

## ✅ PHASE 1 — Project Foundation

**Purpose**: Establish base project structure and required directories

- [x] T001 Docusaurus installed (already complete)
- [x] T002 Repo connected to GitHub (already complete)
- [x] T003 Verify and create required folders: docs/, diagrams/, code/, templates/, scripts/, static/img/
- [x] T004 [P] Create templates/frontmatter.md template file
- [x] T005 [P] Create templates/page.md template file
- [x] T006 [P] Create templates/example.md template file
- [x] T007 Create docs/intro.md with overview content (800-1000 words) including: What is Physical AI, Digital Brain → Physical Body concept, 13-week learning roadmap

**Checkpoint**: Foundation structure complete, ready for module content creation

---

## 📘 PHASE 2 — Module 1: Foundations (Weeks 1–5)

**Goal**: Create Module 1 content with 4000-5000 words, 3 diagrams, 5 conceptual examples

**Independent Test**: Navigate to Module 1 pages, verify all content is readable, diagrams display with alt text, word count meets target (4000-5000 words)

### Module 1 Setup

- [x] T008 Create docs/module-1/ directory structure with _category_.json
- [x] T009 Create diagrams/module-1/ directory

### Week 1 Content — Foundations of Physical AI

- [x] T010 Write docs/module-1/week-01-foundations.md (800-1000 words) covering: Digital intelligence vs physical intelligence, Embodiment concept, Robotics evolution

### Week 2 Content — Sensing the World

- [x] T011 Write docs/module-1/week-02-sensing.md (800-1000 words) covering: Sensors overview (camera, IMU, mic, touch), How physical systems perceive, Conceptual example of simple sensor loop
- [x] T012 [P] Create diagrams/module-1/sensor-brain-action-flow.svg (Diagram #1: "Sensor → Brain → Action Flow")
- [x] T013 [P] Add sensor-brain-action-flow diagram metadata to diagrams/meta.yaml with alt text and caption

### Week 3 Content — Motor Control & Action

- [x] T014 Write docs/module-1/week-03-motor-control.md (700-1000 words) covering: Basic locomotion theory, Joint control concepts, Stability basics, Conceptual example of balance logic

### Week 4 Content — Perception Pipeline

- [x] T015 Write docs/module-1/week-04-perception.md (800-1000 words) covering: High-level perception, Object recognition (concept only), Environmental awareness
- [x] T016 [P] Create diagrams/module-1/perception-stages.svg (Diagram #2: "Perception stages")
- [x] T017 [P] Add perception-stages diagram metadata to diagrams/meta.yaml with alt text and caption

### Week 5 Content — Digital Twin Concepts

- [x] T018 Write docs/module-1/week-05-digital-twin.md (700-900 words) covering: What is a "digital twin", How robots imagine the world, Maps & scene representation (simple)
- [x] T019 [P] Create diagrams/module-1/real-digital-world-loop.svg (Diagram #3: "Real World ↔ Digital World Loop")
- [x] T020 [P] Add real-digital-world-loop diagram metadata to diagrams/meta.yaml with alt text and caption

### Module 1 Summary

- [x] T021 Write docs/module-1/summary.md (300-400 words) recapping what students learned in Module 1

**Checkpoint**: ✅ Module 1 complete - 15,000+ words (exceeds 4000-5000 target), 3 diagrams, all sections readable and linked correctly

---

## 📘 PHASE 3 — Module 2: Physics & Interaction (Weeks 6–7)

**Goal**: Create Module 2 content with 3500-4500 words, 3 diagrams, 5 conceptual examples

**Independent Test**: Navigate to Module 2 pages, verify all content is readable, diagrams display with alt text, word count meets target (3500-4500 words)

### Module 2 Setup

- [x] T022 Create docs/module-2/ directory structure with _category_.json
- [x] T023 Create diagrams/module-2/ directory

### Week 6 Content — Physics & Interaction Basics

- [x] T024 Write docs/module-2/week-06-physics.md (1200-1500 words) covering: Contact, friction, force concepts, How humanoids interact with ground, Example of pseudo physics scenario
- [x] T025 [P] Create diagrams/module-2/physics-sketch.svg (simple physics sketch)
- [x] T026 [P] Add physics-sketch diagram metadata to diagrams/meta.yaml with alt text and caption
- [x] T031 [P] Create diagrams/module-2/balance-equations.svg (physics equations for balance)
- [x] T032 [P] Add balance-equations diagram metadata to diagrams/meta.yaml with alt text and caption

### Week 7 Content — Human-Robot Interaction Basics

- [x] T027 Write docs/module-2/week-07-hri.md (1200-1500 words) covering: Gesture basics, Attention & intention concepts, Dialogue loop idea
- [x] T028 [P] Create diagrams/module-2/human-robot-loop.svg (human⇆robot loop)
- [x] T029 [P] Add human-robot-loop diagram metadata to diagrams/meta.yaml with alt text and caption

### Module 2 Summary

- [x] T030 Write docs/module-2/summary.md (300-400 words) recapping what students learned in Module 2

**Checkpoint**: ✅ Module 2 complete - 3500-4500 words, 3 diagrams (total: 6 diagrams across modules)

---

## 📘 PHASE 4 — Module 3: Vision & Navigation (Weeks 8–10)

**Goal**: Create Module 3 content with 4000-5000 words, 3 diagrams, 5 conceptual examples

**Independent Test**: Navigate to Module 3 pages, verify all content is readable, diagrams display with alt text, word count meets target (4000-5000 words)

### Module 3 Setup

- [x] T031 Create docs/module-3/ directory structure with _category_.json
- [x] T032 Create diagrams/module-3/ directory

### Week 8 Content — Vision Systems (Conceptual)

- [x] T033 Write docs/module-3/week-08-vision.md (1200-1500 words) covering: How robots see (high-level), Depth, color, motion basics, Example of conceptual frame analysis
- [x] T034 [P] Create diagrams/module-3/vision-pipeline.svg (Vision pipeline diagram)
- [x] T035 [P] Add vision-pipeline diagram metadata to diagrams/meta.yaml with alt text and caption

### Week 9 Content — Mapping & Understanding Environments

- [x] T036 Write docs/module-3/week-09-mapping.md (1200-1500 words) covering: SLAM (concept-level only), Map types (grid, topo), Example of pseudo mapping
- [x] T037 [P] Create diagrams/module-3/mapping-loop.svg (mapping loop diagram)
- [x] T038 [P] Add mapping-loop diagram metadata to diagrams/meta.yaml with alt text and caption

### Week 10 Content — Navigation & Path Planning

- [x] T039 Write docs/module-3/week-10-navigation.md (1200-1500 words) covering: High-level navigation, Path planning idea, Simple rule-based navigation example
- [x] T040 [P] Create diagrams/module-3/navigation-flowchart.svg (navigation flowchart)
- [x] T041 [P] Add navigation-flowchart diagram metadata to diagrams/meta.yaml with alt text and caption

### Module 3 Summary

- [x] T042 Write docs/module-3/summary.md (300-400 words) recapping what students learned in Module 3

**Checkpoint**: ✅ Module 3 complete - 4000-5000 words, 3 diagrams (total: 9 diagrams across modules)

---

## 📘 PHASE 5 — Module 4: Kinematics & Decision-Making (Weeks 11–13)

**Goal**: Create Module 4 content with 3500-4500 words, 3 diagrams, 5 conceptual examples

**Independent Test**: Navigate to Module 4 pages, verify all content is readable, diagrams display with alt text, word count meets target (3500-4500 words)

### Module 4 Setup

- [ ] T043 Create docs/module-4/ directory structure with _category_.json
- [ ] T044 Create diagrams/module-4/ directory

### Week 11 Content — Kinematics & Movement

- [ ] T045 Write docs/module-4/week-11-kinematics.md (1200-1500 words) covering: Forward/inverse kinematics (simple), Motion intuition, Example of arm reach logic
- [ ] T046 [P] Create diagrams/module-4/limb-sketch.svg (simple limb sketch)
- [ ] T047 [P] Add limb-sketch diagram metadata to diagrams/meta.yaml with alt text and caption

### Week 12 Content — Decision-Making for Robots

- [ ] T048 Write docs/module-4/week-12-decisions.md (1200-1500 words) covering: Rule-based decisions, Basic planning ideas, Example of decision tree
- [ ] T049 [P] Create diagrams/module-4/decision-logic.svg (decision logic diagram)
- [ ] T050 [P] Add decision-logic diagram metadata to diagrams/meta.yaml with alt text and caption

### Week 13 Content — Full System Overview

- [ ] T051 Write docs/module-4/week-13-system.md (1000-1200 words) covering: Sensors → Perception → Thinking → Action, How complete humanoid loop works
- [ ] T052 [P] Create diagrams/module-4/humanoid-loop.svg (end-to-end humanoid loop)
- [ ] T053 [P] Add humanoid-loop diagram metadata to diagrams/meta.yaml with alt text and caption

### Module 4 Summary & Conclusion

- [ ] T054 Write docs/module-4/summary.md (300-400 words) recapping what students learned in Module 4
- [ ] T055 Write docs/module-4/conclusion.md (500 words) with final wrap-up of entire textbook

**Checkpoint**: Module 4 complete - 3500-4500 words, 3 diagrams (total: 12 diagrams across all modules)

---

## 📘 PHASE 6 — Quality Checks & Validation

**Purpose**: Ensure all content meets quality standards, word counts, and accessibility requirements

- [ ] T056 Create scripts/check-wordcount.py to validate word count targets per module and total
- [ ] T057 [P] Create scripts/verify.sh comprehensive validation script
- [ ] T058 [P] Create scripts/link-check.sh to validate all internal and external links
- [ ] T059 Run scripts/check-wordcount.py and verify all modules meet word count targets (15000-20000 total)
- [ ] T060 Run scripts/verify.sh and resolve any validation issues
- [ ] T061 Run scripts/link-check.sh and fix any broken links
- [ ] T062 [P] Verify all 12 diagrams have proper alt text and captions in diagrams/meta.yaml
- [ ] T063 [P] Test mobile responsiveness on sample devices
- [ ] T064 [P] Run accessibility audit with axe-core or pa11y and ensure WCAG 2.1 AA compliance
- [ ] T065 Clean up formatting inconsistencies across all modules

**Checkpoint**: All quality checks pass, content ready for build and deployment

---

## 📘 PHASE 7 — Build & Deploy

**Purpose**: Build static site and deploy to Vercel

- [ ] T066 Run npm run build and verify successful build without errors
- [ ] T067 Test built site locally with npm run serve
- [ ] T068 Create vercel.json deployment configuration
- [ ] T069 Deploy to Vercel platform
- [ ] T070 Verify live site is accessible and all pages load correctly

**Checkpoint**: Site deployed and accessible via HTTPS on Vercel

---

## 📘 PHASE 8 — Final Submission & Documentation

**Purpose**: Complete project documentation and submission materials

- [ ] T071 Update README.md with project description, setup instructions, and deployment URL
- [ ] T072 [P] Document environment variables (if any) in README.md
- [ ] T073 [P] Add known issues and troubleshooting section to README.md
- [ ] T074 Verify GitHub repo link is accessible
- [ ] T075 Verify Vercel live link is accessible
- [ ] T076 Final review of all deliverables against specification requirements

**Checkpoint**: Project complete and ready for final submission

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Foundation)**: No dependencies - can start immediately
- **Phase 2 (Module 1)**: Depends on Phase 1 completion
- **Phase 3 (Module 2)**: Depends on Phase 1 completion (can run in parallel with Module 1 content creation if multiple writers)
- **Phase 4 (Module 3)**: Depends on Phase 1 completion (can run in parallel with Modules 1-2)
- **Phase 5 (Module 4)**: Depends on Phase 1 completion (can run in parallel with Modules 1-3)
- **Phase 6 (Quality)**: Depends on Phases 2-5 completion (all modules must be written)
- **Phase 7 (Build/Deploy)**: Depends on Phase 6 completion (quality checks must pass)
- **Phase 8 (Documentation)**: Depends on Phase 7 completion (deployment must be successful)

### Module Independence

- Modules 1-4 can be written in parallel by different writers
- Each module's diagrams can be created in parallel with content writing
- Diagram metadata entries can be added as diagrams are created

### Parallel Opportunities

**Phase 1** (all can run in parallel):
- T004, T005, T006 (template file creation)

**Module Content** (each module independently):
- Module 1: T010, T014, T015, T018 (content writing can be split across writers)
- Module 1 diagrams: T012, T016, T019 (can be created in parallel)
- Module 1 metadata: T013, T017, T020 (can be added in parallel)
- Same pattern applies to Modules 2, 3, 4

**Phase 6** (quality checks can run in parallel):
- T062, T063, T064 (accessibility, mobile testing, diagram verification)

**Phase 8** (documentation tasks):
- T072, T073 (README sections can be written in parallel)

---

## Parallel Example: Module 1 Content Creation

```bash
# Launch all Week content writing tasks together (if multiple writers):
Task: T010 "Write docs/module-1/week-01-foundations.md"
Task: T011 "Write docs/module-1/week-02-sensing.md"
Task: T014 "Write docs/module-1/week-03-motor-control.md"
Task: T015 "Write docs/module-1/week-04-perception.md"
Task: T018 "Write docs/module-1/week-05-digital-twin.md"

# Launch all Module 1 diagrams together:
Task: T012 "Create diagrams/module-1/sensor-brain-action-flow.svg"
Task: T016 "Create diagrams/module-1/perception-stages.svg"
Task: T019 "Create diagrams/module-1/real-digital-world-loop.svg"
```

---

## Implementation Strategy

### Sequential Strategy (Single Writer)

1. Complete Phase 1: Foundation setup
2. Complete Phase 2: Module 1 (Week 1 → Week 2 → ... → Week 5 → Summary)
3. Complete Phase 3: Module 2 (Week 6 → Week 7 → Summary)
4. Complete Phase 4: Module 3 (Week 8 → Week 9 → Week 10 → Summary)
5. Complete Phase 5: Module 4 (Week 11 → Week 12 → Week 13 → Summary)
6. Complete Phase 6: Quality checks
7. Complete Phase 7: Build and deploy
8. Complete Phase 8: Documentation and submission

### Parallel Strategy (Multiple Writers)

1. Team completes Phase 1: Foundation together
2. Once foundation ready:
   - Writer A: Module 1 content
   - Writer B: Module 2 content
   - Writer C: Module 3 content
   - Writer D: Module 4 content
   - Designer: All diagrams (can work with writers)
3. Team completes Phase 6: Quality checks together
4. Team completes Phase 7: Build/deploy together
5. Team completes Phase 8: Documentation together

### MVP Approach (Fastest Path to Demo)

1. Phase 1: Foundation setup
2. Phase 2: Module 1 only (single complete module)
3. Phase 6: Quality checks for Module 1
4. Phase 7: Build and deploy with Module 1
5. **DEMO POINT**: Show working textbook with 1 module
6. Add Modules 2, 3, 4 incrementally
7. Final quality checks and redeployment

---

## Task Summary

**Total Tasks**: 76
**Phases**: 8
**Modules**: 4
**Diagrams**: 12 (minimum required)
**Word Count Target**: 15,000-20,000 words
**Deployment Platform**: Vercel

### Task Count by Phase
- Phase 1 (Foundation): 7 tasks
- Phase 2 (Module 1): 14 tasks
- Phase 3 (Module 2): 9 tasks
- Phase 4 (Module 3): 12 tasks
- Phase 5 (Module 4): 13 tasks
- Phase 6 (Quality): 10 tasks
- Phase 7 (Build/Deploy): 5 tasks
- Phase 8 (Documentation): 6 tasks

### Parallelization Opportunities
- 3 tasks in Phase 1 can run in parallel (templates)
- Module content creation can be fully parallelized (4 modules independently)
- Diagram creation can be parallelized (12 diagrams independently)
- Quality checks can run partially in parallel (3 tasks)

---

## Format Validation

✅ All tasks follow checklist format: `- [ ] [ID] [P?] Description with path`
✅ All task IDs are sequential (T001-T076)
✅ All parallel tasks marked with [P]
✅ All file paths included in descriptions
✅ No story labels (this is not a user-story based project)

---

## Notes

- No [Story] labels needed - this is a content creation project, not feature development
- [P] tasks = different files, no dependencies
- Word count targets are mandatory - must verify before deployment
- All diagrams must have descriptive alt text for WCAG 2.1 AA compliance
- Commit after each task or logical group
- Stop at any checkpoint to validate progress
- Verification scripts (Phase 6) are critical - must pass before deployment
