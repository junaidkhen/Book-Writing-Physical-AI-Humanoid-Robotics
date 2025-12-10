# Frontmatter Template

Use this template for all module content pages.

```yaml
---
title: "Your Page Title"
sidebar_label: "Short Label"
sidebar_position: 1
description: "Brief description of the page content"
keywords: [keyword1, keyword2, keyword3]
---
```

## Field Descriptions

- **title**: The full page title displayed at the top (required)
- **sidebar_label**: Shorter label shown in sidebar navigation (optional, defaults to title)
- **sidebar_position**: Numeric order in sidebar (1, 2, 3, etc.) (required)
- **description**: Brief summary for SEO and previews (optional but recommended)
- **keywords**: Array of relevant keywords for search and SEO (optional)

## Example

```yaml
---
title: "Sensor Fusion Techniques"
sidebar_label: "Sensor Fusion"
sidebar_position: 2
description: "Learn how to combine data from multiple sensors for robust robotic perception"
keywords: [sensors, fusion, kalman-filter, perception, robotics]
---
```
