## node 学习日记

[知识来源](https://juejin.cn/column/7274893714970918969)

### 前置概念

1️⃣ v8 引擎

V8 是一个由 Google 开发的开源 JavaScript 引擎，用于 Chrome、Node.js 、Electron 等环境中，作用是**将 JS 代码编译为不同 CPU(Intel, ARM 以及 MIPS 等)对应的汇编代码**。

2️⃣ 异步 I/O （asynchronous I/O）

异步 IO 是一种编程模型，允许程序在执行 I/O 操作时不必等待其完成。异步 IO 可以在进行一个 I/O 操作的同时继续执行其他任务。这种机制特别适用于网络请求频繁或需要大量 I/O 操作的应用场景。

### 了解 Nodejs

- Nodejs 是一个跨平台的 JavaScript 的运行时环境。
- Nodejs 是构建在 V8 引擎之上的，V8 引擎是由 C/C++编写的， JavaSCript 代码需要由 C/C++转化后再执行。
- NodeJs 使用异步 I/O 和事件驱动的设计理念，可以高效地处理大量并发请求，提供了非阻塞式 I/O 接口和事件循环机制，异步 I/O 最终都是由 libuv 事件循环库去实现的。nodejs 适合干一些 IO 密集型应用，不适合 CPU 密集型应用，nodejsIO 依靠 libuv 有很强的处理能力，而 CPU 因为 nodejs 单线程原因，容易造成 CPU 占用率高，如果非要做 CPU 密集型应用，可以使用 C++插件编写 或者 nodejs 提供的 `cluster`。(CPU 密集型指的是图像的处理 或者音频处理需要大量数据结构 + 算法)

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
