---
id: circular-queue
title: 循环队列：判空与判满
summary: 牺牲一个单元、设 size、加 tag 三种方案，以及元素个数公式。
minutes: 18
tags: 循环队列, 判空, 判满, 取模
exam: 循环队列判空判满条件, 元素个数公式, 三种解决方案对比
group: 队列
---

## 核心思想

把数组的最后一个位置和第一个位置"接起来"：`rear = (rear + 1) % MAXSIZE`。这样 rear 永远不会越界，空间可以反复利用。

```
      ┌───┬───┬───┬───┬───┬───┐
      │ 0 │ 1 │ 2 │ 3 │ 4 │ 5 │
      └───┴───┴───┴───┴───┴───┘
        ↑                   ↑
      front               rear
      绕回去：rear = (rear+1) % 6
```

## 问题来了：front == rear 到底是空还是满？

在环形数组里，空的时候 `front == rear`；但如果一直入队，绕一圈之后**满了也会出现 `front == rear`**。

```
空：front = 0, rear = 0
满：入队 6 个后 front = 0, rear = 0（又重合了）
```

所以无法只靠 front 和 rear 区分空和满。三种经典解法：

### 方案一：牺牲一个存储单元（最常见）

**约定：队列最多存 `MAXSIZE - 1` 个元素，永远留一个空位。**

- 空：`front == rear`
- 满：`(rear + 1) % MAXSIZE == front`
- 元素个数：`(rear - front + MAXSIZE) % MAXSIZE`

```cpp
#define MAXSIZE 100
typedef struct {
    int data[MAXSIZE];
    int front, rear;      // rear 指向队尾元素的下一个位置
} SqQueue;

void InitQueue(SqQueue &Q) { Q.front = Q.rear = 0; }

bool QueueEmpty(SqQueue Q) { return Q.front == Q.rear; }

bool QueueFull(SqQueue Q) { return (Q.rear + 1) % MAXSIZE == Q.front; }

int QueueLength(SqQueue Q) { return (Q.rear - Q.front + MAXSIZE) % MAXSIZE; }

bool EnQueue(SqQueue &Q, int e) {
    if (QueueFull(Q)) return false;
    Q.data[Q.rear] = e;
    Q.rear = (Q.rear + 1) % MAXSIZE;
    return true;
}

bool DeQueue(SqQueue &Q, int &e) {
    if (QueueEmpty(Q)) return false;
    e = Q.data[Q.front];
    Q.front = (Q.front + 1) % MAXSIZE;
    return true;
}

bool GetHead(SqQueue Q, int &e) {
    if (QueueEmpty(Q)) return false;
    e = Q.data[Q.front];
    return true;
}
```

:::exam 公式必背
| 项目 | 公式 |
| --- | --- |
| front 前进 | `front = (front + 1) % MAXSIZE` |
| rear 前进 | `rear = (rear + 1) % MAXSIZE` |
| 判空 | `front == rear` |
| 判满 | `(rear + 1) % MAXSIZE == front` |
| 元素个数 | `(rear - front + MAXSIZE) % MAXSIZE` |
| 实际容量 | `MAXSIZE - 1` |

**"牺牲一个单元"是考试默认答案**，看到题目没说别的就用这个。
:::

### 方案二：增加一个 size 变量

记录当前元素个数，`size == 0` 为空，`size == MAXSIZE` 为满。不浪费空间，但要多维护一个变量。

```cpp
bool QueueEmpty(SqQueue Q) { return Q.size == 0; }
bool QueueFull(SqQueue Q)  { return Q.size == MAXSIZE; }
// 入队：data[rear] = e; rear = (rear+1)%MAXSIZE; size++;
// 出队：e = data[front]; front = (front+1)%MAXSIZE; size--;
```

### 方案三：增加 tag 标志

`tag = 0` 表示最近一次操作是**出队**，`tag = 1` 表示最近一次是**入队**。

- `front == rear` 且 `tag == 0` → 空
- `front == rear` 且 `tag == 1` → 满

原理：只有"入队导致重合"才是满，只有"出队导致重合"才是空。

:::tip 三种方案怎么选
- **考试作答**：方案一（牺牲单元），公式最好记，最标准。
- **实际工程**：方案二（size），不浪费空间，代码也最直观。
- **方案三**：只在选择题里出现，理解原理即可。
:::

## 易错点集中营

:::pitfall 每年都有人错的四个地方
1. **rear 指向队尾元素还是它的下一个位置？** 课本主流是"下一个位置"（本篇采用）。若题目说 rear 指向队尾元素本身，判满变成 `(rear + 1) % MAXSIZE == front`，元素个数变成 `(rear - front + 1 + MAXSIZE) % MAXSIZE`。**先看清题目约定。**
2. **`% MAXSIZE` 忘了写**，rear 越界数组直接崩。
3. **判满写成 `rear == front`**，把满当成了空。
4. **元素个数算出负数**：`(rear - front + MAXSIZE) % MAXSIZE`，加 MAXSIZE 是为了处理 rear < front 的情况，不能省。
:::

## 小练习：自己推一遍

MAXSIZE = 5，依次执行：入队 1、2、3 → 出队 → 出队 → 入队 4、5。

```
初始      front=0 rear=0  空
入 1      data[0]=1  rear=1
入 2      data[1]=2  rear=2
入 3      data[2]=3  rear=3
出        返回 data[0]=1, front=1
出        返回 data[1]=2, front=2
入 4      data[3]=4  rear=4
入 5      data[4]=5  rear=(4+1)%5=0
         此时 front=2, rear=0
满了吗？(0+1)%5 = 1 != 2 → 没满（还能再放 1 个，因为牺牲了一个单元）
元素个数：(0 - 2 + 5) % 5 = 3
```

前三个出的顺序是 1、2，队列里现在是 3、4、5 —— 数一数正好 3 个。动手推一遍，比背公式管用。
