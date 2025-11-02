---
sidebar: auto
tags:
  - webpack
---

## 概念理解

- entry:入口。webpack 是基于模块的，使用 webpack 首先需要指定模块解析入口(entry)，webpack 从入口开始根据模块间依赖关系递归解析和处理所有资源文件。
- output:输出。源代码经过 webpack 处理之后的最终产物。
- loader:模块转换器。本质就是一个函数，在该函数中对接收到的内容进行转换，返回转换后的结果。因为 Webpack 只认识 JavaScript，所以 Loader 就成了翻译官，对其他类型的资源进行转译的预处理工作。
- plugin :扩展插件。基于事件流框架 Tapable，插件可以扩展 Webpack 的功能，在 Webpack 运行的生命周期中会广播出许多事件，Plugin 可以监听这些事件，在合适的时机通过 Webpack 提供的 API 改变输出结果。
- module:模块。除了 js 范畴内的 es module、commonJs、AMD 等，css @import、url(...)、图片、字体等在 webpack 中都被视为模块。

### 术语

- module:指在模块化编程中我们把应用程序分割成的独立功能的代码模块

- chunk:指模块间按照引用关系组合成的代码块，一个 chunk 中可以包含多个 module
- chunk group :指通过配置入口点( entry point )区分的块组，一个 chunk group 中可包含一到多个 chunk
- bundling:webpack 打包的过程
- asset/bundle :打包产物

### 简化打包原理

- 一切源代码文件均可通过各种 Loader 转换为 JS 模块 （module）， 模块之间可以互相引用。
- webpack 通过入口点( entry point )递归处理各模块引用关系，最后输出为一个或多个产物包 js(bundle)文件。
- 每一个入口点都是一个块组( chunk group )，在不考虑分包的情况下，一个 chunk group 中只有一个 chunk , 该 chunk 包含递归分析后的所有模块。每一个 chunk 都有对应的一个打包后的输出文件( asset/bundle)

### 打包流程

![](/img/images/resource/打包流程.png)

#### 简版

- Webpack CLI 启动打包流程;
- 载入 Webpack 核心模块，创建 Compiler 对象;
- 使用 Compiler 对象开始编译整个项目;
- 从入口文件开始，解析模块依赖，形成依赖关系树;
- 递归依赖树，将每个模块交给对应的 Loader 处理;
- 合并 Loader 处理完的结果，将打包结果输出到 dist 目录。

#### 构建流程核心概念

构建流程核心概念:

- Tapable:一个基于发布订阅的事件流工具类 **Compiler 和 Compilation 对象都继承于 Tapable**。
- compiler :webpack 实例，在**编译初始化阶段**被创建，全局唯一，把控整个 webpack 打包的构建流程。包含完整配置信息、 loaders、plugins 以及各种工具方法
- compilation :编译实例，在 watch 模式下每一次文件变更触发的重新编译都会生成**新的 compilation 对象**，开始一次新的编译。包含了当前编译的模块 module,编译生成的资源，变化的文件,依赖的状态等。同时通过它提供的 api，可以监听每次编译过程中触发的事件钩子。
- 而每个模块间的依赖关系，则依赖于 AST 语法树。每个模块文件在通过 Loader 解析完成之后，会通过 acorn 库生成模块代码的 AST 语法树，通过语法树就可以分析这个模块是否还有依赖的模块，进而继续循环执行下一个模块的编译解析。

最终 webpack 打包出来的 bundle 文件是一个 IIFE 的执行函数。

## 常见 loader

Webpack 会按顺序链式调用每个 Loader;遵循 Webpack 制定的设计规则和结构，输入与输出均为字符串，各个 Loader 完全独立，即插即用。

- file-loader :加载文件资源，如 字体/图片 等，具有移动/复制/命名等功能
- url-loader:通常用于加载图片，可以将小图片直接转换为 Date Url，减少请求
- babel-loader :加载 is/jsx 文件，将 ES6/ES7 代码转换成 ES5，处理兼容性问题;
- ts-loader:加载 ts/tsx 文件，编译 TypeScript
- style-loader:将 css 代码以 style 标签的形式插入到 html 中;
- css-loader:分析@import 和 url()，引用 css 文件与对应的资源
- postcss-loader:用于 css 的兼容性处理，具有众多功能，例如 添加前缀，单位转换 等;
- less-loader / sass-loader :css 预处理器，在 css 中新增了许多语法，提高了开发效率

## plugin

在编译的整个生命周期中，Webpack 会触发许多事件钩子，Plugin 可以监听这些事件，根据需求在相应的时间点对打包内容进行定向的修改。

plugin 示例

```js
class Plugin {
  // 注册插件时，会调用 apply 方法
  // apply 方法接收 compiler 对象
  // 通过 compiler 上提供的 Api，可以对事件进行监听，执行相应的操作
  apply(compiler) {
    // compilation 是监听每次编译循环
    // 每次文件变化，都会生成新的 compilation 对象并触发该事件
    compiler.plugin('compilation', function (compilation) `{}`);
  }
}
```

注册插件

```js
// webpack.config.js
module.export = {
  plugins: [new Plugin(options)]
};
```

常用的 Plugin

- UglifyJsPlugin:压缩、混淆代码（在生产环境中删除不可能被执行的代码）
- CommonsChunkPlugin:代码分割
- ProvidePlugin: 自动加载模块
- DefinePlugin:定义全局变量
- html-webpack-plugin:自动创建一个 HTML 文件，并把打包好的 JS 插入到 HTML 文件中
- extract-text-webpack-plugin/mini-css-extract-plugin: 抽离 CSS 代码，放到一个单独的文件中;
- optimize-css-assets-webpack-plugin: Css 代码去重，压缩 css
- webpack-bundle-analyzer: 代码分析
- compression-webpack-plugin:使用 gzip 压缩 js 和 css
- happypack: 使用多进程，加速代码构建
- EnvironmentPlugin: 定义环境变量
- clean-webpack-plugin 在每一次打包之前，删除整个输出文件夹下所有的内容

## loader 和 plugin 的区别

- loader 就是模块转换化，或叫加载器。不同的文件，需要不同的 loader 来处 理。
- plugin 是插件，可以参与到整个 webpack 打包的流程中，不同的插件，在合适的时机，可以做不同的事件。

## 热更新

![](/img/images/webpack/hmr.png)

## proxy

接收客户端发送的请求后转发给其他服务器，其目的是为了便于开发者在开发模式下解决跨域问题(浏览器安全策略限制)
想要实现代理首先需要一个中间服务器， webpack 中提供服务器的工具为 webpack-dev-server

### 属性

- target:表示的是代理到的目标地址
- pathRewrite:默认情况下， /api 也会被写入到 URL 中，如果希望删除，可以使用 pathRewrite
- secure:默认情况下不接收转发到 https 的服务器上，如果希望支持，可以设置为 false
- changeOrigin：它表示是否更新代理后请求的 headers 中 host 地址

```js
const path = require('path');
module.exports = {
  devServer: {
    contentBase: path.join(__dirname, 'dist'),
    compress: true,
    port: 9000,
    proxy: {
      '/api': {
        target: 'https://api.github.com'
      }
    }
  }
};
```

### 工作原理

proxy 工作原理实质上是利用 http-proxy-middleware 这个 http 代理中间件，实现请求转发给其他服务器。

通过设置 webpack proxy 实现代理请求后，相当于浏览器与服务端中添加一个代理者。当本地发送请求的时候，**代理服务器**响应请求，并将请求转发到目标服务器，目标服务器响应数据后再将数据返回给代理服务器，最终再由代理服务器将数据响应给本地。在代理服务器传递数据给本地浏览器的过程中，两者同源，并不存在跨域行为，这时候浏览器就能正常接收数据

```js
const express = require('express');
const proxy = require('http-proxy-middleware');
const app = express();
app.use(
  '/api',
  proxy(`{ target: 'http://www.example.org', changeOrigin: true }`)
);
app.listen(3000);
// http://localhost:3000/api/foo/bar -> http://www.example.org/api/foo/bar
```

## babel 原理

babel 编译的三个阶段:parsing、 transforming、generating.

### babel 转译的具体过程

ES6 代码输入 ==》 babylon 进行解析 ==》 得到 AST ==》 plugin 用 babel-traverse 对 AST 树进行遍历转译 ==》 得到新的 AST 树 ==》 用 babel-generator 通过 AST 树生成 ES5 代码

限制：babel 只是转译新标准引入的语法，比如 ES6 的箭头函数转译成 ES5 的函数；而新标准引入的新的原生对象，部分原生对象新增的原型方法，新增的 API 等（如 Proxy、Set 等），这些 babel 是**不会转译**的。需要用户自行引入 **polyfill** 来解决

## 分包

### 分包的适用场景

默认情况下，Webpack 会将所有代码构建成一个单独的包。包体积逐步增长可能会导致应用的响应耗时越来越长。将所有资源打包成一个文件的方式存在两个弊端：

- 资源冗余：客户端必须等待整个应用的代码包都加载完毕才能启动运行，但可能用户当下访问的内容只需要使用其中一部分代码
- 缓存失效：将所有资源达成一个包后，即使只是修改了一个字符，客户端都需要重新下载整个代码包，缓存命中率极低。

### 代码分离（Code Splitting）

- 代码分离到不同的 bundle 中，之后我们可以按需加载，或者并行加载这些文件； 比如默认情况下，所有的 JavaScript 代码（业务代码、第三方依赖、暂时没有用到的模块）在首页全部都加载， 就会影响首页的加载速度；
- 代码分离可以分出出更小的 bundle，以及控制资源加载优先级，提供代码的加载性能；

例如 node_modules 中的资源通常变动较少，可以抽成一个独立的包。

### 代码分离的方式

- 入口起点：使用 entry 配置手动分离代码；

配置多入口 & 共享文件共同的依赖库

```js
const path = require('path');
module.exports = {
  entry: {
    main: `{ import: './src/main.js', dependOn: 'shared' }`, // 第一个入口起点
    app: `{ import: './src/app.js', dependOn: 'shared' }`, // 第二个入口起点
    shared: ['dayjs', 'lodash'] // 共享的库
  },
  output: {
    filename: '[name].bundle.js', // 使用[name]占位符将生成的文件名与入口起点名称对应
    path: path.resolve(__dirname, 'dist')
  }
};
```

- 防止重复：使用 Entry Dependencies 或者 SplitChunksPlugin 去重和分离代码；

  SplitChunksPlugin 插件可以将应用程序中共享的代码拆分成单独的块，以便将其从应用程序代码中分离出来，从而提高性能和加载速度。

```js
const `{ resolve }` = require('path');

module.exports = {
  entry: './src/main.js',
  output: {
    filename: 'bundle.js',
    path: resolve(__dirname, 'build')
  },
  optimization: {
    splitChunks: {
	  // async：拆分异步导入模块
	  // initial：拆分同步导入模块
	  // all:拆分所有模块
      chunks: 'async',
	  // 拆分包的最小尺寸
      minSize: 20000,
      minRemainingSize: 0,
	  // 至少被引入次数
      minChunks: 1,
	  // 最大的初始化请求数量
      maxAsyncRequests: 30,
      maxInitialRequests: 30,
      enforceSizeThreshold: 50000,
	  // 对拆分的包进行分组
      cacheGroups: {
        defaultVendors: {
		  // 匹配符合规则的包
          test: /[\\/]node_modules[\\/]/,
		  // 一个模块可以属于多个cacheGroups。优化将优先考虑具有更高 priority（优先级）的cacheGroups。默认组的优先级为负，自定义组的默认值为 0;
          priority: -10,
		  // 拆分包的name属性
          name:'',
		  // 拆分包的名称
          fileName: 'vender_[id]_[name].js'， //打包之后的文件名
		  // 如果当前 chunk 包含已从主 bundle 中拆分出的模块，则它将被重用，而不是生成新的模块。这可能会影响 chunk 的结果文件名;
          reuseExistingChunk: true,
        },
        default: {
          minChunks: 2,
          priority: -20,
          reuseExistingChunk: true,
        },
      },
    },

  },
};
```

- 动态导入（ES6 的 import()语法）：通过模块的内联函数调用来分离代码

当代码中存在不确定会被使用的模块时，最佳做法是将其分离为一个独立的 JavaScript 文件。这样可以确保在不需要该模块时，浏览器不会加载或处理该文件的 JavaScript 代码。

动态导入也是路由懒加载的原理，都是为了优化性能而延迟加载资源。

```js
homeBtn.addEventListener('click', () => {
  import(/* webpackChunkName: "home" */ './views/home.js'); // 魔法注释
});
```

### 配置打包文件名称 `output.chunkFilename`

```js
const `{ resolve }` = require('path');

module.exports = {
  entry: './src/main.js',
  output: {
    filename: 'bundle.js',
    path: resolve(__dirname, 'build'),
    chunkFilename: 'chunk_[name]_[id].js'
  }
};
```

### 分包的预加载(preload) & 预获取(prefetch)

- preload

preload 是告诉浏览器预先请求当前页面需要的资源，通常是当前页面渲染所必需的关键资源，如字体、样式表或脚本。它会在**当前页面加载时立即开始加载**，而不需要等待解析完 js 或者 css 之后再去加载对应的资源。与浏览器的空闲状态不相关。因此，preload **可能会影响初始页面加载性能**，因为它可以竞争主要资源的带宽。

`import(/* webpackPreload: true */ './view/about');`

- prefetch

在浏览器空闲时，即浏览器已经加载主要资源并且有剩余带宽时开始加载。这意味着 prefetch **不会影响初始页面加载时间**，因为它是在**后台加载**的。通常用于加载将来可能需要的资源，例如懒加载的代码块或其他不太紧急的资源。

`import(/* webpackPrefetch: true */ './view/home')`

### runtime 代码的分包（runtimeChunk）

配置 runtime 相关的代码是否抽取到一个单独的 chunk 中：

- runtime 相关的代码指的是在运行环境中，对模块进行解析、加载、模块信息相关的代码；
- 例如 component、bar 两个通过 import 函数相关的代码加载，就是通过 runtime 代码完成的；

runtime 抽离出来后，有利于浏览器的缓存策略：

- 例如修改了业务代码（main），那么 runtime 和 component、bar 的 chunk 是不需要重新加载的；
- 例如修改了 component、bar 的代码，那么 main 中的代码是不需要重新加载的；

```js
const `{ resolve }` = require('path');

module.exports = {
  entry: './src/main.js',
  output: {
    filename: 'bundle.js',
    path: resolve(__dirname, 'build')
  },
  optimization: {
    runtimeChunk: 'true/multiple' //针对每个入口打包一个runtime文件
    runtimeChunk: 'single'  //打包一个runtime文件
    runtimeChunk: {
      name: function(entrypoint) {
        return `my-$`{entrypoint.name}`` // 决定runtimeChunk的名称
      }
    }

  },
};
```

### css 文件打包

常规的配置`css-loader`和`style-loader`,最终会把 css 注入到页面中。

```js
const `{ resolve }` = require('path');

module.exports = {
  entry: './src/main.js',
  output: {
    filename: 'bundle.js',
    path: resolve(__dirname, 'build')
  },
  module: {
    rules: [
      {
        //通过正则告诉webpack匹配是什么文件
        test: /\.css$/,
        use: [
          //  loader的执行顺序是从右向左，style-loader在css-loader前面；
          `{ loader: 'style-loader' }`,
          `{ loader: 'css-loader' }`
        ]
      }
    ]
  }
};
```

#### 将 css 提取到独立 css 文件中（MiniCssExtractPlugin）

优势：1️⃣ 分离结构和样式，使代码更加模块化和易于维护。2️⃣（缓存优化）独立的 CSS 文件可以被浏览器缓存，当用户再次访问网站时，可以减少加载时间，提高性能。

安装：`npm install mini-css-extract-plugin -D`

配置 rules 和 plugins：

```js
const `{ resolve }` = require('path');
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

module.exports = {
  entry: './src/main.js',
  output: {
    filename: 'bundle.js',
    path: resolve(__dirname, 'build')
  },
  module: {
    rules: [
      {
        test: /\.css$/,
        use: [
          // 将CSS样式提取为单独的CSS文件，通过链接方式(link)引入到HTML中
          `{ loader: MiniCssExtractPlugin.loader }`,
          `{ loader: 'css-loader' }`
        ]
      }
    ]
  },
  plugins: [
    new MiniCssExtractPlugin({
      // 使用MiniCssExtractPlugin插件
      filename: 'css/[name]_[id].css', // 打包后的css文件放到css文件夹中
      chunkFilename: 'css/[name]_[id].css'
    })
  ]
};
```

## Rollup

Rollup 是一款 ES Modules 打包器。它也可以将项 目中散落的细小模块打包为整块代码，从而使得这些划分的模块可以更好地运行在浏览器环境或者 Node.js 环境。

优势：

- 输出结果更加扁平，执行效率更高;
- 自动移除未引用代码;
- 打包结果依然完全可读。

缺点：

- 加载非 ESM 的第三方模块比较复杂;
- 因为模块最终都被打包到全局中，所以无法实现 HMR ;
- 浏览器环境中，代码拆分功能必须使用 Require.js 这样的 AMD 库

实践：
如果应用程序开发，需要大量引用第三方模块，同时还需要 HMR 提升开发体验，而且应用过大就必须要分包。那这些需求 Rollup 都无法满足。

如果是开发一个 JavaScript 框架或者库，那这些优点就特别有必要，而缺点呢几乎都可以忽略，所以在很多像 React 或者 Vue 之类的框架中都是使用的 Rollup 作为模块打包器，而并非 Webpack。

```

```
