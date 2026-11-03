---
id: link-queue
title: 链队列
summary: 队头删、队尾插，为什么需要两个指针，以及出队时要特判空队列。
minutes: 10
tags: 链队列, front, rear
exam: 链队列的判空条件, 出队时 rear 的维护
group: 队列
---

## 结构

链队列 = 一个带头结点的单链表 + 一个**尾指针**。

```cpp
typedef struct QNode {
    int data;
    struct QNode *next;
} QNode, *QueuePtr;

typedef struct {
    QueuePtr front;   // 队头指针，指向头结点
    QueuePtr rear;    // 队尾指针，指向最后一个结点
} LinkQueue;
```

```
          front              rear
            ↓                  ↓
        [头结点] → [10] → [20] → [30|^]
                                 ↑ 入队在这里
            ↑ 出队删这里后面的第一个
```

**为什么必须同时有 front 和 rear？**

- 只有 front：尾插要 O(n) 找尾巴。
- 只有 rear：出队要 O(n) 找前驱。
- 两个都有：入队 O(1)，出队 O(1)。

## 代码

```cpp
bool InitQueue(LinkQueue &Q) {
    Q.front = Q.rear = new QNode;   // 头结点
    if (Q.front == NULL) return false;
    Q.front->next = NULL;
    return true;
}

bool QueueEmpty(LinkQueue Q) {
    return Q.front == Q.rear;       // 或 Q.front->next == NULL
}

bool EnQueue(LinkQueue &Q, int e) {
    QNode *s = new QNode;
    if (s == NULL) return false;
    s->data = e;
    s->next = NULL;
    Q.rear->next = s;               // 接到队尾
    Q.rear = s;                     // 尾指针后移
    return true;
}

bool DeQueue(LinkQueue &Q, int &e) {
    if (Q.front == Q.rear) return false;   // 空队列
    QNode *p = Q.front->next;              // 队头元素
    e = p->data;
    Q.front->next = p->next;
    if (Q.rear == p) Q.rear = Q.front;     // ← 关键：删的是最后一个结点
    delete p;
    return true;
}
```

:::warning 最容易被忽略的一行
`if (Q.rear == p) Q.rear = Q.front;`

当队列里**只剩一个元素**时，出队后队列变空，`rear` 原来指向那个被删掉的结点，如果不把它拉回头结点，rear 就成了**悬空指针**，下一次入队直接崩溃。这是链队列代码里最经典的 bug，也是考试常考的填空点。
:::

## 顺序循环队列 vs 链队列

| | 循环队列 | 链队列 |
| --- | --- | --- |
| 存储 | 连续数组 | 分散结点 |
| 容量 | 固定（实际 MAXSIZE-1） | 按需增长 |
| 判满 | 需要 | 不需要 |
| 每元素开销 | 小 | 多一个指针 |
| 空判断 | `front == rear` | `front == rear`（或 `front->next == NULL`） |
| 适用 | 个数可预估、追求速度 | 个数变化大 |

:::exam 一句话
循环队列**怕满**，链队列**怕空**（出队时 rear 要特判）。两句话把两种结构的难点说完了。
:::
