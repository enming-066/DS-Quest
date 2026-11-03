/* 单链表（C 语言版，带头结点）—— 实验报告可直接用
 * 编译：gcc -std=c11 -o linklist linklist.c
 */
#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

typedef struct LNode {
    int data;
    struct LNode *next;
} LNode, *LinkList;

/* 初始化：头结点不存数据 */
LinkList InitList(void) {
    LinkList L = (LinkList)malloc(sizeof(LNode));
    if (L != NULL) L->next = NULL;
    return L;
}

/* 尾插法建表 */
void CreateListTail(LinkList L, const int a[], int n) {
    LNode *r = L;                 /* r 指向表尾 */
    int i;
    for (i = 0; i < n; i++) {
        LNode *s = (LNode *)malloc(sizeof(LNode));
        s->data = a[i];
        s->next = NULL;
        r->next = s;
        r = s;
    }
}

/* 在第 i 个位置插入 e */
bool ListInsert(LinkList L, int i, int e) {
    LNode *p = L;
    int j = 0;
    LNode *s;
    if (i < 1) return false;
    while (p != NULL && j < i - 1) {   /* 找第 i-1 个结点 */
        p = p->next;
        j++;
    }
    if (p == NULL) return false;
    s = (LNode *)malloc(sizeof(LNode));
    s->data = e;
    s->next = p->next;                /* 先接后断 */
    p->next = s;
    return true;
}

/* 删除第 i 个元素 */
bool ListDelete(LinkList L, int i, int *e) {
    LNode *p = L, *q;
    int j = 0;
    if (i < 1) return false;
    while (p != NULL && j < i - 1) {
        p = p->next;
        j++;
    }
    if (p == NULL || p->next == NULL) return false;
    q = p->next;
    *e = q->data;
    p->next = q->next;
    free(q);                          /* C 用 free */
    return true;
}

/* 遍历输出 */
void PrintList(LinkList L) {
    LNode *p;
    if (L->next == NULL) {
        printf("(空表)\n");
        return;
    }
    for (p = L->next; p != NULL; p = p->next) {
        printf("%d%c", p->data, p->next == NULL ? '\n' : ' ');
    }
}

/* 释放整张表 */
void DestroyList(LinkList L) {
    LNode *p = L, *q;
    while (p != NULL) {
        q = p->next;
        free(p);
        p = q;
    }
}

int main(void) {
    int a[] = {1, 2, 3, 4, 5};
    int deleted = 0;
    LinkList L = InitList();
    if (L == NULL) {
        printf("内存分配失败\n");
        return 1;
    }

    CreateListTail(L, a, 5);
    printf("尾插法：");
    PrintList(L);

    ListInsert(L, 3, 99);
    printf("第3位插入99：");
    PrintList(L);

    ListDelete(L, 1, &deleted);
    printf("删除第1个(%d)：", deleted);
    PrintList(L);

    DestroyList(L);
    return 0;
}
