---
id: link-stack
title: 链栈：用链表实现栈
summary: 为什么链栈一般不让头结点当栈底，入栈出栈就是头插和删头。
minutes: 10
tags: 链栈, 头插法, 栈顶
exam: 链栈的栈顶位置, 链栈的判空条件
group: 栈
---

## 结构

链栈通常**把栈顶放在链表头部**，因为单链表在头部插入/删除是 O(1)，放到尾部反而要 O(n)。

```cpp
typedef struct StackNode {
    int data;
    struct StackNode *next;
} StackNode, *LinkStack;
```

```
top → [30|●] → [20|●] → [10|^]
      栈顶                栈底
```

- `top` 直接指向栈顶结点（**通常不带头结点**）。
- 入栈 = 头插，出栈 = 删除第一个结点。
- 判空：`top == NULL`。
- 由于没有头结点，就不存在"头结点算不算栈元素"的歧义。

## 代码

```cpp
bool InitStack(LinkStack &S) {
    S = NULL;              // 空栈
    return true;
}

bool StackEmpty(LinkStack S) {
    return S == NULL;
}

// 入栈：头插法
bool Push(LinkStack &S, int e) {
    StackNode *s = new StackNode;
    if (s == NULL) return false;   // 内存耗尽
    s->data = e;
    s->next = S;
    S = s;                         // 栈顶移到新结点
    return true;
}

// 出栈：删除栈顶结点
bool Pop(LinkStack &S, int &e) {
    if (S == NULL) return false;
    StackNode *p = S;
    e = p->data;
    S = S->next;                   // 栈顶下移
    delete p;
    return true;
}

bool GetTop(LinkStack S, int &e) {
    if (S == NULL) return false;
    e = S->data;
    return true;
}
```

:::warning 注意
链栈**不需要判满**——只要内存还有，就能一直 push。这是它相比顺序栈最大的优势（没有上溢）。代价是每个结点多一个指针，而且每次操作都要 new/delete，常数更大。
:::

## 顺序栈 vs 链栈

| | 顺序栈 | 链栈 |
| --- | --- | --- |
| 存储 | 连续数组 | 分散结点 |
| 判满 | 需要（上溢） | 不需要 |
| 容量 | 固定，可能浪费或不够 | 按需增长 |
| 每元素开销 | 小 | 多一个指针 |
| 栈顶位置 | 数组尾部（通常） | 链表头部 |
| 适用 | 元素个数可预估 | 个数变化大 |

## 一个小陷阱：如果用带头结点的链表

有的教材写链栈时仍然带一个头结点，这时：

- 判空：`S->next == NULL`
- 栈顶是 `S->next` 而不是 `S`

考试如果给了图，一定要看清 `top` 指的位置。**图里 top 指的那个结点存不存数据，决定了它带不带头结点。**
