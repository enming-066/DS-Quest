// 最大连续子段和 —— 同一道题三种复杂度，对比最直观
// 编译：g++ -std=c++14 -o max_subarray max_subarray.cpp
#include <iostream>
using namespace std;

// ① 暴力枚举所有区间：O(n^3) —— 只用来理解题意
int BruteForce3(const int a[], int n) {
    int best = a[0];
    for (int i = 0; i < n; i++)
        for (int j = i; j < n; j++) {
            int sum = 0;
            for (int k = i; k <= j; k++) sum += a[k];
            if (sum > best) best = sum;
        }
    return best;
}

// ② 枚举起点、边扩展边求和：O(n^2)
int BruteForce2(const int a[], int n) {
    int best = a[0];
    for (int i = 0; i < n; i++) {
        int sum = 0;
        for (int j = i; j < n; j++) {
            sum += a[j];
            if (sum > best) best = sum;
        }
    }
    return best;
}

// ③ Kadane 算法：O(n)，一次扫描
// 思路：以 a[i] 结尾的最大子段和 = max(a[i], 以前一个结尾的最大和 + a[i])
int Kadane(const int a[], int n) {
    int best = a[0];
    int endingHere = a[0];
    for (int i = 1; i < n; i++) {
        endingHere = (endingHere > 0) ? endingHere + a[i] : a[i];
        if (endingHere > best) best = endingHere;
    }
    return best;
}

// ④ 分治：O(n log n)，课件第 0 章 P73 的 Algorithm 3
// 最大子段要么全在左半边、要么全在右半边、要么跨过中点
int MaxCrossing(const int a[], int left, int mid, int right) {
    int leftSum = -1000000000, sum = 0;
    for (int i = mid; i >= left; i--) {          // 从中点往左扫
        sum += a[i];
        if (sum > leftSum) leftSum = sum;
    }
    int rightSum = -1000000000;
    sum = 0;
    for (int i = mid + 1; i <= right; i++) {     // 从中点往右扫
        sum += a[i];
        if (sum > rightSum) rightSum = sum;
    }
    return leftSum + rightSum;
}

int DivideConquer(const int a[], int left, int right) {
    if (left == right) return a[left];           // 只剩一个元素
    int mid = (left + right) / 2;
    int bestLeft = DivideConquer(a, left, mid);
    int bestRight = DivideConquer(a, mid + 1, right);
    int bestCross = MaxCrossing(a, left, mid, right);
    int best = bestLeft > bestRight ? bestLeft : bestRight;
    return best > bestCross ? best : bestCross;
}

int main() {
    int a[] = {-2, 1, -3, 4, -1, 2, 1, -5, 4};
    int n = 9;
    cout << "O(n^3) ：" << BruteForce3(a, n) << "\n";
    cout << "O(n^2) ：" << BruteForce2(a, n) << "\n";
    cout << "O(nlogn)：" << DivideConquer(a, 0, n - 1) << "\n";
    cout << "O(n)   ：" << Kadane(a, n) << "\n";
    // 四者都应该是 6（子段 4 -1 2 1）

    int allNegative[] = {-5, -3, -9};
    cout << "全负数：" << Kadane(allNegative, 3) << "\n";   // -3
    return 0;
}
