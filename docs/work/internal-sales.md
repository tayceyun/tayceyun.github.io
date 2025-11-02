## 项目简介

> - 【项目整体功能】
>   - 用户主要来自于 puma 公司内部员工、员工亲友、艺人及球员。
>   - 根据人员角色权限展示不同的商品及功能权限，在常规购物商城功能开发的基础上，增加额度支付及分享功能，支持小程序由员工/艺人分享额度给亲友等非内部人员购物。
>   - 商品列表、商品分类、购物车、门店/线上下单、订单售后、开票申请、购物额度分享、领用及回收、用户信息维护等

## 记录

### 商品列表缩略图

基础功能，在此做个简单记录

- 缩略图可滑动
- 切换缩略图，商品大图同步切换
- 当 sku 超过三件时，点击右侧 icon 左移缩略图

![](/img/images/list.png)

#### scroll-view 组件功能描述

可滚动视图区域。使用竖向滚动时，需要给 scroll-view 一个固定高度，通过 WXSS 设置 height。组件属性的长度单位默认为 px，2.4.0 起支持传入单位(rpx/px)。

```html
<view class="scroll-img">
  <!-- 缩略图部分 -->
  <scroll-view
    scroll-x
    show-scrollbar="`{{false}`}"
    enhanced="`{{true}`}"
    enable-flex
    class="scroll-view"
    scroll-left="`{{item.scrollLeft}`}"
    data-checkItem="`{{index}`}"
    bindscroll="scroll"
    scroll-with-animation
  >
    <image
      wx:for="`{{item.imgList}`}"
      wx:for-item="img"
      wx:for-index="i"
      wx:key="i"
      src="`{{img+'&imageMogr2/thumbnail/40*40'}`}"
      class="gallery-img `{{item.checkedItem===i?'selected':''}`}"
      data-checkItem="`{{index}`}"
      data-checkId="`{{i}`}"
      catch:tap="changeImage"
      mode="widthFix"
    />
  </scroll-view>
  <!-- 更多按钮 -->
  <image
    wx:if="`{{item.imgList.length>3}`}"
    src="/images/svg/goodsMore.svg"
    mode=""
    class="more"
    data-checkItem="`{{index}`}"
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
    const `{ checkitem, checkid }` = e.currentTarget.dataset;
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
