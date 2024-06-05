## 前置知识

### 1.monorepo

#### 了解 monorepo

当下前端组件库 / 工具库的最佳实践方案基本都是 pnpm + monorepo 的开发模式，如 Vue、React、Vite、Element UI、Varlet UI、Vant UI 等。

Monorepo（单仓多模块） 是一种项目开发与管理的策略模式，它代表"单一代码仓库"（Monolithic Repository）。在 Monorepo 模式中，**所有相关的项目和组件都被存储在一个统一的代码仓库中**，而不是分散在多个独立的代码仓库中，这些项目之间还可能会有依赖关系。

在 Monorepo 中，每个子模块仍然是独立的，有独立的版本，可以独立发包，不受其他模块的限制。最重要的是 Monorepo 的 build、test 都是增量的，只有发生更改的子模块会进行构建和测试，而不需要重新构建和测试整个代码库。这可以大大加快持续集成（CI）的速度，提高开发效率。

#### Monorepo 的优缺点

【优点】

1. 代码复用
2. 模块独立管理
3. 分工明确，业务场景独立
4. 代码耦合度降低
5. 管理所有项目的版本控制更加容易和一致，降低了不同项目之间的版本冲突
6. 可以统一项目的构建和部署流程，降低了配置和维护多个项目所需的工作量

【缺点】

1. 权限管理问题：项目粒度的权限管理较为困难，团队成员可以访问到与自己无关的代码，容易产生非 owner 管理者的改动风险。使用 Monorepo 也就意味着接受了使用团队间的代码共享，如果对代码隔离有强要求，Monorepo 的方案可能就不合适了。
2. Monorepo 可能随着时间推移变得庞大和复杂，导致构建时间增长和管理困难，git clone、pull 的成本增加

#### 包管理工具

npm、yarn、pnpm 等是用来管理项目依赖、发布包、安装依赖的工具，它们都提供了对工作区（workspace）的支持，允许在单个代码库中管理多个项目或包。

这些包管理工具与 monorepo 的关系在于它们可以为 monorepo **提供依赖安装与依赖管理的支持**，借助自身对 workspace 的支持，允许在 monorepo 中的不同子项目之间**共享依赖项**，并提供一种管理这些共享依赖项的方式，这可以简化依赖项管理和构建过程，并提高开发效率。

##### Workspace 工作区

包管理工具通过 workspace 功能来支持 Monorepo 模式。Workspace 是指在一个代码库中管理多个相关项目或模块的能力。

❓ 包管理工具如何实现 workspace 的支持

1️⃣ 代码结构组织：在 Monorepo 中，不同的项目或模块通常位于同一个代码库的不同目录中。包管理工具通过识别并管理这些目录结构，可以将它们作为独立的项目或模块进行操作。

2️⃣ 共享依赖：Monorepo 中的不同项目或模块可以共享相同的依赖项。包管理工具可以通过在根目录中维护一个共享的依赖项列表，以确保这些依赖项在所有项目或模块中都可用。

3️⃣ 交叉引用：在 Monorepo 中，不同项目或模块之间可能存在相互引用的情况。包管理工具需要处理这些交叉引用，以确保正确解析和构建项目之间的依赖关系。

4️⃣ 版本管理：Monorepo 中的不同项目或模块可能具有不同的版本。包管理工具需要能够管理和跟踪这些版本，并确保正确地安装和使用适当的版本。

5️⃣ 构建和测试：包管理工具需要支持在 Monorepo 中进行增量构建和测试。这意味着只有发生更改的项目或模块会重新构建和测试，而不需要重新构建和测试整个代码库。

#### ❓ 为什么 pnpm+Monorepo 是目前的最佳实践

首先来看看 npm 与 yarn 存在的问题：

- 不同项目中重复的包会被重复下载，对磁盘空间的利用率不足

- 扁平化依赖存在依赖非法访问的问题：项目代码在某些情况下可以在代码中使用没有被定义在 package.json 中的包，这种情况就是我们常说的幽灵依赖（安装的包可能依赖了一些包,而依赖的这些包又会依赖其它包...npm 与 yarn 是把这些包扁平放入 node_modules 下,这也就导致 node_modules 里出现了这么多包）。
  - 幽灵依赖会带来哪些问题？
    - 假设安装一个依赖包 A1,而 A1 依赖 B1,如果项目时需要用到 B1,B1 在没有安装的情况被直接使用。如果依赖包 A1 升级为 A2,而 A2 需要依赖升级版的 B2 或者不再需要依赖 B1,这时候启动项目问题就出现了,代码可能就出 B1 版本不兼容或者 B1 依赖丢失问题!

❓pnpm 是如何解决上述问题的

**pnpm 使用硬连接的方式节约磁盘空间利用率、采用虚拟存储目录+软连接解决幽灵依赖**

硬连接：电脑文件系统中的多个文件平等的共享同一个文件存储单元，如果存在改动，那么多个文件会更新改动。

软链接（符号连接）： 包含一条以绝对路径或相对路径的形式指向其他文件或者目录的引用。软链接所产生的文件是无法更改的，它只是存储了目标文件的路径，并根据该路径去访问对应的文件。

##### 基本使用

在代码仓的根目录下存有 pnpm-workspace.yaml 文件指定哪些目录作为独立的工作空间，这个工作空间可以理解为一个子模块或者 npm 包。

'packages/\*': packages 目录下的所有子目录都会被视为独立的模块

![vue源码中的模块](/images/resource/workspace.png)

pnpm 并不是通过目录名称，而是通过目录下 package.json 文件的 name 字段来识别仓库内的包与模块的。

![vue源码示例](/images/resource/pnpm.png)

1️⃣ 为指定模块安装外部依赖

```js
// 为 a 包安装 lodash
pnpm --filter a i -S lodash // 生产依赖
pnpm --filter a i -D lodash // 开发依赖
```

2️⃣ 内部模块的相互依赖

```js
// 指定 a 模块依赖于 b 模块
pnpm --filter a i -S b
```

a/package.json

```json
{
  "name": "a",
  // ...
  "dependencies": {
    "b": "workspace:^"
  }
}
```

在实际发布 npm 包时，workspace:^ 会被替换成内部模块 b 的对应版本号(对应 package.json 中的 version 字段)。替换规律如下所示：

```json
{
  "dependencies": {
    "a": "workspace:*", // 固定版本依赖，被转换成 x.x.x
    "b": "workspace:~", // minor 版本依赖，将被转换成 ~x.x.x
    "c": "workspace:^" // major 版本依赖，将被转换成 ^x.x.x
  }
}
```

### 2.proxy

#### 基础使用

```js
// target 要使用 Proxy 包装的目标对象（可以是任何类型的对象，包括原生数组，函数，甚至另一个代理)
// handler 一个通常以函数作为属性的对象，用来定制拦截行为
const proxy = new Proxy(target, handler);
```

#### 参数 handler 对象的常用方法

- `handler.has()`
- `handler.get()`
- `handler.set()`
- `handler.deleteProperty()	`
- `handler.ownKeys()`

  `Object.getOwnPropertyNames()` 方法和 `Object.getOwnPropertySymbols()` 方法的捕捉器。

  【 补充 💡】

  - `Object.getOwnPropertyNames` 方法返回一个数组，成员是参数对象自身的全部属性的属性名，不管该属性是否可遍历。
  - `Object.keys` 只返回对象自身的可遍历属性的全部属性名。
  - `Object.getOwnPropertySymbols` 方法返回一个给定对象自身的所有 Symbol 属性的数组。

- `handler.apply()`

  函数调用操作的捕捉器。

- `handler.construct()`

  new 操作符的捕捉器

#### 可撤消的 Proxy(常用于完全封闭对目标对象的访问)

创建一个可撤销的代理对象:`Proxy.revocable(target, handler)`

该方法的返回值是一个对象，其结构为： `{"proxy": proxy, "revoke": revoke}`

- proxy 表示新生成的代理对象本身，和用一般方式 new Proxy(target, handler) 创建的代理对象没什么不同，只是它可以被撤销掉。
- revoke 撤销方法，调用的时候不需要加任何参数，就可以撤销掉和它一起生成的那个代理对象。

```js
const target = { name: 'vuejs' };
const { proxy, revoke } = Proxy.revocable(target, handler);
proxy.name; // 正常取值输出 vuejs
revoke(); // 取值完成对proxy进行封闭，撤消代理
proxy.name; // TypeError: Revoked
```

#### proxy 使用场景示例

1️⃣ 实现一个逻辑分离的数据格式验证器

```js
const target = {
  _id: '1024',
  name: 'vuejs'
};

const validators = {
  name(val) {
    return typeof val === 'string';
  },
  _id(val) {
    return typeof val === 'number' && val > 1024;
  }
};

const createValidator = (target, validator) => {
  return new Proxy(target, {
    _validator: validator,
    set(target, propkey, value, proxy) {
      let validator = this._validator[propkey](value);
      if (validator) {
        return Reflect.set(target, propkey, value, proxy);
      } else {
        throw Error(`Cannot set ${propkey} to ${value}. Invalid type.`);
      }
    }
  });
};

const proxy = createValidator(target, validators);

proxy.name = 'vue-js.com'; // vue-js.com
proxy.name = 10086; // Uncaught Error: Cannot set name to 10086. Invalid type.
proxy._id = 1025; // 1025
proxy._id = 22; // Uncaught Error: Cannot set _id to 22. Invalid type
```

2️⃣ 实现私有属性拦截

```js
const target = {
  _id: '1024',
  name: 'vuejs'
};

const proxy = new Proxy(target, {
  get(target, propkey, proxy) {
    if (propkey[0] === '_') {
      throw Error(`${propkey} is restricted`);
    }
    return Reflect.get(target, propkey, proxy);
  },
  set(target, propkey, value, proxy) {
    if (propkey[0] === '_') {
      throw Error(`${propkey} is restricted`);
    }
    return Reflect.set(target, propkey, value, proxy);
  }
});

proxy.name; // vuejs
proxy._id; // Uncaught Error: _id is restricted
proxy._id = '1025'; // Uncaught Error: _id is restricted
```

### 3.Object.defineProperty

#### 基础使用

`Object.defineProperty(obj, prop, descriptor)`

- obj 要定义属性的对象
- prop 要定义或修改的属性的名称或 Symbol
- descriptor 要定义或修改的属性描述符

```js
const obj = {};
Object.defineProperty(obj, 'a', {
  value: 1,
  writable: false, // 是否可写
  configurable: false, // 是否可配置
  enumerable: false // 是否可枚举
});

// 上面给了三个false, 下面的相关操作就很容易理解了
obj.a = 2; // 无效
delete obj.a; // 无效
for (key in obj) {
  console.log(key); // 无效
}
```

#### vue2 内部对于数组变异的方法处理

原因：defineProperty 无法检测到对象属性的添加和删除

```js
const methodsToPatch = [
  'push',
  'pop',
  'shift',
  'unshift',
  'splice',
  'sort',
  'reverse'
];

methodsToPatch.forEach(function (method) {
  // 缓存原生数组
  const original = arrayProto[method];
  // def使用Object.defineProperty重新定义属性
  def(arrayMethods, method, function mutator(...args) {
    const result = original.apply(this, args); // 调用原生数组的方法

    const ob = this.__ob__; // ob就是observe实例observe才能响应式
    let inserted;
    switch (method) {
      // push和unshift方法会增加数组的索引，但是新增的索引位需要手动observe的
      case 'push':
      case 'unshift':
        inserted = args;
        break;
      // 同理，splice的第三个参数，为新增的值，也需要手动observe
      case 'splice':
        inserted = args.slice(2);
        break;
    }
    // 其余的方法都是在原有的索引上更新，初始化的时候已经observe过了
    if (inserted) ob.observeArray(inserted);
    // dep通知所有的订阅者触发回调
    ob.dep.notify();
    return result;
  });
});
```

## vue3 vs vue2

- 1.源码优化:使用 **monorepo** 和 **ts** 管理和开发源码，提升代码可维护性。

  - monorepo 将 vue2 的模块拆分到不同的 package 中，每个 package 有各自的 API、类型定义和测试。

    ![](/images/resource/menu.png)

  - package 可以独立 vue 使用，如果用户只想使用 vue3 的响应式能力，可单独依赖这个响应式库而不用依赖整个 vue，减小了引用包的体积，vue2 无法提供这个功能。

  - vue3 中使用 ts 重构了整个项目，vue2 中使用的 Flow（对复杂场景的类型检查支持不够完善）

- 2.减少了源码体积：

  - 移除一些冷门的 feature（filter 等）
  - 引入 tree-shaking 的技术。tree-shaking 依赖 es2015 的静态结构（import 和 export），**通过编译阶段的静态分析，找到没有引入的模块并打上标记，没有引入的模块对应的代码将不会被打包**。

- 3.数据劫持优化

  数据劫持更新：当数据改变后，为了自动更新 dom，就必须劫持数据的更新。 因为在渲染 dom 的时候访问了数据，可以对它进行访问劫持，这样就在内部建立了依赖关系，也就知道数据对应的 dom 是什么了。

  **vue2 中使用:**

  ```js
  Object.defineProperty(data, 'a', {
    get() {
      // track
    },
    set() {
      //trigger
    }
  });
  ```

  ‼️`Object.defineProperty` 的缺点：

  1️⃣ defineProperty 是对 对象上的属性进行操作，而非对象本身实现数据劫持更新需要预先知道对象的 key，所以无法检测到对象属性的添加和删除，vue2 中对此提供的解决方案分别为`$set`和`$delete`方法

  2️⃣ 对于嵌套层级比较深的对象，vue 无法在运行时判断到底访问哪个属性。所以对于此类对象，vue 采用递归遍历每一层的数据对象且变成响应式，可能存在性能负担。

  **vue3 中使用：**

  示例

```js
observed = new Proxy(data, {
  // propkey 属性名;receiver Proxy 实例本身
  get(target, propKey, receiver) {
    // track
  },
  set() {
    // trigger
  }
});
```

`Proxy`劫持的是整个对象，可以检测到对象属性的添加和删除。但是`Proxy`不能监听到内部深层次的对象变化。vue 对此的处理方式是,在实际访问到内部对象时在 `getter` 中递归响应式

- 4.编译优化

  ![](/images/resource/编译.png)

  vue2 的数据更新并触发重新渲染的粒度是**组件级**的，在单组件内部需要遍历组件的 vnode 树，在 diff 过程中，vnode 性能和模板大小正相关，对于静态节点的 diff 实际上造成了性能的浪费，**理想状态下应只 diff 动态节点**。

  vue3 通过编译阶段对静态模板的分析，编译生成 Block tree，还包含了**对 Slot 的编译优化、事件侦听函数的缓存优化，并在运行时重写了 diff 算法**。

  ![](/images/resource/block.png)

- 5.语法优化

  - vue3 提供了`Composition API`,**将某个逻辑关注点相关的代码全都放在一个函数里。当需要修改一个功能时，不再需要在文件中反复定位**。

  - mixins(vue2) vs hook(vue3)

    当页面文件中多处使用 mixin 文件时，容易出现**命名冲突（props 、vaiable）和来源不清晰**的问题

    hook 解决了以上的问题

- 6.vue2 后期开始引入 RFC（Request For Comments），旨在为新功能进入框架提供一个一致且受控的路径，使得每个版本改动可控。大规模启用 RFC，了解每一个 feature 采用或被废弃的前因后果。

## 组件

一个组件想要渲染生成 dom 的几个步骤：创建 vnode --> 渲染 vnode --> 生成 dom

### 应用程序初始化

一个组件可以通过“模板+对象描述”的方式创建。整个组件树是由根组件开始渲染，为找到根组件的渲染入口，需要从应用程序的初始化过程开始分析。

vue2 初始化应用 vs vue3 初始化应用

都是将 App 组件挂载到 id 为 app 的节点上，但是 vue3 导入了`createApp`入口函数，是 vue3 对外暴露的内部函数。

![](/images/resource/初始化.png)

在 vue3 源码中，实际调用`createApp`函数的是`createAppAPI`方法，创建一个包含 mixins、components、directives、provides 等的对象，

#### `createApp`内部实现

⭐️ 在 app 对象创建过程中，vue 利用闭包和函数柯里化，实现了参数保留

```js
const createApp = (...args) => {
  // 创建app对象
  // ensureRenderer() 创建渲染器
  const app = ensureRenderer().createApp(...args);

  const { mount } = app;
  // 重写mount方法，来完善web平台下的渲染逻辑
  app.mount = (containerOrSelector) => {
    // 标准化容器 containerOrSelector参数：选择器字符串/DOM对象
    const container = normalizeContainer(containerOrSelector);
    if (!container) return;

    const component = app._component;
    // 如果组件对象没有定义render函数和template模板，则取容易的innerHTML作为模板内容
    if (!isFunction(component) && !component.render && !component.template) {
      component.template = container.innerHTML;
    }
    // 在挂载前清空容器内容
    container.innerHTML = '';
    // 真正的挂载
    const proxy = mount(container, false, resolveRootNamespace(container));
    return proxy;
  };
  return app;
};

// 渲染相关的一些配置，比如更新属性的方法，操作dom的方法等
const rendererOptions = {
  patchProp, // 处理props属性
  ...nodeOps //处理dom节点操作
};

// 延时创建渲染器（包含平台渲染核心逻辑的js对象），当用户只依赖响应式包时，可以通过tree-shaking移除核心渲染逻辑相关的代码
let renderer;
function ensureRenderer() {
  return renderer || createRenderer(rendererOptions);
}

export function createRenderer(options) {
  return baseCreateRenderer(options);
}

function baseCreateRenderer(options) {
  const render = (vnode, container, namespace) => {
    // 组件渲染的核心逻辑
    // vnode diff patch均在这个方法中实现
  };

  return {
    render,
    createApp: createAppAPI(render)
  };
}

function createAppAPI(render) {
  // createApp方法接受两个参数：根组件的对象和prop
  return function createApp(rootComponent, rootProps = null) {
    const app = {
      _component: rootComponent,
      _props: rootProps,
      _container: null,
      _context: context,
      _instance: null,

      get config() {
        //...
      },
      set config(v) {
        //...
      },
      use(plugin) {},
      mixin(mixin) {},
      component(name, component) {},
      directive(name, directive) {},
      unmount() {},
      provide(key, value) {},
      runWithContext(fn) {},

      // 挂载组件
      // 该方法是一个标准的可跨平台的组件渲染流程：先创建vnode，再渲染vnode
      mount(rootContainer) {
        // 创建根组件的vnode
        const vnode = createVNode(rootComponent, rootProps);
        // 利用渲染器渲染vnode;
        render(vnode, rootContainer);
        app._container = rootContainer;
        return vnode.component.proxy;
      }
    };

    return app;
  };
}
```

## 核心渲染流程（创建 vnode & 渲染 vnode）

### h()函数的定义

返回一个“虚拟节点” ，通常缩写为 VNode: 一个普通对象，其中包含向 Vue 描述它应该在页面上呈现哪种节点的信息，包括对任何子节点的描述。用于手动编写 render

vnode 本质上是用来描述 dom 的 js 对象，它在 vue 中可以描述不同类型的节点，比如普通元素节点、组件节点等

### h()函数的参数

- type 元素的类型
- propsOrChildren 数据对象, 这里主要表示(props, attrs, dom props, class 和 style)
- children 子节点

```js
export function h(type: any, propsOrChildren?: any, children?: any): VNode {
  const l = arguments.length;
  if (l === 2) {
    if (isObject(propsOrChildren) && !isArray(propsOrChildren)) {
      // single vnode without props
      if (isVNode(propsOrChildren)) {
        return createVNode(type, null, [propsOrChildren]);
      }
      // props without children
      return createVNode(type, propsOrChildren);
    } else {
      // omit props
      return createVNode(type, null, propsOrChildren);
    }
  } else {
    if (l > 3) {
      children = Array.prototype.slice.call(arguments, 2);
    } else if (l === 3 && isVNode(children)) {
      children = [children];
    }
    return createVNode(type, propsOrChildren, children);
  }
}
```

### vnode 的类型

- 普通元素 vnode
- 组件 vnode
- 纯文本 vnode
- 注释 vnode

普通元素 vnode 示例

![](/images/resource/vnode.png)

组件 vnode 示例

![](/images/resource/vnode组件.png)

### vnode 的优势

- 引入 vnode 可以将渲染过程抽象化，从而使组件的抽象能力得到提升

- 跨平台优势，patch vnode 的过程不同的平台可以有自己的实现，基于 vnode 再做服务端渲染，weex 平台、小程序平台渲染会容易很多。

❓vnode 比手动操作 dom 性能好吗

不一定，基于 vnode 实现的 MVVM 框架，在每次 render to vnode 的过程中，渲染组件会有一定的 js 耗时，尤其是大组件（例如数据量大的 table 组件）；不仅如此，在 patch vnode 的过程中，也会存在性能问题。diff 算法的优势在于减少 dom 操作，但是无法避免 dom 操作

### 创建 vnode：`createVNode`内部实现

- 标准化 props class
- 给 VNode 打上编码标记
- 创建 VNode
- 标准化子节点

`const vnode = createVNode(rootComponent,rootProps)`

```js
function createVNode(type, props = null, children = null) {
  if (props) {
    // 处理props相关逻辑，标准化class和style
  }

  // 对vnode类型信息编码
  const shapeFlag = isString(type)
    ? 1 // ELEMENT
    : isSuspense(type)
    ? 128 // SUSPENSE
    : isTeleport(type)
    ? 64 // TELEPORT
    : isObject(type)
    ? 4 // STATEFUL_COMPONENT
    : isFunction(type)
    ? 2 // FUNCTIONAL_COMPONENT
    : 0;

  // 创建vnode对象
  return createBaseVNode(
    type,
    props,
    shapeFlag,
    children
    //...其它属性
  );
}

function createBaseVNode(
  type,
  props,
  shapeFlag,
  children = null,
  patchFlag = 0,
  dynamicProps = null,
  isBlockNode = false,
  needFullChildrenNormalization = false
) {
  const vnode = {
    type,
    props,
    shapeFlag
    // ...一些其它属性
  };

  if (needFullChildrenNormalization) {
    // 标准化子节点，将不同数据类型的children转成数组或文本类型
    normalizeChildren(vnode, children);
  }
  return vnode;
}
```

##### 渲染 vnode

`render(vnode,rootContainer)`

**`render`内部实现**

```js
const render = (vnode, container, namespace) => {
  if (vnode == null) {
    // 销毁组件
    if (container._vnode) {
      unmount(container._vnode, null, null, true);
    }
  } else {
    // 创建或更新组件
    patch(
      container._vnode || null,
      vnode,
      container,
      null,
      null,
      null,
      namespace
    );
  }
  // 缓存vnode节点，表示已经渲染
  container._vnode = vnode;
};

const patch = (
  n1,
  n2,
  container,
  anchor = null,
  parentComponent = null,
  parentSuspense = null,
  namespace = undefined,
  slotScopeIds = null,
  optimized = false
) => {
  if (n1 === n2) {
    return;
  }

  // 如果存在新旧节点，且新旧节点类型不同，则销毁旧节点
  if (n1 && !isSameVNodeType(n1, n2)) {
    anchor = getNextHostNode(n1);
    unmount(n1, parentComponent, parentSuspense, true);
    n1 = null;
  }

  const { type, shapeFlag } = n2;
  // 处理节点的函数参数关注：
  // n1 旧的vnode，当n1为null，表示是一次挂载的过程
  // n2 新的vnode,后续会根据这个vnode类型执行不同的处理逻辑
  // container 表示dom容器，在vnode渲染生成DOM后，会挂载到container下面
  switch (type) {
    case Text:
      // 处理文本节点
      break;
    case Comment:
      // 处理注释节点
      break;
    case Static:
      // 处理静态节点
      break;
    case Fragment:
      // 处理Fragment元素
      break;
    default:
      //ELEMENT
      if (shapeFlag & 1) {
        // 处理普通dom元素
        processElement(
          n1,
          n2,
          container,
          anchor,
          parentComponent,
          parentSuspense,
          namespace,
          slotScopeIds,
          optimized
        );
      } else if (shapeFlag & 6) {
        // COMPONENT
        processComponent(
          n1,
          n2,
          container,
          anchor,
          parentComponent,
          parentSuspense,
          namespace,
          slotScopeIds,
          optimized
        );
      } else if (shapeFlag & 64) {
        // TELEPORT
        type.process(
          n1,
          n2,
          container,
          anchor,
          parentComponent,
          parentSuspense,
          namespace,
          slotScopeIds,
          optimized,
          internals
        );
      } else if (__FEATURE_SUSPENSE__ && shapeFlag & 128) {
        // SUSPENSE
        type.process(
          n1,
          n2,
          container,
          anchor,
          parentComponent,
          parentSuspense,
          namespace,
          slotScopeIds,
          optimized,
          internals
        );
      } else if (__DEV__) {
        warn('Invalid VNode type:', type, `(${typeof type})`);
      }
  }
};

// ❗️组件的processComponent函数实现
const processComponent = (
  n1,
  n2,
  container,
  anchor,
  parentComponent,
  parentSuspense,
  namespace,
  slotScopeIds,
  optimized
) => {
  n2.slotScopeIds = slotScopeIds;

  if (n1 == null) {
    // 挂载组件
    mountComponent(
      n2,
      container,
      anchor,
      parentComponent,
      parentSuspense,
      namespace,
      optimized
    );
  } else {
    // 更新组件
    updateComponent(n1, n2, optimized);
  }
};

// 【组件processComponent函数】挂载组件代码实现
const mountComponent = (
  initialVNode,
  container,
  anchor,
  parentComponent,
  parentSuspense,
  namespace,
  optimized
) => {
  // 创建组件实例，内部通过对象的方式创建了当前渲染的组件实例
  const instance = (initialVNode.component = createComponentInstance(
    initialVNode,
    parentComponent,
    parentSuspense
  ));
  // 设置组件实例，instance保留了很多组件相关的数据，维护了组件上下文包括对props、插槽、以及其它实例的属性的初始化处理
  setupComponent(instance);
  // 设置并运行带副作用的渲染函数
  setupRenderEffect(
    instance,
    initialVNode,
    container,
    anchor,
    parentSuspense,
    namespace,
    optimized
  );
};
```

## vue3 源码结构

### packages

- 📁compiler-core 编译器核心：parse、optimize、codegen
- 📁compiler-dom 编译器针对浏览器的编译器
- 📁compiler-sfc 编译器针对单文件组件的编译器
- 📁compiler-ssr 编译器针对服务端渲染的编译器
- 📁reactivity 响应式：defineReactive、proxy、ref、reactive、computed、watch
- 📁runtime-core 渲染器核心：h、createVNode、renderSlot、patchProp、patchText、patchClass、patchStyle、patchEvent、processElement、processComponent、insert、remove、createApp
- 📁runtime-dom 渲染器针对浏览器的运行时
- 📁server-renderer 服务端渲染

---

### 定义响应式数据

```js
// reactivity/reactive.ts
function reactive(target) {
  // 如果对象只读，无法被修改成响应式对象，则直接返回该对象
  if (isReadonly(target)) {
    return target;
  }
  return createReactiveObject(
    target,
    false,
    mutableHandlers,
    mutableCollectionHandlers,
    reactiveMap
  );
}

function createReactiveObject(
  target,
  isReadonly,
  baseHandlers,
  collectionHandlers,
  proxyMap
) {
  // 基础数据直接返回target
  if (!isObject(target)) {
    return target;
  }

  // 要求返回对象的原始不代理版本，并且对象为响应式 & 非只读
  if (
    target[ReactiveFlags.RAW] &&
    !(isReadonly && target[ReactiveFlags.IS_REACTIVE])
  ) {
    return target;
  }

  // 检查是否存在target对应的代理
  const existingProxy = proxyMap.get(target);
  if (existingProxy) {
    return existingProxy;
  }

  // only specific value types can be observed.
  const targetType = getTargetType(target);
  if (targetType === TargetType.INVALID) {
    return target;
  }
  const proxy = new Proxy(
    target,
    targetType === TargetType.COLLECTION ? collectionHandlers : baseHandlers
  );
  proxyMap.set(target, proxy);
  return proxy;
}
```

## nextTick

### nextTick 的出现是因为 dom 的更新是异步的

以下是官网的说明：

只要侦听到数据变化，Vue 将开启一个队列，并缓冲在同一事件循环中发生的所有数据变更。如果同一个 watcher 被多次触发，只会被推入到队列中一次。这种在缓冲时去除重复数据对于避免不必要的计算和 DOM 操作是非常重要的。然后，在下一个的事件循环“tick”中，Vue 刷新队列并执行实际 (已去重的) 工作。Vue 在内部对异步队列尝试使用原生的 Promise.then、MutationObserver 和 setImmediate，如果执行环境不支持，则会采用 setTimeout(fn, 0) 代替。

`nextTick()`可以在状态改变后立即使用，以等待 DOM 更新完成。nextTick() 返回的是 Promise 对象,可以传递一个回调函数作为参数，或者 await 返回的 Promise。

`function nextTick(callback?: () => void): Promise<void>`

`nextTick()`官网示例：

```vue
<script setup>
import { ref, nextTick } from 'vue';

const count = ref(0);

async function increment() {
  count.value++;

  // DOM 还未更新
  console.log(document.getElementById('counter').textContent); // 0

  await nextTick();
  // DOM 此时已经更新
  console.log(document.getElementById('counter').textContent); // 1
}
</script>

<template>
  <button id="counter" @click="increment">{{ count }}</button>
</template>
```

### 实现 nextTick

原理：基于 js 的事件循环机制实现，创建一个异步任务，在同步任务结束后即执行

```typescript
let currentFlushPromise: Promise<void> | null = null;
const resolvedPromise = Promise.resolve() as Promise<any>;

export function nextTick<T = void, R = void>(
  this: T,
  fn?: (this: T) => R
): Promise<Awaited<R>> {
  const p = currentFlushPromise || resolvedPromise;
  return fn ? p.then(this ? fn.bind(this) : fn) : p;
}
```

### ❓vue3 中任务调度的实现过程

源码 renderer.ts 文件中的`setupRenderEffect`函数是处理组件渲染的核心函数。
setupRenderEffect 函数中创建了 update 对象

![](/images/resource/setupRender.png)

`queueJob()`函数用于 维护 job 列队，将一个任务 job 添加到任务队列 queue，调用 `queueFlush()`函数触发任务刷新 。函数中有去重逻辑(重复数据删除搜索使用 Array.includes() 的 startIndex 参数)，保证任务的唯一性。

具体实现：

- 对 job 任务进行判断

1️⃣ 首先检查任务队列是否为空，如果为空，直接将任务添加到队列中。

2️⃣ 然后，使用 `includes` 方法检查当前任务 job 是否已经在任务队列中。如果任务队列中已经包含了当前任务，就不再添加。

- 如果 job 任务通过判断，就将任务添加到任务队列中

1️⃣ 如果任务的 id 属性为 null，表示没有指定任务的唯一标识，直接将任务添加到队列末尾`queue.push(job)`。

2️⃣ 如果任务的 id 属性不为 null，表示指定了任务的唯一标识，需要根据该标识找到合适的插入位置，以保持任务队列中的任务按照 id 的顺序执行（按照 job id 自增的顺序排列）。调用 `findInsertionIndex(job.id)` 来找到插入位置，然后使用 splice 方法插入任务到指定位置

- 调用 `queueFlush()`函数触发任务刷新

```typescript
// scheduler.ts
export function queueJob(job: SchedulerJob) {
  if (
    !queue.length ||
    !queue.includes(
      job,
      isFlushing && job.allowRecurse ? flushIndex + 1 : flushIndex
    )
  ) {
    if (job.id == null) {
      queue.push(job);
    } else {
      queue.splice(findInsertionIndex(job.id), 0, job);
    }
    queueFlush();
  }
}

// 使用二分查找确认位置保证队列的递增顺序
function findInsertionIndex(id: number) {
  // the start index should be `flushIndex + 1`
  let start = flushIndex + 1;
  let end = queue.length;

  while (start < end) {
    const middle = (start + end) >>> 1;
    const middleJob = queue[middle];
    const middleJobId = getId(middleJob);
    if (middleJobId < id || (middleJobId === id && middleJob.pre)) {
      start = middle + 1;
    } else {
      end = middle;
    }
  }

  return start;
}

function queueFlush() {
  // 没有挂起的刷新请求且没有正在刷新任务队列
  if (!isFlushing && !isFlushPending) {
    isFlushPending = true; // 刷新请求被挂起
    // 将刷新操作包装成 Promise，将 flushJobs 放入下一个微任务中执行
    currentFlushPromise = resolvedPromise.then(flushJobs);
  }
}

function flushJobs(seen?: CountMap) {
  isFlushPending = false;
  // 执行刷新任务队列操作
  isFlushing = true;
  if (__DEV__) {
    seen = seen || new Map();
  }
  // 刷新之前对队列进行排序，确保组件从父级更新到子级。如果在父组件更新期间被卸载，可以跳过更新
  queue.sort(comparator);

  // 检查是否存在递归更新
  const check = __DEV__
    ? (job: SchedulerJob) => checkRecursiveUpdates(seen!, job)
    : NOOP;

  try {
    for (flushIndex = 0; flushIndex < queue.length; flushIndex++) {
      const job = queue[flushIndex];
      if (job && job.active !== false) {
        if (__DEV__ && check(job)) {
          continue;
        }
        callWithErrorHandling(job, null, ErrorCodes.SCHEDULER);
      }
    }
  } finally {
    // 清空 flushIndex，重置任务队列 queue，刷新任务结束，将当前的刷新promise置为null，确保任务只执行一次。
    flushIndex = 0;
    queue.length = 0;

    flushPostFlushCbs(seen);

    isFlushing = false;
    currentFlushPromise = null;

    // 如果任务队列 queue 中仍有任务，或者有挂起的 postFlush 回调函数，就继续执行刷新操作，直到任务队列为空。
    if (queue.length || pendingPostFlushCbs.length) {
      flushJobs(seen);
    }
  }
}
```

`queuePostFlushCb()` 维护 cb 列队，被调用的时候去重，每次调用去执行 `queueFlush()`

```typescript
export function queuePostFlushCb(cb: SchedulerJobs) {
  if (!isArray(cb)) {
    if (
      !activePostFlushCbs ||
      !activePostFlushCbs.includes(
        cb,
        cb.allowRecurse ? postFlushIndex + 1 : postFlushIndex
      )
    ) {
      pendingPostFlushCbs.push(cb);
    }
  } else {
    pendingPostFlushCbs.push(...cb);
  }
  queueFlush();
}
```

todo: diff 算法优化
