/* 顺序栈（C 语言版）—— 实验报告可用
 * 编译：gcc -std=c11 -o seqstack seqstack.c
 */
#include <stdio.h>
#include <stdbool.h>

#define MAXSIZE 100

typedef struct {
    int data[MAXSIZE];
    int top;
} SqStack;

void InitStack(SqStack *S) { S->top = -1; }
bool StackEmpty(const SqStack *S) { return S->top == -1; }
bool StackFull(const SqStack *S) { return S->top == MAXSIZE - 1; }

bool Push(SqStack *S, int e) {
    if (StackFull(S)) return false;
    S->data[++S->top] = e;
    return true;
}

bool Pop(SqStack *S, int *e) {
    if (StackEmpty(S)) return false;
    *e = S->data[S->top--];
    return true;
}

bool GetTop(const SqStack *S, int *e) {
    if (StackEmpty(S)) return false;
    *e = S->data[S->top];
    return true;
}

int main(void) {
    SqStack S;
    int i, e;
    InitStack(&S);

    for (i = 1; i <= 5; i++) Push(&S, i * 10);

    if (GetTop(&S, &e)) printf("栈顶：%d\n", e);

    printf("出栈顺序：");
    while (Pop(&S, &e)) printf("%d ", e);
    printf("\n");

    printf("空栈出栈：%s\n", Pop(&S, &e) ? "成功" : "失败（下溢）");
    return 0;
}
