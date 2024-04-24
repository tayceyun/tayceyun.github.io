---
sidebar: auto
tags:
  - css
---

## css 中的两种规则

### at rule（at 规则）

at-rule 由一个 @ 关键字和后续的一个区块组成，如果没有区块，则以分号结束。

#### @charset

用于提示 css 文件使用的字符编码方式，如果被使用，要求必须出现在最前面。该规则只在语法解析阶段前使用，并不影响页面的展示效果

`@charset "utf-8"`

#### @import

用于引入 css 文件（@charset 规则不会被引入）

```css
@import 'reset.css';
@import url('reset.css');
```

#### @media

对设备类型进行一些判断

```css
@media print {
  body {
    font-size: 10pt;
  }
}
```

#### @page

age 用于分页媒体访问网页时的表现设置，页面是一种特殊的盒模型结构，除了页面本 身，还可以设置它周围的盒。

```css
@page {
  size: 8.5in 11in;
  margin: 10%;

  @top-left {
    content: 'Hamlet';
  }

  @top-right {
    content: 'Page' counter(page);
  }
}
```

### qualified rule（普通规则）
