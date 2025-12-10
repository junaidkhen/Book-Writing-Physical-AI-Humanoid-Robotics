// @ts-check

// This runs in Node.js - Don't use client-side code here (browser APIs, JSX...)

/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.

 Create as many sidebars as you want.

 @type {import('@docusaurus/plugin-content-docs').SidebarsConfig}
 */
const sidebars = {
  // By default, Docusaurus generates a sidebar from the docs folder structure
  tutorialSidebar: [
    {
      type: 'category',
      label: 'Introduction',
      items: ['intro'],
      link: {
        type: 'doc',
        id: 'intro',
      },
    },
    {
      type: 'category',
      label: 'Module 1: Foundations',
      collapsible: true,
      collapsed: false,
      items: [
        'module-1/week-01-foundations',
        'module-1/week-02-sensing',
        'module-1/week-03-motor-control',
        'module-1/week-04-perception',
        'module-1/week-05-digital-twin',
        'module-1/summary',
      ],
    },
    {
      type: 'category',
      label: 'Module 2: Physics & Interaction',
      collapsible: true,
      collapsed: false,
      items: [
        'module-2/week-06-physics',
        'module-2/week-07-hri',
        'module-2/summary',
      ],
    },
    {
      type: 'category',
      label: 'Module 3: Vision & Navigation',
      collapsible: true,
      collapsed: false,
      items: [
        'module-3/week-08-vision',
        'module-3/week-09-mapping',
        'module-3/week-10-navigation',
        'module-3/summary',
      ],
    },
    {
      type: 'category',
      label: 'Module 4: Kinematics & Decision-Making',
      collapsible: true,
      collapsed: false,
      items: [
        'module-4/week-11-kinematics',
        'module-4/week-12-decisions',
        'module-4/week-13-system',
        'module-4/summary',
        'module-4/conclusion',
      ],
    },
  ],
};

export default sidebars;
