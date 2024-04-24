## 浏览器

### 了解多进程浏览器

- 进程之间是**相互隔离**的 ，当一个页面或者插件崩溃时，影响到的仅仅是当前的页面进程或者插件进程，并不会影响到浏览器和其他页面，从而解决了历史单进程浏览器中页面或者插件的崩溃会导致整个浏览器崩溃的问题

- Chrome 把插件进程和渲染进程锁在[沙箱](https://baike.baidu.com/item/Sandbox/9280944?fr=aladdin)里面，这样即使在渲染进程或者插件进程里面执行了恶意程序，恶意程序也无法突破沙箱去获取系统权限。

### ❓chrome 浏览器包含哪些进程

- **浏览器进程** ：主要负责界面显示、用户交互、子进程管理，同时提供存储等功能。

- **渲染进程**：核心任务是将 HTML、CSS 和 JavaScript 转换为用户可以与之交互的网页，排版引擎 Blink 和 JavaScript 引擎 V8 都是运行在该进程中，默认情况下， **Chrome 会为每个 Tab 标签创建一个渲染进程**。出于安全考虑，**渲染进程都是运行在沙箱模式下**。

- **GPU 进程**：Chrome 在其多进程架构上引入了 GPU 进程，网页、Chrome 的 UI 界面都采用 GPU 来绘制。

- **网络进程**：主要负责页面的网络资源加载。

- **插件进程**：主要是负责插件的运行，因插件易崩溃，所以需要通过插件进程来隔离，以保证插件进程崩溃不会对浏览器和页面造成影响。

### 浏览器内核中线程之间的关系

- GUI （Graphical User Interface）渲染线程和 JS 引擎线程互斥。js 是可以操作 DOM 的，如果在修改这些元素的同时渲染页面(js 线程和 ui 线程 同时运行)，那么渲染线程前后获得的元素数据可能就不一致了。
- js 如果执行时间过长就会阻塞页面加载

### js 单线程

Web Worker 的作用，就是为 JavaScript 创造多线程环境，允许主线程创建 Worker 线程，将一些任务分配给后者运行。但是子线程完全受主线程控制，且不得操作 DOM。一般使用 Web Worker 的场景是代码中有很多计算密集型或高延迟的任务，可以考虑分配给 Worker 线程。

### ❓chrome 打开一个页面需要启动多少进程

打开 1 个页面至少需要 1 个网络进程（页面网络资源加载）、1 个浏览器进程（界面显示，用户交互，子进程管理等功能）、1 个 GPU 进程（UI 界面绘制）以及 1 个 渲染进程（v8 引擎和排版引擎 Blink），

### ❓ 浏览器如何渲染网页

![](/images/chrome/渲染网页.png)

#### 1. 处理 HTML 并构建 DOM 树

> 当解析器到达 script 标签的时候，发生下面四件事情
>
> 1. html 解析器停止解析
>
> 2. 如果是外部脚本，就从外部网络获取脚本代码
>
> 3. 将控制权交给 js 引擎，执行 js 代码
>
> 4. 恢复 html 解析器的控制权

❓script 标签是阻塞解析的，如何优化

1️⃣ 将脚本放在网页尾部会加速代码渲染。

2️⃣**defer**（页面解析完成（DOMContentLoaded 事件触发之前）之后按序依次执行） 和 **async** 属性（脚本下载完成后立即执行，顺序不定）也能有助于加载外部脚本。
defer 使得;

#### 2. 处理 CSS 构建 CSSOM 树

⚠️ 在构建 CSSOM 树时会阻塞渲染，直至 CSSOM 树构建完成。并且构建 CSSOM 树是一个十分消耗性能的过程，所以应该尽量保证层级扁平，减少过度层叠，越是具体的 CSS 选择器，执行速度越慢

#### 3. 将 DOM 与 CSSOM 合并成一个渲染树

![](/images/chrome/render.png)

#### 4. 根据渲染树来布局，计算每个节点的位置

#### 5. 调用 GPU 绘制，合成图层，显示在屏幕上

一般来说，可以把普通文档流看成一个图层。特定的属性可以生成一个新的图层。不同的图层渲染互不影响，所以对于某些频繁需要渲染的建议单独生成一个新图层，提高性能。但也不能生成过多的图层，会引起反作用。

**页面重新渲染**通常需要重复之前的第四步骤(重新生成布局)+第五步骤(重新绘制) 或者 只有第五步骤(重新绘制)

### ❓Load 和 DOMContentLoaded 区别

- Load 事件触发代表页面中的 DOM ， CSS ， JS ，图片已经全部加载完毕。
- DOMContentLoaded 事件触发代表初始的 HTML 被完全加载和解析，不需要等待 CSS ， JS ，图片加载。

### ❓ 重绘和重排的区别

重绘是当节点需要更改外观而不会影响布局的，比如改变 color 就叫称为重绘

重排是布局或者几何属性需要改变。

例如：添加或者删除可见的 DOM 元素; 元素尺寸改变——边距、填充、边框、宽度和高度; 内容变化，比如用户在 input 框中输入文字; 浏览器窗口尺寸改变——resize 事件发生时 计算 offsetWidth 和 offsetHeight 属性等等

重排必定发生重绘，重绘不一定引发重排。

#### 如何减少重绘和重排

- 使用 `visibility` 替换 `display:none`

- 尽量避免使用 table 布局，table 布局中一个小改动很容易造成 table 的重新布局

- css 选择符自右向左匹配查找，避免 dom 深度过深

## 缓存机制

### http 缓存的优点

- 减少了冗余的数据传输，减少网费
- 减少服务器端的压力
- Web 缓存能够减少延迟与网络阻塞，进而减少显示某个资源所用的时间
- 加快客户端加载网页的速度

## http 缓存执行过程

⚠️ 强缓存（`Cache-Control` / `Expires`）优先级高于协商缓存（`Last-Modified` / `If-Modified-Since` 或 `ETag` / `If-None-Match`）

⚠️ 在协商缓存中，`ETag`优先级比`Last-Modified`高

⚠️ 当 ctrl+f5 强制刷新网页时，直接从服务器加载，跳过强缓存和协商缓存

⚠️ 当 f5 刷新网页时，跳过强缓存，但是会检查协商缓存

### 执行过程

> 第一次浏览器发送请求给服务器时，此时浏览器还没有本地缓存副本，服务器返回资源给浏览器，响应码是 200 OK ，浏览器收到资源后，把**资源和对应的响应头**一起缓存下来。
>
> 第二次浏览器准备发送请求给服务器时，浏览器会先检查上一次服务端返回的响应头信息中的`Cache-Control`，它的值是一个相对值，单位为秒，表示资源在客户端缓存的最大有效期，过期时间为第一次请求的时间减去`Cache-Control`的值，过期时间跟当前的请求时间比较，如果本地缓存资源没过期，那么命中缓存，不再请求服务器**（强缓存）**。
>
> 如果没有命中，浏览器就会把请求发送给服务器，进入[缓存协商](#缓存协商)阶段。

#### `Cache-Control`和`Expires`

##### `Cache-Control`常见值

![](/images/chrome/cache.png)

##### `Expires`

是一个绝对时间。时间格式是如 Mon,10 Jun 2020 10:10:10 GMT，只要发送请求时间是在`Expires`之前，那么本地缓存始终有效，否则就会去服务器发送请求获取新的资源。如果同时出现`Cache-Control:max-age`和`Expires` ，`max-age`优先级更高。

‼️ 两者也可以组合使用：

```js
Cache-Control: public
Expires: Wed, Jan 10 2018 00:27:04 GMT
```

<a name="缓存协商"></a>

### 缓存协商

❓ 什么情况会进入缓存协商阶段

当第一次请求时服务器返回的响应头中存在以下情况时：

1️⃣ 没有`Cache-Control`和`Expires`

2️⃣`Cache-Control`和`Expires`已过期

3️⃣`Cache-Control`设置为`no-cache`

浏览器第二次请求时就会与服务器进行协商，询问浏览器中的缓存资源是不是旧版本，需不需要更新。

服务器会进行判断，如果缓存和服务端资源的最新版本是一致的，那么就无需再次下载该资源，服务端直接返回 304 Not Modified 状态码。

如果服务器发现浏览器中的缓存已经是旧版本了， 那么服务器就会把最新资源的完整内容返回给浏览器，状态码就是 200 Ok。

那么服务端是根据什么来判断浏览器的缓存是不是最新的呢?

【协商缓存】其实是根据 HTTP 的另外两组头信息，分别是：`Last-Modified` / `If-Modified-Since` 与 `ETag` / `If-None-Match`

#### `Last-Modified` / `If-Modified-Since`

**根据资源修改时间判断资源有无更新**

浏览器第一次请求资源时，服务器会把资源的**最新修改时间**(Last-Modified)放在响应头中返回给浏览器；

第二次请求时，浏览器就会把上一次服务器返回的修改时间放在请求头(If-Modified-Since)发送给服务器，服务器就会拿这个时间跟服务器上的资源的最新修改时间进行对比；

服务端会根据请求头`If-Modified-Since`的值，判断相关资源是否有变化，如果没有，则返回 304 Not Modified，并且不返回资源内容，浏览器使用资源缓存值;否则正常返回资源内容，且更新(Last-Modified)响应头内容。

** 以上方式存在的问题 🙋**

- 精度问题：`Last-Modified`的时间精度为秒，如果在 1 秒内发生修改，那么缓存判断可能会失效;

- 准度问题：存在一种情况，例如一个文件被修改，然后又被还原，内容并没有发生变化，在这种情况下，浏览器的缓存还可以继续使用，但因为修改时间发生变化，也会重新返回重复的内容。

**根据资源内容判断有无更新(基于资源的内容的摘要信息(比如 MD5 hash-信息摘要算法 )来判断)**

浏览器第一次请求资源，服务端在返响应头中加入 `ETag` 字段， `ETag` 字段值为该资源的哈希值。

浏览器发送第二次请求时，会把第一次的响应头信息 `ETag` 的值放在 `If-None-Match` 的请求头中发送到服务器，服务器将请求头中`If-None-Match`字段值和最新的资源的哈希值对比，如果相等则返回 304 Not Modified，否则内容有更新，将最新的资源连同最新的摘要信息返回。

用 `ETag` 的好处是如果因为某种原因到时资源的修改时间没改变，那么用 `ETag` 就能区分资源是不是有被更新。

** 以上方式存在的问题 🙋**

- 计算成本：生成哈希值相对于读取文件修改时间而言是一个开销比较大的操作，尤其是对于大文件而言。如果要精确计算则需读取完整的文件内容，如果从性能方面考虑，只读取文件部分内容又容易判断出错。

- 计算误差：HTTP 并没有规定哈希值的计算方法，所以不同服务端可能会采用不同的哈希值计算方式。这样带来的问题是，同一个资源在两台服务端产生的 `Etag` 可能是不相同的，所以对于使用服务器集群来处理请求的网站来说，使用 `Etag` 的缓存命中率会有所降低。

## 缓存位置

- `Service Worker Cache`：离线缓存
- `Memory Cache`：内存缓存 （效率最快，当渲染进程结束后，内存缓存释放）
- `Disk Cache`：磁盘缓存（存取效率比内存缓存慢，存储容量大，存储时间长）
- `Push Cache`：推送缓存

## cookie

`same-site`：规定浏览器不能在跨域请求中携带 cookie，减少 csrf 攻击

![](/images/chrome/cookie.png)

## 跨域

❓webpack 实现反向代理

1️⃣config 文件

```js
  '/api': {
    target: 'http://www.example.com', // your target host
       changeOrigin: true, // needed for virtual hosted sites
       pathRewrite: {
         '^/api': ''  // rewrite path
       }
},
```

2️⃣http-proxy-middleware 插件对 api 请求地址代理

```js
const express = require('express');
const proxy = require('http-proxy-middleware');
// proxy api requests
const exampleProxy = proxy(options); // 这里的 options 就是 webpack 里面的 proxy 选项对应的每个选项
// mount `exampleProxy` in web server
const app = express();
app.use('/api', exampleProxy);
app.listen(3000);
```

3️⃣nginx 把允许跨域的源地址添加到报头里面即可

## XSS 和 CSRF

### XSS（Cross Site Scripting）跨站脚本攻击

理解：攻击者想尽办法将可执行的代码注入到网页中

常见 xss 攻击举例：

- 窃取网页浏览中的 cookie 值,获取用户敏感信息
- 劫持流量实现恶意跳转`<script>window.location.href="http://www.baidu.com";</script>`
- 利用一些可被攻击的域或其它的域信任的特点，以受信任来源的身份请求一些平时不被允许的操作

❓ 如何防止 xss 攻击

- 输入检查
- 输出检查
- 转义
- 设置白名单/黑名单过滤
- 设置 http only 属性，则客户端的脚本就不能获取到 cookie 信息

#### CSP(Content Security Policy)

CSP 是一种内容安全策略，它用于指示浏览器如何处理页面上的内容，以减少跨站脚本（XSS）攻击的风险。

##### 实现方式

1.meta 标签设置 CSP

```html
<meta
  http-equiv="Content-Security-Policy"
  content="default-src 'self'; script-src 'self' 'unsafe-inline' https://api.example.com"
/>
```

2.使用 HTTP 响应头设置 CSP

```js
Content-Security-Policy: script-src 'self' // 只允许加载本站资源
```

### CSRF（Cross-site request forgery）跨站请求伪造

理解：攻击者盗用了你的身份，以你的名义发送恶意请求。CSRF 的关键点在于，**跨域请求时会自动携带第三方网站的 cookie**

#### 原理

1.用户 C 打开浏览器，访问受信任网站 A，输入用户名和密码请求登录网站 A;

2.在用户信息通过验证后，网站 A 产生 Cookie 信息并返回给浏览器，此时用户登录网站 A 成功，可以正常发送请求到网站 A;

3.用户未退出网站 A 之前，在同一浏览器中，打开一个 TAB 页访问网站 B;

4.网站 B 接收到用户请求后，返回一些攻击性代码，并发出一个请求要求访问第三方站点 A;

5.浏览器在接收到这些攻击性代码后，根据网站 B 的请求，在用户不知情的情况下携带 Cookie 信息，向网站 A 发出请求。网站 A 并不知道该请求其实是由 B 发起的，所以会根据用户 C 的 Cookie 信息以 C 的权限处理该请求，导致来自网站 B 的恶意代码被执行。

❓ 如何防止 csrf 攻击

- 验证码
- Cookie 设置 SameSite 属性
  SameSite 属性的值：
  - None： 任何情况下都会向第三方网站请求发送 Cookie
  - ⭐️Lax：【目前主流浏览器的默认值】只有导航到第三方网站的 Get 链接会发送 Cookie。而跨域的图片 iframe、「fetch 请求，form 表单都不会发送 Cookie
  - Strict：任何情况下都不会向第三方网站请求发送 Cookie
- Token：在请求头中带上 Authorization 字段，服务器验证 Token 是否合法
- Referer check：HTTP 请求头中验证`Referer`字段，`Referer`字段记录了该 HTTP 请求的来源地址。Origin 属性只包含了域名信息，没有包含具体的 URL 路径