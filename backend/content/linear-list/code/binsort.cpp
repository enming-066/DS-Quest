// 箱子排序（Bin Sort）—— 课件第 1 章 P58~P63，链表的经典应用
// 编译：g++ -O2 -std=c++14 -o binsort binsort.cpp
//
// 思路：关键字范围是 [0, range]，就开 range+1 个"箱子"（每个箱子是一条链）。
//   1) 分发：按关键字把结点挂到对应箱子的【尾部】
//   2) 收集：从 0 号箱子开始，把各箱子依次串起来
// 因为分发时挂尾部，所以相同关键字的结点保持原来的相对顺序 —— 稳定排序。
// 时间复杂度 O(n + range)，空间 O(range)。
#include <iostream>
#include <vector>
using namespace std;

struct Node {
    int key;        // 排序关键字，范围 [0, range]
    int id;         // 附加数据，用来验证稳定性
    Node* next;
    Node(int k, int i) : key(k), id(i), next(0) {}
};

// 返回排好序的链表头指针
Node* binSort(Node* first, int range) {
    // bottom[b]、top[b] 分别指向 b 号箱子的头和尾
    vector<Node*> bottom(range + 1, (Node*)0);
    vector<Node*> top(range + 1, (Node*)0);

    // ① 分发：把每个结点从原链表摘下，挂到对应箱子的尾部
    for (Node* p = first; p != 0; ) {
        Node* next = p->next;          // 先记住下一个
        int b = p->key;
        p->next = 0;
        if (bottom[b] == 0) {          // 箱子还空着
            bottom[b] = top[b] = p;
        } else {                       // 挂到箱子尾部（保证稳定）
            top[b]->next = p;
            top[b] = p;
        }
        p = next;
    }

    // ② 收集：按箱号从小到大把各箱子串成一个链表
    Node* head = 0;
    Node* tail = 0;
    for (int b = 0; b <= range; b++) {
        if (bottom[b] == 0) continue;
        if (head == 0) {
            head = bottom[b];
            tail = top[b];
        } else {
            tail->next = bottom[b];
            tail = top[b];
        }
    }
    return head;
}

int main() {
    // (key, id)：两个 key=2 的结点 id 分别是 1 和 3，排序后应保持 1 在 3 前面
    int keys[] = {2, 1, 2, 0, 1};
    int ids[]  = {1, 2, 3, 4, 5};
    int n = 5, range = 2;

    Node* first = 0;
    Node* tail = 0;
    for (int i = 0; i < n; i++) {
        Node* s = new Node(keys[i], ids[i]);
        if (first == 0) first = tail = s;
        else { tail->next = s; tail = s; }
    }

    cout << "排序前：" ;
    for (Node* p = first; p != 0; p = p->next) cout << "(" << p->key << "," << p->id << ") ";
    cout << "\n";

    first = binSort(first, range);

    cout << "排序后：" ;
    for (Node* p = first; p != 0; p = p->next) cout << "(" << p->key << "," << p->id << ") ";
    cout << "\n";

    cout << "按关键字输出 id：" ;
    for (Node* p = first; p != 0; p = p->next) cout << p->id << (p->next ? " " : "");
    cout << "\n";
    return 0;
}
