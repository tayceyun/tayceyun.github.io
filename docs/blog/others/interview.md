---
sidebar: auto
tags:
  - interview
---

### [对比:MVVM 和 MVC] MVC (Model-View-Controller) and MVVM (Model-View-ViewModel)

MVC and MVVM are different design patterns:

• Model: Represents the data and business logic.
• View: Represents the UI elements.
• Controller: Handles user input and updates the Model and View.
• ViewModel: Acts as an intermediary between the View and the Model, handling the presentation logic and state.Exposing data from the Model to the View, manages the state of the View, and handles user interactions by binding them to commands.

总结：

viewModel is an intermediary between the View and the Model.viewModel contains two important functions: **data bindings** & **dom listeners**

The MVVM model simplifies the dependence between the interface and the business logics and solves the problem of frequent data updates.

Also MVVM can be applied across different platforms and frameworks.

bidirectional Binding allows the Viewodel to automatically update when the Model changes, and when the ViewModel changes, the View will also automatically change.

### [SPA：单页面应用]Single Page Application

- After initial loading, SPA can dynamically updates the current page instead of loading new pages from the server.React、Angular、Vue are all popular SPA Frameworks and Libraries.
- Client side routing:hash (theroy: **hashChange** function) 局部刷新，不利于 SEO

Multiple Page Application:history (theroy : history.pushState / history.replaceState)

### [vue2：响应式原理] Object.defineProperty

Proxy 只会代理对象的第一层，那么 vue3 又是怎样处理这个问题的呢?
判断当前 Reflect.get 的 返回值是否为 0bject ，如果是则再通过 reactive 方法做代理这样就实现了深度观测

监测数组的时候可能触发多次 get/set，那么如何防止触发多次呢?
我们可以判断 key 是否为当前被代理对象 target 自身属性，也可以判断旧值与新值是否相等，只有满足以上两个条件之一时，才有可能执行 trigger
