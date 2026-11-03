// 合并两个有序单链表（非递减）—— 双指针"摘结点"，不新建结点
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

// 把 B 合并进 A，复用 A 的头结点，返回结果表
LinkList Merge(LinkList &A, LinkList &B) {
    LNode *p = A->next;
    LNode *q = B->next;
    LNode *r = A;                       // r 是结果表的尾指针
    while (p != nullptr && q != nullptr) {
        if (p->data <= q->data) {       // 谁小先接谁
            r->next = p;
            r = p;
            p = p->next;
        } else {
            r->next = q;
            r = q;
            q = q->next;
        }
    }
    r->next = (p != nullptr) ? p : q;   // 剩下的一段直接接上
    delete B;                           // B 的头结点已经没用了
    B = nullptr;
    return A;
}

int main() {
    LinkList A, B;
    int a[] = {1, 3, 5, 7};
    int b[] = {2, 4, 6, 8, 10};
    CreateListTail(A, a, 4);
    CreateListTail(B, b, 5);

    cout << "A："; PrintList(A);
    cout << "B："; PrintList(B);
    Merge(A, B);
    cout << "合并后："; PrintList(A);
    return 0;
}
