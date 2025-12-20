// @ts-check
import {themes as prismThemes} from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Physical AI & Humanoid Robotics Textbook',
  tagline: 'A comprehensive guide to embodied artificial intelligence',
  favicon: 'img/favicon.ico',

  future: {
    v4: true,
  },

  url: 'https://book-writing-physical-ai-humanoid-r.vercel.app',
  baseUrl: '/',

  organizationName: 'junaidkhen',
  projectName: 'Book-Writing-Physical-AI-Humanoid-Robotics',

  onBrokenLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  // ✅ MUST be top-level
  customFields: {
    apiBaseUrl: process.env.REACT_APP_API_URL || 'http://localhost:8000',
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.js',
          editUrl:
            'https://github.com/junaidkhen/Book-Writing-Physical-AI-Humanoid-Robotics/edit/main/docs/',
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      },
    ],
  ],

  themeConfig: {
    image: 'img/docusaurus-social-card.jpg',
    colorMode: {
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'Physical AI & Humanoid Robotics',
      logo: {
        alt: 'Physical AI & Humanoid Robotics Textbook Logo',
        src: 'img/logo.svg',
      },
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'tutorialSidebar',
          position: 'left',
          label: 'Textbook',
        },
        {
          to: '/docs/intro',
          label: 'Introduction',
          position: 'left',
        },
        {
          href: 'https://github.com/junaidkhen/Book-Writing-Physical-AI-Humanoid-Robotics',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Textbook',
          items: [
            { label: 'Introduction', to: '/docs/intro' },
            { label: 'Module 1: Foundations', to: '/docs/module-1/week-01-foundations' },
            { label: 'Module 2: Physics & Interaction', to: '/docs/module-2/week-06-physics' },
          ],
        },
        {
          title: 'Resources',
          items: [{ label: 'Docusaurus', href: 'https://docusaurus.io' }],
        },
        {
          title: 'More',
          items: [{ label: 'GitHub', href: 'https://github.com/facebook/docusaurus' }],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Physical AI & Humanoid Robotics Textbook.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  },
};

export default config;
