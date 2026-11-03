// 单向链表（链式描述）—— 与课件第 1 章 P26~P31 的写法一致
// 编译：g++ -O2 -std=c++14 -o chain chain.cpp
//
// 与数组描述的区别：
//   数组描述按下标随机访问 Θ(1)，插入删除要挪元素 Θ(n)；
//   链表描述按下标访问要"走"过去 Θ(n)，但拿到位置后插入删除只改指针 Θ(1)。
#include <iostream>
using namespace std;

template<class T> class Chain;      // 前向声明，下面 ChainNode 要把它设为友元

template<class T>
class ChainNode {
    friend class Chain<T>;          // 让 Chain 能直接访问 data / next
public:
    ChainNode(const T& theData, ChainNode<T>* theNext = 0)
        : data(theData), next(theNext) {}
private:
    T data;                  // 数据域
    ChainNode<T>* next;      // 链接域
};

template<class T>
class Chain {
public:
    Chain() { firstNode = 0; listSize = 0; }
    ~Chain();                        // 析构：逐个释放结点

    bool empty() const { return listSize == 0; }
    int size() const { return listSize; }

    // 按下标取元素：从头"走" theIndex 步，Θ(theIndex)
    T& get(int theIndex) const {
        ChainNode<T>* current = firstNode;
        for (int i = 0; i < theIndex; i++)
            current = current->next;
        return current->data;
    }

    // 按值查找：返回第一次出现的下标，找不到返回 -1，Θ(n)
    int indexOf(const T& theElement) const {
        ChainNode<T>* current = firstNode;
        int index = 0;
        while (current != 0 && current->data != theElement) {
            current = current->next;
            index++;
        }
        return current == 0 ? -1 : index;
    }

    // 删除下标为 theIndex 的结点
    // 关键是先找到它的前驱，再让前驱指向后继，最后 delete
    void erase(int theIndex) {
        ChainNode<T>* deleteNode;
        if (theIndex == 0) {                 // 删首结点：没有前驱，特判
            deleteNode = firstNode;
            firstNode = firstNode->next;
        } else {
            ChainNode<T>* p = firstNode;     // p 最终停在待删结点的前驱
            for (int i = 0; i < theIndex - 1; i++)
                p = p->next;
            deleteNode = p->next;
            p->next = p->next->next;         // 越过待删结点
        }
        listSize--;
        delete deleteNode;                   // 释放内存
    }

    // 在下标 theIndex 处插入
    void insert(int theIndex, const T& theElement) {
        if (theIndex < 0 || theIndex > listSize) {
            cout << "插入下标越界：" << theIndex << "\n";
            return;
        }
        if (theIndex == 0) {                 // 插在表头
            firstNode = new ChainNode<T>(theElement, firstNode);
        } else {
            ChainNode<T>* p = firstNode;
            for (int i = 0; i < theIndex - 1; i++)
                p = p->next;
            p->next = new ChainNode<T>(theElement, p->next);
        }
        listSize++;
    }

    void output(ostream& out) const {
        for (ChainNode<T>* p = firstNode; p != 0; p = p->next)
            out << p->data << (p->next == 0 ? "" : " ");
        out << "\n";
    }

private:
    ChainNode<T>* firstNode;   // 首结点指针
    int listSize;              // 元素个数
};

template<class T>
Chain<T>::~Chain() {
    ChainNode<T>* next;
    while (firstNode != 0) {
        next = firstNode->next;
        delete firstNode;
        firstNode = next;
    }
}

int main() {
    Chain<int> c;
    for (int i = 0; i < 5; i++) c.insert(c.size(), i + 1);   // 尾插 1..5
    cout << "初始：";
    c.output(cout);

    c.insert(2, 99);
    cout << "在下标2插入99：";
    c.output(cout);

    c.erase(0);
    cout << "删除下标0：";
    c.output(cout);

    cout << "99 的下标：" << c.indexOf(99) << "，size = " << c.size() << "\n";
    cout << "get(3) = " << c.get(3) << "\n";
    return 0;
}
