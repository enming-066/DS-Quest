// 多项式求值：鲁莽算法 vs Horner 算法 —— 课件第 0 章 P39~P40
// 编译：g++ -O2 -std=c++14 -o horner horner.cpp
//
// 多项式：a[n]x^n + a[n-1]x^(n-1) + ... + a[1]x + a[0]
// 鲁莽算法：每一项单独算 x^i，再乘系数相加 → 2n 次乘法
// Horner：从最高次开始，每次"乘 x 再加下一个系数" → n 次乘法
//
// 结果一样，但乘法次数差一倍。这就是"操作计数"能看出的差别。
#include <iostream>
using namespace std;

// 鲁莽算法：Θ(n^2) 次乘法（因为每次都重新算 x^i）
double naive(double a[], int n, double x) {
    double sum = 0;
    for (int i = 0; i <= n; i++) {
        double power = 1;                 // x^i
        for (int j = 0; j < i; j++) power *= x;   // 这里就是浪费
        sum += a[i] * power;
    }
    return sum;
}

// 改进版：递推计算 x^i，Θ(n) 次乘法
double better(double a[], int n, double x) {
    double sum = 0, power = 1;
    for (int i = 0; i <= n; i++) {
        sum += a[i] * power;
        power *= x;
    }
    return sum;
}

// Horner：从最高次开始 a[n]，每次 result = result * x + a[i]
// 只要 n 次乘法、n 次加法，而且不需要额外存储 x^i
double horner(double a[], int n, double x) {
    double result = a[n];
    for (int i = n - 1; i >= 0; i--) {
        result = result * x + a[i];
    }
    return result;
}

int main() {
    // 2x^3 - 3x^2 + 4x - 5，在 x = 3 处的值：54 - 27 + 12 - 5 = 34
    double a[] = {-5, 4, -3, 2};
    int n = 3;
    double x = 3;

    cout << "鲁莽算法：" << naive(a, n, x) << "\n";
    cout << "递推优化：" << better(a, n, x) << "\n";
    cout << "Horner  ：" << horner(a, n, x) << "\n";
    return 0;
}
