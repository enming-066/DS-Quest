/* 顺序表（C 语言版）—— 实验报告可直接用
 * 编译：gcc -std=c11 -o seqlist seqlist.c
 *
 * 注意 C 和 C++ 的三点区别：
 *   1. 没有引用 &，要修改表必须传指针 SqList *L，用 L-> 访问成员
 *   2. 用 malloc/free 而不是 new/delete
 *   3. 用 bool 需要 #include <stdbool.h>（或直接用 int 0/1）
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define MAXSIZE 100

typedef struct {
    int data[MAXSIZE];
    int length;
} SqList;

/* 初始化 */
void InitList(SqList *L) {
    L->length = 0;
}

/* 求表长 */
int Length(const SqList *L) {
    return L->length;
}

/* 按位取值：位序 i 从 1 开始 */
bool GetElem(const SqList *L, int i, int *e) {
    if (i < 1 || i > L->length) return false;
    *e = L->data[i - 1];
    return true;
}

/* 按值查找：返回位序，找不到返回 0 */
int LocateElem(const SqList *L, int e) {
    int i;
    for (i = 0; i < L->length; i++) {
        if (L->data[i] == e) return i + 1;
    }
    return 0;
}

/* 在第 i 个位置插入 e */
bool ListInsert(SqList *L, int i, int e) {
    int j;
    if (i < 1 || i > L->length + 1) return false;
    if (L->length >= MAXSIZE) return false;
    for (j = L->length; j >= i; j--) {
        L->data[j] = L->data[j - 1];   /* 从后往前挪 */
    }
    L->data[i - 1] = e;
    L->length++;
    return true;
}

/* 删除第 i 个元素 */
bool ListDelete(SqList *L, int i, int *e) {
    int j;
    if (i < 1 || i > L->length) return false;
    *e = L->data[i - 1];
    for (j = i; j < L->length; j++) {
        L->data[j - 1] = L->data[j];   /* 从前往后挪 */
    }
    L->length--;
    return true;
}

/* 遍历输出 */
void PrintList(const SqList *L) {
    int i;
    if (L->length == 0) {
        printf("(空表)\n");
        return;
    }
    for (i = 0; i < L->length; i++) {
        printf("%d%c", L->data[i], i + 1 == L->length ? '\n' : ' ');
    }
}

int main(void) {
    SqList L;
    int a[] = {10, 20, 30, 40, 50};
    int i, deleted = 0;

    InitList(&L);
    for (i = 0; i < 5; i++) ListInsert(&L, L.length + 1, a[i]);
    printf("初始：");
    PrintList(&L);

    ListInsert(&L, 3, 99);
    printf("第3位插入99：");
    PrintList(&L);

    ListDelete(&L, 1, &deleted);
    printf("删除第1个(%d)：", deleted);
    PrintList(&L);

    printf("表长：%d，30 的位置：%d\n", Length(&L), LocateElem(&L, 30));
    return 0;
}
