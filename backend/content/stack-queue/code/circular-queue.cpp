// 循环队列（C++ 版）—— 牺牲一个单元判满
#include <iostream>
using namespace std;

#define MAXSIZE 8

typedef struct {
    int data[MAXSIZE];
    int front, rear;   // rear 指向队尾元素的下一个位置
} SqQueue;

void InitQueue(SqQueue &Q) { Q.front = Q.rear = 0; }
bool QueueEmpty(const SqQueue &Q) { return Q.front == Q.rear; }
bool QueueFull(const SqQueue &Q) { return (Q.rear + 1) % MAXSIZE == Q.front; }
int QueueLength(const SqQueue &Q) { return (Q.rear - Q.front + MAXSIZE) % MAXSIZE; }

bool EnQueue(SqQueue &Q, int e) {
    if (QueueFull(Q)) return false;
    Q.data[Q.rear] = e;
    Q.rear = (Q.rear + 1) % MAXSIZE;
    return true;
}

bool DeQueue(SqQueue &Q, int &e) {
    if (QueueEmpty(Q)) return false;
    e = Q.data[Q.front];
    Q.front = (Q.front + 1) % MAXSIZE;
    return true;
}

bool GetHead(const SqQueue &Q, int &e) {
    if (QueueEmpty(Q)) return false;
    e = Q.data[Q.front];
    return true;
}

void PrintQueue(const SqQueue &Q) {
    cout << "[";
    bool first = true;
    for (int i = Q.front; i != Q.rear; i = (i + 1) % MAXSIZE) {
        if (!first) cout << " ";
        cout << Q.data[i];
        first = false;
    }
    cout << "] length=" << QueueLength(Q) << "\n";
}

int main() {
    SqQueue Q;
    InitQueue(Q);

    for (int i = 1; i <= 6; i++) {
        cout << "入队 " << i << " -> " << (EnQueue(Q, i) ? "成功" : "失败（队满）") << "\n";
    }
    PrintQueue(Q);

    int e;
    DeQueue(Q, e); DeQueue(Q, e);
    cout << "出队两个后：";
    PrintQueue(Q);

    cout << "再入队 7、8：";
    cout << (EnQueue(Q, 7) ? "7成功 " : "7失败 ");
    cout << (EnQueue(Q, 8) ? "8成功" : "8失败") << "\n";
    PrintQueue(Q);
    return 0;
}
