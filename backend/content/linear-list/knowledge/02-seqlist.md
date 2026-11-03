---
id: seqlist
title: 顺序表：数组描述的增删改查
summary: 课件里的 ArrayLinearList——get/indexOf/insert/erase 各自多快，为什么插入要从后往前挪。
minutes: 18
tags: 顺序表, 插入, 删除, 复杂度
exam: 插入删除的元素移动次数, 平均复杂度推导, 下标语义
group: 基础
---

## 存储方式：连续存放 + 一个表长

课件第 1 章 P12 的原话是：**把线性表的元素按逻辑顺序依次存放在数组的连续单元内，再用一个整型量表示最后一个元素所在单元的下标，即表长。**

```
下标:  0    1    2    3    4   ...  max-1
      [a1] [a2] [a3] [ ] [ ]       [ ]
                  ↑
              listSize = 3（或 last = 2）
```

因为地址连续，第 i 个元素的地址可以直接算出来，不用一个一个找：

```
LOC(a_i) = LOC(a_1) + (i - 1) * sizeof(T)
```

这就是课本说的**随机存取结构**——给定下标，Θ(1) 拿到元素。

## 课件里的五个操作，各自多快

| 操作 | 含义 | 时间复杂度 |
| --- | --- | --- |
| `empty()` | 表是否为空 | Θ(1) |
| `size()` | 元素个数 | Θ(1) |
| `get(k)` | 返回下标为 k 的元素 | Θ(1) |
| `indexOf(x)` | 返回 x 第一次出现的下标，没有返回 -1 | 最好 Θ(1)，最坏/平均 Θ(n) |
| `erase(k)` | 删除下标为 k 的元素 | 最好 Θ(1)，最坏/平均 Θ(n) |
| `insert(k, x)` | 把 x 插到下标 k 的位置 | 最好 Θ(1)，最坏/平均 Θ(n) |

:::exam 下标语义（最容易搞错）
课件的 `insert(theIndex, x)` 意思是：**插入之后，x 的下标就是 theIndex**。
所以 `insert(2, 99)` 会把原来的 a2、a3… 整体后移一格。

合法范围：`insert` 是 `[0, listSize]`（可以插到末尾之后），`erase` 是 `[0, listSize-1]`。
**插入比删除多一个位置**，选择题常考这个"差一"。
:::

## insert：为什么必须从后往前挪

要把下标 `theIndex` 空出来，`theIndex` 及其后面的元素整体后移一格：

```
插入前：  10  20  30  40  50
insert(2, 99)
从最后往前挪：
         10  20  30  40  [50] → 10 20 30 40 50 50
         10  20  30  [40] 50 → 10 20 30 40 40 50
         10  20  [30] 40  50 → 10 20 30 30 40 50
放入 99： 10  20  99  30  40  50
```

```cpp
void insert(int theIndex, const T& theElement) {
    if (theIndex < 0 || theIndex > listSize) return;   // 越界
    if (listSize == arrayLength) {                     // 满了，容量翻倍
        changeLength1D(element, arrayLength, 2 * arrayLength);
        arrayLength *= 2;
    }
    for (int i = listSize - 1; i >= theIndex; i--)     // 从后往前
        element[i + 1] = element[i];
    element[theIndex] = theElement;
    listSize++;
}
```

**如果从前往后挪**，`element[theIndex]` 会先被前一个元素覆盖，后面的值全错。这是笔试最爱考的细节。

### 平均要移动多少个元素？

在长度为 n 的表里，`insert(i, x)` 要移动 `n - i` 个元素。

假设每个位置插入概率相同（共 `n+1` 个位置，每个概率 `1/(n+1)`）：

```
E = (1/(n+1)) · Σ(n - i)     (i = 0..n)
  = (1/(n+1)) · (n + (n-1) + ... + 1 + 0)
  = (1/(n+1)) · n(n+1)/2
  = n/2
```

**结论：平均移动 n/2 个，Θ(n)。** 插在末尾不用挪，是 Θ(1)。

## erase：从前往后

```cpp
void erase(int theIndex) {
    for (int i = theIndex; i < listSize - 1; i++)
        element[i] = element[i + 1];    // 后一个盖到前一个
    listSize--;
}
```

删除下标 i 的元素要移动 `n-1-i` 个，平均 `(n-1)/2` 个，仍然是 Θ(n)。

:::exam 必背的两个数字
- 插入：平均移动 **n/2** 个元素
- 删除：平均移动 **(n-1)/2** 个元素

这两个数字在填空题里几乎年年出现，注意删除时分子是 n-1。
:::

## 数组长度加倍（扩容）

`insert` 时如果 `listSize == arrayLength`，就要申请一个两倍大的新数组，把旧数据搬过去，再释放旧数组：

```cpp
void changeLength1D(T*& a, int oldLength, int newLength) {
    T* temp = new T[newLength];
    int number = oldLength < newLength ? oldLength : newLength;
    for (int i = 0; i < number; i++) temp[i] = a[i];
    delete[] a;
    a = temp;
}
```

单次扩容是 Θ(n)，但每次扩容后容量翻倍，n 次插入总共只扩容 log n 次，
**摊还（amortized）到每次插入上是 Θ(1)**。这是"动态数组"能用的根本原因。

## 顺序表的优缺点

**优点**

- 支持随机存取，`get` 是 Θ(1)。
- 存储密度高，没有额外指针。
- 内存连续，CPU 缓存友好。

**缺点**

- 插入删除要移动元素，Θ(n)。
- 数组长度固定，扩容要整体复制。
- 中间删除会留下"空洞"，内存利用率下降。

:::pitfall 四个高频错误
1. 插入范围写成 `[0, listSize-1]`，少了"插到末尾之后"这一个位置。
2. 插入从前往后挪（应该是从后往前）；删除从后往前挪（应该是从前往后）。
3. 扩容后忘了 `delete[]` 旧数组。
4. 忘了维护 `listSize`。
:::
