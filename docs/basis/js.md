---
sidebar: auto
tags:
  - javascript
---

## 环环相扣 💫

知识互联 💬

<el-card class="frame" shadow="always">
[**进程**](#线程和进程) ➡️
[**堆**](#内存)用于存放进程运行时动态分配的内存段 ➡️
js 的[**内存回收机制**](#内存回收) ➡️
[**内存泄漏**](#内存泄漏)问题 ➡️
可能的原因：[**闭包**](#闭包)/定时器未被正确销毁等 ➡️
闭包本质：[**作用域链**](#作用域链)的一个特殊应用 ➡️

【理解作用域链】

理解 1️⃣ ：即 [**作用域**](#作用域)嵌套的结果 ➡️ 全局/函数/块级作用域（**let const**的出现）

理解 2️⃣： 是[**执行上下文**](#执行上下文)的重要属性之一 ➡️ 执行上下文可以理解为一个对象，包含：**变量对象**、**作用域链**、[**this**](#this) ➡️ this 相关：[**call apply bind**](#改变this指向)（es6） / **箭头函数**

理解 3️⃣ ：作用域链决定了变量的访问范围，[**原型链**](#原型链)决定了对象之间的继承关系

</el-card>

<el-card class="frame" shadow="always">
线程 ➡️

1️⃣ 线程使用栈内存 ➡️
[**栈溢出**](#栈溢出)问题 ➡️
可能的原因：**递归**终止条件不正确/函数嵌套调用过深 ➡️
递归优化：**尾递归**

2️⃣ js 是单线程 ➡️

1.[**eventloop** 机制](#eventloop)（事件循环机制）➡️ 同步/异步任务 ➡️ 异步任务分为**宏任务**/**微任务** ➡️ 微任务主要包括 **Promise.then**、**async/await** 等任务

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

<a name="闭包"></a>

## 闭包

### 理解闭包

闭包其实就是一个**可以访问其他函数内部变量的函数**。创建闭包的最常见的方式就是在一个函数内创建另一个函数，创建的函数可以访问到当前函数的局部变量。**每一个子函数都会拷贝上级的作用域，形成一个作用域的链条。**

### 闭包的表现形式

1.返回一个函数

2.在定时器、事件监听、Ajax 请求、Web Workers 或者任何异步中，只要使用了回调函数传参，实际上就是在使用闭包

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

  - 使用 `let` 关键词定义的变量只能在块级作用域中被访问，有"暂时性死区"的特点，也就是说这个变量在定义之前是不能被使用的
  - `if` 语句 及 `for` 语句后面 `{...}` 里面所包括的,也是块极作用域。

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

### 原型、`__proto__`、prototype 的关系

- `__proto__` 属性是**对象独有**的，而 `prototype` 属性是**函数独有**的
- `__proto__` 属性指向了`[[Prototype]]`这个内部属性， `__proto__`本质就是`[[Prototype]]`的一个 getter/setter 实现
- 实例对象.`__proto__` === prototype
- 原型.constructor === 构造函数
- 构造函数.prototype === 原型

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

![](/img/images/js-img/order.svg)

![](/img/images/js-img/函数调用栈.gif)

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

![](/img/images/js-img/this指向.png)

<a name="改变this指向"></a>

### 箭头函数没有`this`

- 箭头函数其实是没有`this`的,箭头函数中的`this`只取决于包裹箭头函数的第一个普通函数的`this`。

- 对箭头函数使用`bind`等这类函数是无效的。

- 另外,箭头函数没有`arguments`对象

### 改变 this 指向的三种函数

![](/img/images/js-img/改变this.png)

```js
  func.call(thisArg, param1, param2, ...)
  func.apply(thisArg, [param1,param2,...])
  func.bind(thisArg, param1, param2, ...)
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
console.log(arrayLike); // `{ '0': 'java', '1': 'script', '2': 'jack', '3': 'lily', length: 4 }`
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

#### 寄生组合继承（原型链继承 + 构造函数继承）

es6 中的 extends 被 babel 编译成 es5 的代码时，采用的就是寄生组合继承，在此基础上 es6 额外进行了`Object.setPrototypeOf(subClass,superClass)`的操作，来**继承父类的静态方法**，**弥补了寄生组合继承的不足**。

```js
function Parent5(name) {
  this.name = 'parent5';
  this.play = [1, 2, 3];
  this.getName = () => {
    console.log(name ?? this.name); // ttt
  };
}

Parent5.prototype.getProtoName = () => {
  console.log('ProtoName');
};

Parent5.getOwnName = () => {
  console.log('own');
};

function Child5() {
  Parent5.call(this); // 子类拿到父类的属性值
  this.type = 'child5';
}

Child5.prototype = Object.create(Parent5.prototype); // 使用Object.create继承父类原型上的方法
Child5.prototype.constructor = Child5; // 指定子类实例的构造函数,构造函数只执行一次

const newChild = new Child5();
newChild.getProtoName(); // ProtoName
newChild.getOwnName(); // TypeError: newChild.getOwnName is not a function
```

### class 继承

class 实现继承的核心在于使用 `extends` 表明继承自哪个父类，并且在子类构造函数中必须调用 `super` ， 因为这段代码可以看成 `Parent.call(this, value)` 。

```js
class Parent {
  constructor(value) {
    this.val = value;
  }
  getVal() {
    console.log(this.val);
  }
}

class Child extends Parent {
  constructor(value) {
    super(value);
    // this.val = value;
  }
}

let chi = new Child(222);

chi.getVal(); // 222
console.log(chi instanceof Parent);
```

### es5 和 es6 继承的区别

- ES6 继承的子类需要调用 super() 才能拿到子类，ES5 的话是通过
  种绑定的方式
- 类声明不会提升，和 let 这些一致

## 面向对象

基本思想是使用**对象，类，继承，封装，多态，抽象**等基本概念来进行程序设计

优势：易扩展，降低重复工作量，重用性和继承性高

### 对象形式的继承

#### 浅拷贝继承

```js
const shallowClone = (target) => {
  if (typeof target === 'object' && target !== null) {
    const cloneTarget = Array.isArray(target) ? [] : `{}`;
    for (let prop in target) {
      if (target.hasOwnProperty(prop)) {
        cloneTarget[prop] = target[prop];
      }
    }
    return cloneTarget;
  } else {
    return target;
  }
};
```

浅拷贝的缺点：浅拷贝对于子对象中引用类型的拷贝只是拷贝了地址，如果修改了引用类型的值，会影响到父对象中的值。

#### 深拷贝继承

利用递归进行深拷贝

使用 for in 遍历对象会遍历原型链上的属性，使用`Object.hasOwnProperty()`检测剔除原型链上的属性

```js
function deepCopy(p, c) {
  let copy = c || `{}`;
  for (let prop in p) {
    if (!p.hasOwnProperty(prop)) continue;

    if (typeof p[prop] === 'object' && p[prop] !== null) {
      copy[prop] = p[prop] instanceof Array ? [] : `{}`;
      deepCopy(p[prop], copy[prop]);
    } else copy[prop] = p[prop];
  }
}
```

#### 使用`call`和`apply`继承

**缺点**：虽然能够拿到父类的属性值，父类原型对象中的方法子类无法继承。

```js
function Parent() {
  this.name = 'abc';
  this.address = `{ home: 'home' }`;
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
var p = `{ name: 'poetry' }`;
var obj = Object.create(p);
console.log(obj.name); // poetry
```

##### 实现`Object.create()`

```js
function myCreate(obj, props) {
  function Fn() `{}`
  Fn.prototype = obj;
  let newFn = new Fn();
  for (let key in props) {
    Object.defineProperty(newFn, key, `{ enumerable: true, value: props[key] }`);
  }
  return newFn;
}

var p = `{ name: 'poetry' }`;
var obj = myCreate(p);
console.log(obj.name); // poetry
```

### 面向对象中的静态方法/静态属性

没有 new，也可以引用静态方法属性

```js
function Person(name) {
  var age = 100;
  this.name = name;
}
//静态成员
Person.walk = function () {
  console.log('static');
};
Person.walk(); // static
```

### 私有/公有

```js
function Person(id) {
  // 私有属性与方法
  var name = 'poetry';

  //公有属性与方法
  this.id = id;
  this.say = function () {
    console.log(this.id, name);
  };
}
var p1 = new Person(123);
console.log(p1.name); // undefined
p1.say(); // 123 poetry
```

### 多态

同一个父类继承出来的子类各有各的形态

```js
function Cat() {
  this.eat = '肉';
}
function Tiger() {
  this.color = '黑黄相间';
}
function Cheetah() {
  this.color = '报文';
}
function Lion() {
  this.color = '土黄色';
}
Tiger.prototype = Cheetah.prototype = Lion.prototype = new Cat(); //共享一个祖先 Cat
var T = new Tiger();
var C = new Cheetah();
var L = new Lion();
console.log(T.color);
console.log(C.color);
console.log(L.color);
console.log(T.eat);
console.log(C.eat);
console.log(L.eat);
```

### 抽象类

抽象类不能被实例化，只能被继承

```js
function DetectorBase() {
  throw new Error('Abstract class can not be invoked directly!');
}

DetectorBase.prototype.detect = function () {
  console.log('Detection starting...');
};

// 不能直接被实例化
// const d = new DetectorBase(); // Error: Abstract class can not be invoked directly!

// 只能通过继承来调用
function LinkDetector() `{}`
LinkDetector.prototype = Object.create(DetectorBase.prototype);
LinkDetector.prototype.constructor = LinkDetector;
var l = new LinkDetector();
l.detect(); //Detection starting...
```

## 深入了解模块化

模块化出现之前存在的问题

每个加载的 js 文件都共享变量和方法，很容易出现**全局变量污染**和**依赖管理混乱**的问题

以前的解决方案：使用**匿名函数自执行**的方式，形成独立的块极作用域解决问题

```js
(function () {
  function name() {
    //...
  }
})();
```

### 模块化规范

- CommonJS ：通过 require 来引入模块，通过 module.exports 定义模块的输出接口，在服务端以同步的方式引入模块。浏览器端，webpack 打包工具具备对 CommonJS 的支持和转换。
- ES Module ：使用 import 和 export 的形式来导入导出模块，在浏览器端以异步的方式引入模块。ES6 的模块系统，如果借助 Babel 的转换，ES6 的模块系统最终还是会转换成 CommonJS 的规范。
- AMD
- CMD

### CommonJS

nodejs 借鉴了 Commonjs 的 Module ，实现了良好的模块化管理。

CommonJS 模块加载过程：

- 模块在被第一次引入时，模块中的 js 代码会被运行一次。
- 被多次引入时，会缓存，最终只加载（运行）一次。
  - 每个模块对象 module 都有一个属性：loaded，为 false 表示还没有加载，为 true 表示已经加载。
- 如果存在循环引入，那么加载顺序是怎样的？
  - Node 采用的是深度优先，所以存在循环引入时，加载顺序是不确定的。

### ES Module

#### 基础使用

**导出模块：a.js**

```js
// 方式一
// ⭐️module 是 Node 独有的一个变量
var greet = function () {
  console.log('Hello World');
};

module.exports = greet;
// 方式二
// exports.a = 1;
```

以上代码会被 node 包装为 IIFE

```js
(function (exports, require, module, __filename, __dirname) {
  //add by node
  var greet = function () {
    console.log('Hello World');
  };
  module.exports = greet;
}).apply(); //add by node

return module.exports; // module.exports 和 exports 指向同一个引用
```

**导入：b.js**

```js
// 实质就是包装了一层立即执行函数
var module = require('./a.js');
module.a; // -> log 1
```

**1.在 script 标签引入模块的 js 文件时，要加上类型 type="module"**

`<script src="./main.js" type="module"></script>`

**2.导出可以给标识符起一个别名：通过 as 关键字**

`export `{ name as cname }``

`import `{ name as fname }` from "./foo.js"`

**3.使用 `*`，将模块功能放到一个模块功能对象上**

`import * as foo from "./foo.js"`

**4.`export default`:默认导出。在一个模块中只能有一个默认导出**

#### ES Module 的解析过程

![](/img/images/js-img/esmodule.png)

阶段一：构建（Construction），根据地址查找 js 文件，并且下载，将其解析成模块记录（Module Record）；

阶段二：实例化（Instantiation），对模块记录进行实例化，并且分配内存空间，解析模块的导入和导出语句，把模块指向对应的内存地址。

阶段三：运行（Evaluation），运行代码，计算值，并且将值填充到内存地址中

### ES6

```js
//导出
export function sum(x, y) {
  return x + y;
}
export const pi = 3.14;

//导入
import `{ sum, pi }` from './my.js';
```

## 事件机制

### 捕获 & 冒泡

- 事件捕获：浏览器会从根节点开始 由外到内进行事件传播，即点击了子元素，如果父 元素通过事件捕获方式注册了对应的事件的话，会 先触发父元素绑定的事件

- 事件冒泡：事件冒泡顺序是由内到外进行事件传播，直到根节点

W3C 的标准是先捕获再冒泡， `addEventListener` 的第三个参数决定把事件注册在捕获(true)还是冒泡(false)

### 事件流阻止

- 阻止默认行为：`event.preventDefault()`
- 阻止冒泡 / 捕获：`event.stopPropagation()`
- 不仅阻止冒泡 / 捕获，而且阻止该事件目标执行别的注册事件：`event.stopImmediatePropagation()`

### 事件委托（事件的冒泡原理）

- 减少 dom 操作
- 节省内存
- 子节点无需注销事件

<a name="eventloop"></a>

## eventloop 机制

### 同步 与 异步

同步：在主线程上排队执行的任务，只有前一个任务执行完毕，才能执行后一个任务

异步：不进入主线程、而进入"任务队列"（task queue）的任务，只有"任务队列"通知主线程，某个异步任务可以执行了，该任务才会进入主线程执行

**宏任务**：script、`setTimeout`、`setInterval`、`setImmediate`、I/O 网络请求完成、文件读写完成事件、UI rendering、用户交互事件(比如鼠标点击、滚动页面、放大缩小等)

**微任务**：`process.nextTick`、`promise`、`Object.observe`、`MutationObserver`

### eventloop 机制运行流程

（1）所有同步任务都在主线程上执行，形成一个执行栈（execution context stack）。

（2）主线程之外，还存在一个"任务队列"（task queue）。只要异步任务有了运行结果，就在"任务队列"之中放置一个事件。

（3）一旦"执行栈"中的所有同步任务执行完毕，系统就会读取"任务队列"，看看里面有哪些事件。那些对应的异步任务，于是结束等待状态，进入执行栈，开始执行。

（4）主线程不断重复上面的第三步

**Tip** ：如果宏任务中的异 步代码有大量的计算并且需要操作 DOM 的话，为了 更快的响应界面响应，我们可以把操作 DOM 放入微任务中

### js 运行的整体流程

- 首先 js 是单线程运行的，在代码执行的时候，通过将不同函数的执行上下文压入执行栈中来保证代码的有序执行
- 在执行同步代码的时候，如果遇到了异步事件，js 引擎并不会一直等待其返回结果，而是会将这个事件挂起，继续执行执行栈中的其他任务
- 当同步事件执行完毕后，再将异步事件对应的回调加入到与当前执行栈中不同的另一个任务队列中等待执行
- 任务队列可以分为宏任务对列和微任务对列，当当前执行栈中的事件执行完毕后，js 引擎首先会判断微任务对列中是否有任务可以执行，如果有就将微任务队首的事件压入栈中执行
- 当微任务对列中的任务都执行完成后再去判断宏任务对列中的任务。

示例：

```js
setTimeout(function () {
  console.log(1);
}, 0);
new Promise(function (resolve, reject) {
  console.log(2);
  resolve();
}).then(function () {
  console.log(3);
});
process.nextTick(function () {
  console.log(4);
});
console.log(5);
```

第一轮:主线程开始执行，遇到`setTimeout`,将`setTimeout`的回调函数放入宏任务队列中，往下执行。

new Promise 立即执行【输出 2】，then 进入微任务队列中

process.nextTick，进入微任务队列中

立即【输出 5】，第一轮同步任务执行完成。

查看微任务队列：then 函数和 nextTick 两个微任务，nextTick 异步任务发生在所有异步任务之前。
先执行 nextTick【输出 4】，再执行 then【输出 3】，第一轮执行结束。

第二轮：从宏任务队列开始， 执行 setTimeout 回调函数【输出 1】

### 重绘和回流和 Event loop 有关

- 当 Event loop 执行完 Microtasks 后，会判断 document 是否需要更新。因为浏览器是 60Hz 的刷新率，每 16ms 才会更新一次。
- 然后判断是否有 resize 或者 scro11 ，有的话会去触发事件，所以 resize 和 scro11 事件也是至少 16ms 才会触发一次，并且自带节流功能。
- 判断是否触发了 media query
- 更新动画并且发送事件
- 判断是否有全屏操作事件
- 执行 requestAnimationFrame 回调
- 执行 Intersectionobserver 回调，该方法用于判断元素是否可见，可以用于懒加载上，但是兼容性不好
- 更新界面
- 以上就是一帧中可能会做的事情。如果在一帧中有空闲时间，就会去执行 requestIdlecallback 回调

## 数据类型

![](/img/images/js-img/类型.png)

**基本数据类型**：Undefined、Null、Boolean、Number、String、Symbol（es6）和 BigInt（es10）。基础类型存储在栈内存，被引用或拷贝时会创建一个完全相等的变量；占据空间小、大小固定，属于被频繁使用的数据，所以放入栈中存储。

**引用数据类型**：Object。引用类型存储在堆内存，存储的是地址，多个引用指向同一个地址，占据空间大、大小不固定。引用数据类型在栈中存储了指针，该指针指向堆中该实体的起始地址。当解释器寻找引用值时，会首先检索其在栈中的地址，取得地址后从堆中获得实体。

## 类型检测方法

### 1.`typeof`

判断除了 null 的基础数据类型

```js
console.log(typeof function () `{}`); // function
console.log(typeof undefined); // undefined
console.log(typeof null); // object
console.log(typeof []); // object
console.log(typeof `{}`); // object
```

### 2.`instanceof`

判断引用数据类型，不能判断基本数据类型。原理：**判断对象的原型链中是否存在类型的 prototype**

#### 实现`instanceof`

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

console.log('test', _instanceof(null, Array)); // false
console.log('test', _instanceof([], Array)); // true
```

### 3.`constructor`

```js
console.log('str'.constructor === String); // true
console.log([].constructor === Array); // true
console.log(function () `{}`.constructor === Function); // true
console.log(`{}`.constructor === Object); // true
```

弊端：创建一个对象并更改它的原型， constructor 会变得不可靠

```js
function Fn() `{}`
Fn.prototype = new Array();

console.log(new Fn().constructor === Array); // true
console.log(new Fn().constructor === Fn); // false
```

### 4.`Object.prototype.toString.call()`

- 对于 Object 对象，直接调用 toString(),就能返回 [object Object] ;而对于其他对象，需要通过 call 来调用，返回正确的类型信息
- 可以区分 window、document、Date、正则等

### 通用的数据类型判断实现

```js
function getType(obj) {
  let type = typeof obj;
  if (type !== 'object') return type;

  return Object.prototype.toString
    .call(obj)
    .replace(/^\[object (\S+)\]$/, '$1')
    .toLowerCase();
}

console.log(getType([])); // array
console.log(getType('ttt')); // string
```

Tip 补充：

```js
// 将英文单词首字母大写
console.log('hello'.toUpperCase().slice(0, 1) + 'hello'.slice(1));

// 英文单词全部大写
console.log('hello'.toUpperCase()); // HELLO

// 英文单词小写
console.log('Hello'.toLowerCase()); // hello
```

## js 对象的两类属性

### 一：数据属性

特征如下：

- `value`:就是属性的值。
- `writable`:决定属性能否被赋值。
- `enumerable`:决定 for in 能否枚举该属性。
- `configurable`:决定该属性能否被删除或者改变特征值。

### 二：访问器属性

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
let o = `{ a: 1 }`;
o.b = 2;
console.log(Object.getOwnPropertyDescriptor(o, 'a')); // `{ value: 1, writable: true, enumerable: true, configurable: true }`
```

#### 定义/修改 对象的属性的 API

常规的定义属性：会产生数据属性

```js
let o = `{ a: 1 }`;
o.b = 2s
```

##### 定义访问器属性/ 改变数据属性特征：`Object.defineProperty()`

```js
let o = `{ a: 1 }`;

Object.defineProperty(o, 'b', {
  value: 1,
  writable: true,
  enumerable: false,
  configurable: true
});

// `{ value: 1, writable: true, enumerable: false, configurable: true }`
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

## lterator 迭代器

Iterator (迭代器)是一种接口，也可以说是一种规范。为各种不同的数据结构提供统一的访问机制。 任何数据结构只要部署 Iterator 接口([Symbol.iterator]属性)，就可以完成遍历操作(即依次处理该数据结构的所有成员)。

原型部署了 Iterator 接口的数据结构有三种，具体包含四种，分别是数组，类似数组的对象，Set 和 Map 结构

```js
const obj = {
  [Symbol.iterator]: function () `{}`
};
```

- 迭代器的遍历方法是首先获得一个迭代器的指针，初始时该指针指向第一条数据之前，接着通过调用 next 方法，改变指针的指向，让其指向下一条数据
- 每一次的 next 都会返回一个对象，该对象有两个属性
  - value 代表想要获取的数据
  - done 布尔值，false 表示当前指针指向的数据有值，true 表示遍历已经结束
- 对象(Object)没有部署 iterator 接口

## Promise

Promise 是 ES6 新增的语法，解决了**回调地狱**的问题。回调地狱就是为是实现代码顺序执行而出现的一种操作，代码阅读性差且难以维护。

可以把 Promise 看成一个状态机。初始是`pending`状态，可以通过函数 `resolve` 和`reject`，将状态转变为`resolved`或者`rejected`状态，**状态一旦改变就不能再次变化**。

### Promise 的三种状态

- 待定(`pending`):初始状态，既没有被完成，也没有被拒绝。
- 已完成(`fulfilled`):操作成功完成。
- 已拒绝(`rejected`):操作失败。

### 静态方法

- `Promise.all`
  - 用途：将多个异步请求并行操作
  - 参数：Promise 的数组，返回一个新的 Promise。
  - 当所有结果成功返回时**按照请求顺序返回成功结果**
  - 当其中有一个失败方法时，则进入失败方法
- `Promise.allSettled`:
  - 用途：将多个异步请求并行操作，并且返回所有结果，操作完成后可以拿到每个 Promise 的状态
  - 参数：Promise 的数组，返回一个新的 Promise。
- `Promise.any`
  - 只要参数 Promise 实例有一个变成`fulfilled`状态，最后 any 返回的实例就会变成`fulfilled`状态;如果所有参数 Promise 实例都变成`rejected`状态，包装实例就会变成`rejected`状态
  - 参数：Promise 的数组，返回一个新的 Promise。
- `Promise.race`:将多个异步请求并行操作，只返回第一个结果
  - 只要参数的 Promise 之中有一个实例率先改变状态，则 race 方法的返回状态就跟着改变。那个率先改变的 Promise 实例的返回值，就传递给 race 方法的回调函数
  - 应用场景：将图片请求和超时判断放到一起，用 race 来实现图片的超时判断
- `Promise.resolve`:将现有对象转为 Promise 对象
- `Promise.reject`:返回一个状态为失败的 Promise 对象

### 实例方法

- `then`:为 Promise 实例添加状态改变时的回调函数
- `catch`:为 Promise 实例添加状态变为 rejected 时的回调函数
- `finally`:为 Promise 实例添加状态改变时的回调函数，无论状态是 fulfilled 还是 rejected

## Generator

Es6 新增，Generator 函数是 ES6 提供的一种异步编程解决方案。通过 yield 标识位和 next() 方法调用，实现函数的分段执行。

Generator 函数可以说是 Iterator 接口的具体实现方式。Generator 最大的特点就是可以控制函数的执行。

- function* 用来声明一个函数是生成器函数，它比普通的函数声明多了一个 * , \* 的位置比较随意可以挨着 function 关键字，也可以挨着函数名
- yield 产出的意思，这个关键字只能出现在生成器函数体内，但是生成器中也 可以没有 yield 关键字，函数遇到 yield 的时候会暂停，并把 yield 后面 的表达式结果抛出去
- next 作用是将代码的控制权交还给生成器函数

function* foo(x) {
let y = 2 * (yield x + 1);
let z = yield y / 3;
return x + y + z;
}
let it = foo(5);
console.log(it.next()); // => `{value: 6, done: false}`
console.log(it.next(12)); // => `{value: 8, done: false}`
console.log(it.next(13)); // => `{value: 42, done: true}`

上面这个示例就是一个 Generator 函数，

我们来分析其执行过程: 首先 Generator 函数调用时它会返回一个迭代器

当执行第一次 next 时，传参会被忽略，并且函数暂停在 yield (x + 1) 处，所以 返回 5 + 1 = 6

当执行第二次 next 时，传入的参数等于上一个 yield 的返回值，如果你不传参， yield 永远返回 undefined。此时 let y = 2 _ 12，所以第二个 yield 等于 2 _ 12 / 3 =8

当执行第三次 next 时，传入的参数会传递给 z，所以 z = 13, x = 5, y = 24，相 加等于 42

`yield`实际就是暂缓执行的标示，每执行一次 next() ，相当于指针移动到下一个`yield`位置

### Generator 函数的简单实现

```js
function generator(cb) {
  return (function () {
    var object = {
      next: 0,
      stop: function () `{}`
    };

    return {
      next: function () {
        var ret = cb(object);
        if (ret === undefined) return `{ value: undefined, done: true }`;
        return {
          value: ret,
          done: false
        };
      }
    };
  })();
}
```

## async/await

Generator 函数的语法糖。有更好的语义、更好的适用性、返回值是 Promise 。

await 相比直接使用 Promise 来说，优势在于处理 then 的调用链，能够更清晰准确的写出代码。缺点在于滥用 await 可能会导致性能问题，因为 await 会阻塞代码，也许之后的异步代码并不依赖于前者，但仍然需要等待前者完成，导致代码失去了并发性，此时更应该使用 Promise.all。

一个函数如果加上 async ，那么该函数就会返回一个 Promise

### async/await 原理

Generator 函数+自动执行器

## ajax

异步通信，通过直接由 js 脚本向服 务器发起 http 通信，然后根据服务器返回的数据， 更新网页的相应部分，而不用刷新整个页面的一种 方法。

```js
//1:创建Ajax对象
var xhr = window.XMLHttpRequest?new XMLHttpRequest():new ActiveXOb ject('Microsoft.XMLHTTP');// 兼容IE6及以下版本
//2:配置 Ajax请求地址
xhr.open('get','index.xml',true);
//3:发送请求
xhr.send(null); // 严谨写法
//4:监听请求，接受响应
xhr.onreadysatechange=function(){
          if(xhr.readySate==4&&xhr.status==200 || xhr.status==304 )
               console.log(xhr.responsetXML)
}
```

### Promise 封装

```js
function getJSON(url) {
  // 创建一个 promise 对象
  let promise = new Promise(function (resolve, reject) {
    let xhr = new XMLHttpRequest();
    // 新建一个 http 请求
    xhr.open('GET', url, true);
    // 设置状态的监听函数
    xhr.onreadystatechange = function () {
      if (this.readyState !== 4) return;
      // 当请求成功或失败时，改变 promise 的状态
      if (this.status === 200) {
        resolve(this.response);
      } else {
        reject(new Error(this.statusText));
      }
    };
    // 设置错误监听函数
    xhr.onerror = function () {
      reject(new Error(this.statusText));
    };
    // 设置响应的数据类型
    xhr.responseType = 'json';
    // 设置请求头信息
    xhr.setRequestHeader('Accept', 'application/json');
    // 发送 http 请求
    xhr.send(null);
  });
  return promise;
}
```

## 防抖 & 节流(性能优化)

```js
function debounce(Fn, wait) {
  var timer = null;

  return function () {
    var contex = this;
    args = arguments;

    if (timer) {
      clearTimeout(timer);
      timer = null;
    }

    timer = setTimeout(() => {
      Fn.apply(contex, args);
    }, wait);
  };
}

function throttle(Fn, delay) {
  var preTime = Date.now();

  return function () {
    var context = this,
      args = arguments,
      nowTime = Date.now();

    if (nowTime - preTime >= delay) {
      preTime = Date.now();
      return Fn.apply(context, args);
    }
  };
}
```

## 实现数组扁平化的几种方式

### 递归

```js
function flatten(arr) {
  let result = [];

  for (let i = 0; i < arr.length; i++) {
    if (Array.isArray(arr[i])) result = result.concat(flatten(arr[i]));
    else result.push(arr[i]);
  }
  return result;
}
```

### 扩展云算法实现

```js
function flatten(arr) {
  while (arr.some((item) => Array.isArray(item))) {
    arr = [].concat(...arr);
  }
  return arr;
}
```

### reduce 迭代

```js
function flatten(arr) {
  return arr.reduce(
    (prev, next) => prev.concat(Array.isArray(next) ? flatten(next) : next),
    []
  );
}
```
