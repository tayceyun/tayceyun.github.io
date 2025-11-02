---
sidebar: auto
tag:
  - scss
---

## css 预处理器

### 了解 scss 和 sass

scss(sassy css)是 sass（(Syntactically Awesome Stylesheets)的改良版本，scss 和 sass 存在着一些区别：

- 语法

> sass 使用缩进来表示代码块，类似于 Python。它使用缩进和换行符来区分不同的代码块。

```sass
$border-color:#aaa; //声明变量
.container
  $border-width:1px;
  border:$border-width solid $border-color; //使用变量
```

> scss 使用更类似于传统 css 的语法，使用花括号 `{}` 和分号 ; 来分隔代码块，因此 scss 更兼容传统的 css 语法。

```scss
$border-color: #aaa; //声明变量
.container {
  $border-width: 1px;
  border: $border-width solid $border-color; //使用变量
}
```

- 文件扩展名不同

> sass 文件使用 .sass 扩展名。
>
> scss 文件使用 .scss 扩展名。

## scss 使用

### 公共变量

```scss
$primary-color: #5c5d9c;

body {
  color: $primary-color;
}
```

### `!global` 声明

变量支持块级作用域，嵌套规则内定义的变量只能在嵌套规则内使用（局部变量），不在嵌套规则内定义的变量则可在任何地方使用（全局变量）。

将局部变量转换为全局变量可以添加 !global 声明：

```scss
#main {
  $width: 5em !global;
  width: $width;
}
```

### `:global(.className)`语法

在 react 项目中，如果想让样式仅作用于某个组件，不影响全局，通常将样式文件进行模块化（打包后每个 class 名都会被编译成哈希字符串）。

使用:global(.className)的语法，可以声明**全局规则**。凡是这样声明的 class，都不会被编译成哈希字符串。

```scss
.main {
  width: 100px;
  :global {
    .ant-popover-title{
        color: red;
    }
  }

// 编译后
.main__3D0Xe`{ width: 100px; }`

.main__3D0Xe .ant-popover-title{
    color: red;
}
```

### 嵌套语法

SASS 允许开发人员以嵌套的方式使用 CSS，但是过度的使用嵌套会让产生的 CSS 难以维护。

### 运算

SASS 提供了标准的算术运算符，例如+、-、\*、/、%。

示例

```scss
p {
  $font-size: 12px;
  $line-height: 30px;
  font: #`{$font-size}`/#`{$line-height}`;
}
```

### 【导入】@import

- 如果文件拓展名为 .scss 或 .sass

```scss
@import 'foo.scss';
// 或
// @import 'foo';
// 同时导入多个文件
// @import "rounded-corners", "text-shadow";
```

- 特殊情况：在以下情况下，@import 仅作为普通的 CSS 语句，不会导入任何 Sass 文件
  - 文件拓展名是 .css；
  - 文件名以 http:// 开头；
  - 文件名是 url()；
  - @import 包含 media queries。
- 不能通过变量动态导入 Sass 文件，只能作用于 CSS 的 url() 导入

```scss
$family: unquote('Droid+Sans');
@import url('http://fonts.googleapis.com/css?family=\#`{$family}`');
```

### 【继承】@extend

示例

```scss
.tag-common {
  display: inline-block;
  width: $width;
  height: $height;
  background-color: lightblue;
  text-align: center;
}

.tag-wrap {
  // 使用@extend来继承.tag-common类
  span {
    @extend .tag-common;
  }
}
```

#### 可使用占位符 `%`

注意 ⚠️：当占位符选择器单独使用时（未通过 @extend 调用），**不会编译到 CSS 文件中**。

```scss
%message-common {
  border: 1px solid #ccc;
  padding: 10px;
}

.message {
  @extend %message-common;
}
```

#### 原理：将重复使用的样式延伸 (extend) 给需要包含这个样式的特殊样式

示例

```scss
.error {
  border: 1px #f00;
  background-color: #fdd;
}
.error.intrusion {
  background-image: url('/image/hacked.png');
}
.seriousError {
  @extend .error;
  border-width: 3px;
}

// 编译后
.error,
.seriousError {
  border: 1px #f00;
  background-color: #fdd;
}

.error.intrusion,
.seriousError.intrusion {
  background-image: url('/image/hacked.png');
}

.seriousError {
  border-width: 3px;
}
```

### 【混入】@mixin & @include

如果样式在多页面复用且样式值可能存在差异，可用 `@mixin` 来书写公共样式,使用`@include xxx()`来调用。

示例

```scss
@mixin tagStyle($selector, $textColor, $bgColor) {
  .#`{$selector}` {
    color: $textColor;
    background-color: $bgColor;
  }
}

.tag-wrap {
  @include tagStyle('tag1', pink, #3070b4);
}
```

#### 可用于添加浏览器兼容性前缀

```scss
@mixin prefix($property, $value) {
  -webkit-#`{$property}`: $value; // 谷歌
  -moz-#`{$property}`: $value; // 火狐
  #`{$property}`: $value;
}

@mixin radius($value) {
  @include prefix(border-radius: $value);
}

div {
  @include radius(10px);
}
```

### 【引用】@use

示例

```scss
@use 'sass:math';

.calc-width {
  width: math.div($width, 2); // 除以2,width:50px
  height: $height + 20px;
  background-color: #3070b4;
}
```

### 【逻辑判断】@if & @else if & @else

示例

```scss
@mixin setColor($class) {
  @if ($class == 'success') {
    color: green;
    border: 1px solid green;
  } @else if ($class == 'error') {
    color: red;
    border: 1px solid red;
  } @else {
    color: orange;
    border: 1px solid orange;
  }
}
```

### 【函数】@function

示例

```scss
@function calc-with($width) {
  @return $width + 30px;
}

.if-wrap {
  width: calc-with(20px); // 调用函数
}
```

### 【遍历】@each

示例

```scss
// 官方示例
@each $animal in puma, sea-slug, egret, salamander {
  .#`{$animal}`-icon {
    background-image: url('/images/#`{$animal}`.png');
  }
}

// 示例二
@each $tagName, $textColor, $bgColor in ('tag1', red, #bf6b97), (
    'tag2',
    pink,
    #3070b4
  ), ('tag3', blue, #f5f5f5)
{
  .#`{$tagName}` {
    color: $textColor;
    background-color: $bgColor;
  }
}
```

## less 使用

### 公共变量

```less
@primary-color: #5c5d9c;
```

### CSS @namespace

@namespace 是用来定义使用在 CSS 样式表中的 XML 命名空间的@规则。定义的命名空间可以把通配、元素和属性选择器限制在指定命名空间里的元素。

任何 @namespace 规则都必须在所有的 @charset 和 @import 规则之后, 并且在样式表中，位于其他任何 style declarations 之前。

可用于定义命名空间前缀，示例：

```less
@namespace: xxx;

// 转义
@prefix-cls: ~'@`{namespace}`-basic-table';

.@`{prefix-cls}` {
  .ant-table-body {
    overflow-y: auto;
  }
}
```

### 命名空间

官网示例：假设你想要在 #bundle 下捆绑一些混合（mixins） 和变量，以供以后重用或分发

```less
#bundle() {
  .button {
    background-color: grey;
    &:hover {
      background-color: white;
    }
  }
  .tab {
    ...;
  }
}
```

在 #header a 中混入 .button 类:

```less
#header a {
  color: orange;
  #bundle.button(); // 也可以写成 #bundle > .button
}
```

### 【混合】Mixin

示例

```less
// 参数 + 默认值
.container(@width:50px,@height:50px) {
  width: @w;
  height: @h;
  background-color: red;
}
.box {
  .container(100px,100px);
}
```

### 【转义】Escaping

转义（Escaping）允许你将任何任意字符串用作属性或变量值。~"anything" 或 ~'anything' 中的任何内容都会原样使用，除了 插值(`@`{variable}``)。

```less
@min768: ~'(min-width: 768px)';
.element {
  @media @min768 {
    font-size: 1.2rem;
  }
}
```

### 【映射】Maps

示例

```less
#colors() {
  primary: blue;
  secondary: green;
}

.button {
  color: #colors[primary];
  border: 1px solid #colors[secondary];
}
```

### 【函数】Functions

详见[Less 函数手册](https://less.xiniushu.com/functions/logical-functions)
