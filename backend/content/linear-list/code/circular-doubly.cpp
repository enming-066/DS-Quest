// 循环链表 + 双向链表 —— 课件第 1 章 P33~P37
// 编译：g++ -O2 -std=c++14 -o circular_doubly circular_doubly.cpp
#include <iostream>
using namespace std;

// ============================================================
// 一、单向循环链表（用尾指针表示）
//   最后一个结点的 next 指回第一个结点，形成环。
//   只记尾指针 rear 的好处：rear->next 就是首结点，头尾都是 Θ(1)。
// ============================================================
template<class T>
class CircList {
public:
    CircList() { rear = 0; length = 0; }

    // 在表尾插入：新结点成为新的尾，它的 next 指回首结点
    void insert(const T& x) {
        Node* p = new Node;
        p->data = x;
        if (rear == 0) {          // 空表：自己指向自己
            rear = p;
            p->next = p;
        } else {
            p->next = rear->next; // 新结点接原来的首结点
            rear->next = p;       // 旧的尾接新结点
            rear = p;             // 尾巴前移
        }
        length++;
    }

    // 约瑟夫环：报数到 m 的人出列
    // 外层走 n-1 轮，内层每轮走 m-1 步 → Θ(mn)
    void josephus(int n, int m) {
        if (rear == 0) return;
        Node* p = rear->next;     // p 指向当前报数的人
        Node* pre = rear;         // pre 是 p 的前驱
        for (int i = 0; i < n; i++) {
            for (int j = 0; j < m - 1; j++) {   // 数 m-1 个人
                pre = p;
                p = p->next;
            }
            cout << p->data << (i + 1 == n ? "" : " ");
            pre->next = p->next;   // 出列：前驱越过 p
            delete p;
            p = pre->next;         // 从下一个人重新报数
        }
        cout << "\n";
        rear = 0;
        length = 0;
    }

private:
    struct Node {
        T data;
        Node* next;
    };
    Node* rear;               // 尾指针（不是头指针！）
    int length;
};

// ============================================================
// 二、双向链表
//   每个结点有 prior 和 next 两个指针，能往回走，
//   已知结点时删除是 Θ(1)（单链表还要找前驱，Θ(n)）。
// ============================================================
template<class T>
struct DNode {
    T data;
    DNode<T>*prior, *next;
    DNode(const T& d, DNode<T>* p = 0, DNode<T>* n = 0) : data(d), prior(p), next(n) {}
};

// 在结点 p 之后插入 s —— 注意四个指针的顺序
template<class T>
void insertAfter(DNode<T>* p, DNode<T>* s) {
    s->next = p->next;             // ① s 接上 p 的原后继
    if (p->next != 0) p->next->prior = s;  // ② 原后继回指 s（可能为空）
    s->prior = p;                  // ③ s 的前驱指向 p
    p->next = s;                   // ④ 最后才改 p->next
}

// 删除结点 p，Θ(1)
template<class T>
void eraseNode(DNode<T>* p) {
    if (p->prior != 0) p->prior->next = p->next;
    if (p->next != 0) p->next->prior = p->prior;
    delete p;
}

template<class T>
void printDList(DNode<T>* head) {
    for (DNode<T>* q = head; q != 0; q = q->next)
        cout << q->data << (q->next == 0 ? "" : " ");
    cout << "\n";
}

int main() {
    cout << "循环链表（约瑟夫，n=8, m=3）：";
    CircList<int> clist;
    for (int i = 1; i <= 8; i++) clist.insert(i);
    clist.josephus(8, 3);

    cout << "双向链表：";
    DNode<int>* head = new DNode<int>(1);
    DNode<int>* second = new DNode<int>(2);
    insertAfter(head, second);
    insertAfter(second, new DNode<int>(3));
    printDList(head);

    eraseNode(second);
    cout << "删除值为 2 的结点后：";
    printDList(head);
    return 0;
}
