// 顺序栈（C++ 版）—— top 指向栈顶元素，初始 -1
#include <iostream>
using namespace std;

#define MAXSIZE 100

typedef struct {
    int data[MAXSIZE];
    int top;
} SqStack;

void InitStack(SqStack &S) { S.top = -1; }
bool StackEmpty(const SqStack &S) { return S.top == -1; }
bool StackFull(const SqStack &S) { return S.top == MAXSIZE - 1; }
int StackLength(const SqStack &S) { return S.top + 1; }

bool Push(SqStack &S, int e) {
    if (StackFull(S)) return false;      // 上溢
    S.data[++S.top] = e;
    return true;
}

bool Pop(SqStack &S, int &e) {
    if (StackEmpty(S)) return false;     // 下溢
    e = S.data[S.top--];
    return true;
}

bool GetTop(const SqStack &S, int &e) {
    if (StackEmpty(S)) return false;
    e = S.data[S.top];
    return true;
}

// 把十进制转成 base 进制（用栈逆序输出）
void Convert(int n, int base) {
    SqStack S;
    InitStack(S);
    if (n == 0) { cout << "0"; return; }
    while (n > 0) {
        Push(S, n % base);
        n /= base;
    }
    int e;
    while (Pop(S, e)) {
        cout << "0123456789ABCDEF"[e];
    }
}

int main() {
    SqStack S;
    InitStack(S);

    for (int i = 1; i <= 5; i++) Push(S, i * 10);
    cout << "栈内元素个数：" << StackLength(S) << "，栈顶：";
    int top;
    GetTop(S, top);
    cout << top << "\n";

    cout << "出栈顺序：";
    int e;
    while (Pop(S, e)) cout << e << " ";
    cout << "\n";

    cout << "255 转 16 进制：";
    Convert(255, 16);
    cout << "\n";
    return 0;
}
