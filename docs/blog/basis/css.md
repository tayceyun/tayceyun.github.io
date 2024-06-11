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

## BFC

### 概念

块级格式化上下文，是一个独立的渲染区域，让处于 BFC 内部的元素与外部的元素相互隔离，使内外元素的定位不会相互影响。

### 触发条件

- 根元素
- `position:absolute / fixed`
- `display:inline-block / table`
- `float`
- `overflow !== visible`

### 规则

- 属于同一个 BFC 的两个相邻 Box 垂直排列
- 属于同一个 BFC 的两个相邻 Box 的 margin 会发生重叠
- BFC 中子元素的 margin box 的左边，与包含块(BFC) border box 的左边相接触(子元素 absolute 除外)
- BFC 的区域不会与 float 的元素区域重叠
- 计算 BFC 的高度时，浮动子元素也参与计算
- 文字层不会被浮动层覆盖，环绕于周围

### 应用

- 阻止 margin 重叠
- 可以包含浮动元素--清除内部浮动(清除浮动的原理是两个 div 都位于同个 BFC 区域之中)
- 自适应两栏布局可以阻止元素被浮动元素覆盖

## 层叠上下文

元素提升为一个比较特殊的图层，在三维空间中 (z 轴) 高出普通元素一等。层叠等级就是层叠上下文在 z 轴上的排序

![](/images/css/z-index.png)

## css 选择器权重

!important > 内联样式 = 外联样式 > ID 选择器 > class 选择器 = 伪类选择器 = 属性选择器 > 元素选择器 = 伪元素选择器 > 通配选择器 = 后代选择器 = 兄弟选择器

注意：在同一级别:后写的会覆盖先写的。

css 选择器的解析原则:选择器定位 DOM 元素是**从右往左**的方向，这样可以尽早的过滤掉一些不必要的样式规则和元素。

## css3 新特性

- transition：过渡
- transform：旋转、缩放、移动或倾斜
- animation：动画
- gradient：渐变
- box-shadow：阴影
- border-radius：圆角
- word-break： normal|break-all|keep-all;文字换行(默认规则|单词也可以换行|只在半角空格或连字符换行)
- text-overflow：文字超出部分处理
- text-shadow：水平阴影，垂直阴影，模糊的距离，以及阴影的颜色。
- box-sizing：content-box|border-box 盒模型
- 媒体查询 @media screen and(max-width:968px){}还有打印 print

transition 和 animation 的区别：

animation 和 transition 大部分属性是相同的，他们都是随时间改变元素的属性值，他们的主要区别是 transition 需要触发一个事件才能改变属性，而 animationion 需要触发任何事件的情况下才会随时间改变属性值，并且 transition 为 2 帧，从 from....to，而 animation 可以一帧一帧的。
