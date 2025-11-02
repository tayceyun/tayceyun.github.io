## 开源项目学习

### Hooks

Hooks 本质上是一组可复用的函数。Vue3 中的 Hooks 是通过 setup 函数来使用的，setup 函数是 Vue3 组件中的一个新的生命周期函数，它在**组件实例被创建之前**调用，并且接收两个参数：`props` 和 `context`。在 setup 函数中，我们可以定义和返回组件中需要使用的响应式数据、方法、计算属性等，而这些都可以通过 Hooks 来实现。

Hooks 使用场景：

1. 逻辑复用：提高代码复用性。
2. 逻辑拆分：使用 Hooks 将组件的逻辑拆分成多个独立的函数，每个函数负责处理一部分逻辑。使组件的代码更加清晰、易于维护。
3. 副作用管理：Hooks 中的函数可以访问组件的响应式数据，并且可以在组件的生命周期中执行副作用操作。

第三方 Hooks：

1. Vueuse
2. @vue/reactivity：Vue 官方提供的响应式库，虽然它不是一个 Hooks 库，但其中的函数和工具可以与 Composition API 结合使用，创建自定义的 Hooks 来处理响应式数据和副作用。例如：可以使用 reactive、ref、computed 等函数来创建响应式数据和计算属性。

3. `InjectionKey`：对`inject`引入数据进行类型约束，确保父子间传递的数据类型是可见、透明的。
4. `UnwrapRef`：解套 Ref 时的类型声明

#### core / useContext： 数据跨层级使用

##### 封装

```typescript
import {
  InjectionKey,
  provide,
  inject,
  reactive,
  readonly as defineReadonly,
  UnwrapRef
} from 'vue';

export interface CreateContextOptions {
  readonly?: boolean;
  createProvider?: boolean;
  native?: boolean;
}

type ShallowUnwrap<T> = {
  // P是 T的key集合
  [P in keyof T]: UnwrapRef<T[P]>;
};

// 封装provide
export function createContext<T>(
  context: any,
  key: InjectionKey<T> = Symbol(),
  options: CreateContextOptions = `{}`
) {
  const `{ readonly = true, createProvider = false, native = false }` = options;

  const state = reactive(context); // 将context转为响应式
  const provideData = readonly ? defineReadonly(state) : state;
  !createProvider && provide(key, native ? context : provideData);

  return {
    state
  };
}

export function useContext<T>(key: InjectionKey<T>, native?: boolean): T;

// 封装inject
export function useContext<T>(
  key: InjectionKey<T> = Symbol(),
  defaultValue?: any
): ShallowUnwrap<T> {
  return inject(key, defaultValue || `{}`);
}
```
