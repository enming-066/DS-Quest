---
id: linkedlist
title: 单链表：链式描述的增删改查
summary: 课件里的 Chain / ChainNode——get 为什么要走 k 步，erase 为什么要先找前驱，析构为什么不能只删一个。
minutes: 20
tags: 单链表, ChainNode, 指针, 复杂度
exam: 链表插入删除的指针顺序, 与数组描述的复杂度对比, 析构函数
group: 基础
---

## 存储方式：把元素装进结点

课件第 1 章 P26 的定义只有两个成员：

```cpp
template <class T>
class ChainNode {
    friend class Chain<T>;
private:
    T data;                // 数据域
    ChainNode<T>* next;    // 链接域
};

template <class T>
class Chain {
protected:
    ChainNode<T>* firstNode;   // 首结点
    int listSize;              // 元素个数
};
```

```
firstNode
   ↓
[10|●] → [20|●] → [30|^]
```

最后一个结点的 `next` 是 `0`（空指针）。**链表不要求内存连续**，靠指针把结点串起来——这就是"用指针表示逻辑相邻"。

:::tip 和数组描述最本质的区别
数组能"算地址"，链表只能"走过去"。
`get(k)`：数组 Θ(1)，链表 Θ(k)——这是链表唯一的硬伤，所有其他优势都建立在"不按下标访问"的前提下。
:::

## get：为什么要走 k 步

```cpp
T& get(int theIndex) const {
    ChainNode<T>* current = firstNode;
    for (int i = 0; i < theIndex; i++)
        current = current->next;
    return current->data;
}
```

没有地址公式可用，只能从首结点开始一步一步走。所以**按下标访问是 Θ(k)，最坏 Θ(n)**。
这也是为什么"链表支持随机访问"是错的——它只支持顺序访问。

## indexOf：和数组一样是 Θ(n)

```cpp
int indexOf(const T& theElement) const {
    ChainNode<T>* current = firstNode;
    int index = 0;
    while (current != 0 && current->data != theElement) {
        current = current->next;
        index++;
    }
    return current == 0 ? -1 : index;
}
```

数组和链表在"按值查找"上都要扫一遍，都是 Θ(n)。**链表的优势不在这里。**

## erase：先找前驱，再越过它

删除结点必须改**前驱**的 `next`，单链表又看不到前驱，所以要先走 `theIndex-1` 步：

```cpp
void erase(int theIndex) {
    ChainNode<T>* deleteNode;
    if (theIndex == 0) {                 // ① 删首结点：没有前驱，特判
        deleteNode = firstNode;
        firstNode = firstNode->next;
    } else {
        ChainNode<T>* p = firstNode;
        for (int i = 0; i < theIndex - 1; i++)
            p = p->next;                 // ② p 停在待删结点的前驱
        deleteNode = p->next;            // ③ 先记住要删的结点
        p->next = p->next->next;         // ④ 前驱越过它
    }
    listSize--;
    delete deleteNode;                   // ⑤ 释放内存
}
```

**三步缺一不可**：找到前驱 → 改链接 → 释放内存。数组删除不需要第 ⑤ 步，这是链表独有的。

## insert：首结点也要特判

```cpp
void insert(int theIndex, const T& theElement) {
    if (theIndex == 0) {                                  // 插在表头
        firstNode = new ChainNode<T>(theElement, firstNode);
    } else {
        ChainNode<T>* p = firstNode;
        for (int i = 0; i < theIndex - 1; i++)
            p = p->next;                                  // 找到前驱
        p->next = new ChainNode<T>(theElement, p->next);  // 新结点接上 p 的后继
    }
    listSize++;
}
```

课件里那个 `new ChainNode<T>(theElement, p->next)` 是**构造函数一次搞定两件事**：建结点 + 让它的 next 指向 p 的后继。写成两行也完全正确：

```cpp
ChainNode<T>* s = new ChainNode<T>(theElement);
s->next = p->next;    // 先接后断
p->next = s;
```

:::warning 顺序不能反
`p->next = s; s->next = p->next;` 是经典错误——第一步就把 `p->next` 改成了 s，第二步 `s->next = s` 自己指向自己，后半条链全丢。
:::

## 析构函数：链表专属的坑

```cpp
template<class T>
Chain<T>::~Chain() {
    ChainNode<T>* next;
    while (firstNode != 0) {
        next = firstNode->next;   // 先存住下一个
        delete firstNode;         // 再删当前
        firstNode = next;
    }
}
```

如果只写 `delete firstNode;`，后面所有结点都会泄漏——而数组描述只要 `delete[] element;` 一句。**这是"链表要不要写析构"的送分题。**

## 复杂度对比（课件 P39~P40）

| 操作 | 数组描述 | 链式描述 |
| --- | --- | --- |
| `get(k)` | Θ(1) | Θ(k) |
| `indexOf(x)` | Θ(n) | Θ(n) |
| `erase(k)` | Θ(n)（挪元素） | Θ(k)（走 + 改指针） |
| `insert(k, x)` | Θ(n)（挪元素） | Θ(k)（走 + 建结点） |
| `size()` / `empty()` | Θ(1) | Θ(1)（维护 listSize） |
| 存储分配 | 预先分配、连续 | 按需申请、分散 |
| 额外开销 | 无 | 每个结点一个指针 |

:::exam 一个很爱问的追问
"如果已经拿到待删结点的指针（不是下标），删除是 Θ(1) 还是 Θ(n)？"
——**单链表还是 Θ(n)**，因为要找回前驱；**双向链表才是 Θ(1)**。这个区别考试反复考。
:::

:::pitfall 四个高频错误
1. 遍历写成 `p->next != 0`，最后一个结点漏掉；应该是 `p != 0`。
2. 删除时先改 `p->next` 再 `delete`，找不到要删的结点了。
3. 插入时先断后接，把后半条链丢了。
4. 析构只删了首结点。
:::
