## 项目简介

> - 【项目整体功能】
>   - 用户主要来自于 puma 公司内部员工、员工亲友、艺人及球员。
>   - 根据人员角色权限展示不同的商品及功能权限，在常规购物商城功能开发的基础上，增加额度支付及分享功能，支持小程序由员工/艺人分享额度给亲友等非内部人员购物。
>   - 商品列表、商品分类、购物车、门店/线上下单、订单售后、开票申请、购物额度分享、领用及回收、用户信息维护等

## 开发记录

### 分包与分包预下载

**理解分包**

- 概念：把一个完整的小程序项目，按照需求划分为不同的自保，在构建时打包成不同的分包，用户在使用时按需进行加载
- 优点：可以优化小程序首次启动的下载时间，以及在多团队共同开发时可以更好的解耦协作

![](/images/subpackage.jpg)

- 组成：分包后，小程序项目由 1 个主包 + 多个分包组成
  - 主包：一般只包含项目的启动页面或 Tabbar 页面，以及所有分包都需要用到的一些公共资源
  * 分包：只包含和当前分包有关的页面和私有资源

* 体积限制：(目前)

  - 整体小程序所有分包大小不超过 16M（主包 + 所有分包）
  - 单个分包 / 主包不能超过 2M

* 加载规则：
  - 在小程序启动时，默认会下载主包并启动主包内页面
  - 当用户进入分包某个页面时，客户端会把对应分包下载下来，下载完成后在进行展示。非 tabBar 页面根据功能的不同，划分为不同的分包之后，进行按需下载。

- 打包原则

  - 小程序会按 subpackages 的配置进行分包，subpackage 之外的目录将被打包到主包中
  - 主包也可以有自己的 pages(即最外层的 pages 字段)
  - tabBar 页面必须在主包内
  - 主分包之间不能相互嵌套

- 引用原则

  - 主包无法引用分包内的私有资源
  - 分包之间不能相互引用私有资源
  - 分包可以引用主包内的公共资源

* 分包划分
  - **按照功能划分的的原则，将同一个功能下的页面和逻辑放置于同一个目录下，对于一些跨功能之间公共逻辑，将其放置于主包下**，这样可以确保在分包引用这部分功能时，这部分的逻辑一定存在。
  - 避免分包与分包之间引用上的耦合。因为分包的加载是由用户操作触发的，并不能确保某分包加载时，另外一个分包就一定存在，这个时候可能会导致 JS 逻辑异常的情况，例如报「"xxx.js" is not defined」这样的错误。
  - 一些公共用到的自定义组件，需要放在主包内。

- 分包配置示例

  > - root：分包的根目录
  > - pages：当前页面下，所有页面的相对路径
  > - name：分包别名
  > - independent：是否为独立分包

  ![](/images/menu.jpg)

**独立分包**

- 理解独立分包：独立分包是小程序中一种特殊类型的分包，可以独立于主包和其他分包运行。从独立分包中页面进入小程序时，不需要下载主包。当用户进入普通分包或主包内页面时，主包才会被下载。

- 引用原则：

  - 独立分包、普通分包、主包之间是相互隔绝的，不能互相引用彼此的资源
  - 主包无法引用独立分包内的私有资源
  - 独立分包之间，不能互相引用私有资源
  - 独立分包和普通分包之间，不能互相引用私有资源
  - 特别注意：独立分包中不能引用主包内的公共资源，而普通分包可以

- 注意事项

  > （1）关于 getApp()
  >
  > - 与普通分包不同，独立分包运行时，App 并不一定被注册，因此 getApp() 也不一定可以获得 App 对象：当用户从独立分包页面启动小程序时，主包不存在，App 也不存在，此时调用 getApp() 获取到的是 undefined。
  > - 当用户进入普通分包或主包内页面时，主包才会被下载，App 才会被注册。当用户是从普通分包或主包内页面跳转到独立分包页面时，主包已经存在，此时调用 getApp() 可以获取到真正的 App。由于这一限制，开发者无法通过 App 对象实现独立分包和小程序其他部分的全局变量共享。
  > - 为了在独立分包中满足这一需求，基础库 2.2.4 版本开始 getApp 支持 [allowDefault] 参数，在 App 未定义时返回一个默认实现。当主包加载，App 被注册时，默认实现中定义的属性会被覆盖合并到真正的 App 中。

  > （2）关于 App 生命周期
  >
  > - 当从独立分包启动小程序时，主包中 App 的 onLaunch 和首次 onShow 会在从独立分包页面首次进入主包或其他普通分包页面时调用。
  > - 由于独立分包中无法定义 App，小程序生命周期的监听可以使用 wx.onAppShow，wx.onAppHide 完成。App 上的其他事件可以使用 wx.onError，wx.onPageNotFound 监听。

**分包预下载**

- 理解：开发者可以预先配置某个页面可能会跳转到的分包（对于独立分包，也可以预下载主包），在进入小程序某个页面时，由基础库在后台自动预下载可能需要的分包。用户在进行页面跳转时，分包通常已经下载完成，不需要额外等待，可以有效提升进入后续分包页面时的启动速度。此外，考虑到用户的流量和存储空间，小程序也会对预下载的大小和网络进行一定的限制。

- 使用方法：开发者可以通过在 app.json 中增加 preloadRule 字段，控制进入某个页面时进行预下载的分包，并设置触发预下载的网络环境。
  ![](/images/preload.jpg)

### pdf 预览

> - 在事件中调用 wx.downloadFile 方法，指定要下载的 pdf 文件的 url 、存储路径和文件的重命名；
> - 下载完成后，再调用 wx.openDocument 方法打开该文件预览。在调用此方法时，需要把之前存储的文件路径传入。

```javascript
  viewProtocolPdf() {
    wx.showLoading({ mask: true });
    const filePath = `${wx.env.USER_DATA_PATH}/${重命名的文件名}.pdf`
    wx.downloadFile({
      url: '', // 文件路径
      filePath,
      success: ({ filePath }) => {
        wx.openDocument({
          filePath,
          complete: () => wx.hideLoading()
        })
      },
      fail: () => {
        wx.hideLoading()
      }
    })
  }
```

### 微信支付相关

```javascript
const util = require('../utils/util.js');
const api = require('../config/api.js');
function payOrder(orderId) {
  return new Promise(function (resolve, reject) {
    util
      .request(
        api.MiniProgramPay,
        {
          OutTradeNo: orderId
        },
        'POST'
      )
      .then((res) => {
        if (res.Code === '200') {
          const payParam = JSON.parse(res.Result.parameter);
          wx.requestPayment({
            ...payParam,
            success: function (res) {
              resolve(res);
            },
            fail: function (res) {
              reject(res);
            },
            complete: function (res) {
              reject(res);
            }
          });
        } else {
          reject(res);
        }
      });
  });
}
```

### token 无感刷新

参考 [ token 无感刷新](https://blog.csdn.net/Cipher_Y/article/details/134318393)

### 内嵌 H5 页面

web-view 组件功能描述：承载网页的容器，会自动铺满整个小程序页面。

小程序端可通过 bindmessage 函数接收 h5 传递的数据
网页向小程序 postMessage 时，会在以下特定时机触发并收到消息：**小程序后退、组件销毁、分享、复制链接**（2.31.1）。`e.detail = { data }`，data 是多次 postMessage 的参数组成的数组。

```html
<web-view src="{{url}}" bindmessage="receiveMsg"></web-view>
```

```javascript
receiveMessage(e){
    console.log(e.detail)//接收H5传过来的数据
}
```

H5 页面通过 postMessage 发送数据

```javascript
wx.miniProgram.postMessage({ data: { foo: 'bar' } });
```

### 商品列表缩略图

基础功能，在此做个简单记录

- 缩略图可滑动
- 切换缩略图，商品大图同步切换
- 当 sku 超过三件时，点击右侧 icon 左移缩略图

![](/images/list.png)

#### scroll-view 组件功能描述

可滚动视图区域。使用竖向滚动时，需要给 scroll-view 一个固定高度，通过 WXSS 设置 height。组件属性的长度单位默认为 px，2.4.0 起支持传入单位(rpx/px)。

```html
<view class="scroll-img">
  <!-- 缩略图部分 -->
  <scroll-view
    scroll-x
    show-scrollbar="{{false}}"
    enhanced="{{true}}"
    enable-flex
    class="scroll-view"
    scroll-left="{{item.scrollLeft}}"
    data-checkItem="{{index}}"
    bindscroll="scroll"
    scroll-with-animation
  >
    <image
      wx:for="{{item.imgList}}"
      wx:for-item="img"
      wx:for-index="i"
      wx:key="i"
      src="{{img+'&imageMogr2/thumbnail/40*40'}}"
      class="gallery-img {{item.checkedItem===i?'selected':''}}"
      data-checkItem="{{index}}"
      data-checkId="{{i}}"
      catch:tap="changeImage"
      mode="widthFix"
    />
  </scroll-view>
  <!-- 更多按钮 -->
  <image
    wx:if="{{item.imgList.length>3}}"
    src="/images/svg/goodsMore.svg"
    mode=""
    class="more"
    data-checkItem="{{index}}"
    catch:tap="viewNextImg"
  />
</view>
```

功能逻辑实现

```javascript
// 缩略图滚动事件--设置横向滚动条位置
  scroll(e) {
    const list = this.data.goodsList;
    list[e.currentTarget.dataset.checkitem].scrollLeft = e.detail.scrollLeft;
  },

// 切换选中缩略图
  changeImage(e) {
    const { checkitem, checkid } = e.currentTarget.dataset;
    const list = this.data.goodsList;

    list.forEach((v, index) => {
      if (checkitem === index) v.checkedItem = checkid;
    });

    this.setData({
      goodsList: list,
    });
  },

// 点击更多按钮，缩略图左移
 viewNextImg(e) {
    const list = this.data.goodsList;
    list[e.currentTarget.dataset.checkitem].scrollLeft += 40;
    this.setData({
      goodsList: list,
    });
  },

```

缩略图样式：

```css
.scroll-img {
  height: 112rpx;
  display: flex;
  align-items: center;
  flex-wrap: nowrap;
  padding: 0 10rpx;
}

.scroll-view {
  white-space: nowrap;
  width: calc(100% - 48rpx);
}

.gallery-img {
  width: 40px;
  height: 40px;
  margin-right: 16rpx;
}

.scroll-img .selected {
  border: 1px solid #cccccc;
  border-radius: 8rpx;
}

.more {
  width: 48rpx;
  height: 80rpx;
}

.cate-item .goods-box {
  width: calc(50% - 6rpx);
  height: 644rpx;
  margin: 0 10rpx 10rpx 0;
  background-color: #ffffff;
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}
```
