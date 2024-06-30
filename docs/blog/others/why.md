---
sidebar: false
---

## Q1.标记清除算法是如何处理循环引用的 ❓

1.引用计数算法及问题

垃圾回收器会为每个对象维护一个引用计数器，记录当前对象被引用的次数。当一个对象的引用被释放时，引用计数器减一。当**引用计数器为 0**时，表示该对象**不再被引用**，即为垃圾对象，垃圾回收器会立即回收并释放其占用的内存空间。

‼️ 引用计数算法无法处理循环引用的情况，可能会导致内存泄漏：

> 举个例子：假设对象 A，包含一个指向对象 B 的引用，而对象 B 也包含一个指向对象 A 的引用。此时，由于对象 A 和 B 互相引用的次数不为 0，垃圾回收器就无法清除这两个对象，导致内存泄漏。

**标记清除算法的处理方式**

在标记阶段，垃圾回收器会将循环引用的对象标记为“可达”，并且在遍历过程中**不会重复标记**已经被标记过的对象。

在清除阶段，由于循环引用的对象被标记为“可达”，因此不会被清除，从而保证了循环引用的正确处理。

> 举个例子：假设对象 A，包含一个指向对象 B 的引用，而对象 B 也包含一个指向对象 A 的引用。在标记阶段，垃圾回收器会从**根对象**开始遍历内存中的所有对象，标记对象 A 和 B 为可达对象，并且标记它们是循环引用的对象。对于循环引用的情况，只要有一个对象不再被根或其他活动对象所引用，垃圾收集器就会清理这个对象，包括它引用的循环中的另一个对象。

## Q2.为什么尾递归可以避免栈溢出 ❓

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

## Q3.如何分析内存或排查内存泄漏 ❓

**Memory(chrome devtools)**

![](/images/js-img/memory.png)

![](/images/js-img/performance.png)

注意：打开 Chrome 的无痕模式，避免 Chrome 插件影响测试内存占用情况

## Q4.5 个 6 和 1、2、3、4、5 的问题 ❓

```js
for (var i = 1; i <= 5; i++) {
  setTimeout(function () {
    console.log(i);
  }, 0);
} // 6 6 6 6 6
```

对输出结果的理解：

1️⃣ `setTimeout`是宏任务，由于 js 中单线程的 eventloop 机制，在主线程同步任务执行完之后才去执行宏任务，因此循环结束后`setTimeout`的回调才依次执行。

2️⃣ `setTimeout`函数也是一种闭包，想上找 父级作用域链是`window`,变量 i 是`window`的全局变量，开始执行`setTimeout`之前变量 i 已经是 6，所以最后的输出都是 6

如何按顺序依次输出 1、2、3、4、5 呢 ❓

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

方式二：使用`let` 块级作用域（相当于匿名函数）

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

## Q5.为什么 `eval()`、`with()`被认为是不推荐使用的特性 ❓

- `eval()`：可以执行传递给它的字符串作为 JS 代码并将结果插入到原位置，**容易被恶意植入**。

示例: `eval("x=10;y=20;document.write(x*y)");`

- `with()`：允许在指定的对象作用域中执行代码块，可以省略对象名称的重复引用。

示例

```js
var obj = { x: 10, y: 20 };

with (obj) {
  console.log(x + y); // 输出 30
}
```

性能问题

①js 引擎会在编译阶段进行性能优化，其中部分优化依赖于对词法作用域的静态分析；

②eval 函数和 with 关键字会欺骗词法作用域（eval 动态修改，with 凭空创建新的），从而导致词法作用域中变量和函数的定义位置无法事先确定；

③js 引擎发现代码中的 eval 和 with 后，会判别无法事先做优化，故直接放弃

## Q6.如果对一个函数进行多次 `bind` ，函数的 this 会如何改变 ❓

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

## Q6.`call`、`apply`、`bind` 原理及实现 ❓

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
  console.log('person age:', this.age, age);
  console.log('person this:', this);
}

Person.prototype.say = function () {
  console.log('say');
};

var obj = { name: 'ttt', age: 12 };
var bindFn = Person.myBind(obj, '修改');
bindFn();
//person name: 修改
// person age: 12 undefined
// person this: { name: 'ttt', age: 12 }

bindFn(999);
// person name: 修改
// person age: 12 999
// person this: { name: 'ttt', age: 12 }

bindFn.prototype.say(); // say

const newFn = new bindFn('构造函数');
// person name: 修改
// person age: undefined 构造函数
// person this: Person {}
newFn.say(); // say

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

## Q7.new 的过程实现 ❓

new 关键词的主要作用就是**执行构造函数，返回一个实例对象**

### new 操作符做了哪些事

- 以构造器的 prototype 属性为原型（区分私有字段[[prototype]]），创建新对象

- 将 this 和调用参数传给构造器，执行

- 如果构造器返回的是对象，则返回，否则返回第一步创建的对象

```js
function myNew(constructor, ...args) {
  // 创建一个新对象，继承构造函数的原型对象
  let newObj = Object.create(constructor.prototype);
  // 执行构造函数，为新对象添加属性，获取函数执行结果result
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

## Q8.`module.exports`和`exports`有区别吗 ❓

- 在 module 对象中，包含 exports 属性，而我们就是通过这个属性（module.exports），向外暴露(共享)成员的。

- 在默认情况下，exports 和 module.exports 指向的是同一个对象`var exports = module.exports;`

- 注意：不能对 exports 直接赋值，这样会导致`module.exports`和`exports`指向不同的引用。

## Q9.commonJS 和 ES Module 中模块化有哪些区别 ❓

- 语法：

  - commonJS 使用`require`、`module.exports`和`exports`关键字。
  - ES Module 使用`import`和`export`

- 运行时：

  - ESModule 支持异步加载，可以与 import()一起使用，实现代码分割和懒加载。

    ```js
    const importPromise = import('./foo.js');
    importPromise.then((res) => {
      console.log(res.name, res.age);
    });
    ```

  - CommonJS 模块是同步加载的。

- 加载机制：

  - ESModule 是**静态**的，**import 和 export 必须位于模块的顶层作用域**。ESModule 可以进行静态分析，从而实现树摇（tree shaking）等优化。
  - CommonJS 是**动态**的，require 可以在代码的任何地方调用，可以根据条件动态加载模块。

## Q10.为什么有的编程规范要求用`void 0`代替`undefined`❓

任何变量在赋值前是 `Undefined` 类型、值为 undefined。在 JS 设计中，`undefined`不是关键字，而是变量。为避免无意篡改值，建议使用`void 0`代替`undefined`值。

在实际编程时，可以将变量先赋值为`null`,`null`表示：定义了但是为空值。一般不会把变量赋值为 `undefined`，这样可以保证所有值为`undefined`的变量，都是从未赋值的自然状态。

## Q11.0.1+0.2 不等于 0.3❓

`console.log(0.1 + 0.2 == 0.3); // false`

浮点数运算的精度问题导致等式两侧的结果并不是严格相等，正确的比较方法是使用 JS 提供的最小精度值`Number.EPSILON`

`console.log(Math.abs(0.1 + 0.2 - 0.3) <= Number.EPSILON); // true`

## Q12.遍历中如何取到`symbol`类型 ❓

常见的对象遍历方法

- `for (let xx in obj)`：【es5】遍历对象的可枚举属性，包括继承（原型上）的属性，遍历顺序不确定。
- `for (let xx of obj)`：【es6】遍历可迭代对象(数组、字符串、Set、Map 等)，不会遍历非述职属性或原型上的属性。**如果没有 `Iterator`接口，无法使用 for of 遍历**。原型部署了 Iterator 接口的数据结构有三种，具体包含四种，分别是数组，类似数组的对象，Set 和 Map 结构。
- `Object.keys(obj)`：返回包含 key 的数组
- `Object.values(obj)`：返回包含 value 的数组
- `Object.getOwnPropertyNames()`：返回包含 key 的数组

如何遍历到`Symbol`

- `Object.getOwnPropertySymbols()`：返回对象中只包含 symbol 类型 key 的数组
- **`Reflect.ownKeys()`** ：返回对象中所有类型 key 的数组（包含 symbol）

## Q13.递归遍历实现深拷贝（for in）❓

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

## Q14.为什么给对象添加的方法能用在基本类型上 ❓

运算符提供了装箱操作，它会根据基础类型构造一个临时对象，使得我们能在基础类型上调用对应对象的方法。

📄**理解装箱转换 & 拆箱转换**

包装类与原始值转换过程叫做「装箱」和「拆箱」，装箱(boxing)是将值类型包装为对象类型，拆箱(unboxing)是将对象类型转换为类型。

每一种基本类型 `Number`、`String`、`Boolean`、`Symbol` 在对象中都有对应内置的类。装箱机制会频繁产生临时对象，在一些对性能要求较高的场景下，我们应该尽量避免对基本类型做装箱转换。

装箱操作的**具体步骤**为：创建该类型的实例，在实例上调用指定的方法，销毁实例。

拆箱转换：在 JavaScript 标准中，规定了 `[Symbol.ToPrimitive]` 函数（es6），允许对象通过重写`toPrimitive` 函数来实现转换（优先级最高）。它是对象类型到基本类型的转换，
如果没有`ToPrimitive`函数，会先后尝试调用 `valueOf` 和 `toString` 来获得拆箱后的基本类型。如果 `valueOf` 和 `toString` 都不存在，或者没有返回基本类型，则会产生类型错误 TypeError。

## Q15.手写实现 Promise❓

```js
function myPromise(constructor) {
  let self = this;
  self.status = 'pending'; // 初始化状态
  self.value = undefined; // 状态为resolved的value
  self.reason = undefined; // 状态为rejected的reason

  function resolve(value) {
    if (self.status === 'pending') {
      self.value = value;
      self.status = 'resolved';
    }
  }

  function reject(reason) {
    if (self.status === 'pending') {
      self.reason = reason;
      self.status = 'rejected';
    }
  }

  // 捕获constructor异常
  try {
    constructor(resolve, reject);
  } catch (e) {
    reject(e);
  }
}

// 定义链式调用的then方法
myPromise.prototype.then = function (onFullfilled, onRejected) {
  let self = this;
  switch (self.status) {
    case 'resolved':
      onFullfilled(self.value);
      break;
    case 'rejected':
      onRejected(self.reason);
      break;
    default:
  }
};
```

## Q16.Load 和 DOMContentLoaded 有什么区别 ❓

- Load 事件触发代表页面中的 DOM ， CSS ， JS ，图片已经全部加载完毕。
- DOMContentLoaded 事件触发代表初始的 HTML 被完全加载和解析，不需要等待 CSS ， JS ，图片加载。

## Q17.重绘和重排有什么区别，如何优化 ❓

重绘是当节点需要更改外观而不会影响布局的，比如改变 color 就叫称为重绘

重排是布局或者几何属性需要改变。

例如：添加或者删除可见的 DOM 元素; 元素尺寸改变——边距、填充、边框、宽度和高度; 内容变化，比如用户在 input 框中输入文字; 浏览器窗口尺寸改变——resize 事件发生时 计算 offsetWidth 和 offsetHeight 属性等等

重排必定发生重绘，重绘不一定引发重排。

**优化：**

- 使用 `visibility` 替换 `display:none`

- 尽量避免使用 table 布局，table 布局中一个小改动很容易造成 table 的重新布局

- css 选择符自右向左匹配查找，避免 dom 深度过深

## Q18.网页的加载流程是怎样的 ❓

- 当打开网址时，浏览器会从服务器中获取到 HTML 内容
- 浏览器获取到 HTML 内容后，就开始从上到下解析 HTML 的元素
- `head`元素内容会先被解析，此时浏览器还没开始渲染页面。
  - `head`元素里有用于描述页面元数据的 `meta` 元素，还有一些`link`元素涉及外部资源(如 图片、css 样式等)，此时浏览器会去获取这些外部资源。`head`元素中还包含着不少的`script`元素，这些`script`元素通过 src 属性指向外部资源
- 当浏览器解析到 `script` 元素时，会暂停解析并下载 JavaScript 脚本
- 当 JavaScript 脚本下载完成后，浏览器的控制权转交给 JavaScript 引擎。当脚本执行完成后，控制权会交回给渲染引擎，渲染引擎继续往下解析 HTML 页面
- `body`元素内容开始被解析，浏览器开始渲染页面

## Q19.性能优化

- 选择合适的缓存策略
  - 强缓存（Expires 和 Cache-Control(优先级高于 Expires)）
  - 协商缓存（`Last-Modified` / `If-Modified-Since` 或 `ETag` / `If-None-Match`）
  - 对于大部分的场景都可以使用强缓存配合协商缓存解决，但是在一些特殊的地方可能需要选择特殊的缓存策略
    - 不需要缓存的资源：`Cache-control: no-store`
    - 频繁变动的资源：`Cache-Control: no-cache` + Etag
  - 对于代码文件，通常使用 Cache-Control: max-age=31536000 并配合策略缓存使用，对文件进行指纹处理，一旦文件名变动就会立刻下载新的文件
- [preload]预加载：对于不需要立即用到，但是希望尽快获取的资源。预加载即声明式的 fetch ，强制浏览器请求资源，并且不会阻塞 onload 事件。预加载可以一定程度上降低首屏的加载时间，因为可以将一些不影响首屏但重要的文件延后加载，唯一缺点就是兼容性不好。

  `<link rel="preload" href="http://example.com">`

- [prerender]预渲染：将下载的文件预先在后台渲染。
  `<link rel="prerender" href="http://example.com">`
- 对于非首屏的资源，可以使用 defer 或 async 的方式引入
  - [defer]：有顺序依赖
  - [async]：脚本加载完执行
- 图片懒加载
- webpack 优化：
  - 使用 es6 模块开启 tree shaking
  - 按路由拆分代码，按需加载
  - 打包出来的文件添加 hash，实现浏览器缓存文件
