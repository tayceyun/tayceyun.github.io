---
sidebar: auto
tags:
  - 小程序
  - 原生
---

## native wx

## 基础

### 运行环境

当小程序基于 WebView 环境下时，WebView 的 JS 逻辑、DOM 树创建、CSS 解析、样式计算、Layout、Paint (Composite) 都发生在同一线程，在 WebView 上执行过多的 JS 逻辑可能阻塞渲染，导致界面卡顿。以此为前提，小程序同时考虑了性能与安全，采用了目前称为「双线程模型」的架构。

### 双线程模型

**概念**

- 渲染线程（UI 线程）和逻辑线程（JS 线程）分离
- 每个页面都需要新建一个 JS 引擎实例（WebView）

**小程序：AppService 和 WebView 的双线程模型**

- WXML 模块和 WXSS 样式运行于**渲染层**，渲染层的界面使用 WebView 进行渲染（一个小程序存在多个界面，所以渲染层存在多个 WebView 线程）

- JS 脚本工作在**逻辑层**，逻辑层采用 JsCore 线程运行 JS 脚本

- 这两个线程的通信会经由微信客户端（Native）做中转，逻辑层发送网络请求也经由 Native 转发，小程序的通信模型下图所示。
  ![](/images/wx/运行环境.png)

### skyline 渲染引擎

为了进一步优化小程序性能，提供更为接近原生的用户体验，小程序在 WebView 渲染之外新增了一个渲染引擎 Skyline，其使用更精简高效的渲染管线，并带来诸多增强特性，让 Skyline 拥有更接近原生渲染的性能体验。

Skyline 创建了一条渲染线程来负责 Layout, Composite 和 Paint 等渲染任务，并在 AppService 中划出一个独立的上下文，来运行之前 WebView 承担的 JS 逻辑、DOM 树创建等逻辑。这种新的架构相比原有的 WebView 架构，有以下特点：

- 界面更不容易被逻辑阻塞，进一步减少卡顿
- 无需为每个页面新建一个 JS 引擎实例（WebView），减少了内存、时间开销
- 框架可以在页面之间共享更多的资源，进一步减少运行时内存、时间开销
- 框架的代码之间无需再通过 JSBridge 进行数据交换，减少了大量通信时间开销

![](/images/wx/双线程.png)

### 模块化

可以将一些公共的代码抽离成为一个单独的 js 文件，作为一个模块。模块只有通过 `module.exports`(建议使用) 或者 `exports` 才能对外暴露接口

示例：

```js
// common.js
function sayHello(name) {
  console.log(`Hello ${name} !`);
}
function sayGoodbye(name) {
  console.log(`Goodbye ${name} !`);
}

module.exports.sayHello = sayHello;
exports.sayGoodbye = sayGoodbye;
```

使用公共函数(require 引入)：

```js
const common = require('common.js');
Page({
  helloMINA: function () {
    common.sayHello('MINA');
  },
  goodbyeMINA: function () {
    common.sayGoodbye('MINA');
  }
});
```

### 生命周期

#### 小程序生命周期

小程序启动

- 冷启动：如果用户首次打开，或小程序销毁后被用户再次打开，此时小程序需要重新加载启动，即冷启动。
- 热启动：如果用户已经打开过某小程序，然后在一定时间内再次打开该小程序，此时小程序并未被销毁，只是从后台状态进入前台状态，这个过程就是热启动

小程序生命周期
![](/images/wx/小程序生命周期.png)

页面生命周期
![](/images/wx/生命周期.png)

### 小程序更新

手动触发更新

```js
const updateManager = wx.getUpdateManager();

updateManager.onCheckForUpdate(function (res) {
  // 请求完新版本信息的回调
  console.log(res.hasUpdate);
});

updateManager.onUpdateReady(function () {
  wx.showModal({
    title: '更新提示',
    content: '新版本已经准备好，是否重启应用？',
    success(res) {
      if (res.confirm) {
        // 新的版本已经下载好，调用 applyUpdate 应用新版本并重启
        updateManager.applyUpdate();
      }
    }
  });
});

updateManager.onUpdateFailed(function () {
  // 新版本下载失败
});
```

## 开发

### 配置文件

**全局配置文件**

```json
{
  "pages": ["pages/index/index"],
  "window": {
    "backgroundTextStyle": "dark",
    "navigationBarBackgroundColor": "#fff",
    "navigationBarTitleText": "WeChat",
    "navigationBarTextStyle": "black",
    "enablePullDownRefresh": false
  },
  "tabBar": {
    "selectedColor": "#ff8189", // 文字高亮颜色
    "list": [
      {
        "pagePath": "pages/home/home",
        "text": "首页",
        "iconPath": "static/icons/shouye.png",
        "selectedIconPath": "static/icons/shouye-active.png"
      }
    ]
  }
}
```

**页面配置文件**

```json
{
  "navigationBarTitleText": "页面标题",
  "enablePullDownRefresh": false, // 下拉刷新
  "usingComponents": {} // 页面中需要用到的组件在此注册
}
```

### 基础语法

#### 重命名`wx:for`遍历元素名称、索引

```html
<view class="books">
  <!-- 将数组中遍历元素item重命名为book；index重命名为i -->
  <view wx:for="{{books}}" wx:key="id" wx:for-item="book" wx:for-index="i">
    {{book.name}} - {{book.price}} - {{i}}
  </view>
</view>
```

#### 条件渲染

```html
<view wx:if="{{view == 'WEBVIEW'}}"> WEBVIEW </view>
<view wx:elif="{{view == 'APP'}}"> APP </view>
<view wx:else="{{view == 'MINA'}}"> MINA </view>
```

### 场景一：判断小程序进入的场景/途径

- 在`onLaunch`生命周期回调函数中，会有`options`参数，`options.scene`值为小程序进入场景

- 常见的打开场景：群聊 / 小程序列表 / 微信扫一扫 / 另一个小程序打开等

### 场景二：onlaunch 函数常见操作

- 登录，将登录成功的数据，保存到 storage
- 读取本地数据，类似于 token，保存在全局供页面使用
- 请求整个应用程序需要的数据

```javascript
App({
  globalData: {
    token: '',
    userInfo: {}
  },
  onLaunch(options) {
    // 从本地获取token / userInfo
    const token = wx.getStorageSync('token');
    const userInfo = wx.getStorageSync('userInfo');
    // 如果没有信息，则进行登录操作
    if (!token || !userInfo) {
      // 将登录成功的数据，保存到storage
      wx.setStorageSync('token', '123');
      wx.setStorageSync('userInfo', { name: 'ttt', age: 12 });
    }

    // 将获取的数据保存到globalData中
    this.globalData = { token, userInfo };
    // 发送网络请求，优先请求一些必要的数据
  },
  onHide() {
    console.log('小程序切后台');
  }
});
```

**页面文件中获取共享数据**

```javascript
Page({
  data: {
    userInfo: ''
  },

  // 获取全局数据
  onLoad() {
    // 获取app实例对象
    const app = getApp();
    // 从app实例对象获取数据
    const token = app.globalData.token; // token
    const userInfo = app.globalData.userInfo; // 用户信息
    // 拿到token，发送网络请求
    wx.request({
      url: 'url'
    });
    // 将数据展示到页面上
    this.setData({
      userInfo
    });
  }
});
```

### 场景三：事件参数传递

- 通过`data-[attr]`传递

- 通过`Mark`传递

  ` <view mark:age="12" bind:tap="checkMark">mark传参</view>`

  ```javascript
    checkMark(e) {
      console.log(e.mark.age);
    },
  ```

### 场景四：获取设备信息（自定义 navbar、胶囊位置、安全底部）

- 自定义 navbar

  index.json: `"navigationStyle": "custom",`

- 胶囊位置 和 安全底部

```javascript
// 获取系统信息：
const systemInfo = wx.getSystemInfoSync();
// 胶囊按钮位置信息：
const menuButtonInfo = wx.getMenuButtonBoundingClientRect();
// iphone底部安全距离：
this.globalData.safeBottom =
  systemInfo.screenHeight - systemInfo.safeArea.bottom;
// 胶囊高度/宽度：
this.globalData.menuHeight = menuButtonInfo.height;
this.globalData.menuWidth = menuButtonInfo.width;
// 状态栏高度
this.globalData.statusBarHeight = systemInfo.statusBarHeight;
// 胶囊距右方间距
this.globalData.menuRight = systemInfo.screenWidth - menuButtonInfo.right;
// 胶囊距底部间距
this.globalData.menuBottom = menuButtonInfo.top - systemInfo.statusBarHeight;
// 胶囊距顶部位置
this.globalData.menuTop = menuButtonInfo.top;
```

### 场景五：路由跳转

1.跳转到 tabBar 页面，并关闭其他所有非 tabBar 页面: `wx.switchTab({url: ""});`

2.关闭所有页面，打开到应用内的某个页面:`wx.reLaunch({url: ""});`

3.关闭当前页面，跳转到应用内的某个页面。但是不允许跳转到 tabbar 页面:`wx.redirectTo({url: ""});`

4.保留当前页面，跳转到应用内的某个页面。但是不能跳到 tabbar 页面:`wx.navigateTo({url: ""});`

5.关闭当前页面，返回上一页面或多级页面:`wx.navigateBack({delta: 1});`

### 场景六：手机号快捷登录（微信开放能力）

查询[微信开放能力](https://developers.weixin.qq.com/miniprogram/dev/component/button.html#%E9%80%9A%E7%94%A8%E5%B1%9E%E6%80%A7)

```html
<van-button
  open-type="getPhoneNumber"
  type="primary"
  bindgetphonenumber="getPhonenumber"
  phone-number-no-quota-toast="{{false}}"
  round
  >手机号快捷登录</van-button
>
```

```javascript
   getPhonenumber(e) {
    const { errMsg } = e.detail;
    if (errMsg === "getPhoneNumber:fail user deny")
      return wx.showToast({
        title: "您已拒绝授权",
        icon: "error",
        duration: 2000,
      });

    if (errMsg === "getPhoneNumber:ok") {
      try {
        wx.showLoading();
        //...获取用户信息
          wx.switchTab({
            url: "/pages/index/index",
          });
        } finally {
        wx.hideLoading();
      }
    }
  },
```

### 场景七：`onShow()`获取页面传参

```javascript
 onShow() {
    const allPages = getCurrentPages(); //获取当前页面栈的实例；
    console.log(allPages[allPages.length - 1].options)
  },
```

### 场景八：上传图片

```html
<van-uploader
  multiple
  file-list="{{fileList}}"
  max-count="4"
  deletable="{{ true }}"
  preview-size="76"
  bind:after-read="afterRead"
  bind:delete="deleteImg"
  sizeType="['original']"
/>
```

```javascript
  afterRead: function (event) {
    try {
      wx.showLoading()
      const tempFiles = event.detail.file
      let that = this
      tempFiles.forEach(file => {
        wx.uploadFile({
          url: `${api.ApiRootUrl}${api.UploadImg}`,
          filePath: file.tempFilePath,
          name: 'files',
          header: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${wx.getStorageSync("token")}`,
          },
          success(res) {
            const data = JSON.parse(res.data)
            // 上传完成需要更新 fileList
            const newRes = data.Result.map(v => {
              return {
                url: v.FileUrl,
                FileID: v.FileID
              }
            })
            const list = that.data.fileList
            that.setData({
              fileList: [...list, ...newRes]
            });
          },
        });
      })
    } finally {
      wx.hideLoading()
    }
  },

  deleteImg(event) {
    let list = this.data.fileList.filter((_, i) => i !== event.detail.index)
    this.setData({
      fileList: list
    })
  },
```

### 场景九：自定义组件

#### 基础使用示例：/components/goods-cpn

json 文件

```json
{
  "component": true,
  "usingComponents": {}
}
```

js 文件

```js
Component({
  properties: {}, // props
  data: {},
  methods: {}
});
```

页面注册使用组件

```json
  "usingComponents": {
    "goods-cpn": "/components/goods-cpn/goods-cpn"
  }
```

#### 组件通信

cpn(wxml)：`<button class="info" bind:tap="onClick">组件按钮</button>`

cpn(js):

```js
Component({
  methods: {
    onClick() {
      this.triggerEvent('titleClick', '123');
    }
  }
});
```

page(wxml):`<section-info bind:titleClick="onTitleClick" />`

page(js):

```js
  onTitleClick(e) {
    console.log("组件传递出的自定义事件", e.detail);
  },
```

#### 组件样式隔离

```js
Component({
  options: {
    styleIsolation: 'isolated' // 完全隔离
  }
});
```

可选值：

- isolated 表示启用样式隔离，在自定义组件内外，使用 class 指定的样式将不会相互影响（一般情况下的默认值）；
- apply-shared 表示页面 wxss 样式将影响到自定义组件，但自定义组件 wxss 中指定的样式不会影响页面；
- shared 表示页面 wxss 样式将影响到自定义组件，自定义组件 wxss 中指定的样式也会影响页面和其他设置了 apply-shared 或 shared 的自定义组件。（这个选项在插件中不可用。）

如果 Component 用于构造页面 ，则默认值为 shared ，且还有以下几个额外的样式隔离选项可用：

- page-isolated 表示在这个页面禁用 app.wxss ，同时，页面的 wxss 不会影响到其他自定义组件；
- page-apply-shared 表示在这个页面禁用 app.wxss ，同时，页面 wxss 样式不会影响到其他自定义组件，但设为 shared 的自定义组件会影响到页面；
- page-shared 表示在这个页面禁用 app.wxss ，同时，页面 wxss 样式会影响到其他设为 apply-shared 或 shared 的自定义组件，也会受到设为 shared 的自定义组件的影响。

#### 外部样式类

```html
<custom-component my-class="red-text large-text" />

<custom-component class="my-class" />
```

```js
Component({
  externalClasses: ['my-class']
});
```

#### 组件局部引用组件所在页面的样式

`<view class="~blue-text" />`

#### 组件引用父组件的样式

`<view class="^red-text" />`

#### 实现 ：自定义组件内部的第一层节点能够响应 flex 布局或者样式由自定义组件本身完全决定

```js
Component({
  options: {
    virtualHost: true
  }
});
```

### 场景十：下拉刷新 / 上滑刷新 / 页面滚动

监听下拉刷新事件：`  onPullDownRefresh() {}`

停止下拉刷新事件:

```javascript
wx.stopPullDownRefresh({
  success: (res) => {
    console.log('success', res);
  },
  fail: (err) => {
    console.log('fail', err);
  }
});
```

上滑刷新配置项

` "onReachBottomDistance": 20` 设置触发事件距离底部的距离

监听事件

```javascript
  onReachBottom() {
    console.log('滚动到底部');
  }
```

页面滚动

```javascript
  onPageScroll() {
    console.log("scroll");
  },
```
