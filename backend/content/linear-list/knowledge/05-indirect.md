---
id: indirect
title: 间接寻址：数组的目录 + 链表的灵活
summary: 元素分散存放，指针集中在数组里。定位 Θ(1)，插入删除只挪指针不挪元素。
minutes: 12
tags: 间接寻址, 指针数组, 复杂度
exam: 三种存储方式的对比, 间接寻址的复杂度, 适用场景
group: 进阶
---

## 为什么要多这一层

数组描述的两个毛病：**长度固定**、**插入删除要搬元素**。
链式描述解决了这两点，却丢了"按下标随机访问"。

间接寻址想同时要两边的好处：

```
table（目录，连续）       元素（分散在堆上）
[0] ───────────────→   [10]
[1] ───────────────→   [20]
[2] ───────────────→   [30]
```

- 元素本身用 `new` 动态分配，像链表一样不连续、可随时增删；
- 但**指向元素的指针集中放在一个数组里**，像目录一样连续。
- 要找第 k 个元素：先查 `table[k-1]`（一次数组寻址），再解引用（一次间接）——**Θ(1)**。

课件 P44 的比喻很准：**链表是超链接，间接寻址是目录索引。**

## 类定义

```cpp
template<class T>
class IndirectList {
public:
    IndirectList(int MaxListSize = 10);
    ~IndirectList();
    bool IsEmpty() const { return length == 0; }
    int Length() const { return length; }
    bool Find(int k, T& x) const;      // 取第 k 个（k 从 1 开始）
    int Search(const T& x) const;      // 按值查
    bool Delete(int k, T& x);
    bool Insert(int k, const T& x);
private:
    T** table;      // 指针数组（目录）
    int length;     // 元素个数
    int MaxSize;    // 目录容量
};
```

注意 `T** table` 是**指针的数组**，不是元素的数组。这是和顺序表最根本的区别。

## 三个关键操作

### 定位：Θ(1)

```cpp
bool Find(int k, T& x) const {
    if (k < 1 || k > length) return false;
    x = *table[k - 1];        // 一次寻址 + 一次解引用
    return true;
}
```

和数组描述一样快，因为目录本身是连续数组。

### 删除：只挪指针

```cpp
bool Delete(int k, T& x) {
    if (!Find(k, x)) return false;
    delete table[k - 1];                    // 释放元素本身
    for (int i = k; i < length; i++)
        table[i - 1] = table[i];            // 指针前移，元素不动
    length--;
    return true;
}
```

复杂度 **Θ(length - k)**，但每次移动的是一个指针（4/8 字节），而不是一个可能很大的元素对象。
元素越大，间接寻址越划算。

### 插入：同样只挪指针

```cpp
bool Insert(int k, const T& x) {
    if (k < 0 || k > length) return false;
    if (length == MaxSize) return false;
    for (int i = length - 1; i >= k; i--)
        table[i + 1] = table[i];            // 指针后移
    table[k] = new T(x);
    length++;
    return true;
}
```

## 三种方式放在一起对比（课件 P49、P51）

| | 数组描述 | 链式描述 | 间接寻址 |
| --- | --- | --- | --- |
| 定位 `get(k)` | Θ(1) | Θ(k) | **Θ(1)** |
| 删除 | Θ(n)（搬元素） | Θ(k)（找前驱） | Θ(n-k)（搬指针） |
| 插入 | Θ(n)（搬元素） | Θ(k)（找位置） | Θ(n-k)（搬指针） |
| 空间 | 预分配、可能浪费 | 每个结点多一个指针 | 目录 + 每个元素一个指针 |
| 适用 | 查多改少、元素小 | 频繁增删、元素大 | 元素大、又要按下标访问 |

:::exam 一句话总结
**间接寻址 = 用"指针数组"换"元素不搬家"。**
它没有解决"目录数组本身要挪"的问题（所以插入删除还是 Θ(n-k)），但把搬运的成本从"整个元素"降到了"一个指针"。
:::

:::pitfall 三个易错点
1. 析构时忘了 `delete[] table`，或者忘了逐个 `delete table[i]`。
2. 把 `table[i]` 当元素用（它是指针，取值要 `*table[i]`）。
3. 课本的 `k` 是 **1 基**（第 k 个），而 `insert/delete` 的语义是"第 k 个之后"，和数组描述的 0 基下标不同，做题时看清是哪种。
:::
