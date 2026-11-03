// 间接寻址（IndirectList）—— 课件第 1 章 P43~P51
// 编译：g++ -O2 -std=c++14 -o indirect indirect.cpp
//
// 思路：元素本身用 new 动态分配（和链表一样分散存放），
//       但把所有"指向元素的指针"集中放进一个数组 table[]（像目录）。
// 结果：定位是 Θ(1)，插入删除只需要移动指针，不用移动元素本身。
#include <iostream>
using namespace std;

template<class T>
class IndirectList {
public:
    IndirectList(int maxListSize = 10) {
        MaxSize = maxListSize > 0 ? maxListSize : 1;
        table = new T*[MaxSize];
        length = 0;
    }

    ~IndirectList() {
        for (int i = 0; i < length; i++) delete table[i];
        delete[] table;
    }

    bool isEmpty() const { return length == 0; }
    int size() const { return length; }

    // 取第 k 个元素（k 从 1 开始，与课本一致）：先查目录，再解引用
    bool find(int k, T& x) const {
        if (k < 1 || k > length) return false;
        x = *table[k - 1];
        return true;
    }

    // 按值查找，返回 1 基序号，找不到返回 0
    int search(const T& x) const {
        for (int i = 0; i < length; i++)
            if (*table[i] == x) return i + 1;
        return 0;
    }

    // 删除第 k 个元素：只把后面的指针往前挪一格，Θ(length - k)
    bool erase(int k, T& x) {
        if (!find(k, x)) return false;
        delete table[k - 1];
        for (int i = k; i < length; i++)
            table[i - 1] = table[i];
        length--;
        return true;
    }

    // 在第 k 个元素之后插入（k = 0 表示插在最前面）
    bool insert(int k, const T& x) {
        if (k < 0 || k > length) return false;
        if (length == MaxSize) return false;
        for (int i = length - 1; i >= k; i--)
            table[i + 1] = table[i];      // 指针后移，元素本身不动
        table[k] = new T(x);
        length++;
        return true;
    }

    void output(ostream& out) const {
        for (int i = 0; i < length; i++)
            out << *table[i] << (i + 1 == length ? "" : " ");
        out << "\n";
    }

private:
    T** table;     // 指针数组（目录）
    int length;    // 当前元素个数
    int MaxSize;   // 目录容量
};

int main() {
    IndirectList<int> L(10);
    for (int i = 1; i <= 5; i++) L.insert(L.size(), i * 10);
    cout << "初始：";
    L.output(cout);

    L.insert(0, 99);          // 插到最前面：只移动指针
    cout << "头部插入99：";
    L.output(cout);

    int deleted = 0;
    L.erase(3, deleted);      // 删除第 3 个（1 基）
    cout << "删除第3个元素(" << deleted << ")：";
    L.output(cout);

    int v = 0;
    L.find(2, v);
    cout << "第2个元素：" << v << "，查找 30 的位置：" << L.search(30) << "\n";
    return 0;
}
