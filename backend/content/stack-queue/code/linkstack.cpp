// 链栈（C++ 版）—— 栈顶在链表头部，不带头结点
#include <iostream>
using namespace std;

typedef struct StackNode {
    int data;
    struct StackNode *next;
} StackNode, *LinkStack;

void InitStack(LinkStack &S) { S = nullptr; }
bool StackEmpty(LinkStack S) { return S == nullptr; }

// 入栈 = 头插
bool Push(LinkStack &S, int e) {
    StackNode *s = new StackNode;
    if (s == nullptr) return false;
    s->data = e;
    s->next = S;
    S = s;
    return true;
}

// 出栈 = 删除第一个结点
bool Pop(LinkStack &S, int &e) {
    if (S == nullptr) return false;
    StackNode *p = S;
    e = p->data;
    S = S->next;
    delete p;
    return true;
}

bool GetTop(LinkStack S, int &e) {
    if (S == nullptr) return false;
    e = S->data;
    return true;
}

int main() {
    LinkStack S;
    InitStack(S);

    for (int i = 1; i <= 4; i++) Push(S, i);
    cout << "出栈顺序：";
    int e;
    while (Pop(S, e)) cout << e << " ";
    cout << "\n";
    return 0;
}
