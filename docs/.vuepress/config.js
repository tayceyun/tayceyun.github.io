module.exports = {
  title: "tayce's library", // 网站标题
  description: '移动的图书馆', // 网站描述
  head: [
    ['link', { rel: 'icon', href: '/images/logo.jpg' }], // meta
    ['link', { rel: 'stylesheet', href: '/styles/index.css' }] // 样式
  ],
  themeConfig: {
    nav: [
      { text: '🏠 Home', link: '/' },
      { text: '💬 All', link: '/blog/linklist/' }
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
      ],
      '/blog/linklist/': [
        ['/blog/others/leak', '内存泄漏的排查过程'],
        ['/blog/others/ts', 'ts'],
        ['/blog/others/scss', 'scss / less'],
        ['/blog/others/node', 'node'],
        ['/blog/others/git', 'git'],
        ['/blog/others/algorithm', '算法基础'],
        ['/blog/others/webpack', 'vite / webpack'],
        ['/blog/framework/vue', 'vue'],
        ['/blog/framework/react', 'react'],
        ['/blog/framework/native-wx', '小程序原生开发'],
        ['/blog/framework/electron', 'electron'],
        ['/blog/basis/html', 'html'],
        ['/blog/basis/css', 'css'],
        ['/blog/basis/js', 'js']
      ]
    },
    sidebarDepth: 3
  },
  plugins: []
};
