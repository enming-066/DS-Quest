---
id: seq-stack
title: 顺序栈的实现
summary: 数组 + top 指针，四种操作的完整代码，以及上溢下溢怎么判断。
minutes: 15
tags: 顺序栈, 上溢, 下溢
exam: 判空判满条件, 入栈出栈代码, 上溢下溢的含义
group: 栈
---

## 结构定义

```cpp
#define MAXSIZE 100
typedef struct {
    int data[MAXSIZE];
    int top;          // 栈顶指针（这里是数组下标，不是指针）
} SqStack;
```

注意：`top` 虽然叫"指针"，实际存的是**数组下标**。这是课本的习惯叫法，别被它误导。

下面统一采用**约定 A：top 指向栈顶元素**（初始 `-1`），这也是大多数教材的写法。

```cpp
void InitStack(SqStack &S) {
    S.top = -1;
}

bool StackEmpty(const SqStack &S) {
    return S.top == -1;
}

bool StackFull(const SqStack &S) {
    return S.top == MAXSIZE - 1;
}

int StackLength(const SqStack &S) {
    return S.top + 1;
}

// 入栈
bool Push(SqStack &S, int e) {
    if (S.top == MAXSIZE - 1) return false;   // 上溢
    S.data[++S.top] = e;
    return true;
}

// 出栈，用 e 返回
bool Pop(SqStack &S, int &e) {
    if (S.top == -1) return false;            // 下溢
    e = S.data[S.top--];
    return true;
}

// 取栈顶但不删除
bool GetTop(const SqStack &S, int &e) {
    if (S.top == -1) return false;
    e = S.data[S.top];
    return true;
}
```

## 上溢和下溢

这是选择题里的名词解释：

| 名字 | 什么时候发生 | 原因 |
| --- | --- | --- |
| **上溢（overflow）** | 栈满了还要入栈 | 数组开小了 / 逻辑有问题 |
| **下溢（underflow）** | 栈空了还要出栈 | 通常是逻辑错误，或者"空栈出栈"本来就是非法的 |

:::exam 必背
- 栈满条件：`top == MAXSIZE - 1`
- 栈空条件：`top == -1`
- 元素个数：`top + 1`
- 入栈：`data[++top] = e`
- 出栈：`e = data[top--]`

如果题目用的是"top 指向栈顶下一个位置"，上面五个式子全部要换，**看到题目先确认约定**。
:::

## 为什么入栈出栈是 O(1)

顺序栈的所有操作都只碰 `top` 所在的那一个位置，不移动其他元素。所以入栈、出栈、取栈顶都是 **O(1)**，这是它比顺序表插入删除更适合"频繁增删"场景的原因。

## 共享栈（两个栈共用一个数组）

让两个栈从数组两头往中间长，可以更充分地利用空间：

```cpp
typedef struct {
    int data[MAXSIZE];
    int top0;   // 初始 -1，从左往右长
    int top1;   // 初始 MAXSIZE，从右往左长
} SharedStack;
```

- 栈 0 满的条件：`top0 + 1 == top1`（两个指针相遇）
- 入栈 0：`data[++top0] = e`
- 入栈 1：`data[--top1] = e`

**只有两个栈的"总容量"满了才算满**，比各占一半更灵活。这是考试里"如何用两个栈共享一个数组"的经典答案。

:::pitfall 常见错误
1. 入栈写成 `S.data[S.top++] = e`，在约定 A 下会把元素放到错误位置（先用了 -1 下标）。
2. 出栈后忘记 `top--`，或者 `Pop` 里先 `top--` 再取值。
3. 判满用了 `top == MAXSIZE`，越界一个位置。
4. 把 `top` 当成指针去 `*top`，它就是个整数下标。
:::
