# Quickstart Guide: Physical AI & Humanoid Robotics Textbook

**Feature**: 001-ai-robotics-textbook
**Date**: 2025-12-10
**Audience**: Developers, content creators, contributors

## Overview

This guide provides step-by-step instructions for setting up the development environment, creating content, running verification scripts, and deploying the Physical AI & Humanoid Robotics textbook.

**Estimated Setup Time**: 15-20 minutes

---

## Prerequisites

Before starting, ensure you have:

- **Node.js 18+**: [Download](https://nodejs.org/)
- **npm 9+**: Comes with Node.js
- **Python 3.8+**: [Download](https://www.python.org/)
- **Conda or Miniconda**: [Download](https://docs.conda.io/en/latest/miniconda.html) (for code examples)
- **Git**: [Download](https://git-scm.com/)
- **Code Editor**: VS Code, Sublime Text, or similar
- **Ubuntu 22.04**: Native, WSL2, or Docker (for testing code examples)

**Optional**:
- **Vercel CLI**: For testing deployments locally
- **Docker**: For isolated testing environments

---

## Part 1: Initial Setup

### Step 1: Install Docusaurus

If you haven't already, create a new Docusaurus site in your project directory:

```bash
# Initialize Docusaurus (user does this manually)
npx create-docusaurus@latest . classic

# Or if starting from scratch
npx create-docusaurus@latest physical-ai-textbook classic
cd physical-ai-textbook
```

### Step 2: Install Dependencies

```bash
npm install
```

### Step 3: Verify Installation

Start the development server to ensure everything works:

```bash
npm start
```

Open http://localhost:3000 in your browser. You should see the default Docusaurus site.

### Step 4: Configure Docusaurus

Edit `docusaurus.config.js` for the textbook:

```javascript
// @ts-check
const lightCodeTheme = require('prism-react-renderer/themes/github');
const darkCodeTheme = require('prism-react-renderer/themes/dracula');

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'Comprehensive Educational Textbook',
  favicon: 'img/favicon.ico',

  url: 'https://your-site.vercel.app',
  baseUrl: '/',

  organizationName: 'your-org',
  projectName: 'physical-ai-textbook',

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          routeBasePath: '/',
          sidebarPath: require.resolve('./sidebars.js'),
          editUrl: 'https://github.com/your-org/physical-ai-textbook/edit/main/',
        },
        blog: false,
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      navbar: {
        title: 'Physical AI & Humanoid Robotics',
        logo: {
          alt: 'Physical AI Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'doc',
            docId: 'intro',
            position: 'left',
            label: 'Textbook',
          },
          {
            href: 'https://github.com/your-org/physical-ai-textbook',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Modules',
            items: [
              {label: 'Module 1', to: '/module-1/introduction'},
              {label: 'Module 2', to: '/module-2/introduction'},
              {label: 'Module 3', to: '/module-3/introduction'},
              {label: 'Module 4', to: '/module-4/introduction'},
            ],
          },
          {
            title: 'Resources',
            items: [
              {label: 'Code Examples', href: 'https://github.com/your-org/physical-ai-textbook/tree/main/code'},
              {label: 'Issues', href: 'https://github.com/your-org/physical-ai-textbook/issues'},
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Physical AI Textbook. Built with Docusaurus.`,
      },
      prism: {
        theme: lightCodeTheme,
        darkTheme: darkCodeTheme,
        additionalLanguages: ['bash', 'python'],
      },
    }),
};

module.exports = config;
```

### Step 5: Create Project Structure

Create the required directories:

```bash
mkdir -p docs/module-{1..4}
mkdir -p diagrams/module-{1..4}
mkdir -p code/module-{1..4}
mkdir -p examples
mkdir -p scripts
mkdir -p templates
```

---

## Part 2: Creating Content

### Creating a New Module

1. **Create Module Directory**:
   ```bash
   mkdir -p docs/module-1
   ```

2. **Add Category Configuration**:
   Create `docs/module-1/_category_.json`:
   ```json
   {
     "label": "Module 1: Physical AI Foundations",
     "position": 1,
     "link": {
       "type": "generated-index",
       "description": "Introduction to Physical AI concepts, sensor systems, and embodied intelligence."
     }
   }
   ```

3. **Create Module Content**:
   Use the module template from `specs/001-ai-robotics-textbook/contracts/module-template.md`

4. **Add Sections**:
   Create individual `.md` files for each section:
   ```bash
   touch docs/module-1/introduction.md
   touch docs/module-1/section-1.md
   touch docs/module-1/section-2.md
   ```

5. **Add Frontmatter** to each file:
   ```yaml
   ---
   title: "Physical AI Foundations"
   sidebar_position: 1
   description: "Introduction to Physical AI concepts"
   ---
   ```

### Creating Code Examples

1. **Create Example Directory**:
   ```bash
   mkdir -p code/module-1/example-01-basic-perception
   cd code/module-1/example-01-basic-perception
   ```

2. **Use Example Template**:
   Follow `specs/001-ai-robotics-textbook/contracts/example-template.md`

3. **Create Required Files**:
   ```bash
   touch main.py
   touch environment.yaml
   touch requirements.txt
   touch test.sh
   touch README.md
   ```

4. **Make test.sh Executable**:
   ```bash
   chmod +x test.sh
   ```

5. **Add Metadata**:
   Update `examples/meta.yaml` with example details

### Adding Diagrams

1. **Create Diagram**:
   - Use tools like draw.io, Figma, or Mermaid
   - Export as SVG (preferred) or PNG
   - Minimum PNG resolution: 800px width

2. **Save to Module Directory**:
   ```bash
   cp my-diagram.svg diagrams/module-1/
   ```

3. **Add Metadata**:
   Update `diagrams/meta.yaml` following the schema in `specs/001-ai-robotics-textbook/contracts/diagram-schema.yaml`

4. **Reference in Content**:
   ```markdown
   ![Descriptive alt text explaining the diagram](../../diagrams/module-1/my-diagram.svg)
   *Figure 1.1: Caption for the diagram*
   ```

---

## Part 3: Development Workflow

### Running Development Server

```bash
npm start
```

This starts a local development server at http://localhost:3000 with hot reload.

### Building the Site

```bash
npm run build
```

This generates static content in the `build/` directory.

### Serving Built Site Locally

```bash
npm run serve
```

This serves the built site at http://localhost:3000 for testing.

### Running Code Examples

```bash
cd code/module-1/example-01-basic-perception
bash test.sh
```

---

## Part 4: Verification & Validation

### Step 1: Word Count Validation

Create and run the word count checker:

```bash
python scripts/check-wordcount.py
```

Expected output:
```
✅ module-1: 4523 words (target: 4000-5000)
✅ module-2: 4102 words (target: 3500-4500)
✅ module-3: 4687 words (target: 4000-5000)
✅ module-4: 3891 words (target: 3500-4500)

✅ Total: 17203 words (target: 15000-20000)

✅ All word count targets met!
```

### Step 2: Link Validation

Create and run the link checker:

```bash
bash scripts/link-check.sh
```

This validates all internal and external links.

### Step 3: Accessibility Testing

Run accessibility audit:

```bash
npm run build
npm run serve &
npx pa11y-ci --sitemap http://localhost:3000/sitemap.xml --threshold 0
```

### Step 4: Comprehensive Verification

Run all checks:

```bash
bash scripts/verify.sh
```

This script should:
1. Check word counts
2. Validate links
3. Run accessibility tests
4. Verify diagram count
5. Verify example count
6. Check for broken images

---

## Part 5: Deployment

### Prerequisites

1. **Vercel Account**: Sign up at https://vercel.com
2. **GitHub Repository**: Push your code to GitHub
3. **Connect Repository**: Link GitHub repo to Vercel

### Deployment Steps

#### Option 1: Automatic Deployment (Recommended)

1. **Connect to Vercel**:
   - Log in to Vercel
   - Click "New Project"
   - Import your GitHub repository
   - Vercel auto-detects Docusaurus

2. **Configure Settings**:
   - Build Command: `npm run build` (auto-detected)
   - Output Directory: `build` (auto-detected)
   - Node Version: 18.x (set in package.json engines)

3. **Deploy**:
   - Click "Deploy"
   - Wait for build to complete
   - Access your site at `https://your-project.vercel.app`

#### Option 2: Manual Deployment

```bash
# Install Vercel CLI
npm install -g vercel

# Build the site
npm run build

# Deploy
vercel --prod
```

### Vercel Configuration

Create `vercel.json` in project root:

```json
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

### Environment Variables (if needed)

If your examples require API keys or configuration:

1. Create `.env.local` (NOT committed to git)
2. Add variables to Vercel dashboard:
   - Project Settings → Environment Variables
   - Add each variable with appropriate scope (Production, Preview, Development)

---

## Part 6: Troubleshooting

### Common Issues

#### Issue: Build Fails with "Module not found"

**Solution**:
```bash
rm -rf node_modules package-lock.json
npm install
npm run build
```

#### Issue: Links to Code Examples Don't Work

**Solution**: Ensure code examples are referenced correctly:
```markdown
<!-- Correct -->
[Example 1](../../code/module-1/example-01-basic-perception)

<!-- Incorrect -->
[Example 1](code/module-1/example-01-basic-perception)
```

#### Issue: Diagrams Not Displaying

**Solution**: Verify diagram paths are correct and files exist:
```bash
# Check if file exists
ls diagrams/module-1/my-diagram.svg

# Correct path in markdown
![Alt text](../../diagrams/module-1/my-diagram.svg)
```

#### Issue: Word Count Script Fails

**Solution**: Ensure Python 3.8+ is installed:
```bash
python3 --version
# If not found, install Python 3.8+
```

#### Issue: Code Example test.sh Fails

**Solution**:
1. Verify conda is installed: `conda --version`
2. Check environment.yaml syntax
3. Ensure test.sh is executable: `chmod +x test.sh`
4. Run manually to see detailed errors:
   ```bash
   bash -x test.sh
   ```

#### Issue: Vercel Deployment Fails

**Solution**:
1. Check build logs in Vercel dashboard
2. Verify Node version in package.json:
   ```json
   {
     "engines": {
       "node": ">=18.0.0"
     }
   }
   ```
3. Test build locally: `npm run build`

### Getting Help

- **Documentation Issues**: Check Docusaurus docs at https://docusaurus.io/docs
- **Code Example Issues**: Review example template in `specs/001-ai-robotics-textbook/contracts/example-template.md`
- **Deployment Issues**: Consult Vercel docs at https://vercel.com/docs
- **Project Support**: Contact via WhatsApp (see README.md)

---

## Part 7: Development Checklist

### Before Creating a Pull Request

- [ ] All modules meet word count targets
- [ ] All diagrams have descriptive alt text
- [ ] All code examples run successfully via test.sh
- [ ] No broken links in content
- [ ] Accessibility audit passes WCAG 2.1 AA
- [ ] Build completes without errors
- [ ] All verification scripts pass
- [ ] New content follows templates
- [ ] Commit messages are clear and descriptive

### Before Final Deployment

- [ ] Comprehensive verification script passes
- [ ] Manual accessibility testing with screen reader
- [ ] Cross-browser testing (Chrome, Firefox, Safari, Edge)
- [ ] Mobile responsiveness check
- [ ] All external links verified
- [ ] Metadata in examples/meta.yaml and diagrams/meta.yaml is complete
- [ ] README.md is updated with any changes
- [ ] Known issues documented
- [ ] WhatsApp contact information current

---

## Part 8: Useful Commands Reference

```bash
# Development
npm start                    # Start dev server
npm run build                # Build for production
npm run serve                # Serve built site locally
npm run clear                # Clear Docusaurus cache

# Verification
python scripts/check-wordcount.py    # Check word counts
bash scripts/link-check.sh           # Validate links
bash scripts/verify.sh               # Run all checks

# Code Examples
cd code/module-X/example-YY-name
bash test.sh                 # Run example
conda env list               # List conda environments
conda activate env-name      # Activate environment
conda deactivate             # Deactivate environment

# Git
git status                   # Check status
git add .                    # Stage changes
git commit -m "message"      # Commit changes
git push origin branch       # Push to remote

# Deployment
vercel                       # Deploy to preview
vercel --prod                # Deploy to production
vercel logs                  # View deployment logs
```

---

## Next Steps

1. ✅ **Setup Complete**: You're ready to create content
2. **Create Modules**: Start with Module 1 using the module template
3. **Add Examples**: Implement code examples for each module
4. **Create Diagrams**: Design visual aids for learning content
5. **Validate**: Run verification scripts regularly
6. **Deploy**: Push to GitHub and deploy to Vercel
7. **Iterate**: Gather feedback and improve content

---

**Quickstart Guide Version**: 1.0
**Last Updated**: 2025-12-10
**Status**: Ready for Phase 2 (Tasks)
