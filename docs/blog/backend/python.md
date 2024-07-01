---
sidebar: auto
tags:
  - python
---

## 常见值类型

- Number
  - 整数：10
  - 浮点数：1.23
  - 复数：4+3j
  - 布尔：True:1;False:0
- String

  - `title()`：字符串每个单词的首字母都改为大写
  - `upper()`：全部大写
  - `lower()`：全部小写
  - 字符串使用变量

    ```python
    age: int = 12

    print(f"年龄：{age}")
    ```

  - 制表符：`\t`
  - 换行符：`\n`
  - `lstrip()`：删除字符串开头的空白
  - `rstrip()`：删除字符串末尾的空白

- List

  - 访问列表元素,索引还可以倒序，最后一个元素的索引为-1，倒数第二个元素的索引为-2，以此类推。

    ```python
    ageList = [12, 23, 43, 54]
    # 23 54
    print(ageList[1], ageList[-1])
    ```

  - 修改列表元素：`ageList[0]=222`
  - 删除列表元素：`del ageList[2]`
  - `append()`：末尾添加元素
  - `pop()`：删除末尾元素
  - `insert(index,item)`：任意位置添加元素
  - 根据值删除列表元素：`remove(item)`；如果列表中有多个重复的值，仅删除第一个符合要求的元素。
  - `sort()`：数组永久排序（改变原数组）

    ```python
    numbers = [3, 1, 2]
    numbers.sort()
    print(numbers) # 输出 [1, 2, 3]

    numbers.sort(reverse=True)
    print(numbers)  # 输出 [3, 2, 1]

    words = ['banana', 'apple', 'cherry']
    words.sort(key=len)
    print(words) # 输出 ['apple', 'banana', 'cherry']

    words = ['banana', 'apple', 'cherry']
    words.sort(key=len, reverse=True)
    print(words)  # 输出 ['banana', 'cherry', 'apple']
    ```

  - `sorted`：数组临时排序（返回一个排序后的列表，不改变原数组），参数与`sort()`相同
  - `reverse()`：列表倒序
  - 列表长度：`len(words)`
  - `count(item)`表示统计列表/元组中 item 出现的次数
  - `index(item)`表示返回列表/元组中 item 第一次出现的索引
  - for 循环

    ```python
    magicians = ['alice', 'david', 'carolina']
    for magician in magicians: # for 循环
        print(magician)
    ```

  - 切片：
    ```python
    l = [1,2,3,4]
    l[0:1] # 返回列表中索引0-1的子列表
    ```

- Tuple:有序的不可变序列

  ```python
  top = (1,2,3,4)

  top[1,2] # 返回元组中索引1-2的子元组
  ```

- Set:无序不重复集合
- Dictionary:无序 key-value 集合

## 基本语法

定义变量：`age: int = 12`

同时给多个变量赋值：`x, y, z = 0, 0, 0`

定义常量：`MAX_CONNECTIONS = 5000`

检测类型：`type(age)`

注释：

```python
# 单行注释

"""
多行注释
111
"""
```
