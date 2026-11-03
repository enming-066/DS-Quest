---
id: summary
title: 本章总复习：一张表 + 四个大题套路
summary: 三种存储方式的复杂度对比、必背结论，以及期末最爱考的四道链表大题。
minutes: 12
tags: 复习, 复杂度, 逆置, 快慢指针
exam: 三种存储对比, 逆置, 快慢指针, 有序合并
group: 复习
---

## 三种存储方式对比（课件的核心结论）

| 操作 | 数组描述 | 链式描述 | 间接寻址 |
| --- | --- | --- | --- |
| `get(k)` 定位 | Θ(1) | Θ(k) | Θ(1) |
| `indexOf(x)` 按值查 | Θ(n) | Θ(n) | Θ(n) |
| `erase(k)` 删除 | Θ(n)（搬元素） | Θ(k)（找前驱） | Θ(n-k)（搬指针） |
| `insert(k,x)` 插入 | Θ(n)（搬元素） | Θ(k)（找位置） | Θ(n-k)（搬指针） |
| 空间分配 | 预分配、连续 | 按需、分散 | 目录连续 + 元素分散 |
| 每元素额外开销 | 无 | 一个指针 | 一个指针 |

:::exam 三句话必背
1. **数组**：定位 Θ(1)，插入删除 Θ(n)——瓶颈是"搬元素"。
2. **链表**：定位 Θ(k)，插入删除 Θ(k)——瓶颈是"找位置"，找到之后只改指针。
3. **间接寻址**：定位 Θ(1)，插入删除 Θ(n-k)——但搬的是指针不是元素，元素越大越划算。
:::

## 本章必背的数字

- 顺序表插入：平均移动 **n/2** 个元素；删除：平均移动 **(n-1)/2** 个。
- 顺序表插入合法下标 `[0, n]`，删除合法下标 `[0, n-1]`——差一个。
- 链表 `get(k)` 走 **k** 步（从 firstNode 出发）。
- 链表删除要**先找前驱**，走 `k-1` 步；双向链表已知结点时删除是 **Θ(1)**。
- 约瑟夫环用循环链表，O(m·n)。
- 单链表析构必须**逐个结点 delete**，数组只需 `delete[]`。

## 四个期末大题套路

> 这四个是超出课件、但期末和考研反复考的题型。统一用课件的 `ChainNode<T>` 风格写。

### 1. 就地逆置（不新建结点）

```cpp
template<class T>
void reverse(Chain<T>& L) {          // 假设能访问 firstNode
    ChainNode<T>* p = L.firstNode;
    ChainNode<T>* q = 0;
    L.firstNode = 0;                 // 头指针清空，成为新表的头
    while (p != 0) {
        q = p->next;                 // ① 先记住后继
        p->next = L.firstNode;       // ② 头插到新表
        L.firstNode = p;             // ③ 更新新表头
        p = q;                       // ④ 继续
    }
}
```

核心：**头插法天然逆序**。四步顺序不能换，尤其是 ① 必须在 ② 之前。

### 2. 快慢指针找中间结点

```cpp
ChainNode<T>* slow = firstNode;
ChainNode<T>* fast = firstNode;
while (fast != 0 && fast->next != 0) {
    slow = slow->next;               // 一次一步
    fast = fast->next->next;         // 一次两步
}
// 偶数个结点时 slow 停在中间偏右那个
```

用途：找中点、判断有环（相遇即有环）、找倒数第 k 个（快指针先走 k 步）。

### 3. 合并两个有序链表

```cpp
// 用哨兵结点省掉"结果表为空"的特判
ChainNode<T> dummy(0);
ChainNode<T>* r = &dummy;
while (a != 0 && b != 0) {
    if (a->data <= b->data) { r->next = a; r = a; a = a->next; }
    else                    { r->next = b; r = b; b = b->next; }
}
r->next = (a != 0) ? a : b;          // 剩下的一段直接接上
```

### 4. 删除所有值为 x 的结点

```cpp
ChainNode<T>* pre = 0;
ChainNode<T>* p = firstNode;
while (p != 0) {
    if (p->data == x) {
        ChainNode<T>* victim = p;
        if (pre == 0) firstNode = p->next;   // 删的是首结点
        else pre->next = p->next;
        p = p->next;
        delete victim;
        listSize--;
    } else {
        pre = p;
        p = p->next;
    }
}
```

要点：**盯住前驱**，删完不要立刻用 `p->next`（那块内存已经释放了）。

## 期末复习清单

- [ ] 能默写顺序表的 insert / erase，并说清 for 的方向为什么不同。
- [ ] 能推导插入平均移动 n/2、删除平均移动 (n-1)/2。
- [ ] 能默写 Chain 的 get / insert / erase / 析构。
- [ ] 能说清"已知结点指针时，单链表删除为什么仍是 Θ(n)"。
- [ ] 能写出循环链表的尾指针表示，并算出约瑟夫环 O(mn)。
- [ ] 能说出双向链表插入要改哪四个指针、顺序为什么不能乱。
- [ ] 能说出间接寻址相比数组/链表各解决了什么问题。
- [ ] 能手写就地逆置、快慢指针、有序合并、删除指定值。

这八条都会了，线性表这一关就稳了。
