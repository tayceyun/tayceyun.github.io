---
sidebar: auto
tags:
  - javascript
---

## 环环相扣 💫

知识互联 💬

<el-card class="frame" shadow="always">
[**进程**](#线程和进程) ➡️
进程使用[**堆内存**](#内存) ➡️
js 的[**内存回收机制**](#内存回收) ➡️
可能出现[**内存泄漏**](#内存泄漏) ➡️
可能的原因：[**闭包**](#闭包)/定时器未被正确销毁等 ➡️
闭包本质：[**作用域链**](#作用域链)的一个特殊应用 ➡️
理解作用域链：

理解 1️⃣ ：即 [**作用域**](#作用域)嵌套的结果 ➡️ 全局/函数/块级作用域（**let const**的出现）

理解 2️⃣： 是[**执行上下文**](#执行上下文)的重要属性之一 ➡️ 执行上下文可以理解为一个对象，包含：**变量对象**、**作用域链**、[**this**](#this) ➡️ this 相关：[**call apply bind**](#改变this指向)（es6） / **箭头函数**

理解 3️⃣ ：作用域链决定了变量的访问范围，[**原型链**](#原型链)决定了对象之间的继承关系

</el-card>

<el-card class="frame" shadow="always">
线程 ➡️

1️⃣ 线程使用栈内存 ➡️
可能出现[**栈溢出**](#栈溢出) ➡️
可能的原因：**递归**终止条件不正确/函数嵌套调用过深 ➡️
递归的优化：**尾递归**

2️⃣ js 是单线程 ➡️

1.**eventloop** 机制（事件循环机制）➡️ 同步/异步任务 ➡️ 异步任务分为**宏任务**/**微任务** ➡️ 微任务主要包括 **Promise.then**、**async/await** 等任务

2. js 多线程的解决方案：h5 的 **webworker**

</el-card>

<a name="线程和进程"></a>

## 什么是线程和进程？

先来了解一些概念：

- 【文件描述符】文件描述符在形式上是一个非负整数。实际上，它是一个索引值，指向内核为每一个进程所维护的该进程打开文件的记录表。当程序打开一个现有文件或者创建一个新文件时，内核向进程返回一个文件描述符。在程序设计中，一些涉及底层的程序编写往往会围绕着文件描述符展开。
- 【程序计数器】
  - 操作系统层面：用来存储 CPU 正在执行的指令位置以及即将执行的下一条指令位置
  - 线程中：是一个线程私有的数据区域，每个线程之间的数据相互不干扰，是一个线程内存空间。可以看作是当前线程所执行的字节码的行号指示器，也就是临时存储下标位置。
- 【OS】操作系统的缩写

### 理解线程和进程

- 进程是一个具有一定独立功能的程序在一个数据集上的一次动态执行的过程。
- 线程是进程的一部分，是程序执行中一个单一的顺序控制流程。

举个例子：

> 假设你正在使用电脑，同时运行着音乐播放器和视频播放器两个应用程序。这两个应用程序代表两个不同的进程，因为每个应用程序都有自己的内存空间和系统资源。进程是操作系统进行资源分配和调度的基本单位，它们拥有独立的**地址空间、文件描述符、打开的文件等资源**。

> 在每个进程内部，可能会有多个子任务需要执行。例如，视频播放器在播放视频时需要同时显示图像、播放声音、显示字幕。这些子任务可以理解为线程，因为它们共享进程的内存空间和资源，它们没有独立的地址空间，但是每个线程都有自己独立的**运行栈和程序计数器**。线程是进程内的执行流，多个线程在一个进程内并发执行，共享进程的资源。

### 两者的关系

- 进程中任意一线程崩溃都会导致整个进程崩溃
- 线程之间可以共享进程中的数据
- 当一个进程被关闭后，操作系统会回收进程占用的资源
- 进程之间的内容相互隔离，使 OS 中的进程互不干扰

进程是 CPU 资源分配的最小单位(是能拥有资源和独立运行的最小单位)。 线程是 CPU 调度的最小单位(是建立在进程基础上的一次程序运行单位)。

<a name="线程和进程"></a>

## 内存

在软件层面上，内存通常指的是操作系统从主存中划分（抽象）出来的内存空间。可以分为两类：**栈内存**和**堆内存**。

### js 程序运行时

> 在 JavaScript 的执行过程中， 主要有三种类型内存空间，分别是**代码空间**、**栈空间**、**堆空间**。
>
> 代码空间主要是存储可执行代码的
>
> 在非全局作用域中产生的局部变量均储存在栈内存中
>
> ➡️ 原始类型的变量是真正地把值储存在栈内存中
>
> ➡️ 引用类型的变量在栈内存中存储的只是一个引用（reference），该引用指向堆内存里的真正的值
>
> **全局变量**以及**被闭包引用的变量**（即使是原始类型）均储存在堆内存中。
>
> 为什么全局变量存储在堆内存中呢？
>
> 在全局作用域下创建的所有变量都会成为全局对象（如 window 对象）的属性,全局对象存储在堆内存中。

### 栈内存

栈内存的容量较小，主要用于存放函数调用信息和变量等数据，大量的内存分配操作会导致**栈溢出**（Stack overflow）。所以栈内存的数据储存基本都是临时性的，**数据会在使用完之后立即被回收**。

栈内存由操作系统直接管理，所以栈内存的大小也由操作系统决定。

🔔 通常来说，每一条线程（Thread）都会有独立的栈内存空间，Windows 给每条线程分配的栈内存默认大小为 1MB。

### 堆内存

堆内存的分配是动态且不连续的，程序可以按需申请堆内存空间，但是访问速度比栈内存慢。

堆内存里的数据可以长时间存在，无用的数据**需要程序主动去回收**，如果大量无用数据占用内存就会造成**内存泄露**（Memory leak）

🔔 通常来说，一个进程（Process）只会有一个堆内存，同一进程下的多个线程会共享同一个堆内存。在 Chrome 浏览器中，一般情况下每个标签页都有单独的进程，不过在某些情况下也会出现多个标签页共享一个进程的情况。

<a name="内存回收"></a>

### 内存回收机制

#### 简介

JS 有**自动**内存回收机制。执行环境会自动负责管理代码的内存回收，通过管理和释放不再使用的内存来避免内存泄漏。

JS 中有两种回收机制：**标记清除（Mark-and-Sweep）**和**引用计数（Reference Counting）**

目前标记清除是 JavaScript 中主流的垃圾回收算法，而引用计数则已经很少被使用。

#### 内存回收机制的工作原理（标记-清除）

**可达对象**：是一个变量是否能够直接或间接通过全局对象访问到，如果可以那么该变量就是可达的（Reachable），否则就是不可达的（Unreachable），不可达的变量可以被安全回收。

主要包括以下几个步骤：

**1.标记阶段**：在这个阶段，垃圾收集器会从根对象开始，遍历所有的可达对象，并对其进行标记。根对象可以是*全局对象、活动函数的调用栈、寄存器中的对象引用*等。通过遍历对象之间的引用关系，垃圾收集器能够找到所有可达的对象，并将其标记为活动对象。

**2.清除阶段**：在标记阶段之后，垃圾收集器会对**堆内存**进行清除。它会遍历整个堆内存，**将未标记的对象视为垃圾**，将其所占用的内存空间标记为可重用。这些未被标记的对象可能是不再被引用的对象，或者是被其他标记对象引用的对象。

**3.压缩阶段**：在清除阶段之后，如果需要进一步优化内存空间的利用，垃圾收集器可能会执行压缩阶段。在这个阶段，它会将存活的对象移动到内存的一端，以便释放连续的内存块。这样做可以**减少内存碎片化**，提高内存的连续性，从而改善内存分配的效率。

**4.内存分配阶段**：在垃圾收集完成后，程序可以继续进行内存分配。垃圾收集器会维护一块可用的内存空间，用于分配新对象。分配过程中，垃圾收集器会根据需要进行内存扩展或缩减，以满足程序的内存需求。

#### 引用计数算法（了解）

垃圾回收器会为每个对象维护一个引用计数器，记录当前对象被引用的次数。当一个对象的引用被释放时，引用计数器减一。当**引用计数器为零**时，表示该对象**不再被引用**，即为垃圾对象，垃圾回收器会立即回收并释放其占用的内存空间。

引用计数算法无法处理循环引用的情况，可能会导致内存泄漏：

> 举个例子：假设对象 A，包含一个指向对象 B 的引用，而对象 B 也包含一个指向对象 A 的引用。此时，由于对象 A 和 B 互相引用的次数不为 0，垃圾回收器就无法清除这两个对象，导致内存泄漏。

### ❓ 标记清除算法是如何处理循环引用的？

在标记阶段，垃圾回收器会将循环引用的对象标记为“可达”，并且在遍历过程中**不会重复标记**已经被标记过的对象。

在清除阶段，由于循环引用的对象被标记为“可达”，因此不会被清除，从而保证了循环引用的正确处理。

> 举个例子：假设对象 A，包含一个指向对象 B 的引用，而对象 B 也包含一个指向对象 A 的引用。在标记阶段，垃圾回收器会从根对象开始遍历内存中的所有对象，标记对象 A 和 B 为可达对象，并且标记它们是循环引用的对象。在清除阶段，由于对象 A 和 B 被标记为可达对象，因此不会被清除。

<a name="栈溢出"></a>

### 栈溢出

栈溢出（Stack Overflow）通常发生在递归调用没有正确终止或者大量的嵌套调用导致**调用栈超过了 JavaScript 引擎设定的限制**。

**栈溢出的常见原因**：

1️⃣ 递归函数没有设置正确的终止条件，导致无限调用自身。

2️⃣ 可能是由于设计错误或者无意中导致的大量函数调用堆积在调用栈中。

**解决办法**：

1️⃣ 检查递归函数终止条件是否正确。

2️⃣ 避免过深的函数嵌套调用。

3️⃣ 使用尾递归优化（如果引擎支持）。

### ❓ 为什么尾递归可以避免栈溢出

**尾递归的概念**：在函数的最后一步调用自身，而不是在调用后还有其他操作。

**尾递归的优势**：尾递归可以有效地避免栈溢出的风险，因为它不需要保存每次调用的上下文，只需要保留一个栈帧即可。尾递归也可以提高递归的性能，因为它减少了函数调用的开销。

**尾递归和普通递归的区别**：递归调用发生的位置不同。在普通递归中，递归函数调用在递归函数的末尾，而在尾递归中，递归函数调用是函数的最后一个操作。

**注意 ⚠️**：尾递归优化只有在严格模式（strict mode）下才能生效。在非严格模式下，尾递归调用仍然会导致堆栈溢出。

代码示例

```js
// 普通递归
function fibonacci(n) {
  if (n <= 1) {
    return n;
  }
  return fibonacci(n - 1) + fibonacci(n - 2);
}
// 尾递归可以被js解释器优化成循环
function fibonacciTail(n, a = 0, b = 1) {
  if (n === 0) {
    return a;
  }
  return fibonacciTail(n - 1, b, a + b);
}
```

<a name="内存泄漏"></a>

### 内存泄漏

#### 概念

由于疏忽或者程序的某些错误造成**未能释放**已经不再使用的内存

#### 内存泄漏的常见原因

1.意外的全局变量无法被回收

2.定时器未被清理，导致所引用的外部变量无法被释放

3.未正确使用闭包的常见场景：

1️⃣ 由于使用未声明的变量，而意外的创建了一个全局变量，而使这个变量一直留在内存中无法被回收。

2️⃣ 设置了 `setInterval` 定时器，而忘记取消它，如果循环函数存在对外部变量的引用，那么这个变量会被一直留在内存中，而无法被回收。

3️⃣ 获取一个 DOM 元素的引用，即使后面这个元素被删除，由于一直保留了对这个元素的引用，所以它也无法被回收。

等等...

### ❓ 如何分析内存或排查内存泄漏

##### Memory(chrome devtools)

![](/images/js-img/memory.png)

![](/images/js-img/performance.png)

注意：打开 Chrome 的无痕模式，避免 Chrome 插件影响测试内存占用情况

待确认 ❕

步骤：

本地打包一个去掉压缩、拥有 sourcemap 及没有任何 console 的生产版本（console 会保留对象引用，阻碍销毁；去掉压缩和保留 sourcemap 有利于定位源码）
启动本地服务器，使 cef 访问本地项目
不断操作和记录 heap snapshots，观察 snapshots 和 timeline 情况
最终内存从 22.5m 上升至 34.6m，conversation 实例从 443 上升至 1117，message 实例从 443 上升至 1287，而该用户实际只有 221 个会话
不断在会话间切换，通过 timeline 看到有内存没被释放，而且生成 detached dom

<a name="闭包"></a>

## 闭包

### 理解闭包

闭包其实就是一个**可以访问其他函数内部变量的函数**。创建闭包的最常见的方式就是在一个函数内创建另一个函数，创建的函数可以访问到当前函数的局部变量。

### 闭包的表现形式

1.返回一个函数

2.在定时器、事件监听、Ajax 请求、Web Workers 或者任何异步中，只要使用了回调函
数传参，实际上就是在使用闭包

以定时器示例

```js
function fn1(x) {
  return function fn2() {
    console.log(x);
  };
}
let fn = fn1(1);
setTimeout(fn, 1000);
```

3.函数作为另一函数参数传递

示例

```js
var a = 1;
function foo() {
  var a = 2;
  function baz() {
    console.log(a);
  }
  bar(baz);
}
function bar(fn) {
  // 这就是闭包 fn();
}
foo(); // 2
```

4.立即执行函数，创建的闭包保存了全局作用域和当前函数作用域，可输出全局变量

示例

```js
var a = 2;
(function IIFE() {
  console.log(a); // 输出2
})();
```

闭包产生的本质就是：**当前环境中存在指向父级作用域的引用**，所以其本质就是作用域链的特殊应用。

### 闭包的用途

- 闭包的第一个用途是在函数外部能够访问到函数内部的变量。通过使用闭包，可以在外部调用闭包函数，从而在外部访问到函数内部的变量，可
  以使用这种方法来创建私有变量。
- 函数的另一个用途是使已经运行结束的函数上下文中的变量对象继续留在内存中，因为闭包函数保留了这个变量对象的引用，所以这个变量对象不会被回收。

[参考文章](http://www.ruanyifeng.com/blog/2009/08/learning_javascript_closures.html)

文中的示例：

```js
function f1() {
  var n = 999;

  // 此处未使用var关键字，所以定义的nAdd是全局变量
  // nAdd的值是一个匿名函数，且该函数本身也是一个闭包
  // n不会被回收
  nAdd = function () {
    n += 1;
  };

  function f2() {
    alert(n);
  }

  return f2;
}

var result = f1();

result(); // 999
nAdd();
result(); // 1000
```

### ❓5 个 6 和 1、2、3、4、5 的问题

```js
for (var i = 1; i <= 5; i++) {
  setTimeout(function () {
    console.log(i);
  }, 0);
} // 6 6 6 6 6
```

对输出结果的理解：

1️⃣ `setTimeout`是宏任务，由于 js 中单线程的 event loop、机制，在主线程同步任务执行完之后才去执行宏任务，因此循环结束后`setTimeout`的回调才依次执行。

2️⃣ `setTimeout`函数也是一种闭包，想上找 父级作用域链是`window`,变量 i 是`window`的全局变量，开始执行`setTimeout`之前变量 i 已经是 6，所以最后的输出都是 6

❓ 如何按顺序依次输出 1、2、3、4、5 呢?

方式一：立即执行函数

```js
for (var i = 1; i <= 5; i++) {
  (function (j) {
    setTimeout(function timer() {
      console.log(j);
    }, 0);
  })(i);
}
```

方式二：使用`let`

```js
for (let i = 1; i <= 5; i++) {
  setTimeout(function () {
    console.log(i);
  }, 0);
}
```

方式三：`setTimeout`第三个参数

```js
for (var i = 1; i <= 5; i++) {
  setTimeout(
    function (j) {
      console.log(j);
    },
    0,
    i
  );
}
```

<a name="作用域链"></a>

## 作用域链 / 作用域

### 作用域链

#### 概念

当访问一个变量时，代码解释器会首先在当前的作用域查找，如果没找到，就去父级作用域去查找，直到找到该变量或者不存在父级作用域中，这样的链路就是作用域链。

#### 理解作用域链

1️⃣： 是**执行上下文**的重要属性之一

2️⃣： 词法**作用域**嵌套的结果

3️⃣ ：作用域链决定了变量的访问范围，**原型链**决定了对象之间的继承关系

<a name="执行上下文"></a>

<a name="作用域"></a>

### 作用域

作用域可以理解为变量的可访问性，总共分为三种类型，分别为:

- 全局作用域

  全局变量是挂载在 window 对象下的变量，所以在任何位置都可以使用并且访问到这个全局变量

- 函数作用域

  函数中定义的变量叫作函数变量，这个时候只能在函数内部才能访问到它，所以它的作用域也就是函
  数的内部，称为函数作用域。

- 块级作用域，ES6 中的 `let` 、`const` 就可以产生该作用域

  - 使用 `let` 关键词定义的变量只能在块级作用域中被访问，有“暂时性死区”的特点，也就 是说这个变量在定义之前是不能被使用的
  - `if` 语句 及 `for` 语句后面 {...} 里面所包括的,也是块极作用域。

<a name="原型链"></a>

## 原型 / 原型链

简单理解原型与原型链：

- 如果所有对象都有私有字段 [[prototype]]，就是对象的原型;
- 读一个属性，如果对象本身没有，则会继续访问对象的原型，直到原型为空或者找到为止。

访问/设置原型的内置函数：

1️⃣`Object.create` 根据指定的原型创建新对象，原型可以是 `null`

并非真的去复制一个原型对象，而是使得新对象持有一个原型的引用

```js
var cat = {
  say() {
    console.log('cat say');
  }
};

var tiger = Object.create(cat, {
  say: {
    writable: true,
    configurable: true,
    enumerable: true,
    value: function () {
      console.log('new tiger say');
    }
  }
});

tiger.say(); // new tiger say
var anotherCat = Object.create(cat);
anotherCat.say(); // cat say
```

2️⃣`Object.getPrototypeOf`获得对象的原型

3️⃣`Object.setPrototypeOf`设置对象的原型

## 执行上下文

浏览器的 JS 引擎创建一个特殊的环境来处理 JS 代码的转换和执行。这个环境称为执行上下文。

当执行 JS 代码时，会产生三种执行上下文：

- 全局执行上下文(Global Execution Context)
- 函数执行上下文(Function Execution Context)
- eval 执行上下文

每个执行上下文中都有三个重要的属性:

- 变量对象( Variable/Object )，包含变量、函数声明和函数的形参，该属性只能在全局上下 文中访问
- 作用域链( JS 采用词法作用域，也就是说变量的作用域是在定义时就决定了)
- `this`

示例：

```js
// 全局上下文 & 函数foo上下文
var a = 10;
function foo(i) {
  var b = 20;
}
foo();
```

### 函数和变量提升

js 在生成执行上下文时，会有两个阶段：

- 全局执行上下文 和 函数执行上下文 的第一个阶段存在区别

**全局执行上下文**：第一个阶段是**创建变量对象(VO)阶段**。变量对象(VO)是一个在执行上下文创建的类对象容器，存储了在执行上下文中定义的变量和函数声明。

对于需要提升的变量，JS 解释器会在 VO 中添加一个指向该变量的属性，并将其设置为“undefined”；

对于需要提升的函数，JS 解释器会在 VO 中添加一个属性指向该函数，并将该属性存储在内存中。这意味着所有函数声明都将被存储在 VO 中，甚至在代码开始运行之前就可以访问。

如果 JS 解释器判断到一个闭包，会在堆空间创建换一个 `closure(fn)` 的对象用来保存闭包中的变量。

**函数执行上下文**：函数执行上下文并不建立 VO,它生成一个类似数组的对象，称为“参数”对象，其中包括提供给函数的所有参数。

- 创建变量对象(VO)阶段:变量对象(VO)是一个在执行上下文创建的类对象容器，存储了在执行上下文中定义的变量和函数声明。 JS 解释器会找出需要提升的变量和函数，并且给他们提前在内存中开辟好空间，函数的话会将整个函数存入内存中，变量只声明并且赋值为 `undefined` 。
- 代码执行阶段，我们可以直接提前使用。

注意 ⚠️：在提升的过程中，相同的函数会覆盖上一个函数，并且函数提升优于变量提升

示例：

```js
b(); // call b second
function b() {
  console.log('call b fist');
}
function b() {
  console.log('call b second');
}
var b = 'Hello world';
```

注意 ⚠️：非匿名的立即执行函数的特殊性

当 JS 解释器在遇到非匿名的立即执行函数时，会创建一个**辅助的特定对象**，然后将**函数名称**作为这个对象的属性，因此函数内部才可以访问到 foo ，但是这个值又是只读的，所以对它的赋值并不生效，所以打印的结果还是这个函数，并且外部的值也没有发生更改。

```js
var foo = 1;
(function foo() {
  foo = 10;
  console.log(foo);
})(); // [Function: foo]
```

`var` 会产生很多错误，所以在 es6 中引入了`let`、`const`

### ❓ 为什么 `eval()`、`with()`被认为是不推荐使用的特性

- `eval()`：可以执行传递给它的字符串作为 JS 代码并将结果插入到原位置。

示例: `eval("x=10;y=20;document.write(x*y)");`

- `with()`：允许在指定的对象作用域中执行代码块，可以省略对象名称的重复引用。

示例

```js
var obj = { x: 10, y: 20 };

with (obj) {
  console.log(x + y); // 输出 30
}
```

### 函数调用栈(call stack)

[参考文章](https://blog.csdn.net/sonicwater/article/details/112278984)

```js
function fn1() {
  let fn1 = 'fn1';
  console.log(fn1);
  fn2();
  fn3();
}
function fn2() {
  let fn2 = 'fn2';
  console.log(fn2);
}
function fn3() {
  let fn3 = 'fn3';
  console.log(fn3);
}
fn1();
```

在函数调用栈中，最先入栈的是全局上下文，它永远在栈底。用户关闭浏览器时出栈。栈顶是当时正在执行的函数上下文。
上面的代码执行过程中，fn1 先入栈，fn2 再入栈。待 fn2 执行完毕后 fn2 出栈，然后 fn3 入栈，待 fn3 执行完毕后 fn3 出栈，再等待 fn1 执行完毕后 fn1 出栈。

![](/images/js-img/order.svg)

![](/images/js-img/函数调用栈.gif)

#### `eval()`、`with()`在 JS 中都会影响性能

1.作用域链的改变：`eval()`和 `with()` 都会改变当前的作用域链。`eval() `可以访问和修改其所在上下文的作用域，这使得 JavaScript 引擎难以优化变量的查找和分配，`with()` 语句潜在地改变了其内部代码的作用域链。这意味着 JavaScript 引擎无法在编译阶段确定变量的位置，必须等到运行时才能确定，这会导致更多的计算，从而影响性能。

2.安全性问题：eval 函数会执行传入的字符串作为 JavaScript 代码，这可能会导致安全问题。如果传入的字符串来自不可信的源，可能会导致恶意代码的执行。

## This

<a name="this"></a>

### this 指向

1️⃣ 在浏览器里，在全局范围内 this 指向 window 对象;

2️⃣ 在函数中，this 永远指向最后调用他的那个对象;

3️⃣ 构造函数中，this 指向 new 出来的那个新的对象;

4️⃣call、apply、bind 中的 this 被强绑定在指定的那个对象上;

![](/images/js-img/this指向.png)

<a name="改变this指向"></a>

### 箭头函数没有`this`

- 箭头函数其实是没有`this`的,箭头函数中的`this`只取决于包裹箭头函数的第一个普通函数的`this`。

- 对箭头函数使用`bind`等这类函数是无效的。

- 另外,箭头函数没有`arguments`对象

### 改变 this 指向的三种函数

![](/images/js-img/改变this.png)

```js
  func.call(thisArg, param1, param2, ...)
  func.apply(thisArg, [param1,param2,...])
  func.bind(thisArg, param1, param2, ...)
```

### ❓ 如果对一个函数进行多次 `bind` ，函数的 this 会如何改变?

```js
// fn.bind().bind(a) 等于
let fn2 = function fn1() {
  return function () {
    return fn.apply();
  }.apply(a);
};
fn2();
```

结论：不论对函数 `bind` 了多少次， fn 中的 `this` 永远由第一次 bind 决定。

### ❓`call`、`apply`、`bind` 原理

### `call`

先来看看`call`的基础使用

```js
function add(c, d) {
  return this.a + this.b + c + d;
}

const obj = {
  a: 1,
  b: 2
};

console.log(add.call(obj, 3, 4)); // 10
```

#### call 做了什么？

> 1.将函数设为对象的属性
>
> 2.执行和删除这个函数
>
> 3.指定 this 到函数并传入给定参数,执行函数
>
> 4.如果不传入参数，默认指向 window

如果以上文字看不懂，请看如下代码 ⬇️

```js
const o = {
  a: 1,
  b: 2,
  add: function (c, d) {
    return this.a + this.b + c + d;
  }
};
```

#### 实现 `call`方法

```js
Function.prototype.myCall = function (context = window, ...args) {
  let fnKey = Symbol(); // 唯一属性名，不会出现属性名的覆盖
  // context表示call传入的this
  // this表示调用call的函数fn
  context[fnKey] = this; // 将fn函数设为 context 的属性

  // fn内部this指向context 相当于 context.fn()
  const result = context[fnKey](...args);
  delete context[fnKey]; // 清理fn
  return result;
};
```

### `apply`

#### 实现 `apply`方法

apply 第二个参数是 Array,而 call 是将一个个传入

```js
Function.prototype.myApply = function (context = window, args) {
  if (!(args instanceof Array)) throw new Error('params must be array');
  let fnKey = Symbol();
  context[fnKey] = this;

  const result = context[fnKey](...args);
  delete context[fnKey];
  return result;
};
```

### `bind`

当这个新函数被调用时，bind() 的第一个参数将作为它运行时的 this，
之后的一序列参数将会在传递的实参前传入作为它的参数。

#### `bind`基础使用

```js
function foo(c, d) {
  this.b = 100;
  console.log(this.a); // 1
  console.log(this.b); // 100
  console.log(c); // 1st
  console.log(d); // 2nd
}
// 我们将foo bind到{a: 1}
var func = foo.bind(
  {
    a: 1
  },
  '1st'
);
func('2nd');
```

#### `bind`的实现

考虑两点：

1.对于普通函数，绑定`this`指向

2.对于构造函数，要保证原函数的原型对象上的属性不能丢失

```js
Function.prototype.myBind = function (context, ...args) {
  if (typeof this !== 'function') throw new TypeError('Error');
  // this表示调用bind的函数
  let self = this; //  fn.bind(obj) self就是fn

  // this instanceof fBound为true时，表明为构造函数：new func.bind(obj)
  // 如果是普通函数，this默认指向window，如果为false时，将绑定函数的this指向context
  let fBound = function (...innerArgs) {
    return self.apply(
      this instanceof fBound ? this : context,
      args.concat(innerArgs) // 拼接参数
    );
  };

  // 使用Object.create实现继承
  fBound.prototype = Object.create(this.prototype);
  return fBound;
};

// --测试代码--
// 构造函数
function Person(name, age) {
  console.log('person name:', name);
  console.log('person age:', age);
  console.log('person this:', this);
}

Person.prototype.say = function () {
  console.log('say');
};

var obj = { name: 'ttt', age: 12 };
var bindFn = Person.myBind(obj, '修改');

// person name: 修改
// person age: 111
// person this: Person {}
var newFn = new bindFn(111);

// newFn.say(); // say

// 普通函数
function normalFunc(name, age) {
  console.log('普通函数 name', name);
  console.log('普通函数 age', age);
  console.log('普通函数 this', this);
}

var bindNormalFunc = normalFunc.bind(obj, 'qqq');

// 普通函数 name qqq
// 普通函数 age 33
// 普通函数 this { name: 'ttt', age: 12 }
bindNormalFunc(33);
```

### call、apply、bind 的实际应用

1️⃣ 判断数据类型`Object.prototype.toString.call()`

类型检测代码实现

```js
function getType(obj) {
  let type = typeof obj;
  if (type !== 'object') {
    return type;
  }
  return Object.prototype.toString
    .call(obj)
    .replace(/^\[object (\S+)\]$/, '$1');
}
```

2️⃣ 类数组借用方法

类数组因为不是真正的数组，所有没有数组类型上自带的种种方法，所以我们就可以利用一些方法去借用数组的方法，比如借用数组的 `push` 方法。

代码示例：

```js
var arrayLike = {
  0: 'java',
  1: 'script',
  length: 2
};
Array.prototype.push.call(arrayLike, 'jack', 'lily');
console.log(typeof arrayLike); // 'object'
console.log(arrayLike); // { '0': 'java', '1': 'script', '2': 'jack', '3': 'lily', length: 4 }
```

3️⃣ 获取数组最大/最小值

```js
let arr = [13, 6, 10, 11, 16];
const max = Math.max.apply(Math, arr);
const min = Math.min.apply(Math, arr);
console.log(max); // 16
console.log(min); // 6
```

## 继承

### 【es5】继承

[es5 继承速览](https://www.jianshu.com/p/124ed22c4844)

组合式继承（原型链继承 + 构造函数继承）

```js
function Parent(name) {
  this.name = name;
  this.friend = ['lucky'];
}

Parent.prototype.getFriend = function () {
  console.log('friend', this.friend);
};

function Student(name) {
  Parent.call(this, name);
}

Student.prototype = new Parent('tom');
let stu1 = new Student('lily');

console.log(stu1);
```

### 对象形式的继承

#### 浅拷贝继承

```js
function normalCopy(p, c) {
  let c = c || {};

  for (let prop in p) {
    c[prop] = p[prop];
  }
}
```

浅拷贝的缺点：浅拷贝对于引用类型的拷贝只是拷贝了地址，如果修改了引用类型的值，会影响到父对象中的值。

#### 深拷贝继承

利用递归进行深拷贝

```js
function deepCopy(p, c) {
  let c = c || {};
  for (let prop in p) {
    if (typeof p[prop] === 'object') {
      c[prop] = p[prop].constructor === Array ? [] : {};
      deepCopy(p[prop], c[prop]);
    } else c[prop] = p[prop];
  }
}
```

#### 使用`call`和`apply`继承

```js
function Parent() {
  this.name = 'abc';
  this.address = { home: 'home' };
}
function Child() {
  Parent.call(this);
  this.language = 'js';
}

const chi = new Child();
console.log(chi.name); // abc
console.log(chi.language); // js
```

#### 【es5】`Object.create()`

`Object.create()`是 new 操作符的替代方案

```js
var p = { name: 'poetry' };
var obj = Object.create(p);
console.log(obj.name); // poetry
```

##### 实现`Object.create()`

```js
function myCreate(o) {
  function F() {}
  F.prototype = o;
  o = new F();
  return o;
}

var p = { name: 'poetry' };
var obj = myCreate(p);
console.log(obj.name); // poetry
```

## ❓new 的过程实现

### new 操作符做了哪些事

- 以构造器的 prototype 属性为原型（区分私有字段[[prototype]]），创建新对象

- 将 this 和调用参数传给构造器，执行

- 如果构造器返回的是对象，则返回，否则返回第一步创建的对象

```js
function myNew(constructor, ...args) {
  // 创建一个新对象，继承构造函数的原型对象
  let newObj = Object.create(constructor.prototype);
  // 调用构造函数，为新对象添加属性，获取函数执行结果result
  let result = constructor.apply(newObj, args);
  // 如果函数执行结果的返回值类型是对象，则返回执行结果，否则返回新创建的对象
  return typeof result === 'object' ? result : newObj;
}
```

new 操作符的行为，客观上提供了两种方式添加属性：

1️⃣ 在构造器中添加属性

```js
function c1() {
  this.p1 = '构造器的属性';
  this.p2 = function () {
    console.log(this.p1);
  };
}

var o1 = new c1();
o1.p2(); // 构造器的属性
```

2️⃣ 在构造器的 `prototype` 属性上添加属性

```js
function c2() {}

c2.prototype.p1 = '原型的属性';
c2.prototype.p2 = function () {
  console.log(this.p1);
};

var o2 = new c2();
o2.p2(); // 原型的属性
```

<!-- ### 类继承 -->

## 类型

![](/images/js-img/类型.png)

**基本数据类型**：基础类型存储在栈内存，被引用或拷贝时会创建一个完全相等的变量；占据空间小、大小固定，属于被频繁使用的数据，所以放入栈中存储。

**引用数据类型**：引用类型存储在堆内存，存储的是地址，多个引用指向同一个地址，占据空间大、大小不固定。引用数据类型在栈中存储了指针，该指针指向堆中该实体的起始地址。当解释器寻找引用值时，会首先检索其在栈中的地址，取得地址后从堆中获得实体。

### ❓ 为什么有的编程规范要求用`void 0`代替`undefined`

任何变量在赋值前是 `Undefined` 类型、值为 undefined。在 JS 设计中，`undefined`不是关键字，而是变量。为避免无意篡改值，建议使用`void 0`代替`undefined`值。

在实际编程时，可以将变量先赋值为`null`,`null`表示：定义了但是为空值。一般不会把变量赋值为 `undefined`，这样可以保证所有值为`undefined`的变量，都是从未赋值的自然状态。

### ❓ 0.1+0.2 不等于 0.3

`console.log(0.1 + 0.2 == 0.3); // false`

浮点数运算的精度问题导致等式两侧的结果并不是严格相等，正确的比较方法是使用 JS 提供的最小精度值`Number.EPSILON`

`console.log(Math.abs(0.1 + 0.2 - 0.3) <= Number.EPSILON); // true`

### ❓ 遍历中如何取到`symbol`类型

常见的对象遍历方法

- `for (let xx in obj)`：【es5】遍历对象的可枚举属性，包括继承（原型上）的属性，遍历顺序不确定。
- `for (let xx of obj)`：【es6】遍历可迭代对象(数组、字符串、Set、Map 等)，不会遍历非述职属性或原型上的属性
- `Object.keys(obj)`：返回包含 key 的数组
- `Object.values(obj)`：返回包含 value 的数组
- `Object.getOwnPropertyNames()`：返回包含 key 的数组

如何遍历到`Symbol`

- `Object.getOwnPropertySymbols()`：返回对象中只包含 symbol 类型 key 的数组
- `Reflect.ownKeys()` ：返回对象中所有类型 key 的数组（包含 symbol）

### ❓ 递归遍历实现深拷贝（for in）

```js
function deepClone(obj) {
  if (typeof obj !== 'object' || obj === null) return obj;

  let copyObj = obj instanceof Array ? [] : {};

  for (let key in obj) {
    if (obj.hasOwnProperty(key)) {
      copyObj[obj] = deepClone(obj[key]);
    }
  }
  return copyObj;
}
```

### ❓ 为什么给对象添加的方法能用在基本类型上

运算符提供了装箱操作，它会根据基础类型构造一个临时对象，使得我们能在基础类型上调用对应对象的方法。

📄**理解装箱转换 & 拆箱转换**

包装类与原始值转换过程叫做「装箱」和「拆箱」，装箱(boxing)是将值类型包装为对象类型，拆箱(unboxing)是将对象类型转换为类型。

每一种基本类型 `Number`、`String`、`Boolean`、`Symbol` 在对象中都有对应内置的类。装箱机制会频繁产生临时对象，在一些对性能要求较高的场景下，我们应该尽量避免对基本类型做装箱转换。

装箱操作的**具体步骤**为：创建该类型的实例，在实例上调用指定的方法，销毁实例。

拆箱转换：在 JavaScript 标准中，规定了 `toPrimitive` 函数（es6），允许对象通过重写`toPrimitive` 函数来实现转换（优先级最高）。它是对象类型到基本类型的转换，如果没有`ToPrimitive`函数，会先后尝试调用 `valueOf` 和 `toString` 来获得拆箱后的基本类型。如果 `valueOf` 和 `toString` 都不存在，或者没有返回基本类型，则会产生类型错误 TypeError。

## 类型检测

### ❓`instanceof`的实现原理

判断对象的原型链中是否存在类型的 prototype

实现代码

```js
function myInstanceOf(instance, classOrFunc) {
  if (typeof instance !== 'object' || instance === null) return false;

  let proto = Object.getPrototypeOf(instance);
  while (proto) {
    if (proto === classOrFunc.prototype) return true;
    proto = Object.getPrototypeOf(proto);
  }
  return false;
}
```

## 理解 js 对象的两类属性

### 第一类属性：数据属性

特征如下：

- `value`:就是属性的值。
- `writable`:决定属性能否被赋值。
- `enumerable`:决定 for in 能否枚举该属性。
- `configurable`:决定该属性能否被删除或者改变特征值。

### 第二类属性：访问器属性

特征如下：

- `getter`:函数或 undefined，在取属性值时被调用。
- `setter`:函数或 undefined，在设置属性值时被调用。
- `enumerable`:**决定 for in 能否枚举该属性**。
- `configurable`:决定该属性能否被删除或者改变特征值。

访问器属性使得属性在读和写时执行代码，它允许使用者在写和读属性时，得到完全不同的值，它可以视为一种函数的语法糖。

### 查询 / 修改 对象的属性

#### 查询对象的数据属性的 API

`Object.getOwnPropertyDescriptor()`

```js
let o = { a: 1 };
o.b = 2;
console.log(Object.getOwnPropertyDescriptor(o, 'a')); // { value: 1, writable: true, enumerable: true, configurable: true }
```

#### 定义/修改 对象的属性的 API

常规的定义属性：会产生数据属性

```js
let o = { a: 1 };
o.b = 2s
```

##### 定义访问器属性/ 改变数据属性特征：`Object.defineProperty()`

```js
let o = { a: 1 };

Object.defineProperty(o, 'b', {
  value: 1,
  writable: true,
  enumerable: false,
  configurable: true
});

// { value: 1, writable: true, enumerable: false, configurable: true }
console.log(Object.getOwnPropertyDescriptor(o, 'b'));
```

##### 创建访问器属性：get 和 set 关键字

```js
let o = {
  b: 222,
  a: 5,
  get b() {
    return this.a * 2;
  },
  set b(n) {
    this.a = n;
    console.log(this.a); // 777
  },
  get c() {
    return 22;
  }
};
console.log(o.c); // 22
o.b = 777;
```
