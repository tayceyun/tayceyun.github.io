import './styles/index.css';
import { defineUserConfig } from 'vuepress';
import recoTheme from 'vuepress-theme-reco';

export default defineUserConfig({
  title: "tayce's library",
  description: 'Just playing around',
  theme: recoTheme({
    home: '/',
    style: '@vuepress-reco/style-default',
    logo: '/head.jpg',
    author: 'tayce',
    authorAvatar: '/head.jpg',
    docsRepo: 'https://github.com/vuepress-reco/vuepress-theme-reco-next',
    docsBranch: 'main',
    docsDir: 'example',
    lastUpdatedText: '',
    navbar: [
      { text: 'Category', link: '/categories/' },
      { text: 'Tags', link: '/tags/' },
      {
        text: 'Extension',
        link: '/docs/extension'
      }
    ]
  })
});
