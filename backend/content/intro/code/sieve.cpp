// 埃拉托斯特尼筛法 —— O(n log log n)，求 1..n 里所有素数
// 编译：g++ -std=c++14 -o sieve sieve.cpp
#include <iostream>
using namespace std;

const int MAXN = 1000005;
bool isComposite[MAXN];      // false 表示可能是素数
int primes[80000];           // 1e6 以内有 78498 个素数

int main() {
    int n = 100000;
    int cnt = 0;

    for (int i = 2; i <= n; i++) {
        if (!isComposite[i]) {
            primes[cnt++] = i;
            // 从 i*i 开始标记：更小的倍数已经被更小的素数筛过了
            if ((long long)i * i <= n) {
                for (long long j = (long long)i * i; j <= n; j += i) {
                    isComposite[j] = true;
                }
            }
        }
    }

    cout << "1.." << n << " 之间共有 " << cnt << " 个素数\n";
    cout << "前 10 个：";
    for (int i = 0; i < 10 && i < cnt; i++) cout << primes[i] << " ";
    cout << "\n";
    return 0;
}
