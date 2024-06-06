---
sidebar: auto
tags:
  - 算法题
---

## 算法题记录

题目来源及学习路径：[代码随想录](https://programmercarl.com/%E6%95%B0%E7%BB%84%E7%90%86%E8%AE%BA%E5%9F%BA%E7%A1%80.html)

## 数组

### 704. 二分查找

给定一个 n 个元素有序的（升序）整型数组 nums 和一个目标值 target ，写一个函数搜索 nums 中的 target，如果目标值存在返回下标，否则返回 -1。

示例 1:
输入: nums = [-1,0,3,5,9,12], target = 9
输出: 4
解释: 9 出现在 nums 中并且下标为 4

示例 2:
输入: nums = [-1,0,3,5,9,12], target = 2
输出: -1
解释: 2 不存在 nums 中因此返回 -1

#### 题解

```js
// 左闭右开
function search(nums: number[], target: number): number {
  let left: number = 0,
    right: number = nums.length;

  while (left < right) {
    const mid = Math.floor((left + right) / 2);

    if (nums[mid] === target) return mid;
    else if (nums[mid] > target) right = mid;
    else left = mid + 1;
  }

  return -1;
}

// 左闭右闭
function search(nums: number[], target: number): number {
  let left: number = 0,
    right: number = nums.length - 1;

  while (left <= right) {
    const mid = Math.floor((left + right) / 2);

    if (nums[mid] === target) return mid;
    else if (nums[mid] > target) right = mid - 1;
    else left = mid + 1;
  }
  return -1;
}
```

### 35. 搜索插入位置 ⭐️

给定一个排序数组和一个目标值，在数组中找到目标值，并返回其索引。如果目标值不存在于数组中，返回它将会被按顺序插入的位置。
请必须使用时间复杂度为 O(log n) 的算法。

示例 1:
输入: nums = [1,3,5,6], target = 5 输出: 2

示例 2:
输入: nums = [1,3,5,6], target = 2 输出: 1

示例 3:
输入: nums = [1,3,5,6], target = 7 输出: 4

#### 题解

```js
var searchInsert = function (nums, target) {
  // 目标值在数组所有元素之前
  // 目标值等于数组某一元素
  // 目标值插入数组中某一位置
  // 目标值在数组所有元素之后
  let left = 0,
    right = nums.length - 1,
    middle = 0;

  while (left <= right) {
    middle = Math.floor((left + right) / 2);
    if (nums[middle] === target) return middle;

    if (nums[middle] > target) right = middle - 1;
    else left = middle + 1;
  }

  return nums[middle] > target ? middle : middle + 1;
};
```

### 34. 在排序数组中查找元素的第一个和最后一个位置

给你一个按照非递减顺序排列的整数数组 nums，和一个目标值 target。请你找出给定目标值在数组中的开始位置和结束位置。
如果数组中不存在目标值 target，返回 [-1, -1]。
你必须设计并实现时间复杂度为 O(log n) 的算法解决此问题。

示例 1：
输入：nums = [5,7,7,8,8,10], target = 8
输出：[3,4]

示例 2：
输入：nums = [5,7,7,8,8,10], target = 6
输出：[-1,-1]

示例 3：
输入：nums = [], target = 0 输出：[-1,-1]

#### 题解

```js
// 解法一
var searchRange = function (nums, target) {
  let left = 0,
    right = nums.length - 1,
    result = [-1, -1];

  while (left <= right) {
    if (nums[left] < target) left++;
    if (nums[right] > target) right--;
    if (nums[left] === target && nums[right] === target) return [left, right];
  }

  return result;
};

// 解法二
var searchRange = function (nums, target) {
  const getLeftBorder = (nums, target) => {
    let left = 0,
      right = nums.length - 1;

    let leftBoard = Infinity;

    while (left <= right) {
      const mid = Math.floor((left + right) / 2);

      if (nums[mid] >= target) {
        right = mid - 1;
        leftBoard = right;
      } else left = mid + 1;
    }
    return leftBoard;
  };

  const getRightBorder = (nums, target) => {
    let left = 0,
      right = nums.length - 1;
    let rightBoard = Infinity;

    while (left <= right) {
      const mid = Math.floor((left + right) / 2);

      if (nums[mid] > target) {
        right = mid - 1;
      } else {
        left = mid + 1;
        rightBoard = left;
      }
    }
    return rightBoard;
  };

  // 获取第一个小于target的下标
  const leftBorder = getLeftBorder(nums, target);
  // 获取第一个大于target的下标
  const rightBorder = getRightBorder(nums, target);

  if (leftBorder === Infinity || rightBorder === Infinity) return [-1, -1];
  if (rightBorder - leftBorder > 1) return [leftBorder + 1, rightBorder - 1];
  return [-1, -1];
};
```

### 69. x 的平方根 ⭐️

给你一个非负整数 x ，计算并返回 x 的 算术平方根 。
由于返回类型是整数，结果只保留 整数部分 ，小数部分将被 舍去 。
注意：不允许使用任何内置指数函数和算符，例如 pow(x, 0.5) 或者 x \*\* 0.5。

示例 1：
输入：x = 4 输出：2

示例 2：
输入：x = 8 输出：2 解释：8 的算术平方根是 2.82842..., 由于返回类型是整数，小数部分将被舍去。

#### 题解

```js
var mySqrt = function (x) {
  let mid = Math.floor(x / 2);

  while (mid * mid > x) {
    mid = Math.floor(mid / 2);
  }

  while (mid * mid <= x) {
    if ((mid + 1) * (mid + 1) <= x) {
      mid = mid + 1;
    } else break;
  }

  return mid;
};
```

### 367. 有效的完全平方数

给你一个正整数 num 。如果 num 是一个完全平方数，则返回 true ，否则返回 false 。
完全平方数 是一个可以写成某个整数的平方的整数。换句话说，它可以写成某个整数和自身的乘积。
不能使用任何内置的库函数，如 sqrt 。

示例 1：
输入：num = 16 输出：true 解释：返回 true ，因为 4 \_ 4 = 16 且 4 是一个整数。

示例 2：
输入：num = 14 输出：false 解释：返回 false ，因为 3.742 \_ 3.742 = 14 但 3.742 不是一个整数。

#### 题解

```js
var isPerfectSquare = function (num) {
let mid = Math.ceil(num / 2)
while ((mid \* mid) > num) {
mid = Math.ceil(mid / 2)
}

    while (mid * mid < num) {
        if (((mid + 1) * (mid + 1)) <= num) {
            mid++
        } else break
    }

    return mid * mid === num

};
```

### 209. 长度最小的子数组（滑动窗口）⭐️

给定一个含有 n 个正整数的数组和一个正整数 target 。
找出该数组中满足其总和大于等于 target 的长度最小的 连续子数组 [numsl, numsl+1, ..., numsr-1, numsr] ，并返回其长度。如果不存在符合条件的子数组，返回 0 。

示例 1：
输入：target = 7, nums = [2,3,1,2,4,3]
输出：2
解释：子数组 [4,3] 是该条件下的长度最小的子数组。

示例 2：
输入：target = 4, nums = [1,4,4]输出：1

示例 3：
输入：target = 11, nums = [1,1,1,1,1,1,1,1]输出：0

#### 题解

```js
function minSubArrayLen(target: number, nums: number[]): number {
  let left = 0,
    right = 0;

  let res = Infinity,
    sum = 0;

  while (right <= nums.length) {
    if (sum < target) {
      // 等同于 sum+=nums[right];right++
      sum += nums[right++];
    } else {
      res = Math.min(res, right - left);
      // 移动慢指针，更新 sum 的值
      sum -= nums[left++];
    }
  }
  return res === Infinity ? 0 : res;
}
```

### 904. 水果成篮 ⭐️

你正在探访一家农场，农场从左到右种植了一排果树。这些树用一个整数数组 fruits 表示，其中 fruits[i] 是第 i 棵树上的水果 种类 。
你想要尽可能多地收集水果。然而，农场的主人设定了一些严格的规矩，你必须按照要求采摘水果：

- 你只有 两个 篮子，并且每个篮子只能装 单一类型 的水果。每个篮子能够装的水果总量没有限制。
- 你可以选择任意一棵树开始采摘，你必须从 每棵 树（包括开始采摘的树）上 恰好摘一个水果 。采摘的水果应当符合篮子中的水果类型。每采摘一次，你将会向右移动到下一棵树，并继续采摘。
- 一旦你走到某棵树前，但水果不符合篮子的水果类型，那么就必须停止采摘。
  给你一个整数数组 fruits ，返回你可以收集的水果的 最大数目。

示例 1：
输入：fruits = [1,2,1]输出：3 解释：可以采摘全部 3 棵树。

示例 2：
输入：fruits = [0,1,2,2]输出：3 解释：可以采摘 [1,2,2] 这三棵树。如果从第一棵树开始采摘，则只能采摘 [0,1] 这两棵树。

示例 3：
输入：fruits = [1,2,3,2,2]输出：4 解释：可以采摘 [2,3,2,2] 这四棵树。如果从第一棵树开始采摘，则只能采摘 [1,2] 这两棵树。

示例 4：
输入：fruits = [3,3,3,1,2,1,1,2,3,3,4]输出：5 解释：可以采摘 [1,2,1,1,2] 这五棵树。

#### 题解

```js
  function totalFruit(fruits: number[]): number {
  const n = fruits.length
  const cnt = new Map<number, number>()

      let left = 0, res = 0
      for (let right = 0; right < n; right++) {
          cnt.set(fruits[right], (cnt.get(fruits[right]) || 0) + 1)

          while (cnt.size > 2) {
              cnt.set(fruits[left], cnt.get(fruits[left]) - 1)
              // 跳出循环条件
              if (cnt.get(fruits[left]) === 0) {
                  cnt.delete(fruits[left])
              }
           // 不断更新慢指针位置，使得慢指针最终不包含被删掉的类型
              left++
          }
          res = Math.max(res, right - left + 1)
      }
      return res

  };
```

### 76. 最小覆盖子串 ⭐️

给你一个字符串 s 、一个字符串 t 。返回 s 中涵盖 t 所有字符的最小子串。如果 s 中不存在涵盖 t 所有字符的子串，则返回空字符串 "" 。
注意：

- 对于 t 中重复字符，我们寻找的子字符串中该字符数量必须不少于 t 中该字符数量。
- 如果 s 中存在这样的子串，我们保证它是唯一的答案。

示例 1：
输入：s = "ADOBECODEBANC", t = "ABC"输出："BANC"解释：最小覆盖子串 "BANC" 包含来自字符串 t 的 'A'、'B' 和 'C'。

示例 2：
输入：s = "a", t = "a"输出："a"解释：整个字符串 s 是最小覆盖子串。

示例 3:
输入: s = "a", t = "aa"输出: ""解释: t 中两个字符 'a' 均应包含在 s 的子串中，因此没有符合条件的子字符串，返回空字符串。

#### 题解

```js
// 记录目标字符种类数，记录单个字符存在数
var minWindow = function (s, t) {
  let needsMap = {};

  for (const chart of t) {
    needsMap[chart] = (needsMap[chart] || 0) + 1;
  }

  let typeList = Object.keys(needsMap).length; // 目标字符种类数
  let left = 0,
    right = 0,
    minLen = Infinity,
    minStr = '';

  while (right < s.length) {
    const rightS = s[right];

    if (rightS in needsMap) {
      needsMap[rightS]--;
      if (needsMap[rightS] === 0) typeList--;
    }
    right++;

    // 窗口已包含所有目标字符，缩小窗口
    while (typeList === 0) {
      if (right - left < minLen) {
        // 更新记录
        minLen = right - left;
        minStr = s.slice(left, right);
      }
      const leftS = s[left];
      if (leftS in needsMap) {
        needsMap[leftS]++;
        if (needsMap[leftS] > 0) typeList++;
      }
      left++;
    }
  }
  return minStr;
};
```

### 54. 螺旋矩阵（模拟行为）

给你一个 m 行 n 列的矩阵 matrix ，请按照 顺时针螺旋顺序 ，返回矩阵中的所有元素。

示例 1：
输入：matrix = [[1,2,3],[4,5,6],[7,8,9]]
输出：[1,2,3,6,9,8,7,4,5]

示例 2：
输入：matrix = [[1,2,3,4],[5,6,7,8],[9,10,11,12]]
输出：[1,2,3,4,8,12,11,10,9,5,6,7]

**思路**

模拟顺时针画矩阵的过程:
填充上行从左到右
填充右列从上到下
填充下行从右到左
填充左列从下到上

#### 题解

```js
function spiralOrder(matrix: number[][]): number[] {
  let top = 0,
    left = 0,
    bottom = matrix.length - 1,
    right = matrix[0].length - 1;
  let result = [];

  while (1) {
    if (left > right) break;
    for (let i = left; i <= right; i++) {
      result.push(matrix[top][i]);
    }
    top++;

    if (top > bottom) break;
    for (let i = top; i <= bottom; i++) {
      result.push(matrix[i][right]);
    }
    right--;

    if (left > right) break;
    for (let i = right; i >= left; i--) {
      result.push(matrix[bottom][i]);
    }
    bottom--;

    if (top > bottom) break;
    for (let i = bottom; i >= top; i--) {
      result.push(matrix[i][left]);
    }
    left++;
  }

  return result;
}
```

### 59. 螺旋矩阵 II

给你一个正整数 n ，生成一个包含 1 到 n2 所有元素，且元素按顺时针顺序螺旋排列的 n x n 正方形矩阵 matrix 。

示例 1：输入：n = 3 输出：[[1,2,3],[8,9,4],[7,6,5]]

示例 2：输入：n = 1 输出：[[1]]

#### 题解

```js
function generateMatrix(n: number): number[][] {
  const result = new Array(n).fill(0).map(() => new Array(n).fill(0));
  let updateNum = 1;

  if (n === 1) return [[1]];

  let left = 0,
    top = 0,
    right = n - 1,
    bottom = n - 1;

  while (updateNum <= n * n) {
    for (let i = left; i <= right; i++) {
      result[top][i] = updateNum++;
    }
    top++;

    for (let i = top; i <= bottom; i++) {
      result[i][right] = updateNum++;
    }
    right--;

    for (let i = right; i >= left; i--) {
      result[bottom][i] = updateNum++;
    }
    bottom--;

    for (let i = bottom; i >= top; i--) {
      result[i][left] = updateNum++;
    }
    left++;
  }

  return result;
}
```

### LCR 146. 螺旋遍历二维数组

给定一个二维数组 array，请返回「螺旋遍历」该数组的结果。
螺旋遍历：从左上角开始，按照 向右、向下、向左、向上 的顺序 依次 提取元素，然后再进入内部一层重复相同的步骤，直到提取完所有元素。

示例 1：
输入：array = [[1,2,3],[8,9,4],[7,6,5]]输出：[1,2,3,4,5,6,7,8,9]

示例 2：
输入：array = [[1,2,3,4],[12,13,14,5],[11,16,15,6],[10,9,8,7]]输出：[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16]

#### 题解

```js
var spiralArray = function (array) {
  if (!array.length || !array[0].length) return [];

  let left = 0,
    right = array[0].length - 1,
    top = 0,
    bottom = array.length - 1;
  let result = [];

  while (1) {
    if (left > right) break;
    for (let i = left; i <= right; i++) {
      result.push(array[top][i]);
    }
    top++;

    if (top > bottom) break;
    for (let i = top; i <= bottom; i++) {
      result.push(array[i][right]);
    }
    right--;

    if (left > right) break;
    for (let i = right; i >= left; i--) {
      result.push(array[bottom][i]);
    }
    bottom--;

    if (top > bottom) break;
    for (let i = bottom; i >= top; i--) {
      result.push(array[i][left]);
    }
    left++;
  }
  return result;
};
```

### 1365. 有多少小于当前数字的数字

给你一个数组 nums，对于其中每个元素 nums[i]，请你统计数组中比它小的所有数字的数目。
换而言之，对于每个 nums[i] 你必须计算出有效的 j 的数量，其中 j 满足 j != i 且 nums[j] < nums[i] 。
以数组形式返回答案。

示例 1：

输入：nums = [8,1,2,2,3]输出：[4,0,1,1,3]

解释：

对于 nums[0]=8 存在四个比它小的数字：（1，2，2 和 3）。

对于 nums[1]=1 不存在比它小的数字。

对于 nums[2]=2 存在一个比它小的数字：（1）。

对于 nums[3]=2 存在一个比它小的数字：（1）。

对于 nums[4]=3 存在三个比它小的数字：（1，2 和 2）。

#### 题解

```js
var smallerNumbersThanCurrent = function (nums) {
  let sortNums = JSON.parse(JSON.stringify(nums));
  sortNums = sortNums.sort((a, b) => a - b);

  let indexMap = new Map();
  for (let i = 0; i < sortNums.length; i++) {
    if (indexMap.has(sortNums[i])) continue;
    indexMap.set(sortNums[i], i);
  }

  return nums.map((v) => indexMap.get(v));
};
```

### 941. 有效的山脉数组

给定一个整数数组 arr，如果它是有效的山脉数组就返回 true，否则返回 false。
让我们回顾一下，如果 arr 满足下述条件，那么它是一个山脉数组：

- arr.length >= 3
- 在 0 < i < arr.length - 1 条件下，存在 i 使得：
- arr[0] < arr[1] < ... arr[i-1] < arr[i]
- arr[i] > arr[i+1] > ... > arr[arr.length - 1]

#### 题解

```js
var validMountainArray = function (arr) {
  let len = arr.length,
    left = 0,
    right = len - 1;
  if (len < 3) return false;
  // 山峰不可以在两端 所以条件为：left < len - 2 / right>1
  while (left < len - 2 && arr[left] < arr[left + 1]) left++;
  while (right > 1 && arr[right] < arr[right - 1]) right--;

  return left === right;
};
```

### 1207. 独一无二的出现次数

给你一个整数数组 arr，请你帮忙统计数组中每个数的出现次数。
如果每个数的出现次数都是独一无二的，就返回 true；否则返回 false。

示例 1：
输入：arr = [1,2,2,1,1,3]输出：true
解释：在该数组中，1 出现了 3 次，2 出现了 2 次，3 只出现了 1 次。没有两个数的出现次数相同。

示例 2：
输入：arr = [1,2]输出：false

示例 3：
输入：arr = [-3,0,1,-3,1,1,1,-3,10,0]输出：true

#### 题解

```js
var uniqueOccurrences = function (arr) {
  let timesMap = new Map();

  for (let i = 0; i < arr.length; i++) {
    let time = timesMap.get(arr[i]) || 0;
    timesMap.set(arr[i], time + 1);
  }
  let uniqueSize = Array.from(new Set(Array.from(timesMap.values()))).length;
  return uniqueSize === timesMap.size;
};
```

### 189. 轮转数组

给定一个整数数组 nums，将数组中的元素向右轮转 k 个位置，其中 k 是非负数。

示例 1:
输入: nums = [1,2,3,4,5,6,7], k = 3 输出: [5,6,7,1,2,3,4]

解释:
向右轮转 1 步: [7,1,2,3,4,5,6]

向右轮转 2 步: [6,7,1,2,3,4,5]

向右轮转 3 步: [5,6,7,1,2,3,4]

示例 2:
输入：nums = [-1,-100,3,99], k = 2 输出：[3,99,-1,-100]

解释:
向右轮转 1 步: [99,-1,-100,3]

向右轮转 2 步: [3,99,-1,-100]

#### 题解

方法一的思路：
反转整个字符串-->反转区间为前 k 的子串-->反转区间为 k 到末尾的子串

```js
// 方法一
var reverse = function (arr, start, end) {
  while (start < end) {
    [arr[start++], arr[end--]] = [arr[end], arr[start]];
  }
};

var rotate = function (nums, k) {
  k %= nums.length;
  reverse(nums, 0, nums.length - 1);
  reverse(nums, 0, k - 1);
  reverse(nums, k, nums.length - 1);
  return nums;
};
```

```js
// 方法二
var rotate = function (nums, k) {
  const len = nums.length;
  if (len === 1 || !len) return;

  const position = k > len ? k % len : k;
  const reverseArr = nums.splice(len - position, position);
  nums.unshift(...reverseArr);
};
```

### 922. 按奇偶排序数组 II

给定一个非负整数数组 nums， nums 中一半整数是 奇数 ，一半整数是 偶数 。
对数组进行排序，以便当 nums[i] 为奇数时，i 也是 奇数 ；当 nums[i] 为偶数时， i 也是 偶数 。
你可以返回 任何满足上述条件的数组作为答案 。

示例 1：
输入：nums = [4,2,5,7]输出：[4,5,2,7]解释：[4,7,2,5]，[2,5,4,7]，[2,7,4,5] 也会被接受。

示例 2：
输入：nums = [2,3]输出：[2,3]

#### 题解

```js
var sortArrayByParityII = function (nums) {
  let oddInd = 1;
  for (let i = 0; i < nums.length; i += 2) {
    if (nums[i] % 2 === 1) {
      // 如果偶数位是奇数
      while (nums[oddInd] % 2 !== 0) oddInd += 2;
      [nums[oddInd], nums[i]] = [nums[i], nums[oddInd]];
    }
  }
  return nums;
};
```

## 链表

### 定义链表

#### javascript 版

```js
class ListNode {
  val;
  next = null;
  constructor(value) {
    this.val = value;
    this.next = null;
  }
}
```

#### typescript 版

```typescript
class ListNode {
  public val: number;
  public next: ListNode | null = null;
  constructor(value: number) {
    this.val = value;
    this.next = null;
  }
}
```

### 203. 移除链表元素

给你一个链表的头节点 head 和一个整数 val ，请你删除链表中所有满足 Node.val == val 的节点，并返回 新的头节点 。

示例 1：输入：head = [1,2,6,3,4,5,6], val = 6 输出：[1,2,3,4,5]

示例 2：输入：head = [], val = 1 输出：[]

示例 3：输入：head = [7,7,7,7], val = 7 输出：[]

#### 题解

```js
function removeElements(head: ListNode | null, val: number): ListNode | null {
  if (head === null) return null;
  while (head && val === head.val) {
    head = head.next;
  }

  let currentNode = head;
  while (currentNode?.next) {
    if (currentNode.next.val === val) {
      currentNode.next = currentNode.next.next;
    } else {
      currentNode = currentNode.next;
    }
  }
  return head;
}

// 解二：虚拟头节点
function removeElements(head: ListNode | null, val: number): ListNode | null {
  // 添加虚拟节点
  const data = new ListNode(0, head);
  let pre = data,
    cur = data.next;
  while (cur) {
    if (cur.val === val) {
      pre.next = cur.next;
    } else {
      pre = cur;
    }
    cur = cur.next;
  }
  return data.next;
}
```

### 707. 设计链表

你可以选择使用单链表或者双链表，设计并实现自己的链表。
单链表中的节点应该具备两个属性：val 和 next 。val 是当前节点的值，next 是指向下一个节点的指针/引用。
如果是双向链表，则还需要属性 prev 以指示链表中的上一个节点。假设链表中的所有节点下标从 0 开始。
实现 MyLinkedList 类：

- MyLinkedList() 初始化 MyLinkedList 对象。
- int get(int index) 获取链表中下标为 index 的节点的值。如果下标无效，则返回 -1 。
- void addAtHead(int val) 将一个值为 val 的节点插入到链表中第一个元素之前。在插入完成后，新节点会成为链表的第一个节点。
- void addAtTail(int val) 将一个值为 val 的节点追加到链表中作为链表的最后一个元素。
- void addAtIndex(int index, int val) 将一个值为 val 的节点插入到链表中下标为 index 的节点之前。如果 index 等于链表的长度，那么该节点会被追加到链表的末尾。如果 index 比长度更大，该节点将 不会插入 到链表中。
- void deleteAtIndex(int index) 如果下标有效，则删除链表中下标为 index 的节点。

示例：

输入["MyLinkedList", "addAtHead", "addAtTail", "addAtIndex", "get", "deleteAtIndex", "get"]
[[], [1], [3], [1, 2], [1], [1], [1]]

输出[null, null, null, null, 2, null, 3]

解释
MyLinkedList myLinkedList = new MyLinkedList();

myLinkedList.addAtHead(1);

myLinkedList.addAtTail(3);

myLinkedList.addAtIndex(1, 2);

// 链表变为 1->2->3myLinkedList.get(1);

// 返回 2myLinkedList.deleteAtIndex(1);

// 现在，链表变为 1->3myLinkedList.get(1);

// 返回 3

#### 题解

```js
class NodeItem {
val: number;
next: NodeItem | null = null

    constructor(val: number) {
        this.val = val
        this.next = null
    }

}

class MyLinkedList {
public size: number = 0
public head: NodeItem | null = null

    get(index: number): number {
        if (index < 0 || index >= this.size) return -1

        let currentInd = 0
        let current = this.head

        while (currentInd++ < index && current) {
            current = current.next
        }
        return current ? current.val : -1
    }

    addAtHead(val: number): void {
        const headNode = new NodeItem(val)
        if (this.size === 0) {
            this.head = headNode
        } else {
            headNode.next = this.head
            this.head = headNode
        }
        this.size++
    }

    addAtTail(val: number): void {
        const newNode = new NodeItem(val)

        if (this.size === 0) {
            this.head = newNode
        } else {
            let current = this.head
            while (current && current.next) {
                current = current.next
            }
            current.next = newNode
        }
        this.size++
    }

    addAtIndex(index: number, val: number): void {
        if (index < 0 || index > this.size) return
        if (index === 0) return this.addAtHead(val)
        if (index === this.size) return this.addAtTail(val)

        const newNode = new NodeItem(val)
        let ind = 0
        let current = this.head
        let prev: NodeItem | null = null
        while (ind < index && current) {
            prev = current
            current = current.next
            ind++
        }
        prev.next = newNode
        prev.next.next = current

        this.size++
    }

    deleteAtIndex(index: number): void {
        if (index < 0 || index >= this.size || this.size === 0) return

        let ind: number = 0
        let current = this.head
        let prev: NodeItem | null = this.head
        // 需要判断index===0的情况
        if (index === 0) {
            this.head = this.head?.next ?? null
        }

        while (ind < index && current) {
            prev = current
            current = current.next
            ind++
        }
        prev!.next = current.next ?? null
        this.size--
    }
}
```

解二 TODO：设计双向链表

### 206. 反转链表

给你单链表的头节点 head ，请你反转链表，并返回反转后的链表。

示例 1：输入：head = [1,2,3,4,5]输出：[5,4,3,2,1]

示例 2：输入：head = [1,2]输出：[2,1]

示例 3：输入：head = []输出：[]

题解

```js
// 非递归方法
function reverseList(head: ListNode | null): ListNode | null {
  if (head === null || head.next === null) return head;
  let newHead: ListNode | null = null;

  while (head) {
    const current: ListNode | null = head.next;
    head.next = newHead;
    newHead = head;
    head = current;
  }
  return newHead;
}

// 递归
function reverseByRecursion(head: NodeItem | null): NodeItem | null {
  if (head === null || head.next === null) return head;
  const newHead = reverseByRecursion(head?.next ?? null);
  head.next.next = head;
  head.next = null;

  return newHead;
}
```

### 24. 两两交换链表中的节点

给你一个链表，两两交换其中相邻的节点，并返回交换后链表的头节点。你必须在不修改节点内部的值的情况下完成本题（即，只能进行节点交换）。

示例 1：输入：head = [1,2,3,4]输出：[2,1,4,3]

示例 2：输入：head = []输出：[]

示例 3：输入：head = [1]输出：[1]

#### 题解

```js
// 递归法：时间复杂度 O(n)，空间复杂度 O(n)
function swapPairs(head: ListNode | null): ListNode | null {
  if (!head || !head.next) return head;

  let nextNode = head.next;
  head.next = swapPairs(nextNode.next);
  nextNode.next = head;
  return nextNode;
}
// 迭代法：时间复杂度 O(n),空间复杂度 O(1)
function swapPairs(head: ListNode | null): ListNode | null {
  const dummy = new ListNode(0, head); // 虚拟头节点
  let current = dummy;

  while (current.next && current.next.next) {
    const first = current.next; // 节点1
    const second = first.next; // 节点2
    current.next = second; // 将节点2赋值给节点1
    first.next = second.next; // 节点1.next 指向 节点2.next
    second.next = first; // 节点2 指向节点1
    current = first; //将current移向下一组的前一个节点位置
  }
  return dummy.next;
}
```

### 19. 删除链表的倒数第 N 个结点

给你一个链表，删除链表的倒数第 n 个结点，并且返回链表的头结点。

示例 1：输入：head = [1,2,3,4,5], n = 2 输出：[1,2,3,5]

示例 2：输入：head = [1], n = 1 输出：[]

示例 3：输入：head = [1,2], n = 1 输出：[1]

#### 题解

```js
// 双指针：时间复杂度 O(n)；空间复杂度: O(1)
function removeNthFromEnd(head: ListNode | null, n: number): ListNode | null {
  if (n === 1 && !head.next) return null;

  let dummy = new ListNode(0, head);

  let slowNode = dummy,
    fastNode = dummy;
  while (n--) {
    fastNode = fastNode.next;
  }

  while (fastNode.next) {
    slowNode = slowNode.next;
    fastNode = fastNode.next;
  }
  slowNode.next = slowNode.next.next;
  return dummy.next;
}
```

### 160. 相交链表

给你两个单链表的头节点 headA 和 headB ，请你找出并返回两个单链表相交的起始节点。如果两个链表不存在相交节点，返回 null 。

图示两个链表在节点 c1 开始相交：

题目数据 保证 整个链式结构中不存在环。

注意，函数返回结果后，链表必须保持其原始结构。

评测系统将根据这些输入创建链式数据结构，并将两个头节点 headA 和 headB 传递给你的程序。如果程序能够正确返回相交节点，那么你的解决方案将被 视作正确答案 。

示例 1：输入：intersectVal = 8, listA = [4,1,8,4,5], listB = [5,6,1,8,4,5], skipA = 2, skipB = 3

输出：Intersected at '8'

解释：相交节点的值为 8 （注意，如果两个链表相交则不能为 0）。

从各自的表头开始算起，链表 A 为 [4,1,8,4,5]，链表 B 为 [5,6,1,8,4,5]。

在 A 中，相交节点前有 2 个节点；在 B 中，相交节点前有 3 个节点。— 请注意相交节点的值不为 1，因为在链表 A 和链表 B 之中值为 1 的节点 (A 中第二个节点和 B 中第三个节点) 是不同的节点。换句话说，它们在内存中指向两个不同的位置，而链表 A 和链表 B 中值为 8 的节点 (A 中第三个节点，B 中第四个节点) 在内存中指向相同的位置。

示例 2：

输入：intersectVal = 2, listA = [1,9,1,2,4], listB = [3,2,4], skipA = 3, skipB = 1

输出：Intersected at '2'

解释：相交节点的值为 2 （注意，如果两个链表相交则不能为 0）。从各自的表头开始算起，链表 A 为 [1,9,1,2,4]，链表 B 为 [3,2,4]。在 A 中，相交节点前有 3 个节点；在 B 中，相交节点前有 1 个节点。

#### 题解

```js
function getLength(head: ListNode): number {
  let current = head,
    length = 0;

  while (current) {
    length++;
    current = current.next;
  }
  return length;
}

function getIntersectionNode(
  headA: ListNode | null,
  headB: ListNode | null
): ListNode | null {
  let fastNode = headA;
  let slowNode = headB;
  const lengthA = getLength(headA);
  const lengthB = getLength(headB);
  let num: number = lengthA - lengthB;
  if (lengthA < lengthB) {
    num = lengthB - lengthA;
    fastNode = headB;
    slowNode = headA;
  }

  while (num-- > 0) {
    fastNode = fastNode.next;
  }

  // 寻找出相交的 node，如果找不到则返回 node.next(null)
  while (fastNode && fastNode !== slowNode) {
    fastNode = fastNode?.next;
    slowNode = slowNode?.next;
  }
  return fastNode;
}
```

### 21. 合并两个有序链表

将两个升序链表合并为一个新的 升序 链表并返回。新链表是通过拼接给定的两个链表的所有节点组成的。

示例 1：输入：l1 = [1,2,4], l2 = [1,3,4]输出：[1,1,2,3,4,4]

示例 2：输入：l1 = [], l2 = []输出：[]

示例 3：输入：l1 = [], l2 = [0]输出：[0]

#### 题解

```js
function mergeTwoLists(
  list1: ListNode | null,
  list2: ListNode | null
): ListNode | null {
  let dummy = new ListNode(); // 虚拟头节点
  let current = dummy;

  while (list1 && list2) {
    if (list1.val >= list2.val) {
      current.next = list2;
      list2 = list2.next;
    } else {
      current.next = list1;
      list1 = list1.next;
    }
    current = current.next;
  }
  current.next = list1 ? list1 : list2; // 将剩余部分加到新链表的末尾

  return dummy.next;
}
```

### 234. 回文链表

给你一个单链表的头节点 head ，请你判断该链表是否为回文链表。如果是，返回 true ；否则，返回 false 。
示例 1：输入：head = [1,2,2,1]输出：true

示例 2：输入：head = [1,2]输出：false

#### 题解

```js
var isPalindrome = function (head) {
  // 反转链表
  function reverse(head) {
    let temp = null,
      pre = null;
    while (head) {
      temp = head.next;
      head.next = pre;
      pre = head;
      head = temp;
    }
    return pre;
  }

  if (!head && !head.next) return true;

  let slow = head,
    fast = head,
    pre = head;
  // 将链表分割为两部分
  while (fast && fast.next) {
    pre = slow;
    slow = slow.next;
    fast = fast.next.next;
  }
  pre.next = null;

  let left = head,
    right = reverse(slow); // 前半部分 & 后半部分反转链表
  while (left) {
    if (left.val !== right.val) return false;
    left = left.next;
    right = right.next;
  }
  return true;
};
```

### 143. 重排链表 ⭐️[未解决]

给定一个单链表 L 的头节点 head ，单链表 L 表示为：
L0 → L1 → … → Ln - 1 → Ln
请将其重新排列后变为：
L0 → Ln → L1 → Ln - 1 → L2 → Ln - 2 → …

不能只是单纯的改变节点内部的值，而是需要实际的进行节点交换。

#### 题解

```js
var reorderList = function (head) {
  const reverse = (head) => {
    let vnode = new ListNode(0);
    let current = head,
      next = null;
    while (current) {
      next = current.next;
      current.next = vnode.next;
      vnode.next = current;
      current = next;
    }
    return vnode.next;
  };

  let fast = head,
    slow = head;

  while (fast.next && fast.next.next) {
    slow = slow.next;
    fast = fast.next.next;
  }
  // 右部分
  let right = slow.next;
  slow.next = null; // 切割左右部分
  right = reverse(right); // 反转右部分，right是反转后右部分的起点
  // 左部分
  let left = head;
  while (right) {
    let curLeft = left.next;
    left.next = right;
    left = curLeft;

    let curRight = right.next;
    right.next = left;
    right = curRight;
  }
};
```

### 141. 环形链表

给你一个链表的头节点 head ，判断链表中是否有环。
如果链表中有某个节点，可以通过连续跟踪 next 指针再次到达，则链表中存在环。 为了表示给定链表中的环，评测系统内部使用整数 pos 来表示链表尾连接到链表中的位置（索引从 0 开始）。注意：pos 不作为参数进行传递 。仅仅是为了标识链表的实际情况。
如果链表中存在环 ，则返回 true 。 否则，返回 false 。

示例 1：输入：head = [3,2,0,-4], pos = 1 输出：true

解释：链表中有一个环，其尾部连接到第二个节点。

思路：

快慢指针法， 分别定义 fast 和 slow 指针，从头结点出发，fast 指针每次移动两个节点，slow 指针每次移动一个节点，如果 fast 和 slow 指针在途中相遇 ，说明这个链表有环。

#### 题解

```js
var hasCycle = function (head) {
  let slow = head,
    fast = head;

  while (fast && fast.next) {
    fast = fast.next.next;
    slow = slow.next;
    if (slow === fast) return true;
  }
  return false;
};
```

### 142. 环形链表 II

给定一个链表的头节点 head ，返回链表开始入环的第一个节点。 如果链表无环，则返回 null。
如果链表中有某个节点，可以通过连续跟踪 next 指针再次到达，则链表中存在环。 为了表示给定链表中的环，评测系统内部使用整数 pos 来表示链表尾连接到链表中的位置（索引从 0 开始）。如果 pos 是 -1，则在该链表中没有环。注意：pos 不作为参数进行传递，仅仅是为了标识链表的实际情况。
不允许修改 链表。

示例 1：输入：head = [3,2,0,-4], pos = 1 输出：返回索引为 1 的链表节点解释：链表中有一个环，其尾部连接到第二个节点。

示例 2：输入：head = [1,2], pos = 0 输出：返回索引为 0 的链表节点解释：链表中有一个环，其尾部连接到第一个节点。

示例 3：输入：head = [1], pos = -1 输出：返回 null 解释：链表中没有环。

#### 题解

从头结点出发，fast 指针每次移动两个节点，slow 指针每次移动一个节点，如果 fast 和 slow 指针在途中相遇 ，说明这个链表有环；

从头结点出发一个指针，从相遇节点 也出发一个指针，这两个指针每次只走一个节点， 那么当这两个指针相遇的时候就是 环形入口的节点。

```js
function detectCycle(head: ListNode | null): ListNode | null {
  if (!head?.next) return null;
  let fastNode = head,
    slowNode = head;

  while (fastNode?.next) {
    fastNode = fastNode.next.next;
    slowNode = slowNode.next;
    if (fastNode === slowNode) {
      slowNode = head;
      while (fastNode !== slowNode) {
        fastNode = fastNode.next;
        slowNode = slowNode.next;
      }
      return slowNode;
    }
  }
  return null;
}
```

## 哈希表

### 205. 同构字符串

给定两个字符串 s 和 t ，判断它们是否是同构的。
如果 s 中的字符可以按某种映射关系替换得到 t ，那么这两个字符串是同构的。
每个出现的字符都应当映射到另一个字符，同时不改变字符的顺序。不同字符不能映射到同一个字符上，相同字符只能映射到同一个字符上，字符可以映射到自己本身。

示例 1:输入：s = "egg", t = "add" 输出：true

#### 题解

```js
var isIsomorphic = function (s, t) {
  let len = s.length;
  if (len === 0) return true;
  let mapS = new Map();
  let mapT = new Map();

  for (let i = 0, j = 0; i < len; i++, j++) {
    if (!mapS.has(s[i])) {
      mapS.set(s[i], t[j]);
    }

    if (!mapT.has(t[j])) {
      mapT.set(t[j], s[i]);
    }

    if (mapS.get(s[i]) !== t[j] || mapT.get(t[j]) !== s[i]) return false;
  }
  return true;
};
```

### 1002. 查找共用字符

给你一个字符串数组 words ，请你找出所有在 words 的每个字符串中都出现的共用字符（ 包括重复字符），并以数组形式返回。你可以按 任意顺序 返回答案。

示例 1：
输入：words = ["bella","label","roller"]输出：["e","l","l"]

示例 2：
输入：words = ["cool","lock","cook"]输出：["c","o"]

## 字符串

### 344. 反转字符串

编写一个函数，其作用是将输入的字符串反转过来。输入字符串以字符数组 s 的形式给出。
不要给另外的数组分配额外的空间，你必须原地修改输入数组、使用 O(1) 的额外空间解决这一问题。

示例 1：
输入：s = ["h","e","l","l","o"]输出：["o","l","l","e","h"]

示例 2：
输入：s = ["H","a","n","n","a","h"]输出：["h","a","n","n","a","H"]

#### 题解

```js
// 双指针：时间复杂度: O(n);空间复杂度: O(1)
function reverseString(s: string[]): void {
  let fast = s.length - 1,
    slow = 0;

  while (slow < fast) {
    [s[slow], s[fast]] = [s[fast], s[slow]];
    slow++;
    fast--;
  }
}
```

### 541. 反转字符串 II

给定一个字符串 s 和一个整数 k，从字符串开头算起，每计数至 2k 个字符，就反转这 2k 字符中的前 k 个字符。

- 如果剩余字符少于 k 个，则将剩余字符全部反转。
- 如果剩余字符小于 2k 但大于或等于 k 个，则反转前 k 个字符，其余字符保持原样。

#### 题解

```js
function reverseStr(s: string, k: number): string {
let arr: string[] = s.split('')
let left: number, right: number
for (let i = 0; i < arr.length; i += 2 \* k) {
left = i
// i + k > arr.length 说明剩余字符少于 k 个，将剩余自负全部反转
right = i + k > arr.length ? arr.length - 1 : i + k - 1

          while (left < right) {
              [arr[left], arr[right]] = [arr[right], arr[left]]
              left++
              right--
          }
      }
      return arr.join('')

};
```

### 151. 反转字符串中的单词

给你一个字符串 s ，请你反转字符串中 单词 的顺序。
单词 是由非空格字符组成的字符串。s 中使用至少一个空格将字符串中的 单词 分隔开。
返回 单词 顺序颠倒且 单词 之间用单个空格连接的结果字符串。
注意：输入字符串 s 中可能会存在前导空格、尾随空格或者单词间的多个空格。返回的结果字符串中，单词间应当仅用单个空格分隔，且不包含任何额外的空格。

示例 1：
输入：s = "the sky is blue"
输出："blue is sky the"

示例 2：
输入：s = " hello world "输出："world hello"解释：反转后的字符串中不能存在前导空格和尾随空格。

示例 3：
输入：s = "a good example"输出："example good a"解释：如果两个单词间有多余的空格，反转后的字符串需要将单词间的空格减少到仅有一个。

```js
function reverseWords(s: string): string {
  // 处理所有的空格：首尾无空格，每个单词之间一个空格
  function delExtraSpace(arr: string[]): void {
    let left: number = 0,
      right: number = 0,
      length: number = arr.length;

    while (right < length && arr[right] === ' ') {
      // 起始位置的空格去除
      right++;
    }
    while (right < length) {
      if (arr[right] === ' ' && arr[right - 1] === ' ') {
        // 如果中间空格超过1个，去除多余的空格
        right++;
        continue;
      }
      arr[left++] = arr[right++];
    }
    // 单独处理一下末尾多空格的问题
    arr.length = arr[left - 1] === ' ' ? left - 1 : left;
  }

  // 翻转字符串
  function reverseWord(strArr: string[], start: number, end: number) {
    while (start < end) {
      [strArr[start], strArr[end]] = [strArr[end], strArr[start]];
      start++;
      end--;
    }
  }

  let strArr: string[] = s.split(''),
    length = strArr.length;
  delExtraSpace(strArr);
  reverseWord(strArr, 0, length - 1);

  // 翻转每个单词
  let start: number = 0,
    end: number = 0;
  while (start < length) {
    end = start;
    while (strArr[end] !== ' ' && end < length) {
      end++;
    }
    // 翻转单个单词
    reverseWord(strArr, start, end - 1);
    start = end + 1;
  }

  return strArr.join('');
}

// 解法二
var reverseWords = function (s) {
  const arr = s.split(' ').filter((v) => v);

  let left = 0,
    right = arr.length - 1;
  while (left <= right) {
    [arr[left++], arr[right--]] = [arr[right], arr[left]];
  }
  for (let i = 0; i < arr.length; i++) {
    if (i !== arr.length - 1) arr[i] = arr[i] + ' ';
  }

  return arr.join('');
};
```

### 28. 找出字符串中第一个匹配项的下标

给你两个字符串 haystack 和 needle ，请你在 haystack 字符串中找出 needle 字符串的第一个匹配项的下标（下标从 0 开始）。如果 needle 不是 haystack 的一部分，则返回 -1 。

示例 1：
输入：haystack = "sadbutsad", needle = "sad"输出：0 解释："sad" 在下标 0 和 6 处匹配。第一个匹配项的下标是 0 ，所以返回 0 。

示例 2：
输入：haystack = "leetcode", needle = "leeto"输出：-1 解释："leeto" 没有在 "leetcode" 中出现，所以返回 -1 。

#### 题解

KMP 的经典思想就是:当出现字符串不匹配时，可以记录一部分之前已经匹配的文本内容，利用这些信息避免从头再去做匹配

```js
function strStr(haystack: string, needle: string): number {
  let n = needle.length,
    h = haystack.length;
  let next: number[] = new Array(n).fill(0);

  for (let i = 1, j = 0; i < n; i++) {
    while (j > 0 && needle[i] !== needle[j]) {
      // j - 1就指向了上一个子串未匹配好的位置
      j = next[j - 1];
    }
    if (needle[i] === needle[j]) j++;
    // 将当前子串的最长相等前后缀添加到next数组中
    next[i] = j;
  }

  for (let i = 0, j = 0; i < h; i++) {
    while (j > 0 && haystack[i] !== needle[j]) {
      j = next[j - 1];
    }
    if (haystack[i] === needle[j]) j++;
    if (j === n) return i - n + 1;
  }
  return -1;
}
```

### 459. 重复的子字符串

给定一个非空的字符串 s ，检查是否可以通过由它的一个子串重复多次构成。

示例 1:
输入: s = "abab"输出: true 解释: 可由子串 "ab" 重复两次构成。

示例 2:
输入: s = "aba"输出: false

示例 3:
输入: s = "abcabcabcabc"输出: true 解释: 可由子串 "abc" 重复四次构成。 (或子串 "abcabc" 重复两次构成。)
由重复子串组成的字符串--next 数组
a s d a s d a s d
0 0 0 1 2 3 4 5 6

我们可以看出如果 s 是由子串重复构成的话，会从第二个重复子串开始有最长相等前后缀，
并且 len - 6 就是第一个字串的长度 a s d，因为第一个子串都是 0,
如果这个长度可以被整除，就说明整个字符串就是这个周期的循环

#### 题解

```js
function repeatedSubstringPattern(s: string): boolean {
  let next: number[] = new Array(s.length).fill(0);
  let sLen: number = s.length;

  for (let i = 1, j = 0; i < sLen; i++) {
    while (j > 0 && s[i] !== s[j]) {
      j = next[j - 1];
    }

    if (s[i] === s[j]) j++;
    next[i] = j;
  }

  if (
    next[next.length - 1] !== 0 &&
    sLen % (sLen - next[next.length - 1]) === 0
  )
    return true;
  return false;
}
```

### 724. 寻找数组的中心下标

给你一个整数数组 nums ，请计算数组的 中心下标 。
数组 中心下标 是数组的一个下标，其左侧所有元素相加的和等于右侧所有元素相加的和。
如果中心下标位于数组最左端，那么左侧数之和视为 0 ，因为在下标的左侧不存在元素。这一点对于中心下标位于数组最右端同样适用。
如果数组有多个中心下标，应该返回 最靠近左边 的那一个。如果数组不存在中心下标，返回 -1 。

示例 1：
输入：nums = [1, 7, 3, 6, 5, 6]输出：3 解释：中心下标是 3 。左侧数之和 sum = nums[0] + nums[1] + nums[2] = 1 + 7 + 3 = 11 ，右侧数之和 sum = nums[4] + nums[5] = 5 + 6 = 11 ，二者相等。

示例 2：
输入：nums = [1, 2, 3]输出：-1 解释：数组中不存在满足此条件的中心下标。

示例 3：
输入：nums = [2, 1, -1]输出：0 解释：中心下标是 0 。左侧数之和 sum = 0 ，（下标 0 左侧不存在元素），右侧数之和 sum = nums[1] + nums[2] = 1 + -1 = 0 。

思路 1.遍历一遍求出总和 sum 2.遍历第二遍求中心索引左半和 leftSum

- 同时根据 sum 和 leftSum 计算中心索引右半和 rightSum
- 判断 leftSum 和 rightSum 是否相同

#### 题解

```js
var pivotIndex = function (nums) {
  const sum = nums.reduce((a, b) => a + b);
  let leftSum = 0,
    rightSum = 0;

  for (let i = 0; i < nums.length; i++) {
    leftSum += nums[i];
    rightSum = sum - leftSum + nums[i];
    if (leftSum === rightSum) return i;
  }
  return -1;
};
```

### 925. 长按键入

你的朋友正在使用键盘输入他的名字 name。偶尔，在键入字符 c 时，按键可能会被长按，而字符可能被输入 1 次或多次。
你将会检查键盘输入的字符 typed。如果它对应的可能是你的朋友的名字（其中一些字符可能被长按），那么就返回 True。

示例 1：
输入：name = "alex", typed = "aaleex"输出：true 解释：'alex' 中的 'a' 和 'e' 被长按。

示例 2：
输入：name = "saeed", typed = "ssaaedd"输出：false 解释：'e' 一定需要被键入两次，但在 typed 的输出中不是这样。

#### 题解

```js
var isLongPressedName = function (name, typed) {
  let nLen = name.length,
    tLen = typed.length,
    preRecord = '',
    i = 0,
    j = 0;

  while (i < nLen && j < tLen) {
    if (name[i] === typed[j]) {
      preRecord = name[i];
      i++;
      j++;
    } else if (typed[j] === preRecord) {
      j++;
    } else return false;
  }

  if (i < nLen) return false;
  while (j < tLen) {
    if (typed[j] === preRecord) {
      j++;
    } else return false;
  }
  return true;
};
```

## 双指针

### 27. 移除元素

给你一个数组 nums 和一个值 val，你需要 原地 移除所有数值等于 val 的元素，并返回移除后数组的新长度。
不要使用额外的数组空间，你必须仅使用 O(1) 额外空间并 原地 修改输入数组。
元素的顺序可以改变。你不需要考虑数组中超出新长度后面的元素。
说明:
为什么返回数值是整数，但输出的答案是数组呢?
请注意，输入数组是以「引用」方式传递的，这意味着在函数里修改输入数组对于调用者是可见的。
你可以想象内部操作如下:
// nums 是以“引用”方式传递的。也就是说，不对实参作任何拷贝 int len = removeElement(nums, val);// 在函数里修改输入数组对于调用者是可见的。// 根据你的函数返回的长度, 它会打印出数组中 该长度范围内 的所有元素。for (int i = 0; i < len; i++) { print(nums[i]);}

示例 1：
输入：nums = [3,2,2,3], val = 3
输出：2, nums = [2,2]
解释：函数应该返回新的长度 2, 并且 nums 中的前两个元素均为 2。你不需要考虑数组中超出新长度后面的元素。例如，函数返回的新长度为 2 ，而 nums = [2,2,3,3] 或 nums = [2,2,0,0]，也会被视作正确答案。

示例 2：
输入：nums = [0,1,2,2,3,0,4,2], val = 2
输出：5, nums = [0,1,3,0,4]
解释：函数应该返回新的长度 5, 并且 nums 中的前五个元素为 0, 1, 3, 0, 4。注意这五个元素可为任意顺序。你不需要考虑数组中超出新长度后面的元素。

#### 题解

```js
function removeElement(nums: number[], val: number): number {
  let left = 0,
    right = 0;

  while (right < nums.length) {
    if (nums[right] !== val) {
      nums[left] = nums[right];
      left++;
      right++;
    } else right++;
  }
  return left;
}
```

### 26. 删除有序数组中的重复项

给你一个 非严格递增排列 的数组 nums ，请你 原地 删除重复出现的元素，使每个元素 只出现一次 ，返回删除后数组的新长度。元素的 相对顺序 应该保持 一致 。然后返回 nums 中唯一元素的个数。
考虑 nums 的唯一元素的数量为 k ，你需要做以下事情确保你的题解可以被通过：

- 更改数组 nums ，使 nums 的前 k 个元素包含唯一元素，并按照它们最初在 nums 中出现的顺序排列。nums 的其余元素与 nums 的大小不重要。
- 返回 k 。
  判题标准:
  系统会用下面的代码来测试你的题解:
  int[] nums = [...]; // 输入数组
  int[] expectedNums = [...]; // 长度正确的期望答案

int k = removeDuplicates(nums); // 调用

assert k == expectedNums.length;
for (int i = 0; i < k; i++) {
assert nums[i] == expectedNums[i];
}
如果所有断言都通过，那么您的题解将被 通过。

示例 1：
输入：nums = [1,1,2]
输出：2, nums = [1,2,_]
解释：函数应该返回新的长度 2 ，并且原数组 nums 的前两个元素被修改为 1, 2 。不需要考虑数组中超出新长度后面的元素。

示例 2：
输入：nums = [0,0,1,1,1,2,2,3,3,4]
输出：5, nums = [0,1,2,3,4]
解释：函数应该返回新的长度 5 ， 并且原数组 nums 的前五个元素被修改为 0, 1, 2, 3, 4 。不需要考虑数组中超出新长度后面的元素。

#### 题解

```js
function removeDuplicates(nums: number[]): number {
  let left = 1,
    right = 1;

  while (right < nums.length) {
    if (nums[right] !== nums[right - 1]) {
      nums[left] = nums[right];
      left++;
    }
    right++;
  }
  return left;
}
```

### 283. 移动零

给定一个数组 nums，编写一个函数将所有 0 移动到数组的末尾，同时保持非零元素的相对顺序。
请注意 ，必须在不复制数组的情况下原地对数组进行操作。

示例 1:
输入: nums = [0,1,0,3,12]
输出: [1,3,12,0,0]

示例 2:
输入: nums = [0]
输出: [0]

#### 题解

```js
function moveZeroes(nums: number[]): void {
  let left = 0,
    right = 0;

  while (right < nums.length) {
    if (nums[right] !== 0) {
      nums[left] = nums[right];
      left++;
      right++;
    } else {
      right++;
    }
  }

  while (left < nums.length) {
    nums[left] = 0;
    left++;
  }
}
```

### 844. 比较含退格的字符串 ⭐️

给定 s 和 t 两个字符串，当它们分别被输入到空白的文本编辑器后，如果两者相等，返回 true 。# 代表退格字符。
注意：如果对空文本输入退格字符，文本继续为空。

示例 1：
输入：s = "ab#c", t = "ad#c"输出：true 解释：s 和 t 都会变成 "ac"。

示例 2：
输入：s = "ab##", t = "c#d#"输出：true 解释：s 和 t 都会变成 ""。

示例 3：
输入：s = "a#c", t = "b"输出：false 解释：s 会变成 "c"，但 t 仍然是 "b"。

#### 题解

```js
function backspaceCompare(s: string, t: string): boolean {
  function getActualString(str: string) {
    let newString = '';
    let skip = 0;

    for (let i = str.length - 1; i >= 0; i--) {
      if (str[i] === '#') {
        skip++;
        continue;
      }
      if (skip > 0 && str[i] !== '#') {
        skip--;
        continue;
      }
      if (str[i] !== '#') {
        newString = str[i] + newString;
      }
    }
    return newString;
  }

  return getActualString(s) === getActualString(t);
}
```

### 977. 有序数组的平方

给你一个按 非递减顺序 排序的整数数组 nums，返回 每个数字的平方 组成的新数组，要求也按 非递减顺序 排序。

示例 1：
输入：nums = [-4,-1,0,3,10]输出：[0,1,9,16,100]解释：平方后，数组变为 [16,1,0,9,100]排序后，数组变为 [0,1,9,16,100]

示例 2：
输入：nums = [-7,-3,2,3,11]输出：[4,9,9,49,121]

#### 题解

```js
function sortedSquares(nums: number[]): number[] {
  let length = nums.length,
    left = 0,
    right = length - 1,
    newArrayLen = length - 1;
  let newArr = new Array(length).fill(0);

  while (left <= right) {
    let l = nums[left] * nums[left];
    let r = nums[right] * nums[right];

    if (l < r) {
      newArr[newArrayLen] = r;
      right--;
      newArrayLen--;
    } else {
      newArr[newArrayLen] = l;
      left++;
      newArrayLen--;
    }
  }
  return newArr;
}
```

### 344. 反转字符串

编写一个函数，其作用是将输入的字符串反转过来。输入字符串以字符数组 s 的形式给出。
不要给另外的数组分配额外的空间，你必须原地修改输入数组、使用 O(1) 的额外空间解决这一问题。

示例 1：
输入：s = ["h","e","l","l","o"]输出：["o","l","l","e","h"]

示例 2：
输入：s = ["H","a","n","n","a","h"]输出：["h","a","n","n","a","H"]

#### 题解

```js
function reverseString(s: string[]): void {
  let fast = s.length - 1,
    slow = 0;

  while (slow < fast) {
    [s[slow], s[fast]] = [s[fast], s[slow]];
    slow++;
    fast--;
  }
}
```

### 1. 两数之和

给定一个整数数组 nums 和一个整数目标值 target，请你在该数组中找出 和为目标值 target 的那 两个 整数，并返回它们的数组下标。
你可以假设每种输入只会对应一个答案。但是，数组中同一个元素在答案里不能重复出现。
你可以按任意顺序返回答案。

示例 1：
输入：nums = [2,7,11,15], target = 9 输出：[0,1]解释：因为 nums[0] + nums[1] == 9 ，返回 [0, 1] 。

示例 2：
输入：nums = [3,2,4], target = 6 输出：[1,2]

示例 3：
输入：nums = [3,3], target = 6 输出：[0,1]

#### 题解

```js
function twoSum(nums: number[], target: number): number[] {
  let obj = {};

  for (let i = 0; i < nums.length; i++) {
    if (obj[target - nums[i]] !== undefined) return [obj[target - nums[i]], i];
    obj[nums[i]] = i;
  }
}
```

### 2. 三数之和

给你一个整数数组 nums ，判断是否存在三元组 [nums[i], nums[j], nums[k]] 满足 i != j、i != k 且 j != k ，同时还满足 nums[i] + nums[j] + nums[k] == 0 。请
你返回所有和为 0 且不重复的三元组。
注意：答案中不可以包含重复的三元组。

示例 1：
输入：nums = [-1,0,1,2,-1,-4]输出：[[-1,-1,2],[-1,0,1]]解释：nums[0] + nums[1] + nums[2] = (-1) + 0 + 1 = 0 。nums[1] + nums[2] + nums[4] = 0 + 1 + (-1) = 0 。nums[0] + nums[3] + nums[4] = (-1) + 2 + (-1) = 0 。不同的三元组是 [-1,0,1] 和 [-1,-1,2] 。注意，输出的顺序和三元组的顺序并不重要。

示例 2：
输入：nums = [0,1,1]输出：[]解释：唯一可能的三元组和不为 0 。

示例 3：
输入：nums = [0,0,0]输出：[[0,0,0]]解释：唯一可能的三元组和为 0 。

#### 题解

```js
function threeSum(nums: number[]): number[][] {
  let res = [];
  const size = nums.length;
  nums.sort((a, b) => a - b); // 将数组排序

  for (let i = 0; i < size; i++) {
    if (nums[i] > 0) break; // 第一个数>0 ,无解
    if (i > 0 && nums[i] === nums[i - 1]) continue; // 去重

    let left = i + 1,
      right = size - 1;
    while (left < right) {
      const sum = nums[i] + nums[left] + nums[right];

      if (sum === 0) {
        res.push([nums[i], nums[left], nums[right]]);
        while (left < right && nums[left] === nums[left + 1]) left++; // 跳过左侧重复值
        while (left < right && nums[right] === nums[right - 1]) right--; // 跳过右侧重复值
        left++;
        right--;
      } else if (sum < 0) left++;
      else right--;
    }
  }
  return res;
}
```

### 3. 四数之和

给你一个由 n 个整数组成的数组 nums ，和一个目标值 target 。请你找出并返回满足下述全部条件且不重复的四元组 [nums[a], nums[b], nums[c], nums[d]] （若两个四元组元素一一对应，则认为两个四元组重复）：

- 0 <= a, b, c, d < n
- a、b、c 和 d 互不相同
- nums[a] + nums[b] + nums[c] + nums[d] == target
  你可以按 任意顺序 返回答案 。

  示例 1：
  输入：nums = [1,0,-1,0,-2,2], target = 0 输出：[[-2,-1,1,2],[-2,0,0,2],[-1,0,0,1]]

  示例 2：
  输入：nums = [2,2,2,2,2], target = 8 输出：[[2,2,2,2]]

  #### 题解

  ```js
  function fourSum(nums: number[], target: number): number[][] {
    let res = [],
      size = nums.length;
    nums.sort((a, b) => a - b); // 数组排序

    for (let i = 0; i < size - 3; i++) {
      if (i > 0 && nums[i] === nums[i - 1]) continue; // 跳过重复相等值nums[i]

      if (nums[i] + nums[i + 1] + nums[i + 2] + nums[i + 3] > target) break; // 首和校验不能大于目标值

      if (nums[i] + nums[size - 1] + nums[size - 2] + nums[size - 3] < target)
        continue; // 如果最大值<target

      for (let j = i + 1; j < size - 2; j++) {
        // 同上
        if (j > i + 1 && nums[j] === nums[j - 1]) continue;

        if (nums[i] + nums[j] + nums[j + 1] + nums[j + 2] > target) break;

        if (nums[i] + nums[j] + nums[size - 1] + nums[size - 2] < target)
          continue;

        let left = j + 1,
          right = size - 1;
        while (left < right) {
          const total = nums[i] + nums[j] + nums[left] + nums[right];
          if (total === target) {
            res.push([nums[i], nums[j], nums[left], nums[right]]);

            while (nums[left] === nums[left + 1]) left++;
            while (nums[right] === nums[right - 1]) right--;
            left++;
            right--;
          } else if (total < target) left++;
          else right--;
        }
      }
    }
    return res;
  }
  ```

## 栈与队列

### 232. 用栈实现队列

请你仅使用两个栈实现先入先出队列。队列应当支持一般队列支持的所有操作（push、pop、peek、empty）：
实现 MyQueue 类：

- void push(int x) 将元素 x 推到队列的末尾
- int pop() 从队列的开头移除并返回元素
- int peek() 返回队列开头的元素
- boolean empty() 如果队列为空，返回 true ；否则，返回 false
  说明：
- 你 只能 使用标准的栈操作 —— 也就是只有 push to top, peek/pop from top, size, 和 is empty 操作是合法的。
- 你所使用的语言也许不支持栈。你可以使用 list 或者 deque（双端队列）来模拟一个栈，只要是标准的栈操作即可。

  示例 1：
  输入：["MyQueue", "push", "push", "peek", "pop", "empty"][], [1], [2], [], [], []]输出：[null, null, null, 1, 1, false]

  解释：

  MyQueue myQueue = new MyQueue();

  myQueue.push(1); // queue is: [1]

  myQueue.push(2); // queue is: [1, 2] (leftmost is front of the queue)

  myQueue.peek(); // return 1

  myQueue.pop(); // return 1, queue is [2]

  myQueue.empty(); // return false

#### 题解

```js
// 先进先出
class MyQueue {
public stackIn: number[]
public stackOut: number[]
constructor() {
this.stackIn = []
this.stackOut = []
}

    push(x: number): void {
        this.stackIn.push(x)
    }

    // 队列首部删除元素
    pop(): number {
        if (this.stackOut.length === 0) {
            while (this.stackIn.length > 0) {
                this.stackOut.push(this.stackIn.pop()!)
            }
        }
        return this.stackOut.pop()
    }

    peek(): number {
        // 调用pop方法
        let temp:number = this.pop()
        // 后进先出
        this.stackOut.push(temp) // 放到stackOut栈中，无变化操作
        return temp
    }

    empty(): boolean {
        return !this.stackIn.length && !this.stackOut.length
    }

}
```

### 225. 用队列实现栈

请你仅使用两个队列实现一个后入先出（LIFO）的栈，并支持普通栈的全部四种操作（push、top、pop 和 empty）。
实现 MyStack 类：

- void push(int x) 将元素 x 压入栈顶。
- int pop() 移除并返回栈顶元素。
- int top() 返回栈顶元素。
- boolean empty() 如果栈是空的，返回 true ；否则，返回 false 。
  注意：
- 你只能使用队列的基本操作 —— 也就是 push to back、peek/pop from front、size 和 is empty 这些操作。
- 你所使用的语言也许不支持队列。 你可以使用 list （列表）或者 deque（双端队列）来模拟一个队列 , 只要是标准的队列操作即可。

#### 题解

```js
class MyStack {
constructor(public queueIn: number[] = [], public queueOut: number[] = []) { }

      push(x: number): void {
          this.queueIn.push(x)
      }

      pop(): number {
          // 将队列1中的元素逐个取出放入队列2，最后一个元素即为pop目标元素，再从队列2中取出元素逐个放入队列1中
          while (this.queueIn.length>1) {
              this.queueOut.push(this.queueIn.shift())
          }
          let res = this.queueIn.shift()
          while (this.queueOut.length) {
              this.queueIn.push(this.queueOut.shift())
          }
          return res
      }

      top(): number {
          let temp = this.pop()
          this.push(temp)
          return temp
      }

      empty(): boolean {
          return !this.queueIn.length
      }

}
```

```js
// 用一个队列实现
class MyStack {
constructor(public queue: number[] = []) { }

      push(x: number): void {
          this.queue.push(x)
      }

      pop(): number {
          let length = this.queue.length
          for (let i = 0; i < length - 1; i++) {
              this.queue.push(this.queue.shift())
          }
          return this.queue.shift()
      }

      top(): number {
          let temp = this.pop()
          this.push(temp)
          return temp
      }

      empty(): boolean {
          return !this.queue.length
      }

}
```

### 20. 有效的括号

给定一个只包括 '('，')'，'{'，'}'，'['，']' 的字符串 s ，判断字符串是否有效。
有效字符串需满足： 1.左括号必须用相同类型的右括号闭合。 2.左括号必须以正确的顺序闭合。 3.每个右括号都有一个对应的相同类型的左括号。

示例 1：
输入：s = "()"输出：true

示例 2：
输入：s = "()[]{}"输出：true

示例 3：
输入：s = "(]"输出：false
提示：

- 1 <= s.length <= 10
  4
- s 仅由括号 '()[]{}' 组成

#### 题解

```js
function isValid(s: string): boolean {
  let rightArr = [];
  for (let i = 0; i < s.length; i++) {
    if (s[i] === '(') {
      rightArr.push(')');
      continue;
    }
    if (s[i] === '{') {
      rightArr.push('}');
      continue;
    }
    if (s[i] === '[') {
      rightArr.push(']');
      continue;
    }
    if (s[i] !== rightArr.pop()) return false;
  }

  return !rightArr.length;
}
```

### 1047. 删除字符串中的所有相邻重复项

给出由小写字母组成的字符串 S，重复项删除操作会选择两个相邻且相同的字母，并删除它们。
在 S 上反复执行重复项删除操作，直到无法继续删除。
在完成所有重复项删除操作后返回最终的字符串。答案保证唯一。

示例：
输入："abbaca"输出："ca"解释：例如，在 "abbaca" 中，我们可以删除 "bb" 由于两字母相邻且相同，这是此时唯一可以执行删除操作的重复项。之后我们得到字符串 "aaca"，其中又只有 "aa" 可以执行重复项删除操作，所以最后的字符串为 "ca"。

提示：
1.1 <= S.length <= 20000
2.S 仅由小写英文字母组成。

#### 题解

```js
function removeDuplicates(s: string): string {
  let result: string[] = [];
  for (let i = 0; i < s.length; i++) {
    let lastInd = result.length - 1;
    if (s[i] === result[lastInd]) {
      result.pop();
    } else result.push(s[i]);
  }

  return result.join('');
}
```

### 150. 逆波兰表达式求值

给你一个字符串数组 tokens ，表示一个根据 逆波兰表示法 表示的算术表达式。
请你计算该表达式。返回一个表示表达式值的整数。
注意：

- 有效的算符为 '+'、'-'、'\*' 和 '/' 。
- 每个操作数（运算对象）都可以是一个整数或者另一个表达式。
- 两个整数之间的除法总是 向零截断 。
- 表达式中不含除零运算。
- 输入是一个根据逆波兰表示法表示的算术表达式。
- 答案及所有中间计算结果可以用 32 位 整数表示。

示例 1：
输入：tokens = ["2","1","+","3","*"]输出：9 解释：该算式转化为常见的中缀算术表达式为：((2 + 1) \_ 3) = 9

示例 2：
输入：tokens = ["4","13","5","/","+"]输出：6 解释：该算式转化为常见的中缀算术表达式为：(4 + (13 / 5)) = 6

示例 3：
输入：tokens = ["10","6","9","3","+","-11","_","/","_","17","+","5","+"]输出：22 解释：该算式转化为常见的中缀算术表达式为： ((10 _ (6 / ((9 + 3) _ -11))) + 17) + 5= ((10 _ (6 / (12 _ -11))) + 17) + 5= ((10 \_ (6 / -132)) + 17) + 5= ((10 \* 0) + 17) + 5= (0 + 17) + 5= 17 + 5= 22

提示：

- 1 <= tokens.length <= 10
  4
- tokens[i] 是一个算符（"+"、"-"、"\*" 或 "/"），或是在范围 [-200, 200] 内的一个整数

逆波兰表达式：
逆波兰表达式是一种后缀表达式，所谓后缀就是指算符写在后面。

- 平常使用的算式则是一种中缀表达式，如 ( 1 + 2 ) \* ( 3 + 4 ) 。
- 该算式的逆波兰表达式写法为 ( ( 1 2 + ) ( 3 4 + ) \* ) 。
  逆波兰表达式主要有以下两个优点：
- 去掉括号后表达式无歧义，上式即便写成 1 2 + 3 4 + \* 也可以依据次序计算出正确结果。
- 适合用栈操作运算：遇到数字则入栈；遇到算符则取出栈顶两个数字进行计算，并将结果压入栈中

#### 题解

```js
  function evalRPN(tokens: string[]): number {
  let arrStack: number[] = []

      const operationMap: Map<string, (a: number, b: number) => number> = new Map([
          ['+', (a, b) => a + b],
          ['-', (a, b) => a - b],
          ['/', (a, b) => a / b | 0],
          ['*', (a, b) => a * b]
      ])

      let a:number,b:number;
      for(let t of tokens){
          if(operationMap.has(t)){
              b = arrStack.pop()
              a=arrStack.pop()
              arrStack.push(operationMap.get(t)!(a,b))
          } else arrStack.push(Number(t))
      }

      return arrStack.pop()

  };
```

### 239. 滑动窗口最大值

给你一个整数数组 nums，有一个大小为 k 的滑动窗口从数组的最左侧移动到数组的最右侧。你只可以看到在滑动窗口内的 k 个数字。滑动窗口每次只向右移动一位。
返回 滑动窗口中的最大值 。

示例 1：
输入：nums = [1,3,-1,-3,5,3,6,7], k = 3 输出：[3,3,5,5,6,7]解释：滑动窗口的位置 最大值--------------- -----[1 3 -1] -3 5 3 6 7 3 1 [3 -1 -3] 5 3 6 7 3 1 3 [-1 -3 5] 3 6 7 5 1 3 -1 [-3 5 3] 6 7 5 1 3 -1 -3 [5 3 6] 7 6 1 3 -1 -3 5 [3 6 7] 7

示例 2：
输入：nums = [1], k = 1 输出：[1]
提示：

- 1 <= nums.length <= 10
  5
- -10
  4 <= nums[i] <= 10
  4
- 1 <= k <= nums.length

```js
  function maxSlidingWindow(nums: number[], k: number): number[] {
  class MonoQueue {
  constructor(private queue: number[] = []) { }

          // 入队：如果value大于队尾元素，则删除队尾元素，直至队尾元素大于value，或者队列为空
          public enqueue(value: number): void {
              let last: number | undefined = this.queue[this.queue.length - 1]
              while (last !== undefined && last < value) {
                  this.queue.pop()
                  last = this.queue[this.queue.length - 1]
              }
              this.queue.push(value)
          }

          // 出队：当队头元素等于value时 出队
          public dequeue(value: number): void {
              let top: number | undefined = this.top()
              if (top !== undefined && top === value) this.queue.shift()
          }

          public top(): number | undefined {
              return this.queue[0]
          }
      }

      const arrQueue: MonoQueue = new MonoQueue()
      let i: number = 0, j: number = 0
      let resArr: number[] = []
      while (j < k) {
          arrQueue.enqueue(nums[j++])
      }

      resArr.push(arrQueue.top())

      while (j < nums.length) {
          arrQueue.enqueue(nums[j])// 将新元素加入到队列中
          arrQueue.dequeue(nums[i])// 去除前一位元素
          resArr.push(arrQueue.top()!) // 获取新滑动窗口的最大值
          j++, i++
      }
      return resArr

  };
```

### 347. 前 K 个高频元素

给你一个整数数组 nums 和一个整数 k ，请你返回其中出现频率前 k 高的元素。你可以按 任意顺序 返回答案。

示例 1:
输入: nums = [1,1,1,2,2,3], k = 2 输出: [1,2]

示例 2:
输入: nums = [1], k = 1 输出: [1]
提示：

- 1 <= nums.length <= 105
- k 的取值范围是 [1, 数组中不相同的元素的个数]
- 题目数据保证答案唯一，换句话说，数组中前 k 个高频元素的集合是唯一的
  进阶：你所设计算法的时间复杂度 必须 优于 O(n log n) ，其中 n 是数组大小。

#### 题解

```js
function topKFrequent(nums: number[], k: number): number[] {
  const countMap: Map<number, number> = new Map();

  for (let num of nums) {
    countMap.set(num, (countMap.get(num) || 0) + 1);
  }

  return [...countMap.entries()]
    .sort((a, b) => b[1] - a[1])
    .slice(0, k)
    .map((i) => i[0]);
}
```

## 二叉树

### 概念

满二叉树：如果一棵二叉树只有度为 0 的结点和度为 2 的结点，并且度为 0 的结点在同一层上，则这棵二叉树为满二叉树。

完全二叉树：在完全二叉树中，除了最底层节点可能没填满外，其余每层节点数都达到最大值，并且最下面一层的节点都集中在该层最左边的若干位置。若最底层为第 h 层（h 从 1 开始），则该层包含 1~ 2^(h-1) 个节点。

二叉搜索树：有序树

- 若它的左子树不空，则左子树上所有结点的值均小于它的根结点的值；
- 若它的右子树不空，则右子树上所有结点的值均大于它的根结点的值；
- 它的左、右子树也分别为二叉排序树

平衡二叉搜索树：又被称为 AVL（Adelson-Velsky and Landis）树，且具有以下性质：它是一棵空树或它的左右两个子树的高度差的绝对值不超过 1，并且左右两个子树都是一棵平衡二叉树。

#### 二叉树的存储方式

二叉树可以链式存储（指针），也可以顺序存储（数组）。

数组：如果父节点的数组下标是 i，那么它的左孩子就是 i _ 2 + 1，右孩子就是 i _ 2 + 2

二叉树的遍历方式

1.深度优先遍历：先往深走，遇到叶子节点再往回走：

前序遍历（递归法，迭代法）；

中序遍历（递归法，迭代法）；

后序遍历（递归法，迭代法） 【栈】

2.广度优先遍历：一层一层的去遍历：

层次遍历（迭代法）【队列】

树-定义树子节点

```js
class TreeNode {
  val: number;
  left: TreeNode | null;
  right: TreeNode | null;
  constructor(val?: number, left?: TreeNode | null, right?: TreeNode | null) {
    this.val = val === undefined ? 0 : val;
    this.left = left === undefined ? null : left;
    this.right = right === undefined ? null : right;
  }
}
```

### 144. 二叉树的前序遍历

给你二叉树的根节点 root ，返回它节点值的前序遍历。

```js
// 递归法
function preorderTraversal(root: TreeNode | null): number[] {
  function traverse(node: TreeNode | null, res: number[]) {
    if (node === null) return;
    res.push(node.val);
    traverse(node.left, res);
    traverse(node.right, res);
  }

  const result: number[] = [];
  traverse(root, result);
  return result;
}

// 迭代法 中左右
function preorderTraversal(root: TreeNode | null): number[] {
  if (root === null) return [];
  let result: number[] = [];
  let helperStack: TreeNode[] = [];
  let current: TreeNode = root;
  helperStack.push(current);

  while (helperStack.length > 0) {
    current = helperStack.pop();
    result.push(current.val);
    if (current.right !== null) helperStack.push(current.right);
    if (current.left !== null) helperStack.push(current.left);
  }
  return result;
}
```

### 145. 二叉树的后序遍历

给你一棵二叉树的根节点 root ，返回其节点值的后序遍历 。

```js
// 递归法
function postorderTraversal(root: TreeNode | null): number[] {
  function traverse(node: TreeNode | null, res: number[]) {
    if (node === null) return;
    traverse(node.left, res);
    traverse(node.right, res);
    res.push(node.val);
  }

  const result: number[] = [];
  traverse(root, result);
  return result;
}

// 迭代法 中右左-->左右中（反转）
function postorderTraversal(root: TreeNode | null): number[] {
  if (root === null) return [];
  let result: number[] = [];
  let current: TreeNode = root;
  let helperStack: TreeNode[] = [root];

  while (helperStack.length) {
    current = helperStack.pop();
    result.push(current.val);
    if (current.left) helperStack.push(current.left);
    if (current.right) helperStack.push(current.right);
  }

  return result.reverse();
}
```

### 94. 二叉树的中序遍历

给定一个二叉树的根节点 root ，返回 它的中序遍历 。

```js
// 递归法
function inorderTraversal(root: TreeNode | null): number[] {
  function traverse(node: TreeNode | null, res: number[]) {
    if (node === null) return;
    traverse(node.left, res);
    res.push(node.val);
    traverse(node.right, res);
  }

  const result: number[] = [];
  traverse(root, result);
  return result;
}

// 迭代法
function inorderTraversal(root: TreeNode | null): number[] {
  if (root === null) return [];
  let result: number[] = [];
  let helperStack: TreeNode[] = [];
  let current = root;

  while (current || helperStack.length) {
    if (current) {
      helperStack.push(current);
      current = current.left ?? null;
    } else {
      current = helperStack.pop();
      result.push(current.val);
      current = current.right ?? null;
    }
  }

  return result;
}
```

### 102. 二叉树的层序遍历

给你二叉树的根节点 root ，返回其节点值的 层序遍历 。 （即逐层地，从左到右访问所有节点）。

```js
function levelOrder(root: TreeNode | null): number[][] {
  if (root === null) return [];
  let helperQueue: TreeNode[] = [root];
  let resultArr = [];
  let tempArr: number[] = [];

  while (helperQueue.length) {
    for (let i = 0, len = helperQueue.length; i < len; i++) {
      const node = helperQueue.shift();
      tempArr.push(node.val);
      if (node.left) helperQueue.push(node.left);
      if (node.right) helperQueue.push(node.right);
    }
    resultArr.push(tempArr);
    tempArr = [];
  }
  return resultArr;
}
```

### 107. 二叉树的层序遍历 II

给你二叉树的根节点 root ，返回其节点值 自底向上的层序遍历 。 （即按从叶子节点所在层到根节点所在的层，逐层从左向右遍历）

```js
function levelOrderBottom(root: TreeNode | null): number[][] {
  if (root === null) return [];
  let helperQueue: TreeNode[] = [root];
  let resultArr = [];
  let tempArr: number[] = [];

  while (helperQueue.length) {
    for (let i = 0, len = helperQueue.length; i < len; i++) {
      const node = helperQueue.shift();
      tempArr.push(node.val);
      if (node.left) helperQueue.push(node.left);
      if (node.right) helperQueue.push(node.right);
    }
    resultArr.unshift(tempArr);
    tempArr = [];
  }
  return resultArr;
}
```

### 199. 二叉树的右视图

给定一个二叉树的 根节点 root，想象自己站在它的右侧，按照从顶部到底部的顺序，返回从右侧所能看到的节点值。

示例 1:
输入: [1,2,3,null,5,null,4]输出: [1,3,4]

```js
function rightSideView(root: TreeNode | null): number[] {
  if (root === null) return [];

  let helperQueue: TreeNode[] = [root];
  let result: number[] = [];

  while (helperQueue.length) {
    for (let i = 0, len = helperQueue.length; i < len; i++) {
      const node = helperQueue.shift();
      if (i == len - 1) result.push(node.val);
      if (node.left) helperQueue.push(node.left);
      if (node.right) helperQueue.push(node.right);
    }
  }
  return result;
}
```

### 637. 二叉树的层平均值

给定一个非空二叉树的根节点 root , 以数组的形式返回每一层节点的平均值。与实际答案相差 10 -5 以内的答案可以被接受。

```js
function averageOfLevels(root: TreeNode | null): number[] {
  let helperQueue: TreeNode[] = [root];
  let lineSum: number = 0;
  let result: number[] = [];
  let currentNode: TreeNode;

  while (helperQueue.length) {
    for (let i = 0, len = helperQueue.length; i < len; i++) {
      currentNode = helperQueue.shift();
      lineSum += currentNode.val;
      if (i === len - 1) {
        result.push(lineSum / len);
        lineSum = 0;
      }
      if (currentNode.left) helperQueue.push(currentNode.left);
      if (currentNode.right) helperQueue.push(currentNode.right);
    }
  }
  return result;
}
```

### 589. N 叉树的前序遍历

### 590. N 叉树的后序遍历

### 429. N 叉树的层序遍历

### 515. 在每个树行中找最大值

### 116. 填充每个节点的下一个右侧节点指针

### 117. 填充每个节点的下一个右侧节点指针 II

### 104. 二叉树的最大深度

### 111. 二叉树的最小深度

### 226. 翻转二叉树

给你一棵二叉树的根节点 root ，翻转这棵二叉树，并返回其根节点。

示例 1：输入：root = [4,2,7,1,3,6,9]输出：[4,7,2,9,6,3,1]

```js
// 递归法--前序遍历
function invertTree(root: TreeNode | null): TreeNode | null {
  if (!root) return root;
  // 交换左右子节点
  let tempNode: TreeNode = root.right;
  root.right = root.left;
  root.left = tempNode;
  // 翻转子节点的 左 / 右子节点
  invertTree(root.left);
  invertTree(root.right);
  return root;
}

// 后序遍历
function invertTree(root: TreeNode | null): TreeNode | null {
  if (!root) return root;

  invertTree(root.left);
  invertTree(root.right);

  let tempNode: TreeNode = root.right;
  root.right = root.left;
  root.left = tempNode;
  return root;
}

// 中序遍历
function invertTree(root: TreeNode | null): TreeNode | null {
  if (!root) return root;

  invertTree(root.left);
  let tempNode: TreeNode = root.right;
  root.right = root.left;
  root.left = tempNode;
  // 因为左右节点已经进行交换，此时的root.left 是原先的root.right
  invertTree(root.left);

  return root;
}
```

### 101. 对称二叉树

给你一个二叉树的根节点 root ， 检查它是否轴对称。

示例 1：输入：root = [1,2,2,3,4,4,3]输出：true

## 回溯算法

### 回溯法解决问题分类

回溯法，一般可以解决如下几种问题：

- 组合问题：N 个数里面按一定规则找出 k 个数的集合
- 切割问题：一个字符串按一定规则有几种切割方式
- 子集问题：一个 N 个数的集合里有多少符合条件的子集
- 排列问题：N 个数按一定规则全排列，有几种排列方式
- 棋盘问题：N 皇后，解数独等等
  回溯法解决的问题都可以抽象为树形结构，中心思想：for 循环横向遍历，递归纵向遍历，回溯不断调整结果集
  回溯法解决的都是在集合中递归查找子集，集合的大小就构成了树的宽度，递归的深度，构成了树的深度。
  回溯算法通常使用递归来实现。
  递归的本质是函数调用自身，每次调用都会将当前状态压入调用栈。当递归到某一层时，如果发现当前路径不符合条件，就需要回溯到上一层，即退出当前函数的执行并返回到上一层函数的调用处。

### 回溯法模版

```js
// for 循环横向遍历，递归纵向遍历，回溯不断调整结果集
function backtracking(参数) {
if (终止条件) {
存放结果;
return;
}

    for (选择：本层集合中元素（树中节点孩子的数量就是集合的大小）) {
        处理节点，存放满足条件的结果;
        backtracking(路径，选择列表); // 向下纵向递归
        弹出节点最后一项，以用于下一次递归
    }

}
```

### ‼️77. 组合

给定两个整数 n 和 k，返回范围 [1, n] 中所有可能的 k 个数的组合。你可以按 任何顺序 返回答案。
示例 1：
输入：n = 4, k = 2 输出：[ [2,4], [3,4], [2,3], [1,2], [1,3], [1,4],]

#### 题解

```js
// 未优化（未剪枝）
var combine = function (n, k) {
  let result = [];

  const backTrack = (startIndex, current) => {
    // 如果当前列表的长度等于k，说明找到了
    if (current.length === k) {
      result.push([...current]);
      return;
    }

    // 从startIndex 遍历到n
    for (let i = startIndex; i <= n; i++) {
      current.push(i);
      backTrack(i + 1, current);
      current.pop();
    }
  };

  backTrack(1, []);
  return result;
};
```

如何进行优化？
有效的剪枝策略：在递归过程中，当剩余可选元素不足以构成一个完整的组合时，就提前结束递归。

优化版题解：

```js
var combine = function (n, k) {
  let result = [];

  const backTrack = (startIndex, current) => {
    // 如果当前列表的长度等于k，说明找到了
    if (current.length === k) {
      result.push([...current]);
      return;
    }

    // 从startIndex 遍历到n current.length n-k+1
    for (let i = startIndex; i <= n - (k - current.length) + 1; i++) {
      current.push(i);
      backTrack(i + 1, current);
      current.pop();
    }
  };

  backTrack(1, []);
  return result;
};
```

### ‼️216. 组合总和 III

找出所有相加之和为 n 的 k 个数的组合，且满足下列条件：

- 只使用数字 1 到 9
- 每个数字 最多使用一次
  返回 所有可能的有效组合的列表 。该列表不能包含相同的组合两次，组合可以以任何顺序返回。

  示例 1:
  输入: k = 3, n = 7 输出: [[1,2,4]]解释:1 + 2 + 4 = 7 没有其他符合的组合了。

  示例 2:
  输入: k = 3, n = 9 输出: [[1,2,6], [1,3,5], [2,3,4]]解释:1 + 2 + 6 = 91 + 3 + 5 = 92 + 3 + 4 = 9 没有其他符合的组合了。

  示例 3:
  输入: k = 4, n = 1 输出: []解释: 不存在有效的组合。在[1,9]范围内使用 4 个不同的数字，我们可以得到的最小和是 1+2+3+4 = 10，因为 10 > 1，没有有效的组合。

#### 题解

```js
var combinationSum3 = function (k, n) {
  let result = [];

  const backTrack = (startIndex, tempArr, sum) => {
    // 如果长度满足要求，（与n相等就push数组）return
    if (tempArr.length === k) {
      if (sum === n) result.push([...tempArr]);
      return;
    }

    for (let i = startIndex; i <= 9 - (k - tempArr.length) + 1; i++) {
      sum += i;
      tempArr.push(i);
      // 如果sum值大于n，回溯
      if (sum > n) {
        sum -= i;
        tempArr.pop();
        return;
      }
      backTrack(i + 1, tempArr, sum);
      sum -= i;
      tempArr.pop();
    }
  };

  backTrack(1, [], 0);
  return result;
};
```

### 17. 电话号码的字母组合

给定一个仅包含数字 2-9 的字符串，返回所有它能表示的字母组合。答案可以按 任意顺序 返回。
给出数字到字母的映射如下（与电话按键相同）。注意 1 不对应任何字母。

示例 1：
输入：digits = "23"输出：["ad","ae","af","bd","be","bf","cd","ce","cf"]

示例 2：
输入：digits = ""输出：[]

示例 3：
输入：digits = "2"输出：["a","b","c"]

#### 题解

```js
var letterCombinations = function (digits) {
  if (!digits) return [];
  const letterMap = {
    2: ['a', 'b', 'c'],
    3: ['d', 'e', 'f'],
    4: ['g', 'h', 'i'],
    5: ['j', 'k', 'l'],
    6: ['m', 'n', 'o'],
    7: ['p', 'q', 'r', 's'],
    8: ['t', 'u', 'v'],
    9: ['w', 'x', 'y', 'z']
  };

  const result = [];

  function backTrack(currentInd, tempArr) {
    if (tempArr.length === digits.length) {
      result.push([...tempArr].join(''));
      return;
    }

    const letters = letterMap[digits[currentInd]];

    for (let i = 0; i < letters.length; i++) {
      tempArr.push(letters[i]);
      backTrack(currentInd + 1, tempArr);
      tempArr.pop();
    }
  }

  backTrack(0, []);
  return result;
};
```

### 39. 组合总和

给你一个 无重复元素 的整数数组 candidates 和一个目标整数 target ，找出 candidates 中可以使数字和为目标数 target 的 所有 不同组合 ，并以列表形式返回。你可以按 任意顺序 返回这些组合。
candidates 中的 同一个 数字可以 无限制重复被选取 。如果至少一个数字的被选数量不同，则两种组合是不同的。
对于给定的输入，保证和为 target 的不同组合数少于 150 个。

示例 1：
输入：candidates = [2,3,6,7], target = 7
输出：[[2,2,3],[7]]
解释：
2 和 3 可以形成一组候选，2 + 2 + 3 = 7 。注意 2 可以使用多次。
7 也是一个候选， 7 = 7 。
仅有这两种组合。

示例 2：
输入: candidates = [2,3,5], target = 8
输出: [[2,2,2,2],[2,3,3],[3,5]]

示例 3：
输入: candidates = [2], target = 1
输出: []

#### 题解

```js
var combinationSum = function (candidates, target) {
  const result = [];

  function backTrack(currentSum, currentInd, tempArr) {
    if (currentSum >= target) {
      currentSum === target && result.push([...tempArr]);
      return;
    }

    for (let i = currentInd; i < candidates.length; i++) {
      tempArr.push(candidates[i]);
      currentSum += candidates[i];
      if (sum > target) {
        current.pop();
        sum -= candidates[i];
        continue;
      }
      backTrack(currentSum, i, tempArr);
      currentSum -= candidates[i];
      tempArr.pop();
    }
  }

  backTrack(0, 0, []);
  return result;
};
```

### 40. 组合总和 II

给定一个候选人编号的集合 candidates 和一个目标数 target ，找出 candidates 中所有可以使数字和为 target 的组合。
candidates 中的每个数字在每个组合中只能使用 一次 。
注意：解集不能包含重复的组合。

示例 1:
输入: candidates = [10,1,2,7,6,1,5], target = 8, 输出: [[1,1,6],[1,2,5],[1,7],[2,6]]

示例 2:
输入: candidates = [2,5,2,1,2], target = 5,输出:[[1,2,2],[5]]

#### 题解

```js
var combinationSum2 = function (candidates, target) {
  const result = [];
  candidates.sort((a, b) => a - b);

  function backTrack(currentSum, currentInd, tempArr) {
    if (currentSum >= target) {
      currentSum === target && result.push([...tempArr]);
      return;
    }

    for (let i = currentInd; i < candidates.length; i++) {
      // 优化
      if (candidates[i] > target - currentSum) continue;
      // 去重
      if (i > currentInd && candidates[i] === candidates[i - 1]) continue;
      tempArr.push(candidates[i]);
      currentSum += candidates[i];
      backTrack(currentSum, i + 1, tempArr);
      tempArr.pop();
      currentSum -= candidates[i];
    }
  }

  backTrack(0, 0, []);
  return result;
};
```

### ‼️131. 分割回文串

给你一个字符串 s，请你将 s 分割成一些子串，使每个子串都是
回文串 。返回
s 所有可能的分割方案。

示例 1：
输入：s = "aab"输出：[["a","a","b"],["aa","b"]]

示例 2：
输入：s = "a"输出：[["a"]]

#### 题解

```js
const isPalindrome = (str, left, right) => {
  for (let i = left, j = right; i < j; i++, j--) {
    if (str[i] !== str[j]) return false;
  }
  return true;
};

var partition = function (s) {
  const result = [];
  backTrack(0, []);

  function backTrack(startIndex, tempArr) {
    if (startIndex >= s.length) {
      result.push([...tempArr]);
      return;
    }

    for (let i = startIndex; i < s.length; i++) {
      if (!isPalindrome(s, startIndex, i)) continue;
      tempArr.push(s.slice(startIndex, i + 1));
      backTrack(i + 1, tempArr);
      tempArr.pop();
    }
  }
  return result;
};
```

### 93. 复原 IP 地址

有效 IP 地址 正好由四个整数（每个整数位于 0 到 255 之间组成，且不能含有前导 0），整数之间用 '.' 分隔。

- 例如："0.1.2.201" 和 "192.168.1.1" 是 有效 IP 地址，但是 "0.011.255.245"、"192.168.1.312" 和 "192.168@1.1" 是 无效 IP 地址。
  给定一个只包含数字的字符串 s ，用以表示一个 IP 地址，返回所有可能的有效 IP 地址，这些地址可以通过在 s 中插入 '.' 来形成。你 不能 重新排序或删除 s 中的任何数字。你可以按 任何 顺序返回答案。

  示例 1：
  输入：s = "25525511135"输出：["255.255.11.135","255.255.111.35"]

  示例 2：
  输入：s = "0000"输出：["0.0.0.0"]

  示例 3：
  输入：s = "101023"输出：["1.0.10.23","1.0.102.3","10.1.0.23","10.10.2.3","101.0.2.3"]

#### 题解

```js
var restoreIpAddresses = function (s) {
  const result = [];
  backTrack(0, []);

  function backTrack(currentInd, tempArr) {
    if (tempArr.length === 4 && currentInd === s.length) {
      result.push(tempArr.join('.')); // 用.拼接
      return;
    } // 优先判断正确情况
    if (tempArr.length >= 4 || currentInd >= s.length) return; // 超过4段

    for (let i = currentInd; i < s.length; i++) {
      const str = s.slice(currentInd, i + 1);
      if (Number(str) > 255 || str.length > 3) break; // 大于255
      if (str[0] === '0' && str.length > 1) break; // 含有前导0
      tempArr.push(str);
      backTrack(i + 1, tempArr);
      tempArr.pop();
    }
  }
  return result;
};

// 数字校验条件：1.<=255；2.不含有非导 0；ip 地址校验条件：tempArr 的长度等于 4 且分割结束（currentInd=s.length）
```

### ‼️78. 子集

给你一个整数数组 nums ，数组中的元素 互不相同 。返回该数组所有可能的子集（幂集）。
解集 不能 包含重复的子集。你可以按 任意顺序 返回解集。

示例 1：
输入：nums = [1,2,3]输出：[[],[1],[2],[1,2],[3],[1,3],[2,3],[1,2,3]]

示例 2：
输入：nums = [0]输出：[[],[0]]

#### 题解

```js
var subsets = function (nums) {
  const result = [],
    route = [];
  backTrack(0);
  return result;

  function backTrack(currentInd) {
    result.push([...route]);

    for (let i = currentInd; i < nums.length; i++) {
      route.push(nums[i]);
      backTrack(i + 1);
      route.pop();
    }
  }
};
```

### ‼️90. 子集 II

给你一个整数数组 nums ，其中可能包含重复元素，请你返回该数组所有可能的<span data-keyword="subset">子集</span>（幂集）。
解集 不能 包含重复的子集。返回的解集中，子集可以按 任意顺序 排列。

示例 1：
输入：nums = [1,2,2]输出：[[],[1],[1,2],[1,2,2],[2],[2,2]]

示例 2：
输入：nums = [0]输出：[[],[0]]

#### 题解

```js
var subsetsWithDup = function (nums) {
  const result = [];
  nums.sort((a, b) => a - b); // 对数组进行排序

  function backTrack(currentInd, route) {
    result.push([...route]);

    for (let i = currentInd; i < nums.length; i++) {
      // 跳过重复读取的值
      if (currentInd < i && nums[i] === nums[i - 1]) continue;
      route.push(nums[i]);
      backTrack(i + 1, route);
      route.pop();
    }
  }

  backTrack(0, []);
  return result;
};
```

### ‼️491. 非递减子序列

给你一个整数数组 nums ，找出并返回所有该数组中不同的递增子序列，递增子序列中 至少有两个元素 。你可以按 任意顺序 返回答案。
数组中可能含有重复元素，如出现两个整数相等，也可以视作递增序列的一种特殊情况。

示例 1：
输入：nums = [4,6,7,7]输出：[[4,6],[4,6,7],[4,6,7,7],[4,7],[4,7,7],[6,7],[6,7,7],[7,7]]

示例 2：
输入：nums = [4,4,3,2,1]输出：[[4,4]]

#### 题解

```js
var findSubsequences = function (nums) {
  const result = [];

  function backTrack(currentInd, route) {
    if (route.length >= 2) result.push([...route]); // 至少两个元素

    const usedSet = new Set(); // 记录使用过的元素
    for (let i = currentInd; i < nums.length; i++) {
      // 同一父节点下的同层上使用过的元素就不能再使用了
      if (usedSet.has(nums[i])) continue;
      // 是否满足递增条件：route的最后一个元素<=nums[i]
      if (route[route.length - 1] > nums[i]) continue;

      route.push(nums[i]);
      usedSet.add(nums[i]);
      backTrack(i + 1, route);
      route.pop();
    }
  }

  backTrack(0, []);
  return result;
};
```

### ‼️46. 全排列

给定一个不含重复数字的数组 nums ，返回其 所有可能的全排列 。你可以 按任意顺序 返回答案。

示例 1：
输入：nums = [1,2,3]输出：[[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]

示例 2：
输入：nums = [0,1]输出：[[0,1],[1,0]]

示例 3：
输入：nums = [1]输出：[[1]]

#### 题解

用数组记录使用过的元素

```js
var permute = function (nums) {
  const result = [],
    usedMap = new Map();

  function backTrack(route, usedMap) {
    if (route.length === nums.length) {
      result.push([...route]);
      return;
    }

    for (let i = 0; i < nums.length; i++) {
      if (usedMap.has(nums[i])) continue;
      route.push(nums[i]);
      usedMap.set(nums[i], true);
      backTrack(route, usedMap);
      route.pop();
      usedMap.delete(nums[i]);
    }
  }

  backTrack([], usedMap);
  return result;
};
```

### ‼️47. 全排列 II

给定一个可包含重复数字的序列 nums ，按任意顺序 返回所有不重复的全排列。

示例 1：
输入：nums = [1,1,2]输出：[[1,1,2], [1,2,1], [2,1,1]]

示例 2：
输入：nums = [1,2,3]输出：[[1,2,3],[1,3,2],[2,1,3],[2,3,1],[3,1,2],[3,2,1]]

#### 题解

```js
function permuteUnique(nums: number[]): number[][] {
  nums.sort((a, b) => a - b);

  const result: number[][] = [],
    usedArr: boolean[] = new Array(nums.length).fill(false);
  backTrack(nums, []);
  return result;

  function backTrack(nums: number[], route: number[]): void {
    if (route.length === nums.length) {
      result.push([...route]);
      return;
    }

    for (let i = 0; i < nums.length; i++) {
      // nums[i]===nums[i-1] && usedArr[i-1]===false 说明同一树层上有两个重复的元素nums[i]和nums[i-1],不可以重复选取
      if (i > 0 && nums[i] === nums[i - 1] && usedArr[i - 1] === false)
        continue;

      if (!usedArr[i]) {
        route.push(nums[i]);
        usedArr[i] = true;
        backTrack(nums, route);
        usedArr[i] = false;
        route.pop();
      }
    }
  }
}
```

### 22. 括号生成

数字 n 代表生成括号的对数，请你设计一个函数，用于能够生成所有可能的并且 有效的 括号组合。

示例 1：
输入：n = 3 输出：["((()))","(()())","(())()","()(())","()()()"]

示例 2：
输入：n = 1 输出：["()"]

#### 题解

```js
function generateParenthesis(n: number): string[] {
  const result: string[] = [];

  function backTrack(leftCount: number, rightCount: number, route: string) {
    if (route.length >= 2 * n) {
      result.push(route);
      return;
    }

    if (leftCount > 0) {
      backTrack(leftCount - 1, rightCount, route + '(');
    }

    // 当剩下的)比(多时，才可以选)
    if (leftCount < rightCount) {
      backTrack(leftCount, rightCount - 1, route + ')');
    }
  }
  backTrack(n, n, '');
  return result;
}
```

### 332. 重新安排行程（困难）

给你一份航线列表 tickets ，其中 tickets[i] = [fromi, toi] 表示飞机出发和降落的机场地点。请你对该行程进行重新规划排序。
所有这些机票都属于一个从 JFK（肯尼迪国际机场）出发的先生，所以该行程必须从 JFK 开始。如果存在多种有效的行程，请你按字典排序返回最小的行程组合。

- 例如，行程 ["JFK", "LGA"] 与 ["JFK", "LGB"] 相比就更小，排序更靠前。
  假定所有机票至少存在一种合理的行程。且所有的机票 必须都用一次 且 只能用一次。
  示例 1：

输入：tickets = [["MUC","LHR"],["JFK","MUC"],["SFO","SJC"],["LHR","SFO"]]输出：["JFK","MUC","LHR","SFO","SJC"]

示例 2：

输入：tickets = [["JFK","SFO"],["JFK","ATL"],["SFO","ATL"],["ATL","JFK"],["ATL","SFO"]]输出：["JFK","ATL","JFK","SFO","ATL","SFO"]解释：另一种有效的行程是 ["JFK","SFO","ATL","JFK","ATL","SFO"] ，但是它字典排序更大更靠后。

### 51. N 皇后（困难）

按照国际象棋的规则，皇后可以攻击与之处在同一行或同一列或同一斜线上的棋子。
n 皇后问题 研究的是如何将 n 个皇后放置在 n×n 的棋盘上，并且使皇后彼此之间不能相互攻击。
给你一个整数 n ，返回所有不同的 n 皇后问题 的解决方案。
每一种解法包含一个不同的 n 皇后问题 的棋子放置方案，该方案中 'Q' 和 '.' 分别代表了皇后和空位。
示例 1：

输入：n = 4 输出：[[".Q..","...Q","Q...","..Q."],["..Q.","Q...","...Q",".Q.."]]解释：如上图所示，4 皇后问题存在两个不同的解法。

示例 2：
输入：n = 1 输出：[["Q"]]

### 37. 解数独（困难）

编写一个程序，通过填充空格来解决数独问题。
数独的解法需 遵循如下规则： 1.数字 1-9 在每一行只能出现一次。 2.数字 1-9 在每一列只能出现一次。 3.数字 1-9 在每一个以粗实线分隔的 3x3 宫内只能出现一次。（请参考示例图）
数独部分空格内已填入了数字，空白格用 '.' 表示。
示例 1：

输入：board = [["5","3",".",".","7",".",".",".","."],["6",".",".","1","9","5",".",".","."],[".","9","8",".",".",".",".","6","."],["8",".",".",".","6",".",".",".","3"],["4",".",".","8",".","3",".",".","1"],["7",".",".",".","2",".",".",".","6"],[".","6",".",".",".",".","2","8","."],[".",".",".","4","1","9",".",".","5"],[".",".",".",".","8",".",".","7","9"]]输出：[["5","3","4","6","7","8","9","1","2"],["6","7","2","1","9","5","3","4","8"],["1","9","8","3","4","2","5","6","7"],["8","5","9","7","6","1","4","2","3"],["4","2","6","8","5","3","7","9","1"],["7","1","3","9","2","4","8","5","6"],["9","6","1","5","3","7","2","8","4"],["2","8","7","4","1","9","6","3","5"],["3","4","5","2","8","6","1","7","9"]]解释：输入的数独如上图所示，唯一有效的解决方案如下所示：

## 贪心算法

贪心算法一般分为如下四步：

- 将问题分解为若干个子问题
- 找出适合的贪心策略
- 求解每一个子问题的最优解
- 将局部最优解堆叠成全局最优解

### 455. 分发饼干

假设你是一位很棒的家长，想要给你的孩子们一些小饼干。但是，每个孩子最多只能给一块饼干。
对每个孩子 i，都有一个胃口值 g[i]，这是能让孩子们满足胃口的饼干的最小尺寸；并且每块饼干 j，都有一个尺寸 s[j] 。如果 s[j] >= g[i]，我们可以将这个饼干 j 分配给孩子 i ，这个孩子会得到满足。你的目标是尽可能满足越多数量的孩子，并输出这个最大数值。

示例 1:
输入: g = [1,2,3], s = [1,1]输出: 1
解释: 你有三个孩子和两块小饼干，3 个孩子的胃口值分别是：1,2,3。虽然你有两块小饼干，由于他们的尺寸都是 1，你只能让胃口值是 1 的孩子满足。所以你应该输出 1。

示例 2:
输入: g = [1,2], s = [1,2,3]输出: 2
解释: 你有两个孩子和三块小饼干，2 个孩子的胃口值分别是 1,2。你拥有的饼干数量和尺寸都足以让所有孩子满足。所以你应该输出 2.

#### 题解

```js
var findContentChildren = function (g, s) {
  g.sort((a, b) => a - b);
  s.sort((a, b) => a - b);
  let sIndex = s.length - 1,
    result = 0;

  for (let i = g.length - 1; i >= 0; i--) {
    if (sIndex >= 0 && s[sIndex] >= g[i]) {
      result++;
      sIndex--;
    }
  }
  return result;
};
```

### 376. 摆动序列

如果连续数字之间的差严格地在正数和负数之间交替，则数字序列称为 摆动序列 。第一个差（如果存在的话）可能是正数或负数。仅有一个元素或者含两个不等元素的序列也视作摆动序列。

- 例如， [1, 7, 4, 9, 2, 5] 是一个 摆动序列 ，因为差值 (6, -3, 5, -7, 3) 是正负交替出现的。
- 相反，[1, 4, 7, 2, 5] 和 [1, 7, 4, 5, 5] 不是摆动序列，第一个序列是因为它的前两个差值都是正数，第二个序列是因为它的最后一个差值为零。
  子序列 可以通过从原始序列中删除一些（也可以不删除）元素来获得，剩下的元素保持其原始顺序。
  给你一个整数数组 nums ，返回 nums 中作为 摆动序列 的 最长子序列的长度 。

  示例 1：
  输入：nums = [1,7,4,9,2,5]输出：6 解释：整个序列均为摆动序列，各元素之间的差值为 (6, -3, 5, -7, 3) 。

  示例 2：
  输入：nums = [1,17,5,10,13,15,10,5,16,8]输出：7 解释：这个序列包含几个长度为 7 摆动序列。其中一个是 [1, 17, 10, 13, 10, 16, 8] ，各元素之间的差值为 (16, -7, 3, -3, 6, -8) 。

  示例 3：
  输入：nums = [1,2,3,4,5,6,7,8,9]输出：2

  题解

  1.情况一：上下坡中有平坡,记录峰值的条件为：(preDiff <= 0 && curDiff > 0) || (preDiff >= 0 && curDiff < 0)

  2.情况二：数组首尾两端,针对序列[2,5]，可以假设为[2,2,5]，这样它就有坡度了即 preDiff = 0
  result 初始值为 1（默认最右边有一个峰值）

  3.情况三：单调坡中有平坡

```js
var wiggleMaxLength = function (nums) {
  if (nums.length <= 1) return nums.length;
  // 将 result 初始值设为 1，preDiff = 0，兼容只有 2 个元素的情况
  let result = 1,
    preDiff = 0,
    curDiff = 0;
  for (let i = 0; i < nums.length; i++) {
    curDiff = nums[i + 1] - nums[i];
    // 考虑上下坡有平坡的情况
    if ((curDiff > 0 && preDiff <= 0) || (curDiff < 0 && preDiff >= 0)) {
      // 在坡度正负变化时，更新 preDiff，兼容单调坡度的情况
      result++;
      preDiff = curDiff;
    }
  }
  return result;
};
```

### 53. 最大子数组和

给你一个整数数组 nums ，请你找出一个具有最大和的连续子数组（子数组最少包含一个元素），返回其最大和。
子数组是数组中的一个连续部分。

示例 1：
输入：nums = [-2,1,-3,4,-1,2,1,-5,4]输出：6 解释：连续子数组 [4,-1,2,1] 的和最大，为 6 。

示例 2：
输入：nums = [1]输出：1

示例 3：
输入：nums = [5,4,-1,7,8]输出：23

#### 题解

局部最优：当前“连续和”为负数的时候立刻放弃，从下一个元素重新计算“连续和”，因为负数加上下一个元素 “连续和”只会越来越小。

```js
var maxSubArray = function (nums) {
  let result = -Infinity,
    count = 0;

  for (let i = 0; i < nums.length; i++) {
    count += nums[i];
    // 更新result为动态最大值
    if (count > result) result = count;
    // “连续和”为负数时重新计算
    if (count < 0) count = 0;
  }
  return result;
};
```

### 122. 买卖股票的最佳时机 II

给你一个整数数组 prices ，其中 prices[i] 表示某支股票第 i 天的价格。
在每一天，你可以决定是否购买和/或出售股票。你在任何时候 最多 只能持有 一股 股票。你也可以先购买，然后在 同一天 出售。
返回 你能获得的 最大 利润 。

示例 1：
输入：prices = [7,1,5,3,6,4]输出：7 解释：在第 2 天（股票价格 = 1）的时候买入，在第 3 天（股票价格 = 5）的时候卖出, 这笔交易所能获得利润 = 5 - 1 = 4 。 随后，在第 4 天（股票价格 = 3）的时候买入，在第 5 天（股票价格 = 6）的时候卖出, 这笔交易所能获得利润 = 6 - 3 = 3 。 总利润为 4 + 3 = 7 。

示例 2：
输入：prices = [1,2,3,4,5]输出：4 解释：在第 1 天（股票价格 = 1）的时候买入，在第 5 天 （股票价格 = 5）的时候卖出, 这笔交易所能获得利润 = 5 - 1 = 4 。 总利润为 4 。

示例 3：
输入：prices = [7,6,4,3,1]输出：0 解释：在这种情况下, 交易无法获得正利润，所以不参与交易可以获得最大利润，最大利润为 0 。

#### 题解

```js
var maxProfit = function (prices) {
  let result = 0;
  for (let i = 1; i < prices.length; i++) {
    result += Math.max(prices[i] - prices[i - 1], 0);
  }
  return result;
};
```

### 55. 跳跃游戏

给你一个非负整数数组 nums ，你最初位于数组的 第一个下标 。数组中的每个元素代表你在该位置可以跳跃的最大长度。
判断你是否能够到达最后一个下标，如果可以，返回 true ；否则，返回 false 。

示例 1：
输入：nums = [2,3,1,1,4]输出：true 解释：可以先跳 1 步，从下标 0 到达下标 1, 然后再从下标 1 跳 3 步到达最后一个下标。

示例 2：
输入：nums = [3,2,1,0,4]输出：false 解释：无论怎样，总会到达下标为 3 的位置。但该下标的最大跳跃长度是 0 ， 所以永远不可能到达最后一个下标。

#### 题解

```js
var canJump = function (nums) {
  if (nums.length === 1) return true;
  let currentInd = 0;

  // i 每次移动只能在 currentInd 的范围内移动，每移动一个元素，currentInd 得到该元素数值（新的覆盖范围）的补充，让 i 继续移动下去。
  for (let i = 0; i <= currentInd; i++) {
    currentInd = Math.max(currentInd, i + nums[i]);
    if (currentInd >= nums.length - 1) return true;
  }

  return false;
};
```

### 45. 跳跃游戏 II

给定一个长度为 n 的 0 索引整数数组 nums。初始位置为 nums[0]。
每个元素 nums[i] 表示从索引 i 向前跳转的最大长度。换句话说，如果你在 nums[i] 处，你可以跳转到任意 nums[i + j] 处:

- 0 <= j <= nums[i]
- i + j < n
  返回到达 nums[n - 1] 的最小跳跃次数。生成的测试用例可以到达 nums[n - 1]。

  示例 1:输入: nums = [2,3,1,1,4]
  输出: 2
  解释: 跳到最后一个位置的最小跳跃数是 2。从下标为 0 跳到下标为 1 的位置，跳 1 步，然后跳 3 步到达数组的最后一个位置。

  示例 2:
  输入: nums = [2,3,0,1,4]输出: 2

  #### 题解

```js
var jump = function (nums) {
  let currentIndex = 0,
    nextIndex = 0,
    step = 0;

  for (let i = 0; i < nums.length - 1; i++) {
    nextIndex = Math.max(i + nums[i], nextIndex);

    // 移动下标达到了当前覆盖的最远距离下标时，步数就要加一，来增加覆盖距离
    if (i === currentIndex) {
      currentIndex = nextIndex;
      step++;
    }
  }
  return step;
};
```

### 1005. K 次取反后最大化的数组和

给你一个整数数组 nums 和一个整数 k ，按以下方法修改该数组：

- 选择某个下标 i 并将 nums[i] 替换为 -nums[i] 。
  重复这个过程恰好 k 次。可以多次选择同一个下标 i 。
  以这种方式修改数组后，返回数组 可能的最大和 。

示例 1：
输入：nums = [4,2,3], k = 1 输出：5 解释：选择下标 1 ，nums 变为 [4,-2,3] 。

示例 2：
输入：nums = [3,-1,0,2], k = 3 输出：6 解释：选择下标 (1, 2, 2) ，nums 变为 [3,1,0,2] 。

示例 3：
输入：nums = [2,-3,-1,5,-4], k = 2 输出：13 解释：选择下标 (1, 4) ，nums 变为 [2,3,-1,5,4] 。

思路

- 第一步：将数组按照绝对值大小从大到小排序，注意要按照绝对值的大小
- 第二步：从前向后遍历，遇到负数将其变为正数，同时 K--
- 第三步：如果 K 还大于 0，那么反复转变数值最小的元素，将 K 用完
- 第四步：求和

#### 题解

```js
var largestSumAfterKNegations = function (nums, k) {
  nums.sort((a, b) => a - b);
  let ind = 0,
    sum = 0;

  while (k) {
    if (nums[ind] <= 0) {
      nums[ind] = Math.abs(nums[ind]);
      ind++;
      k--;
    } else break;
  }

  let isLeft = k % 2 !== 0;
  const min = Math.min(...nums);

  for (let i = 0; i < nums.length; i++) {
    if (isLeft && nums[i] === min) {
      sum -= nums[i];
      isLeft = false;
    } else sum += nums[i];
  }
  return sum;
};

// 方法二
var largestSumAfterKNegations = function (nums, k) {
  let sum = 0;

  nums.sort((a, b) => Math.abs(b) - Math.abs(a));

  for (let i = 0; i < nums.length; i++) {
    if (nums[i] < 0 && k > 0) {
      nums[i] = -nums[i];
      k--;
    }
    sum += nums[i];
  }

  if (k % 2 !== 0) sum -= 2 * nums[nums.length - 1];
  return sum;
};
```

### 134. 加油站

在一条环路上有 n 个加油站，其中第 i 个加油站有汽油 gas[i] 升。
你有一辆油箱容量无限的的汽车，从第 i 个加油站开往第 i+1 个加油站需要消耗汽油 cost[i] 升。你从其中的一个加油站出发，开始时油箱为空。
给定两个整数数组 gas 和 cost ，如果你可以按顺序绕环路行驶一周，则返回出发时加油站的编号，否则返回 -1 。如果存在解，则 保证 它是 唯一 的。

示例 1:
输入: gas = [1,2,3,4,5], cost = [3,4,5,1,2]
输出: 3
解释:从 3 号加油站(索引为 3 处)出发，可获得 4 升汽油。此时油箱有 = 0 + 4 = 4 升汽油开往 4 号加油站，此时油箱有 4 - 1 + 5 = 8 升汽油开往 0 号加油站，此时油箱有 8 - 2 + 1 = 7 升汽油开往 1 号加油站，此时油箱有 7 - 3 + 2 = 6 升汽油开往 2 号加油站，此时油箱有 6 - 4 + 3 = 5 升汽油开往 3 号加油站，你需要消耗 5 升汽油，正好足够你返回到 3 号加油站。因此，3 可为起始索引。

示例 2:
输入: gas = [2,3,4], cost = [3,4,3]
输出: -1
解释:你不能从 0 号或 1 号加油站出发，因为没有足够的汽油可以让你行驶到下一个加油站。我们从 2 号加油站出发，可以获得 4 升汽油。 此时油箱有 = 0 + 4 = 4 升汽油开往 0 号加油站，此时油箱有 4 - 3 + 2 = 3 升汽油开往 1 号加油站，此时油箱有 3 - 3 + 3 = 3 升汽油你无法返回 2 号加油站，因为返程需要消耗 4 升汽油，但是你的油箱只有 3 升汽油。因此，无论怎样，你都不可能绕环路行驶一周。
思路

- 情况一：如果 gas 的总和小于 cost 总和，那么无论从哪里出发，一定是跑不了一圈的
- 情况二：rest[i] = gas[i]-cost[i]为一天剩下的油，i 从 0 开始计算累加到最后一站，如果累加没有出现负数，说明从 0 出发，油就没有断过，那么 0 就是起点。
- 情况三：如果累加的最小值是负数，汽车就要从非 0 节点出发，从后向前，看哪个节点能把这个负数填平，能把这个负数填平的节点就是出发节点。

#### 题解

```js
var canCompleteCircuit = function (gas, cost) {
  let curSum = 0;
  let min = Infinity;

  for (let i = 0; i < gas.length; i++) {
    let rest = gas[i] - cost[i];
    curSum += rest;
    if (curSum < min) min = curSum;
  }
  if (curSum < 0) return -1; // 总油量 小于 总消耗量
  if (min > 0) return 0; // 邮箱一直有油

  // 当前累加 rest[i]的和 curSum 一旦小于 0，起始位置至少要是 i+1，因为从 i 之前开始一定不行。全局最优：找到可以跑一圈的起始位置。
  for (let i = gas.length - 1; i >= 0; i--) {
    let rest = gas[i] - cost[i];
    min += rest;
    if (min >= 0) return i;
  }
  return -1;
};
```

### 135. 分发糖果

n 个孩子站成一排。给你一个整数数组 ratings 表示每个孩子的评分。
你需要按照以下要求，给这些孩子分发糖果：

- 每个孩子至少分配到 1 个糖果。
- 相邻两个孩子评分更高的孩子会获得更多的糖果。
  请你给每个孩子分发糖果，计算并返回需要准备的 最少糖果数目 。

  示例 1：
  输入：ratings = [1,0,2]输出：5 解释：你可以分别给第一个、第二个、第三个孩子分发 2、1、2 颗糖果。

  示例 2：
  输入：ratings = [1,2,2]输出：4 解释：你可以分别给第一个、第二个、第三个孩子分发 1、2、1 颗糖果。 第三个孩子只得到 1 颗糖果，这满足题面中的两个条件。

  思路

- 自左向右，如果右侧元素大于左侧元素，右侧元素值为左侧元素 candy+1
- 自右向左，如果左侧元素大于右侧元素，左侧元素 candy 为右侧元素+1 和左侧元素现值取大

#### 题解

```js
var candy = function (ratings) {
  let candys = new Array(ratings.length).fill(1);
  // 自左向右，如果右侧元素大于左侧元素，右侧元素 candy+1
  for (let i = 1; i < ratings.length; i++) {
    if (ratings[i] > ratings[i - 1]) candys[i] = candys[i - 1] + 1;
  }

  // 自右向左，如果左侧元素大于右侧元素，左侧元素+1
  for (let i = ratings.length - 2; i >= 0; i--) {
    if (ratings[i] > ratings[i + 1])
      candys[i] = Math.max(candys[i], candys[i + 1] + 1);
  }

  let count = candys.reduce((a, b) => a + b);
  return count;
};
```

### 860. 柠檬水找零

在柠檬水摊上，每一杯柠檬水的售价为 5 美元。顾客排队购买你的产品，（按账单 bills 支付的顺序）一次购买一杯。
每位顾客只买一杯柠檬水，然后向你付 5 美元、10 美元或 20 美元。你必须给每个顾客正确找零，也就是说净交易是每位顾客向你支付 5 美元。
注意，一开始你手头没有任何零钱。
给你一个整数数组 bills ，其中 bills[i] 是第 i 位顾客付的账。如果你能给每位顾客正确找零，返回 true ，否则返回 false 。

示例 1：
输入：bills = [5,5,5,10,20]输出：true 解释：前 3 位顾客那里，我们按顺序收取 3 张 5 美元的钞票。第 4 位顾客那里，我们收取一张 10 美元的钞票，并返还 5 美元。第 5 位顾客那里，我们找还一张 10 美元的钞票和一张 5 美元的钞票。由于所有客户都得到了正确的找零，所以我们输出 true。

#### 题解

```js
var lemonadeChange = function (bills) {
  const moneyArr = new Array(3).fill(0);
  for (let i = 0; i < bills.length; i++) {
    if (bills[i] === 5) moneyArr[0] += 5;
    if (bills[i] === 10) {
      if (moneyArr[0]) {
        moneyArr[0] -= 5;
        moneyArr[1] += 10;
      } else return false;
    }
    if (bills[i] === 20) {
      if (moneyArr[1] && moneyArr[0]) {
        moneyArr[1] -= 10;
        moneyArr[0] -= 5;
        moneyArr[2] += 20;
      } else if (moneyArr[0] >= 15) moneyArr[0] -= 15;
      else return false;
    }
  }
  return true;
};
```

### 861. 根据身高重建队列

假设有打乱顺序的一群人站成一个队列，数组 people 表示队列中一些人的属性（不一定按顺序）。每个 people[i] = [hi, ki] 表示第 i 个人的身高为 hi ，前面 正好 有 ki 个身高大于或等于 hi 的人。
请你重新构造并返回输入数组 people 所表示的队列。返回的队列应该格式化为数组 queue ，其中 queue[j] = [hj, kj] 是队列中第 j 个人的属性（queue[0] 是排在队列前面的人）。

示例 1：
输入：people = [[7,0],[4,4],[7,1],[5,0],[6,1],[5,2]]
输出：[[5,0],[7,0],[5,2],[6,1],[4,4],[7,1]]
解释：编号为 0 的人身高为 5 ，没有身高更高或者相同的人排在他前面。编号为 1 的人身高为 7 ，没有身高更高或者相同的人排在他前面。编号为 2 的人身高为 5 ，有 2 个身高更高或者相同的人排在他前面，即编号为 0 和 1 的人。编号为 3 的人身高为 6 ，有 1 个身高更高或者相同的人排在他前面，即编号为 1 的人。编号为 4 的人身高为 4 ，有 4 个身高更高或者相同的人排在他前面，即编号为 0、1、2、3 的人。编号为 5 的人身高为 7 ，有 1 个身高更高或者相同的人排在他前面，即编号为 1 的人。因此 [[5,0],[7,0],[5,2],[6,1],[4,4],[7,1]] 是重新构造后的队列。

示例 2：
输入：people = [[6,0],[5,0],[4,0],[3,2],[2,2],[1,4]]
输出：[[4,0],[5,0],[2,2],[3,2],[1,4],[6,0]]

#### 题解

```js
var reconstructQueue = function (people) {
  let queue = [];

  people.sort((a, b) => {
    if (b[0] !== a[0]) return b[0] - a[0];
    else return a[1] - b[1];
  });
  for (let i = 0; i < people.length; i++) {
    queue.splice(people[i][1], 0, people[i]);
  }
  return queue;
};
```

## 动态规划

解题步骤

1.确定 dp 数组（dp table）以及下标的含义

2.确定递推公式

3.dp 数组如何初始化

4.确定遍历顺序

5.举例推导 dp 数组

### 509. 斐波那契数

斐波那契数 （通常用 F(n) 表示）形成的序列称为 斐波那契数列 。该数列由 0 和 1 开始，后面的每一项数字都是前面两项数字的和。也就是：
F(0) = 0，F(1) = 1
F(n) = F(n - 1) + F(n - 2)，其中 n > 1
给定 n ，请计算 F(n) 。

示例 1：
输入：n = 2 输出：1 解释：F(2) = F(1) + F(0) = 1 + 0 = 1

示例 2：
输入：n = 3 输出：2 解释：F(3) = F(2) + F(1) = 1 + 1 = 2

示例 3：
输入：n = 4 输出：3 解释：F(4) = F(3) + F(2) = 2 + 1 = 3

#### 题解

```js
// 动态规划
function fib(n: number): number {
  const dp: number[] = [0, 1];

  for (let i = 2; i <= n; i++) {
    dp[i] = dp[i - 1] + dp[i - 2];
  }
  return dp[n];
}

// 递归
function fib(n: number): number {
  if (n < 2) return n;
  return fib(n - 1) + fib(n - 2);
}
```

### 70. 爬楼梯

假设你正在爬楼梯。需要 n 阶你才能到达楼顶。
每次你可以爬 1 或 2 个台阶。你有多少种不同的方法可以爬到楼顶呢？

示例 1：
输入：n = 2 输出：2 解释：有两种方法可以爬到楼顶。1. 1 阶 + 1 阶 2. 2 阶

示例 2：
输入：n = 3 输出：3 解释：有三种方法可以爬到楼顶。1. 1 阶 + 1 阶 + 1 阶 2. 1 阶 + 2 阶 3. 2 阶 + 1 阶

#### 题解

```js
function climbStairs(n: number): number {
  let dp: number[] = [1, 2];

  for (let i = 2; i < n; i++) {
    dp[i] = dp[i - 1] + dp[i - 2];
  }
  return dp[n - 1];
}
```

### 746. 使用最小花费爬楼梯

给你一个整数数组 cost ，其中 cost[i] 是从楼梯第 i 个台阶向上爬需要支付的费用。一旦你支付此费用，即可选择向上爬一个或者两个台阶。
你可以选择从下标为 0 或下标为 1 的台阶开始爬楼梯。
请你计算并返回达到楼梯顶部的最低花费。

示例 1：
输入：cost = [10,15,20]输出：15 解释：你将从下标为 1 的台阶开始。- 支付 15 ，向上爬两个台阶，到达楼梯顶部。总花费为 15 。

示例 2：
输入：cost = [1,100,1,1,1,100,1,1,100,1]输出：6 解释：你将从下标为 0 的台阶开始。- 支付 1 ，向上爬两个台阶，到达下标为 2 的台阶。- 支付 1 ，向上爬两个台阶，到达下标为 4 的台阶。- 支付 1 ，向上爬两个台阶，到达下标为 6 的台阶。- 支付 1 ，向上爬一个台阶，到达下标为 7 的台阶。- 支付 1 ，向上爬两个台阶，到达下标为 9 的台阶。- 支付 1 ，向上爬一个台阶，到达楼梯顶部。总花费为 6 。

#### 题解

```js
function minCostClimbingStairs(cost: number[]): number {
  const dp = [0, 0];
  for (let i = 2; i <= cost.length; i++) {
    dp[i] = Math.min(cost[i - 1] + dp[i - 1], cost[i - 2] + dp[i - 2]);
  }
  return dp[cost.length];
}
```

### 62. 不同路径

一个机器人位于一个 m x n 网格的左上角 （起始点在下图中标记为 “Start” ）。
机器人每次只能向下或者向右移动一步。机器人试图达到网格的右下角（在下图中标记为 “Finish” ）。
问总共有多少条不同的路径？

示例 1：
输入：m = 3, n = 7 输出：28

示例 2：
输入：m = 3, n = 2 输出：3 解释：从左上角开始，总共有 3 条路径可以到达右下角。1. 向右 -> 向下 -> 向下 2. 向下 -> 向下 -> 向右 3. 向下 -> 向右 -> 向下

示例 3：
输入：m = 7, n = 3 输出：28

示例 4：
输入：m = 3, n = 3 输出：6

#### 题解

```js
function uniquePaths(m: number, n: number): number {
const dp = Array(m).fill(0).map(\_ => [])
for (let i = 0; i < m; i++) {
dp[i][0] = 1
}

    for (let i = 0; i < n; i++) {
        dp[0][i] = 1
    }

    for (let i = 1; i < m; i++) {
        for (let j = 1; j < n; j++) {
            dp[i][j] = dp[i - 1][j] + dp[i][j - 1]
        }
    }
    return dp[m - 1][n - 1]

};
```

### 63. 不同路径 II

一个机器人位于一个 m x n 网格的左上角 （起始点在下图中标记为 “Start” ）。
机器人每次只能向下或者向右移动一步。机器人试图达到网格的右下角（在下图中标记为 “Finish”）。
现在考虑网格中有障碍物。那么从左上角到右下角将会有多少条不同的路径？
网格中的障碍物和空位置分别用 1 和 0 来表示。

示例 1：
输入：obstacleGrid = [[0,0,0],[0,1,0],[0,0,0]]
输出：2
解释：3x3 网格的正中间有一个障碍物。
从左上角到右下角一共有 2 条不同的路径：

1. 向右 -> 向右 -> 向下 -> 向下
2. 向下 -> 向下 -> 向右 -> 向右

示例 2：
输入：obstacleGrid = [[0,1],[0,0]]输出：1

#### 题解

```js
function uniquePathsWithObstacles(obstacleGrid: number[][]): number {
  let rowLen = obstacleGrid[0].length,
    colLen = obstacleGrid.length;
  for (let i = 0; i < rowLen; i++) {
    for (let j = 0; j < colLen; j++) {
      if (obstacleGrid[j][i] === 0) {
        if (j == 0) {
          obstacleGrid[j][i] = obstacleGrid[j][i - 1] ?? 1;
        } else if (i === 0) {
          obstacleGrid[j][i] = obstacleGrid[j - 1]?.[i] ?? 1;
        } else
          obstacleGrid[j][i] = obstacleGrid[j - 1][i] + obstacleGrid[j][i - 1];
      } else {
        obstacleGrid[j][i] = 0;
      }
    }
  }
  return obstacleGrid[colLen - 1][rowLen - 1];
}
```

### 343. 整数拆分

给定一个正整数 n ，将其拆分为 k 个 正整数 的和（ k >= 2 ），并使这些整数的乘积最大化。
返回 你可以获得的最大乘积 。
示例 1:
输入: n = 2 输出: 1 解释: 2 = 1 + 1, 1 × 1 = 1。

示例 2:
输入: n = 10 输出: 36 解释: 10 = 3 + 3 + 4, 3 × 3 × 4 = 36。

#### 题解

new Array(n+1)：索引为 n 长度为 n+1

```js
function integerBreak(n: number): number {
  const dp: number[] = new Array(n + 1).fill(0);
  dp[2] = 1;

  for (let i = 1; i <= n; i++) {
    // j <= i / 2：拆分一个数n 使之乘积最大，一定是拆分成m个近似相同的子数相乘才是最大的
    for (let j = 1; j <= i / 2; j++) {
      // (i - j) * j 直接相乘可以获得dp[i];
      // dp[i - j] * j=>继续拆分dp[i - j]，即拆分成两个及两个以上的数相乘
      dp[i] = Math.max(dp[i], Math.max(dp[i - j] * j, (i - j) * j));
    }
  }
  return dp[n];
}
```

### 96. 不同的二叉搜索树

给你一个整数 n ，求恰由 n 个节点组成且节点值从 1 到 n 互不相同的 二叉搜索树 有多少种？返回满足题意的二叉搜索树的种数。

示例 1：
输入：n = 3 输出：5

示例 2：
输入：n = 1 输出：1

#### 题解

```js
function numTrees(n: number): number {
  let dp = new Array(n + 1).fill(0);
  dp[0] = 1;
  dp[1] = 1;

  for (let i = 2; i <= n; i++) {
    for (let j = 1; j <= i; j++) {
      dp[i] += dp[j - 1] * dp[i - j];
    }
  }
  return dp[n];
}
```

## 背包理论

举例：

dp[i][j] 表示从下标为[0-i]的物品里任意取，放进容量为 j 的背包，价值总和最大是多少。
推导 dp[i][j]的值

二维数组版本：

```js
function testWeightBagProblem(weight, value, size) {
  // 定义 dp 数组
  const len = weight.length,
    dp = Array(len)
      .fill()
      .map(() => Array(size + 1).fill(0));

  // 初始化
  for (let j = weight[0]; j <= size; j++) {
    dp[0][j] = value[0];
  }

  // weight 数组的长度len 就是物品个数
  for (let i = 1; i < len; i++) {
    // 遍历物品
    for (let j = 0; j <= size; j++) {
      // 遍历背包容量
      if (j < weight[i]) dp[i][j] = dp[i - 1][j];
      else
        dp[i][j] = Math.max(dp[i - 1][j], dp[i - 1][j - weight[i]] + value[i]);
    }
  }
  return dp[len - 1][size];
}

function test() {
  console.log(testWeightBagProblem([1, 3, 4, 5], [15, 20, 30, 55], 6));
}

test();
```

一维数组版本：

```js
function testWeightBagProblem(wight, value, size) {
  const len = wight.length,
    dp = Array(size + 1).fill(0);
  for (let i = 1; i <= len; i++) {
    for (let j = size; j >= wight[i - 1]; j--) {
      dp[j] = Math.max(dp[j], value[i - 1] + dp[j - wight[i - 1]]);
    }
  }
  return dp[size];
}

function test() {
  console.log(testWeightBagProblem([1, 3, 4, 5], [15, 20, 30, 55], 6));
}

test();
```

### 416. 分割等和子集

给你一个 只包含正整数 的 非空 数组 nums 。请你判断是否可以将这个数组分割成两个子集，使得两个子集的元素和相等。

示例 1：
输入：nums = [1,5,11,5]输出：true 解释：数组可以分割成 [1, 5, 5] 和 [11] 。

示例 2：
输入：nums = [1,2,3,5]输出：false 解释：数组不能分割成两个元素和相等的子集。

```js
function canPartition(nums: number[]): boolean {
  const sum = nums.reduce((prev, current) => prev + current);
  if (sum % 2 === 1) return false;
  const dp = new Array(sum / 2 + 1).fill(0);
  // dp[j]: 容量为 j 的背包，所背的物品价值可以最大为 dp[j]

  for (let i = 0; i < nums.length; i++) {
    // 倒序遍历
    for (let j = sum / 2; j >= nums[i]; j--) {
      dp[j] = Math.max(dp[j], dp[j - nums[i]] + nums[i]);
      if (dp[j] === sum / 2) return true;
    }
  }
  return dp[sum / 2] === sum / 2;
}
```
