---
sidebar: auto
tags:
  - vue3
  - pinia
  - axios
---

## vue3 基础知识

## 理解 vue

vue 基于标准 HTML、CSS 和 JavaScript 构建，并提供了一套声明式的、组件化的编程模型，帮助开发者高效地开发用户界面。

### 核心功能

- 声明式渲染(Declarative Rendering)：Vue 基于标准 HTML 拓展了一套模板语法，使得我们可以声明式地描述最终输出的 HTML 和 JavaScript 状态之间的关系。

- 响应性(Reactivity)：Vue 会自动跟踪 JavaScript 状态并在其发生变化时响应式地更新 DOM。

### 声明式和命令式编程

![](/images/vue/声明式.png)

### MVVM 模型

![](/images/vue/mvvm.png)

vue 做了两件事：data bindings（绑定数据）和 dom listeners（监听事件）

## VNode(virtual node)

- 无论是组件还是元素，在 vue 上呈现出的都是一个个 vnode
- vnode 本质是一个 js 对象

### 虚拟 dom

template --> vnode --> 真实 dom

模板中的每一个元素先形成 vnode，所有的 vnode 会形成树结构的虚拟 dom。

虚拟 dom 有着广泛的用处：（方便项目跨平台）

- 可生成真实 dom，渲染在浏览器上
- 可解析转化成移动端的 button/view/image/ios UIButton/UIView/UIimageView 等--以移动原生控件方式在移动端显示出来
- 可渲染成桌面端部分控件
- 可渲染到 vr 设备上的控件

### diff 算法

vue 中对于列表更新的操作：

- 有 key，使用`patchKeyedChildren`方法

**过程：**

从头开始遍历、比较，a 和 b 一致，继续进行遍历；

c 和 f 因为 key 不一致，会 break 跳出循环；

从尾部开始遍历，比较；

如果旧节点遍历完毕，依然有新节点，那么就新增节点；

如果新节点遍历完毕，仍然有旧节点，那么就移除旧节点。

![](/images/vue/节点.png)

![](/images/vue/节点移动.png)

- 没有 key，使用`patchUnkeyedChildren`方法

![](/images/vue/没有key.png)

## 语法和指令

### mustache 语法

**用于文本插值**

mustache 语法：可使用三元运算符或函数

![](/images/vue/mustache.png)

### `v-once`

**用于一次性编译节点**

【性能优化】当数据发生变化时，元素/组件及其所有子项将被当作静态内容并跳过渲染

在 Vue 的编译过程中，当遇到 v-once 指令时，它会生成一个指令绑定函数，在这个函数中，会将节点的内容保存到变量中，并在之后的更新中直接使用这个变量的值，而不是重新执行表达式。

简化的实现示例：

```javascript
// 将绑定的表达式计算的初始值保存在onceValue数据属性中
function doOnce(value) {
  this.onceValue = value;
}

function bind() {
  this.onceValue = this.onceValue || this.value;
  this.textContent = this.onceValue;
}

Vue.directive('once', {
  // 在后续的DOM更新中，Vue会调用bind函数，它会检查onceValue是否已经被设置，如果设置了，则直接使用这个值，否则计算当前的表达式值并保存。
  bind,
  inserted: doOnce,
  update: doOnce
});
```

### `v-memo`【⭐️3.2+】

- 缓存一个模板的子树。在元素和组件上都可以使用。为了实现缓存，该指令需要传入一个固定长度的依赖值数组进行比较。如果数组里的每个值都与最后一次的渲染相同，那么整个子树的更新将被跳过(包括虚拟 DOM 的 vnode 创建)

- v-memo 传入空依赖数组 (`v-memo="[]"`) 将与 v-once 效果相同

```vue
<div v-memo="[valueA, valueB]">
  ...
</div>
```

#### 使用场景示例

与 `v-for` 一起使用

v-memo 仅用于性能至上场景中的微小优化，应该很少需要。最常见的情况可能是有助于渲染海量 v-for 列表 (长度超过 1000 的情况)：

```vue
<template>
  <div v-for="item in list" :key="item.id" v-memo="[item.id === selected]">
    <p>ID: {{ item.id }} - selected: {{ item.id === selected }}</p>
    <p>...more child nodes</p>
  </div>
</template>
```

当组件的 selected 状态改变，默认会重新创建大量的 vnode，尽管绝大部分都跟之前是一模一样的。v-memo 用在这里本质上是在说“只有当该项的被选中状态改变时才需要更新”。这使得每个选中状态没有变的项能完全重用之前的 vnode 并跳过差异比较。注意这里 memo 依赖数组中并不需要包含 item.id，因为 Vue 也会根据 item 的 :key 进行判断。

### `v-text` 和 `v-html`

- `v-text` 通过设置元素的 `textContent` 属性来实现

- 在网站上动态渲染任意 HTML 是非常危险的，因为这非常容易造成 XSS 漏洞。请仅在内容安全可信时再使用 `v-html`，并且永远不要使用用户提供的 HTML 内容

#### 简化版实现`v-text`

```javascript
// 创建一个简单的 v-text 指令的函数
function vText(el, binding) {
  el.textContent = binding.value;
}

// 假设 Vue 实例的代码如下
new Vue({
  el: '#app',
  data: {
    message: 'Hello Vue!'
  },
  // 在组件的 directives 选项中注册 v-text 指令
  directives: {
    text: {
      bind(el, binding) {
        vText(el, binding);
      },
      update(el, binding) {
        if (binding.oldValue !== binding.value) {
          vText(el, binding);
        }
      }
    }
  }
});
```

#### 简化版实现`v-html`

```javascript
// 注册一个自定义指令 `v-html`
Vue.directive('html', {
  // 当绑定元素插入到DOM中
  inserted: function (el, binding) {
    // 设置元素的innerHTML为绑定的值
    el.innerHTML = binding.value;
  },
  // 当绑定的数据更新时
  update: function (el, binding) {
    // 更新元素的innerHTML
    el.innerHTML = binding.value;
  }
});
```

### v-pre

跳过该元素及其所有子元素的编译，输出原始文本(展示原始的 Mustache 标签)，加快编译速度

简化版实现`v-pre`

```javascript
// 假设的Vue编译器核心函数
function compile(el) {
  const children = el.childNodes;
  for (let i = 0; i < children.length; i++) {
    const child = children[i];
    if (child.nodeType === 1 && child.hasAttribute('v-pre')) {
      // 如果是元素节点且含有v-pre指令，则跳过该元素的编译
      continue;
    }
    // 对子元素进行递归编译
    compile(child);
  }
}
```

### v-cloak

#### 使用方法

和 css 规则一起使用时，这个指令可以隐藏未编译的 mustache 标签直到组件实例准备完毕；

如下例中的 h1 标签不会显示，直到编译结束

```vue
<template>
  <div>
    <h1 v-cloak>{{ message }}</h1>
  </div>
</template>
```

```css
<style>
  [v-cloak] {
    dispaly: none;
  }
</style>
```

在 Vue 实例准备好并替换掉 message 之前，`<h1>`元素上会有 v-cloak 属性。

当 Vue 实例完成初始渲染后，v-cloak 属性会被自动移除，v-cloak 对应的 CSS 规则会失效，`<h1>` 元素随即会显示出来。这样就避免了用户看到未经 Vue 处理的 message 文本。

### v-on

```html
<button @click="doThis"></button>
<!-- 动态事件 -->
<button @[event]="doThis"></button>
<!-- 阻止冒泡 -->
<button @click.stop="doThis"></button>
<!-- 阻止默认事件 -->
<button @click.prevent="doThis"></button>
<!-- 不带表达式地阻止默认事件 -->
<form @submit.prevent></form>
<!-- 链式调用 -->
<button @click.stop.prevent="doThis"></button>
<!-- 按键用于 keyAlias 修饰符-->
<input @keyup.enter="onEnter" />
<!-- 点击事件将最多触发一次 -->
<button v-on:click.once="doThis"></button>
<!-- 对象语法 -->
<button v-on="{ mousedown: doThis, mouseup: doThat }"></button>
```

### v-bind

#### 修饰符

- `.camel` - 将短横线命名的 `attribute` 转变为驼峰式命名。
- `.prop` - 强制绑定为 `DOM property`。【⭐️3.2+】
- `.attr` - 强制绑定为 `DOM attribute`。【⭐️3.2+】

在处理绑定时，Vue 默认会利用 in 操作符来检查该元素上是否定义了和绑定的 key 同名的 `DOM property`。如果存在同名的 property，则 Vue 会将它作为 DOM property 赋值，而不是作为 attribute 设置。这个行为在大多数情况都符合期望的绑定值类型，但是你也可以显式用 .prop 和 .attr 修饰符来强制绑定方式。

由于 DOM attribute 的值只能为**字符串**，使用 `setAttribute` 和 `getAttribute` 来设置和获取属性。

对属性 Property 可以赋任何类型的值,因此我们只能使用 DOM 对象的属性（property）来传递复杂数据。

```html
<my-element :user.prop="{ name: 'jack' }"></my-element>
<!-- 等价缩写 -->
<my-element .user="{ name: 'jack' }"></my-element>
```

#### 计算属性绑定

```html
<!-- 计算属性 绑定 -->
<div :class="classObject"></div>
```

```javascript
const classObject = computed(() => ({
  active: isActive.value && !error.value,
  'text-danger': error.value && error.value.type === 'fatal'
}));
```

```html
<img :src="imageSrc" />
<!--【⭐️3.4+】 缩写形式的动态 attribute 名，扩展为 :src="src" -->
<img :src />
<!-- 动态 attribute 名的缩写 -->
<button :[key]="value"></button>

<!-- 动态class -->
<div :class="{ red: isRed }"></div>
<div :class="[classA, classB]"></div>
<div :class="[classA, { classB: isB, classC: isC }]"></div>

<!-- 动态style -->
<div :style="{ fontSize: size + 'px' }"></div>
<div :style="[styleObjectA, styleObjectB]"></div>

<!-- 绑定对象形式的 attribute -->
<div v-bind="{ id: someProp, 'other-attr': otherProp }"></div>

<!-- prop 绑定。“prop” 必须在子组件中已声明。 -->
<MyComponent :prop="someThing" />

<!-- 【💡组件传值】传递子父组件共有的 prop -->
<MyComponent v-bind="props" />

<!-- XLink -->
<svg><a :xlink:special="foo"></a></svg>
```

### v-if & v-else & v-else-if & v-show

- v-if 是惰性的，条件为 true 时才渲染条件块中内容，条件为 false 时判断的内容完全不会被渲染到 dom 中或被销毁掉
- template 渲染为不可见的元素
- v-show**不支持**template、不可以和 v-else、v-else-if 使用，原理是通过 css 样式：`display:none`来控制元素展示或隐藏
- 如果原生需要在显示和隐藏之间频繁切换使用 v-show，不会频繁切换使用 v-if

### v-for

#### 基础用法

in 和 of 的操作相同，所以也可以写 of

- 可用于遍历对象

```html
<p v-for="(value, key, index) in info">{{value}}-{{key}}-{{index}}</p>
```

- 可遍历字符串

```html
<p v-for="item in 'test'">{{index}}</p>
```

- 可遍历数字

```html
<p v-for="(num, index) in 10">{{num}}-{{index}}</p>
```

#### 数组更新检测

不修改原数组的方法不会被检测到，以下数组方法更新数据可以被检测：

`splice`、`pop`、`push`、`shift`、`unshift`、`reverse`、`reverse`

#### v-for 中的`key`属性

- 在使用 v-for 进行列表渲染时，需要给元素或组件绑定 key 属性
- key 属性主要用于 vue 的虚拟 dom 算法，在新旧 nodes 对比时辨识 vnodes；
- 如果不使用 key，vue 会使用一种最大限度减少动态元素并且尽可能的尝试就地修改/复用相同类型元素的算法；而使用 key 时，它会基于 key 的变化重新排列元素顺序，并且会移除/销毁 key 不存在的元素

### template

`template`元素可以当作不可见的包裹元素，并在`v-if`上使用，但最终`template`不会被渲染出来；类似于小程序中的`block`。

#### template 编译

template 模板中的元素会经历：--> `createVNode()` -->`VNode`-->`虚拟dom`-->`真实dom`

**默认 vue 版本**：webpack 加载 vue 文件时使用的是`vue-loader`,runtime、`vue-loader`会帮助文件完成上述的转换过程

**不是 vue 文件的 template 编译**：rutime、compile 对 template 进行编译

`vue.esm-bundler.js`包含运行时编译器，如果想要运行时的模板编译，需要配置构建工具：将 vue 设置为这个文件

![](/images/vue/bundler.png)

### `computed`

计算属性将被混入到组件实例中

- 所有的`getter`和`setter`中的`this`绑定的是当前所在的组件实例

- 计算属性会基于响应式数据的依赖关系进行缓存，数据不发生变化时，计算属性不需要重新计算；依赖的数据发生变化时，计算属性会重新进行计算。

- **原理**-- 对`computed`对象进行遍历，判断 key 对应的值是对象还是函数。如果是函数，返回该函数；如果是对象，取对象中的`get`和`set`函数。

  ```js
  // options api
  computed: {
     fullName() {
      return `${name}111`
     }
  }
  ```

  计算属性完整写法：

  ```js
  computed: {
     fullName: {
       get:function() {
            return `${name}111`
       },
       set:function(value) {
           const names = value.split(' ')
           this.firstName = names[0]
           this.lastName = names[2]
       }
     }
  }
  methods: {
      setFullName() {
          this.fullName = '111 222 333'
      }
  }
  ```

### `watch`

如果侦听对象类型，拿到的 oldValue 和 newValue 是被 proxy 包裹后的代理对象，

如果想要拿到原始对象有两种方法：①`{...oldValue}` ②`toRaw(newValue)`

侦听器配置选项：

深度监听：`deep:true` (watch 的默认监听不是深度监听)

立即监听：`immediate:true`

```js
// options api
 watch: {
   info: {
       handler(newValue,oldValue) {
        console.log(newValue,oldValue)
        },
       deep:true
     }
  }

// 也可以在created的生命周期中用this.$watch来侦听
created() {
    this.$watch("info",(newValue,oldValue)=>{
    },{deep:true})
}
```

### v-model

#### 原理

> 两个操作：
>
> ①v-bind 绑定 value 属性的值；
>
> ②v-on 绑定 input 事件监听到函数中，函数会获取最新的值赋值到绑定的属性中

```vue
<input type="text" v-model="message" />
<!-- 手动实现 -->
<input type="text" :value="message" @input="inputChange" />
```

#### 修饰符

`lazy`

默认情况下，v-model 在进行双向绑定时，绑定为 input 事件，那么会在每次内容输入后就将最新值和绑定的属性进行同步

添加`lazy`修饰符后，input 事件会切换为 change 事件，只有在提交时才会触发

`number`

值从 string 类型转为 number 类型

`trim`

去掉值前后的空格

多个修饰符同时使用时**链式调用**

### 组件的 v-model

#### 组件上使用 v-model 实质

![](/images/vue/model组件.png)

#### 组件 v-model 的实现

![](/images/vue/model实现.png)

组件可以绑定多个 v-model

`  <SonPage v-model:name="sonComponent" v-model:age="ageProps"></SonPage>`

![](/images/vue/多个model.png)

## 组件

![](/images/vue/组件化.png)

#### 组件名称

![](/images/vue/组件名称.png)

#### 全局组件注册

![](/images/vue/全局组件.png)

#### 局部组件注册

![](/images/vue/局部组件.png)

## 配置路径别名(vue.config.js)

```javascript
const { defineConfig } = require('@vue/cli-service');

module.exports = defineConfig({
  transpileDependencies: true,
  configureWebpack: {
    // 配置路径别名
    // @是已经配置好的路径别名：对应的是src路径
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src'),
        utils: '@/utils'
      }
    }
  }
});
```

## 配置路径(js.config.json )

```javascript
{
  "compilerOptions": {
    "target": "esnext",
    "module": "esnext", // 在代码中采用最新版本的模块化
    "moduleResolution": "node", // 按node规则查找规则查找文件
    "baseUrl": ".", // 指定base_url
    "lib": ["dom", "esnext"],// 项目开发中可能用到的库，vscode提示更友好
    "removeComments": true,
    "paths": {
       // 配置路径
      "/@/*": ["src/*"],
      "/#/*": ["types/*"]
    }
  },
}
```

## scoped 原理

单文件 vue style 有自己的作用域：添加 scoped 后，会给每个元素添加属性，该文件内的样式时会被加上属性选择器，来限定样式的作用范围。

## 组件通信

### `props`

数组语法：

`props:['name','age','title']`

对象语法：

```javascript
props:{
  name:{
   type:String,
   default:'默认name',
   required:true
 },
  friend:{
    type:Object,
    // 对象或数组默认值必须从一个工厂函数获取
    default:()=>({name:'jame'})
   },
  friendArr:{
    type:Array,
    default:()=>['篮球','rap','唱跳']
   },
   // 自定义验证
   propF:{
     validator(value) {
        // 值必须匹配下列字符串中的一个
        return ['success','warning','danger'].includes(value)
        }
    }
    friendFn:{
      type:Function,
      // 对象或数组默认值必须从一个工厂函数获取
      default() {
    // 与对象或数组默认值不同，这不是一个工厂函数（是一个用作默认值的函数）
        return 'Default Func'
    }
   },
}
```

**非 prop 的 attribute**

![](/images/vue/attr.png)

**禁用 Attribute 继承和多根节点:`inheritAttrs:false`**

![](/images/vue/禁用attr.png)

**手动指定：**

```vue
<template>
  <div class="info"></div>
  <div class="others" v-bind="$attrs"></div>
</template>
```

### `emits`

emits 数组写法：`emits:['numChange']`

emit 对象写法：对参数进行验证

```js
emits:{
 addOne:null,
 addTen:(payload)=>{
   if(payload===10) return true
   return false // 验证返回为false会报警告
  }
}
```

## 插槽 slot

![](/images/vue/插槽.png)
![](/images/vue/插槽2.png)

### 基本使用 & 插槽默认内容

#### 插槽默认内容

```vue
<template>
  <div class="menu">
    <h1>{{ isUpdate }}</h1>
    <div class="content">
      <slot>
        <!-- 插槽的默认内容 -->
        <div>没有传入slot时显示</div>
      </slot>
    </div>
  </div>
</template>
```

使用组件

```vue
<template>
  <MenuDrawer>
    <button>插槽的按钮元素</button>
  </MenuDrawer>
</template>
```

### 具名插槽

`<slot>`元素有一个特殊的 `attribute:name`；

一个不带 name 的 slot，会带有隐含的名字：default

组件

```vue
<template>
  <div class="menu">
    <div class="nav">
      <div class="left">
        <slot name="left"></slot>
      </div>
      <div class="center">
        <slot name="center"></slot>
      </div>
      <div class="right">
        <slot name="right"></slot>
      </div>
    </div>
  </div>
</template>
```

使用具名插槽

```vue
<template>
  <MenuDrawer>
    <template #left>
      <h4>左边插槽</h4>
    </template>
    <template #center>
      <button>中间插槽</button>
    </template>
    <template v-slot:right>
      <h4>右边插槽</h4>
    </template>
  </MenuDrawer>
</template>
```

### 动态插槽名

![](/images/vue/动态插槽.png)

### 渲染作用域

![](/images/vue/渲染作用域.png)

### 作用域插槽：子组件将值传递给父组件

父组件使用作用域插槽：

![](/images/vue/作用域插槽.png)

子组件插槽：

![](/images/vue/作用域插槽2.png)

![](/images/vue/作用域插槽3.png)

#### 独占默认插槽缩写

```vue
<template>
  <MenuDrawer>
    <!-- 独占默认插槽简写（v-slot:default='props'） -->
    <template v-slot="props">
      <h4>{{ props.isUpdate }}</h4>
    </template>
  </MenuDrawer>
</template>
```

如果只有一个插槽，可以不用写`template`，直接写在`<MenuDrawer v-slot="props"></MenuDrawer>`

如果有多个插槽，不能使用该写法。

## 非父子组件通信

### provide 和 inject

![](/images/vue/provide.png)

App.vue

```vue
<template>
  <header>
    <div class="wrapper">
      <AboutView></AboutView>
    </div>
  </header>
</template>

<script setup lang="ts">
import { provide } from 'vue';
import AboutView from './views/AboutView.vue';
provide('name', '依赖注入');
</script>
```

SonPage.vue

```vue
<template>
  <div class="about">
    <h1>This is an son page:{{ name }}</h1>
  </div>
</template>

<script setup lang="ts">
import { inject } from 'vue';
// 可以设置默认值
const name = inject('name', 'defaultName');
</script>
```

### options api 中 inject 使用变量写法

inject 注入的值，用到 computed 返回的是 ref 对象，在 template 中使用不会自动解包，需要加上.value。

![](/images/vue/inject.png)

### 事件总线

![](/images/vue/事件总线.png)

### ref

#### 获取组件实例的根元素/获取组件实例的其他根元素（多个根元素情况）

![](/images/vue/ref.png)

![](/images/vue/ref2.png)

### $parent和$root

![](/images/vue/parent.png)

## 动态组件

引入组件

template 中使用：`<component name="nameProps" :is="currentTab[index]"></component>`

![](/images/vue/动态组件.png)

## keep-alive

### 属性使用

使用 include 属性时，**组件必须要定义 name 选项**：

![](/images/vue/include.png)

![](/images/vue/其它属性.png)

### keep-alive 生命周期

`activated`和`deactivated`

## webpack 代码分包/异步组件

import 函数可以让 webpack 打包文件时进行分包处理

```js
// 示例
import('./utils/math').then((res) => res.sum(20, 30));
```

```js
// 异步组件--在打包时会进行分包处理
import { defineAsyncComponent } from 'vue';
const AsyncCategory = defineAsyncComponent(() =>
  import('./views/category.vue')
);
```

![](/images/vue/默认打包.png)

![](/images/vue/工厂函数.png)

![](/images/vue/工厂函数2.png)

## mixin

### 基础使用

![](/images/vue/mixin.png)

##### 合并规则

![](/images/vue/合并规则.png)

##### 全局混入

main.js 文件

![](/images/vue/全局混入.png)

## 从 options api 到 composition api

### options api 弊端

![](/images/vue/options.png)

##### setup 函数

![](/images/vue/setup.png)

composition api 使用 hook 优势示例：可复用性高，代码更为灵活

hook/useCounter.js

![](/images/vue/counter.png)

![](/images/vue/counter2.png)

template 中的 ref 对象会被自动解包

### composition api

#### reactive

用于定义对象或数组类型

应用场景：常应用于本地数据 /多个数据之前存在关联（聚合的数据），组织在一起有特定作用

![](/images/vue/reactive.png)

#### ref

![](/images/vue/ref理解.png)

模板中的解包是浅层解包（存在矛盾:使用时不需要写`.value`，函数修改时需要写`.value`）

![](/images/vue/ref理解2.png)

### 其它函数补充

#### 注意：

子组件拿到父组件传递的数据后只能使用，不能修改，如果确实需要修改数据，应该将事件传递出去，由父组件修改数据（**单向数据流规范**）

在 react 中，任何一个组件都应该像纯函数一样，不能修改传入的 props

#### readonly

![](/images/vue/readonly.png)

![](/images/vue/readonly2.png)

```vue
<template>
  <header>
    <div class="wrapper">
      <HomeView :homeProps="readAccount"></HomeView>
    </div>
  </header>
</template>

<script setup lang="ts">
import { reactive, readonly } from 'vue';
import HomeView from './views/HomeView.vue';
const account = reactive({
  name: 'loginName',
  password: '123456'
});
// 只读 子组件接收props时，是readonly；如果需要修改数据，则由父组件修改变量account
const readAccount = readonly(account);
</script>
```

### isProxy、isReactive、isReadonly、toRaw、shallowReactive、shallowReadonly

![](/images/vue/proxy.png)

### toRefs

![](/images/vue/torefs.png)

### toRef

只解构一个值使用 toRef

![](/images/vue/toref.png)

### unRef、isRef、shallowRef、triggerRef

![](/images/vue/unref.png)

### 在 setup 函数中不能使用 this

![](/images/vue/this.png)

![](/images/vue/this2.png)

### computed

computed 返回的是 computedRef 对象

![](/images/vue/computedref.png)

### ref 获取元素或组件

```vue
<template>
  <header>
    <div class="wrapper">
      <div ref="nameRef"></div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import HomeView from './views/HomeView.vue';
const nameRef = ref(null);
//  获取实例
console.log(`output->nameRef.value`, nameRef.value);
</script>
```

### 生命周期

![](/images/vue/生命周期.png)

### watch

返回值从 proxy 对象变为普通对象的写法：

![](/images/vue/watch.png)

侦听多个数据源

![](/images/vue/watch2.png)

watch 选项

![](/images/vue/watch3.png)

### watchEffect

在执行过程中，会自动收集函数中的所有依赖

![](/images/vue/依赖.png)

停止侦听

![](/images/vue/停止.png)

hook/useTitle.js

![](/images/vue/usetitle.png)

index.vue 使用 useTitle

![](/images/vue/使用usetitle.png)

### definProps 和 defineEmits

![](/images/vue/definprops.png)

### defineExpose

![](/images/vue/defineexpose.png)

#### 25.vue-router

##### 路由发展

① 后端路由阶段：将 url 传递给服务器，服务器根据地址将完整网页 html 渲染出来，再返回给浏览器进行展示。url 和网页形成了对应关系。

![image-20230524114835539](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230524114835539.png)

② 前后端分离阶段：将 url 传递给服务器，服务器根据地址将仅返回页面的基本结构，页面数据由前端发送 ajax 请求来获取数据并渲染到页面上。

![image-20230524114922585](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230524114922585.png)

③ 前端路由（SPA：single page application）阶段：路由与页面映射关系由前端来维护，不同路由显示不同页面。

![image-20230524114952897](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230524114952897.png)

url 的 hash

![image-20230524115243996](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230524115243996.png)

url 的 history

![image-20230524115316447](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230524115316447.png)

##### vue-router 简介

![image-20230524140446498](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230524140446498.png)

##### router 使用步骤

![image-20230524142042127](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230524142042127.png)

```js
import { createRouter, createWebHistory } from 'vue-router';
import HomeView from '../views/HomeView.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  // history模式：createWebHistory()
  // hash模式：createWebHashHistory()
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('../views/AboutView.vue') // 使用import函数可以分包
    }
  ]
});

export default router;
```

**路由懒加载**：使用魔法注释，可以支持对分包进行命名

![image-20230524145545362](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230524145545362.png)

##### router-link

replace 属性设置后不会记录历史路径；

active-class 可设置选中的 class 类名

![image-20230524144654738](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230524144654738.png)

##### 动态路由

![image-20230524150343480](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230524150343480.png)

在模板中获取 id

`{{$route.params.id}}`

在 setup 中获取路由参数

```vue
<script setup lang="ts">
import { useRoute } from 'vue-router';
import { onMounted } from 'vue';

onMounted(() => {
  const route = useRoute();
  console.log(`output->route.params.id`, route.params.id);
});
</script>
```

配置 404 页面-匹配规则加\*

```js
    {
       // 加了*号，会将路径解析成数组
      path: '/:pathMatch(.*)*',
      component: () => import('../views/NotFound.vue')
    }
```

![image-20230524160729527](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230524160729527.png)

##### 路由跳转

```vue
<script setup lang="ts">
import {  useRouter } from 'vue-router';
import { onMounted } from 'vue';

onMounted(() => {
  const router = useRouter();
  router.push('/home');
  router.push({
    path: '/home',
    query: {
      name: '111',
      age: 12
    }
  }); // 通过$route.query获取参数
  router.back() // 返回
  router.forward() // 向前路径
  router.go(-1)
</script>
```

##### 动态添加路由

![image-20230525142951424](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230525142951424.png)

##### 删除路由

![image-20230525143200746](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230525143200746.png)

##### 路由守卫

![image-20230525144718281](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230525144718281.png)

守卫示例：

```js
router.beforeEach((to, from) => {
  const token = localStorage.getItem('token');
  if (!token && to.path === '/order') {
    return '/login';
  }
});
```

导航解析流程：![image-20230525151558480](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230525151558480.png)

#### 26.状态管理（vuex）

![image-20230525152912353](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230525152912353.png)

##### 单一状态树

![image-20230525155401946](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230525155401946.png)

##### state

###### mapState 映射

![image-20230525155941468](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230525155941468.png)

###### 在 setup 使用 mapState 映射函数

方式一：

![image-20230525160343700](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230525160343700.png)

此处的 name 和 leve 解构出来的都是函数，相当于：

```js
name() {
  return this.$store.state.name
}
```

方式二：封装 useState 来解决这个问题

![image-20230525162310793](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230525162310793.png)

方式三：对 store.state 解构

```js
const store = useStore();
const { name, level } = toRefs(store.state);
```

##### getters

###### getters 返回函数

![image-20230525163833978](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230525163833978.png)

###### getters 参数

```js
getters:{
 message(state,getters,rootState) {
  console.log(rootState) // 根元素
  return `name:${state.name} level:@{getters.level}`
  }
}
```

###### mapGetters 映射

![image-20230525164557914](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230525164557914.png)

#### mutation

![image-20230525165843231](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230525165843231.png)

普通提交方式：

```js
methods: {
 changeName() {
   store.commit("changeName",{newName:'111'})
 }
}
```

###### mutation 常量类型（设计规范-vue 官方推荐）

![image-20230525170817267](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230525170817267.png)

###### mapMutations 映射

![image-20230525171147526](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230525171147526.png)

###### setup 使用 mapState 映射函数

![image-20230525171445008](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230525171445008.png)

###### mutation 原则

![image-20230525172017694](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230525172017694.png)

##### actions

![image-20230529144821191](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230529144821191.png)

派发 action：`store.dispatch("incrementAction","参数")`

```js
actions: {
  changeNameAction(context,payload) {
    console.log(payload) // 传参
    context.commit("changeName","mutations参数") // 调用mutations方法修改数据
  }
}
```

###### 使用 mapActions 辅助函数

![image-20230529145815595](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230529145815595.png)

###### 在 setup 中使用 actions

![image-20230529150158376](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230529150158376.png)

###### actions 使用的默认做法:

```js
// 自己定义函数手动调用actions的方法
function incrementAction() {
  store.dispatch('incrementAction');
}
```

###### 手动 new Promise 处理操作

![image-20230529152421829](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230529152421829.png)

##### modules 的使用

![image-20230529153037376](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230529153037376.png)

在 template 中使用模块中的数据需要采用`state.moduleA.name`的方式，但调用 mutation 和 actions 的方法时不需要根模块

![image-20230529154311285](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230529154311285.png)

![image-20230529154646313](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230529154646313.png)

命名空间：`namespaced:true`

修改根模块的 state

![image-20230529155458664](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230529155458664.png)

#### 27.pinia

##### pinia 和 vuex 的对比

pinia 兼容 options api

![image-20230529160150405](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230529160150405.png)

##### pinia 基础使用

main.ts

```typescript
import { createApp } from 'vue';
import { createPinia } from 'pinia';

import App from './App.vue';
import router from './router';

const app = createApp(App);

app.use(createPinia());
app.use(router);

app.mount('#app');
```

store/index.js

```js
import { createPinia } from 'pinia';

const pinia = createPinia();

export default pinia;
```

store/counter.js

**store 是使用`defineStore()`定义的，需要一个唯一名称（name），作为第一个参数传递。这个 name 也称为 id，是必要的，pinia 使用 name 来连接 devtools**

**返回的函数统一用 useX 命名**

```js
import { defineStore } from 'pinia';

const useCounter = defineStore('counter', {
  state: () => ({
    count: 11
  })
});

export default useCounter;
```

在页面文件中使用 pinia ，**调用 use 函数来使用**

**store 中的属性被解构后会失去响应式，需要使用`storeToRefs()`来保持响应式**

```js
import { storeToRefs } from 'pinia';
const counterStore = useCounter();
const { count } = storeToRefs(counterStore);
```

home.vue

```vue
<template>
  <div>
    <div>home-count:{{ counterStore.count }}</div>
    <div>home-title:{{ counterStore.title }}</div>
    <div>home-doubleCount:{{ counterStore.doubleCount }}</div>
    <div>home-doubleCountAddOne:{{ counterStore.doubleCountAddOne }}</div>
    <div>home-getNumByCount:{{ counterStore.getNumByCount(1) }}</div>
    <button @click="changeCount">修改state</button>
    <button @click="resetCount">重置state</button>
    <button @click="changeCountStore">一次性修改多个值</button>
    <button @click="setNewState">替换state</button>
  </div>
</template>

<script setup lang="ts">
import useCounter from '@/stores/counter.js';

const counterStore = useCounter();

const changeCount = () => {
  // 直接修改值
  counterStore.count = 1000;
};

const resetCount = () => {
  // 调用内部属性需要加上$
  counterStore.$reset();
};

// 一次性修改多个值
const changeCountStore = () => {
  counterStore.$patch({
    title: '再次修改',
    count: 0
  });
};

const setNewState = () => {
  counterStore.$state = {
    title: '1'
  };
};
</script>
```

##### store

![image-20230529162841395](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230529162841395.png)

##### state

![image-20230529164306953](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230529164306953.png)

![image-20230529164621858](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230529164621858.png)

订阅（subscribe）

订阅状态会被绑定到组件上，组件被卸载时，订阅会被自动移除，如果添加`detached:true`则订阅不会被自动移除

`counterStore.$subscribe(callback,{detached:true})`

##### getters

counter.js

```js
import { defineStore } from 'pinia';

const useCounter = defineStore('counter', {
  state: () => ({
    count: 11,
    title: '修改一次',
    AllCounts: [1, 23, 43, 54, 65, 765]
  }),
  getters: {
    //   基本使用
    doubleCount(state) {
      return state.count * 2;
    },

    // 获取getters中的值可以用this.
    doubleCountAddOne() {
      return this.doubleCount + 100;
    },

    // 传入参数(返回函数)
    getNumByCount(state) {
      return function (id) {
        if (state.AllCounts.find((v) => v === id)) {
          return 'Find';
        } else return '404';
      };
    },

    // 如果getters用到了别的store中的数据
    showMesage(state) {
      const useUser = useUser();
      return `${useUser.name}-${state.num}`;
    }
  }
});

export default useCounter;
```

##### actions

异步操作

![image-20230529170803976](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230529170803976.png)

同样可以通过 new Promise 获取 actions 何时结束（同 vuex）

![image-20230529170913197](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230529170913197.png)

##### 28.axios

##### axios 请求方式

![image-20230529171753136](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230529171753136.png)

发送 request 请求 ![image-20230529172118494](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230529172118494.png)

发送 get 请求

![image-20230529173029662](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230529173029662.png)

发送 post 请求

![image-20230529173147883](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230529173147883.png)

axios.all(本质就是 promise.all)

![image-20230529174312281](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230529174312281.png)

##### 常见配置项

![image-20230529173422233](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230529173422233.png)

##### 对 axios 实例进行公共配置：

```js
axios.defaults.baseUrl = BaseUrl;
axios.defaults.timeout = 1000;
```

##### axios 创建实例

![image-20230529174810527](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230529174810527.png)

##### 请求和响应拦截器

![image-20230529174858820](C:\Users\tayceyun\AppData\Roaming\Typora\typora-user-images\image-20230529174858820.png)

在请求成功拦截时开启 loading/header/认证登录/对参数进行转化，在响应成功拦截中关闭 loading/对返回值进行统一处理。

##### 基础封装 axios

```js
import axios from 'axios';
class axiosRequest {
  constructor(baseUrl, timeout = 1000) {
    this.instance = axios.create({
      baseUrl,
      timeout
    });
  }

  request(config) {
    return new Promise((resolve, reject) => {
      this.instance
        .request(config)
        .then((res) => {
          resolve(res.data);
        })
        .catch((err) => {
          reject(err);
        });
    });
  }
  get(config) {
    return this.request({ ...config, method: 'get' });
  }
  post(config) {
    return this.request({ ...config, method: 'post' });
  }
}

export default new axiosRequest();
```

project 细节整理
