---
id: linkedlist
title: 单链表：指针到底怎么改
summary: 用"头结点 + 指针操作"把插入、删除讲透，附带指针顺序的常见坑。
minutes: 20
tags: 单链表, 指针, 头结点, 插入, 删除
exam: 带头结点与不带头结点的区别, 插入删除的指针赋值顺序, 头插法与尾插法
group: 基础
---

## 存储方式：每个结点自己带"下一站地址"

顺序表是一条连续的大街，单链表则是一串**分散的房子**，每个房子里放两样东西：数据、以及下一间房子的门牌号。

```cpp
typedef struct LNode {
    int data;            // 数据域
    struct LNode *next;  // 指针域：指向下一个结点
} LNode, *LinkList;
```

- `LNode` 强调这是一个**结点**。
- `LinkList` 强调这是一个**指向结点的指针**，通常用来表示整张表（"表头指针"）。
- 两者本质一样，只是语义不同，考试里两个名字都要认识。

```
head → [d1|●] → [d2|●] → [d3|^]
                      最后一个结点的 next 是 NULL
```

## 头结点：一个"假的第一间房子"

考试里 `LinkList L` 有的带头结点，有的不带头。区别是：

| | 带头结点 | 不带头结点 |
| --- | --- | --- |
| 第一个结点 | 头结点（数据域没用或存表长） | 首元结点（存真数据） |
| 空表判断 | `L->next == NULL` | `L == NULL` |
| 在第 1 个位置插入 | 和别的位置写法一样 | 要单独改 `L` |
| 代码难度 | 低，操作统一 | 高，处处要特判 |

:::tip 结论
**做题、写实验代码一律用带头结点**。它把"插在第一个"和"插在中间"统一成同一种操作，少写一堆 if。只有在考试题目明确要求"不带头结点"时，才需要特判。
:::

## 初始化

```cpp
// 带头结点：L 指向一个不存数据的头结点
bool InitList(LinkList &L) {
    L = new LNode;
    if (L == NULL) return false;   // 内存分配失败
    L->next = NULL;
    return true;
}
```

C 语言里对应 `L = (LNode *)malloc(sizeof(LNode));`。

## 插入：先接后断

在结点 `p` **之后**插入新结点 `s`：

```cpp
s->next = p->next;   // ① 新结点先接上后面的链子
p->next = s;         // ② 再让 p 指向 s
```

**顺序不能反**。如果先写 `p->next = s;`，那 `p->next` 原来指向的那个结点地址就丢了，后面的整条链子直接断掉，程序很可能崩溃。

```
正确：  p → [ ] → [X]        s → [e|→X]
        ① s->next = p->next
        ② p->next = s

错误：  先 p->next = s，原有的 X 就再也找不到了
```

在某个位序 `i` 插入（带头结点）：

```cpp
bool ListInsert(LinkList &L, int i, int e) {
    LNode *p = L;                 // p 从头结点开始
    int j = 0;                    // j 记录 p 当前是第几个结点（头结点算 0）
    while (p != NULL && j < i - 1) {  // 找第 i-1 个结点
        p = p->next;
        j++;
    }
    if (p == NULL) return false;  // i 太大
    LNode *s = new LNode;
    s->data = e;
    s->next = p->next;
    p->next = s;
    return true;
}
```

注意找的是**第 i-1 个结点**，因为单链表只能"站在前驱上往后插"，看不到前一个结点就无法修改它的 `next`。

## 删除：先记后断，别忘 free

删除 `p` 之后的结点：

```cpp
if (p->next == NULL) return false;   // 后面没有结点
LNode *q = p->next;                  // ① 记住要删的结点
p->next = q->next;                   // ② 把链子接过去
delete q;                            // ③ 释放内存
```

```cpp
bool ListDelete(LinkList &L, int i, int &e) {
    LNode *p = L;
    int j = 0;
    while (p != NULL && j < i - 1) { p = p->next; j++; }
    if (p == NULL || p->next == NULL) return false;
    LNode *q = p->next;
    e = q->data;
    p->next = q->next;
    delete q;
    return true;
}
```

:::warning 三个必须记住的点
1. **删除必须释放内存**（`delete` / `free`），否则内存泄漏。顺序表不需要，这是链表独有的。
2. **删除前必须先保存 `q`**，否则 `p->next` 一改，那个结点就成孤儿，既删不掉也找不回。
3. **删除第一个结点不需要特判**（带头结点时），因为它前面就是头结点。
:::

## 建表：头插法 vs 尾插法

**头插法**：每次插到头结点后面。特点是**输入顺序和链表顺序相反**，常用于"链表逆置"。

```cpp
void CreateListHead(LinkList &L, int a[], int n) {
    L = new LNode; L->next = NULL;        // 头结点
    for (int i = 0; i < n; i++) {
        LNode *s = new LNode;
        s->data = a[i];
        s->next = L->next;   // 新结点接在头结点原来的后面
        L->next = s;         // 头结点指向新结点
    }
}
// 输入 1 2 3 4 5 → 链表 5 4 3 2 1
```

**尾插法**：维护一个 `r` 指针始终指向表尾。特点是**保持输入顺序**，最常用。

```cpp
void CreateListTail(LinkList &L, int a[], int n) {
    L = new LNode; L->next = NULL;
    LNode *r = L;                         // r 是尾指针
    for (int i = 0; i < n; i++) {
        LNode *s = new LNode;
        s->data = a[i];
        r->next = s;
        r = s;                            // 尾指针后移
    }
    r->next = NULL;                       // 收尾，千万别忘
}
```

:::exam 常考
"用头插法建立链表，输入 `1 2 3`，输出是什么？" 答：`3 2 1`。
"尾插法建表，输入 `1 2 3`，输出是什么？" 答：`1 2 3`。
这题每年都有人错，画一下图就不会混。
:::

## 单链表 vs 顺序表：什么时候选谁

| 场景 | 选它 | 原因 |
| --- | --- | --- |
| 频繁按位置读取 | 顺序表 | O(1) 随机访问 |
| 频繁在中间插入删除 | 链表 | 改指针 O(1)，只差"找位置"的 O(n) |
| 不知道要存多少数据 | 链表 | 随时 new，不用扩容 |
| 内存紧张、元素很小 | 顺序表 | 链表每个结点多一个指针，存储密度低 |
| 需要排序、随机访问、二分 | 顺序表 | 链表做不到随机访问 |

一句话：**查得多用顺序表，改得多用链表。**

## 链表的"阴间"操作预告

下面这些是期末大题和考研真题的常客，后面代码库里都有模板：

- 就地逆置：把 `next` 一个个反向，不新建结点。
- 找中间结点：快慢指针，快指针走两步、慢指针走一步。
- 判断有环：快慢指针相遇即有环。
- 合并两个有序链表：双指针"摘结点"。
- 删除倒数第 k 个：快指针先走 k 步。

掌握"双指针"这个套路，上面五类题都能现场推。
