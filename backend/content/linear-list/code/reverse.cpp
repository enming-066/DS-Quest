// 单链表就地逆置 —— 期末最爱考的大题之一
// 要求：不新建结点、不额外开数组，只改指针
#include <iostream>
using namespace std;

typedef struct LNode {
    int data;
    struct LNode *next;
} LNode, *LinkList;

void CreateListTail(LinkList &L, const int a[], int n) {
    L = new LNode;
    L->next = nullptr;
    LNode *r = L;
    for (int i = 0; i < n; i++) {
        LNode *s = new LNode;
        s->data = a[i];
        s->next = nullptr;
        r->next = s;
        r = s;
    }
}

void PrintList(LinkList L) {
    if (L->next == nullptr) { cout << "(空表)\n"; return; }
    for (LNode *p = L->next; p != nullptr; p = p->next) {
        cout << p->data << (p->next == nullptr ? '\n' : ' ');
    }
}

// 核心：把每个结点摘下来，头插到新表
void Reverse(LinkList L) {
    LNode *p = L->next;      // p 是当前要处理的结点
    LNode *q = nullptr;      // q 用来暂存 p 的后继
    L->next = nullptr;       // 头结点断开，成为新表的头
    while (p != nullptr) {
        q = p->next;         // ① 先记住下一个
        p->next = L->next;   // ② 当前结点指向新表头部
        L->next = p;         // ③ 头结点指向当前结点
        p = q;               // ④ 继续处理下一个
    }
}

int main() {
    LinkList L;
    int a[] = {1, 2, 3, 4, 5};
    CreateListTail(L, a, 5);
    cout << "逆置前：";
    PrintList(L);
    Reverse(L);
    cout << "逆置后：";
    PrintList(L);
    return 0;
}
