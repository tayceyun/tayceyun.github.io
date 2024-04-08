---
sidebar: auto
tags:
  - ts
---

## 基础

### 变量类型推导

- 声明一个标识符时，如果有直接进行赋值，会根据赋值类型推导除标识符的类型注解
- let 进行类型推导，推导出来的是通用类型
- const 进行类型推导，推导出来的是字面量类型
- 如果对象使用字面量表示，会触发 ts 严格字面量检查

```typescript
const point: {
  x: number;
  y: number;
} = {
  x: 1,
  y: 1,
  z: 1 // 报错
};
```

ts 对字面量进行严格检查的目的，主要是防止拼写错误

```typescript
type Options = {
  title: string;
  darkMode?: boolean;
};

const obj: Options = {
  title: '我的网页',
  darkmode: true // 报错
};

// 规避严格字面量检查，可以使用中间变量
let myOptions = {
  title: '我的网页',
  darkmode: true
};

const obj: Options = myOptions;

// 也可使用类型断言规避严格字面量检查
const obj: Options = {
  title: '我的网页',
  darkmode: true
} as Options;

// 如果允许字面量有多余属性，可以在类型里面定义一个通用属性
// tsconfig.json 文件中：
// compilerOptions-->suppressExcessPropertyErrors:关闭多余属性检查
let x: {
  foo: number;
  [x: string]: any;
};

x = { foo: 1, baz: 2 };
```

### 数据类型

```typescript
// 基础数据类型
let message: string = 'hello';
let num: number = 1;
let flag: boolean = false;
let initNum: null = null;
let data: undefined = undefined;

// 如果没有声明类型的变量，被赋值为undefined或null，它们的类型会被推断为any
let a = undefined; // any
const b = undefined; // any
let c = null; // any
const d = null; // any
// 如果打开编译选项strictNullChecks：赋值为undefined的变量会被推断为undefined类型，赋值为null的变量会被推断为null类型
let aa = undefined; // undefined
const bb = undefined; // undefined
let cc = null; // null
const dd = null; // null

// 值类型
// ts对const命令声明的变量，如果代码里面没有注明类型，就会推断该变量是值类型。
// x 的类型是 "https"
const x = 'https';

// number是5的父类型, y的类型是 string
const y: string = 'https';

// 父类型不能赋值给子类型
const x: 5 = 4 + 1; // 报错

// 如果要让子类型可以赋值为父类型的值，用类型断言
const z: 5 = (4 + 1) as 5; // 正确

// 子类型可以赋值给父类型
let x: 5 = 5;
let y: number = 4 + 1;

x = y; // 报错
y = x; // 正确

// 复杂数据类型
// 数组类型
// 第一种写法
let names: string[] = ['text', 'test'];
let arr: (number | string)[];

// 第二种写法：ts内置的array接口，泛型写法
let nicknames: Array<string> = ['text', 'test'];
let arr: Array<number | string>;

// 使用方括号读取数组成员的类型
type Names = string[];
type Name = Names[0]; // string
// 数组成员的索引类型是number，读取成员类型可写成如下：
type Names = string[];
type Name = Names[number]; // string

// 多维数组：T[][]（二维数组），T是最底层数组成员的类型
var multi: number[][] = [
  [1, 2, 3],
  [23, 24, 25]
];

// 对象类型
// 使用关键字type
type InfoType = {
  name: string;
  age: number;
};

const info: InfoType = {
  name: 'test',
  age: 1
};

// Symbol
const person: symbol = Symbol('person');
// symbol子类型:unique symbol 表示单个的、某个具体的symbol值，只能用const声明，使用let声明会报错
const x: unique symbol = Symbol();

// const命令为变量赋值 Symbol 值时，变量类型默认就是unique symbol，所以类型可以省略不写。

// 函数
// 声明函数时，可以在每个参数后添加类型注解，以声明函数接受的参数类型
function sum(num1: number, num2: number): number {
  return num1 + num2;
}

// 任何其他类型的变量都可以赋值为undefined或null
// js中：变量如果等于undefined就表示还没有赋值，如果等于null就表示值为空
let age: number = 24;

age = null; // 正确
age = undefined; // 正确

// ts提供了strictNullChecks编译选项，只要打开这个选项，undefined和null就不能赋值给其他类型的变量（除了any类型和unknown类型）
```

### 上下文类型

![](/images/ts-img/上下文类型.jpg)

### any 类型

TypeScript 提供了一个编译选项`noImplicitAny`，打开该选项，只要推断出 any 类型就会报错

注意：**即使打开了 noImplicitAny，使用 let 和 var 命令声明变量，但不赋值也不指定类型，是不会报错的**。

```typescript
var x; // 不报错
let y; // 不报错
```

由于这个原因，建议使用 let 和 var 声明变量时，如果不赋值，就一定要显式声明类型，否则可能存在安全隐患。

any 类型会“污染”其他变量。它可以赋值给其他任何类型的变量（因为没有类型检查），导致其他变量出错。

```typescript
let x: any = 'hello';
let y: number;

y = x; // 不报错

y * 123; // 不报错
y.toFixed(); // 不报错
```

### unknown 类型

- 和 any 类型有点类似，但 unknown 类型默认情况下在上面进行任意的操作都是非法的。要求必须进行类型校验（缩小），才能根据缩小之后的类型，进行对应的操作。

```typescript
if (typeof foo === 'string') {
  console.log(`output->foo.length`, foo.length);
}
```

- `unknown`类型的变量，不能直接赋值给其他类型的变量（除了`any`类型和`unknown`类型）

```typescript
// 变量v是unknown类型，赋值给any和unknown以外类型的变量都会报错
let v: unknown = 123;

let v1: boolean = v; // 报错
let v2: number = v; // 报错
```

- 不能直接调用`unknown`类型变量的方法和属性

```typescript
let v1: unknown = { foo: 123 };
v1.foo; // 报错

let v2: unknown = 'hello';
v2.trim(); // 报错

let v3: unknown = (n = 0) => n + 1;
v3(); // 报错
```

- `unknown`类型变量能够进行的运算是有限的，只能进行**比较运算**（运算符`==`、`===`、`!=`、`!==`、`||`、`&&`、`?`）、取反运算（运算符`!`）、`typeof`运算符和`instanceof`运算符这几种，其他运算都会报错。

```typescript
let a: unknown = 1;

a + 1; // 报错
a === 1; // 正确
```

### void

- 如果一个函数没有返回值，返回值类型即为 void 类型；

- 如果返回值是 void 类型，void 类型允许返回`undefined`或`null`,如果打开了`strictNullChecks`编译选项，那么 void 类型只允许返回`undefined`；

- 当基于上下文的类型推导 推导出返回类型为 void 时，并不会强制函数一定不能返回内容

```typescript
// 函数类型
type FooType = () => void;
const fooFunc: FooType = () => {};
```

### never

实际开发中只有进行类型推导时，会自动推导出来是 never 类型，但很少使用

```typescript
// 封装工具或框架时，对工具进行扩展时,使用never会进行报错
function handleMsg(msg: string | number) {
  switch (typeof msg) {
    case 'string':
      console.log(`output->string`);
    case 'number':
      console.log(`output->number`);
    default:
      const check: never = msg;
      console.log(`output->`, check);
  }
}

handleMsg('11');
handleMsg(true); // 报波浪线
```

`never`类型的一个重要特点是，可以赋值给任意其他类型。任何类型都包含了`never`类型。因此，`never`类型是任何其他类型所共有的，ts 把这种情况称为“底层类型”（bottom type）。

ts 有两个“顶层类型”（`any`和`unknown`）

```typescript
// 函数f()会抛错，所以返回值类型可以写成never，即不可能返回任何值。各种其他类型的变量都可以赋值为f()的运行结果（never类型）。
function f(): never {
  throw new Error('Error');
}

let v1: number = f(); // 不报错
let v2: string = f(); // 不报错
let v3: boolean = f(); // 不报错
```

### 只读数组 const 断言

声明只读数组

`const arr:readonly number[] = [0, 1];`

TypeScript 提供了两个专门的泛型，用来生成只读数组的类型

```typescript
const a1: ReadonlyArray<number> = [0, 1];

const a2: Readonly<number[]> = [0, 1];
```

使用 const 断言 生成只读数组

```typescript
const arr = [0, 1] as const;

arr[0] = [2]; // 报错
```

readonly 关键字不能与数组的泛型写法一起使用

```typescript
// 报错
const arr: readonly Array<number> = [0, 1];
```

### tuple 类型（元组）

元组数据解构中可以存放不同的数据类型，取出的 item 有明确的类型

元组中每个元素都有自己特定的类型，根据索引值获取到的值可以确定对应的类型

`const information: [string, number, number] = ['why', 1, 2];`

```typescript
function useState(initial: number): [number, (newVal: number) => void] {
  let stateValue = initial;
  function setValue(newValue: number) {
    stateValue = newValue;
  }

  return [stateValue, setValue];
}

const [stateValue, setValue] = useState(111);
```

元组成员的类型可添加问号后缀（`?`），表示该成员可选（**问号只能用于元组的尾部成员**）

`let a:[number, number?] = [1];`

使用扩展运算符（`...`），表示不限成员数量的元组

```typescript
type NamedNums = [string, ...number[]];

const a: NamedNums = ['A', 1, 2];
const b: NamedNums = ['B', 1, 2, 3];
```

扩展运算符用在元组的任意位置都可以，但是它后面只能是数组或元组

```typescript
type t1 = [string, number, ...boolean[]];
type t2 = [string, ...boolean[], number];
type t3 = [...boolean[], string, number];
```

只读元组

```typescript
type t = readonly [number, string];
type t = Readonly<[number, string]>;
```

### 联合类型

- 是由两个或者多个其他类型组成的类型
- 可以是这些类型中的任何一值
- 联合类型中的每一个类型被称为联合成员(union's members)
  `let myVar: string | number;`

### 类型别名

```typescript
type BasicLength = number | string;

function transferLength(length: BasicLength) {}
```

### typeof

```typescript
let a = 1;
let b:typeof a; // ts的类型运算

// js的值运算
if (typeof a === 'number') {
  b = a;
// 编译后，js的typeof会保留，ts的typeof类型运算会被全部删除

// 编译后代码
let a = 1;
let b;
if (typeof a === 'number') {
    b = a;
}

// ts规定：typeof的参数只能是标识符，不能是需要运算的表达式
type T = typeof Date(); // 报错

// typeof命名的参数不能是类型
type Age = number; // Age是类型别名,用作typeof命令的参数会报错
type MyAge = typeof Age; // 报错

// 可以使用父类型的地方，都可以使用子类型，反过来不行
let a:'hi' = 'hi';
let b:string = 'hello';

b = a; // 正确
a = b; // 报错
```

如果**一个变量要套用另一个函数类型**，可以使用 typeof 运算符

扩展：任何需要类型的地方，都可以使用`typeof`运算符从一个值获取类型

```typescript
function add(x: number, y: number) {
  return x + y;
}

const myAdd: typeof add = function (x, y) {
  return x + y;
};
```

### interface(接口)

多个同名接口会合并成一个接口

规则例外：同名方法之中，如果有一个参数是字面量类型，字面量类型有更高的优先级

```typescript
interface pointType {
  x: number;
  name: string;
}
```

```typescript
interface A {
  f(x: 'foo'): boolean;
}

interface A {
  f(x: any): void;
}

// 等同于
interface A {
  f(x: 'foo'): boolean;
  f(x: any): void;
}
```

#### 对象方法写法

```typescript
// 写法一
interface A {
  f(x: boolean): string;
}

// 写法二
interface B {
  f: (x: boolean) => string;
}

// 写法三
interface C {
  f: { (x: boolean): string };
}

// 属性名可以采用表达式
const f = 'f';

interface A {
  [f](x: boolean): string;
}
```

#### 声明独立的函数

```typescript
interface Add {
  (x: number, y: number): number;
}

const myAdd: Add = (x, y) => x + y;
```

#### 声明构造函数

```typescript
interface ErrorConstructor {
  new (message?: string): Error;
}
```

#### 支持多重继承

```typescript
// 如果子接口与父接口存在同名属性，那么子接口的属性会覆盖父接口的属性

interface Style {
  color: string;
}

interface Shape {
  name: string;
}

interface Circle extends Style, Shape {
  radius: number;
}
```

#### interface 支持继承 type

```typescript
type Country = {
  name: string;
  capital: string;
};

interface CountryWithPop extends Country {
  population: number;
}
```

#### interface 支持继承 class

```typescript
class A {
  x: string = '';

  y(): boolean {
    return true;
  }
}

interface B extends A {
  z: number;
}
```

### interface 和 type 区别

- type 类型使用范围更广，可以声明基本数据类型，接口类型只能声明对象（包括数组、函数等）
- 声明对象时，interface 可以多次声明,多次声明均有效，type 类型不行
- interface 支持继承，可以被类实现，type 不支持继承
- 对于非对象类型定义使用 type，对象类型使用 interface
- `type`定义的对象类型如果想要添加属性，只能使用`&`运算符，重新定义一个类型

```typescript
type Animal = {
  name: string;
};

type Bear = Animal & {
  honey: boolean;
};
```

```typescript
interface IPointType {
  x: number;
  name: string;
}

interface IPoint extends IPointType {
  z: number;
}

const point: IPoint = {
  x: 1,
  z: 2,
  name: 'test'
};

// 支持继承
interface IPerson extends IPoint {
  age: number;
}

// 被类实现
class Person implements IPerson {
  x: 11;
  z: 22;
  name: 'test';
  age: 123;
}
```

- `interface`不能包含属性映射（mapping），`type`可以

```typescript
interface Point {
  x: number;
  y: number;
}

// 正确
type PointCopy1 = {
  [Key in keyof Point]: Point[Key];
};

// 报错
interface PointCopy2 {
  [Key in keyof Point]: Point[Key];
};
```

- this 关键字只能用于 interface

```typescript
// 正确
interface Foo {
  add(num: number): this;
}

// 报错
type Foo = {
  add(num: number): this;
};
```

- type 可以扩展原始数据类型，interface 不行

```typescript
// 正确
type MyStr = string & {
  type: 'new';
};

// 报错
interface MyStr extends string {
  type: 'new';
}
```

### 交叉类型

两种（多种）类型要同时满足

```typescript
interface IPage {
  pageNum: number;
  pageChange: (pageNum: number) => void;
}

interface ISize {
  size: number;
  total: number;
}

const pagination: IPage & ISize = {
  pageNum: 1,
  size: 10,
  total: 100,
  pageChange: (num) => {
    console.log(`output->num`, num);
  }
};
```

#### 类型断言

```typescript
const imgE1 = document.querySelector('.img') as HTMLImageElement;
imgE1.src = 'http://122';
```

#### 非空类型断言

```typescript
// 可选链
console.log(`output->existInfo?.friend.name`, existInfo.friend?.name);
// 类型缩小
if (existInfo.friend) {
  existInfo.friend.name = 'orange';
}
// 非空断言--只有确保一定有值的情况下才可使用
existInfo.friend!.name = 'orange';
```

### 字面量类型

将多个字面量类型联合

`type Direction = 'left' | 'right' | 'down';`

**示例**：info 对象在进行字面量推理时，info 其实是一个`{url:string,method:string}`,所以无法将 string 赋值给一个字面量类型

```typescript
const info = { url: '', method: 'GET' };

function request(url: string, method: 'GET' | 'POST') {
  console.log(url, method);
}

request(info.url, info.method); // info.method报波浪线
```

**解决方法一**：使用`as const`

1.`request(info.url,info.method as 'GET')`

2.`const info = { url: '', method: 'GET' } as const;`

### 类型缩小

- `typeof`
- 平等缩小（===、!==）
- instanceof
- in

“类型缩小”是 ts 处理联合类型的标准方法

#### in 运算符

**用于确定对象是否具有带名称的属性**

如果指定的属性在指定的对象或其原型链中，则 in 运算符返回 true

```typescript
interface ISwim {
  swim: () => void;
}

interface IRun {
  run: () => void;
}

function move(animal: ISwim | IRun) {
  if ('swim' in animal) {
    animal.swim();
  } else if ('run' in animal) {
    animal.run();
  }
}
```

### 函数类型

#### 函数类型表达式

```typescript
type BarType = (num: number) => number;

const bar: BarType = (arg: number): number => {
  return 1;
};
```

#### 函数参数个数问题

ts 对传入的函数类型的参数个数不进行检测，对于传入的函数类型的多余参数会被忽略掉

```typescript
type BarFunc = (num: number, num2: number) => number;

function calc(fn: BarFunc) {}

calc(() => 123);
```

#### 函数调用签名（call signatures）

函数表达式不能支持声明属性，如果想描述一个带有属性的函数，可以在对象类型中写调用签名。

如果只描述函数类型本身（函数可以被调用），使用函数类型表达式

如果在描述函数作为对象可以被调用，同时也有其他属性时，使用函数调用签名

```typescript
interface IBar {
  name: string;
  // 调用签名
  (num: number): number;
}

const bar: IBar = (num: number): number => {
  return num;
};

bar.name = '测试';
bar(111);
```

js 函数可以使用 new 操作符，当被调用时，ts 会认为是构造函数，因为该操作会产生一个新对象

```typescript
class Person {
  name: string;
  constructor(name: string) {
    this.name = name;
  }
}

interface IPerson {
  new (name: string): Person;
}

function factory(newObj: IPerson) {
  return new newObj('text');
}
```

#### 参数可选类型

```typescript
// 可选参数是 ：数据类型 | undefined 联合类型
function foo(x: number, y?: number) {
  if (y !== undefined) {
    console.log(`output->y`, y);
  }
}
```

#### 函数参数默认值

```typescript
// 有默认值的情况下，参数的类型注解可以省略
function foo(x: number, y = 1) {
  console.log(`output->y`, y);
}

foo(10);
foo(10, 55);
foo(10, undefined); // 可以传入undefined
```

#### 剩余参数

```typescript
// 剩余参数语法允许将一个不定量的参数放到一个数组中
function sum(...sums: number[]) {
  let total = 0;
  for (const num of sums) {
    total += num;
  }
  return total;
}

const result = sum(10, 20, 30);

function foo(...arr: (number | string)[]) {
  console.log(`output->...arr`, ...arr);
}
```

#### 函数重载

有些函数可以接受不同类型或不同个数的参数，并且根据参数的不同，会有不同的函数行为。这种根据参数类型不同，执行不同逻辑的行为，称为函数重载（function overload）。

```typescript
// 可以编写不同的重载签名来表示函数可以以不同方式调用
// 一般是编写两个以上的重载签名，再写一个通用函数实现
// 在调用函数时，会根据传入的参数类型来决定执行函数体时，执行哪个函数的重载签名
function add(arg1: number, arg2: number): number;
function add(arg1: string, arg2: string): string;

function add(arg1, arg2) {
  return arg1 + arg2;
}

function add2(x: number, y: number): number;
function add2(x: any[], y: any[]): any[];
function add2(x: number | any[], y: number | any[]): number | any[] {
  if (typeof x === 'number' && typeof y === 'number') {
    return x + y;
  } else if (Array.isArray(x) && Array.isArray(y)) {
    return [...x, ...y];
  }

  throw new Error('wrong parameters');
}
```

函数重载的类型声明与函数实现不能存在冲突

```typescript
// 报错
function fn(x: boolean): void;
function fn(x: string): void;
function fn(x: number | string) {
  console.log(x);
}
```

重载声明的排序很重要，因为 TypeScript 是按照顺序进行检查的，一旦发现符合某个类型声明，就不再往下检查了，所以类型最宽的声明应该放在最后面，防止覆盖其他类型声明。

```typescript
function f(x: any): number;
function f(x: string): 0 | 1;
function f(x: any): any {
  // ...
}

const a: 0 | 1 = f('hi'); // 报错
```

对象的方法也可以使用重载

```typescript
class StringBuilder {
  #data = '';

  add(num: number): this;
  add(bool: boolean): this;
  add(str: string): this;
  add(value: any): this {
    this.#data += String(value);
    return this;
  }

  toString() {
    return this.#data;
  }
}
```

在实际开发中，尽量使用联合类型 而不是重载来实现

`function getLength(a: string | any[]) {}`

#### this 相关的内置工具

1.`ThisParameterType`：提取函数中 this 的类型

2.`OmitThisParameter`：移除一个函数类型 type 的 this 参数类型，并且返回当前的函数类型

3.`ThisType`：标记上下文的 this 类型

```typescript
function foo(this: { name: string }, info: { name: string }) {
  console.log(`output-this`, this, info);
}

type FooType = typeof foo;
// 1.提取FooType类型中this的类型,使用内置工具
type FooThisType = ThisParameterType<FooType>;
// 2.剔除this参数类型，剩余的函数类型
type PureFooType = OmitThisParameter<FooType>;

// 3.ThisType 不返回一个转换过的类习惯，被用作标记一个上下文的this类型
interface IState {
  name: string;
  age: number;
}
interface IStore {
  state: IState;
  eating: () => void;
  running: () => void;
}
// 交叉条件,使用ThisType绑定this上下文
const store: IStore & ThisType<IState> = {
  state: {
    name: 'test',
    age: 12
  },
  eating: function () {
    console.log(`output->this.name`, this.name);
  },
  running: function () {
    console.log(`output->this.age`, this.age);
  }
};
```

### 类

示例
![](/images/ts-img/创建类.png)

#### 类的成员修饰符

![](/images/ts-img/修饰符.png)

只读属性：`readonly`

- 只读属性只能在对象初始化期间赋值，此后就不能修改该属性

- `readonly`关键字不能与数组的泛型写法一起使用

报错：`const arr:readonly Array<number> = [0, 1]`

- 如果属性值是对象，`readonly`修饰符不禁止修改该对象属性，但禁止完全替换掉该对象

```typescript
interface Home {
  readonly resident: {
    name: string;
    age: number;
  };
}

const h: Home = {
  resident: {
    name: 'Vicky',
    age: 42
  }
};

h.resident.age = 32; // 正确
h.resident = {
  name: 'Kate',
  age: 23
}; // 报错
```

- 如果一个对象有两个引用，即两个变量对应同一个对象，其中一个变量是可写的，另一个变量是只读的，那么从可写变量修改属性，会影响到只读变量

```typescript
interface Person {
  name: string;
  age: number;
}

interface ReadonlyPerson {
  readonly name: string;
  readonly age: number;
}

let w: Person = {
  name: 'Vicky',
  age: 42
};

let r: ReadonlyPerson = w;

w.age += 1;
r.age; // 43
```

- ts 提供了两个专门的泛型，用来生成只读数组的类型

```typescript
const a1: ReadonlyArray<number> = [0, 1];

const a2: Readonly<number[]> = [0, 1];
```

- 声明只读数组的其它方法：使用`const`断言

`as const`：推断类型时将变量 arr 推断为只读数组

```typescript
const arr = [0, 1] as const;
arr[0] = [2]; // 报错
```

`as const`属于 ts 的类型推断，如果变量明确地声明了类型，那么 ts 会以声明的类型为准

```typescript
const myUser: { name: string } = {
  name: 'Sabrina'
} as const;

myUser.name = 'Cynthia'; // 正确
```

getters 和 setters

```typescript
class Person {
  private _name: string = '';
  constructor(name: string) {
    this._name = name;
  }

  // setter和getter对数据进行拦截,进行逻辑处理
  set setName(newName: string) {
    if (newName === 'test') {
      this._name = 'new';
    } else {
      this._name = newName;
    }
  }
  get name() {
    return this._name;
  }
}
```

#### 参数属性

将一个构造函数参数转成一个同名同值的类属性

在构造参数前添加一个可见性修饰符（public、private、protected、readonly）来创建参数属性，最后这些类属性字段也会得到这些修饰符

```typescript
class Person {
  // 语法糖
  constructor(
    public name: string,
    private age: number,
    readonly height: number
  ) {
    console.log(`output->`, name, age, height);
  }
  running() {
    //   只能在类内部访问
    console.log(`output->this.age`, this.age);
  }
}
```

#### 抽象类`abstract`

```typescript
// 抽象方法必须写在抽象类中,且子类中必须实现抽象方法
// 抽象类不能被实例化 const newShape = new Shape()
abstract class Shape {
  // getArea方法只有声明没有方法体,让子类自己实现;此时可以将方法定义为抽象方法
  abstract getArea();
}

class Circle extends Shape {
  constructor(public radius: number) {
    super();
  }
  getArea() {
    return this.radius ** 2 * Math.PI;
  }
}

class Rectangle extends Shape {
  constructor(public width: number, public height: number) {
    super();
  }
  getArea() {
    return this.width * this.height;
  }
}

function calcArea(shape: Shape) {
  return shape.getArea();
}

calcArea(new Circle(10));
calcArea(new Rectangle(10, 20));
calcArea({ getArea: function () {} });

// 多态: 父类引用指向子类对象;
const shape1: Shape = new Rectangle(10, 20);
```

抽象类的特点总结：
![](/images/ts-img/抽象类.png)

#### 鸭子类型

```typescript
// ts对于类型检测使用的是鸭子类型(只关注属性和行为,不关注是不是对应的类)
class Person {
  constructor(public name: string, public age: number) {}
}

function printPerson(p: Person) {
  console.log(`output->p.name,p.name`, p.name, p.name);
}

printPerson(new Person('text', 10));
printPerson({ name: 'name', age: 12 });
```

类的作用：

① 可以创建类对应的实例对象 ② 类本身可以作为实例的类型 ③ 类也可以当作有一个构造签名的函数

#### 索引签名

```typescript
interface ICollection {
  // 索引签名
  [index: string]: number;
  length: number;
}

function iteratorCollection(collection: ICollection) {
  console.log(`output->`, collection[0]);
  console.log(`output->`, collection[1]);
}
iteratorCollection({ name: 23, length: 1 });
```

#### 接口继承

```typescript
interface IPerson {
  name: string;
  age: number;
}

interface IRun {
  running: () => void;
}

// 从其它接口继承属性
interface IMan extends IPerson {
  slogan: string;
}

// 可以多个接口被类实现
class Person implements IMan, IRun {
  name: string;
  age: number;
  slogan: string;
  sex: string;
  running() {
    console.log(`output->1`, 1);
  }
}

const male: IMan = {
  name: 'orange',
  age: 2,
  slogan: 'a cat'
};
```

#### 抽象类和接口的区别

1.抽象类是事物的抽象，抽象类用来捕捉子类的通用特性，接口通常是一些行为的描述

2.抽象类通常用于一系列关系紧密的类之间，接口只是用来描述一个类应该具有什么行为

3.接口可以被多层实现，而抽象类只能单一继承

4.抽象类中可以有实现体，接口中只能有函数的声明

#### 类、抽象类和接口之间的关系

1.抽象类是对事物的抽象，表达的是 is a 的关系，猫是一种动物（动物就可以定义成一个抽象类）

2.接口是对行为的抽象，表达的是 has a 的关系，猫拥有跑（可以定义一个单独的接口）、爬树（定义单独接口）的行为

### 严格字面量赋值检测

（左一）第一次创建对象字面量时标识为全新的，对于全新的字面量会进行严格的类型检测；

但类型断言或对象字面量的类型扩大时，全新的标记会消失

eg:

定义 info，类型是`IPerson`类型，虽然类型不符合`IPerson`接口，但是定义 p 时，类型检测没有报错

`const obj = {name:"text",age:12,height:100}`传入`printInfo`函数时，不会报错

![](/images/ts-img/字面量定义.png)

### 对象类型索引签名

```typescript
interface IIndexType {
  // 两个索引类型的写法
  // 数字类型索引的类型,必须是字符串类型索引类型的子类型,所有的数字类型都会转成字符串类型去对象中获取内容
  // 如下面的 数字索引的类型string是字符串索引类型any的子类型
  // 如果索引签名中有定义其它属性,其它属性返回的类型必须符合string类型返回的属性
  [index: number]: string;
  [key: string]: any;
}

const names: IIndexType = ['11', '22', '3232'];
const item = names[0];
const forFn = names['22'];
```

### 索引类型:

- 属性名的字符串索引

```typescript
type MyObj = {
  [property: string]: string;
};

const obj: MyObj = {
  foo: 'a',
  bar: 'b',
  baz: 'c'
};
```

- number 和 symbol

```typescript
type T1 = {
  [property: number]: string;
};

type T2 = {
  [property: symbol]: string;
};

type MyArr = {
  [n: number]: number;
};

const arr: MyArr = [1, 2, 3];
// 或者
const arr: MyArr = {
  0: 1,
  1: 2,
  2: 3
};
```

所有的数值属性名都会自动转为字符串属性名，数值索引与字符串索引的值类型不能冲突

```typescript
type MyType = {
  [x: number]: boolean; // 报错
  [x: string]: string;
};
```

属性名的数值索引不宜用来声明数组，因为采用这种方式声明数组，就不能使用各种数组方法以及`length`属性，因为类型里面没有定义这些

```typescript
type MyArr = {
  [n: number]: number;
};

const arr: MyArr = [1, 2, 3];
arr.length; // 报错
```

### 枚举

```typescript
enum Direction {
  UP = 'up',
  DOWN = 'down',
  LEFT = 'left',
  RIGHT = 'right',
  // 位运算
  READ = 1 << 0,
  WRITE = 1 << 1,
  FOO = 1 << 2
}

function turnDirection(direction: Direction) {
  switch (direction) {
    case Direction.LEFT:
      console.log(`output->left`);
      break;
    case Direction.RIGHT:
      console.log(`output->right`);
      break;
  }
}
const d: Direction = Direction.UP;
turnDirection(d);
```

### 泛型

类型参数化：封装一个函数，传入一个参数，并返回这个参数

两种方式调用：

① 可以通过<类型>方式将类型传递给函数

② 通过类型推导，自动推导出传入变量的类型（可能推导出是字面量类型，字面量类型对于函数也同样适用）

```typescript
function bar<Type>(arg: Type) {
  return arg;
}

const res = bar<number>(1);
const res2 = bar<string>('1');
const res3 = bar<{ name: string }>({ name: '1' });

const res4 = bar(21212);
```

```typescript
function useState<Type>(initialState: Type): [Type, (newState: Type) => void] {
  let state = initialState;
  function setState(newState) {
    state = newState;
  }
  return [state, setState];
}

const [count, setCount] = useState<number>(100);
const [message, setMessage] = useState<string>('hello');
const [banners, setBanners] = useState<any[]>([]);
```

```typescript
function foo<Type, Element>(arg1: Type, arg2: Element) {}

foo(10, 20);
foo(10, '123');
foo<string, { name: string }>('abc', { name: 'abc' });
```

#### 常用名称缩写

![](/images/ts-img/缩写.png)

如果有多个类型参数，则使用 T 后面的 U、V 等字母命名，各个参数之间使用逗号（“,”）分隔

```typescript
// 示例:将数组的实例方法map()改写成全局函数，它有两个类型参数T和U。
// 含义是，原始数组的类型为T[]，对该数组的每个成员执行一个处理函数f，将类型T转成类型U，那么就会得到一个类型为U[]的数组

function map<T, U>(arr: T[], f: (arg: T) => U): U[] {
  return arr.map(f);
}

// 用法实例
map<string, number>(['1', '2', '3'], (n) => parseInt(n)); // 返回 [1, 2, 3]
```

#### 泛型接口

```typescript
// 可以设置类型默认值
interface IPerson<T = string> {
  name: T;
  age: number;
  slogan: string;
}

const jack: IPerson<boolean> = {
  name: true,
  age: 12,
  slogan: '测试'
};
```

#### 泛型类

```typescript
class Point<T = number> {
  x: T;
  y: number;
  constructor(x: T, y: number) {
    this.x = x;
    this.y = y;
  }
}

const p2 = new Point<string>('1', 22);
```

#### 泛型约束（generic constraints）

```typescript
interface ILength {
  length: number;
}

function getLength(arg: ILength) {
  return arg;
}
// 此时的info1 info2 info3类型显示为ILength,丢失了原类型
const info1 = getLength('aaa');
const info2 = getLength(['aaa', 'bbb']);
const info3 = getLength({ length: 100 });

// T相当于是一个变量,用于记录本次调用的类型,所以在整个函数的执行周期中,一直保留着参数的类型
function getNewLength<T extends ILength>(args: T): T {
  return args;
}
const newInfo1 = getNewLength('aaa');
const newInfo2 = getNewLength(['aaa', 'bbb']);
const newInfo3 = getNewLength({ length: 100 });
```

```typescript
// 要求传入的参数key必须要是obj中存的key之一
// keyof O-- 代表着O里面所有K的联合类型
function getObjProperty<O, K extends keyof O>(obj: O, key: K) {
  return obj[key];
}

const info = {
  name: 'text',
  age: 12
};

const nickName = getObjProperty(info, 'name');
```

### 映射类型

一个类型需要基于另外一个类型，可以考虑使用映射类型

映射类型建立在索引签名的语法上；就是使用了`PropertyKeys`联合类型的泛型；

其中`PropertyKeys`是通过`keyof`创建，然后循环遍历键名创建一个类型

```typescript
interface IPerson {
  name: string;
  age?: number;
  length?: string;
  slogan?: string;
}

type Mapperson<T> = {
  [key in keyof T]: T[key];
  // 可选属性
  //  [key in keyof T]?: T[key];
  // 只读属性
  //  readonly [key in keyof T]: T[key];

  // 删除?号(属性强制必传)和删除readonly(可以赋值)
  // -readonly [key in keyof T]-?: T[key];
};

type NewPerson = Mapperson<IPerson>;

const mapPerson: NewPerson = {
  name: '1',
  age: 1,
  length: '1',
  slogan: '111'
};
```

#### 映射修饰符--示例

添加 / 移除 可选属性

```typescript
// 添加可选属性
type Optional<Type> = {
  [Prop in keyof Type]+?: Type[Prop];
};

// 移除可选属性
type Concrete<Type> = {
  [Prop in keyof Type]-?: Type[Prop];
};
```

添加 / 移除只读属性

```typescript
// 添加 readonly
type CreateImmutable<Type> = {
  +readonly [Prop in keyof Type]: Type[Prop];
};

// 移除 readonly
type CreateMutable<Type> = {
  -readonly [Prop in keyof Type]: Type[Prop];
};
```

同时增删?和 readonly 这两个修饰符

```typescript
// 增加
type MyObj<T> = {
  +readonly [P in keyof T]+?: T[P];
};

// 移除
type MyObj<T> = {
  -readonly [P in keyof T]-?: T[P];
};
```

#### 键名重映射

```typescript
type A = {
  foo: number;
  bar: number;
};

type B = {
  [p in keyof A as `${p}ID`]: number;
};

// 等同于
type B = {
  fooID: number;
  barID: number;
};
```

复杂示例

```typescript
interface Person {
  name: string;
  age: number;
  location: string;
}

type Getters<T> = {
  [P in keyof T as `get${Capitalize<string & P>}`]: () => T[P];
};

type LazyPerson = Getters<Person>;
// 等同于
type LazyPerson = {
  getName: () => string;
  getAge: () => number;
  getLocation: () => string;
};
```

解释：

1.get：为键名添加的前缀。

2.`Capitalize<T>`：一个原生的工具泛型，用来将 T 的首字母变成大写。

3.`string & P`：一个交叉类型，其中的 P 是 keyof 运算符返回的键名联合类型`string|number|symbol`，但是 `Capitalize<T>`只能接受字符串作为类型参数，因此 string & P 只返回 P 的字符串属性名。

键名重映射过滤特定属性

```typescript
type User = {
  name: string;`
  age: number;
};

type Filter<T> = {
  [K in keyof T as T[K] extends string ? K : never]: string;
};

type FilteredUser = Filter<User>; // { name: string }
```

联合类型映射

```typescript
// 原始键名的映射是E in Events，这里的Events是两个对象组成的联合类型S|C。
// 所以，E是一个对象，然后再通过键名重映射，得到字符串键名E['kind']。
type S = {
  kind: 'square';
  x: number;
  y: number;
};

type C = {
  kind: 'circle';
  radius: number;
};

type MyEvents<Events extends { kind: string }> = {
  [E in Events as E['kind']]: (event: E) => void;
};

type Config = MyEvents<S | C>;
// 等同于
type Config = {
  square: (event: S) => void;
  circle: (event: C) => void;
};
```

### 类型运算符

- keyof
- in
- 方括号运算符
- extends...?
- infer
- is

#### keyof 运算符

JavaScript 对象的键名只有三种类型，所以对于任意对象的键名的联合类型就是 string|number|symbol（keyof 返回的类型）

```
// string | number | symbol
type KeyT = keyof any;
```

如果只需要其中一种类型，可采用交叉类型写法

`type Capital<T extends string> = Capitalize<T>;`

如果对象属性名采用索引形式，keyof 会返回属性名的索引类型

```typescript
// 示例一
interface T {
  [prop: number]: number;
}

// number
type KeyT = keyof T;

// 示例二
interface T {
  [prop: string]: number;
}

// string|number
type KeyT = keyof T;
```

如果 keyof 运算符用于数组或元组类型,keyof 会返回数组的所有键名，包括数字键名和继承的键名

```typescript
type Result = keyof ['a', 'b', 'c'];
// 返回 number | "0" | "1" | "2"
// | "length" | "pop" | "push" | ···
```

对于联合类型，keyof 返回成员共有的键名

```typescript
type A = { a: string; z: boolean };
type B = { b: string; z: boolean };

// 返回 'z'
type KeyT = keyof (A | B);
```

对于交叉类型，keyof 返回所有键名

```typescript
type A = { a: string; x: boolean };
type B = { b: string; y: number };

// 返回 'a' | 'x' | 'b' | 'y'
type KeyT = keyof (A & B);

// 相当于
keyof (A & B) ≡ keyof A | keyof B
```

取出键值组成的联合类型

```typescript
type MyObj = {
  foo: number;
  bar: string;
};

type Keys = keyof MyObj;

type Values = MyObj[Keys]; // number|string
```

keyof 可用于属性映射，即将一个类型的所有属性逐一映射成其他值

```typescript
type NewProps<Obj> = {
  [Prop in keyof Obj]: boolean;
};

// 用法
type MyObj = { foo: number };

// 等于 { foo: boolean; }
type NewObj = NewProps<MyObj>;
```

#### in 运算符

in 运算符用来确定对象是否包含某个属性名。in 运算符的左侧是一个字符串，表示属性名，右侧是一个对象，它的返回值是一个布尔值。

```typescript
type U = 'a' | 'b' | 'c';

type Foo = {
  [Prop in U]: number;
};
// 等同于
type Foo = {
  a: number;
  b: number;
  c: number;
};
```

#### 方括号运算符

用于取出对象的键值类型，比如 T[K]会返回对象 T 的属性 K 的类型

```typescript
type Person = {
  age: number;
  name: string;
  alive: boolean;
};

// Age 的类型是 number
type Age = Person['age'];

type Person = {
  age: number;
  name: string;
  alive: boolean;
};

// number|string
type T = Person['age' | 'name'];

// number|string|boolean
type A = Person[keyof Person];
```

#### extends...?

```typescript
interface Animal {
  live(): void;
}
interface Dog extends Animal {
  woof(): void;
}

// number
type T1 = Dog extends Animal ? number : string;

// string
type T2 = RegExp extends Animal ? number : string;

// 判断联合类型
(A|B) extends U ? X : Y
// 等同于
(A extends U ? X : Y) |
(B extends U ? X : Y)

// 联合类型不被条件运算符展开
// string[]|number[]
type T = ToArray<string|number>;

// 示例二
type ToArray<Type> =
  [Type] extends [any] ? Type[] : never;

// (string | number)[]
type T = ToArray<string|number>;
```

#### infer

```typescript
// infer Item表示Item参数是ts自己推断出来的
// Flatten<Type>则表示Type这个类型参数是外部传入的
// Type extends Array<infer Item>则表示，如果参数Type是一个数组，那么就将该数组的成员类型推断为Item，即Item是从Type推断出来的。

type Flatten<Type> = Type extends Array<infer Item> ? Item : Type;

// 示例
// string
type Str = Flatten<string[]>;

// number
type Num = Flatten<number>;

// 解释：
// 第一个例子Flatten<string[]>传入的类型参数是string[]，可以推断出Item的类型是string，所以返回的是string。
// 第二个例子Flatten<number>传入的类型参数是number，它不是数组，所以直接返回自身
```

#### is

```typescript
function isFish(pet: Fish | Bird): pet is Fish {
  return (pet as Fish).swim !== undefined;
}
```

is 运算符的特殊用法，就是用在类（class）的内部，描述类的方法的返回值

```typescript
// isStudent()方法的返回值类型，取决于该方法内部的this是否为Student对象。如果是的，就返回布尔值true，否则返回false。
class Teacher {
  isStudent(): this is Student {
    return false;
  }
}

class Student {
  isStudent(): this is Student {
    return true;
  }
}
```

### ts 模块化

ts 中主要使用的模块化方案是 es module

##### 非模块

![](/images/ts-img/非模块化.png)

### 内置类型导入

```typescript
// ts模块化.ts
export type IDType = number | string;

export interface IPerson {
  name: string;
  age: number;
}
```

```typescript
// index.ts

// 使用type前缀,表明被导入的是一个类型
// 此操作可以让非ts编辑器如babel\swc\esbuild知道什么样的导入可以被安全移除
// 写法一: import { type IDType, type IPerson } from './ts模块化';
// 写法二
import type { IDType, IPerson } from './ts模块化';

const id: IDType = 11;
```

### 命名空间

```typescript
// 命名空间.ts

export namespace price {
  export function format(price: number): string {
    return '$' + price;
  }
}

export namespace data {
  export function format(price: number): string {
    return '~' + price;
  }
}
```

```typescript
import { price } from './命名空间';

price.format(12);
```

### 类型查找

#### .d.ts 文件

.d.ts 文件，用来做类型申明，被称为类型申明/定义文件

#### ts 查找类型声明：

- 内置类型声明；（例如 vscode 内置、ts 内置）

内置类型声明是 ts 自带的，内置了 js 运行时的一些标准化 API 的声明文件

> 比如 Fuction、String、Math、Date 等内置类型
>
> 也包括运行环境中的 DOM API,比如 Window、Document 等

- 外部定义类型声明；（第三方库）

![](/images/ts-img/外部类型声明.png)

- 自定义类型声明

  > 情况一：我们使用的第三方库是一个纯的 js 库，没有对应的声明文件；比如 lodash
  >
  > 情况二：我们给自己代码中声明的类型，以便在其它地方使用

  ```typescript
  declare const projectName: string;

  declare function foo(params: string): string;

  declare class Person {
    name: string;
    age: number;
    constructor(name: string, age: number);
  }

  // 作为第三方库为其它开发者提供类型声明文件 axios.d.ts

  // 声明文件模块
  declare module '*.png';
  declare module '*.jpeg';
  // 在其它文件使用img资源
  // import logo from './src/imgs/logo.img';
  // const imgE1 = document.createElement('img');
  // imgE1.src = logo;
  // document.body.append(imgE1);

  declare namespace price {
    export function add(p: number): void;
  }
  ```

### declare

![](/images/ts-img/declare.png)
![](/images/ts-img/vue.png)

### tsconfig.json 文件

![](/images/ts-img/config.png)
![](/images/ts-img/config使用.png)

### 内置工具

参考[内置工具](https://wangdoc.com/typescript/utility#recordkeys-type)
