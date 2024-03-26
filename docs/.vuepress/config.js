module.exports = {
  title: "tayce's library", // 网站标题
  description: '移动的图书馆', // 网站描述
  head: [
    ['link', { rel: 'icon', href: '/logo.jpg' }] // meta
  ],
  themeConfig: {
    logo: '/logo.jpg',
    nav: [
      // target: '_blank'/_self； link: ''：外链
      { text: 'Home', link: '/' },
      {
        text: 'Work record',
        link: '/blog/work/'
      },
      {
        text: 'Framework',
        items: [
          { text: 'vue', link: '/blog/framework/' }
          //   { text: 'react', link: '/language/english/' },
          //   { text: 'electron', link: '/language/english/' },
          //   { text: 'native wx', link: '/language/english/' }
        ]
      }
      //   {
      //     text: 'Category-Tech',
      //     items: [
      //       {
      //         text: 'basis'
      //         // items: [
      //         //   { text: 'html', link: '/language/english/' },
      //         //   { text: 'css', link: '/language/english/' },
      //         //   { text: 'javascript', link: '/language/english/' }
      //         // ]
      //       }
      //       //   {
      //       //     text: 'others'
      //       //     // items: [
      //       //     //   { text: 'typescript', link: '/language/english/' },
      //       //     //   { text: 'node', link: '/language/english/' },
      //       //     //   { text: 'webpack', link: '/language/english/' },
      //       //     //   { text: 'git', link: '/language/english/' }
      //       //     //   { text: 'algorithm', link: '/language/english/' }
      //       //     // ]
      //       //   }
      //     ]
      //   }
    ],
    sidebar: {
      '/blog/work/': ['', ['plate', '细究touch事件'], 'work']
    },
    sidebarDepth: 3
  },
  plugins: []
};
