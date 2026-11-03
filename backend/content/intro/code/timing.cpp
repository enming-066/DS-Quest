// 实验报告用：用真实运行时间验证复杂度
// 编译：g++ -O2 -std=c++14 -o timing timing.cpp
//
// 这个程序让 O(n^2) 和 O(n log n) 跑同样的规模，
// 把 n 翻倍时耗时的变化打印出来——你会发现：
//   O(n)     耗时约 2 倍
//   O(n log n) 耗时约 2.1 倍
//   O(n^2)   耗时约 4 倍
// 这就是"看增长趋势"最直观的证据。
#include <iostream>
#include <algorithm>
#include <chrono>
#include <cstdlib>
using namespace std;
using namespace std::chrono;

// O(n^2)：冒泡排序
void BubbleSort(int a[], int n) {
    for (int i = 0; i < n - 1; i++) {
        bool swapped = false;
        for (int j = 0; j < n - 1 - i; j++) {
            if (a[j] > a[j + 1]) {
                swap(a[j], a[j + 1]);
                swapped = true;
            }
        }
        if (!swapped) break;   // 已经有序就提前结束（最好情况 O(n)）
    }
}

int main() {
    srand(12345);
    cout << "规模n\t冒泡O(n^2)\t快排O(nlogn)\n";

    for (int n = 1000; n <= 16000; n *= 2) {
        int *a = new int[n];
        int *b = new int[n];
        for (int i = 0; i < n; i++) a[i] = b[i] = rand() % 100000;

        auto t1 = high_resolution_clock::now();
        BubbleSort(a, n);
        auto t2 = high_resolution_clock::now();
        sort(b, b + n);              // STL 的 sort 是 O(n log n)
        auto t3 = high_resolution_clock::now();

        double ms1 = duration<double, milli>(t2 - t1).count();
        double ms2 = duration<double, milli>(t3 - t2).count();
        cout << n << "\t" << ms1 << "\t\t" << ms2 << "\n";

        delete[] a;
        delete[] b;
    }
    return 0;
}
