// 后缀表达式求值 —— 栈的经典应用
// 输入：一行，操作数和运算符用空格分隔，例如  5 1 2 + 4 * + 3 -
// 输出：整数结果
#include <iostream>
#include <sstream>
#include <string>
#include <stack>
using namespace std;

int main() {
    string line;
    getline(cin, line);
    istringstream iss(line);
    stack<long long> st;
    string token;

    while (iss >> token) {
        if (token == "+" || token == "-" || token == "*" || token == "/") {
            long long b = st.top(); st.pop();   // 先弹出的是右操作数
            long long a = st.top(); st.pop();
            if (token == "+") st.push(a + b);
            else if (token == "-") st.push(a - b);
            else if (token == "*") st.push(a * b);
            else st.push(a / b);
        } else {
            st.push(stoll(token));
        }
    }
    cout << st.top() << "\n";
    return 0;
}
