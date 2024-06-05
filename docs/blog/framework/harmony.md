## 鸿蒙-学习

### 了解 HarmonyOS

#### HarmonyOS 特征

- 搭载该操作系统的设备在系统层面融为一体、形成超级终端，让设备的硬件能力可以弹性扩展，实现设备之间硬件互助，资源共享。

  对消费者而言，HarmonyOS 能够将生活场景中的各类终端进行能力整合，实现不同终端设备之间的快速连接、能力互助、资源共享，匹配合适的设备、提供流畅的全场景体验。

  关键技术包括分布式软总线、分布式设备虚拟化、分布式数据管理、分布式任务调度等

- 面向开发者，实现一次开发，多端部署。

  对应用开发者而言，HarmonyOS 采用了多种分布式技术，使应用开发与不同终端设备的形态差异无关，从而让开发者能够聚焦上层业务逻辑，更加便捷、高效地开发应用。

- 一套操作系统可以满足不同能力的设备需求，实现统一 OS，弹性部署。

  对设备开发者而言，HarmonyOS 采用了组件化的设计方案，可根据设备的资源能力和业务特征灵活裁剪，满足不同形态终端设备对操作系统的要求。

#### 架构

![](/images/harmony/架构.jpg)

### 工程目录

- AppScope 中存放应用全局所需要的资源文件。
- entry 是应用的主模块，存放 HarmonyOS 应用的代码、资源等。
- oh_modules 是工程的依赖包，存放工程依赖的源文件。
- build-profile.json5 是工程级配置信息，包括签名、产品配置等。
- hvigorfile.ts 是工程级编译构建任务脚本，hvigor 是基于任务管理机制实现的一款全新的自动化构建工具，主要提供任务注册编排，工程模型管理、配置管理等核心能力。
- oh-package.json5 是工程级依赖配置文件，用于记录引入包的配置信息。

  在 AppScope，其中有 resources 文件夹和配置文件 app.json5。

  AppScope>resources>base 中包含 element 和 media 两个文件夹，

- 其中 element 文件夹主要存放公共的字符串、布局文件等资源。
- media 存放全局公共的多媒体资源文件。

- AppScope>app.json5 是应用的全局的配置文件，用于存放应用公共的配置信息。
  - bundleName 是包名。
  - vendor 是应用程序供应商。
  - versionCode 是用于区分应用版本。
  - versionName 是版本号。

### 模块级目录

entry>src 目录中主要包含总的 main 文件夹，单元测试目录 ohosTest，以及模块级的配置文件

- main 文件夹中，ets 文件夹用于存放 ets 代码，resources 文件存放模块内的多媒体及布局文件等，module.json5 文件为模块的配置文件。
  - entry>src>main>module.json5 是模块的配置文件，包含当前模块的配置信息。
- ohosTest 是单元测试目录。
- build-profile.json5 是模块级配置信息，包括编译构建配置项。
- hvigorfile.ts 文件是模块级构建脚本。
- oh-package.json5 是模块级依赖配置信息文件。

进入 src>main>ets 目录中，其分为 entryability、pages 两个文件夹。

- entryability 存放 ability 文件，用于当前 ability 应用逻辑和生命周期管理。
- pages 存放 UI 界面相关代码文件，初始会生成一个 Index 页面。

## ArkTS

### 装饰器

1. @Entry 装饰的自定义组件将作为 UI 页面的入口。在单个 UI 页面中，最多可以使用@Entry 装饰一个自定义组件。@Entry 可以接受一个可选的 LocalStorage 的参数。

2. @Component 装饰器，代表自定义组件

3. @State 装饰器，被它装饰的变量值发生改变时，会触发该变量所对应的自定义组件 的 UI 界面进行自动刷新。

4. @Builder 装饰的函数：自定义构建函数，该方法被认为是该组件的私有、特殊类型的成员函数。

   全局的自定义构建函数可以被整个应用获取，不允许使用 this 和 bind 方法。

5. @Prop 装饰的变量可以和父组件建立单向的同步关系。@Prop 装饰的变量是可变的，但是变化不会同步回其父组件。

   @Prop 修饰复杂类型时是深拷贝，在拷贝的过程中除了基本类型、Map、Set、Date、Array 外，都会丢失类型。

   @Prop 装饰器不能在@Entry 装饰的自定义组件中使用。

6. @Link,子组件中被@Link 装饰的变量与其父组件中对应的数据源建立双向数据绑定。

### 事件

1. 箭头函数

```js
Button('Click me').onClick(() => {
  this.myText = 'ArkUI';
});
```

2. 匿名函数

```js
Button('add counter').onClick(
  function () {
    this.counter += 2;
  }.bind(this)
);
```

3. 成员函数

```js
myClickHandler(): void {
  this.counter += 2;
}
...
Button('add counter')
  .onClick(this.myClickHandler.bind(this))
```

### 自定义组件

#### 组件构成

自定义组件基于 struct 实现，struct + 自定义组件名 + {...}的组合构成自定义组件，不能有继承关系。对于 struct 的实例化，可以省略 new。

⭐️ @Component 装饰器仅能装饰 struct 关键字声明的数据结构。struct 被@Component 装饰后具备组件化的能力，需要实现 build 方法描述 UI，一个 struct 只能被一个@Component 装饰。

⭐️ build()函数用于定义自定义组件的声明式 UI 描述，自定义组件必须定义 build()函数。

- @Entry 装饰的自定义组件，其 build()函数下的根节点唯一且必要，且必须为容器组件，其中 ForEach 禁止作为根节点。
- @Component 装饰的自定义组件，其 build()函数下的根节点唯一且必要，可以为非容器组件，其中 ForEach 禁止作为根节点。

```js
@Component
struct MyComponent {
	build(){}
}
```

⭐️ 自定义组件除了必须要实现 build()函数外，还可以实现其他成员函数，成员函数具有以下约束：

- 不支持静态函数。
- 成员函数的访问是私有的。
  自定义组件可以包含成员变量，成员变量具有以下约束：
  - 不支持静态成员变量。
  - 所有成员变量都是私有的，变量的访问规则与成员函数的访问规则相同。
- 自定义组件的成员变量本地初始化有些是可选的，有些是必选的。具体是否需要本地初始化，是否需要从父组件通过参数传递初始化子组件的成员变量，请参考状态管理。

⚠️ 注意：自定义组件不允许调用没有用@Builder 装饰的方法，允许系统组件的参数是 TS 方法的返回值。

```js
@Component
struct ParentComponent {
  doSomeCalculations() {
  }

  calcTextValue(): string {
    return 'Hello World';
  }

  @Builder doSomeRender() {
    Text(`Hello World`)
  }

  build() {
    Column() {
      // 反例：不能调用没有用@Builder装饰的方法
      this.doSomeCalculations();
      // 正例：可以调用
      this.doSomeRender();
      // 正例：参数可以为调用TS方法的返回值
      Text(this.calcTextValue())
    }
  }
}
```

#### 创建和渲染流程

1)自定义组件的创建：自定义组件的实例由 ArkUI 框架创建。

2)初始化自定义组件的成员变量：通过本地默认值或者构造方法传递参数来初始化自定义组件的成员变量，初始化顺序为成员变量的定义顺序。

3)如果开发者定义了 aboutToAppear，则执行 aboutToAppear 方法。

4)在首次渲染的时候，执行 build 方法渲染系统组件，如果子组件为自定义组件，则创建自定义组件的实例。在执行 build()函数的过程中，框架会观察每个状态变量的读取状态，将保存两个 map：

a.状态变量 -> UI 组件（包括 ForEach 和 if）。

b.UI 组件 -> 此组件的更新函数，即一个 lambda 方法，作为 build()函数的子集，创建对应的 UI 组件并执行其属性方法，示意如下。

```js
build() {
  ...
  this.observeComponentCreation(() => {
    Button.create();
  })

  this.observeComponentCreation(() => {
    Text.create();
  })
  ...
}
```

#### 重新渲染

当事件句柄被触发（比如设置了点击事件，即触发点击事件）改变了状态变量时，或者 LocalStorage / AppStorage 中的属性更改，并导致绑定的状态变量更改其值时：

1)框架观察到了变化，将启动重新渲染。

2)根据框架持有的两个 map（自定义组件的创建和渲染流程中第 4 步），框架可以知道该状态变量管理了哪些 UI 组件，以及这些 UI 组件对应的更新函数。执行这些 UI 组件的更新函数，实现最小化更新。

#### 删除

如果 if 组件的分支改变，或者 ForEach 循环渲染中数组的个数改变，组件将被删除：

1)在删除组件之前，将调用其 aboutToDisappear 生命周期函数，标记着该节点将要被销毁。ArkUI 的节点删除机制是：后端节点直接从组件树上摘下，后端节点被销毁，对前端节点解引用，当前端节点已经没有引用时，将被 JS 虚拟机垃圾回收。

2)自定义组件和它的变量将被删除，如果其有同步的变量，比如@Link、@Prop、@StorageLink，将从同步源上取消注册。

不建议在生命周期 aboutToDisappear 内使用 async await，如果在生命周期的 aboutToDisappear 使用异步操作（Promise 或者回调方法），自定义组件将被保留在 Promise 的闭包中，直到回调方法被执行完，这个行为阻止了自定义组件的垃圾回收。

## 生命周期

### 页面生命周期（被@Entry 装饰的组件生命周期）

- onPageShow：页面每次显示时触发。
- onPageHide：页面每次隐藏时触发一次。
- onBackPress：当用户点击返回按钮时触发。

  触发返回一个页面后会导致当前 Index 页面被销毁。

### 组件生命周期（用@Component 装饰的自定义组件的生命周期）

- aboutToAppear：组件即将出现时回调该接口，具体时机为在创建自定义组件的新实例后，在执行其 build()函数之前执行。
- aboutToDisappear：在自定义组件即将析构销毁时执行。
  生命周期流程如下图所示，下图展示的是被@Entry 装饰的组件（首页）生命周期。

![](/images/harmony/生命周期.jpg)

❓pushUrl 和 replaceUrl 的区别

- 调用 router.pushUrl ，执行当前页面生命周期 onPageHide 函数，跳转到新页面后，执行初始化新页面的生命周期的流程。

- 调用 router.replaceUrl，执行当前页面生命周期 onPageHide 函数，当前页面组件调用 aboutToDisappear 函数，再执行初始化新页面的生命周期流程。

❓ 父组件和拥有@Prop 变量的子组件初始渲染和更新流程

1)初始渲染：

a.执行父组件的 build()函数将创建子组件的新实例，将数据源传递给子组件；

b.初始化子组件@Prop 装饰的变量。

2)更新：

a.子组件@Prop 更新时，更新仅停留在当前子组件，不会同步回父组件；

b.当父组件的数据源更新时，子组件的@Prop 装饰的变量将被来自父组件的数据源重置，所有@Prop 装饰的本地的修改将被父组件的更新覆盖。

```js
@Component
struct CountDownComponent {
  @Prop count: number;
  costOfOneAttempt: number = 1;

  build() {
    Column() {
      if (this.count > 0) {
        Text(`You have ${this.count} Nuggets left`).height(80)
      } else {
        Text('Game over!').height(80)
		      }
      // @Prop装饰的变量不会同步给父组件
      Button(`Try again`).onClick(() => {
        this.count -= this.costOfOneAttempt;
      }).height(80)
        .width(250)
        .margin(5)
    }
  }
}

@Entry
@Component
struct ParentComponent {
  @State countDownStartValue: number = 10;

  build() {
    Column() {
      Text(`Grant ${this.countDownStartValue} nuggets to play.`)
        .height(80)
      // 父组件的数据源的修改会同步给子组件
      Button(`+1 - Nuggets in New Game`).onClick(() => {
        this.countDownStartValue += 1;
      }).height(80)
        .width(250)
        .margin(5)

      // 父组件的修改会同步给子组件
      Button(`-1  - Nuggets in New Game`).onClick(() => {
        this.countDownStartValue -= 1;
      }).height(80)
        .width(250)
        .margin(5)

      CountDownComponent({ count: this.countDownStartValue, costOfOneAttempt: 2 })
      Divider()
    }
  }
}
```

❓ 父组件和拥有@Link 变量的子组件的关系，初始渲染和双向更新的流程

1)初始渲染：执行父组件的 build()函数后将创建子组件的新实例。初始化过程如下：

a.必须指定父组件中的@State 变量，用于初始化子组件的@Link 变量。子组件的@Link 变量值与其父组件的数据源变量保持同步（双向数据同步）。

b.父组件的@State 状态变量包装类通过构造函数传给子组件，子组件的@Link 包装类拿到父组件的@State 的状态变量后，将当前@Link 包装类 this 指针注册给父组件的@State 变量。

2)@Link 的数据源的更新：即父组件中状态变量更新，引起相关子组件的@Link 的更新。处理步骤：

a.通过初始渲染的步骤可知，子组件@Link 包装类把当前 this 指针注册给父组件。父组件@State 变量变更后，会遍历更新所有依赖它的系统组件（elementid）和状态变量（比如@Link 包装类）。

b.通知@Link 包装类更新后，子组件中所有依赖@Link 状态变量的系统组件（elementId）都会被通知更新。以此实现父组件对子组件的状态数据同步。

3)@Link 的更新：当子组件中@Link 更新后，处理步骤如下（以父组件为@State 为例）：

a.@Link 更新后，调用父组件的@State 包装类的 set 方法，将更新后的数值同步回父组件。

b.子组件@Link 和父组件@State 分别遍历依赖的系统组件，进行对应的 UI 的更新。以此实现子组件@Link 同步回父组件@State。

```js
@Component
struct Child {
  @Link items: number[];

  build() {
	    Column() {
      Button(`Button1: push`).onClick(() => {
        this.items.push(this.items.length + 1);
      })
      Button(`Button2: replace whole item`).onClick(() => {
        this.items = [100, 200, 300];
      })
    }
  }
}
```

```js
@Entry
@Component
struct Parent {
  @State arr: number[] = [1, 2, 3];

  build() {
    Column() {
      Child({ items: $arr })
      ForEach(this.arr,
        item => {
          Text(`${item}`)
        },
        item => item.toString()
      )
    }
  }
}
```

### ForEach 使用

```js
@Entry
@Component
struct Parent {
  @State simpleList: Array<string> = ['one', 'two', 'three','two'];

  build() {
    Row() {
      Column() {
        ForEach(this.simpleList, (item: string) => {
          ChildItem({ item: item })
        }, (item: string) => item)
      }
      .width('100%')
      .height('100%')
    }
    .height('100%')
    .backgroundColor(0xF1F3F5)
  }
}

@Component
struct ChildItem {
  item: string;

  build() {
    Text(this.item)
      .fontSize(50)
  }
}
```
