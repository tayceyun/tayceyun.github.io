import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import Layout from '@theme/Layout';
import Heading from '@theme/Heading';
import styles from './index.module.css';

export default function Home(): JSX.Element {
  const {siteConfig} = useDocusaurusContext();
  return (
    <Layout
      title="技术文章汇总"
      description="tayce的技术博客 - 移动的图书馆">
      <main className="container" style={{ padding: '2rem 0' }}>
        <Heading as="h1">💬 Quick list</Heading>
        <p>欢迎来到技术文章汇总页面！这里整理了所有的技术学习笔记和工作总结。</p>

        <Heading as="h2">📚 分类导航</Heading>

        <Heading as="h3">前端基础</Heading>
        <ul>
          <li><strong>Javascript</strong>: <Link to="/blog/basis/js">js知识整理,从基础到深入</Link></li>
          <li><strong>CSS</strong>: <Link to="/blog/basis/css">css知识整理,从基础到深入</Link></li>
          <li><strong>SCSS</strong>: <Link to="/blog/basis/scss">scss、less等css预处理器</Link></li>
          <li><strong>Http/浏览器</strong>: <Link to="/blog/others/chrome">http / 浏览器</Link></li>
          <li><strong>TypeScript</strong>: <Link to="/blog/others/ts">ts语法</Link></li>
          <li><strong>算法基础</strong>: <Link to="/blog/basis/algorithm">算法基础</Link></li>
          <li><strong>算法题</strong>: <Link to="/blog/basis/ques">算法题记录</Link></li>
        </ul>

        <Heading as="h3">前端框架</Heading>
        <ul>
          <li><strong>Vue3</strong>: <Link to="/blog/framework/vue">Vue3学习笔记</Link></li>
          <li><strong>React18</strong>: <Link to="/blog/framework/react">React18学习笔记</Link></li>
          <li><strong>微信小程序</strong>: <Link to="/blog/framework/native-wx">Wx native</Link></li>
          <li><strong>Electron</strong>: <Link to="/blog/framework/electron">Electron基础</Link></li>
          <li><strong>HarmonyOS</strong>: <Link to="/blog/framework/harmony">HarmonyOS基础</Link></li>
          <li><strong>源码学习</strong>: <Link to="/blog/others/resource">了解源码(Vue)</Link></li>
        </ul>

        <Heading as="h3">工具合集</Heading>
        <ul>
          <li><strong>Git</strong>: <Link to="/blog/others/git">Git使用指南</Link></li>
          <li><strong>Webpack</strong>: <Link to="/blog/others/webpack">Webpack配置与优化</Link></li>
        </ul>

        <Heading as="h3">后端技术</Heading>
        <ul>
          <li><strong>Linux</strong>: <Link to="/blog/backend/linux">Linux整理</Link></li>
          <li><strong>Node.js</strong>: <Link to="/blog/backend/node">node学习日记</Link></li>
          <li><strong>SQL</strong>: <Link to="/blog/backend/sql">sql学习</Link></li>
          <li><strong>Python</strong>: <Link to="/blog/backend/python">python语法</Link></li>
        </ul>

        <Heading as="h3">其他</Heading>
        <ul>
          <li><strong>问题总结</strong>: <Link to="/blog/others/why">❓问题聚集地🙋‍♀️</Link></li>
        </ul>
      </main>
    </Layout>
  );
}

