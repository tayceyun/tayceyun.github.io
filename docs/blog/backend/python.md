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

  # discard 删除元素
  s1.discard(2)

  # 并集： union 等同于 the | operator
  set1 = {1, 2, 3}
  set2 = {3, 4, 5}
  set3 = {5, 6, 7}
  union_set = set1.union(set2, set3)
  print(union_set) # Output: {1, 2, 3, 4, 5, 6, 7}
  # Using the | operator
  union_set = set1 | set2 | set3
  print(union_set) # Output: {1, 2, 3, 4, 5, 6, 7}

  # 交集：intersection 等同于 the & operator
  set1 = {1, 2, 3}
  set2 = {2, 3, 4}
  set3 = {3, 4, 5}
  intersection_set = set1.intersection(set2, set3)
  print(intersection_set)  # Output: {3}
  # Using the & operator
  intersection_set = set1 & set2 & set3
  print(intersection_set) # Output: {3}
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

#### `lambda` 匿名函数

lambda 是一个表达式（expression），并不是一个语句（statement）

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

# 在列表内部使用示例
# [0, 1, 4, 9, 16, 25, 36, 49, 64, 81]
print([(lambda x: x*x)(x) for x in range(10)])

# lambda 可以被用作某些函数的参数
list1 = [(1, 20), (3, 0), (9, 10), (2, -1)]
list1.sort(key=lambda x: x[1])  # 按列表中元祖的第二个元素排序
# [(2, -1), (3, 0), (9, 10), (1, 20)]
print(list1)
```

根据字典的值进行从高到低排序

```python
d = {'mike': 10, 'lucy': 2, 'ben': 30}

# dict_items([('mike', 10), ('lucy', 2), ('ben', 30)])
print(d.items())

# [('ben', 30), ('mike', 10), ('lucy', 2)]
print(sorted(d.items(), key=lambda x: x[1], reverse=True))
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

#### `all()`

检查可迭代对象（例如列表、元组或集合）中的所有元素是否为 True。如果所有元素均为 True，则返回 True，否则返回 False。如果可迭代对象为空，则 all() 返回 True。

```python
numbers = [1, 2, 3, 4, 5]
result = all(numbers)
print(result)  # Output: True

empty = []
result = all(empty)
print(result)  # Output: True
```

#### ` [start:stop:step]`

可以在列表、元组、字符串中使用

```python
original_string = "Hello, World!"
reversed_string = original_string[::-1]
print(reversed_string)  # Output: !dlroW ,olleH

original_list = [1, 2, 3, 4, 5]
reversed_list = original_list[::-1]
print(reversed_list)  # Output: [5, 4, 3, 2, 1]

original_tuple = (1, 2, 3, 4, 5)
reversed_tuple = original_tuple[::-1]
print(reversed_tuple)  # Output: (5, 4, 3, 2, 1)
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

### 函数中访问 / 修改内部变量

```python
# 全局变量，可以在文件内的任何地方被访问
MIN_VALUE = 1


# Python 的解释器会默认函数内部的变量为局部变量，但是又发现局部变量 MIN_VALUE 并没有声明，因此就无法执行相关操作。所以，如果要在函数内部改变全局变量的值，加上 global 声明
def validation_check(value):
    # 不能在函数内部随意改变全局变量的值
    global MIN_VALUE
    MIN_VALUE += value


validation_check(5)
# 6
print(MIN_VALUE)
```

### 嵌套函数中：内部函数修改外部函数变量

在内部函数中修改外部函数变量前，使用关键字`nonlocal`

```python
def outer():
    x = "local"
    def inner():
        nonlocal x
        x = 'nonlocal'
        print("inner:", x)
    inner()
    print("outer:", x)


# inner: nonlocal
# outer: nonlocal
outer()
```

如果没有 `nonlocal` 关键字，而内部函数的变量又和外部函数变量同名，**内部函数变量会覆盖外部函数的变量**。

```python
def outer():
    x = "local"

    def inner():
        x = 'inner--ttt'
        print("inner:", x)
    inner()
    print("outer:", x)


# inner: inner--ttt
# outer: local
outer()
```

### 闭包

```python
def nth_power(exponent):
    def exponent_of(base):
        return base ** exponent
    return exponent_of


# 计算一个数的平方 9
print(nth_power(2)(3))
# 计算一个数的立方 27
print(nth_power(3)(3))
```

### 面向对象编程(object oriented programming)

四要素： 类、属性、函数（方法）、对象（实例）

一个简单的类 示例：

```python
class Document:
    # 定义常量
    CONSTANT_STR = '每个实例对象都可以访问的常量,书名：{}'

    # 构造函数：对象生成时会被自动调用
    def __init__(self, title, author, context):
        print('init function')
        self.title = title
        self.author = author
        # __context ： 私有属性，在类函数之外无法访问和修改
        self.__context = context

    # 类函数 cls:在类方法中引用类本身
    @classmethod
    def create_empty_book(cls, title, author):
        return cls(title=title, author=author, context='nothing')

    # 成员函数
    def get_context_length(self):
        # print: 3 每个实例对象都可以访问的常量
        print(len(self.__context))

    # 静态函数
    @staticmethod
    def get_constant_name(context):
        return Document.CONSTANT_STR.format(context)


test_book = Document('ttt', 'name', '111')

# 3
test_book.get_context_length()

# ttt
print(test_book.title)

# 报错：AttributeError: 'Document' object has no attribute '__context'
# print(test_book.__context)

# print: 每个实例对象都可以访问的常量,书名：ttt
print(test_book.get_constant_name(test_book.title))
```

#### 类的继承

一个类既拥有另一个类的特征，也拥有不同于另一个类的独特特征

```python
class WordDocument(Document):
    def __init__(self, title, author, context, word_type):
        self.type = word_type
        super().__init__(title, author, context)

    def transfer_type(self, new_value):
        self.type = new_value
        print('new type is {}'.format(self.type))
        print(f'test {self.type}')


word_doc = WordDocument('son_doc', 'son_author', 'son_context', 'son_type')

word_doc.transfer_type('新的类型')
```

#### 补充：引擎是如何工作的？

一个搜索引擎由搜索器、索引器、检索器和用户接口四个部分组成。

搜索器（爬虫 scrawler），在互联网上大量爬取各类网站的内容，送给索引器。索引器拿到网页和内容后，会对内容进行处理，形成索引（index），存储于内部的数据库等待检索。用户接口指网页和 App 前端界面。用户通过用户接口，向搜索引擎发出询问（query），询问解析后送达检索器；检索器高效检索后，再将结果返回给用户。

```python
# SearchEngineBase 引擎基类，继承的类分别代表不同的算法引擎
class SearchEngineBase(object):
    def __init__(self):
        pass

    # 读取文件内容，将文件路径作为 ID，连同内容一起送到 process_corpus 中。
    def add_corpus(self, file_path):
        with open(file_path, 'r') as fin:
            text = fin.read()
            self.process_corpus(file_path, text)

    # 索引器，对内容进行处理，然后文件路径为 ID ，将处理后的内容存下来。处理后的内容就叫做索引（index）。
    def process_corpus(self, id, text):
        raise Exception('process_corpus not implemented')

    # 检索器：给定一个询问，处理询问，再通过索引检索，然后返回。
    def search(self, query):
        raise Exception('search not implemented')


# 提供搜索器和用户接口
def main(search_engine):
    for file_path in ['1.txt', '2.txt', '3.txt', '4.txt', '5.txt']:
        search_engine.add_corpus(file_path)

    while True:
        query = input()
        results = search_engine.search(query)
        print('found {} result(s):'.format(len(results)))
        for result in results:
            print(result)


class SimpleEngine(SearchEngineBase):
    def __init__(self):
        super(SimpleEngine, self).__init__()
        self.__id_to_texts = {}

    def process_corpus(self, id, text):
        self.__id_to_texts[id] = text

     def search(self, query):
         results = []
         for id, text in self.__id_to_texts.items():
             if query in text:
                results.append(id)
                return results

search_engine = SimpleEngine()
main(search_engine)
```

#### 扩展：LRU Cache （Least Recently Used）

How LRU Cache Works?

1. Capacity: The cache has a fixed maximum capacity.
2. Order of Usage: Items in the cache are ordered by their usage, with the most recently used items at the front and the least recently used items at the back.
3. Eviction: When the cache reaches its capacity and a new item is added, the least recently used item is evicted to make space.

Python 的 functools 模块提供了一种使用 @lru_cache 装饰器创建 LRU 缓存的内置方法。

```python
from functools import lru_cache

@lru_cache(maxsize=3)
def expensive_function(x):
    print(f"Computing {x}...")
    return x * x

print(expensive_function(2))  # Computes and caches the result
print(expensive_function(3))  # Computes and caches the result
print(expensive_function(4))  # Computes and caches the result
print(expensive_function(2))  # Retrieves the result from cache
print(expensive_function(5))  # Computes and caches the result, evicting the least recently used entry
```

自定义 LRU 缓存

```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        else:
            # Move the accessed item to the end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            # Update the value and move to the end
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            # Pop the first item (least recently used)
            self.cache.popitem(last=False)

# Example usage
cache = LRUCache(2)
cache.put(1, 1)
cache.put(2, 2)
print(cache.get(1))  # Returns 1
cache.put(3, 3)      # Evicts key 2
print(cache.get(2))  # Returns -1 (not found)
cache.put(4, 4)      # Evicts key 1
print(cache.get(1))  # Returns -1 (not found)
print(cache.get(3))  # Returns 3
print(cache.get(4))  # Returns 4
```

### 函数 / 闭包

函数也是对象。可以把函数赋予变量

```python
def func(message):
    print('func message:{}'.format(message))
    return message


send_message = func

# func message:ttt
send_message('ttt')


# 类比js中的高阶函数
def get_message_length(message):
    return len(func(message))


print(get_message_length('ttt1'))


# 闭包
def get_msg_list(message):
    def transfer_list(message):
        return message.split(',')

    return transfer_list(message)


# ['hello', 'ttt']
print(get_msg_list('hello,ttt'))
```

### 装饰器

#### 简单的示例

```python
def my_decorator(func):
    def wrapper():
        print('wrapper of decorator')
        func()
    return wrapper


@my_decorator
def greet():
    print('hello world')


greet()
```

#### 带有参数的装饰器

```python
import functools


def authorize_decorator(required_roles):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(user, *args, **kwargs):
            # Step 3: Define the wrapper function
            if not set(required_roles).issubset(set(user.get('roles', []))):
                raise PermissionError("User does not have the required roles")
            return func(user, *args, **kwargs)
        return wrapper
    return decorator


@authorize_decorator(['admin', 'editor'])
def edit_content(user, content):
    print(f"Content edited: {content}")


# Example users
admin_user = {'name': 'Tayce', 'roles': ['admin', 'editor']}
guest_user = {'name': 'Guest', 'roles': ['guest']}

edit_content(admin_user, "New content")  # This should work
try:
    edit_content(guest_user, "New content")  # This should raise a PermissionError
except PermissionError as e:
    print(e)
```

#### 类装饰器

类装饰器主要依赖于函数`__call__()`，每调用一个类的实例时，函数`__call__()`就会被执行一次。

### `__name__`

#### 理解`__name__`

- `__name__`是 Python 中的一个特殊属性，它表示当前文件或模块的名称。
- 当一个 Python 脚本作为主文件或者主模块被直接运行时，`__name__` 的值就是 `__main__`。
- 而当该脚本被其他模块导入时，即`__name__`位于次文件（被导入的文件）中，则执行`__name__`时返回的值就是导入的文件名。

#### 用途

- 用于判断当前模块是否作为主模块运行，从而执行不同的逻辑。
- 在被导入的模块中，根据 `__name__` 的值来控制某些代码是否执行，例如只在模块自身运行时执行一些测试或示例代码。

示例：

```python
# example.py

def main():
    print("This is the main function.")

if __name__ == "__main__":
    # This block will only execute if this script is run directly
    main()
```

```python
# another_script.py

import example

# The code here does not trigger the execution of example.main() because
# example.py is imported as a module and its __name__ is now 'example'.
```

### `@functools.wraps`的作用

```python
import functools


def my_decorator(func):
    @functools.wraps(func)  # Ensure wrapper looks like the original function
    def wrapper(*args, **kwargs):
        print(f"Calling function {func.__name__}")
        return func(*args, **kwargs)
    return wrapper


@my_decorator
def greet(name):
    """greet introduction"""
    return f"Hello, {name}!"


# 如果未使用@functools.wraps(func)  print: wrapper / None
print(greet.__name__)
print(greet.__doc__)

# 使包装函数的行为接近原始函数 使用@functools.wraps(func) print: greet / greet introduction
print(greet.__name__)
print(greet.__doc__)
```

TODO 18.metaclass
