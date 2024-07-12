---
sidebar: auto
tags:
  - node
---

## node 学习日记

[知识来源](https://juejin.cn/column/7274893714970918969)

[Node 官网](https://www.nodejs.com.cn/)

[node 部分源码解析](https://juejin.cn/post/7264044879209775141)

### 前置概念

1️⃣ v8 引擎

V8 是一个由 Google 开发的开源 JavaScript 引擎，用于 Chrome、Node.js 、Electron 等环境中，作用是**将 JS 代码编译为不同 CPU(Intel, ARM 以及 MIPS 等)对应的汇编代码**。

2️⃣ 异步 I/O （asynchronous I/O）

异步 IO 是一种编程模型，允许程序在执行 I/O 操作时不必等待其完成。异步 IO 可以在进行一个 I/O 操作的同时继续执行其他任务。这种机制特别适用于网络请求频繁或需要大量 I/O 操作的应用场景。

3️⃣ npx 和 npm 区别

- npx **侧重于执行命令**，执行某个模块命令，允许用户在不安装全局包的情况下，运行已安装在本地项目中的包或者远程仓库中的包。虽然会自动安装模块，但是重在执行命令

- npm **侧重于安装或者卸载模块**。重在安装，并不具备执行某个模块的功能。

- 查看全局安装的包：`npm ls -g`

- npx 的运行查找规则与 npm 相同

- npm 命令

  - `npm init`：初始化 npm 项目，创建 package.json 文件。
  - `npm install <package-name>`：安装指定的包
  - `npm install <package-name> --save`：安装包到依赖列表中
  - `npm install <package-name> --save-dev`：安装包到开发依赖列表中
  - `npm install -g <package-name>`：全局安装指定的包
  - `npm config list`：npm 配置信息
  - `npm get registry`：获取当前 npm 包的下载地址
  - `npm config set registry <registry-url>`： 永久更改下载源地址
  - `npm install <package-name> --registry <registry-url>`：临时更改下载源地址

### 发布 npm 包

确认 package.json 文件的信息：包名、版本等--> npm adduser --> npm login --> npm publish

### npm 搭建私服

将 npm 私服部署到内网集群后，可以：

- 可以离线使用
- 避免使用公共的 npm 包出现漏洞
- 提高包的下载速度，将经常使用的 npm 包缓存到本地，减少依赖包的下载时间。对于团队内部开发和持续集成、部署等场景非常有用

使用 **Verdaccio** 工具可以快速构建 npm 私服

## 了解 Nodejs

- Nodejs 是一个跨平台的 JavaScript 的运行时环境。
- Nodejs 是构建在 V8 引擎之上的，V8 引擎是由 C/C++编写的， JavaSCript 代码需要由 C/C++转化后再执行。
- NodeJs 使用异步 I/O 和事件驱动的设计理念，可以高效地处理大量并发请求，提供了非阻塞式 I/O 接口和事件循环机制，异步 I/O 最终都是由 libuv 事件循环库去实现的。nodejs 适合干一些 IO 密集型应用，不适合 CPU 密集型应用，nodejsIO 依靠 libuv 有很强的处理能力，而 CPU 因为 nodejs 单线程原因，容易造成 CPU 占用率高，如果非要做 CPU 密集型应用，可以使用 C++插件编写 或者 nodejs 提供的 `cluster`。(CPU 密集型指的是图像的处理 或者音频处理需要大量数据结构 + 算法)

### nodejs 模块化规范

#### CommonJS 规范

- `require`：引入模块
  - 内置模块： `http`、`os`、`fs`、`child_process`
  - 第三方模块：`express`、`md5`、`koa`
  - 示例
    ```js
    const fs = require('node:fs'); // 导入核心模块
    const express = require('express'); // 导入 node_modules 目录下的模块
    const myModule = require('./myModule.js'); // 导入相对路径下的模块
    const nodeModule = require('./myModule.node'); // 导入扩展模块
    ```
- `exports` 和 `module.exports`

  ```js
  module.exports = {
    hello: function () {
      console.log('Hello, world!');
    }
  };
  ```

  `module.exports = 123`

#### ESM 模块规范

**注意**

1. 使用 ESM 模块的时候必须开启一个选项 打开 package.json 设置 `type:module`

   示例：`import fs from 'node:fs'`

2. 如果要引入 json 文件需要特殊处理 需要增加断言并且指定类型 json

   示例：`import data from './data.json' assert { type: "json" };`

3. 加载模块的整体对象

   示例：`import * as all from 'xxx.js'`

4. 动态导入

   示例：`import('./test.js').then()`

5. 默认导出 和 变量导出

   ```js
   export default {
     name: 'test'
   };
   ```

   `export const a = 1`

### 内置全局 api

#### 定义全局变量

使用 es2020 的 `globalThis`：在 node 环境会切换成 global，浏览器环境切换为 window

只能在 cjs 使用的内置全局 api

1️⃣`__dirname`：当前模块的所在目录的绝对路径

2️⃣`__filename`：当前模块文件的绝对路径，包括文件名和文件扩展名

#### process 全局对象

可以在任何模块中直接访问，无需导入或定义。`process`提供了与当前进程和运行时环境交互的方法和属性。通过 `process` 对象，我们可以访问进程的信息、控制流程和进行进程间通信。

- `process.arch`：返回操作系统 CPU 架构
- `process.cwd()`：返回当前的工作目录
- `process.argv`：获取执行进程后面的参数
- `process.memoryUsage`：用于获取当前进程的内存使用情况。该方法返回一个对象，其中包含了各种内存使用指标，如 rss（Resident Set Size，常驻集大小）、heapTotal（堆区总大小）、heapUsed（已用堆大小）和 external（外部内存使用量）等
- `process.exit()`：强制进程尽快退出，即使仍有未完全完成的异步操作挂起
- `process.kill`：kill 用来杀死一个进程，接受一个参数进程 id 可以通过 process.pid 获取
- `process.env`：读取操作系统所有的环境变量，也可以修改和查询环境变量
  - `cross-env`库：跨平台设置和使用环境变量

```js
// arm64
console.log(process.arch);

// /Users/tayce/code/test
console.log(process.cwd());

// [ '/usr/local/bin/node', '/Users/tayce/code/test/node.js' ]
console.log(process.argv);

// [Function: memoryUsage] { rss: [Function: rss] }
console.log(process.memoryUsage);
```

[参考](https://juejin.cn/post/7266009957576884239)

#### `child_process` 子进程模块

child_process 模块可以在子进程中运行任何系统命令来访问操作系统功能

创建子进程，包含 Sync 是同步 API，不包含是异步 API

- spawn 执行命令
- exec 执行命令
- execFile 执行可执行文件
- fork 创建 node 子进程
- `execSync` 执行命令 同步执行
- `execFileSync` 执行可执行文件 同步执行
- `spawnSync` 执行命令 同步执行

spawn 用于执行一些实时获取的信息因为 spawn 返回的是流边执行边返回，exec 是返回一个完整的 buffer，buffer 的大小是 200k，如果超出会报错，而 spawn 是无上限的。

spawn 在执行完成后会抛出 close 事件监听，并返回状态码，通过状态码可以知道子进程是否顺利执行。exec 只能通过返回的 buffer 去识别完成状态，识别起来较为麻烦。

exec 是底层通过 execFile 实现 execFile 底层通过 spawn 实现。

### 在 node 环境操作 DOM 和 BOM

使用 jsdom 示例

安装： `npm i jsdom`

#### 示例 1️⃣

```js
const { JSDOM } = require('jsdom');

// Create a new JSDOM instance with some initial HTML content
const dom = new JSDOM(`
<!DOCTYPE html>
<html>
<head>
    <title>Example</title>
</head>
<body>
    <h1>Hello, world!</h1>
    <p>This is a paragraph.</p>
    <ul id="list">
        <li>Item 1</li>
        <li>Item 2</li>
        <li>Item 3</li>
    </ul>
</body>
</html>
`);

// Access the document and window objects
const { document } = dom.window;

// Manipulate the DOM: Add a new list item
const newListItem = document.createElement('li');
newListItem.textContent = 'Item 4';
document.getElementById('list').appendChild(newListItem);

// Extract information from the DOM
const title = document.querySelector('title').textContent;
const heading = document.querySelector('h1').textContent;
const listItems = [...document.querySelectorAll('#list li')].map(
  (li) => li.textContent
);

console.log('Title:', title);
console.log('Heading:', heading);
console.log('List Items:', listItems);

// Modify the DOM: Change the heading text
document.querySelector('h1').textContent = 'Hello, jsdom!';

// Serialize the modified HTML back to a string
const modifiedHtml = dom.serialize();
console.log('Modified HTML:', modifiedHtml);
```

输出

![](/images/backend/jsdom.png)

#### 示例 2️⃣

```js
const fs = require('node:fs');
const { JSDOM } = require('jsdom');

const dom = new JSDOM(`<!DOCTYPE html><div id='app'></div>`);

const document = dom.window.document;

const window = dom.window;

fetch('https://api.thecatapi.com/v1/images/search?limit=10&page=1')
  .then((res) => res.json())
  .then((data) => {
    const app = document.getElementById('app');
    data.forEach((item) => {
      const img = document.createElement('img');
      img.src = item.url;
      img.style.width = '200px';
      img.style.height = '200px';
      app.appendChild(img);
    });
    fs.writeFileSync('./index.html', dom.serialize());
  });
```

生成 index.html，这就是 ssr 的实现：

![](/images/backend/ssr.png)

#### CSR 和 SSR 的区别

![](/images/backend/比较.png)

### vite 的配置项：`open: true`

用途：开发服务器启动时自动打开浏览器

```js
import { defineConfig } from 'vite';

export default defineConfig({
  server: {
    open: true // 自动在浏览器中打开应用
  }
});
```

#### 🧐 配置项的原理是什么？

os 模块可以跟操作系统进行交互：`var os = require("node:os")`

获取 CPU 的线程以及详细信息：`os.cpus()`

获取网络信息：`os.networkInterfaces()`

```js
const { exec } = require('child_process');
const os = require('os');

function openBrowser(url) {
  if (os.platform() === 'darwin') {
    // macOS
    exec(`open ${url}`); //执行shell脚本
  } else if (os.platform() === 'win32') {
    // Windows
    exec(`start ${url}`); //执行shell脚本
  } else {
    // Linux, Unix-like
    exec(`xdg-open ${url}`); //执行shell脚本
  }
}

// Example usage
openBrowser('https://www.juejin.cn');
```

### crypto 模块（加密和哈希算法）

### 对称加密示例

对称加密算法的加密速度很快，适合对大量数据进行加密和解密操作。然而，对称密钥的安全性是一个挑战，因为需要确保发送者和接收者都安全地共享密钥，否则有风险被未授权的人获取密钥并解密数据。

```js
// 【引入 crypto 模块】
const crypto = require('node:crypto');

// 【初始化加密过程】生成一个随机的 16 字节的初始化向量 (IV)
const iv = Buffer.from(crypto.randomBytes(16));

// 生成一个随机的 32 字节的随机密钥，用于加密和解密操作
const key = crypto.randomBytes(32);

// 创建加密实例，使用 AES-256-CBC 算法，提供密钥和初始化向量
const cipher = crypto.createCipheriv('aes-256-cbc', key, iv);

// 对输入数据进行加密，指定编码为 utf-8，并输出加密结果的十六进制hex表示
cipher.update('www', 'utf-8', 'hex');

// 使用 final 方法完成加密操作，并获取加密后的十六进制字符串结果
const result = cipher.final('hex');

// 解密
const de = crypto.createDecipheriv('aes-256-cbc', key, iv);
de.update(result, 'hex');
const decrypted = de.final('utf-8');

console.log('Decrypted:', decrypted);
```

### 非对称加密示例

非对称加密使用一对密钥，分别是公钥和私钥。发送者使用接收者的公钥进行加密，而接收者使用自己的私钥进行解密。公钥可以自由分享给任何人，而私钥必须保密。非对称加密算法提供了更高的安全性，因为即使公钥泄露，只有持有私钥的接收者才能解密数据。然而，非对称加密算法的加密速度相对较慢，不适合加密大量数据。因此，在实际应用中，通常使用非对称加密来交换对称密钥，然后使用对称加密算法来加密实际的数据。

```js
const crypto = require('node:crypto');
// 生成 2048位的RSA 密钥对
const { privateKey, publicKey } = crypto.generateKeyPairSync('rsa', {
  modulusLength: 2048 // 密钥对的模数长度为 2048 位
});

// 要加密的数据
const text = 'ttt';

// 使用公钥进行加密
// Buffer.from(text, 'utf-8')是要加密的文本内容，最后加密的结果为一个二进制的 Buffer
const encrypted = crypto.publicEncrypt(publicKey, Buffer.from(text, 'utf-8'));

// 使用私钥进行解密
const decrypted = crypto.privateDecrypt(privateKey, encrypted);

console.log(decrypted.toString());
```

### 哈希函数

哈希函数具有以下特点：

- 固定长度输出：不论输入数据的大小，哈希函数的输出长度是固定的。例如，常见的哈希函数如 MD5 和 SHA-256 生成的哈希值长度分别为 128 位和 256 位。
- 不可逆性：哈希函数是单向的，意味着从哈希值推导出原始输入数据是非常困难的，几乎不可能。即使输入数据发生微小的变化，其哈希值也会完全不同。
- 唯一性：哈希函数应该具有较低的碰撞概率，即不同的输入数据生成相同的哈希值的可能性应该非常小。这有助于确保哈希值能够唯一地标识输入数据。

```js
const crypto = require('node:crypto');

// 要计算哈希的数据
let text = '123456';

// 创建哈希对象，并使用 MD5 算法
const hash = crypto.createHash('md5');

// 使用 update 方法更新哈希对象，将文本数据添加到哈希计算中
hash.update(text);

// 使用 digest 方法计算最终的哈希值，并以十六进制字符串形式输出
const hashValue = hash.digest('hex');

console.log('Text:', text);
console.log('Hash:', hashValue);
```
