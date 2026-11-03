// 括号匹配 —— 栈最经典的应用
#include <iostream>
#include <string>
#include <stack>
using namespace std;

bool Match(const string &s) {
    stack<char> st;
    for (char c : s) {
        if (c == '(' || c == '[' || c == '{') {
            st.push(c);
        } else if (c == ')' || c == ']' || c == '}') {
            if (st.empty()) return false;            // 右括号多了
            char t = st.top();
            bool ok = (c == ')' && t == '(') ||
                      (c == ']' && t == '[') ||
                      (c == '}' && t == '{');
            if (!ok) return false;                   // 类型不匹配
            st.pop();
        }
    }
    return st.empty();                               // 左括号多了也不匹配
}

int main() {
    string s;
    while (cin >> s) {
        cout << (Match(s) ? "YES" : "NO") << "\n";
    }
    return 0;
}
