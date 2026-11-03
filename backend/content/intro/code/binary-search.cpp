// 二分查找 —— O(log n) 的典型代表
// 编译：g++ -std=c++14 -o binary_search binary_search.cpp
#include <iostream>
using namespace std;

// 在有序数组 a[0..n-1] 中查找 target，返回下标，找不到返回 -1
int BinarySearch(const int a[], int n, int target) {
    int left = 0, right = n - 1;
    while (left <= right) {
        int mid = left + (right - left) / 2;   // 防止 left+right 溢出
        if (a[mid] == target) return mid;
        if (a[mid] < target) left = mid + 1;   // 去右半边
        else right = mid - 1;                  // 去左半边
    }
    return -1;
}

// 变体：找第一个 >= target 的位置（可用元素个数表示"没找到"）
int LowerBound(const int a[], int n, int target) {
    int left = 0, right = n;                   // 注意 right = n，表示"答案可能越界"
    while (left < right) {
        int mid = left + (right - left) / 2;
        if (a[mid] < target) left = mid + 1;
        else right = mid;
    }
    return left;                               // 返回 [0, n] 中的位置
}

int main() {
    int a[] = {1, 3, 5, 7, 9, 11, 13};
    int n = 7;

    cout << "查找 7：" << BinarySearch(a, n, 7) << "\n";       // 3
    cout << "查找 8：" << BinarySearch(a, n, 8) << "\n";       // -1

    cout << "第一个 >= 8 的位置：" << LowerBound(a, n, 8) << "\n";  // 4
    cout << "第一个 >= 0 的位置：" << LowerBound(a, n, 0) << "\n";  // 0
    cout << "第一个 >= 100 的位置：" << LowerBound(a, n, 100) << "\n"; // 7（越界，说明没有）
    return 0;
}
