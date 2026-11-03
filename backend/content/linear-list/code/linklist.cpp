// 单链表（C++ 版，带头结点）—— 建表、插入、删除、遍历、清空
// 编译：g++ -std=c++17 -o linklist linklist.cpp
#include <iostream>
using namespace std;

typedef struct LNode {
    int data;
    struct LNode *next;
} LNode, *LinkList;

// 初始化：创建一个头结点，数据域不用
bool InitList(LinkList &L) {
    L = new LNode;
    if (L == nullptr) return false;
    L->next = nullptr;
    return true;
}

// 尾插法建表：保持输入顺序
void CreateListTail(LinkList &L, const int a[], int n) {
    InitList(L);
    LNode *r = L;                       // r 始终指向表尾
    for (int i = 0; i < n; i++) {
        LNode *s = new LNode;
        s->data = a[i];
        s->next = nullptr;
        r->next = s;
        r = s;
    }
}

// 头插法建表：顺序会反过来（输入 1 2 3 → 链表 3 2 1）
void CreateListHead(LinkList &L, const int a[], int n) {
    InitList(L);
    for (int i = 0; i < n; i++) {
        LNode *s = new LNode;
        s->data = a[i];
        s->next = L->next;
        L->next = s;
    }
}

// 求表长
int Length(LinkList L) {
    int n = 0;
    for (LNode *p = L->next; p != nullptr; p = p->next) n++;
    return n;
}

// 在第 i 个位置插入 e（位序从 1 开始）
bool ListInsert(LinkList &L, int i, int e) {
    if (i < 1) return false;
    LNode *p = L;
    int j = 0;
    while (p != nullptr && j < i - 1) {   // 找第 i-1 个结点
        p = p->next;
        j++;
    }
    if (p == nullptr) return false;
    LNode *s = new LNode;
    s->data = e;
    s->next = p->next;                    // 先接后断
    p->next = s;
    return true;
}

// 删除第 i 个元素，e 带回被删的值
bool ListDelete(LinkList &L, int i, int &e) {
    if (i < 1) return false;
    LNode *p = L;
    int j = 0;
    while (p != nullptr && j < i - 1) {
        p = p->next;
        j++;
    }
    if (p == nullptr || p->next == nullptr) return false;
    LNode *q = p->next;                   // 先记住要删的结点
    e = q->data;
    p->next = q->next;                    // 越过它
    delete q;                             // 别忘了释放
    return true;
}

// 按值查找：返回结点指针，找不到返回 nullptr
LNode *Locate(LinkList L, int e) {
    for (LNode *p = L->next; p != nullptr; p = p->next) {
        if (p->data == e) return p;
    }
    return nullptr;
}

// 遍历输出
void PrintList(LinkList L) {
    if (L->next == nullptr) {
        cout << "(空表)\n";
        return;
    }
    for (LNode *p = L->next; p != nullptr; p = p->next) {
        cout << p->data << (p->next == nullptr ? '\n' : ' ');
    }
}

// 清空并释放所有结点（含头结点），防止内存泄漏
void DestroyList(LinkList &L) {
    LNode *p = L;
    while (p != nullptr) {
        LNode *q = p->next;
        delete p;
        p = q;
    }
    L = nullptr;
}

int main() {
    LinkList L;
    int a[] = {1, 2, 3, 4, 5};
    CreateListTail(L, a, 5);
    cout << "尾插法：";
    PrintList(L);
    cout << "长度：" << Length(L) << "\n";

    ListInsert(L, 3, 99);
    cout << "第3位插入99：";
    PrintList(L);

    int deleted = 0;
    ListDelete(L, 1, deleted);
    cout << "删除第1个(" << deleted << ")：";
    PrintList(L);

    cout << "查找 99：" << (Locate(L, 99) ? "找到了" : "没有") << "\n";

    DestroyList(L);
    return 0;
}
