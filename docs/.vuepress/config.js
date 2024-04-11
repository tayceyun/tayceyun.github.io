module.exports = {
  title: "tayce's library", // 网站标题
  description: '移动的图书馆', // 网站描述
  head: [
    ['link', { rel: 'icon', href: '/images/logo.jpg' }], // meta
    ['link', { rel: 'stylesheet', href: '/styles/index.css' }] // 样式
  ],
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      {
        text: 'Technology',
        items: [
          {
            text: 'basis',
            items: [
              { text: 'html', link: '/blog/basis/html/' },
              { text: 'css', link: '/blog/basis/css/' },
              { text: 'javascript', link: '/blog/basis/js' }
            ]
          },
          {
            text: 'framework',
            items: [
              { text: 'vue', link: '/blog/framework/vue/' },
              { text: 'react', link: '/blog/framework/react/' },
              { text: 'electron', link: '/blog/framework/electron/' },
              { text: 'native wx', link: '/blog/framework/native-wx/' }
            ]
          },
          {
            text: 'others',
            items: [
              { text: 'typescript', link: '/blog/others/ts/' },
              { text: 'node', link: '/blog/others/node/' },
              { text: 'vite/webpack', link: '/blog/others/webpack/' },
              { text: 'git', link: '/blog/others/git/' },
              { text: 'algorithm', link: '/blog/others/algorithm/' }
            ]
          }
        ]
      }
      //   {
      //     text: 'Work',
      //     link: '/blog/work/'
      //   }
    ],
    sidebar: {
      '/blog/work/': [
        ['', '项目经历'],
        ['/blog/work/internal-sales', 'Internal Sales Project'],
        ['/blog/work/frankie', 'Frankie Project'],
        ['/blog/work/NLS', 'ASIA NLS Project'],
        ['/blog/work/roche', 'Regulatory Intelligence Project'],
        ['/blog/work/ticket', 'ticket 项目'],
        ['/blog/work/expense', '内部费用管理项目'],
        ['/blog/work/expense', '消费者bg']
      ]
    },
    sidebarDepth: 3
  },
  plugins: []
};
