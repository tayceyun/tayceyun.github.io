## vue3 vs vue2

- 1.源码优化:使用 monorepo 和 ts 管理和开发源码，提升代码可维护性。

  - monorepo 将 vue2 的模块拆分到不同的 package 中，每个 package 有各自的 API、类型定义和测试。

    ![](/images/resource/menu.png)

  - package 可以独立 vue 使用，如果用户只想使用 vue3 的响应式能力，可单独依赖这个响应式库而不用依赖整个 vue，减小了引用包的体积，vue2 无法提供这个功能。

  - vue3 中使用 ts 重构了整个项目，vue2 中使用的 Flow（对复杂场景的类型检查支持不够完善）

- 2.减少了源码体积：

  - 移除一些冷门的 feature（filter 等）
  - 引入 [tree-shaking](https://juejin.cn/post/6844903544756109319) 的技术。tree-shaking 依赖 es2015 的静态结构（import 和 export），**通过编译阶段的静态分析，找到没有引入的模块并打上标记**，没有引入的模块对应的代码将不会被打包。

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

  1️⃣ 实现数据劫持更新需要预先知道对象的 key，所以无法检测到对象属性的添加和删除，vue2 中对此提供的解决方案分别为`$set`和`$delete`方法

  2️⃣ 对于嵌套层级比较深的对象，vue 无法在运行时判断到底访问哪个属性。所以对于此类对象，vue 采用递归遍历每一层的数据对象且变成响应式，可能存在性能负担。

  **vue3 中使用：**

  ```js
  observed = new Proxy(data, {
    get() {
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

  vue2 的数据更新并触发重新渲染的粒度是组件级的，在单组件内部需要遍历组件的 vnode 树，在 diff 过程中，vnode 性能和模板大小正相关，对于静态节点的 diff 实际上造成了性能的浪费，理想状态下应只 diff 动态节点。

  vue3 通过编译阶段对静态模板的分析，编译生成 Block tree，还包含了对 Slot 的编译优化、事件侦听函数的缓存优化，并在运行时重写了 diff 算法。

  ![](/images/resource/block.png)

- 5.语法优化

  - vue3 提供了`Composition API`,将某个逻辑关注点相关的代码全都放在一个函数里。当需要修改一个功能时，不再需要在文件中反复定位。

  - mixins(vue2) vs hook(vue3)

    当页面文件中多处使用 mixin 文件时，容易出现命名冲突（props 、vaiable）和来源不清晰的问题

    hook 解决了以上的问题

- 6.vue2 后期开始引入 RFC（Request For Comments），旨在为新功能进入框架提供一个一致且受控的路径，使得每个版本改动可控。大规模启用 RFC，了解每一个 feature 采用或被废弃的前因后果。

## 组件

一个组件想要渲染生成 dom 的几个步骤：创建 vnode --> 渲染 vnode --> 生成 dom

### 应用程序初始化

一个组件可以通过“模板+对象描述”的方式创建。整个组件树是由根组件开始渲染，为找到根组件的渲染入口，需要从应用程序的初始化过程开始分析。

vue2 初始化应用 vs vue3 初始化应用

都是将 App 组件挂载到 id 为 app 的节点上，但是 vue3 导入了`createApp`入口函数，是 vue3 对外暴露的内部函数。

![](/images/resource/初始化.png)

**`createApp`内部实现**

⭐️ 在 app 对象创建过程中，vue 利用闭包和函数柯里化，实现了参数保留

```js
const createApp = (...args) => {
  // 创建app对象
  // ensureRenderer() 延时创建渲染器
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
const rendererOptions = { patchProp, ...nodeOps };

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

### 核心渲染流程（创建 vnode & 渲染 vnode）

#### vnode

vnode 本质上是用来描述 dom 的 js 对象，它在 vue 中可以描述不同类型的节点，比如普通元素节点、组件节点等

##### vnode 的类型

- 普通元素 vnode
- 组件 vnode
- 纯文本 vnode
- 注释 vnode

普通元素 vnode 示例

![](/images/resource/vnode.png)

组件 vnode 示例

![](/images/resource/vnode组件.png)

##### vnode 的优势

- 引入 vnode 可以将渲染过程抽象化，从而使组件的抽象能力得到提升

- 跨平台优势，patch vnode 的过程不同的平台可以有自己的实现，基于 vnode 再做服务端渲染，weex 平台、小程序平台渲染会容易很多。

❓vnode 比手动操作 dom 性能好吗

不一定，基于 vnode 实现的 MVVM 框架，在每次 render to vnode 的过程中，渲染组件会有一定的 js 耗时，尤其是大组件（例如数据量大的 table 组件）；不仅如此，在 patch vnode 的过程中，也会存在性能问题。diff 算法的优势在于减少 dom 操作，但是无法避免 dom 操作

##### 创建 vnode

**`createVNode`内部实现**

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
