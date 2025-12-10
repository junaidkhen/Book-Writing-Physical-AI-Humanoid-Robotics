# Data Model: Physical AI & Humanoid Robotics Textbook

**Feature**: 001-ai-robotics-textbook
**Date**: 2025-12-10
**Phase**: Phase 1 - Design

## Overview

This document defines the content entities, their structure, relationships, and validation rules for the Physical AI & Humanoid Robotics textbook. Since this is a static documentation site, the "data model" refers to the structure of content files, metadata schemas, and validation contracts.

---

## Entity Definitions

### Entity 1: Module

**Description**: A learning unit representing one of four major topics in Physical AI and Humanoid Robotics.

**Location**: `docs/module-{n}/`

**Structure**:
```
docs/module-1/
├── _category_.json          # Sidebar configuration
├── introduction.md          # Module overview (500-800 words)
├── section-1.md             # Core concept 1 (1000-1500 words)
├── section-2.md             # Core concept 2 (1000-1500 words)
├── section-3.md             # Core concept 3 (1000-1500 words)
└── summary.md               # Module summary (500-800 words)
```

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| module_id | integer | 1-4 | Unique module identifier |
| title | string | required | Human-readable module name |
| sidebar_position | integer | 1-4 | Order in sidebar navigation |
| word_count_target | range | Module 1: 4000-5000<br>Module 2: 3500-4500<br>Module 3: 4000-5000<br>Module 4: 3500-4500 | Total words across all sections |
| diagram_count | integer | >= 3 | Minimum diagrams per module |
| example_count | integer | exactly 5 | Code examples per module |
| sections | array | 3-5 sections | Learning sections within module |

**Frontmatter Schema**:
```yaml
---
title: "Physical AI Foundations"
sidebar_label: "Module 1"
sidebar_position: 1
description: "Introduction to Physical AI concepts, sensor systems, and embodied intelligence"
keywords: [physical ai, robotics, sensors, perception]
---
```

**Validation Rules**:
- Total word count (all .md files in module) must be within target range
- Must contain at least 3 diagrams (referenced in Markdown)
- Must have exactly 5 associated code examples
- All internal links must resolve
- All images must have alt text
- Heading hierarchy must be valid (no skipped levels)

**Relationships**:
- Has Many: Sections (3-5 per module)
- Has Many: Diagrams (minimum 3 per module)
- Has Many: Code Examples (exactly 5 per module)

---

### Entity 2: Section

**Description**: A focused learning topic within a module, covering one specific concept.

**Location**: `docs/module-{n}/{section-name}.md`

**Structure**: Single Markdown file with frontmatter

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| section_id | string | kebab-case | Unique identifier within module |
| title | string | required | Section heading |
| sidebar_position | integer | required | Order within module |
| word_count | integer | 500-1500 | Words in this section |
| learning_objectives | array | 2-5 items | What students will learn |
| diagrams | array | optional | Associated diagrams |
| code_references | array | optional | Related code examples |

**Frontmatter Schema**:
```yaml
---
title: "Sensor Fusion Techniques"
sidebar_position: 2
description: "Combining data from multiple sensors for robust perception"
---
```

**Content Structure**:
```markdown
# Sensor Fusion Techniques

## Learning Objectives

By the end of this section, you will:
- Understand Kalman filter fundamentals
- Implement basic sensor fusion algorithms
- Apply fusion techniques to robotic perception

## Introduction

[Content...]

## Core Concepts

### Kalman Filtering

[Content...]

![Kalman Filter Architecture](../../diagrams/module-1/kalman-filter.svg)
*Figure 1.2: Kalman filter prediction-update cycle*

### Multi-Sensor Integration

[Content...]

:::tip Practical Application
See [Example 2: Sensor Fusion](../../code/module-1/example-02) for hands-on implementation.
:::

## Summary

[Content...]

## Further Reading

- [Resource 1]
- [Resource 2]
```

**Validation Rules**:
- Word count must be between 500-1500 words
- Must have 1-3 heading levels (h1, h2, h3)
- All image references must exist
- All code example references must exist
- No broken links

**Relationships**:
- Belongs To: Module (1 parent)
- References: Diagrams (0-many)
- References: Code Examples (0-many)

---

### Entity 3: Code Example

**Description**: A runnable Python script demonstrating Physical AI concepts with full dependency management.

**Location**: `code/module-{n}/example-{nn}-{name}/`

**Structure**:
```
code/module-1/example-01-basic-perception/
├── main.py              # Primary Python script
├── utils.py             # Supporting modules (optional)
├── environment.yaml     # Conda environment specification
├── requirements.txt     # Python package dependencies
├── test.sh              # Execution script
├── README.md            # Example documentation
└── output/              # Expected outputs (optional)
```

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| example_id | string | module-{n}-example-{nn} | Unique identifier |
| module_id | integer | 1-4 | Parent module |
| title | string | required | Human-readable name |
| description | string | required | Brief explanation (1-2 sentences) |
| difficulty | enum | beginner\|intermediate\|advanced | Complexity level |
| requires_gpu | boolean | default: false | GPU requirement flag |
| python_version | string | "3.8", "3.9", "3.10", "3.11" | Supported Python versions |
| dependencies | array | required | List of Python packages |
| estimated_runtime | string | e.g., "< 1 minute", "5-10 minutes" | Execution time |

**Metadata Schema** (in `examples/meta.yaml`):
```yaml
examples:
  - id: "module-1-example-01"
    module: 1
    title: "Basic Object Detection with OpenCV"
    description: "Detect objects in images using pre-trained deep learning models"
    difficulty: "beginner"
    gpu: false
    estimated_runtime: "< 1 minute"
    tags: ["computer-vision", "opencv", "detection"]

  - id: "module-2-example-03"
    module: 2
    title: "Real-Time Robot Localization"
    description: "Implement particle filter for robot pose estimation"
    difficulty: "intermediate"
    gpu: true
    estimated_runtime: "5-10 minutes"
    tags: ["localization", "particle-filter", "slam"]
```

**File Requirements**:

**environment.yaml**:
```yaml
name: module-1-example-01
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

**requirements.txt**:
```
opencv-python==4.8.1.78
numpy==1.24.3
matplotlib==3.8.2
```

**test.sh**:
```bash
#!/bin/bash
set -e

ENV_NAME="module-1-example-01"

# Check if conda is installed
if ! command -v conda &> /dev/null; then
    echo "❌ Conda not found. Please install Miniconda or Anaconda."
    exit 1
fi

# Create environment if it doesn't exist
if ! conda env list | grep -q "$ENV_NAME"; then
    echo "📦 Creating conda environment..."
    conda env create -f environment.yaml
fi

# Activate and run
echo "🚀 Running example..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate "$ENV_NAME"
python main.py

echo "✅ Example completed successfully"
```

**main.py** (must include):
```python
"""
Module 1 Example 01: Basic Object Detection

This example demonstrates object detection using OpenCV and pre-trained models.
Students will learn how to load models, process images, and visualize results.
"""

import cv2
import numpy as np
from typing import List, Tuple

def detect_objects(image_path: str) -> List[Tuple[str, float]]:
    """
    Detect objects in an image using a pre-trained model.

    Args:
        image_path: Path to input image

    Returns:
        List of (class_name, confidence) tuples

    Raises:
        FileNotFoundError: If image file doesn't exist
    """
    try:
        # Implementation with error handling
        pass
    except Exception as e:
        print(f"Error: {e}")
        raise

if __name__ == "__main__":
    # Example usage
    results = detect_objects("sample_image.jpg")
    print(f"Detected {len(results)} objects")
```

**Validation Rules**:
- All files (main.py, environment.yaml, requirements.txt, test.sh, README.md) must exist
- test.sh must be executable (chmod +x)
- test.sh must run without errors on Ubuntu 22.04 headless
- All code comments must be in English
- All functions must have type hints
- All functions must have basic error handling (try/except or validation)
- README.md must document setup and usage
- If gpu: true in metadata, must clearly indicate GPU requirement in README

**Relationships**:
- Belongs To: Module (1 parent)
- Has Metadata In: examples/meta.yaml
- Referenced By: Sections (0-many)

---

### Entity 4: Diagram

**Description**: A visual illustration (SVG or PNG) supporting learning content with accessibility metadata.

**Location**: `diagrams/module-{n}/{diagram-name}.svg` or `.png`

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| diagram_id | string | kebab-case | Unique identifier |
| module_id | integer | 1-4 | Parent module |
| filename | string | required | File name with extension |
| format | enum | svg\|png | Image format (SVG preferred) |
| alt_text | string | required, 50-200 chars | Descriptive alternative text |
| caption | string | required | Figure caption for reference |
| width | integer | optional | Display width in pixels |
| height | integer | optional | Display height in pixels |

**Metadata Schema** (in `diagrams/meta.yaml`):
```yaml
diagrams:
  - id: "ai-perception-pipeline"
    module: 1
    filename: "ai-perception-pipeline.svg"
    format: "svg"
    alt_text: "Flowchart showing AI perception pipeline: sensors capture data, preprocessing filters noise, feature extraction identifies patterns, and classification outputs object labels"
    caption: "Figure 1.1: End-to-end AI perception pipeline for robotic systems"
    tags: ["perception", "architecture", "pipeline"]

  - id: "kalman-filter-cycle"
    module: 1
    filename: "kalman-filter-cycle.svg"
    format: "svg"
    alt_text: "Circular diagram showing Kalman filter two-phase cycle: prediction phase uses system model, update phase incorporates measurements"
    caption: "Figure 1.2: Kalman filter prediction-update cycle"
    tags: ["kalman-filter", "estimation", "sensors"]
```

**Usage in Markdown**:
```markdown
![Flowchart showing AI perception pipeline: sensors capture data, preprocessing filters noise, feature extraction identifies patterns, and classification outputs object labels](../../diagrams/module-1/ai-perception-pipeline.svg)

*Figure 1.1: End-to-end AI perception pipeline for robotic systems*
```

**Validation Rules**:
- File must exist at specified path
- Alt text must be descriptive (not just filename)
- Alt text length must be 50-200 characters
- Caption must be provided
- SVG format preferred over PNG
- If PNG, resolution must be minimum 800px width
- All diagrams must be referenced in at least one section

**Relationships**:
- Belongs To: Module (1 parent)
- Referenced By: Sections (1-many)

---

### Entity 5: Verification Script

**Description**: Automated validation script ensuring content quality and completeness.

**Location**: `scripts/{script-name}.{sh|py}`

**Types**:

1. **verify.sh** (comprehensive validation)
   - Runs all other validation scripts
   - Reports overall pass/fail status
   - Outputs summary of issues

2. **check-wordcount.py** (word count validation)
   - Counts words in all module Markdown files
   - Validates against target ranges
   - Reports per-module and total counts

3. **link-check.sh** (link validation)
   - Checks all internal links
   - Validates external links (with retry)
   - Reports broken links

**Attributes**:

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| script_name | string | required | Script filename |
| language | enum | bash\|python | Implementation language |
| purpose | string | required | What the script validates |
| exit_codes | object | 0: success, 1: failure | Standard exit codes |
| inputs | array | optional | Files or directories to validate |
| outputs | string | stdout/stderr | Validation results |

**check-wordcount.py Schema**:
```python
#!/usr/bin/env python3
"""
Word Count Validator for Physical AI Textbook

Validates that each module meets word count targets:
- Module 1: 4000-5000 words
- Module 2: 3500-4500 words
- Module 3: 4000-5000 words
- Module 4: 3500-4500 words
- Total: 15000-20000 words
"""

import os
import re
from pathlib import Path
from typing import Dict

# Word count targets
TARGETS = {
    "module-1": (4000, 5000),
    "module-2": (3500, 4500),
    "module-3": (4000, 5000),
    "module-4": (3500, 4500),
}
TOTAL_TARGET = (15000, 20000)

def count_words_in_markdown(file_path: Path) -> int:
    """Count words in a Markdown file, excluding frontmatter and code blocks."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Remove frontmatter
    content = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)

    # Remove code blocks
    content = re.sub(r'```.*?```', '', content, flags=re.DOTALL)

    # Remove inline code
    content = re.sub(r'`[^`]+`', '', content)

    # Remove links
    content = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', content)

    # Remove images
    content = re.sub(r'!\[([^\]]*)\]\([^\)]+\)', '', content)

    # Count words
    words = content.split()
    return len(words)

def validate_module(module_dir: Path, min_words: int, max_words: int) -> Dict:
    """Validate word count for a single module."""
    total_words = 0
    files = []

    for md_file in module_dir.glob("*.md"):
        word_count = count_words_in_markdown(md_file)
        total_words += word_count
        files.append({"file": md_file.name, "words": word_count})

    return {
        "module": module_dir.name,
        "total_words": total_words,
        "min": min_words,
        "max": max_words,
        "valid": min_words <= total_words <= max_words,
        "files": files,
    }

def main():
    docs_dir = Path("docs")
    results = []
    total_words = 0

    # Validate each module
    for module_name, (min_w, max_w) in TARGETS.items():
        module_path = docs_dir / module_name
        if not module_path.exists():
            print(f"❌ Module not found: {module_name}")
            continue

        result = validate_module(module_path, min_w, max_w)
        results.append(result)
        total_words += result["total_words"]

        # Print result
        status = "✅" if result["valid"] else "❌"
        print(f"{status} {module_name}: {result['total_words']} words (target: {min_w}-{max_w})")

    # Validate total
    total_valid = TOTAL_TARGET[0] <= total_words <= TOTAL_TARGET[1]
    status = "✅" if total_valid else "❌"
    print(f"\n{status} Total: {total_words} words (target: {TOTAL_TARGET[0]}-{TOTAL_TARGET[1]})")

    # Exit with appropriate code
    if not all(r["valid"] for r in results) or not total_valid:
        exit(1)

    print("\n✅ All word count targets met!")
    exit(0)

if __name__ == "__main__":
    main()
```

**Validation Rules**:
- Scripts must have clear purpose and documentation
- Must return exit code 0 on success, 1 on failure
- Must provide human-readable output
- Must run on Ubuntu 22.04 without additional dependencies
- Must be executable (chmod +x for .sh files)

**Relationships**:
- Validates: Modules, Sections, Code Examples, Diagrams (all entities)

---

## Entity Relationships Diagram

```
Module (1)
  ├── Has Many (3-5) → Section
  ├── Has Many (≥3) → Diagram
  └── Has Many (5) → Code Example

Section (many)
  ├── Belongs To (1) → Module
  ├── References (0-many) → Diagram
  └── References (0-many) → Code Example

Code Example (20 total)
  ├── Belongs To (1) → Module
  ├── Has Metadata In → examples/meta.yaml
  └── Referenced By (0-many) → Section

Diagram (≥12 total)
  ├── Belongs To (1) → Module
  ├── Has Metadata In → diagrams/meta.yaml
  └── Referenced By (1-many) → Section

Verification Script (3)
  └── Validates → All Entities
```

---

## File System Organization

```
/
├── docs/
│   ├── intro.md
│   ├── module-1/
│   │   ├── _category_.json
│   │   ├── introduction.md
│   │   ├── section-1.md
│   │   └── ...
│   └── ...
│
├── diagrams/
│   ├── module-1/
│   │   ├── diagram-1.svg
│   │   └── ...
│   └── meta.yaml
│
├── code/
│   ├── module-1/
│   │   ├── example-01-{name}/
│   │   │   ├── main.py
│   │   │   ├── environment.yaml
│   │   │   ├── requirements.txt
│   │   │   ├── test.sh
│   │   │   └── README.md
│   │   └── ...
│   └── ...
│
├── examples/
│   └── meta.yaml
│
└── scripts/
    ├── verify.sh
    ├── check-wordcount.py
    └── link-check.sh
```

---

## Validation Summary

### Pre-Release Validation Checklist

- [ ] All modules have word counts within target ranges
- [ ] Total word count is between 15,000-20,000
- [ ] Each module has at least 3 diagrams
- [ ] Each module has exactly 5 code examples
- [ ] All diagrams have descriptive alt text (50-200 chars)
- [ ] All code examples run successfully via test.sh
- [ ] All internal links resolve correctly
- [ ] All external links are valid (or documented as intentionally broken)
- [ ] Accessibility audit passes WCAG 2.1 AA
- [ ] No broken images or missing files
- [ ] All code comments are in English
- [ ] All functions have type hints
- [ ] All functions have basic error handling

---

**Data Model Status**: COMPLETE
**Ready for Contracts**: YES
