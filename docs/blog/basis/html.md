---
sidebar: auto
tags:
  - html
---

## 深入了解语义化标签

### ❓ 语义化结构的页面有什么优势

语义类标签对开发者更为友好，使用语义类标签增强了可读性，即便是在没有 CSS 的时候，开发者也能够清晰地看出网页的结构，也更为便于团队的开发和维护。

除了对人类友好之外，语义类标签也十分适宜机器阅读。它的文字表现力丰富，更适合搜索引擎检索(SEO)，也可以让搜索引擎爬虫更好地获取到更多有效信息，有效提升网页的搜索量，并且语义类还可以支持读屏软件，根据文章可以自动生成目录等等。

### 常见的语义化标签

- `ul`：无序列表
- `ol`：有序列表
- `article`：文章主体
- `em`：重音
- `strong`：表示词很重要
- `abbr`：缩写
- `p`：普通段落
- `hr`：横向分隔线，表示故事走向的转变或者话题的转变
- `header`：通常出现在前部，表示导航或者介绍性的内容（header 中的导航多数是到文章自己的目录）。
- `footer`：通常出现在尾部，包含一些作者信息、相关链接、版权信息等
- `aside`：表示跟文章主体不那么相关的部分，它可能包含导航、广告等工具性质的内容（aside 中的导航多数是到关联页面或者是整站地图）。
- `address`：表示“文章(作者)的联系方式”，address 明确地只关联到 article 和 body。
- `hgroup`：避免副标题产生额外的一个层级
- `blockquote`：表示段落级引述内容
- `q`：表示行内的引述内容
- `cite`：表示引述的作品名
- `figure`：用于表示与主文章相关的图像、照片等流内容
- `figcaption`：在`figure`标签内使用，表示图片内容的标题等
- `pre`：表示这部分内容是预先排版过的，不需要浏览器进行排版。

  - 示例

  ```html
  <figure>
    <img src="https://.....440px-NeXTcube_first_webserver.JPG" />
    <figcaption>The NeXT Computer used by Tim Berners-Lee at CERN.</figcaption>
  </figure>
  ```

  - 语义化的 HTML 能够支持自动生成目录结构。h1-h6 是最基本的标题，它们表示了文章中不同层级的标题。有时候可能会有副标题，为了避免副标题产生额外的一个层级，可以使用 `hgroup` 标签。

    示例

```html
<hgroup>
  <h1>JavaScript 对象</h1>
  <h2>我们需要模拟类吗?</h2>
</hgroup>

<p>balah balah</p>
```

页面展示

![](/images/html/hgroup.png)

### 【示例】整体结构类的语义标签

```html
<body>
  <header>
    <nav>......</nav>
  </header>
  <aside>
    <nav>......</nav>
  </aside>
  <section>......</section>
  <section>......</section>
  <footer>
    <address>......</address>
  </footer>
</body>
```
