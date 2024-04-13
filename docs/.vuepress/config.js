module.exports = {
  title: "tayce's library", // 网站标题
  description: '移动的图书馆 - 速查⬇️', // 网站描述
  head: [
    ['link', { rel: 'icon', href: '/images/logo.jpg' }], // meta
    ['link', { rel: 'stylesheet', href: '/styles/index.css' }] // 样式
  ],
  themeConfig: {
    nav: [
      { text: '🏠 Home', link: '/' },
      { text: '💬 All', link: '/blog/linklist/linklist' }
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
