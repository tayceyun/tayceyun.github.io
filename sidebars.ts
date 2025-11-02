import type {SidebarsConfig} from '@docusaurus/plugin-content-docs';

const sidebars: SidebarsConfig = {
  mainSidebar: [
    {
      type: 'category',
      label: '前端基础',
      items: [
        {
          type: 'category',
          label: 'Javascript',
          items: [
            'basis/js',
            'basis/ts',
          ],
        },
        {
          type: 'category',
          label: 'Http',
          items: [
            'others/chrome',
          ],
        },
        {
          type: 'category',
          label: 'CSS',
          items: [
            'basis/css',
            'basis/scss',
          ],
        },
        {
          type: 'category',
          label: 'Algorithm',
          items: [
            'basis/algorithm',
            'basis/question',
          ],
        },
      ],
    },
    {
      type: 'category',
      label: '前端框架',
      items: [
        'framework/vue',
        'framework/react',
        'framework/native-wx',
        'framework/electron',
        'framework/harmony',
        'others/resource',
      ],
    },
    {
      type: 'category',
      label: '工具合集',
      items: [
        'others/git',
        'others/webpack',
      ],
    },
    {
      type: 'category',
      label: '后端',
      items: [
        'backend/linux',
        'backend/node',
        'backend/sql',
        'backend/python',
        'backend/docker',
      ],
    },
    // {
    //   type: 'category',
    //   label: '工作记录',
    //   items: [
    //     'work/README',
    //     'work/internal-sales',
    //     'work/frankie',
    //     'work/NLS',
    //     'work/roche',
    //     'work/ticket',
    //     'work/expense',
    //     'work/bg',
    //   ],
    // },
    {
      type: 'category',
      label: '其他',
      items: [
        'linklist/README',
        'others/why',
        'others/interview',
        'others/leak',
        'others/axios',
        'others/vben-admin',
      ],
    },
  ],
};

export default sidebars;
