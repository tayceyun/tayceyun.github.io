---
sidebar: auto
tags:
  - react
---

## React 基础

### react 和 vue 对比

1️⃣ 设计理念

- Vue 是一款渐进式框架，可以根据项目的需求逐渐引入和使用其功能。Vue 强调灵活性和高效性。
- React 是一款组件化的框架，将用户界面划分为独立可复用的组件，强调构建大型应用的可维护性和性能优化。

2️⃣ 语法

- Vue 使用模板语法（如{{}}）来处理数据绑定和渲染，模板中可以直接写 HTML 标签和 Vue 特有的指令。
- React 使用 JSX 语法，将 HTML 和 JavaScript 结合在一起，通过编写 JavaScript 代码来创建组件和处理数据渲染。

3️⃣ 响应式原理

- Vue 使用响应式数据绑定机制，当数据变化时，自动更新相关的 DOM。Vue 通过 Proxy 或 Object.defineProperty 来实现响应式。
- React 使用虚拟 DOM 和 diff 算法，通过比较前后两次虚拟 DOM 的差异来更新真实 DOM，从而提高渲染性能。

4️⃣ 数据流

- Vue 使用双向绑定，即数据的变化可以自动更新视图，同时视图的变化也可以自动更新数据。
- React 使用单向数据流，数据的变化只能从父组件传递到子组件，子组件不能直接修改父组件的数据。

### 了解 React

react 特点：① 声明式编程 ② 组件化开发

react 有三个依赖：① react ② react-dom ③ babel

## 语法

### 属性绑定

```jsx
class App extends React.Component {
  constructor() {
    super();
    this.state = {
      message: 'hello world',
      movies: ['测试1', '测试2', '测试3']
    };
    // 方式二：对需要绑定的方法提前操作
    this.changeClick = this.changeClick.bind(this);
  }

  btnClick() {
    // 将state中的message修改，自动执行render函数
    this.setState({
      message: 'change text'
    });
  }

  changeClick() {
    this.setState({
      message: 'change'
    });
  }

  render() {
    const { message } = this.state;
    return (
      <div>
        {/*1. 基础使用 */}
        <h2>解构赋值:{message}</h2>
        <h2>{this.state.message}</h2>
        {/* 方式一：使用bind方法绑定this */}
        <button onClick={this.btnClick.bind(this)}>change text</button>
        <br></br>
        <button onClick={this.changeClick}>change text</button>
        <button onClick={() => this.changeClick}>change text</button>

        {/*2. 列表渲染 */}
        <ul>
          {this.state.movies.map((v) => (
            <li key={v}>{v}</li>
          ))}
        </ul>

        {/*3. 属性绑定 */}
        <h2 title={title}>属性绑定</h2>

        {/*4. class和style绑定 */}
        <div className="aaa">className</div>
        <div className={className}>动态class</div>
        <div style={{ color: 'red', fontSize: '20px' }}>test style</div>
      </div>
    );
  }
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
```

### jsx 原理

> jsx 是 `React.createElement(component,props,...children)`函数的语法糖

> 需要传递三个参数：
>
> `type`: 当前`ReactElement`的类型；如果是标签元素，就用字符串表示如'div';如果是组件元素就用组件名称
>
> `config`: 所有 jsx 中的属性都在 config 中以对象的属性和值的形式存储，如传入`className`作为元素的 class
>
> `children`: 存放在标签中的内容，以 children 数组的方式进行存储

### 虚拟 dom

> 通过`ReactDOM.render`让虚拟 dom 和真实 dom 同步起来，这个过程叫做协调。
>
> 虚拟 dom 帮助我们从命令式编程转为声明式编程的模式

### render 函数的返回值

> 当 render 被调用时，它会检查`this.props`和`this.state`的变化并返回以下类型之一:
>
> - React 元素：
>
> ① 通常通过`JSX`创建
>
> ② 如 `div`会被 react 渲染成`DOM`节点，`<MyComponent>`会被 react 渲染为自定义组件
>
> - 数组或`fragments`:使用`render`方法可以返回多个元素；如果是数组，react 内部将遍历数组的元素并渲染展示到页面上。
> - `Portals` 可以渲染子节点到不同的`DOM`子树中
> - 字符串或数值类型：在`DOM`中会被渲染为文本节点
> - 布尔类型或 null：不渲染

### 书籍案例

```jsx
import React from 'react';
import ReactDOM from 'react-dom';
import { bookList } from './config';

// 书籍案例
class App extends React.Component {
  constructor() {
    super();
    this.state = {
      bookList: bookList
    };
  }

  changeNum = (index, count) => {
    const newBookList = [...this.state.bookList];
    newBookList[index].num += count;
    this.setState({
      bookList: newBookList
    });
  };

  delBook = (index) => {
    let newBookList = [...this.state.bookList];
    newBookList.splice(index, 1);
    this.setState({
      bookList: newBookList
    });
  };

  getTotalPrice = () => {
    return this.state.bookList.reduce((prev, item) => {
      return prev + item.num * item.price;
    }, 0);
  };

  renderBooks = () => {
    return (
      <div>
        <table>
          <thead>
            <tr>
              <th>序号</th>
              <th>书籍名称</th>
              <th>价格</th>
              <th>数量</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            {bookList.map((item, index) => {
              return (
                <tr key={index}>
                  <td>{item.id}</td>
                  <td>{item.name}</td>
                  <td>{item.price}</td>
                  <td>
                    <button
                      disabled={item.num <= 1}
                      onClick={() => this.changeNum(index, -1)}
                    >
                      -
                    </button>
                    {item.num}
                    <button onClick={() => this.changeNum(index, 1)}>+</button>
                  </td>
                  <td>
                    <button onClick={() => this.delBook(index)}>删除</button>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
        <div>合计:{this.getTotalPrice()}</div>
      </div>
    );
  };

  emptyBook = () => {
    return (
      <div>
        <h1>暂无数据</h1>
      </div>
    );
  };

  render() {
    const { bookList } = this.state;
    return bookList.length ? this.renderBooks() : this.emptyBook();
  }
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<App />);
```

## 组件分类

### 按定义方式：函数组件和类组件

- 类组件

> 类组件有如下要求：
>
> ① 定义类，继承自`React.component`
>
> ② 类组件必须实现`render`函数
>
> ③ 组件名称是大写字符开头

> 使用`class`定义一个组件：
>
> ①`constructor`是可选的，通常在`constructor`中初始化一些数据
>
> ②`this.state`来维护组件内部的数据
>
> ③`render()`方法是`class`组件中唯一必须实现的方法

```jsx
import React from 'react';
class App extends React.Component {
  constructor() {
    super();
    this.state = {
      message: 'app component'
    };
  }
  render() {
    const { message } = this.state;
    return <div>{message}</div>;
  }
}

export default App;
```

- 函数式组件

  **特点：**

  ① 会被更新并挂载，但没有生命周期

  ②`this`关键字不能指向组件实例

  ③ 没有内部状态`state`

  ④ 不能使用`ref`

```jsx
function App() {
  return (
    <div className="App">
      <h1>函数式组件</h1>
    </div>
  );
}
export default App;
```

### 按是否有状态维护：无状态组件和有状态组件

### 按不同职责：展示型组件和容器型组件

### vscode 插件常见代码块生成

```jsx
// rcep 对传入组件的类型进行限制
import PropTypes from 'prop-types';
import React, { Component } from 'react';

export class App extends Component {
  static propTypes = {};

  render() {
    return <div>App</div>;
  }
}

export default App;


// rpc
import React, { PureComponent } from 'react'

export default class App extends PureComponent {
  render() {
	return (
	  <div>App</div>
	)
  }
}

// rpce
import React, { PureComponent } from 'react'

export class App extends PureComponent {
  render() {
	return (
	  <div>App</div>
	)
  }
}

export default App

// rmc 函数式组件
import React, { memo } from 'react'

const App = memo(() => {
  return (
	<div>App</div>
  )
})

export default App
```

## 生命周期

### 基础执行顺序

先执行`constructor`,再执行`render`;

当组件挂载到 dom 上时，执行`componentDidMount`；

当数据发生修改时会再执行`render`函数，组件 dom 更新完成，dom 发生更新时执行`componentDidUpdate`函数；组件卸载或销毁前执行`componentWillUnmount`函数。

### 常用生命周期函数

- `Constructor`:

  - 给`this.state`赋值对象来初始化内部的`state`;为事件绑定实例`this`。

  - 如不初始化 state 或不进行方法绑定，则不需要为 react 组件实现构造函数。

- `componentDidMount`:会在组件挂载到 dom 上时调用：

  - 进行`dom`操作

  - 数据请求

  - 添加订阅（在`compoentWillUnmount`中取消订阅）

- `componentDidUpdate`:

  - `componentDidUpdate(prevProps,prevState,snapshot)`在更新之后会被立即调用，首次渲染不会执行；

  - 如果需要对更新前后的`props`进行比较，可执行此函数。

- `componentWillUnmount`:

  - 会在组件被卸载及销毁之前直接调用

### 不常用生命周期函数

- `getDerivedStateFromProps`: `state`的值在任何时候都依赖于`props`时使用，该方法返回一个对象来更新`state`
- `getSnapshotBeforeUpdate`:在 react 更新`dom`前回调的函数，可以获取`DOM`更新前的信息（比如滚动位置）
- `shouldComponentUpdate`: 常用于性能优化

## 父子通信

父组件传递数据给子组件的方式:

- 父组件通过属性=值的形式传递给子组件数据
- 子组件通过`props`参数获取父组件传递过来的数据

### 父传子

```jsx
// App.jsx
import React from 'react';
import SonComponent from './SonComponent';

class App extends React.Component {
  constructor() {
    super();
    this.state = {
      productList: ['test1', 'test2']
    };
  }
  render() {
    const { productList } = this.state;
    return (
      <div>
        <SonComponent productList={productList}></SonComponent>
      </div>
    );
  }
}

export default App;
```

子组件

```jsx
// SonComponent.jsx
import React, { Component } from 'react';

export class son extends Component {
  // 如果子组件中不需要定义state,可省略constructor函数
  // constructor(props) {
  //   super(props);
  // }
  render() {
    const { productList } = this.props;
    return (
      <div>
        <ul>
          {productList.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      </div>
    );
  }
}

export default son;
```

#### 传值类型检查 & 参数默认值

使用`propTypes`对传入子组件的变量进行类型检查

- Ⅰ array、 bool、 func、 number、 object、 string、 symbol、 node(节点类型)、 element（react 元素）、 elementType(react 元素类型)
- Ⅱ 或可以声明 prop 为类的实例，使用 instanceof 操作符 `propTypes.instanceof()`
- Ⅲ 或可使 prop 只能是特定的值 枚举类型 `propTypes.oneOf(['news','photo'])`
- Ⅳ 或可设定是集中类型中的任意一个类型 `propTypes.oneOfType([propTypes.string,propTypes.number])`

`defaultProps`设置默认值(2 种方式)，如下：

```JSX
import React, { Component } from 'react';
import propTypes from 'prop-types';

export class SonComponent extends Component {
 // es2022 props默认值设置的另一种方式: 在react类组件中将 defaultProps声明为静态属性
 // static defaultProps = {
 //   productList: []
 // };
  render() {
    const { productList } = this.props;
    return (
      <div>
        <ul>
          {productList.map((item) => (
            <li key={item.title}>{item.title}</li>
          ))}
        </ul>
      </div>
    );
  }
}

SonComponent.propTypes = {
  productList: propTypes.array.isRequired
};

SonComponent.defaultProps = {
  productList: []
};
export default SonComponent;
```

### 子传父

```jsx
// 父组件
import React from 'react';
import AddCount from './AddCount';

class App extends React.Component {
  constructor() {
    super();
    this.state = {
      num: 0
    };
  }

  changeCount = (count) => {
    this.setState({
      num: (this.state.num += count)
    });
  };

  render() {
    const { num } = this.state;
    return (
      <div>
        计数：{num}
        <br />
        计数子组件：
        <AddCount addClick={(count) => this.changeCount(count)}></AddCount>
      </div>
    );
  }
}

export default App;
```

子组件

```jsx
// 子组件
import React, { Component } from 'react';
import propTypes from 'prop-types';

export class AddCount extends Component {
  addNum(count) {
    this.props.addClick(count);
  }
  render() {
    return (
      <div>
        <button onClick={() => this.addNum(1)}>1</button>
      </div>
    );
  }
}

AddCount.propTypes = {
  addClick: propTypes.func
};

export default AddCount;
```

## 实现插槽

### 方式一：组件的`children`子元素

弊端：通过索引取元素容易出错

父组件

```jsx
// App.jsx
import React from 'react';
import NavBar from './NavBar';

class App extends React.Component {
  constructor() {
    super();
    this.state = {};
  }

  render() {
    return (
      <div className="app">
        <NavBar>
          {/* 如果放多个，children是数组，如果是一个，则children为单个标签 */}
          <span>左边</span>
          {/* <input type="text" />
          <button>搜索</button> */}
        </NavBar>
      </div>
    );
  }
}

export default App;
```

子组件

```jsx
// NavBar.jsx
import React, { Component } from 'react';
import propTypes from 'prop-types';

export class NavBar extends Component {
  render() {
    const { children } = this.props;
    return (
      <div className="nav-bar">
        <div className="left">{children}</div>
        {/* <div className="mid">{children[1]}</div>
        <div className="right">{children[2]}</div> */}
      </div>
    );
  }
}

NavBar.propTypes = {
  // 限制传入的children只能是一个元素
  children: propTypes.element
  // 多个元素
  // children: propTypes.Array
};

export default NavBar;
```

### 方式二：`props`属性传递 react 元素

```jsx
// App.jsx
import React from 'react';
import NavbarProp from './NavbarProp';

class App extends React.Component {
  render() {
    return (
      <div className="app">
        <NavbarProp
          leftSlot={<span>左边</span>}
          midSlot={<input type="text" />}
          rightSlot={<button>搜索</button>}
        ></NavbarProp>
      </div>
    );
  }
}

export default App;
```

```jsx
// NavbarProp.jsx
import React, { Component } from 'react';
import './views/navbar-demo/navbar.css';

export class NavbarProp extends Component {
  render() {
    const { leftSlot, rightSlot, midSlot } = this.props;
    return (
      <div className="nav-bar">
        <div className="left">{leftSlot}</div>
        <div className="mid">{midSlot}</div>
        <div className="right">{rightSlot}</div>
      </div>
    );
  }
}

export default NavbarProp;
```

### 作用域插槽

同样通过`props`实现

父组件

```jsx
// App.js
import React, { PureComponent } from 'react';
import NavBar from './NavBar';

export class App extends PureComponent {
  constructor() {
    super();
    this.state = {
      titles: ['测试', '标题', '插槽']
    };
  }

  render() {
    const { titles } = this.state;
    return (
      <div>
        <NavBar
          itemType={(item) => <button>{item}</button>}
          title={titles}
        ></NavBar>
      </div>
    );
  }
}

export default App;
```

子组件

```jsx
// NavBar.jsx
import React, { PureComponent } from 'react';

export class NavBar extends PureComponent {
  render() {
    const { title, itemType } = this.props;
    return (
      <div className="nav-bar">
        {title.map((item) => {
          return <div key={item}>{itemType(item)}</div>;
        })}
      </div>
    );
  }
}

export default NavBar;
```

## 非父子组件通信

类似于 vue 中的`provide`和`inject`

### 方式一：逐层传递`props`

> 注意点：① 如何将对象传给子组件 `<Context {...info}></Context>` 、`<SonContext {...this.props}></SonContext>`

父组件

```jsx
// App.jsx
import React from 'react';
import Context from './Context';

class App extends React.Component {
  constructor() {
    super();
    this.state = {
      info: { home: 'Context', age: 18 }
    };
  }

  render() {
    const { info } = this.state;
    return (
      <div className="app">
        {/* 对象传值到子组件 */}
        <Context {...info}></Context>
      </div>
    );
  }
}

export default App;
```

子组件

```jsx
// Context.jsx
import React, { Component } from 'react';
import SonContext from './SonContext';

export class Context extends Component {
  render() {
    const { home, age } = this.props;
    return (
      <div>
        <h2>Home:{home}</h2>
        <h2>Age:{age}</h2>
        <SonContext {...this.props}></SonContext>
      </div>
    );
  }
}

export default Context;
```

孙组件

```jsx
// SonContext.jsx
import React, { Component } from 'react';

export class SonContext extends Component {
  render() {
    const { home } = this.props;
    return (
      <div>
        SonContext
        <h2>SonHome:{home}</h2>
      </div>
    );
  }
}

export default SonContext;
```

### 方式二：`Context`

在层级复杂的情况下,`Context`提供了一种在组件之间共享此类值的方式，不需要显式地逐层传递`props`。

> **Ⅰ**`React.createContext()`:
>
> ①：创建一个需要共享的`Context`对象
>
> ②：如果一个组件订阅了`Context`，那么这个组件会从离自身最近的匹配的`Provider`中读到当前的`Context`值；
>
> ③：`defaultValue`是组件在顶层查找过程中没找到对应的`Provider`，就使用默认值：`const MyContent=React.createContext(defaultValue)`

> **Ⅱ**`Context.Provider`
>
> ①：每个`Context`对象都会返回一个`Provider React`组件，它允许消费组件订阅`Context`的变化；
>
> ②：`Provider`接收一个`value`属性，传递给消费组件
>
> ③：一个`Provider`可以和多个消费组件有对应关系
>
> ④：多个`Provider`可以嵌套使用，里层的会覆盖外层的数据
>
> ⑤：当`Provider`的`value`值发生变化时，它内部的所有消费组件都会重新渲染

> **Ⅲ**`Class.contextType`
>
> ①：挂载在`class`上的`contextType`属性会被重新赋值为一个由`Class.contextType`创建的`Context`对象
>
> ②：可在任意生命周期中访问到，包括`render`函数

> **Ⅳ**`Context.Consumer`
>
> ①：可在函数式组件中完成订阅`Context`
>
> ②：函数接收当前的`Context`值，返回一个`React`节点
>
> ③：什么时候使用`Context.Consumer`？1.使用 value 的组件是一个函数式组件时；2.当组件中需要使用多个`Context`时

#### 类组件

**Step1**：创建 context

```jsx
// ThemeContext.jsx
import React from 'react';
// 创建一个context
const ThemeContext = React.createContext();

export default ThemeContext;
```

**类组件 Step2**:使用`Provider`

```jsx
// App.jsx
import React from 'react';
import Context from './Context';
import ThemeContext from './ThemeContext';
import UserContext from './UserContext';

class App extends React.Component {
  render() {
    return (
      <div className="app">
        <UserContext.Provider value={{ nickColor: 'blue' }}>
          <ThemeContext.Provider value={{ color: 'red', size: 30 }}>
            <Context></Context>
          </ThemeContext.Provider>
        </UserContext.Provider>
      </div>
    );
  }
}

export default App;
```

```jsx
// Context.jsx
import React, { Component } from 'react';
import SonContext from './SonContext';

export class Context extends Component {
  render() {
    return (
      <div>
        <SonContext></SonContext>
      </div>
    );
  }
}

export default Context;
```

**类组件 Step3**：设置组件的`contextType`后，可使用`context`数据，

如某组件在`Provider`包裹的组件外需要用`Provider`的数据，可通过设置默认值来实现：

`const MyContent=React.createContext(defaultValue)`

```jsx
// SonContext.jsx
import React, { Component } from 'react';
import ThemeContext from './ThemeContext';
import UserContext from './UserContext';

export class SonContext extends Component {
  render() {
    const { color } = this.context;
    return (
      <div>
        {/* 来自App组件的数据传递：{color} */}
        {/* 多个context时，如何使用？(使用Consumer共享数据) */}
        <UserContext.Consumer>
          {(value) => {
            return <h2>{value.nickColor}</h2>;
          }}
        </UserContext.Consumer>
      </div>
    );
  }
}

SonContext.contextType = ThemeContext;

export default SonContext;
```

#### 函数式组件

使用`Context`:使用`Consumer`

```jsx
// rcm
import React, { memo } from 'react';
import ThemeContext from './ThemeContext';

const SonBanner = memo(() => {
  return (
    <div>
      SonBanner
      <ThemeContext.Consumer>
        {(value) => {
          return <h2>ThemeColor:{value.color}</h2>;
        }}
      </ThemeContext.Consumer>
    </div>
  );
});

export default SonBanner;
```

## `setState`原理

### 为什么使用`setState`

> react 中没有像 vue 中使用`Proxy`和`Object.defineProperty`来监听数据变化，所以需要通过`setState`来告知 react 数据已发生变化。**`setState`方法是从`Component`中继承过来的。**

### `setState`的两种方式

```jsx
// 普通形式
// this.setState({
//   message: '你好'
// });

// 回调函数的优势：可在函数中增加逻辑，可将改变之前的state和prop传递进来
this.setState((state, props) => {
  return {
    message: '你好'
  };
});
```

### 异步调用

**`setState`在 react 的事件处理中是异步调用**

> 在调用`setState`后打印 state 的值，仍是之前的值。如果希望在数据更新之后进行逻辑操作，可在`setState`中传入第二个参数:`callback`

```jsx
this.setState(
  {
    message: '你好'
  },
  () => {
    console.log('updated');
  }
);
```

> ⏰
>
> `setState`设计为异步是为了显著地提高性能，如果每次调用`setState`都进行一次更新，那么`render`函数会被频繁调用，界面重新渲染，效率较低。最好的方式是获取到多个更新，并进行批量更新。
>
> 如果同步更新了`state`,但是还没有执行`render`函数，那么`state`和`props`不能保持同步。

```jsx
// 举例说明：如果用普通的setState方式,在一个方法中调用三次setState，则最终方法只调用最后一次setState方法:
this.setState({
  num: this.state.num + 2
});

// 如果使用回调函数的方式，如下示例，则所有的setState方法都会调用一遍。
this.setState((state) => {
  return {
    num: state.num + 2
  };
});
```

#### react18 之前

① 在组件生命周期或 react 合成事件中，`setState`是异步；

② 在`setTimeOut`或者原生 dom 事件或`promise`回调中，`setState`是同步。

如想要在调用`setState`后立即拿到数据更新后的 state，可使用`flushSync`

```jsx
import { flushSync } from 'react-dom';

flushSync(() => {
  this.setState({
    num: this.state.num + 2
  });
});
```

## 性能优化

### 前置知识

1️⃣ **react 的渲染流程**：jsx-->虚拟 dom-->真实 dom

---

2️⃣ **react 的更新流程**：`props`/`state`改变--> `render`函数重新执行-->产生新的 dom 树-->新旧 dom 树进行 diff-->计算出差异进行更新-->更新到真实的 dom

如果一棵树参照另外一棵树进行**完全比较更新**，该算法复杂程度为**O(n²)**，其中 n 是树中元素的数量。

> **react 对算法优化成了 O(n)**：
>
> ①：同层节点之间相互比较，不会跨节点比较；
>
> ②：不同类型的节点，产生不同的树结构；
>
> ③：可以通过`key`来指定哪些节点在不同的渲染下保持稳定。

> 遍历列表修改数据的几种情况：
>
> ①： 在最后位置插入数据：有无`key`意义不大
>
> ②：在前面插入数据：无`key`的情况下，所有数据子项都要修改；当有`key`时，react 用`key`去匹配原有树上的子元素以及最新树上的子元素。另外，`key`应该是唯一的，不能使用随机数，使用`index`作为`key`对性能没有优化。

---

3️⃣ **`render`函数调用**： 当 App 的 `render`函数被调用时，所有的子组件 `render`函数都会被重新调用，那么只要是修改了 app 中的数据，所有的组件都需要重新 render，进行 diff 算法，性能比较低。

### 优化一：`shouldComponentUpdate` (SCU)函数

该方法有两个参数

1.`nextProps`(修改后最新的`props`属性)

2.`nextState`(修改后最新的`state`属性)

返回值为布尔类型，返回值为`true`则需要调用 `render`函数，返回`false`不调用 `render`函数，默认返回值为`true` 。

```jsx
// 官网示例
class Rectangle extends Component {
  state = {
    isHovered: false
  };

  shouldComponentUpdate(nextProps, nextState) {
    if (
      nextProps.position.x === this.props.position.x &&
      nextProps.position.y === this.props.position.y &&
      nextProps.size.width === this.props.size.width &&
      nextProps.size.height === this.props.size.height &&
      nextState.isHovered === this.state.isHovered
    ) {
      // 没有任何改变，因此不需要重新渲染
      return false;
    }
    return true;
  }

  // ...
}
```

### 类组件优化：`PureComponent`（浅层比较）

```jsx
import React, { PureComponent } from 'react';

class App extends PureComponent {
  constructor() {
    super();
  }

  render() {
    return <div className="app"></div>;
  }
}

export default App;
```

`pureComponent` 源码

![](/images/react/pure.jpg)

- `class`继承自`PureComponent`,`pureComponent`在它的原型上添加了一个属性`isPureComponent`。
- 在源码中是`checkShouldComponentUpdate`方法来控制检查一个组件是否进行 render 更新：
  拿到组件实例并调用组件实例的`shouldComponentUpdate`方法，该方法有三个参数：`newProps`、`newState`、`nextContext`,当是纯函数时，进行`oldProps`和`newProps` 、`oldState`和`newState`的浅层比较。

### 函数式组件优化：`memo`

```jsx
import React, { memo } from 'react';

const SonBanner = memo((props) => {
  return <div>SonBanner</div>;
});

export default SonBanner;
```

## 受控组件/非受控组件

### 受控组件

表单：表单数据是由 react 组件管理

表单的`onChange`事件：将多个表单放到一个函数里处理

```jsx
inputChange(e) {
    this.setState({
        [e.target.name]:e.target.value
    })
}
```

多选的`onChange`事件：

```jsx
inputChange(e) {
    const optiions = Array.from(e.target.selectedOptions)
    const values = options.map(item=>item.value)
    this.setState({frult:values})
}

// Array.from 有两个参数，第二个参数是mapFn，所以以上代码可并成一行为：
// const values = Array.from(e.target.selectedOptions,item=>item.value)
```

### 非受控组件

表单：表单数据由 dom 节点处理

- 使用`ref`

- 在非受控组件重通常使用`defaultValue`来设置默认值
- `<input type="checkbox">`和`<input type="radio">`支持`defaultChecked`
- `<select>`和`<textarea>`支持`defaultValue`

## 高阶函数和高阶组件 ⭐️

### 高阶函数概念

至少满足以下条件之一：① 接受一个或多个函数作为输入；② 输出一个函数

常见的`filter`、`map`、`reduce`都是高阶函数

### 高阶组件（HOC）概念

参数为组件，返回值为新组件的函数

### 定义高阶组件

```jsx
import React, { PureComponent } from 'react';

// 定义高阶组件
function hoc(component) {
  // 第1种:定义类组件
  class NewCpn extends PureComponent {
    render() {
      return (
        <div>
          <h1> 高阶组件中的render</h1>
          <component />
        </div>
      );
    }
  }
  // 2.定义函数组件
  //   function NewCpn2(props) {}
  //   return NewCpn2;

  // 修改组件的名称
  NewCpn.displayName = 'NewName';
  return NewCpn;
}

class HelloWorld extends PureComponent {
  render() {
    return <h1>hello</h1>;
  }
}

const HelloWorldHOC = hoc(HelloWorld);
export class App extends PureComponent {
  render() {
    return (
      <div>
        <h1>App组件</h1>
        <HelloWorldHOC />
      </div>
    );
  }
}

export default App;
```

### 高阶组件应用 💬

#### 第三方库中使用

①`redux`的`connect`：

`export default connet(fn1,fn2)(Home)`作用：将`redux`中的数据插入到`Home`中的`props`里；

②`react-router`中的`withRouter`

#### 通过定义高阶组件给一些需要特殊数据的组件,注入 props

案例 1：

```jsx
import React, { PureComponent } from 'react';

// 通过定义高阶组件,给一些需要特殊数据的组件,注入props
function enhanceUser(OriginComponent) {
  class NewConponent extends PureComponent {
    constructor() {
      super();
      this.state = {
        userInfo: {
          name: 'user',
          age: 20
        }
      };
    }

    render() {
      return <OriginComponent {...this.state.userInfo} />;
    }
  }
  return NewConponent;
}

const Home = enhanceUser((props) => <h1>Home:{props.name}</h1>);

export class App extends PureComponent {
  render() {
    return (
      <div>
        <Home></Home>
      </div>
    );
  }
}

export default App;
```

案例 2——在案例 1 基础上增强`props`传值

```jsx
// EnhanceUser.jsx

import React, { PureComponent } from 'react';

function enhanceUser(OriginComponent) {
  class NewConponent extends PureComponent {
    constructor(props) {
      super(props);
      this.state = {
        userInfo: {
          name: 'user',
          age: 20
        }
      };
    }

    render() {
      return <OriginComponent {...this.props} {...this.state.userInfo} />;
    }
  }
  return NewConponent;
}

export default enhanceUser;
```

```jsx
// App.jsx

import React, { PureComponent } from 'react';
import enhanceUser from './EnhanceUser';

const Home = enhanceUser((props) => {
  return (
    <div>
      <h1>Home:{props.name}</h1>
      {props.propsData.map((item) => (
        <h2>{item}</h2>
      ))}
    </div>
  );
});

export class App extends PureComponent {
  render() {
    return (
      <div>
        <Home propsData={['data1', 'data2']}></Home>
      </div>
    );
  }
}

export default App;
```

案例 3——高阶组件的实际应用场景

```jsx
// App.jsx

import React, { PureComponent } from 'react';
import ThemeContext from './context/themeContext';
import Product from './product';

export class App extends PureComponent {
  render() {
    return (
      <div>
        <ThemeContext.Provider value={{ color: 'red', size: 30 }}>
          <Product></Product>
        </ThemeContext.Provider>
      </div>
    );
  }
}

export default App;
```

```jsx
// themeContext.jsx
import { createContext } from 'react';

const ThemeContext = createContext();

export default ThemeContext;
```

```jsx
// withTheme.jsx -- 高阶组件
import ThemeContext from '../context/themeContext';

function withTheme(OriginComponent) {
  return (props) => {
    return (
      <ThemeContext.Consumer>
        {(value) => {
          {
            /* 注入themeContext的value */
          }
          return <OriginComponent {...value} {...props}></OriginComponent>;
        }}
      </ThemeContext.Consumer>
    );
  };
}

export default withTheme;
```

```jsx
// product.jsx 子组件
import React, { PureComponent } from 'react';
import withTheme from './HOC/withTheme';
export class product extends PureComponent {
  render() {
    const { color } = this.props;
    return <div>product中的color:{color}</div>;
  }
}

export default withTheme(product);
```

强制更新 api(不推荐使用)：`this.forceUpdate()`

## `Portals`的使用

如何实现渲染的内容独立于父组件，甚至是独立于当前挂载到的 dom 元素中？

（默认是挂载到 id 为 root 的 dom 元素上）

第一个参数是任何可渲染的 react 子元素，第二个参数是一个 dom 元素：`ReactDOM.createPortal(child,container)`

```jsx
// App.js
import React, { PureComponent } from 'react';
import { createPortal } from 'react-dom';

export class App extends PureComponent {
  render() {
    return (
      <div className="app">
        <h1>挂载到id为root的dom元素</h1>
        {createPortal(
          <h2>挂载到wrapper的元素上</h2>,
          document.querySelector('#wrapper')
        )}
      </div>
    );
  }
}

export default App;
```

应用实例：

index.html

```html
<div id="root"></div>
<div id="detail"></div>
```

App.js

```jsx
import React, { PureComponent } from 'react';
import Detail from './Detail';

export class App extends PureComponent {
  render() {
    return (
      <div>
        <Detail>
          <h2>标题</h2>
          <h2>内容</h2>
        </Detail>
      </div>
    );
  }
}

export default App;
```

Detail.jsx

```jsx
import React, { PureComponent } from 'react';
import { createPortal } from 'react-dom';

export class Detail extends PureComponent {
  render() {
    return createPortal(this.props.children, document.querySelector('#detail'));
  }
}

export default Detail;
```

## 通过`ref`获取原生 dom

### 获取 dom 的三种方式

```jsx
import React, { createRef, PureComponent } from 'react';

export class App extends PureComponent {
  constructor() {
    super();
    this.titleCreateRef = createRef();
    this.titleEl = null;
  }
  getNativeDom() {
    // 方式一：不推荐使用
    console.log(this.refs.titleRef);
    // 方式二（常用）：提前创建ref对象，createRef(),将创建出来的对象绑定到元素
    console.log(this.titleCreateRef.current);
    // 方式三：传入一个回调函数，在对应的元素被渲染之后，回调函数被执行，并将元素传入
    console.log(this.titleEl);
  }
  render() {
    return (
      <div>
        <h2 ref="titleRef">ref获取原生dom方式一</h2>
        <h2 ref="titleCreateRef">ref获取原生dom方式二</h2>
        <h2 ref={(el) => (this.titleEl = el)}>ref获取原生dom方式三</h2>
        <button onClick={(e) => this.getNativeDom()}></button>
      </div>
    );
  }
}

export default App;
```

### 获取组件实例的方式

**类组件**使用`createRef`；**函数式组件**使用`forwardRef`

```jsx
import React, { createRef, forwardRef, PureComponent } from 'react';

export class HelloWorld extends PureComponent {
  render() {
    return <h1>类组件</h1>;
  }
}

const FuncComponent = forwardRef(function (props, ref) {
  return <h2 ref={ref}>函数式组件</h2>;
});

export class App extends PureComponent {
  constructor() {
    super();
    this.hwRef = createRef();
    this.funcRef = createRef();
  }

  getComponent() {
    console.log(this.hwRef.current);
    console.log(this.funcRef.current);
  }

  render() {
    return (
      <div>
        {/*类组件*/}
        <HelloWorld ref={this.hwRef}></HelloWorld>
        {/*函数式组件*/}
        <FuncComponent ref={this.funcRef}></FuncComponent>
        <button onClick={(e) => this.getComponent()}> 获取组件实例</button>
      </div>
    );
  }
}

export default App;
```

## fragment

使用`fragment`，可替代根标签的`div`，类似于 vue 的`template`，不会被渲染成 dom 元素

注意，如果需要绑定属性则不能写语法糖，只能写`<Fragment></Fragment>`

```jsx
import React, { PureComponent, Fragment } from 'react';

export class App extends PureComponent {
  render() {
    return (
      <Fragment>
        <h1>标题</h1>
        <h2>内容</h2>
      </Fragment>
    );
  }
}

export default App;
```

语法糖:

```jsx
import React, { PureComponent } from 'react';

export class App extends PureComponent {
  render() {
    return (
      <>
        <h1>标题</h1>
        <h2>内容</h2>
      </>
    );
  }
}

export default App;
```

## StrictMode

### 理解严格模式

① 严格模式检查仅在开发模式下运行，不影响生产构建；

② 可以为应用程序的任何部分启用严格模式：不会对`Header`和`Footer`组件运行严格模式检查；

### 开启严格模式

整个应用：

```jsx
// index.js
const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

部分组件：

```jsx
// App.js
  render() {
    return (
      <>
        <React.StrictMode>
          <Detail></Detail>
        </React.StrictMode>
      </>
    );
  }
```

### 严格模式检查内容

- 识别不安全的声明周期
- 使用过时的 API
  - `ref` API
  - `findDOMNode` API:如组件已被挂载到 dom 上，该方法会返回浏览器中相应的原生 dom 元素
  - `context` API :早期的`Context`是通过`static`属性声明`Context`对象属性，通过`getChildContext`返回`Context`对象等方式来使用`Context`的
- 检测意外副作用：
  - 组件的`constructor`会被调用两次，是严格模式下故意进行的操作，用来查看被调用多次时，是否会产生一些副作用
  - 在生产环境中是不会被调用两次的

## 过渡动画

### `react-transition-group`库

- 可实现组件的入场和立场动画，使用时需要进行额外安装:

  `npm install react-transition-group --save `

- 主要包含四个组件：

  - `Transition`:该组件和平台无关
  - `CSSTransition`：用来完成过渡动画效果
    - 执行过程中，有三个状态`appear`、`enter`、`exit`
    - 开始状态：对应的类是`-appear`、`-enter`、`exit`
    - 执行动画：对应的类是`-appear-active`、``-enter-active`、`-exit-active`
    - 执行结束：对应的类是`-appear-done`、``-enter-done`、`-exit-done`
  - `SwitchTransition`：两个组件显示和隐藏切换时，使用该组件
  - `TransitionGroup`：将多个动画组件包裹在其中，一般用于列表中元素的动画

#### `CSSTransition `实例：

**常用属性：**

- `unmountOnExit`(必须):值为 true 时，该组件会在执行退出动画结束后被移除掉
- `timeout`(必须):过渡动画的时长，
- `in`(必须)：布尔值：
  - ①true 触发进入状态，会添加-enter、-enter-active 的 class 开始执行动画，当动画执行结束会移除两个 class，并且添加-enter-done 的 class
  - ②false 触发退出状态，会添加-exit、-exit-active 的 class 开始执行动画，当动画执行结束后，会移除两个 class，并且添加-enter-done 的 class
- `classNames`(必须):样式类名
- `appear`(必须):是否在初次进入添加动画（需要和 in 同时为 true）

**钩子函数：**

- `onEnter`：进入动画之前触发
- `onEntering`:在应用进入动画时被触发
- `onEntered`：在应用进入动画结束后被触发
- `onExit`：开始离开动画
- `onExiting`:执行离开动画
- `onExited`：执行离开结束

```jsx
// App.js
import React, { PureComponent } from 'react';
import { CSSTransition } from 'react-transition-group';
import './title.css';

export class App extends PureComponent {
  constructor() {
    super();
    this.state = {
      isShowTitle: false
    };
  }
  render() {
    const { isShowTitle } = this.state;
    return (
      <div>
        <button onClick={(e) => this.setState({ isShowTitle: !isShowTitle })}>
          切换
        </button>
        {/* 必须声明的属性-- 

        */}
        <CSSTransition
          in={isShowTitle}
          unmountOnExit={true}
          classNames="title"
          timeout={2000}
        >
          <h2>hahh </h2>
        </CSSTransition>
      </div>
    );
  }
}

export default App;
```

```css
/* title.css */
/* 第一次动画 */
.title-appear {
  transform: translateX(-150px);
}

.title-appear-active {
  transform: translateX(0);
  transition: transform 2s ease;
}

/* 进入动画 */
.title-enter {
  opacity: 0;
}

.title-enter-active {
  opacity: 1;
  transition: opacity 2s ease;
}

/* 离开动画 */
.title-exit {
  opacity: 1;
}
.title-exit-active {
  opacity: 0;
  transition: opacity 2s ease;
}
```

#### `SwitchTransition`实例：

**常用属性：**

- `mode`:
  - `in-out`：表示新组件先进入，旧组件再移除；
  - `out-in`：表示旧组件先移除，新组件再进入

如何使用：

- `SwitchTransition`组件里面要有`CSSTranstiion`或`Transition`组件，不能直接包裹需要切换的组件
- `SwitchTransition`里面的`CSSTranstiion`或`Transition`组件不再接受`in`属性来判断状态，而是用`key`属性

```jsx
// App.jsx
import React, { PureComponent } from 'react';
import { SwitchTransition, CSSTransition } from 'react-transition-group';
import './login.css';

export class App extends PureComponent {
  constructor() {
    super();
    this.state = {
      isLogin: true
    };
  }
  render() {
    const { isLogin } = this.state;
    return (
      <div>
        <SwitchTransition mode="out-in">
          <CSSTransition
            key={isLogin ? 'exit' : 'login'}
            classNames="login"
            timeout={1000}
          >
            <button onClick={() => this.setState({ isLogin: !isLogin })}>
              {' '}
              {isLogin ? '注销' : '登录'}
            </button>
          </CSSTransition>
        </SwitchTransition>
      </div>
    );
  }
}

export default App;
```

```css
/* login.css */
.login-enter {
  transform: translateX(100px);
  opacity: 0;
}

.login-enter-active {
  transform: translateX(0);
  opacity: 1;
  transition: all 1s ease;
}

.login-exit {
  transform: translateX(0);
  opacity: 1;
}

.login-exit-active {
  transform: translateX(-100px);
  opacity: 0;
}
```

#### `TransitionGroup`实例：

```jsx
// App.jsx

import React, { PureComponent } from 'react';
import { TransitionGroup, CSSTransition } from 'react-transition-group';
import './book.css';

export class App extends PureComponent {
  constructor() {
    super();
    this.state = {
      books: [
        { name: 'name11', print: '22' },
        { name: 'name22', print: '33' }
      ]
    };
  }

  addBook() {
    const newBook = [...this.state.books];
    newBook.push({ name: 'name333', print: '44' });
    this.setState({
      books: newBook
    });
  }

  delBook(index) {
    const delBook = [...this.state.books];
    delBook.splice(index, 1);
    this.setState({
      books: delBook
    });
  }
  render() {
    const { books } = this.state;
    return (
      <div>
        <h2>书籍列表</h2>
        <TransitionGroup component="ul">
          {books.map((item, index) => {
            return (
              <CSSTransition key={index} classNames="book" timeout={1000}>
                <li>
                  <span>{item.print}</span>
                  <button onClick={() => this.delBook(index)}>删除</button>
                </li>
              </CSSTransition>
            );
          })}
        </TransitionGroup>
        <button onClick={() => this.addBook()}>新增</button>
      </div>
    );
  }
}

export default App;
```

```css
/* book.css */
.book-enter {
  transform: translateX(100px);
  opacity: 0;
}

.book-enter-active {
  transform: translateX(0);
  opacity: 1;
  transition: all 1s ease;
}

.book-exit {
  transform: translateX(0);
  opacity: 1;
  transition: all 1s ease;
}

.book-exit-active {
  transform: translateX(-100px);
  opacity: 0;
}
```

## react 中的 css

### 组件化中的 css 解决方案要求

- 可以编写局部 css，css 具备自己的作用域，不会随意污染其他组件内的元素

- 可以编写动态的 css，可以获取当前组件的一些状态，根据状态的变化生成不同的 css 样式

- 支持所有的 css 特性：伪类、动画、媒体查询等

### css 解决方案

- **内联样式**：可使用 state 中的状态来设置相关的样式

  ```jsx
  import React, { PureComponent } from 'react';

  export class App extends PureComponent {
    constructor() {
      super();
      this.state = {
        titleSize: 20
      };
    }
    render() {
      const { titleSize } = this.state;
      return (
        <div>
          {/* 方案一：内联样式 */}
          <h1 style={{ color: 'red', fontSize: `${titleSize}px` }}>title</h1>
        </div>
      );
    }
  }

  export default App;
  ```

- **普通 css 方案**：编写单独文件，进行引入。普通 css 都属于全局的 css，样式之间会相互影响

- **css modules**：

  - 使用了类似于 webpack 配置的环境下都可以使用；如果在其他项目使用，需要自行配置如：webpack.config.js 中的`modules:true`

  - 实现方案：

    - .css/.less/.scss 等样式文件都需要修改成.module.css/.module.less/.module.scss 等

    - ```jsx
      import React, { PureComponent } from 'react';
      import appStyle from './App.module.css';

      export class App extends PureComponent {
        render() {
          return (
            <div>
              <h1 className={appStyle.title}>title</h1>
            </div>
          );
        }
      }

      export default App;
      ```

  - 实现原理：动态生成 class 类名---- `class="App_title__nX3w1" ` 文件名+文件中的样式类名+动态哈希值。

  - 缺陷：

    ① 不能使用连接符（.app-title）

    ② 所有的 className 必须使用`{style.className}`形式编写

    ③ 不方便动态修改样式，仍然需要使用内联样式的方式

- **css in js**

  - 安装：`npm install --save styled-components`

  - 知识补充：

    ```js
    // 标签模板字符串

    const name = 'tayce';

    function foo(...args) {
      console.log(args);
    }

    foo`test ${name}`; // [Array(2), 'tayce']
    ```

  - 实际使用

    ```js
    // Style.js
    // 生成div标签,针对AppWrapper组件内的子元素使用样式
    // 样式间不会产生冲突
    // 可使用嵌套语法
    // 可针对子组件进行细分
    // 可接收外部传入的props
    // 可通过attrs设置默认值
    // 可从单独文件中引入变量;
    // 可设置全局样式
    // 可继承

    import styled from 'styled-components';

    // 继承
    export const radiusButton = styled.button`
      border-radius: 5px;
    `;

    export const Button = styled(radiusButton)``;

    export const AppWrapper = styled.div`
      .title {
        color: red;
        &:hover {
          color: blue;
        }
      }
    `;

    export const SectionWrapper = styled.div.attrs((props) => {
      return {
        // 设置默认值
        fontWeight: '700',
        textColor: props.color || 'pink'
      };
    })`
      .section-title {
        color: ${(props) => props.textColor};
        font-size: ${(props) => props.size}px;
        background-color: ${(props) => props.bgc};
        border: ${(props) => props.theme.border};
      }
    `;
    ```

    ```js
    // index.js 设置全局样式

    import React from 'react';
    import ReactDOM from 'react-dom/client';
    import App from './App';
    import { ThemeProvider } from 'styled-components';

    const root = ReactDOM.createRoot(document.getElementById('root'));

    root.render(
      <React.StrictMode>
        <ThemeProvider theme={{ border: '1px solid red' }}>
          <App />
        </ThemeProvider>
      </React.StrictMode>
    );
    ```

    ```jsx
    // App.jsx

    import React, { PureComponent } from 'react';
    import { AppWrapper, SectionWrapper } from './Style.js';
    import * as vars from './color.js';

    export class App extends PureComponent {
      constructor() {
        super();
        this.state = {
          size: 30
        };
      }
      render() {
        const { size } = this.state;
        return (
          <AppWrapper>
            <h2 className="title">title</h2>
            <SectionWrapper size={size} bgc={vars.bgc}>
              <h2 className="section-title">title</h2>
              {/*可修改css变量值；传入动态css变量值*/}
              <button onClick={() => this.setState({ size: 12 })}>
                标题变小
              </button>
            </SectionWrapper>
          </AppWrapper>
        );
      }
    }

    export default App;
    ```

    ```jsx
    // color.js 可设置css变量导入到jsx文件中使用

    export const fontColor = 'yellow';
    export const bgc = '#cbc4dd';
    ```

## redux

### 初步使用 redux（无 react-redux）

```jsx
// index.js

const { createStore } = require('redux');
const reducer = require('./reducer');

// 创建store
const store = createStore(reducer);

module.exports = store;
```

```js
// reducer.js
const { CHANGE_NAME } = require('./constant');

// 初始化的数据
const initialState = {
  name: 'test'
};

// 定义reducer函数:纯函数,接收两个参数:
// 参数1:store中目前保存到的state;参数2:本次需要更新的action(dispatch传入的action)
// 返回值:会作为store之后存储的state
function reducer(state = initialState, action) {
  // 有新数据进行更新时,返回新的state;没有新数据更新,就返回之前的state
  if (action.type === CHANGE_NAME) {
    return { ...state, name: action.name };
  }
  return state;
}

module.exports = {
  reducer
};
```

```js
// actionCreator.js
const { CHANGE_NAME } = require('./constant');
// 独立文件用于创建action
const changeNameAction = (name) => ({
  type: CHANGE_NAME,
  name
});

module.exports = {
  changeNameAction
};
```

```js
// constant.js
const CHANGE_NAME = 'changeName';

module.exports = {
  CHANGE_NAME
};
```

```jsx
// 使用修改store数据.js
const store = require('./store/index');
const { changeNameAction } = require('./store/actionCreator');

// subscribe订阅数据变化
const unsubscribe = store.subscribe(() => {
  console.log('订阅数据变化', store.getState());
});

// 修改store中的数据
store.dispatch(changeNameAction('change111'));

console.log(store.getState()); // { name: 'changeName' }

// 取消订阅
unsubscribe();

store.dispatch(changeNameAction('change222'));
```

### redux 代码优化总结

- 将派发的 action 生成过程放到一个 actionCreator 函数中
- 将定义的所有 actionCreators 的函数，放到一个独立文件中： actionCreator.js
- actionCreator 和 reducer 函数中使用字符串常量是一致的，所以将常量抽取到一个独立 constants 的文件中
- 将 reducer 和默认值（initialState）放到一个独立的 reducer.js 文件中，而不是在 index.js

### redux 的三大原则

- **单一数据源**

  - 整个应用程序的 state 被存储在一个 object tree 中，并且这个 object tree 只存储在一个 store 中
  - 单一数据源可以让整个应用程序的 state 变得方便维护、追踪和修改

- **state 只读**

  - 唯一修改 state 的方法是触发 action，不能通过其他方式修改 state
  - 这样可以保证所有的修改都被集中化处理，并且按照严格顺序执行，所以不用担心 race condition 的问题

- **使用纯函数来执行修改**
  - 通过 reducer 将旧 state 和 action 联系在一起，并返回一个新的 state
  - 可以将 reducer 拆分成多个小的 reducers，分别操作不同 state tree 的一部分
  - 所有的 reducer 都必须是纯函数，不能产生副作用

![](/images/react/原则.jpg)

### redux 数据共享（使用 react-redux）

① 安装库：`npm install react-redux`

② 使用 Provider：

```js
// index.js
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { Provider } from 'react-redux';
import store from './store/index.js';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <Provider store={store}>
      <App />
    </Provider>
  </React.StrictMode>
);
```

③ 创建 store 文件夹

- store/index.js

  ```jsx
  import { createStore } from 'redux';
  import reducer from './reducer';

  const store = createStore(reducer);

  export default store;
  ```

- store/reducer.js--定义初始化 state 数据；定义 reducer 函数

  ```js
  import * as actionTypes from './constant';

  const initialState = {
    banners: []
  };

  function reducer(state = initialState, action) {
    switch (action.type) {
      case actionTypes.CHANGE_BANNERS:
        return { ...state, banners: action.banners };
      default:
        return state;
    }
  }

  export default reducer;
  ```

- store/constant.js--定义 reducer 文件中使用的常量

  ```js
  export const CHANGE_BANNERS = 'change_banners';
  ```

- store/actionCreator.js--创建 action

  ```js
  import * as actionTypes from './constant';
  export const changeBannersAction = (banners) => ({
    type: actionTypes.CHANGE_BANNERS,
    banners
  });
  ```

④ 组件使用 connect

举例：在 cate 中获取存储数据(`mapDispatch`)，在 about 组件中使用(`mapStateToProps`)

- connect()返回值是一个高阶组件，有两个参数
  - 参数 1：`mapStateToProps`--将 redux 中的**state 数据**映射到当前组件
  - 参数 2：`mapDispatch` --将 redux 中的**dispach 函数**映射到当前组件
  - 可以通过`props`直接调用

```jsx
// cate.jsx
import React, { PureComponent } from 'react';
import axios from 'axios';
import { connect } from 'react-redux';
import { changeBannersAction } from '../store/actionCreator';
export class cate extends PureComponent {
  componentDidMount() {
    axios.get('http://123.207.32.32:8000/home/multidata').then((res) => {
      const banners = res.data.data.banner.list;
      this.props.changeBanners(banners);
    });
  }

  render() {
    return <div className="cate">cate</div>;
  }
}

const mapDispatch = (dispatch) => ({
  changeBanners: (banners) => {
    dispatch(changeBannersAction(banners));
  }
});

// 执行connect函数，返回高阶组件再传参执行函数
export default connect(null, mapDispatch)(cate);
```

```jsx
// about.jsx

import React, { PureComponent } from 'react';
import { connect } from 'react-redux';

export class About extends PureComponent {
  render() {
    const { banners } = this.props;
    return (
      <div className="about">
        <h2> About Data:</h2>
        {banners.map((item, index) => (
          <li key={index}>{item.title}</li>
        ))}
      </div>
    );
  }
}

const mapStateToProps = (state) => ({
  banners: state.banners
});

export default connect(mapStateToProps, mapDispatch)(About);
```

redux 异步操作流程：

![](/images/react/redux异步.jpg)

注意：在开发中，在子组件`componentDidMount`进行网络请求并不合适，应将网络请求统一在一个文件中处理，子组件进行调用。

## redux-thunk 中间件

如果是普通的 action，则需要返回 action 对象，但对象是不能直接拿到服务器请求的异步数据的 。

正常情况下`dispatch`派发为对象：`store.dispatch(obj) `,如果想派发函数，就需要用到**redux-thunk**

`Middleware`(中间件): 中间件的目的是在 dispatch 的 action 和最终到达的 reducer 之间，扩展一些自己的代码，比如日志记录、调用异步接口、添加代码调试功能等。

① 安装：`npm install redux-thunk`

② 导入，使用 redux-thunk

```jsx
// store/index.js

import { applyMiddleware, createStore } from 'redux';
import thunk from 'redux-thunk';
import reducer from './reducer';

// 通过中间件增强
const store = createStore(reducer, applyMiddleware(thunk));

export default store;
```

③ 由派发对象改为派发函数

```jsx
// cate.jsx

import { fetchHomeMutilDataAction } from '../store/actionCreator';

componentDidMount() {
    this.props.fetchHomeMutilData();
  }

const mapDispatchToProps = (dispatch) => ({
  fetchHomeMutilData() {
    dispatch(fetchHomeMutilDataAction());
  }
});
```

④ 进行异步接口调用处理，进行派发

```js
// actionCreator.js

export const fetchHomeMutilDataAction = () => {
  //  有两个参数：
  // dispatch 用于之后再次派发action
  // getState 想获取store的变量，可通过getState().banners
  function getBannersData(dispatch, getState) {
    axios.get('http://123.207.32.32:8000/home/multidata').then((res) => {
      const banners = res.data.data.banner.list;
      dispatch(changeBannersAction(banners));
    });
  }

  return getBannersData;
};
```

#### 日志打印

```jsx
// store/index.js

// 对每次派发的action进行拦截，进行日志打印
function log(store) {
  const next = store.dispatch;
  function logAndDispatch(action) {
    console.log('派发前', action);
    //  真正派发的代码：使用之前的dispatch进行派发
    next(action);
    console.log('派发后', action);
  }
  // monkey patch 篡改现有的代码，对整体的执行逻辑进行修改
  store.dispatch = logAndDispatch;
}

log(store);
```

#### 手写中间件

```jsx
function thunk() {
  const next = store.dispatch;
  function dispatchThunk(action) {
    if (typeof action === 'function') {
      // 传入新的dispatch
      action(store.dispatch, store.getState);
    } else {
      next(action);
    }
  }
  store.dispatch = dispatchThunk;
}

thunk(store);
```

## combineReducers 函数

该函数可用来对多个`reducer`合并

```jsx
const reducer = combineReducers({
  counterInfo: counterReducer,
  homeInfo: homeReducer
});

export default reducer;
```

### 实现原理

- 将传入的`reducers`合并到一个对象中，最终返回一个`combination`的函数
- 在执行`combination`的函数的过程中，通过判断前后返回的数据是否相同来决定返回之前的 state 还是新的 state
- 新的 state 会触发订阅者发生新的刷新，而旧的 state 可以有效的组织订阅者发生刷新

## redux toolkit

### 核心 api

![](/images/react/核心api.jpg)

#### ① `createSlice`

![](/images/react/createSlice.jpg)

#### ② configureStore

![](/images/react/configureStore.jpg)

#### 使用流程：

① 安装： `npm install @reduxjs/toolkit react-redux`

② 创建`slice`，定义的`addNumber`和`subNumber`可以通过`counterSlice.actions`拿到

```jsx
// store/features/counter.js
import { createSlice } from '@reduxjs/toolkit';

const counterSlice = createSlice({
  name: 'counter',
  initialState: {
    counter: 222
  },
  reducers: {
    addNumber(state, { payload }) {
      state.counter = state.counter + payload;
    },
    subNumber(state, { payload }) {
      state.counter = state.counter - payload;
    }
  }
});

export const { addNumber, subNumber } = counterSlice.actions;
export default counterSlice.reducer;
```

③ 创建 store 对象，使用`configureStore`

```js
// store/index.js

import { configureStore } from '@reduxjs/toolkit';
import counterReducer from './features/counter';

const store = configureStore({
  reducer: {
    counter: counterReducer
  }
});

export default store;
```

④ 使用 redux 的`provider`

```js
// index.js

import { Provider } from 'react-redux';
import store from './store';

<Provider store={store}>
  <App />
</Provider>;
```

⑤ 使用 redux 的`connect`,使用数据

```jsx
// App.jsx
import React, { PureComponent } from 'react';
import { connect } from 'react-redux';
import Home from './pages/Home';
import Profile from './pages/Profile';
import './style.css';

export class App extends PureComponent {
  render() {
    const { counter } = this.props;
    return (
      <div>
        <h2>App counter:{counter}</h2>
        <div className="pages">
          <Home></Home>
          <Profile></Profile>
        </div>
      </div>
    );
  }
}

const mapStateToProps = (state) => ({
  counter: state.counter.counter
});

export default connect(mapStateToProps)(App);
```

⑥ 组件使用 redux 的数据

```jsx
// Home.jsx

import React, { PureComponent } from 'react';
import { connect } from 'react-redux';
import { addNumber } from '../store/features/counter';

export class Home extends PureComponent {
  addNumber(num) {
    this.props.addNumber(num);
  }
  render() {
    const { counter } = this.props;
    return (
      <div className="home">
        <h2>Home counter:{counter}</h2>
        <button onClick={() => this.addNumber(5)}>count :+5</button>
      </div>
    );
  }
}

const mapStateToProps = (state) => ({
  counter: state.counter.counter
});

const mapDispatchToProps = (dispatch) => ({
  addNumber(num) {
    dispatch(addNumber(num));
  }
});

export default connect(mapStateToProps, mapDispatchToProps)(Home);
```

⑦ **获取异步数据**

```jsx
// Home.jsx

import { fetchHomeBannersDataAction } from '../store/features/home';
  componentDidMount() {
    this.props.fetchHomeBannersData();
  }

const mapDispatchToProps = (dispatch) => ({
  fetchHomeBannersData() {
    dispatch(fetchHomeBannersDataAction());
  }
});
```

```js
// home.js

import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';
import axios from 'axios';

export const fetchHomeBannersDataAction = createAsyncThunk(
  'fetchHomeBannersData',
  async () => {
    const res = await axios.get('http://123.207.32.32:8000/home/multidata');
    return res.data;
  }
);

const homeSlice = createSlice({
  name: 'counter',
  initialState: {
    banners: []
  },
  reducers: {},
  extraReducers: {
    [fetchHomeBannersDataAction.fulfilled](state, { payload }) {
      state.banners = payload.data.banner.list;
    }
  }

  // 第二种写法
  //   extraReducers: (builder) => {
  //     builder.addCase(
  //       fetchHomeBannersDataAction.fulfilled,
  //       (state, action) => {}
  //     );
  //   }
});

export const { getBanners } = homeSlice.actions;
export default homeSlice.reducer;
```

- `extraReducers`:可以在`extraReducers`中监听`createAsyncThunk`创建的 action 被 dispatch 时的三种状态
- 有三种状态：`pending`、`fulfilled`、`rejected`
- 第二种写法：` extraReducers`可以传入一个函数，函数接收一个 builder 参数

**第三种写法：使用 dispatch**

```jsx
// home.js

export const fetchHomeBannersDataAction = createAsyncThunk(
  'fetchHomeBannersData',
  async (extraInfo, store) => {
    const res = await axios.get('http://123.207.32.32:8000/home/multidata');
    const banners = res.data.data.banner.list;
    store.dispatch(getBanners(banners));
  }
);
```

#### 数据不可变性

![](/images/react/数据不可变.jpg)

#### 自定义 connect 函数

HOC/connect.js

```js
import { PureComponent } from 'react';
import { StoreContext } from './StoreContext';

export function connect(mapStateToProps, mapDispatchToProps) {
  return function (WrapperComponent) {
    class NewComponent extends PureComponent {
      constructor(props, context) {
        super(props);
        this.state = mapStateToProps(context.getState());
      }

      componentDidMount() {
        this.unsubscribe = this.context.subscribe(() => {
          this.setState(mapStateToProps(this.context.getState()));
        });
      }
      componentWillUnmount() {
        this.unsubscribe();
      }
      render() {
        const stateObj = mapStateToProps(this.context.getState());
        const dispatchObj = mapDispatchToProps(this.context.dispatch);
        return (
          <WrapperComponent
            {...this.props}
            {...stateObj}
            {...dispatchObj}
          ></WrapperComponent>
        );
      }
    }

    NewComponent.contextType = StoreContext;
    return NewComponent;
  };
}
```

HOC/StoreContext.js

```js
import { createContext } from 'react';

export const StoreContext = createContext();
```

HOC/index.js

```js
export { StoreContext } from './StoreContext';
export { connect } from './connect';
```

pages/About.jsx

```jsx
import React, { PureComponent } from 'react';
import { connect } from '../HOC/connect';
import { addNumber } from '../store/features/counter';

export class About extends PureComponent {
  render() {
    const { counter } = this.props;
    return (
      <div className="about">
        <h2>About:{counter}</h2>
      </div>
    );
  }
}

const mapStateToProps = (state) => ({
  counter: state.counter.counter
});

const mapDispatchToProps = (dispatch) => ({
  addNumber(num) {
    dispatch(addNumber(num));
  }
});
export default connect(mapStateToProps, mapDispatchToProps)(About);
```

index.js

```js
import { StoreContext } from './HOC';

<Provider store={store}>
  <StoreContext.Provider value={store}>
    <App />
  </StoreContext.Provider>
</Provider>;
```

## 状态管理总结

### 三种状态管理方案

- 1.组件中自己的 state 管理
- 2.`context`数据的共享状态
- 3.redux 管理应用状态

### state 管理方案推荐

- ui 相关的组件内部可以维护的状态，在组件内部自己来维护
- 大部分需要共享的状态，交给 redux 管理和维护
- 从服务器请求的数据（包括请求的操作），交给 redux 维护

## react router

### 后端路由

![](/images/react/后端路由.jpg)

### 前端路由

![](/images/react/前端路由.jpg)

### react router 使用

#### 1.安装：

`npm install react-router-dom`

#### 2.api:

- `BrowserRouter`:使用**history**模式
- `HashRouter`:使用**hash**模式

router 中包含了对路径改变的监听，并将响应的路径传递给子组件

#### 3.引入 api（以 hash 路由为例）

```jsx
import React, { PureComponent } from 'react';
import { HashRouter } from 'react-router-dom';

export class App extends PureComponent {
  render() {
    return (
      <div>
        <HashRouter>
          <App />
        </HashRouter>
      </div>
    );
  }
}

export default App;
```

#### 4.路由映射配置

- `Routes`： 包裹所有的`Route`，在其中匹配一个路由；router5.x 使用的是 Switch 组件

- `Route`：Route 用于路径的匹配

  - `path`：用于设置匹配到的路径
  - `element`: 设置匹配到路径后，渲染的组件；（router5.x 使用的是`component`属性）
  - ~~`exact`: 精准匹配，只有精准匹配到完全一致的路径，才会渲染对应的组件；（router6 不再支持该属性，将自动进行精准匹配）~~

- `Link`:用于路径跳转，最终背渲染为 a 元素

  - `to`:用于设置跳转到的路径
  - `replace`: boolean 值，路径是否替换
  - `state`:history 模式使用
  - `reloadDocument`:重载文档

- `NavLink`:在 link 基础上添加了一些样式属性

  - 选中的 link 项默认添加了 active 的 class 属性

    ```jsx
    <NavLink
      to="/other"
      style={({ isActive }) => ({ color: isActive ? 'red' : '' })}
      className={({ isActive }) => (isActive ? 'link-active' : '')}
    >
      其它
    </NavLink>
    ```

  - `style`&`className`: 传入函数，函数接收一个对象，包含`isActive`属性

- `Navigate`导航：用于路由的重定向，当组件出现时，会执行跳转到对应的 to 路径中

  Ⅰ.` <Navigate to="/home"></Navigate> `

  Ⅱ.`   <Route path="/" element={<Navigate to="/home" />} /> ` 用于首次页面重定向

  补充：配置 notfound 页面

  `         <Route path="*" element={<NotFound />}></Route> `

- 嵌套多级路由：在嵌套组路由的页面文件中需要使用 outlet 组件占位

  ```jsx
  // App.jsx

  <Routes>
    <Route path="/" element={<Navigate to="/home" />} />
    <Route path="/home" element={<Home />}>
      {/* 当路径为'/'时，默认跳转到HomeRecommend */}
      <Route path="/home" element={<Navigate to="/home/recommend" />} />
      <Route path="/home/recommend" element={<HomeRecommend />} />
      <Route path="/home/banner" element={<HomeBanner />} />
    </Route>
  </Routes>
  ```

  ```jsx
  // home.jsx

    render() {
      return (
        <div>
          {/* outlet组件用于在父路由元素中作为子路由的占位元素 */}
          <Outlet></Outlet>
          <h2> home</h2>
          <Link to="/home/recommend">推荐</Link>
          <Link to="/home/banner">Banner</Link>
        </div>
      );
    }
  ```

- 手动跳转

  - 函数式组件--使用`useNavigate`

    ```jsx
    // App.jsx

    import {
      Routes,
      Route,
      Link,
      Navigate,
      useNavigate
    } from 'react-router-dom';
    export function App(props) {
      const navigate = useNavigate();

      function navigateTo(path) {
        // 有两个参数：path(路径)和option option为对象:例如{replace:true}
        // 也可以传入delta：例如 -1或1 后退或前进路由
        navigate(path);
      }

      return (
        <div>
          <div className="header">
            <button onClick={() => navigateTo('/order')}>手动跳转</button>
          </div>
          <div className="content">
            <Routes>
              <Route path="/order" element={<Order />} />
            </Routes>
          </div>
        </div>
      );
    }
    ```

  - 类组件--封装高阶组件

    ```jsx
    import React, { PureComponent } from 'react';
    import { Link, Outlet, useNavigate } from 'react-router-dom';

    // 封装对应高阶组件
    function withRouter(WrapperComponent) {
      return function (props) {
        const navigate = useNavigate();
        const router = { navigate };
        return <WrapperComponent {...props} router={router} />;
      };
    }

    export class home extends PureComponent {
      navigateTo(path) {
        const { navigate } = this.props.router;
        navigate(path);
      }
      render() {
        return (
          <div>
            {/* outlet组件用于在父路由元素中作为子路由的占位元素 */}
            <Outlet></Outlet>
            <h2> home</h2>
            <button onClick={() => this.navigateTo('/home/songmenu')}>
              类组件手动跳转
            </button>
          </div>
        );
      }
    }

    export default withRouter(home);
    ```

#### 5.路由参数传递

- 路径动态传参 ：

  `          <Route path="/detail/:id" element={<Detail />} /> `

  示例：点击不同数据传参不同 id 到详情页面

  封装 WithRouter 高阶组件, 使用 useParams 传参

  ```jsx
  // HOC/WithRouter.js

  import { useNavigate, useParams } from 'react-router-dom';

  // 封装对应高阶组件
  function WithRouter(WrapperComponent) {
    return function NavigateComponent(props) {
      const navigate = useNavigate();
      const params = useParams();
      const router = { navigate, params };
      return <WrapperComponent {...props} router={router} />;
    };
  }

  export default WithRouter;
  ```

  动态传参 id：

  ```jsx
  // HomeSong.jsx

  import React, { PureComponent } from 'react';
  import WithRouter from '../HOC/WithRouter';

  export class HomeSong extends PureComponent {
    constructor(props) {
      super(props);
      this.state = {
        songs: [
          { id: 1, name: '测试1' },
          { id: 2, name: '测试2' },
          { id: 3, name: '测试3' }
        ]
      };
    }

    navigateToDetail(id) {
      const { navigate } = this.props.router;
      // 动态跳转
      navigate(`/detail/${id}`);
    }

    render() {
      const { songs } = this.state;
      return (
        <div>
          <h2>HomeSong</h2>
          <ul>
            {songs.map((item) => (
              <li key={item.id} onClick={() => this.navigateToDetail(item.id)}>
                {item.name}
              </li>
            ))}
          </ul>
        </div>
      );
    }
  }

  export default WithRouter(HomeSong);
  ```

  detail 文件使用参数：

  ```jsx
  import React, { PureComponent } from 'react';
  import WithRouter from '../HOC/WithRouter';

  export class Detail extends PureComponent {
    render() {
      const { router } = this.props;
      return (
        <div>
          <h1>Detail</h1>
          <h2>id:{router.params.id}</h2>
        </div>
      );
    }
  }

  export default WithRouter(Detail);
  ```

- `queryString`动态传参

  `<Link to="/user?id=1&name=user">user</Link> `

  `<Route path="/user" element={<User />} /> `

  ```jsx
  // WithRouter.js

  import { useLocation, useNavigate, useSearchParams } from 'react-router-dom';

  // 封装对应高阶组件
  function WithRouter(WrapperComponent) {
    return function NavigateComponent(props) {
      const navigate = useNavigate();
      //   方式一：
      const location = useLocation();
      //   方式二:常用
      const [searchParam] = useSearchParams();
      const query = Object.fromEntries(searchParam);
      const router = { navigate, query };
      return <WrapperComponent {...props} router={router} />;
    };
  }

  export default WithRouter;
  ```

  ```jsx
  // User.jsx

  import React, { PureComponent } from 'react';
  import WithRouter from '../HOC/WithRouter';

  export class User extends PureComponent {
    render() {
      const { router } = this.props;
      return <div>User: {router.query.name}</div>;
    }
  }

  export default WithRouter(User);
  ```

#### 6.将 router 配置提取到独立文件夹

```jsx
// App.jsx

import { Link, useNavigate, useRoutes } from 'react-router-dom';
import routes from './router/index';

<div className="content">{useRoutes(routes)}</div>;
```

```js
// router/index.js

import Home from '../pages/home';
import About from '../pages/about';
import Login from '../pages/Login';
import NotFound from '../pages/NotFound';
import HomeBanner from '../pages/HomeBanner';
import HomeRecommend from '../pages/HomeRecommend';
import Order from '../pages/Order';
import HomeSong from '../pages/HomeSong';
import Detail from '../pages/Detail';
import User from '../pages/User';
import { Navigate } from 'react-router-dom';

const routes = [
  {
    path: '/',
    element: <Navigate to="/home" />
  },
  {
    path: '/home',
    element: <Home />,
    children: [
      {
        path: '/home/recommend',
        element: <HomeRecommend />
      },
      {
        path: '/home/banner',
        element: <HomeBanner />
      },
      {
        path: '/home/songmenu',
        element: <HomeSong />
      }
    ]
  },
  {
    path: '/about',
    element: <About />
  },
  {
    path: '/login',
    element: <Login />
  },
  {
    path: '/order',
    element: <Order />
  },
  {
    path: '/detail/:id',
    element: <Detail />
  },
  {
    path: '/user',
    element: <User />
  },
  {
    path: '*',
    element: <NotFound />
  }
];
export default routes;
```

#### 7.路由懒加载

1.使用`React.lazy `

```js
// router/index.js

import React from 'react';

const About = React.lazy(() => import('../pages/about'));
const Login = React.lazy(() => import('../pages/Login'));
```

2.异步加载导致可能出现报错,使用`Suspense`进行包裹

```js
import React, { Suspense } from 'react';

root.render(
  <React.StrictMode>
    <HashRouter>
      {/* 懒加载 */}
      <Suspense fallback={<h3>Loading</h3>}>
        <App />
      </Suspense>
    </HashRouter>
  </React.StrictMode>
);
```

## hooks

### 函数式组件存在的问题

- class 组件可定义自己的 state，用来保存自己内部的状态；函数式组件不可以，函数每次调用都会产生新的临时变量
- class 组件有自己的生命周期，可在对应生命周期里处理逻辑；函数式组件如果没有 hooks，如果在函数中发送网络请求，意味着每次重新渲染都会重新发送一次网络请求
- class 组件可以在状态改变时只会重新执行 render 函数以及重新调用生命周期函数`componentDidUpdate`等；函数式组件在重新渲染时，整个函数会被执行

### hook 概述

![](/images/react/hook概述.jpg)

### hook 简单应用

```jsx
// CounterFunc.jsx

import { memo, useState } from 'react';

function CounterHook(props) {
  const [counter, setCounter] = useState(0);

  return (
    <div>
      <h2>当前计数：{counter}</h2>
      <button onClick={() => setCounter(counter + 1)}>+1</button>
      <button onClick={() => setCounter(counter - 1)}>-1</button>
    </div>
  );
}

export default memo(CounterHook);
```

```js
// App.js

import React, { memo } from 'react';
import CounterFunc from './counter/CounterFunc';

const App = memo(() => {
  return (
    <div>
      <p> App</p>
      <CounterFunc></CounterFunc>
    </div>
  );
});

export default App;
```

核心代码解读：

![](/images/react/核心代码.jpg)

### 使用 hook 的额外规则

- 只能在函数最外层调用 hook，不要在循环、条件判断或者子函数中调用
- 只能在 react 函数组件中调用 hook，不能在其它 js 函数中调用
- 自定义的 hooks 中，可以使用 react 提供的其他 hooks，**必须使用 use 开头**，例如 useFunc()

### State Hook--useState

- useState 定义一个 state 变量，一般来说在函数退出后变量就会消失，而 state 中的变量会被 react 保留；它与 class 里面的`this.state`提供的功能完全相同
- useState 接收一个唯一参数，在第一次组件被调用时使用来作为初始化值（如果没有传递参数，那么初始化值为 undefined）
- useState 的返回值是一个数组，可以通过数组解构来进行赋值

### Effect Hook--useEffect

- 用于完成一些类似于 class 中生命周期的功能,通过 useEffect 的 Hook，可以告诉 react 需要渲染后执行某些操作

- 类似于**网络请求**、**手动更新 dom**、事件监听、都是 react 更新 dom 的一些副作用

- useEffect 的参数：

  - 第一个参数：要求传入一个回调函数，在 react 执行完更新 dom 操作后，就会回调这个函数

  - 第二个参数：表示该 useEffect 在哪些 state 发生变化时，才重新执行；

    如果一个函数不希望依赖任何内容，也可以传入一个空数组[]

- **默认情况下**，无论是第一次渲染之后，还是每次更新之后，都会执行这个回调函数，可能会导致性能问题

- useEffect 传入的回调函数可以有一个返回值，进行清除 effect 逻辑处理，会在**组件更新和卸载的时候执行清除操作**

- 一个函数式组件中，**可以存在多个 useEffect**

示例：

```js
import React, { memo, useState, useEffect } from 'react';

const App = memo(() => {
  const [count, setCount] = useState(200);

  // 完成一些副作用的代码逻辑
  useEffect(() => {
    // 当前传入的回调函数会在组件渲染完成后，自动执行
    document.title = count;

    return () => {
      // 返回值：回调函数-- 组件被重新渲染或者组件卸载时执行
    };
  });
  return (
    <div>
      <h2>APP</h2>
      <button onClick={() => setCount(count + 1)}>修改数字</button>
    </div>
  );
});

export default App;
```

### Context Hook--useContext

示例：

--使用 Provider

```js
// index.js

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { UserContext } from './context/index';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <UserContext.Provider value={{ name: 'text', age: 20 }}>
      <App />
    </UserContext.Provider>
  </React.StrictMode>
);
```

```jsx
// App.jsx

import React, { memo, useContext } from 'react';
import { UserContext } from './context/index';

const App = memo(() => {
  // 使用context
  const user = useContext(UserContext);
  return (
    <div>
      <h1>{user.name}</h1>
    </div>
  );
});

export default App;
```

```js
context / index.js;

import { createContext } from 'react';

const UserContext = createContext();

export { UserContext };
```

### Reducer Hook--useReducer

- useState 的一种替代方案

### useCallback（性能优化）和 useMemo

**useCallback**

- 性能优化点：1.当需要将一个函数传递给子组件时，最好使用 useCallback 进行优化，将优化之后的函数传递给子组件
- 函数参数：第一个参数传入**回调函数**，会返回一个新的函数，在依赖不变的情况下，多次定义时，返回值是相同的；第二个参数是**依赖变量值组成的数组**
- 进一步优化：依赖变化的情况下，仍只返回同一个值，使用 useRef

```jsx
import React, { memo, useState, useCallback, useRef } from 'react';

// 子组件
const NEWIncrement = memo((props) => {
  const { increment } = props;
  return (
    <div>
      <button onClick={increment}>NEWIncrement+1</button>
    </div>
  );
});

// 每次函数式组件渲染时，increment函数都会被重新定义，
const App = memo(() => {
  const [count, setCount] = useState(0);
  const [name, setName] = useState('change');

  // 进一步优化：当count发生变化时,也使用同一个函数--使用useRef解决 在组件多次渲染时,返回同一个值
  const countRef = useRef();
  countRef.current = count;
  const increment = useCallback(
    function () {
      //   这样可以保证每次拿到的count值都是最新的值
      setCount(countRef.current + 1);
    },
    [count]
  );
  return (
    <div>
      <h2>count:{count}</h2>
      <h2>name:{name}</h2>
      <button onClick={increment}>+1</button>
      <button onClick={() => setName('new')}>修改名称</button>
      <NEWIncrement increment={increment}></NEWIncrement>
    </div>
  );
});

export default App;
```

**useMemo**

```jsx
import React, { memo, useCallback, useMemo, useState } from 'react';

function calcNum(num) {
  let total = 0;
  for (let i = 0; i < num; i++) {
    total += i;
  }
  return total;
}

const App = memo(() => {
  // 使用useMemo，依赖值不发生改变时，即使组件重新渲染，useMemo不会重新执行
  // const increment = useCallback(fn,[])相当于 const increment = useMemo(()=>fn,[])
  let result = useMemo(() => {
    return calcNum(50);
  }, []);
  return (
    <div>
      <h2>计算结果：{calcNum(50)}</h2>
      <h2>计算结果：{result}</h2>
    </div>
  );
});

export default App;
```

### useRef

**含义**：useRef 返回一个 ref 对象，返回的 ref 对象在组件的整个生命周期保持不变

**两种用法**：1.引入 dom（或者组件，但是需要是 class 组件）元素；2.保存一个数据，这个对象在整个生命周期中可以保持不变

```jsx
import React, { memo, useEffect, useRef } from 'react';

const App = memo(() => {
  //   不推荐使用
  //   useEffect(() => {
  //     document.querySelector('.title');
  //   }, []);

  function showDom() {
    console.log(titleRef.current); // <h2 class="title">操作dom</h2>
    inputRef.current.focus(); // 获取焦点
  }

  const titleRef = useRef();
  const inputRef = useRef();
  return (
    <div>
      <h2 ref={titleRef} className="title">
        操作dom
      </h2>
      <input type="text" ref={inputRef}></input>
      <button onClick={showDom}>获取dom</button>
    </div>
  );
});

export default App;
```

### forwardRef & useImperativeHandle

- 通过 forwardRef 可以将 ref 转发到子组件,子组件拿到父组件中创建的 ref,绑定到自己的某一元素中;
- 问题:父组件可以拿到 dom 后进行任意操作,导致某些情况不可控
- 通过 useImperativeHandle 可只暴露固定的操作,将传入的 ref 和 useImperativeHandle 第二个参数返回的对象绑定到了一起

```jsx
import React, { memo, useRef, forwardRef, useImperativeHandle } from 'react';

const HelloWorld = memo(
  forwardRef((props, ref) => {
    const sonInputRef = useRef();
    //   useImperativeHandle用来暴露给父组件的限定功能
    useImperativeHandle(ref, () => {
      return {
        focus() {
          sonInputRef.current.focus();
        }
      };
    });
    return <input type="text" ref={ref}></input>;
  })
);

const App = memo(() => {
  const titleRef = useRef();
  const inputRef = useRef();

  function handleDom() {
    console.log(titleRef.current);
    console.log(inputRef.current);
  }
  return (
    <div>
      <h2 ref={titleRef}>title标题</h2>
      <HelloWorld ref={inputRef}></HelloWorld>
      <button onClick={handleDom}>按钮</button>
    </div>
  );
});

export default App;
```

### useLayoutEffect

和 useEffect 的区别:

- useEffect 会在渲染的内容更新到 dom 上后执行,不会阻塞 dom 的更新
- useLayoutEffect 会在渲染内容更新到 dom 上之前执行,会阻塞 dom 的更新

### 自定义 hook

- 自定义 hook 命名以 use 开头

**案例 1:打印生命周期**

```jsx
import React, { memo, useEffect, useState } from 'react';

function useLogLife(componentName) {
  useEffect(() => {
    console.log(`${componentName}创建`);
    return () => {
      console.log(`${componentName}销毁`);
    };
  }, []);
}

const Home = memo(() => {
  useLogLife('home');
  return <h1>Home Page</h1>;
});

const About = memo(() => {
  useLogLife('about');
  return <h1>About Page</h1>;
});

const App = memo(() => {
  const [isShow, setIsShow] = useState(true);
  useLogLife('app');
  return (
    <div>
      <h1>App Root Component</h1>
      <button onClick={() => setIsShow(!isShow)}>切换</button>
      {isShow && <Home />}
      {isShow && <About />}
    </div>
  );
});

export default App;
```

**案例 2.从 context 中获取数据**

```js
// hooks/useUserToken.js

import { UserContext, TokenContext } from '../context';
import { useContext } from 'react';

function useUserToken() {
  const user = useContext(UserContext);
  const token = useContext(TokenContext);
  return [user, token];
}

export default useUserToken;
```

```js
// hooks/index.js

import useUserToken from './useUserToken';

export { useUserToken };
```

```jsx
// App.jsx

import React, { memo } from 'react';
import { useUserToken } from './hooks';

const Home = memo(() => {
  const [user, token] = useUserToken();
  return (
    <div>
      <p>Home:{user.name}</p>
      <p>Token:{token}</p>
    </div>
  );
});

const App = memo(() => {
  return (
    <div>
      <h1>app </h1>
      <Home></Home>
    </div>
  );
});

export default App;
```

## redux hooks

### useSelector & useDispatch

**作用:** 将 state 映射到组件中

**参数:** 参数一:将 state 映射到需要的数据中;参数二:可以进行比较来**决定是否组件重新渲染**

**注意:** useSelector 会默认比较返回的两个对象是否相等,也就是必须返回两个完全相等的对象才可以不引起重新渲染

**安装:** `npm install @reduxjs/toolkit react-redux`

引入`Provider`

```js
// index.js

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import store from './redux-store';
import { Provider } from 'react-redux';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <Provider store={store}>
    <App />
  </Provider>
);
```

新建 store 模块，创建 slice 片段：

```js
// redux-store/modules/counter.js

import { createSlice } from '@reduxjs/toolkit';

const counterSlice = createSlice({
  name: 'counter',
  initialState: {
    counter: 11
  },
  reducers: {
    addNumber(state, { payload }) {
      state.counter = state.counter + payload;
    },
    subNumber(state, { payload }) {
      state.counter = state.counter - payload;
    }
  }
});

export const { addNumber, subNumber } = counterSlice.actions;
export default counterSlice.reducer;
```

模块统一管理导出：

```js
// redux-store/index.js

import { configureStore } from '@reduxjs/toolkit';
import counterReducer from './modules/counter';

const store = configureStore({
  reducer: {
    counter: counterReducer
  }
});

export default store;
```

**使用`useSelector`将 redux 中 store 的数据映射到组件内**

**使用`useDispatch `直接派发 action：**

**使用`shallowEqual `进行性能优化：**

```jsx
import React, { memo } from 'react';
import { useSelector, useDispatch, shallowEqual } from 'react-redux';
import {
  addNumber,
  subNumber,
  changeMessage
} from './redux-store/modules/counter';

// memo高阶组件包裹起来的组件有对应特点: 只有props发生改变时, 才会重新渲染;
// 此处使用useSelector监听的是整个state,如果state中的值改变,则home子组件就重新渲染,从性能优化的角度,useSelector传入第二个参数shallowEqual,进行浅层比较以决定组件是否重新渲染
const Home = memo(() => {
  const { message } = useSelector(
    (state) => ({
      message: state.counter.message
    }),
    shallowEqual
  );

  const dispatch = useDispatch();
  function changeTitle() {
    dispatch(changeMessage('change'));
  }

  return (
    <div>
      <h2>Home:{message}</h2>
      <button onClick={() => changeTitle()}>改变title</button>
    </div>
  );
});

const App = memo((props) => {
  const { count } = useSelector(
    (state) => ({
      count: state.counter.counter
    }),
    shallowEqual
  );

  const dispatch = useDispatch();
  function addNumberHandle(num, isAdd = true) {
    if (isAdd) {
      dispatch(addNumber(num));
    } else {
      dispatch(subNumber(num));
    }
  }

  return (
    <div>
      <h2>当前计数: {count}</h2>
      <button onClick={() => addNumberHandle(1)}>+1</button>
      <button onClick={() => addNumberHandle(5)}>+5</button>
      <button onClick={() => addNumberHandle(10, false)}>-10</button>
      <Home></Home>
    </div>
  );
});

export default App;
```

### useTransition

官方解释：返回一个状态值表示过渡任务的等待状态，以及一个启动该过渡任务的函数，实质是在告诉 react 对某部分任务的更新优先级比较低，可以稍后进行更新

![](/images/react/useTransition.jpg)

### useDeferredValue

概念：useDeferredValue 接受一个值，并返回该值的副本，该副本将推迟到更紧急的更新之后

![](/images/react/useDeferr.jpg)

### useId(react18 新增)

#### 概念：

useId 是一个用于生成横跨服务端和客户端的稳定的唯一 ID 的同时避免 hydration 不匹配的 hook

![](/images/react/useId.jpg)

## 两种渲染方式

- **SSR**（Server Side Rendering 服务端渲染）：早期服务端渲染包括 PHP、JSP、ASP 等方式，指的是页面在服务器端已经生成了完整的 html 结构，浏览器将整个 html 请求过来，不需要浏览器通过执行 js 代码，提前完成了页面结构

- **CSR**（Client Side Rendering 客户端渲染）：SPA 页面通常依赖的就是客户端渲染

### SSR 同构应用

概念：一套代码既可以在服务端运行，又可以在客户端运行

具体流程：

- 当用户发出请求时，现在服务器通过 SSR 渲染出首页的内容
- 但是对应代码同样可以在客户端被执行
- 执行目的包括事件绑定等以及其他页面切换时也可以在客户端被渲染

## SPA 单页面富应用问题

1.首屏渲染速度

2.不利于 SEO 优化(搜索引擎优化)

### SPA 如何在浏览器渲染页面

1.浏览器根据域名或 ip 地址去服务器请求对应文件：index.html ， webpack 搭建的环境中 index.html 中 body 元素中只有` <div id="root"></div> `,搜索引擎如百度进行爬虫获取信息时是下载 index.html 文件，而 index.html 中 body 元素中内容极少，所以不利于 SEO 优化。

2.浏览器通过 script src="bundle.js"下载 bundle.js 文件，且由浏览器执行 bundle.js 代码，所以首屏渲染速度较慢

### Hydration

![](/images/react/hydration.jpg)

这个过程称为**Hydration**

```jsx
import React, { memo } from 'react';
import { useState, useId } from 'react';

const App = memo(() => {
  const [count, setCount] = useState();
  const id = useId();
  console.log(id); // 打印的值始终为同一个值
  return (
    <div>
      <button onClick={() => setCount(count + 1)}>+1:{count}</button>
    </div>
  );
});

export default App;
```

## react-项目

### Ⅰ 配置别名 @=>src

**问题**:因为 react 脚手架隐藏 webpack

解决一:`npm run eject` /

**解决二**: craco => create-react-app config

安装:`npm install @craco/craco@alpha -D` 新建 craco.config.js 文件

```js
// craco.config.js

const path = require('path');
const resolve = (pathname) => path.resolve(__dirname, pathname);

module.exports = {
  webpack: {
    alias: {
      // 拼接当前文件所在路径和src 生成绝对路径
      '@': resolve('src')
    }
  }
};
```

package.json 中运行命令修改

```json
	// 原

	"scripts": {
		"start": "react-scripts start",
		"build": "react-scripts build",
		"test": "react-scripts test",
		"eject": "react-scripts eject"
	},

	// 修改为
		"scripts": {
		"start": "craco start",
		"build": "craco build",
		"test": "craco test",
		"eject": "react-scripts eject"
	},
```

### Ⅱ 配置 less

安装: `npm install craco-less@2.1.0-alpha.0`

安装:`npm install craco-less`

新建 craco.config.js 文件

```js
const path = require('path');
const CracoLessPlugin = require('craco-less');

const resolve = (pathname) => path.resolve(__dirname, pathname);

module.exports = {
  Plugins: [
    {
      plugin: CracoLessPlugin
    }
  ],
  webpack: {
    alias: {
      // 拼接当前文件所在路径和src 生成绝对路径
      '@': resolve('src')
    }
  }
};
```

### Ⅲ css 样式重置

安装:`npm install normalize.css`

index.js 文件中导入:

```js
// index.js

import 'normalize.css';
```

```less
// variables.less

@textColor: #484848;
@textColorSecondary: #222;
```

```less
// reset.less

@import './variables.less';

* {
  padding: 0;
  margin: 0;
}

a {
  color: @textColor;
  text-decoration: none;
}

img {
  vertical-align: top;
}

ul,
li {
  list-style: none;
}
```

```less
// assets/css/index.less

@import './variables.less';
@import './reset.less';
```

### Ⅳ 路由配置

安装:`npm install react-router-dom`

导入: 采用路由懒加载要导入 suspense

```js
// index.js

import React from 'react';
import ReactDOM from 'react-dom/client';
import App from '@/App';
import 'normalize.css';
import './assets/css/index.less';
import { Suspense } from 'react';

import { HashRouter } from 'react-router-dom';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <Suspense fallback="loading">
      <HashRouter>
        <App />
      </HashRouter>
    </Suspense>
  </React.StrictMode>
);
```

搭建基本页面,建 router 文件夹:

```js
// router/index.js

import React from 'react';
import { Navigate } from 'react-router-dom';

const Home = React.lazy(() => import('@/views/home'));
const Entire = React.lazy(() => import('@/views/entire'));
const Detail = React.lazy(() => import('@/views/detail'));

const routes = [
  {
    path: '/home',
    element: <Home />
  },
  {
    path: '/',
    element: <Navigate to="/home" />
  },
  {
    path: '/entire',
    element: <Entire />
  },
  {
    path: '/detail',
    element: <Detail />
  }
];

export default routes;
```

### Ⅴ redux 状态管理

两种方式:① 普通方式:目前项目中使用率非常高; ② @reduxjs/toolkit 方式:推荐

安装:`npm install @reduxjs/toolkit react-redux`

建 store 文件,导入`configureStore`

```js
// store/index.js

import { configureStore } from '@reduxjs/toolkit';

const store = configureStore({
  reducer: {}
});

export default store;
```

主入口文件导入`Provider `

```js
// index.js

import { Provider } from 'react-redux';
import store from './store';

<Provider store={store}>
  <HashRouter>
    <App />
  </HashRouter>
</Provider>;
```

**第二种方式:**

```js
// store/modules/home.js

import { createSlice } from '@reduxjs/toolkit';

const homeSlice = createSlice({
  name: 'home',
  initialState: {},
  reducers: {}
});

export default homeSlice.reducer;
```

```js
// store/index.js

import { configureStore } from '@reduxjs/toolkit';
import homeReducer from './modules/home';

const store = configureStore({
  reducer: {
    home: homeReducer
  }
});

export default store;
```

**第一种方式:**

```js
// entire/reducer.js

const initailState = {};

function reducer(state = initailState, action) {
  switch (action.type) {
    default:
      return state;
  }
}

export default reducer;
```

```js
// entire/index.js

import reducer from './reducer';

export default reducer;
```

```js
// store/index.js

import entireReducer from './modules/entire/index';

const store = configureStore({
  reducer: {
    entire: entireReducer
  }
});
```

### Ⅵ axios

安装:`npm install axios`

```js
// services/request/config.js

export const BASE_URL = 'http://codercba.com:1888/airbnb/api';

export const TIMEOUT = 5000;
```

封装 axios

```js
// services/request/index.js

import axios from 'axios';
import { BASE_URL, TIMEOUT } from './config';

class ReactRequest {
  constructor(baseURL, timeout) {
    this.instance = axios.create({
      baseURL,
      timeout
    });

    //   响应拦截
    this.instance.interceptors.response.use(
      (res) => {
        return res.data;
      },
      (err) => {
        return err;
      }
    );
  }

  request(config) {
    return this.instance.request(config);
  }

  get(config) {
    return this.request({ ...config, method: 'get' });
  }
  post(config) {
    return this.request({ ...config, method: 'post' });
  }
}

export default new ReactRequest(BASE_URL, TIMEOUT);
```

```js
// services/index.js

import ReactRequest from './request';

export default ReactRequest;
```

home 组件调用接口获取数据

```jsx
import React, { memo, useEffect, useState } from 'react';
import ReactRequest from '@/services';

const index = memo(() => {
  // 定义状态
  const [highhScore, setHighScore] = useState({});
  // 发送网络请求
  useEffect(() => {
    ReactRequest.get({ url: '/home/highscore' }).then((res) => {
      setHighScore(res);
    });
  }, []);

  const { list, title, subtitle } = highhScore;
  return (
    <div>
      <h2>{title}</h2>
      <h2>{subtitle}</h2>

      {list?.map((item) => (
        <div key={item.id}>
          <li>{item.name}</li>
          <li>{item.price_format}</li>
        </div>
      ))}
    </div>
  );
});

export default index;
```
