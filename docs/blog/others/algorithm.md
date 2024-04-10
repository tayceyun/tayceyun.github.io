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
