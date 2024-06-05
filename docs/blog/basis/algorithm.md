---
sidebar: auto
tags:
  - 算法
---

## 数据结构与算法

### 算法概念

- 一个有限指令集，每条指令的描述不依赖于语言
- 接受一些输入
- 产生输出
- 在有限步骤之后终止

### 数据结构定义

![](/images/algorithm/数据结构概念.png)
![](/images/algorithm/分类.png)
![](/images/algorithm/常见数据结构.png)

## 线性结构

![](/images/algorithm/线性结构.png)

常见的线性结构

- 数组结构（Array）是一种线性结构
- 链表结构（Linkedlist）是一种线性结构
- 栈结构（Stack）是一种受限的线性结构
- 队列结构(Queue)是一种受限的线性结构

### Array

- Array 是原生数据结构（语言自带）
- 可以借助数组结构来实现其它的数据结构，比如栈、队列、堆（底层实现是通过数组）
- 通常数组的内存是连续的，数组在知道下标值的情况下，访问效率非常高，同时数组在数组头部/中间插入元素的效率较低。
- 数组是一种线性结构，并且可以在数组的任意位置插入和删除数据

![](/images/algorithm/Array.png)

### 栈结构（Stack）

栈：受限的线性结构--后进先出/先进后出

栈结构示意图：

![](/images/algorithm/stack.png)
![](/images/algorithm/栈概念.png)

#### 常见操作

![](/images/algorithm/栈操作.png)

#### 基于数组实现栈结构

```typescript
interface IStack<T> {
  push(element: T): void;
  pop(): T | undefined;
  peek(): T | undefined;
  isEmpty(): boolean;
  size(): number;
}

// 封装一个栈
export default class ArrayStack<T = string> implements IStack<T> {
  // 定义一个数组/链表，用于存储元素
  private data: Array<T> = [];

  // 实现栈中相关的操作方法
  // 1.push:添加元素到栈顶
  push(element: T): void {
    this.data.push(element);
  }

  // 2.pop方法:将栈顶的元素弹出栈（移除栈顶的第一个元素（数组的最后一个元素），并返回删除的元素）
  pop(): T | undefined {
    return this.data.pop();
  }

  // 3.peek方法:获取栈顶元素，不进行操作
  peek(): T | undefined {
    return this.data[this.data.length - 1];
  }

  // 4.isEmpty方法：判断栈是否为空
  isEmpty(): boolean {
    return !!this.data.length;
  }

  // 5.size方法：栈的元素个数
  size(): number {
    return this.data.length;
  }
}
```

---

**题一：十进制转二进制**

转换二进制是计算机科学领域中经常使用的算法

二进制中的与、或、非、异运算

- 与：运算符号为 & ，运算法则为遇 0 得 0。也就是说只要有 0，结果即为 0
  1001 & 1100--->1000
- 或：运算符号为 | ，就是一个竖线，运算法则为遇 1 得 1。也就是说，只要有 1，结果就为 1
- 异或：参加运算的两个对象，如果两个相应位为“异”（值不同），则该位结果为 1，否则为 0（0^0=0； 0^1=1； 1^0=1； 1^1=0）

  二进制和十进制互相转换
  ![](/images/algorithm/二转十.png)

  ![](/images/algorithm/十转二.png)

```typescript
import ArrayStack from './stack';

function decimalToBinary(decimal: number): string {
  // 1.创建一个栈，用于存放余数
  const stackObj = new ArrayStack<number>();

  // 2.while（不知道循环次数时使用，只知道循环结束条件）/for（知道循环次数时使用）
  // Math.floor:向下取整/Math.ceil:向上取整
  while (decimal > 0) {
    const result = decimal % 2;
    stackObj.push(result);
    decimal = Math.floor(decimal / 2);
  }

  // 3.依次取出
  let binary = '';
  while (!stackObj.isEmpty()) {
    binary += stackObj.pop();
  }
  return binary;
}

decimalToBinary(100);
```

**题二：[十进制整数的反码](https://leetcode.cn/problems/complement-of-base-10-integer/description/)**

```typescript
function bitwiseComplement(n: number): number {
  let arr: number[] = [];

  if (n === 0) return 1;

  while (n > 0) {
    let current = n % 2;
    arr.push(current);
    n = Math.floor(n / 2);
  }

  let str: number[] = [];
  while (arr.length) {
    str.unshift(arr[arr.length - 1] === 0 ? 1 : 0);
    arr.pop();
  }

  let result: number = 0;
  for (let j = str.length - 1; j >= 0; j--) {
    if (str[j]) result += Math.pow(2, j) * str[j];
  }

  return result;
}
```

### 队列结构（Queue）

队列：受限的线性结构，先进先出

- 只允许在队列的前端进行删除操作（shift）
- 在队列的后端进行插入操作（push）

![](/images/algorithm/队列.png)
![](/images/algorithm/线程队列.png)

#### 常见操作

![](/images/algorithm/队列操作.png)

#### 基于数组实现队列

```typescript
interface IQueue<T> {
  enqueue(element: T): void;
  dequeue(): T | undefined;
  peek(): T | undefined;
  isEmpty(): boolean;
  get size(): number;
}

class ArrayQueue<T> implements IQueue<T> {
  private data: T[] = [];
  enqueue(element: T): void {
    this.data.push(element);
  }
  dequeue(): T | undefined {
    return this.data.shift();
  }
  peek(): T | undefined {
    return this.data[0];
  }
  isEmpty(): boolean {
    return this.data.length === 0;
  }
  get size(): number {
    return this.data.length;
  }
}

export default ArrayQueue;
```

---

**题一：击鼓传花算法**

题目描述：n 个人编号 1,2……n。按编号逆时针站一圈，从第 1 号开始，每一次从当前的人顺时针数 m 个，被数到编号的人出局。重复上述过程，问最后剩下的人是谁

```typescript
import ArrayQueue from './Queue';

// num：传递的次数
function getLast(list: string[], num: number): string | void {
  if (list.length === 0) return;
  let arr = new ArrayQueue<string>();
  for (const item of list) {
    arr.enqueue(item);
  }

  while (arr.size > 1) {
    for (let i = 1; i < num; i++) {
      const item = arr.dequeue();
      item && arr.enqueue(item);
    }
    arr.dequeue();
    console.log(arr, '删除之后的arr');
  }

  return arr.dequeue()!;
}

console.log(getLast(['红', '橙', '黄', '绿', '青', '蓝'], 2));
```

**题二：[破冰游戏](https://leetcode.cn/problems/yuan-quan-zhong-zui-hou-sheng-xia-de-shu-zi-lcof/description/)**

**TODO...**

### 链表结构（LinkedList）

#### 数组的缺点

![](/images/algorithm/数组缺点.png)

#### 链表优势

![](/images/algorithm/链表优势.png)

#### 封装链表结构

![](/images/algorithm/链表结构.png)

```typescript
// 创建node节点类
// 泛型类：用于封装每一个节点上的信息（包括值和指向下一个节点的引用）
class Node<T> {
  value: T;
  next: Node<T> | null = null; // 设置默认值
  constructor(value: T) {
    //   创建时赋值
    this.value = value;
    this.next = null;
  }
}

// 创建linkedlist类
// 用于表示链表结构，链表中两个属性：链表长度 / 链表中第一个节点
class LinkedList<T> {
  private head: Node<T> | null = null;
  private size: number = 0;
  get length() {
    return this.size;
  }
}
```

#### 常见操作

![](/images/algorithm/链表操作.png)

---

**题一：[设计链表](https://leetcode.cn/problems/design-linked-list/description/)**

```typescript
// 创建node节点类
class Node<T> {
  value: T;
  next: Node<T> | null = null; // 设置默认值
  constructor(value: T) {
    //   创建时赋值
    this.value = value;
    this.next = null;
  }
}

// 创建linkedlist类
class LinkedList<T> {
  private head: Node<T> | null = null;
  private size: number = 0;
  get length() {
    return this.size;
  }

  // 封装私有方法
  // 根据position获取到当前的节点（不是节点的value，而是获取节点）
  private getNode(position: number): Node<T> | null {
    let current = this.head;
    let index = 0;
    while (index++ < position && current) {
      current = current?.next; // 后一节点
    }
    return current;
  }

  // 追加节点
  append(value: T) {
    const newNode = new Node(value);

    if (!this.head) {
      // 情况一：链表本身为空
      this.head = newNode;
    } else {
      // 情况二：链表不为空
      let current = this.head;
      while (current.next) {
        current = current.next;
      }
      current.next = newNode;
    }
    this.size++;
  }

  // 遍历链表
  traverse() {
    let current = this.head;
    let val: Array<T> = [];
    while (current) {
      val.push(current.value);
      current = current.next;
    }
    console.log(val.join('--'));
  }

  // 插入节点
  insert(value: T, position: number) {
    // position范围：  0<=position<=this.size
    if (position < 0 || position > this.size) {
      throw new Error('position 越界');
    } else {
      const newNode = new Node(value);
      if (position === 0) {
        // 情况一：插入到头部
        newNode.next = this.head;
        this.head = newNode;
      } else {
        // 情况二：插入到其它位置

        let prev: Node<T> | null = null;
        //  --封装前代码
        //   let current = this.head;
        // let index = 0;
        // while (index++ < position && current) {
        //   prev = current; // 前一节点
        //   current = current?.next; // 后一节点
        // }
        prev = this.getNode(position - 1);
        newNode.next = prev?.next ?? null;
        prev!.next = newNode;
      }
      this.size++;
    }
  }

  // 删除节点--
  removeAt(position: number): T | null {
    if (position < 0 || position >= this.size) {
      throw new Error('position 越界');
    } else {
      let current = this.head;
      // 情况一：删除第一个元素
      if (position === 0) {
        this.head = current?.next ?? null;
      } else {
        // 情况二：插入到其它位置
        let prev: Node<T> | null = null;
        //  --封装前代码
        // let index = 0;
        // while (index++ < position && current) {
        //   prev = current; // 前一节点
        //   current = current?.next; // 后一节点
        // }
        prev = this.getNode(position - 1);
        current = prev!.next; // 重新赋值current
        prev!.next = prev?.next?.next ?? null;
      }
      this.size--;
      return current?.value ?? null;
    }
  }

  remove(value: T): void {
    const index = this.indexOf(value);
    this.removeAt(index);
  }

  // 获取对应位置的元素
  get(position: number): T | null {
    if (position < 0 || position >= this.size) return null;
    return this.getNode(position)?.value ?? null;
  }

  // 更新某个位置
  update(value: T, position: number) {
    if (position < 0 || position >= this.size) return false;
    // 获取对应位置节点，进行更新
    const currentNode = this.getNode(position);
    currentNode!.value = value;
    return true;
  }

  // 根据值获取对应位置索引
  indexOf(value: T): number {
    let current = this.head;
    let index = 0;
    while (current) {
      if (current.value === value) {
        return index;
      }
      current = current.next;
      index++;
    }
    return -1;
  }

  // 判断链表是否为空
  isEmpty(): boolean {
    return this.size === 0;
  }
}

const linkedArray = new LinkedList<string>();
linkedArray.append('qwqe');
linkedArray.append('asdf');
linkedArray.append('ooo');
linkedArray.insert('insert到中间', 3);
linkedArray.removeAt(2);
linkedArray.get(0);
linkedArray.get(2);
linkedArray.update('更新的值', 1);
linkedArray.indexOf('insert到中间');

linkedArray.traverse();
export { LinkedList };
```

**题二：[删除链表中的节点](https://leetcode.cn/problems/delete-node-in-a-linked-list/description/)**

```typescript
class ListNode {
  val: number;
  next: ListNode | null;
  constructor(val?: number, next?: ListNode | null) {
    this.val = val === undefined ? 0 : val;
    this.next = next === undefined ? null : next;
  }
}

function deleteNode(node: ListNode | null): void {
  //删除节点并不是指从内存中删除它：
  // 思路：将node的值变为下一个节点的值；node的next指向node.next.next
  node!.val = node?.next?.val;
  node!.next = node?.next?.next;
}
```

## 算法性能分析

详见[算法性能分析](https://programmercarl.com/%E5%89%8D%E5%BA%8F/%E5%85%B3%E4%BA%8E%E6%97%B6%E9%97%B4%E5%A4%8D%E6%9D%82%E5%BA%A6%EF%BC%8C%E4%BD%A0%E4%B8%8D%E7%9F%A5%E9%81%93%E7%9A%84%E9%83%BD%E5%9C%A8%E8%BF%99%E9%87%8C%EF%BC%81.html)

### 大 O 表示法

![](/images/algorithm/大O.png)

### 空间复杂度

![](/images/algorithm/空间复杂度.png)

### 数组和链表的复杂度对比

![](/images/algorithm/复杂度对比.png)

## 哈希表

### 哈希表的优势与不足

![](/images/algorithm/哈希表.png)

哈希函数：让某个 key 的信息和索引值对应起来
![](/images/algorithm/哈希表结构.png)

### 冲突

![](/images/algorithm/冲突.png)

### 开放地址法

![](/images/algorithm/开放地址法.png)

### 线性探测法

![](/images/algorithm/线性探测.png)

线性探测存在的问题

![](/images/algorithm/线性探测问题.png)

### 二次探测

![](/images/algorithm/二次探测.png)

### 再哈希法

![](/images/algorithm/再哈希法.png)

### 哈希化的效率

个数/容量=装填因子

当装填因子大于特定值，会进行扩容

![](/images/algorithm/装填因子.png)

### 链地址法

![](/images/algorithm/链地址法.png)

### 哈希函数

![](/images/algorithm/哈希函数.png)

### 快速计算：霍纳法则

![](/images/algorithm/霍纳法则.png)

经过霍纳法则变换的多项式只需要执行 n 次乘法运算便可以得到 n 阶多项式的值，所以复杂度自然就为 O(n)

### 均匀分布

![](/images/algorithm/均匀分布.png)

### 实现哈希表

```typescript
/**
 * 哈希函数，将key映射成index
 * @param key 转换的key
 * @param max 数组的长度（最大的数组）
 * @returns 索引值
 */

function hashFunc(key: string, max: number): number {
  let hashCode = 0;
  const length = key.length;
  for (let i = 0; i < length; i++) {
    // 霍纳法则
    // charCodeAt() 方法返回字符串中规定索引（下标）处字符的 Unicode
    hashCode = 31 * hashCode + key.charCodeAt(i);
  }

  // 求出索引值
  const index = hashCode % max;
  return index;
}

// 测试哈希函数-- 目前loadFactor 6 / 8-->需要扩容
// 将6个字符串放到长度为7的hash表中
console.log(hashFunc('abc', 8));
console.log(hashFunc('aaa', 8));
console.log(hashFunc('ttt', 8));
console.log(hashFunc('ccc', 8));
console.log(hashFunc('111', 8));
console.log(hashFunc('222', 8));
```

### 哈希表扩容

![](/images/algorithm/扩容.png)

#### 扩容质数

![](/images/algorithm/扩容质数.png)
![](/images/algorithm/扩容质数2.png)

### 实现哈希表

```typescript
class HashTable<T = any> {
  // 创建数组，用来存放链地址法中的链（数组）
  // [string, T][][]--元组类型
  private storage: [string, T][][] = [];
  // 定义数组长度
  private length: number = 7;
  // 记录已经存放元素的个数
  private count: number = 0;
  // loadFactor: count/length

  // 扩容/缩容  loadFactor大于0.75时进行扩容
  private resize(newLength: number) {
    // 设置新的长度
    this.length = this.getPrime(newLength) < 7 ? 7 : this.getPrime(newLength);

    //   获取原来所有的数据，并且重新放入到新的容量数组中
    const oldStorage = this.storage;
    //   对数据进行初始化
    this.storage = [];
    this.count = 0;
    //   获取原来数据，放入新的数组中
    oldStorage.forEach((bucket) => {
      if (!bucket) return;
      for (let i = 0; i < bucket.length; i++) {
        const tuple = bucket[i];
        this.put(tuple[0], tuple[1]);
      }
    });
  }

  // 获取下一个质数
  getPrime(num: number): number {
    while (!this.isPrime(num)) {
      num++;
    }
    return num;
  }

  // 判断是否是质数 O(logn)
  isPrime(num: number): boolean {
    const squareRoot = Math.sqrt(num); // Math.sqrt 求平方根
    for (let i = 2; i <= squareRoot; i++) {
      if (num % i === 0) {
        return false;
      }
    }
    return true;
  }

  private hashFunc(key: string, max: number) {
    let hashCode = 0;
    const length = key.length;
    for (let i = 0; i < length; i++) {
      hashCode = 31 * hashCode + key.charCodeAt(i);
    }

    // 求出索引值
    const index = hashCode % max;
    return index;
  }

  // 插入/修改数据
  put(key: string, value: T) {
    // 根据key获取数组中对应的索引值
    const index = this.hashFunc(key, this.length);
    // 取出索引值对应位置的数组（桶）
    let bucket: [string, T][] = this.storage[index];

    // 判断bucket是否有值(初始化)
    if (!bucket) {
      bucket = [];
      this.storage[index] = bucket;
    }

    let isUpdate = false;
    // 此处确定有数组，但数组中是否已存在key是不确定的
    for (let i = 0; i < bucket.length; i++) {
      let tuple = bucket[i];
      if (tuple[0] === key) {
        tuple[1] = value;
        isUpdate = true;
      }
    }

    // 如果没有覆盖，执行插入操作
    if (!isUpdate) {
      bucket.push([key, value]);
      this.count++;

      // loadFactor>0.75时进行扩容操作
      if (this.count / this.length > 0.75) {
        this.resize(this.length * 2);
      }
    }
  }

  // 获取
  get(key: string): T | undefined {
    const index = this.hashFunc(key, this.length);
    let bucket = this.storage[index];
    if (bucket) {
      for (let i = 0; i < bucket.length; i++) {
        const tuple = bucket[i];
        if (key === tuple[0]) {
          return tuple[1];
        }
      }
      return undefined;
    }
    return undefined;
  }

  // 删除
  delete(key: string): T | undefined {
    const index = this.hashFunc(key, this.length);
    let bucket = this.storage[index];
    if (bucket) {
      for (let i = 0; i < bucket.length; i++) {
        const tuple = bucket[i];
        if (key === tuple[0]) {
          bucket.splice(i, 1);
          this.count--;
          // loadFactor<0.25时进行缩容操作
          if (this.count / this.length < 0.25) {
            this.resize(Math.floor(this.length / 2));
          }
          return tuple[1];
        }
      }
      return undefined;
    }
    return undefined;
  }
}

const hashTable = new HashTable();

hashTable.put('aaa', 100);
hashTable.put('bbb', 200);
hashTable.put('ccc', 300);

const ind = hashTable.get('bbb');
console.log(ind);

const deleteInd = hashTable.get('bbb');
console.log(deleteInd);
```

## 树结构

### 数组、链表、哈希表的优缺点

![](/images/algorithm/优缺点.png)
![](/images/algorithm/优缺点2.png)
![](/images/algorithm/优缺点3.png)

### 树结构的基本情况

![](/images/algorithm/树基本情况.png)

### 树的术语

![](/images/algorithm/树2.png)

### 二叉树

#### 概念

二叉树可以为空（没有节点），若不为空，则它是由根节点和称为其左子树 TL（tree left）和右子树 TR（tree right）的两个不相交的二叉树组成，树中每个节点最多只能有两个子节点。

#### 二叉树的五种形态

![](/images/algorithm/五种形态.png)

#### 重要特性

![](/images/algorithm/重要特性.png)

#### 完美二叉树

![](/images/algorithm/完美二叉树.png)

#### 完全二叉树

![](/images/algorithm/完全二叉树.png)

#### 二叉树的存储

![](/images/algorithm/二叉树存储.png)

#### 二叉搜索树

二叉搜索树的好处：

- 查找所需的最大次数等于二叉搜索树的深度
- 插入节点时，也利用类似的方法，一层层比较大小，找到新节点合适的位置

![](/images/algorithm/二叉搜索树.png)

#### 二叉树常用操作

![](/images/algorithm/遍历.png)

#### 遍历二叉树

先序/中序/后序:取决于访问根（root）节点的时机

先序遍历（preorder traverse）

- 在所有的树结构中，优先访问根节点
- 之后开始访问左子树
- 之后开始访问右子树

![](/images/algorithm/先序遍历.png)

中序遍历（in order traverse）-- 在二叉搜索树中，按值从小到大排序

- 先访问左子树
- 访问根结点
- 访问右子树

![](/images/algorithm/中序遍历.png)

后序遍历（post order traverse）

- 先访问左子树
- 访问右子树
- 访问根结点

![](/images/algorithm/后序遍历.png)

层序遍历（level order traverse）逐层遍历

![](/images/algorithm/层序遍历.png)

**代码实现**

```typescript
class INode<T> {
  value: T;
  constructor(value: T) {
    this.value = value;
  }
}

class TreeNode<T> extends INode<T> {
  left: TreeNode<T> | null = null;
  right: TreeNode<T> | null = null;
  parent: TreeNode<T> | null = null;

  get isLeft(): boolean {
    // this.parent.left是否等于当前节点
    return !!(this.parent && this.parent.left === this);
  }
  get isRight(): boolean {
    // this.parent.right是否等于当前节点
    return !!(this.parent && this.parent.right === this);
  }
}

class BSTree<T = number> {
  root: TreeNode<T> | null = null;

  printTree(root: TreeNode<T> | null) {
    btPrint(root);
  }

  // insert--插入数据
  insert(value: T) {
    // 根据传入value创建node（Treenode）节点
    const newNode = new TreeNode(value);

    // 判断当前是否已有根节点
    if (!this.root) {
      this.root = newNode;
    } else {
      this.insertNode(this.root, newNode);
    }
  }

  // 插入
  private insertNode(root: TreeNode<T>, newNode: TreeNode<T>) {
    if (newNode.value < root.value) {
      // 在左边寻找空白位置
      if (root.left === null) {
        root.left = newNode;
      } else {
        this.insertNode(root.left, newNode);
      }
    } else {
      // 在右边寻找空白位置
      if (root.right === null) {
        root.right = newNode;
      } else {
        this.insertNode(root.right, newNode);
      }
    }
  }

  // 遍历
  // ①先序遍历
  preorderTraverse() {
    this.preorderTraverseNode(this.root);
  }
  // 使用递归
  private preorderTraverseNode(node?: TreeNode<T> | null) {
    if (node) {
      console.log(node);
      this.preorderTraverseNode(node.left);
      this.preorderTraverseNode(node.right);
    }
  }
  // 非递归
  preorderTraverseStack() {
    let stack: TreeNode<T>[] = [];
    let current: TreeNode<T> | null = this.root;

    while (current !== null || stack.length !== 0) {
      while (current !== null) {
        console.log(current.value);
        stack.push(current);
        current = current.left;
      }
      current = stack.pop()!;
      current = current.right;
    }
  }

  // ②中序遍历
  inorderTraverse() {
    this.inorderTraverseNode(this.root);
  }
  private inorderTraverseNode(node?: TreeNode<T> | null) {
    if (node) {
      this.inorderTraverseNode(node.left);
      console.log(node);
      this.inorderTraverseNode(node.right);
    }
  }
  // 非递归
  inorderTraverseStack() {
    let stack: TreeNode<T>[] = [];
    let current: TreeNode<T> | null = this.root;

    while (current !== null || stack.length !== 0) {
      while (current !== null) {
        stack.push(current);
        current = current.left;
      }
      current = stack.pop()!;
      console.log(current.value);
      current = current.right;
    }
  }

  // ③后序遍历
  postorderTraverse() {
    this.postorderTraverseNode(this.root);
  }
  private postorderTraverseNode(node?: TreeNode<T> | null) {
    if (node) {
      this.postorderTraverseNode(node.left);
      this.postorderTraverseNode(node.right);
      console.log(node);
    }
  }
  // 非递归
  postorderTraverseStack() {
    let stack: TreeNode<T>[] = [];
    let current: TreeNode<T> | null = this.root;
    let lastVisitedNode: TreeNode<T> | null = null;

    while (current !== null || stack.length !== 0) {
      while (current !== null) {
        stack.push(current);
        current = current.left;
      }
      current = stack[stack.length - 1];
      if (current.right !== null || current.right === lastVisitedNode) {
        console.log(current.value);
        lastVisitedNode = current;
        stack.pop();
        current = null;
      } else {
        current = current.right;
      }
    }
  }

  // ④层序遍历
  // --访问队列中的出队元素，并且访问
  // --将出队的左子节点和右子节点分别加入队列
  levelOrderTraverse() {
    if (!this.root) return;
    //   创建队列结构
    let queue: TreeNode<T>[] = [];
    //   第一个节点（根节点）
    queue.push(this.root);

    //   遍历队列中所有的节点（依次出队）
    while (queue.length) {
      // 访问节点的过程
      const current = queue.shift()!;
      console.log(current.value);
      // 将左子节点放入到队列中
      if (current?.left) {
        queue.push(current?.left);
      }
      // 将右子节点放入到队列中
      if (current?.right) {
        queue.push(current?.right);
      }
    }
  }

  // 获取最值
  // ①最大值
  getMaxValue(): T | null {
    let current = this.root;
    while (current && current.right) {
      current = current.right;
    }
    return current?.value ?? null;
  }

  // ②最小值
  getMinValue(): T | null {
    let current = this.root;
    while (current && current.left) {
      current = current.left;
    }
    return current?.value ?? null;
  }

  // 搜索特定值
  // 判断拿到的节点是否是搜索的节点
  // 如果不是：搜索节点比当前节点大，从右边找/搜索节点比当前节点小，从左边找
  search(value: T): boolean {
    return !!this.searchNode(value);
  }
  searchNode(value: T): TreeNode<T> | null {
    let current = this.root;
    let parent: TreeNode<T> | null = null;
    while (current) {
      if (current.value === value) return current;
      parent = current;
      if (current.value < value) {
        current = current.right;
      } else {
        current = current.left;
      }
      // 保存父节点的值
      if (current) {
        current.parent = parent;
      }
    }
    return null;
  }
  // 递归写法
  searchVal(node: TreeNode<T> | null, value: T): boolean {
    if (node === null) return false;
    if (node.value > value) {
      return this.searchVal(node.left, value);
    } else if (node.value < value) {
      return this.searchVal(node.right, value);
    } else return true;
  }

  // 删除
  // 三种情况：1.节点不存在 2.该节点是叶节点 3.该节点有一个子节点 4.该节点有两个子节点
  remove(value: T): boolean {
    let replaceNode: TreeNode<T> | null = null;
    const current = this.searchNode(value);
    // 情况1：节点不存在
    if (!current) return false;

    // 情况2：叶子节点
    if (current.left === null && current.right === null) {
      replaceNode = null;
    }
    // 情况3：只有一个子节点
    // 左子节点
    else if (current.right === null) {
      replaceNode = current.left;
    }
    // 右子节点
    else if (current.left === null) {
      replaceNode = current.right;
    }
    // 有两个子节点
    // 方式一：去左边找一个比current节点小，且左子树中最大的节点（前驱节点）
    // 方式二：去右边找一个比current节点大，且右子树中最小的节点（后继节点）
    else {
      if (!current) return false;
      // 寻找后继节点
      let curr: TreeNode<T> | null = current.right;
      let successor: TreeNode<T> | null = null;
      while (curr) {
        successor = curr;
        curr = curr.left ?? null;
        if (curr) {
          curr.parent = successor;
        }
      }
      if (successor !== current.right) {
        successor!.parent!.left = successor!.right;
        successor!.right = current.right;
      }
      successor!.left = current.left;

      replaceNode = successor;

      if (current === this.root) {
        this.root = replaceNode;
      } else if (current.isLeft) {
        current.parent!.left = replaceNode;
      } else {
        current.parent!.right = replaceNode;
      }
    }
    return true;
  }
}

const bst = new BSTree<number>();
bst.insert(12);
bst.insert(18);
bst.insert(5);
bst.insert(13);
bst.insert(4);
bst.insert(7);
bst.insert(1);
bst.insert(41);
bst.insert(19);
bst.printTree(bst.root);

bst.remove(12);
bst.printTree(bst.root);
```

#### 二叉搜索树的缺陷

![](/images/algorithm/搜索树缺陷.png)

#### 树平衡性

![](/images/algorithm/树平衡性.png)

## 图结构

### 理解图结构

![](/images/algorithm/图.png)

### 图的特点

![](/images/algorithm/图的特点.png)
![](/images/algorithm/图概念.png)
![](/images/algorithm/度和路径.png)

### 邻接表

![](/images/algorithm/邻接表.png)

### 图的遍历

![](/images/algorithm/图的遍历.png)

### 广度优先搜索

![](/images/algorithm/广度优先搜索.png)

### 深度优先搜索

![](/images/algorithm/深度优先搜索.png)

### 图的实现

```typescript
class Graph<T> {
  verteces: T[] = []; // 顶点
  addJoinList: Map<T, T[]> = new Map(); // 邻接表（边）

  // 添加顶点和边的方法
  addVertex(vertex: T) {
    // 将顶点添加到数组中保存
    this.verteces.push(vertex);
    // 创建一个邻接表中的数组
    this.addJoinList.set(vertex, []);
  }

  addEdge(v1: T, v2: T) {
    // 顶点之间相互添加边
    this.addJoinList.get(v1)?.push(v2);
    this.addJoinList.get(v2)?.push(v1);
  }

  traverse() {
    console.log('Graph');
    this.verteces.forEach((vertex) => {
      const edges = this.addJoinList.get(vertex);
      console.log(`${vertex}-->${edges?.join(' ')}`);
    });
  }

  // 广度优先
  bfs() {
    // 判断是否有顶点
    if (this.verteces.length === 0) return;

    // 创建队列结构访问每一个顶点
    let queue: T[] = [];
    queue.push(this.verteces[0]);

    // 创建Set结构，记录某一个顶点是否被访问过
    const visited = new Set<T>();
    visited.add(this.verteces[0]);

    // 遍历队列中每一个顶点
    while (queue.length) {
      const vertex = queue.shift()!;
      const neighbours = this.addJoinList.get(vertex);
      if (!neighbours) continue;

      for (const item of neighbours) {
        if (!visited.has(item)) {
          queue.push(item);
          visited.add(item);
        }
      }
    }
  }

  // 深度优先
  dfs() {
    // 判断是否有顶点
    if (this.verteces.length === 0) return;

    // 创建栈结构
    const stack: T[] = [];
    stack.push(this.verteces[0]);

    // 创建Set结构
    const visited = new Set<T>();
    visited.add(this.verteces[0]);

    // 从第一个顶点开始访问
    while (stack.length) {
      const vertex = stack.pop()!;
      const neighbours = this.addJoinList.get(vertex);
      if (!neighbours) continue;

      for (let i = neighbours.length - 1; i >= 0; i--) {
        if (!visited.has(neighbours[i])) {
          stack.push(neighbours[i]);
          visited.add(neighbours[i]);
        }
      }
    }
  }
}

const graph = new Graph();
graph.addVertex('A');
graph.addVertex('B');
graph.addVertex('C');
graph.addVertex('D');
graph.addVertex('E');
graph.addVertex('F');
graph.addVertex('G');
graph.addEdge('A', 'B');
graph.addEdge('A', 'C');
graph.addEdge('C', 'D');
graph.addEdge('D', 'H');
graph.addEdge('B', 'E');
graph.addEdge('B', 'F');
graph.addEdge('C', 'G');
graph.traverse();
```

## 循环链表

### 循环链表概念

![](/images/algorithm/循环链表.png)

### 实现循环链表

思路：

![](/images/algorithm/实现循环链表.png)

```typescript
// 创建node节点类
class Node<T> {
  value: T;
  next: Node<T> | null = null; // 设置默认值
  constructor(value: T) {
    // 创建时赋值
    this.value = value;
    this.next = null;
  }
}

// 创建linkedlist类
class ILinkedList<T> {
  protected head: Node<T> | null = null;
  protected size: number = 0;
  protected tail: Node<T> | null = null; //【★新增】 尾部节点

  get length() {
    return this.size;
  }

  // 【★新增】判断是否是最后一个节点方法
  private isTail(node: Node<T>): boolean {
    return this.tail === node;
  }

  // 封装私有方法
  // 根据position获取到当前的节点（不是节点的value，而是获取节点）
  protected getNode(position: number): Node<T> | null {
    let current = this.head;
    let index = 0;
    while (index++ < position && current) {
      current = current?.next; // 后一节点
    }
    return current;
  }

  // 追加节点
  append(value: T) {
    const newNode = new Node(value);
    if (!this.head) {
      // 情况一：链表本身为空
      this.head = newNode;
    } else {
      // 情况二：链表不为空
      this.tail!.next = newNode; // 【★修改】
    }

    this.tail = newNode; // 【★修改】tail等于新节点
    this.size++;
  }

  // 遍历链表
  traverse() {
    let current = this.head;
    let val: Array<T> = [];
    while (current) {
      val.push(current.value);
      if (this.isTail(current)) {
        // 【★新增】 遍历到最后一个节点
        current = null;
      } else {
        current = current.next;
      }
    }
    // 【★新增】 如果是循环链表：链表末处加上第一个节点的值
    if (this.head && this.tail?.next === this.head) {
      val.push(this.head.value);
    }
    console.log(val.join('--'));
  }

  // 插入节点
  insert(value: T, position: number): boolean {
    // position范围：  0<=position<=this.size
    if (position < 0 || position > this.size) {
      throw new Error('position 越界');
      return false;
    } else {
      const newNode = new Node(value);
      if (position === 0) {
        // 情况一：插入到头部
        newNode.next = this.head;
        this.head = newNode;
      } else {
        // 情况二：插入到其它位置
        let prev: Node<T> | null = null;
        prev = this.getNode(position - 1);
        newNode.next = prev?.next ?? null;
        prev!.next = newNode;
        // 【★修改】尾部插入节点的情况
        if (position === this.length) {
          this.tail = newNode;
        }
      }
      this.size++;
      return true;
    }
  }

  // 删除节点--
  removeAt(position: number): T | null {
    if (position < 0 || position >= this.size) {
      throw new Error('position 越界');
    } else {
      let current = this.head;
      // 情况一：删除第一个元素
      if (position === 0) {
        this.head = current?.next ?? null;
        // 【★修改】只有一个元素
        if (this.length === 1) {
          this.tail = null;
        }
      } else {
        // 情况二：删除其它位置
        let prev: Node<T> | null = null;
        //  --封装前代码
        prev = this.getNode(position - 1);
        current = prev!.next;
        prev!.next = prev?.next?.next ?? null;
        // 【★修改】删除最后一个节点
        if (position === this.length - 1) {
          this.tail = prev;
        }
      }
      this.size--;
      return current?.value ?? null;
    }
  }

  remove(value: T): void {
    const index = this.indexOf(value);
    this.removeAt(index);
  }

  // 获取对应位置的元素
  get(position: number): T | null {
    if (position < 0 || position >= this.size) return null;
    return this.getNode(position)?.value ?? null;
  }

  // 更新某个位置
  update(value: T, position: number) {
    if (position < 0 || position >= this.size) return false;
    // 获取对应位置节点，进行更新
    const currentNode = this.getNode(position);
    currentNode!.value = value;
    return true;
  }

  // 根据值获取对应位置索引
  indexOf(value: T): number {
    let current = this.head;
    let index = 0;
    while (current) {
      if (current.value === value) {
        return index;
      }
      // 【★新增】兼容循环链表
      if (this.isTail(current)) {
        current.next = null;
      } else {
        current = current.next;
      }
      index++;
    }
    return -1;
  }

  // 判断链表是否为空
  isEmpty(): boolean {
    return this.size === 0;
  }
}

export default ILinkedList;
```

**实现循环链表**

需要重新实现的方法：append、insert、removeAt

```typescript
// 在单向链表基础上封装循环链表
class CircleLinkedList<T> extends ILinkedList<T> {
  append(value: T): void {
    // ★ 使用super继承append方法
    super.append(value);
    // 将尾部节点指向head
    this.tail!.next = this.head;
  }

  insert(value: T, position: number): boolean {
    const isSuccess = super.insert(value, position);
    // ★ 头部和尾部插入节点，尾部节点的指向要改为指向head
    if (isSuccess && (position === this.length - 1 || !position)) {
      this.tail!.next = this.head;
    }
    return isSuccess;
  }

  removeAt(position: number): T | null {
    const delItem = super.removeAt(position);
    // ★ 头部和尾部删除节点，尾部节点的指向要改为指向head
    if (delItem && this.length && (position === this.length || !position)) {
      this.tail!.next = this.head;
    }
    return delItem;
  }
}

// const cLinkedList = new CircleLinkedList<string>();
// cLinkedList.append('qwqe');
// cLinkedList.append('asdf');
// cLinkedList.append('ooo');
// cLinkedList.insert('insert到中间', 1);
// // cLinkedList.remove('asdf');
// // cLinkedList.removeAt(1);
// console.log(cLinkedList.get(2));
// cLinkedList.update('OOO', 3);
// console.log(cLinkedList.indexOf('OOO'));
// cLinkedList.remove('asdf');
// console.log(cLinkedList.isEmpty());
// console.log(cLinkedList.length);
// cLinkedList.traverse();
```

## 双向链表

### 概念

![](/images/algorithm/双向链表.png)

![](/images/algorithm/双向链表图.png)

#### 常见方法

![](/images/algorithm/双向链表方法.png)

### 代码实现

**双向链表的节点封装**

```typescript
export class Node<T> {
  value: T;
  next: Node<T> | null = null; // 设置默认值
  constructor(value: T) {
    //   创建时赋值
    this.value = value;
    this.next = null;
  }
}

export class DoubleNode<T> extends Node<T> {
  prev: DoubleNode<T> | null = null;
  next: DoubleNode<T> | null = null; // ★ 重写next的类型（必须是Node类型或者Node类型的子类型）
}
```

**代码具体实现**

```typescript
import { DoubleNode } from './interface';
import ILinkedList from './重构linkedList';

class DoubleLinkedList<T> extends ILinkedList<T> {
  protected head: DoubleNode<T> | null = null;
  protected tail: DoubleNode<T> | null = null;

  // 尾部追加元素
  append(value: T): void {
    const newNode = new DoubleNode<T>(value);
    if (!this.head) {
      // ★ 添加的第一个节点既是首节点，也是尾节点
      this.head = newNode;
      this.tail = newNode;
    } else {
      // ★ tail指向新的末尾节点
      // ★ 新末尾节点 prev指向前末尾节点
      // ★ tail等于新末尾节点
      this.tail!.next = newNode;
      // 不能将父类对象赋值给子类类型，可以将子类类型赋值给父类类型（多态）
      newNode.prev = this.tail;
      this.tail = newNode;
    }
    this.size++;
  }

  // 头部添加元素
  prepend(value: T): void {
    const newNode = new DoubleNode<T>(value);
    if (!this.head) {
      // ★ 添加的第一个节点既是首节点，也是尾节点
      this.head = newNode;
      this.tail = newNode;
    } else {
      // ★ 新头部节点next指向原头部节点
      // ★ head节点prev指向新头部节点
      // ★ head等于新头部节点
      newNode.next = this.head;
      // head指针反向指回newNode
      this.head.prev = newNode;
      this.head = newNode;
    }
    this.size++;
  }

  // ★ 反向遍历
  postTraverse() {
    let current = this.tail;
    let val: T[] = [];
    while (current) {
      val.push(current.value);
      current = current.prev;
    }
    console.log(val.join('--'));
  }

  // 根据索引插入元素
  insert(value: T, position: number): boolean {
    if (position < 0 || position > this.length) return false;
    if (position === 0) {
      this.prepend(value);
    } else if (position === this.length) {
      this.append(value);
    } else {
      const newNode = new DoubleNode<T>(value);
      const current = this.getNode(position) as DoubleNode<T>;
      // ★ current前一节点next指向--newnode next / prev -- current节点prev指向
      current.prev!.next = newNode; // ★ current前一个指针的next指向新节点
      newNode.next = current;
      newNode.prev = current.prev;
      current.prev = newNode; // ★ 放到最后
      this.size++;
    }
    return true;
  }

  // 根据索引删除元素
  removeAt(position: number): T | null {
    if (position < 0 || position >= this.length) return null;
    let current: DoubleNode<T> | null = this.head;
    if (position === 0) {
      if (this.length === 1) {
        this.head = null;
        this.tail = null;
      } else {
        // head指针指向head后面的节点
        this.head = this.head!.next;
        // 置空head指向的新节点的prev指向
        this.head!.prev = null;
      }
    } else if (position === this.length - 1) {
      current = this.tail;

      // tail指针指向tail前面的节点
      this.tail = this.tail!.prev;
      // 置空tail节点的next指向
      this.tail!.next = null;
    } else {
      current = this.getNode(position) as DoubleNode<T>;
      // 改变current的前后指针的指向
      current.next!.prev = current.prev;
      current.prev!.next = current.next;
    }
    this.size--;
    return current?.value ?? null;
  }
}

const dLinkedList = new DoubleLinkedList<string>();
dLinkedList.append('aaa');
dLinkedList.append('bbb');
dLinkedList.append('ccc');
dLinkedList.append('ddd');
dLinkedList.prepend('1');
dLinkedList.insert('insert', 2);
dLinkedList.removeAt(0);
dLinkedList.removeAt(5);
dLinkedList.removeAt(2);
console.log(dLinkedList.get(2));
dLinkedList.update('修改', 1);
console.log(dLinkedList.indexOf('ddd'));
dLinkedList.remove('ddd');
dLinkedList.traverse();
// dLinkedList.postTraverse();
```

## 堆结构（Heap）

### 概念

![](/images/algorithm/堆.png)
![](/images/algorithm/堆图.png)

### 堆结构优势

![](/images/algorithm/堆优势.png)

**堆结构通常用来解决 Top K 问题（在一组数据中，找出最前面的 K 个最大/ 最小的元素）**

### 堆结构常见属性

![](/images/algorithm/堆属性1.png)
![](/images/algorithm/堆属性2.png)
![](/images/algorithm/堆属性3.png)

### 封装堆结构

```typescript
export default class Heap<T> {
  // 属性
  protected data: T[] = []; // 泛型数组：存储堆中元素
  protected length: number = 0; // 当前堆中元素的数量
  protected isMax: boolean;

  constructor(arr: T[] = [], isMax = true) {
    this.isMax = isMax;
    if (arr.length === 0) return;
    this.buildHeap(arr);
  }

  // 私有工具方法--交换i 和 j位置
  private swap(i: number, j: number) {
    const temp = this.data[i];
    this.data[i] = this.data[j];
    this.data[j] = temp;
  }

  // 插入元素--每次插入元素后，需要对堆重构，以维护最大堆的性质
  // 将新元素（67）直接添加到数组的最后位置
  // 检测是否符合最大堆的特性
  // 将新插入的元素，进行上滤操作
  // --①循环 将新元素和父元素比较: 新元素索引：data.length-1  父元素索引：Math.floor((index - 1) / 2)
  // 情况1：新元素<父元素，break
  // 情况2：新元素>=父元素,调用swap交换位置，索引更新为父元素索引
  // index<0时，循环结束

  insert(value: T) {
    this.data.push(value);
    this.length++;
    // 最后位置的元素上滤操作
    this.heapifyUp();
  }

  // 上滤
  private heapifyUp() {
    let index = this.length - 1; // 新元素
    while (index > 0) {
      let parentIndex = Math.floor((index - 1) / 2); // 父元素
      if (this.data[index] < this.data[parentIndex]) {
        break;
      } else {
        this.swap(index, parentIndex);
        index = parentIndex;
      }
    }
  }

  // 去除（提取）元素
  //  让一个元素不符合最大堆即可（数组中最后一个元素提到首位（完全二叉树的最后一个元素））
  // 下滤操作：将该元素进行下滤--循环操作
  // ①index=0
  // ②左子节点的索引：2*index+1
  // ③右子节点的索引：2*index+2
  // ④比较左右子节点，找到较大值
  // --如果较大值<index元素，break
  // --如果较大值>index元素,交换较大与index位置，更新index值
  // 循环结束条件：左子节点索引（2*index+1）<length
  extract(): T | undefined {
    if (this.length === 0) return undefined;
    if (this.length === 1) {
      this.length--;
      return this.data.shift();
    }

    const topValue = this.data[0];
    this.data[0] = this.data.pop()!;
    this.length--;

    // 下滤操作
    this.heapifyDown(0);

    return topValue;
  }

  // 下滤
  private heapifyDown(start: number) {
    let index = start;
    while (2 * index + 1 < this.length) {
      let leftChildInd = 2 * index + 1;
      let rightChildInd = 2 * index + 2;
      let largerIndex = leftChildInd;
      //   比较左右子节点，找到较大值
      if (
        rightChildInd < this.length &&
        this.data[leftChildInd] < this.data[rightChildInd]
      ) {
        largerIndex = rightChildInd;
      }
      // 如果较大值<index元素，break
      if (this.data[index] > this.data[largerIndex]) break;
      // 交换位置
      this.swap(index, largerIndex);
      index = largerIndex;
    }
  }

  // 返回最大 / 最小值
  peek(): T | undefined {
    return this.data[0];
  }

  size() {
    return this.length;
  }

  isEmpty() {
    return this.length === 0;
  }

  buildHeap(arr: T[]) {
    this.data = arr;
    this.length = arr.length;

    // 从第一个非叶子节点,进行下滤操作
    const start = Math.floor(this.length / 2 - 1);
    for (let i = start; i >= 0; i--) {
      this.heapifyDown(i);
    }
  }
}

// const arr = [9, 11, 20, 56, 23, 45];
// const heap = new Heap<number>(arr);

// console.log(heap);

// heap.buildHeap(arr);
// console.log(arr); // [ 56, 23, 45, 11, 9, 20 ]

// for (const item of arr) {
//   heap.insert(item);
// }

// console.log(heap.data);
// console.log(heap.extract());
// console.log(heap.data);
```

### 原地建堆（in-place heap construction）

指建立堆的过程中，不使用额外的内存空间，直接在原有数组上进行操作

从第一个非叶子节点开始,进行**下滤**操作

```typescript
buildHeap(arr: T[]) {
    this.data = arr;
    this.length = arr.length;

    // 从第一个非叶子节点,进行下滤操作
    const start = Math.floor((this.length / 2 ) - 1 );
    for (let i = start; i >= 0; i--) {
      this.heapifyDown(i);
    }
  }

const arr = [9, 11, 20, 56, 23, 45];
const heap = new Heap<number>();

// heap.buildHeap(arr);
// console.log(arr); // [ 56, 23, 45, 11, 9, 20 ]

```

### 实现最小堆：修改 上滤 / 下滤 方法

```typescript
// 上滤
  private heapifyUp() {
    let index = this.length - 1; // 新元素
    while (index > 0) {
      let parentIndex = Math.floor((index - 1) / 2); // 父元素
      if (this.data[index] >= this.data[parentIndex]) {
        break;
      } else {
        this.swap(index, parentIndex);
        index = parentIndex;
      }
    }
  }

  // 下滤
  private heapifyDown(start: number) {
    let index = start;
    while (2 * index + 1 < this.length) {
      let leftChildInd = 2 * index + 1;
      let rightChildInd = 2 * index + 2;
      let largerIndex = leftChildInd;
      //   比较左右子节点，找到较大值
      if (
        rightChildInd < this.length &&
        this.data[leftChildInd] >= this.data[rightChildInd]
      ) {
        largerIndex = rightChildInd;
      }
      // 如果较大值<index元素，break
      if (this.data[index] <= this.data[largerIndex]) break;
      // 交换位置
      this.swap(index, largerIndex);
      index = largerIndex;
    }
  }
```

## 双端队列（Deque）

双端队列在单向队列的基础上解除了一部分限制：允许在队列的两端添加（入队）和删除（出队）元素

### 实现双端队列

```typescript
import ArrayQueue from './Queue';

class ArrayDeque<T> extends ArrayQueue<T> {
  // 头部追加元素
  addFront(value: T) {
    this.data.unshift(value);
  }

  // 尾部删除元素
  removeBack(): T | undefined {
    return this.data.pop();
  }
}

const deque = new ArrayDeque<string>();
deque.enqueue('aaa');
deque.enqueue('bbb');
deque.enqueue('vvv');
deque.enqueue('ggg');
deque.enqueue('hhh');

while (!deque.isEmpty()) {
  console.log(deque.removeBack());
}
```

## 优先级队列(Priority Queue)

- 是一种比普通队列更加高效的数据结构
- 每次出队的元素是具有最高优先级的，可理解位元素按关键字进行排序
- 优先级队列可以用数组、链表等数据结构实现，堆是最常用的实现方式

### 实现优先级队列

- 方法一：创建优先级节点，保存在堆结构中

```typescript
import Heap from './封装堆结构';

class PriorityNode<T> {
  constructor(public value: T, public priority: number) {}

  valueOf() {
    return this.priority;
  }
}

class PriorityQueue<T> {
  private heap: Heap<PriorityNode<T>> = new Heap();

  enqueue(value: T, priority: number) {
    const newNode = new PriorityNode(value, priority);
    this.heap.insert(newNode);
  }

  // 取出最大值
  dequeue(): T | undefined {
    return this.heap.extract()?.value;
  }

  peek(): T | undefined {
    return this.heap.peek()?.value;
  }

  isEmpty() {
    return this.heap.isEmpty();
  }

  size() {
    return this.heap.size();
  }
}

const pQueue = new PriorityQueue<string>();
pQueue.enqueue('qq', 12);
pQueue.enqueue('ee', 32);
pQueue.enqueue('gg', 78);
pQueue.enqueue('hh', 1);

while (!pQueue.isEmpty()) {
  console.log(pQueue.dequeue());
}
```

- 方法二：不创建节点

```typescript
class PriorityQueue<T> {
  private heap: Heap<T> = new Heap();

  enqueue(value: T) {
    this.heap.insert(value);
  }

  // 取出最大值
  dequeue(): T | undefined {
    return this.heap.extract();
  }

  peek(): T | undefined {
    return this.heap.peek();
  }

  isEmpty() {
    return this.heap.isEmpty();
  }

  size() {
    return this.heap.size();
  }
}

class Student {
  constructor(public name: string, public score: number) {}

  valueOf() {
    return this.score;
  }
}

const pQueue = new PriorityQueue<Student>();
pQueue.enqueue(new Student('qq', 12));
pQueue.enqueue(new Student('ee', 32));
pQueue.enqueue(new Student('gg', 78));
pQueue.enqueue(new Student('hh', 1));

console.log(pQueue.peek());

while (!pQueue.isEmpty()) {
  console.log(pQueue.dequeue());
}
```

## 平衡树

![](/images/algorithm/平衡树概念.png)
![](/images/algorithm/平衡树图.png)

**如何让树变得相对平衡**

在随机插入或删除元素后，通过某种方式观察树是否平衡，如果不平衡通过特定的方式（例如旋转），让树保持平衡。

![](/images/algorithm/平衡树应用.png)

### 常见的平衡二叉搜索树

![](/images/algorithm/平衡树分类.png)

### AVL 树

![](/images/algorithm/avl.png)

#### AVL 旋转情况

![](/images/algorithm/旋转.png)

**封装步骤整理**

![](/images/algorithm/avl封装.png)

##### 左左情况

![](/images/algorithm/左左.png)

TODO...待补充

## 排序算法

### 常见排序算法

- 冒泡排序
- 选择排序
- 插入排序
- 归并排序
- 快速排序
- 堆排序
- 希尔排序
- 计数排序
- 桶排序
- 基数排序
- 内省排序
- 平滑排序

### 排序算法标准

![](/images/algorithm/排序标准.png)
![](/images/algorithm/排序复杂度.png)

---

### 冒泡排序（Bubble Sort）

![](/images/algorithm/冒泡排序.png)

#### 冒泡排序图解

![](/images/algorithm/冒泡图解.png)

#### 代码实现

```typescript
function bubbleSort(arr: number[]): number[] {
  const n = arr.length;
  for (let i = 0; i < n; i++) {
    let swappped = false;

    for (let j = 0; j < n - 1 - i; j++) {
      if (arr[j] > arr[j + 1]) {
        //   es6交换语法
        [arr[j], arr[j + 1]] = [arr[j + 1], arr[j]];
        swappped = true;
      }
    }
    // 如果在前一轮无任何交换，就不用继续循环
    if (!swappped) break;
  }

  return arr;
}

console.log(bubbleSort([12, 32, 1, 43, 5, 23]));
```

**时间复杂度**

![](/images/algorithm/冒泡复杂度.png)

---

### 选择排序（Selection Sort）

![](/images/algorithm/选择概念.png)

**堆排序是选择排序的一种优化手段**

#### 思路

![](/images/algorithm/选择思路.png)
![](/images/algorithm/选择图解.png)

#### 代码实现

```typescript
function selectionSort(arr: number[]): number[] {
  const n = arr.length;

  for (let i = 0; i < n; i++) {
    let minIndex = i;
    for (let j = 1 + i; j < n; j++) {
      if (arr[minIndex] > arr[j]) {
        minIndex = j;
      }
    }
    if (minIndex !== i) swap(arr, minIndex, i);
  }
  return arr;
}

console.log(selectionSort([12, 32, 1, 43, 5, 23]));
```

**时间复杂度**

![](/images/algorithm/选择复杂度.png)

---

### 插入排序（Insertion Sort）

![](/images/algorithm/插入概念.png)
![](/images/algorithm/插入图解.png)

#### 代码实现

```typescript
function insertSort(arr: number[]): number[] {
  const n = arr.length;

  for (let i = 1; i < n; i++) {
    const newVal = arr[i];
    let j = i - 1;
    while (arr[j] > newVal && j >= 0) {
      arr[j + 1] = arr[j];
      j--;
    }
    arr[j + 1] = newVal;
  }
  return arr;
}

console.log(insertSort([12, 32, 1, 43, 5, 23]));
```

**时间复杂度**

![](/images/algorithm/插入复杂度.png)

---

### 归并排序(merge sort)

![](/images/algorithm/归并1.png)
![](/images/algorithm/归并图.png)

#### 思路

![](/images/algorithm/归并思路.png)

#### 代码实现

**方式一**

```typescript
function mergeSort(arr: number[]): number[] {
  if (arr.length <= 1) return arr;
  // 分解成两个数组
  const mid = Math.floor(arr.length / 2);

  const leftArr = arr.slice(0, mid);
  const rightArr = arr.slice(mid);

  // 递归切割leftArr rightArr
  const newLeftArr = mergeSort(leftArr);
  const newRightArr = mergeSort(rightArr);

  // 合并
  // 定义双指针
  const newArr: number[] = [];
  let i = 0;
  let j = 0;
  while (i < newLeftArr.length && j < newRightArr.length) {
    if (newLeftArr[i] <= newRightArr[j]) {
      newArr.push(newLeftArr[i]);
      i++;
    } else {
      newArr.push(newRightArr[j]);
      j++;
    }
  }

  // 如果左侧循环完，还有剩余元素
  if (i < newLeftArr.length) {
    newArr.push(...newLeftArr.slice(i));
  }

  // 如果右侧循环完，还有剩余元素
  if (j < newRightArr.length) {
    newArr.push(...newRightArr.slice(j));
  }

  return newArr;
}

console.log(mergeSort([12, 2, 45, 23, 63, 76, 11, 33]));
```

**方式二**

```typescript
function mergeSort2(arr: number[]): number[] {
  const n = arr.length;
  mergeSortInternal(arr, 0, n - 1);
  return arr;
}

function mergeSortInternal(arr: number[], left: number, right: number): void {
  if (left >= right) {
    // 如果区间只有一个元素或为空，返回
    return;
  }

  const mid = left + Math.floor((right - left) / 2);
  // 递归对左右两个子区间进行排序
  mergeSortInternal(arr, left, mid);
  mergeSortInternal(arr, mid + 1, right);
  // 将排好序的左右两个子区间进行合并
  merge(arr, left, mid, right);
}

// 将已排好序的左右两个子区间合并成一个有序的区间
function merge(arr: number[], left: number, mid: number, right: number): void {
  const temp = new Array(right - left + 1);
  let i = left,
    j = mid + 1,
    k = 0;

  // 比较左右两个子区间的元素，将较小的元素插入到temp中
  while (i <= mid && j <= right) {
    if (arr[i] <= arr[j]) {
      temp[k++] = arr[i++];
    } else {
      temp[k++] = arr[j++];
    }
  }

  while (i <= mid) {
    temp[k++] = arr[i++];
  }

  while (j <= right) {
    temp[k++] = arr[j++];
  }

  for (let p = 0; p < temp.length; p++) {
    arr[left + p] = temp[p];
  }
}

console.log(mergeSort2([12, 2, 45, 23, 63, 76, 11, 33]));
```

**时间复杂度**

![](/images/algorithm/归并复杂度.png)

---

### 快速排序（Quick Sort）

![](/images/algorithm/快速排序.png)

![](/images/algorithm/快速排序图.png)

#### 实现思路

![](/images/algorithm/快排思路.png)

#### 代码实现

```typescript
function swap(arr: number[], i: number, j: number) {
  const temp = arr[i];
  arr[i] = arr[j];
  arr[j] = temp;
}

function quickSort(arr: number[]): number[] {
  partition(0, arr.length - 1);

  function partition(left: number, right: number) {
    if (left >= right) return; // 结束条件

    // 找到基准元素(pivot轴心)
    const pivot = arr[right];

    // 双指针进行交换操作
    let i = left;
    let j = right - 1;

    while (i <= j) {
      while (arr[i] < pivot) {
        i++;
      }

      while (arr[j] > pivot) {
        j--;
      }

      if (i <= j) {
        swap(arr, i, j);
        i++;
        j--;
      }
    }

    swap(arr, i, right);

    partition(left, j);
    partition(i + 1, right);
  }

  return arr;
}

console.log(quickSort([12, 32, 1, 4, 62, 87, 24]));
```

**时间复杂度**

![](/images/algorithm/快排复杂度.png)

---

### 堆排序（Heap Sort）

![](/images/algorithm/堆排序.png)

#### 思路分析

![](/images/algorithm/堆排序思路.png)

![](/images/algorithm/堆排序思路2.png)

#### 代码实现

```typescript
function heapSort(arr: number[]): number[] {
  // 获取数组的长度
  const n = arr.length;
  // 对arr进行原地建堆
  // 从第一个非叶子节点进行下滤操作
  const start = Math.floor(n / 2 - 1);
  for (let i = start; i >= 0; i--) {
    // 下滤操作
    heapifyDown(arr, n, i);
  }

  // 对最大堆进行排序--将第一个值和最后一个值互换位置，再进行下滤操作（length-1）
  for (let i = n - 1; i >= 0; i--) {
    swap(arr, 0, i);
    heapifyDown(arr, i, 0);
  }
  return arr;
}

/**
 *
 * @param arr 下滤操作的数组
 * @param n 下滤操作的数组length
 * @param index 下滤操作的index
 */
function heapifyDown(arr: number[], n: number, index: number) {
  while (2 * index + 1 < n) {
    // 获取左右子节点的索引
    const leftChildIndex = 2 * index + 1;
    const rightChildIndex = 2 * index + 2;

    // 找出左右子节点中较大值
    let largerIndex = leftChildIndex;
    if (rightChildIndex < n && arr[leftChildIndex] < arr[rightChildIndex]) {
      largerIndex = rightChildIndex;
    }

    // 比较arr[index]和arr[largerIndex]
    if (arr[index] >= arr[largerIndex]) break;
    // 交换位置
    swap(arr, index, largerIndex);
    index = largerIndex;
  }
}

console.log(heapSort([12, 32, 1, 42, 62, 78, 2]));
```

**时间复杂度**

![](/images/algorithm/堆排序复杂度.png)

---

### 希尔排序

![](/images/algorithm/希尔排序.png)

![](/images/algorithm/希尔效率.png)

![](/images/algorithm/希尔做法.png)

#### 代码实现

```typescript
function shellSort(arr: number[]): number[] {
  const n = arr.length;

  // 选择不同的增量（步长 / 间隔）
  let gap = Math.floor(n / 2);
  console.log(gap);

  // 循环1:不断改变步长
  while (gap > 0) {
    // 循环2:找到不同的队列集合进行插入排序的操作
    // 获取到不同的gap，使用gap进行插入排序
    for (let i = gap; i < n; i++) {
      let j = i;
      const num = arr[i];

      // 循环3:对数列进行插入排序
      // 使用num向前去招一个比num小的值
      while (j > gap - 1 && num < arr[j - gap]) {
        arr[j] = arr[j - gap];
        j = j - gap;
      }
      arr[j] = num;
    }
    gap = Math.floor(gap / 2);
  }

  return arr;
}

console.log(shellSort([87, 2, 43, 1, 4, 56, 12, 64, 83, 76]));
```

## 补充

### 1.对象的值比较(类实现 valueOf 方法)

默认情况下，两个对象不能比较大小，添加 valueof 方法实现值比较

即使两个对象值相等，如==、===，无法用 valueof 实现相等比较

```typescript
class Person {
  name: string;
  age: number;

  constructor(name: string, age: number) {
    this.name = name;
    this.age = age;
  }

  // 给类添加valueOf方法,实例化对象就可以进行值比较
  valueOf() {
    return this.age;
  }
}

// 定义类使用语法糖写法，与Person类效果相同
class Product {
  constructor(public name: string, public price: number) {}
  valueOf() {
    return this.price;
  }
}

const p1 = new Person('test', 12);
const p2 = new Person('test2', 13);

console.log(p1 < p2); // true
console.log(p2 == p3); // false
console.log(p2 === p3); // false
```

### 2.类初始变量定义与赋值的两种方式

```typescript
// 方式一
class PriorityNode<T> {
  priority: number;
  value: T;

  constructor(value: T, priority: number) {
    this.value = value;
    this.priority = priority;
  }
}

// 方式二： 语法糖
class PriorityNode<T> {
  constructor(public value: T, public priority: number) {}
}
```
