// 链队列 —— 课件第 2 章（2）的 LinkedQueue 写法
// 编译：g++ -O2 -std=c++14 -o linkqueue linkqueue.cpp
//
// 为什么需要两个指针：
//   只有 front：入队要找表尾，Θ(n)
//   只有 rear ：出队要找前驱，Θ(n)
//   两个都有 ：入队、出队都是 Θ(1)
#include <iostream>
using namespace std;

template<class T>
struct Node {
    T data;
    Node<T>* next;
    Node(const T& d, Node<T>* n = 0) : data(d), next(n) {}
};

template<class T>
class LinkedQueue {
public:
    LinkedQueue() { front = rear = 0; }
    ~LinkedQueue() {
        while (front != 0) {
            Node<T>* next = front->next;
            delete front;
            front = next;
        }
    }

    bool IsEmpty() const { return front == 0; }

    T& First() const { return front->data; }   // 队首
    T& Last() const { return rear->data; }     // 队尾

    // 入队：接到表尾，尾指针后移
    void Add(const T& x) {
        Node<T>* p = new Node<T>(x);
        if (front == 0) front = rear = p;      // 队列本来是空的
        else { rear->next = p; rear = p; }
    }

    // 出队：删掉第一个结点
    void Delete(T& x) {
        if (front == 0) return;
        Node<T>* p = front;
        x = p->data;
        front = front->next;
        if (front == 0) rear = 0;              // 删完就空了，rear 也要归零
        delete p;
    }

    void Output() const {
        cout << "[";
        for (Node<T>* p = front; p != 0; p = p->next)
            cout << p->data << (p->next == 0 ? "" : " ");
        cout << "]\n";
    }

private:
    Node<T>* front;    // 队首
    Node<T>* rear;     // 队尾
};

int main() {
    LinkedQueue<int> q;
    for (int i = 1; i <= 4; i++) q.Add(i);
    cout << "入队 1..4：";
    q.Output();
    cout << "队首 " << q.First() << "，队尾 " << q.Last() << "\n";

    int x = 0;
    q.Delete(x);
    cout << "出队 " << x << " 后：";
    q.Output();

    q.Add(5);
    cout << "再入队 5：";
    q.Output();

    while (!q.IsEmpty()) { q.Delete(x); }
    cout << "全部出队后是否为空：" << (q.IsEmpty() ? "是" : "否") << "\n";
    return 0;
}
