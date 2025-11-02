import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: "tayce's library",
  tagline: '移动的图书馆',
  favicon: 'img/logo.jpg',

  future: {
    v4: true,
  },

  // 设置你的 GitHub Pages URL
  url: 'https://tayceyun.github.io',
  baseUrl: '/',

  // GitHub pages 部署配置
  organizationName: 'tayceyun',
  projectName: 'tayceyun.github.io',
  deploymentBranch: 'gh-pages',
  trailingSlash: false,

  onBrokenLinks: 'warn',
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'zh-Hans',
    locales: ['zh-Hans'],
  },

  presets: [
    [
      'classic',
      {
        docs: {
          sidebarPath: './sidebars.ts',
          routeBasePath: 'blog', // 使用 /blog 作为文档路径
          editUrl: undefined, // 禁用编辑链接
        },
        blog: false, // 禁用默认的博客功能
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  markdown: {
    mermaid: true,
    format: 'detect', // 自动检测 md/mdx 格式
  },

  themeConfig: {
    image: 'img/orange.jpg',
    colorMode: {
      defaultMode: 'light',
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: "tayce's library",
      logo: {
        alt: 'Logo',
        src: 'img/logo.jpg',
      },
      items: [
        {
          to: '/',
          label: '💬 技术文章',
          position: 'left',
        },
      ],
    },
    footer: {
      style: 'dark',
      copyright: `Copyright © ${new Date().getFullYear()} tayce's library. Built with Docusaurus.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
      additionalLanguages: ['bash', 'python', 'javascript', 'typescript', 'jsx', 'tsx'],
    },
  } satisfies Preset.ThemeConfig,
};

export default config;

