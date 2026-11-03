---
id: queue-apps
title: 队列的两个高频应用
summary: 用队列写 BFS 求最短路，用单调队列求滑动窗口最大值。
minutes: 15
tags: 应用, BFS, 单调队列
exam: BFS 的队列过程, 单调队列维护最值
group: 队列
---

## 应用一：BFS 广度优先搜索

队列最经典的应用。从起点出发，先访问"距离 1"的所有点，再访问"距离 2"的所有点……正好是队列的 FIFO 顺序。

以迷宫最短路为例（0 可走，1 是墙，求从左上角到右下角的最少步数）：

```cpp
#include <queue>
int n, m;
int g[105][105], dist[105][105];
int dx[4] = {-1, 1, 0, 0};
int dy[4] = {0, 0, -1, 1};

int bfs(int sx, int sy) {
    memset(dist, -1, sizeof(dist));
    queue<pair<int,int>> q;
    q.push({sx, sy});
    dist[sx][sy] = 0;

    while (!q.empty()) {
        pair<int,int> cur = q.front();
        int x = cur.first, y = cur.second;
        q.pop();
        if (x == n - 1 && y == m - 1) return dist[x][y];

        for (int d = 0; d < 4; d++) {
            int nx = x + dx[d], ny = y + dy[d];
            if (nx < 0 || nx >= n || ny < 0 || ny >= m) continue;
            if (g[nx][ny] == 1 || dist[nx][ny] != -1) continue;
            dist[nx][ny] = dist[x][y] + 1;   // 第一次访问就是最短距离
            q.push({nx, ny});
        }
    }
    return -1;                                // 走不到
}
```

**为什么第一次访问就是最短路？** 因为 BFS 是按层扩展的，队列里的点距离都是单调不减的。这是 BFS 能求无权图最短路的核心原因，也是简答题常考的点。

:::exam BFS vs DFS
| | BFS | DFS |
| --- | --- | --- |
| 数据结构 | 队列 | 栈 / 递归 |
| 访问顺序 | 按层，由近到远 | 一条路走到黑 |
| 能否求最短路 | 能（无权图） | 不能（不保证第一次到就是最短） |
| 空间 | 最坏 O(点数) | 最坏 O(点数)，但常数小 |
:::

## 应用二：单调队列（滑动窗口最大值）

给一个长度为 n 的数组和一个窗口大小 k，窗口从左往右滑动，输出每个窗口里的最大值。

暴力做法每个窗口扫一遍，O(nk)。用**单调递减队列**可以做到 O(n)：

```cpp
vector<int> maxSlidingWindow(vector<int>& a, int k) {
    deque<int> dq;             // 存下标，对应的值从队头到队尾单调递减
    vector<int> res;
    for (int i = 0; i < (int)a.size(); i++) {
        // 1. 队头超出窗口范围就弹出
        while (!dq.empty() && dq.front() <= i - k) dq.pop_front();
        // 2. 队尾比当前元素小的都没用了，弹掉
        while (!dq.empty() && a[dq.back()] <= a[i]) dq.pop_back();
        // 3. 当前元素入队
        dq.push_back(i);
        // 4. 窗口形成后，队头就是最大值
        if (i >= k - 1) res.push_back(a[dq.front()]);
    }
    return res;
}
```

关键理解：**队列里存的是"还有可能成为最大值"的下标**，比当前元素小的那些永远不可能再成为最大值了，可以直接扔掉。

:::tip 单调队列的本质
它就是"一个会自动淘汰过时元素、并保持有序的队列"。滑动窗口最大值、窗口最小值、求最长子数组使最大最小差不超过 k，都是它的变体。
:::

## 顺带一提：两个队列 / 两个栈的转换

这是考试简答题的常客：

| 题目 | 做法 | 代价 |
| --- | --- | --- |
| 用两个栈实现队列 | 入队压 stackIn；出队时若 stackOut 空，把 stackIn 全部倒入 stackOut 再弹 | 均摊 O(1) |
| 用两个队列实现栈 | 入栈压 q1；出栈时把 q1 前 n-1 个移到 q2，弹出最后一个 | 均摊 O(n) |

"两个栈实现队列"是很常见的面试题，也是本章的一道练习题。
