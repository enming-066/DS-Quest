/* 循环队列（C 语言版）—— 实验报告可用
 * 编译：gcc -std=c11 -o cirqueue cirqueue.c
 */
#include <stdio.h>
#include <stdbool.h>

#define MAXSIZE 8

typedef struct {
    int data[MAXSIZE];
    int front, rear;
} SqQueue;

void InitQueue(SqQueue *Q) { Q->front = Q->rear = 0; }
bool QueueEmpty(const SqQueue *Q) { return Q->front == Q->rear; }
bool QueueFull(const SqQueue *Q) { return (Q->rear + 1) % MAXSIZE == Q->front; }
int QueueLength(const SqQueue *Q) { return (Q->rear - Q->front + MAXSIZE) % MAXSIZE; }

bool EnQueue(SqQueue *Q, int e) {
    if (QueueFull(Q)) return false;
    Q->data[Q->rear] = e;
    Q->rear = (Q->rear + 1) % MAXSIZE;
    return true;
}

bool DeQueue(SqQueue *Q, int *e) {
    if (QueueEmpty(Q)) return false;
    *e = Q->data[Q->front];
    Q->front = (Q->front + 1) % MAXSIZE;
    return true;
}

void PrintQueue(const SqQueue *Q) {
    int i;
    bool first = true;
    printf("[");
    for (i = Q->front; i != Q->rear; i = (i + 1) % MAXSIZE) {
        printf("%s%d", first ? "" : " ", Q->data[i]);
        first = false;
    }
    printf("] length=%d\n", QueueLength(Q));
}

int main(void) {
    SqQueue Q;
    int i, e;
    InitQueue(&Q);

    for (i = 1; i <= 6; i++) {
        printf("入队 %d -> %s\n", i, EnQueue(&Q, i) ? "成功" : "失败（队满）");
    }
    PrintQueue(&Q);

    DeQueue(&Q, &e);
    DeQueue(&Q, &e);
    printf("出队两个后：");
    PrintQueue(&Q);

    printf("再入队 7：%s\n", EnQueue(&Q, 7) ? "成功" : "失败");
    PrintQueue(&Q);
    return 0;
}
