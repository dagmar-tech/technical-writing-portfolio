// @ts-check

import {themes as prismThemes} from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Technical writing portfolio',
  tagline: 'Clear documentation that helps people get things done',

  future: {
    v4: true,
  },

  url: 'https://dagmar-tech.github.io',
  baseUrl: '/technical-writing-portfolio/',

  organizationName: 'dagmar-tech',
  projectName: 'technical-writing-portfolio',

  onBrokenLinks: 'throw',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          path: '..',
          include: [
            'tutorials/releasing-a-versioned-phrasebook-package.md',
            'projects/outdated-reference-finder/README.md',
          ],
          sidebarPath: './sidebars.js',
        },

        blog: false,

        theme: {
          customCss: './src/css/custom.css',
        },
      },
    ],
  ],

  themeConfig: {
    colorMode: {
      respectPrefersColorScheme: true,
    },

    navbar: {
      title: 'Technical writing portfolio',
      items: [
        {
          type: 'docSidebar',
          sidebarId: 'portfolioSidebar',
          position: 'left',
          label: 'Samples',
        },
        {
          href: 'https://github.com/dagmar-tech/technical-writing-portfolio',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },

    footer: {
      style: 'dark',
      links: [
        {
          title: 'Portfolio',
          items: [
            {
              label: 'GitHub repository',
              href: 'https://github.com/dagmar-tech/technical-writing-portfolio',
            },
          ],
        },
      ],
      copyright: `Copyright © ${new Date().getFullYear()} Dagmar Mikmekova.`,
    },

    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  },
};

export default config;
