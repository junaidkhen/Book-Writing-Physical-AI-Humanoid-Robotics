# Research: Physical AI & Humanoid Robotics Textbook

**Feature**: 001-ai-robotics-textbook
**Date**: 2025-12-10
**Phase**: Phase 0 - Requirements Clarification

## Overview

This document consolidates research findings for building a Docusaurus-based educational textbook on Physical AI and Humanoid Robotics. All technical unknowns from the Technical Context section have been resolved.

## Research Areas

### 1. Docusaurus Best Practices for Educational Content

**Decision**: Use Docusaurus 3.x with standard configuration optimized for educational documentation

**Key Findings**:
- **Sidebar Organization**: Use `_category_.json` files in each module directory to define sidebar ordering and labels
- **Frontmatter**: Include `title`, `sidebar_label`, `sidebar_position`, and `description` in each Markdown file
- **MDX Features**: Support interactive code blocks with syntax highlighting via Prism.js (built-in)
- **Search**: Integrate Algolia DocSearch or local search plugin for content discoverability
- **Navigation**: Use breadcrumbs and "Edit this page" links to GitHub for contributor-friendly documentation

**Implementation Approach**:
```javascript
// docusaurus.config.js structure
module.exports = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'Comprehensive Educational Textbook',
  url: 'https://your-site.vercel.app',
  baseUrl: '/',
  organizationName: 'your-org',
  projectName: 'physical-ai-textbook',
  themeConfig: {
    navbar: { /* navigation */ },
    footer: { /* footer links */ },
    prism: {
      theme: lightCodeTheme,
      darkTheme: darkCodeTheme,
    },
  },
  presets: [
    [
      'classic',
      {
        docs: {
          routeBasePath: '/',
          sidebarPath: require.resolve('./sidebars.js'),
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],
};
```

**References**:
- Docusaurus official documentation: https://docusaurus.io/docs
- Docusaurus showcase for educational sites: https://docusaurus.io/showcase?tags=education

---

### 2. Markdown/MDX Features for Technical Documentation

**Decision**: Use MDX for interactive components, standard Markdown for text-heavy content

**Key Findings**:
- **Code Blocks**: Support language-specific syntax highlighting with title and line numbers
- **Admonitions**: Use built-in callouts (note, tip, warning, danger) for important information
- **Tabs**: Group related content (e.g., Python vs JavaScript examples) using `@theme/Tabs`
- **Diagrams**: Embed SVG/PNG images using standard Markdown image syntax with alt text
- **Math**: Integrate KaTeX for mathematical equations (important for robotics formulas)
- **Mermaid**: Optional support for flowcharts and diagrams via remark-mermaid plugin

**Implementation Approach**:
```markdown
---
title: Module 1 - Physical AI Foundations
sidebar_position: 1
---

# Physical AI Foundations

:::tip Prerequisites
This module assumes basic knowledge of linear algebra and Python programming.
:::

## Sensor Fusion

![Sensor Fusion Architecture](../../diagrams/module-1/sensor-fusion.svg)
*Figure 1.1: Multi-sensor fusion pipeline for robot perception*

```python title="sensor_fusion.py"
import numpy as np

def kalman_filter(measurement, prediction):
    # Kalman filter implementation
    return fused_estimate
```

:::warning GPU Required
This example requires CUDA-compatible GPU for real-time performance.
:::
```

**References**:
- MDX documentation: https://mdxjs.com/
- Docusaurus Markdown features: https://docusaurus.io/docs/markdown-features

---

### 3. WCAG 2.1 AA Compliance for Diagrams and Code Examples

**Decision**: Implement comprehensive accessibility features meeting WCAG 2.1 AA standards

**Key Findings**:
- **Alt Text**: Every diagram must have descriptive alt text (not just filename)
- **Color Contrast**: Minimum contrast ratio of 4.5:1 for normal text, 3:1 for large text
- **Semantic HTML**: Use proper heading hierarchy (h1, h2, h3) without skipping levels
- **Keyboard Navigation**: All interactive elements accessible via keyboard
- **Screen Reader Support**: Test with NVDA (Windows) and VoiceOver (macOS)
- **Code Blocks**: Ensure syntax highlighting doesn't rely solely on color

**Implementation Approach**:
```markdown
<!-- Good: Descriptive alt text -->
![Architecture diagram showing three layers: perception, planning, and control, with arrows indicating data flow between components](../../diagrams/module-1/architecture.svg)

<!-- Bad: Non-descriptive alt text -->
![diagram](../../diagrams/module-1/architecture.svg)
```

**Validation Tools**:
- **axe-core**: Automated accessibility testing library
- **WAVE**: Browser extension for manual accessibility evaluation
- **Lighthouse**: Automated audits in Chrome DevTools (Accessibility category)
- **pa11y**: Command-line tool for automated accessibility testing

**Automated Testing Script**:
```bash
#!/bin/bash
# scripts/accessibility-check.sh
npx pa11y-ci --sitemap http://localhost:3000/sitemap.xml --threshold 0
```

**References**:
- WCAG 2.1 Guidelines: https://www.w3.org/WAI/WCAG21/quickref/
- Docusaurus accessibility: https://docusaurus.io/docs/accessibility

---

### 4. Python Dependency Management (environment.yaml + requirements.txt)

**Decision**: Use conda environment.yaml for system-level dependencies, pip requirements.txt for Python packages

**Key Findings**:
- **environment.yaml**: Manage Python version, system libraries (OpenCV, CUDA)
- **requirements.txt**: Pin Python package versions for reproducibility
- **pyproject.toml**: Optional alternative for modern Python projects with Poetry/Hatch
- **test.sh**: Wrapper script to set up environment and run example

**Implementation Approach**:
```yaml
# code/module-1/example-01/environment.yaml
name: physical-ai-example-01
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.10
  - numpy=1.24
  - pip
  - pip:
    - -r requirements.txt
```

```txt
# code/module-1/example-01/requirements.txt
opencv-python==4.8.1.78
scikit-learn==1.3.2
matplotlib==3.8.2
```

```bash
#!/bin/bash
# code/module-1/example-01/test.sh
set -e

# Create conda environment if it doesn't exist
if ! conda env list | grep -q "physical-ai-example-01"; then
  conda env create -f environment.yaml
fi

# Activate environment and run example
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate physical-ai-example-01
python main.py

echo "✅ Example completed successfully"
```

**References**:
- Conda documentation: https://docs.conda.io/en/latest/
- pip requirements files: https://pip.pypa.io/en/stable/reference/requirements-file-format/

---

### 5. Vercel Deployment Configuration for Docusaurus

**Decision**: Use Vercel's zero-config deployment with custom build settings for Docusaurus

**Key Findings**:
- **Build Command**: `npm run build` (Docusaurus default)
- **Output Directory**: `build/` (Docusaurus default)
- **Node Version**: 18.x or higher (specify in package.json engines field)
- **Environment Variables**: None required for static site (add if using external APIs)
- **Preview Deployments**: Automatic preview for every PR
- **Production Deployment**: Automatic deployment on merge to main branch

**Implementation Approach**:
```json
// vercel.json
{
  "version": 2,
  "buildCommand": "npm run build",
  "outputDirectory": "build",
  "framework": "docusaurus",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

```json
// package.json (relevant sections)
{
  "engines": {
    "node": ">=18.0.0"
  },
  "scripts": {
    "start": "docusaurus start",
    "build": "docusaurus build",
    "serve": "docusaurus serve"
  }
}
```

**Deployment Steps**:
1. Connect GitHub repository to Vercel
2. Vercel auto-detects Docusaurus framework
3. Configure build settings (usually auto-detected)
4. Deploy (automatic on git push)

**References**:
- Vercel Docusaurus guide: https://vercel.com/docs/frameworks/docusaurus
- Docusaurus deployment: https://docusaurus.io/docs/deployment

---

### 6. Automated Accessibility Testing Tools

**Decision**: Use axe-core for CI, Lighthouse for local testing, manual testing for final validation

**Key Findings**:
- **axe-core**: Industry-standard accessibility testing library (Deque Systems)
- **pa11y**: Command-line tool built on axe-core for CI integration
- **Lighthouse CI**: Google's automated testing tool with accessibility scoring
- **Manual Testing**: Essential for edge cases not caught by automated tools

**CI Integration**:
```yaml
# .github/workflows/accessibility.yml
name: Accessibility Tests
on: [push, pull_request]
jobs:
  a11y:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: 18
      - run: npm ci
      - run: npm run build
      - run: npm run serve &
      - run: npx wait-on http://localhost:3000
      - run: npm run a11y-test
```

```json
// package.json scripts
{
  "scripts": {
    "a11y-test": "pa11y-ci --sitemap http://localhost:3000/sitemap.xml"
  }
}
```

**References**:
- axe-core: https://github.com/dequelabs/axe-core
- pa11y: https://pa11y.org/

---

### 7. Link Checking and Validation Tools for Static Sites

**Decision**: Use linkinator for fast, reliable link checking in CI and local development

**Key Findings**:
- **linkinator**: Google's link checker, fast and supports various URL patterns
- **markdown-link-check**: Check Markdown files for broken links before build
- **broken-link-checker**: Comprehensive crawler for deployed sites
- **Custom Script**: Lightweight bash script for basic validation

**Implementation Approach**:
```bash
#!/bin/bash
# scripts/link-check.sh
set -e

echo "🔍 Checking links in built site..."

# Start local server
npm run serve &
SERVER_PID=$!
sleep 5

# Run link checker
npx linkinator http://localhost:3000 --recurse --skip "linkedin.com|twitter.com"

# Kill server
kill $SERVER_PID

echo "✅ All links validated"
```

```json
// package.json scripts
{
  "scripts": {
    "link-check": "bash scripts/link-check.sh",
    "link-check:markdown": "find docs -name '*.md' -exec markdown-link-check {} \\;"
  }
}
```

**CI Integration**:
```yaml
# .github/workflows/link-check.yml
name: Link Check
on: [push, pull_request]
jobs:
  links:
    runs-on: ubuntu-22.04
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
      - run: npm ci
      - run: npm run build
      - run: npm run link-check
```

**References**:
- linkinator: https://github.com/JustinBeckwith/linkinator
- markdown-link-check: https://github.com/tcort/markdown-link-check

---

## Summary of Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| Static Site Generator | Docusaurus 3.x | Best-in-class for technical docs, strong accessibility |
| Content Format | MDX + Markdown | Interactive components when needed, simplicity otherwise |
| Accessibility | WCAG 2.1 AA compliance | Legal requirement, ethical imperative, automated + manual testing |
| Python Dependencies | conda + pip | System-level + Python packages, reproducible environments |
| Deployment | Vercel zero-config | Simplest deployment, automatic previews, fast CDN |
| Accessibility Testing | axe-core + pa11y | Industry standard, CI-friendly, comprehensive coverage |
| Link Validation | linkinator | Fast, reliable, supports recursion and URL filtering |

---

## Open Questions / Risks

1. **Content Creation Bandwidth**: Writing 15,000-20,000 words of high-quality educational content is time-intensive. Mitigation: Start with module outlines and incrementally expand.

2. **Diagram Tool Selection**: Should we use Mermaid (code-based, version-controllable) or draw.io (GUI, easier for non-technical contributors)? Recommendation: Start with Mermaid for flowcharts, use draw.io/Figma for complex architectural diagrams.

3. **GPU Example Testing**: How to validate GPU-required examples in CI without GPU runners? Recommendation: Mock GPU operations in CI, document manual testing requirements in README.

4. **Conda in CI**: Conda can be slow in CI/CD. Mitigation: Use mamba (faster conda alternative) or cache conda environments.

---

## Next Steps

1. ✅ Research complete
2. **Phase 1**: Create data-model.md defining content entities
3. **Phase 1**: Create contracts/ with templates and schemas
4. **Phase 1**: Create quickstart.md for developer onboarding
5. **Phase 1**: Run agent context update script

---

**Research Phase Status**: COMPLETE
**Ready for Phase 1**: YES
