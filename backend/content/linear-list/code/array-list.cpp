// 顺序表（数组描述）—— 与课件第 1 章 P13~P16 的写法一致
// 编译：g++ -O2 -std=c++14 -o array_list array_list.cpp
//
// 约定（很重要，和课本一致）：
//   insert(theIndex, x) 把 x 插到"下标恰好为 theIndex"的位置，
//   erase(theIndex) 删除下标为 theIndex 的元素，后面的元素整体前移。
//   下标从 0 开始，合法范围分别是 [0, listSize] 和 [0, listSize-1]。
#include <iostream>
using namespace std;

template<class T>
class ArrayLinearList {
public:
    ArrayLinearList(int initialCapacity = 10) {
        if (initialCapacity < 1) initialCapacity = 1;
        arrayLength = initialCapacity;
        element = new T[arrayLength];
        listSize = 0;
    }
    ~ArrayLinearList() { delete[] element; }

    bool empty() const { return listSize == 0; }
    int size() const { return listSize; }

    // 取下标为 theIndex 的元素，Θ(1)
    T& get(int theIndex) const {
        checkIndex(theIndex);
        return element[theIndex];
    }

    // 返回元素 x 第一次出现的下标，找不到返回 -1
    // 最好 Θ(1)，最坏 Θ(n)，平均 Θ(n)
    int indexOf(const T& theElement) const {
        for (int i = 0; i < listSize; i++)
            if (element[i] == theElement) return i;
        return -1;
    }

    // 删除下标为 theIndex 的元素：后面的元素依次前移
    // 最好（删最后一个）Θ(1)，最坏（删第一个）Θ(n)，平均 Θ(n)
    void erase(int theIndex) {
        checkIndex(theIndex);
        for (int i = theIndex; i < listSize - 1; i++)
            element[i] = element[i + 1];
        listSize--;
    }

    // 在下标 theIndex 处插入：从后往前把元素后移一格
    // 最好（插在末尾）Θ(1)，最坏（插在最前）Θ(n)，平均 Θ(n)
    void insert(int theIndex, const T& theElement) {
        if (theIndex < 0 || theIndex > listSize) {
            cout << "插入下标越界：" << theIndex << "\n";
            return;
        }
        if (listSize == arrayLength) {                 // 满了，容量翻倍
            changeLength1D(element, arrayLength, 2 * arrayLength);
            arrayLength *= 2;
        }
        for (int i = listSize - 1; i >= theIndex; i--) // 从后往前挪
            element[i + 1] = element[i];
        element[theIndex] = theElement;
        listSize++;
    }

    void output(ostream& out) const {
        for (int i = 0; i < listSize; i++)
            out << element[i] << (i + 1 == listSize ? "" : " ");
        out << "\n";
    }

private:
    void checkIndex(int theIndex) const {
        if (theIndex < 0 || theIndex >= listSize)
            cout << "下标越界：" << theIndex << "\n";
    }
    void changeLength1D(T*& a, int oldLength, int newLength) {
        T* temp = new T[newLength];
        int number = oldLength < newLength ? oldLength : newLength;
        for (int i = 0; i < number; i++) temp[i] = a[i];
        delete[] a;
        a = temp;
    }

    T* element;      // 元素数组
    int arrayLength; // 数组容量
    int listSize;    // 当前元素个数
};

int main() {
    ArrayLinearList<int> L(4);

    for (int i = 0; i < 5; i++) L.insert(L.size(), i * 10);  // 依次追加
    cout << "初始：";
    L.output(cout);

    L.insert(2, 99);                 // 插到下标 2
    cout << "在下标2插入99：";
    L.output(cout);

    L.erase(0);                      // 删除第一个
    cout << "删除下标0：";
    L.output(cout);

    cout << "99 的下标：" << L.indexOf(99) << "，size = " << L.size() << "\n";
    cout << "get(1) = " << L.get(1) << "\n";
    return 0;
}
