// 循环队列 —— 严格按课件第 2 章（2）P19~P23 的写法
// 编译：g++ -O2 -std=c++14 -o circular_queue circular_queue.cpp
//
// 课件约定（和很多教材相反，务必看清）：
//   front 指向队首元素的【前一个位置】，rear 指向最后一个元素。
//   空：front == rear
//   满：front == (rear + 1) % MaxSize
//   构造时 MaxSize = MaxQueueSize + 1，多留一格用来区分空和满。
#include <iostream>
using namespace std;

template<class T>
class Queue {
public:
    Queue(int MaxQueueSize = 10) {
        MaxSize = MaxQueueSize + 1;        // 留出一个额外空间
        queue = new T[MaxSize];
        front = rear = 0;
    }
    ~Queue() { delete[] queue; }

    bool IsEmpty() const { return front == rear; }
    bool IsFull() const { return ((rear + 1) % MaxSize == front); }

    // 队首在 front 的后一格，队尾就是 rear 那一格
    T First() const { return queue[(front + 1) % MaxSize]; }
    T Last() const { return queue[rear]; }

    // 入队：先移动 rear，再写入
    bool Add(const T& x) {
        if (IsFull()) return false;
        rear = (rear + 1) % MaxSize;
        queue[rear] = x;
        return true;
    }

    // 出队：先移动 front，再取值
    bool Delete(T& x) {
        if (IsEmpty()) return false;
        front = (front + 1) % MaxSize;
        x = queue[front];
        return true;
    }

    // 元素个数：两种约定下公式一样
    int Length() const { return (rear - front + MaxSize) % MaxSize; }

    void Output() const {
        cout << "[";
        for (int i = 1; i <= Length(); i++) {
            cout << queue[(front + i) % MaxSize];
            if (i < Length()) cout << " ";
        }
        cout << "]  个数=" << Length() << "\n";
    }

private:
    int front;    // 队首的前一个位置
    int rear;     // 队尾
    int MaxSize;
    T* queue;
};

int main() {
    Queue<int> q(4);                 // 用户说容量 4，实际数组 5，能存 4 个

    for (int i = 1; i <= 4; i++) {
        bool ok = q.Add(i);
        cout << "Add(" << i << ") " << (ok ? "成功" : "失败（队满）") << "  ";
        q.Output();
    }

    int x = 0;
    q.Delete(x);
    cout << "Delete -> " << x << "  ";
    q.Output();

    q.Add(5);
    cout << "Add(5) 成功  ";
    q.Output();

    cout << "还能再插入吗？" << (q.IsFull() ? "不能，满了" : "可以") << "\n";
    cout << "队首 First = " << q.First() << "，队尾 Last = " << q.Last() << "\n";
    return 0;
}
