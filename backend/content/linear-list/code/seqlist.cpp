// 顺序表（C++ 版）—— 课堂/考试标准写法
// 编译：g++ -std=c++17 -o seqlist seqlist.cpp
#include <iostream>
using namespace std;

#define MAXSIZE 100

typedef struct {
    int data[MAXSIZE];
    int length;
} SqList;

// 初始化：把长度置 0
void InitList(SqList &L) {
    L.length = 0;
}

// 求表长
int Length(const SqList &L) {
    return L.length;
}

// 按位取值：位序 i 从 1 开始，返回第 i 个元素，失败返回 false
bool GetElem(const SqList &L, int i, int &e) {
    if (i < 1 || i > L.length) return false;
    e = L.data[i - 1];
    return true;
}

// 按值查找：返回位序，找不到返回 0
int LocateElem(const SqList &L, int e) {
    for (int i = 0; i < L.length; i++) {
        if (L.data[i] == e) return i + 1;
    }
    return 0;
}

// 在第 i 个位置插入 e：1 <= i <= length+1
bool ListInsert(SqList &L, int i, int e) {
    if (i < 1 || i > L.length + 1) return false;
    if (L.length >= MAXSIZE) return false;
    for (int j = L.length; j >= i; j--) {   // 从后往前挪
        L.data[j] = L.data[j - 1];
    }
    L.data[i - 1] = e;
    L.length++;
    return true;
}

// 删除第 i 个元素，用 e 带回被删的值
bool ListDelete(SqList &L, int i, int &e) {
    if (i < 1 || i > L.length) return false;
    e = L.data[i - 1];
    for (int j = i; j < L.length; j++) {    // 从前往后挪
        L.data[j - 1] = L.data[j];
    }
    L.length--;
    return true;
}

// 遍历输出
void PrintList(const SqList &L) {
    for (int i = 0; i < L.length; i++) {
        cout << L.data[i] << (i + 1 == L.length ? '\n' : ' ');
    }
    if (L.length == 0) cout << "(空表)\n";
}

int main() {
    SqList L;
    InitList(L);

    int a[] = {10, 20, 30, 40, 50};
    for (int i = 0; i < 5; i++) ListInsert(L, L.length + 1, a[i]);
    cout << "初始：";
    PrintList(L);

    ListInsert(L, 3, 99);          // 第 3 个位置插入 99
    cout << "第3位插入99：";
    PrintList(L);

    int deleted = 0;
    ListDelete(L, 1, deleted);     // 删除第 1 个
    cout << "删除第1个(" << deleted << ")：";
    PrintList(L);

    cout << "表长：" << Length(L) << "，30 的位置：" << LocateElem(L, 30) << "\n";
    return 0;
}
