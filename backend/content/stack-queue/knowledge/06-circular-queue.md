---
id: circular-queue
title: 循环队列：判空与判满
summary: 课件用"front 指向队首前一个位置、rear 指向队尾"的约定，公式和另一种常见写法完全不同，别混用。
minutes: 18
tags: 循环队列, 判空, 判满, 取模
exam: 课件约定的判空判满公式, 元素个数, 三种解决方案对比
group: 队列
---

## 核心思想

把数组的最后一个位置和第一个位置"接起来"：`rear = (rear + 1) % MaxSize`。这样 rear 永远不会越界，空间可以反复利用。

```
      ┌───┬───┬───┬───┬───┬───┐
      │ 0 │ 1 │ 2 │ 3 │ 4 │ 5 │
      └───┴───┴───┴───┴───┴───┘
        ↑                   ↑
      front               rear
      绕回去：rear = (rear+1) % MaxSize
```

## 问题：front == rear 到底是空还是满？

环形数组里，**空的时候 front == rear**；但一直入队绕一圈之后，**满了也会 front == rear**。所以光看两个指针分不出来。

课件给的解决方案是：**只允许最多存 MaxSize-1 个元素，留一个空位**。

## 课件用的约定（重点，按这个答题）

课件第 2 章（2）P18~P23 的写法（引自《数据结构、算法与应用》）：

- **`front` 指向队首元素的前一个位置**（即 `location(1) - 1`）
- **`rear` 指向最后一个元素所在的位置**
- 队列空：`front == rear`
- 队列满：`front == (rear + 1) % MaxSize`
- 队首元素：`queue[(front + 1) % MaxSize]`
- 队尾元素：`queue[rear]`

入队和出队都是**先移动指针、再操作元素**：

```cpp
template<class T>
class Queue {
public:
    Queue(int MaxQueueSize = 10) {
        MaxSize = MaxQueueSize + 1;      // 留出一个额外空间
        queue = new T[MaxSize];
        front = rear = 0;
    }
    ~Queue() { delete[] queue; }

    bool IsEmpty() const { return front == rear; }
    bool IsFull() const  { return ((rear + 1) % MaxSize == front); }

    T First() const { return queue[(front + 1) % MaxSize]; }
    T Last() const  { return queue[rear]; }

    void Add(const T& x) {
        if (IsFull()) return;            // 课件里是抛 NoMem 异常
        rear = (rear + 1) % MaxSize;     // 先移指针
        queue[rear] = x;                 // 再放元素
    }

    void Delete(T& x) {
        if (IsEmpty()) return;           // 课件里是抛 OutOfBounds 异常
        front = (front + 1) % MaxSize;   // 先移指针
        x = queue[front];                // 再取元素
    }

private:
    int front, rear, MaxSize;
    T* queue;
};
```

:::exam 为什么构造函数要 +1
用户传 `MaxQueueSize = 10`，实际数组开 11。因为**要空出一个位置来区分空和满**，
所以真正能存的是 `MaxQueueSize` 个元素。这一行 `MaxSize = MaxQueueSize + 1;` 是课件里专门标注的。
:::

## 两种约定别混用（最常见的丢分点）

同一道题，如果题目换了约定，所有公式都要换。对照记：

| 项目 | 课件约定：front 指向队首**前一位**，rear 指向队尾 | 另一种常见约定：front 指向队首，rear 指向队尾**后一位** |
| --- | --- | --- |
| 空 | `front == rear` | `front == rear` |
| 满 | `front == (rear+1) % MaxSize` | `(rear+1) % MaxSize == front` |
| 入队 | `rear = (rear+1)%M; q[rear] = x;` | `q[rear] = x; rear = (rear+1)%M;` |
| 出队 | `front = (front+1)%M; x = q[front];` | `x = q[front]; front = (front+1)%M;` |
| 队首 | `q[(front+1)%M]` | `q[front]` |
| 元素个数 | `(rear - front + M) % M` | `(rear - front + M) % M` |

**好消息**：元素个数的公式两边一样，都是 `(rear - front + M) % M`。
**坏消息**：判满的式子写法相反，答题前先看题目给的是哪种。

:::tip 怎么快速判断是哪种
看题目里的图：**如果 front 指着的那格是空的（或指向队首的前一格），就是课件约定**；
如果 front 指的那格有元素，就是另一种。抢答一句：看 `rear` 指的格子有没有装元素——装了就是课件约定。
:::

## 另外两种解决方案（选择题会考）

### 方案二：增加一个 size 变量

记当前元素个数，`size == 0` 为空，`size == MaxSize` 为满。不浪费空间，但要多维护一个变量。

### 方案三：增加 tag 标志

`tag = 0` 表示最近一次操作是出队，`tag = 1` 表示最近一次是入队。

- `front == rear` 且 `tag == 0` → 空
- `front == rear` 且 `tag == 1` → 满

原理：只有"入队导致重合"才是满，只有"出队导致重合"才是空。

:::exam 三种方案怎么答
- **考试作答**：方案一（牺牲一个单元），因为是课件原话。
- **实际工程**：方案二（size），不浪费空间、代码最直观。
- **方案三**：只在选择题里出现，理解原理即可。
:::

## 易错点

:::pitfall 每年都有人错的四个地方
1. 把课件的 `front` 当成"指向队首元素"，结果 First() 取错了位置。
2. 忘了 `% MaxSize`，rear 越界数组直接崩。
3. 判满写成 `rear == front`，把满当成了空。
4. 构造函数没有 `+1`，导致实际少存一个元素，或者判满失效。
:::

## 小练习

MaxSize = 5（能存 4 个），初始 `front = rear = 0`，依次执行：Add(1)、Add(2)、Add(3)、Delete、Add(4)、Add(5)、Add(6)。

```
Add 1   rear=1  q[1]=1        front=0
Add 2   rear=2  q[2]=2        front=0
Add 3   rear=3  q[3]=3        front=0
Delete  front=1  x=q[1]=1     front=1, rear=3
Add 4   rear=4  q[4]=4        front=1
Add 5   rear=(4+1)%5=0 q[0]=5 front=1
Add 6   (0+1)%5 = 1 == front → 满了，失败
```

此时队列里是 2、3、4、5，共 4 个，正好是 MaxSize-1。动手推一遍，比背公式管用。
