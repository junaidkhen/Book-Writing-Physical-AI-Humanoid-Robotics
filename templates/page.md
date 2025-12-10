# Page Content Template

Use this template structure for all module content pages.

```markdown
---
title: "Your Page Title"
sidebar_position: 1
description: "Brief description"
---

# Your Page Title

## Learning Objectives

By the end of this section, you will:
- Understand [concept 1]
- Learn how to [skill 1]
- Apply [technique 1] to [use case]

## Introduction

[Brief introduction to the topic, 2-3 paragraphs explaining why it matters and what students will learn.]

## Core Concepts

### Concept 1

[Detailed explanation of the first key concept]

![Descriptive alt text](../../diagrams/module-X/diagram-name.svg)
*Figure X.Y: Caption describing the diagram*

### Concept 2

[Detailed explanation of the second key concept]

:::tip Practical Application
See [Example X: Name](../../code/module-X/example-XX) for a hands-on implementation.
:::

### Concept 3

[Detailed explanation of the third key concept]

:::note Key Insight
Important insight or best practice related to this concept.
:::

## Real-World Applications

[Examples of how these concepts are used in actual robotics systems]

- **Application 1**: Description
- **Application 2**: Description
- **Application 3**: Description

## Summary

[Brief recap of what was covered, 1-2 paragraphs reinforcing key takeaways]

## Further Reading

- [Resource title 1](URL) - Brief description
- [Resource title 2](URL) - Brief description
- [Resource title 3](URL) - Brief description

## Next Steps

Continue to [Next Section](./next-section.md) to learn about [next topic].
```

## Content Guidelines

### Word Count
- Introduction sections: 500-800 words
- Main content sections: 1000-1500 words
- Summary sections: 300-400 words

### Writing Style
- Use clear, accessible language
- Define technical terms when first introduced
- Include concrete examples
- Use active voice
- Break complex concepts into smaller subsections

### Visual Elements
- Include at least 1 diagram per main section
- Use Docusaurus admonitions (:::tip, :::note, :::warning, :::caution)
- Reference code examples where relevant
- Add figure captions for all images

### Accessibility
- All images must have descriptive alt text
- Use proper heading hierarchy (no skipped levels)
- Link text should be descriptive (not "click here")
- Maintain proper semantic structure
