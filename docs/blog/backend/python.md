---
sidebar: auto
tags:
  - python
---

## Python 学习 📑

### 常见值类型

- Number
  - 整数：10
  - 浮点数：1.23
  - 复数：4+3j
  - 布尔：True:1;False:0
  - `%d`：表示整型
  - `float()`：浮点型
  - `int()`：整型
- String

  - 单引号、双引号和三引号这三种表达方式均被支持：`s3 = """hello"""` ; `s2 = "hello"` ; `s1 = 'hello'`

  - `title()`：字符串每个单词的首字母都改为大写
  - `upper()`：全部大写
  - `lower()`：全部小写
  - 字符串使用变量：f-string

    ```python
    age: int = 12

    print(f"年龄：{age}")
    ```

  - 制表符：`\t`
  - 换行符：`\n`
  - `strip()`：去掉字符串的首位空白
  - `lstrip()`：删除字符串开头的空白
  - `rstrip()`：删除字符串末尾的空白
  - `%s`：表示字符串型

- List(列表)

  - 访问列表元素,索引还可以倒序，最后一个元素的索引为-1，倒数第二个元素的索引为-2，以此类推。

    ```python
    ageList = [12, 23, 43, 54]
    # 23 54
    print(ageList[1], ageList[-1])
    ```

  - 获取列表的长度：`len(list)`
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
    for magician in magicians:  # for 循环
        print(magician)
    ```

  - 切片：
    ```python
    l = [1,2,3,4]
    l[0:1] # 返回列表中索引0-1的子列表
    ```

- Tuple:(元组)有序的**不可变**序列

  ```python
  top = (1,2,3,4)
  top[1,2] # 返回元组中索引1-2的子元组
  ```

- Set:(集合)没有键和值的配对、**无序不重复**的集合

  ```python
  s1 = {1, 2, 3}
  s2 = set([1, 2, 3])

  # 增加 {1,2,3,4}
  s1.add(4)

  # 删除 {1, 2, 3}
  s1.remove(4)

  # 删除集合中最后一个元素：pop()
  ```

  注意：集合并不支持索引操作，因为集合本质上是一个哈希表，和列表不一样。

- Dictionary:(字典)有序的 key-value 集合

  ```python
  # 字典的定义方式：
  d1 = {'name': 'jason', 'age': 20, 'gender': 'male'}
  d2 = dict({'name': 'jason', 'age': 20, 'gender': 'male'})
  d3 = dict([('name', 'jason'), ('age', 20), ('gender', 'male')])
  d4 = dict(name='jason', age=20, gender='male')

  d1['name'] # 'jason'
  # get(key, default):如果键不存在，调用 get() 函数可以返回一个默认值。
  d1.get('name') # 'jason'
  d1.get('ttt','null') # 'null'

  # 增加元素
  d1['ttt'] = 'ttt'

  # 删除元素
  d1.pop('ttt')
  ```

### 补充

1️⃣ 列表和元组可以通过 list() 和 tuple() 函数相互转换：

```python
list((1, 2, 3)) # [1, 2, 3]

tuple([1, 2, 3]) # (1, 2, 3)
```

2️⃣ 相比于列表和元组，字典的性能更优，特别是对于查找、添加和删除操作，字典都能在常数时间复杂度内完成。

3️⃣ 判断一个元素在不在字典或集合内，可以用 value in dict/set 来判断。除了创建和访问，字典和集合也同样支持增加、删除、更新等操作。

4️⃣ 常见的转义字符

![](/images/python/转义.png)

```python

s = {1, 2, 3}
1 in s # True

d = {'name': 'jason', 'age': 20}
'name' in d # True

```

4️⃣ 字典和集合的性能：字典和集合的内部结构都是一张哈希表，所以查找、插入和删除操作比较高效

示例 1：比如电商企业的后台，存储了每件产品的 ID、名称和价格。现在的需求是，给定某件商品的 ID，我们要找出其价格。

```python
# 列表 时间复杂度 O(n) / 二分法：O(logn)
def find_product_price(products, product_id):
    for id, price in products:
        if id == product_id:
            return price


products = [
    (143121312, 100),
    (432314553, 30),
    (32421912367, 150)
]

print(find_product_price(products, 432314553))

# dictionary 时间复杂度：O(1)
products = {
    143121312: 100,
    432314553: 30,
    32421912367: 150
}

print(products[432314553])  # 30
```

示例 2：获取这些商品中有多少种不同的价格

```python

# list
def find_unique_price_using_list(products):
    unique_price_list = []
    for _, price in products:  # A
        if price not in unique_price_list:  # B
            unique_price_list.append(price)
            return len(unique_price_list)


products = [
    (143121312, 100),
    (432314553, 30),
    (32421912367, 150),
    (937153201, 30)
]

print(find_unique_price_using_list(products))

# set
def find_unique_price_using_set(products):
    unique_price_set = set()
    for _, price in products:
        unique_price_set.add(price)
    return len(unique_price_set)


products = [
    (143121312, 100),
    (432314553, 30),
    (32421912367, 150),
    (937153201, 30)
]

print(find_unique_price_using_set(products))

```

## 基本语法

### 基础

1. 定义变量：`age: int = 12`

2. 同时给多个变量赋值：`x, y, z = 0, 0, 0`

3. 定义常量：`MAX_CONNECTIONS = 5000`

4. 检测类型：`type(age)`

5. 注释：

```python
# 单行注释

"""
多行注释
111
"""
```

6. 输入输出基础：

`input()` 函数暂停程序运行，同时等待键盘输入；直到回车被按下。

```python
# Prompt the user for input and convert to an integer
age = int(input("Enter your age: "))

# Output the input
print(f"You are {age} years old.")
```

7. JSON 编码与解码：序列化：`json.dumps()` / 反序列化：`json.loads()`

### 条件 & 循环

#### 条件

```python
if condition_1:
statement_1
elif condition_2:
statement_2
else:
statement_n
```

#### 循环

1️⃣ 列表、集合的遍历：`for item in <iterable>:`

2️⃣ 字典的遍历：

```python
d = {'name': 'jason', 'dob': '2000-01-01', 'gender': 'male'}
for k in d: # 遍历字典的键
print(k)

for v in d.values(): # 遍历字典的值
print(v)

for k, v in d.items(): # 遍历字典的键值对
print('key: {}, value: {}'.format(k, v))
```

3️⃣ 遍历时需要索引和元素：

```python
list1 = [1, 2, 3, 4, 5, 6, 7]
for index, item in enumerate(list1):
    if index < 5:
        print(index, item)
```

4️⃣ continue & break
continue：程序跳过当前循环，继续执行下面的循环；
break：完全跳出所在的整个循环体

5️⃣ for 循环和 while 循环的效率问题：

`range()`函数是直接由 C 语言写的，调用它速度非常快。而 while 循环中的“i+= 1”这个操作，得通过 Python 的解释器间接调用底层的 C 语言；并且这个简单的操作，又涉及到了对象的创建和删除（因为 i 是整型，是 immutable，i += 1 相当于 i =new int(i + 1)）。for 循环的效率更胜一筹。

```python
i = 0
while i < 1000000:
    i += 1

for i in range(0, 1000000):
    pass
```

#### 将条件与循环并做一行的写法

例一：`expression1 if condition else expression2 for item in iterable`

等价于：

```python
for item in iterable:
    if condition:
        expression1
    else:
        expression2
```

例二：绘制 y = 2\*|x| + 5 的函数图像，给定集合 x 的数据点，需要计算出 y 的数据集合

`y = [value * 2 + 5 if value > 0 else -value * 2 + 5 for value in x]`

例三：将文件中逐行读取的一个完整语句，按逗号分割单词，去掉首位的空字符，并过滤掉长度小于等于 3 的单词，最后返回由单词组成的列表。

```python
text = ' Today, is, Sunday'
text_list = [s.strip() for s in text.split(',') if len(s.strip()) > 3]
# ['Today', 'Sunday']
print(text_list)
```

例四：

```python
attributes = ['name', 'dob', 'gender']
values = [['jason', '2000-01-01', 'male'],['mike', '1999-01-01', 'male'],['nancy', '2001-02-01', 'female']]

# expected output:
# [{'name': 'jason', 'dob': '2000-01-01', 'gender': 'male'},
# {'name': 'mike', 'dob': '1999-01-01', 'gender': 'male'},
# {'name': 'nancy', 'dob': '2001-02-01', 'gender': 'female'}]

# 一行代码
print([dict(map(lambda x, y: (x, y), attributes, value)) for value in values])

# 方式二
print([dict(zip(attributes,value)) for value in values])

# 多行
result = []
for index, item in enumerate(values):
    result.append({})
    for ind, val in enumerate(attributes):
        result[index][attributes[ind]] = values[index][ind]
print(result)
```

### 函数的使用

#### `map()`

`map(function, iterable, ...)`

```python
# 1.Use map with a lambda function to add corresponding elements
numbers1 = [1, 2, 3]
numbers2 = [4, 5, 6]
summed_numbers = map(lambda x, y: x + y, numbers1, numbers2)
print(list(summed_numbers))  # Output: [5, 7, 9]

# 2.Example using the square function
numbers = [1, 2, 3, 4, 5]
squared_numbers = map(lambda x: x ** 2, numbers)
print(list(squared_numbers))  # Output: [1, 4, 9, 16, 25]

# 3.Use map with the built-in str function to convert each number to a string
numbers = [1, 2, 3, 4, 5]
string_numbers = map(str, numbers)
print(list(string_numbers))  # Output: ['1', '2', '3', '4', '5']
```

#### `lambda`

`lambda arguments: expression`

```python
# Example 1: Lambda function to add 10 to a number
add_ten = lambda x: x + 10
print(add_ten(5))  # Output: 15

# Example 2: Lambda function to multiply two numbers
multiply = lambda x, y: x * y
print(multiply(2, 3))  # Output: 6

# Example 3: Lambda function to return the maximum of two numbers
maximum = lambda x, y: x if x > y else y
print(maximum(4, 7))  # Output: 7
```

#### `filter()`

```python
# Using lambda with filter to get even numbers
numbers = [1, 2, 3, 4, 5, 6]
even_numbers = filter(lambda x: x % 2 == 0, numbers)
print(list(even_numbers))  # Output: [2, 4, 6]
```

#### `reduce()`

```python
from functools import reduce

# Using lambda with reduce to calculate the product of a list of numbers
numbers = [1, 2, 3, 4, 5]
product = reduce(lambda x, y: x * y, numbers)
print(product)  # Output: 120
```

#### `zip()` & Unzipping

`zip(iterable1, iterable2, ...)`

```python
list1 = [1, 2, 3]
list2 = ['a', 'b', 'c']
# [(1, 'a'), (2, 'b'), (3, 'c')]
print(list(zip(list1, list2)))

list1 = [1, 2, 3]
list2 = ['a', 'b']
zipped = zip(list1, list2)
# [(1, 'a'), (2, 'b')]
print(list(zipped))

# * to unzip
zipped = [(1, 'a', True), (2, 'b', False), (3, 'c', True)]
# (1, 'a', True) (2, 'b', False) (3, 'c', True)
print(*zipped)
# [(1, 2, 3), ('a', 'b', 'c'), (True, False, True)]
print(list(zip(*zipped)))

# create a dictionary by zipping together keys and values
keys = ['name', 'age', 'city']
values = ['Alice', 25, 'New York']
dictionary = dict(zip(keys, values))
# {'name': 'Alice', 'age': 25, 'city': 'New York'}
print(dictionary)

#  transpose a matrix (a list of lists) using zip()
matrix = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9]
]
# Use zip with unpacking operator * to transpose the matrix
transposed_matrix = list(zip(*matrix))
# [(1, 4, 7), (2, 5, 8), (3, 6, 9)]
print(transposed_matrix)

# split a list of tuples back into individual lists.
pairs = [(1, 'one'), (2, 'two'), (3, 'three')]
# Use zip with unpacking operator * to unzip
numbers, words = zip(*pairs)
print(numbers)  # Output: (1, 2, 3)
print(words)    # Output: ('one', 'two', 'three')

# handle iterables of different lengths without truncating
from itertools import zip_longest
list1 = [1, 2, 3]
list2 = ['a', 'b']
zipped = zip_longest(list1, list2, fillvalue='N/A')
# Convert the zip_longest object to a list and print it
print(list(zipped))  # Output: [(1, 'a'), (2, 'b'), (3, 'N/A')]
```

#### `reduce()`

```python
from functools import reduce
reduce(function, iterable, [initializer])

from functools import reduce

# List of numbers
numbers = [1, 2, 3, 4, 5]

# Use reduce with a lambda function to sum the numbers
sum_result = reduce(lambda x, y: x + y, numbers)

print(sum_result)  # Output: 15
```

### 异常处理

`try` 和 `except`

```python
# 自定义异常
class NegativeNumberError(Exception):
"""Exception raised when there're errors in input"""
def __init__(self, value): # 自定义异常类型的初始化
self.value = value
def __str__(self): # 自定义异常类型的 string 表达形式
return ("{} is invalid input".format(repr(self.value)))

try:
    number = int(input("Enter a positive number: "))
    if number < 0:
        raise NegativeNumberError("Negative number entered!")
    result = 10 / number
except ZeroDivisionError:
    print("Cannot divide by zero!")
except NegativeNumberError as e:
    print("NegativeNumberError:", e)
else:
    print("The result is:", result)
finally:
    print("This runs no matter what.")
```
