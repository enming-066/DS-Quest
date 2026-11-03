---
id: summary
title: 本章总复习：一张表 + 八个套路
summary: 把线性表的所有考点压缩成一张速查表和八个代码套路，考前翻这一页。
minutes: 10
tags: 复习, 复杂度, 套路
exam: 复杂度对比, 逆置, 快慢指针, 有序合并
group: 复习
---

## 复杂度速查表

| 操作 | 顺序表 | 单链表 | 备注 |
| --- | --- | --- | --- |
| 按位查找 | O(1) | O(n) | 顺序表的核心优势 |
| 按值查找 | O(n) | O(n) | 都要扫 |
| 插入（已知位置） | O(n) | O(1) | 链表只改指针，但"找位置"仍是 O(n) |
| 删除（已知位置） | O(n) | O(1) | 同上 |
| 长度 | O(1) | O(n)（不存长度时） | 链表可加 length 字段优化 |
| 存储密度 | 1 | < 1 | 链表每个结点多一个指针 |

:::exam 一句话必背
顺序表：**随机访问快，插入删除慢**；链表：**插入删除快，随机访问慢**。
插入平均移动 `n/2`，删除平均移动 `(n-1)/2`。
:::

## 八个必须会的套路

### 1. 就地逆置（不新建结点）

```cpp
void Reverse(LinkList L) {
    LNode *p = L->next, *q;
    L->next = NULL;              // 头结点断链，成为新表的头
    while (p != NULL) {
        q = p->next;             // 先记住后继
        p->next = L->next;       // 头插
        L->next = p;
        p = q;                   // 往后走
    }
}
```

核心：**头插法天然逆序**。把每个结点摘下来，插到新表头，顺序自然就反了。

### 2. 找中间结点（快慢指针）

```cpp
LNode *FindMid(LinkList L) {
    LNode *slow = L->next, *fast = L->next;
    while (fast != NULL && fast->next != NULL) {
        slow = slow->next;          // 一次 1 步
        fast = fast->next->next;    // 一次 2 步
    }
    return slow;                    // 偶数个结点时返回中间偏右那个
}
```

### 3. 判断有环（Floyd 判圈）

```cpp
bool HasCycle(LinkList L) {
    LNode *slow = L, *fast = L;
    while (fast != NULL && fast->next != NULL) {
        slow = slow->next;
        fast = fast->next->next;
        if (slow == fast) return true;   // 相遇即有环
    }
    return false;
}
```

### 4. 合并两个有序链表

```cpp
LinkList Merge(LinkList A, LinkList B) {
    LNode *p = A->next, *q = B->next;
    LNode *r = A;                  // 复用 A 的头结点当结果表头
    while (p != NULL && q != NULL) {
        if (p->data <= q->data) { r->next = p; r = p; p = p->next; }
        else                    { r->next = q; r = q; q = q->next; }
    }
    r->next = (p != NULL) ? p : q; // 把剩下的整段接上
    delete B;                      // B 的头结点不要了
    return A;
}
```

### 5. 删除所有值为 x 的结点

关键是**用前驱 `pre` 的视角**，这样删头结点后的第一个也不用特判。

```cpp
void DeleteX(LinkList L, int x) {
    LNode *pre = L, *p = L->next;
    while (p != NULL) {
        if (p->data == x) {
            pre->next = p->next;
            delete p;
            p = pre->next;
        } else {
            pre = p;
            p = p->next;
        }
    }
}
```

### 6. 删除倒数第 k 个结点

快指针先走 k 步，然后快慢一起走，快到头时慢指针正好在倒数第 k+1 个（即待删结点的前驱）。

### 7. 两个链表求交集 / 差集

双指针 + 归并思想，边比较边摘结点。

### 8. 判断两个链表是否相交

先求长度差，长的先走差值步，然后一起走，相遇即相交。注意比的是**结点地址**不是 `data`。

## 期末复习清单

- [ ] 能默写顺序表的插入、删除，并说清指针移动方向和平均移动次数。
- [ ] 能说清带头结点/不带头结点的空表判断和插入差异。
- [ ] 能手写头插法、尾插法建表。
- [ ] 能手写就地逆置、有序合并、删除指定值。
- [ ] 能说出循环链表、双向链表的判空条件和插入删除的指针顺序。
- [ ] 看到一道题能立刻判断"该用顺序表还是链表"。

这些都过了，线性表这一关就算通关。
