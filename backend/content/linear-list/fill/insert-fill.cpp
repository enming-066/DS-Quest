// 填空练习：顺序表插入
// 把代码里标出来的空位补全，程序要通过所有测试点。
// 对应课件第 1 章 P15 的 insert 分析。
#include <iostream>
using namespace std;

int main() {
    int n;
    cin >> n;
    int a[1005];
    for (int i = 0; i < n; i++) cin >> a[i];

    int pos, x;
    cin >> pos >> x;

    // 合法的位序范围是 1 ~ n+1
    if (pos < 1 || pos > /*BLANK1*/) {
        cout << "error\n";
        return 0;
    }

    // 从后往前挪，给下标 pos-1 腾位置
    for (int j = n; j >= pos; j--) {
        a[j] = /*BLANK2*/;
    }

    // 把 x 放到第 pos 个位置（也就是下标 pos-1）
    a[/*BLANK3*/] = x;
    n++;

    for (int i = 0; i < n; i++)
        cout << a[i] << (i + 1 == n ? '\n' : ' ');
    return 0;
}
