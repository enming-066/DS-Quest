"""端到端冒烟测试：直接打本机 8000 端口的接口，确认前后端链路是通的。

用法：python backend/smoke_test.py
"""

from __future__ import annotations

import json
import sys
import urllib.request

BASE = "http://127.0.0.1:8000"
ok_count = 0
fail_count = 0


def get(path: str):
    with urllib.request.urlopen(BASE + path, timeout=20) as r:
        return r.status, r.read().decode("utf-8")


def post(path: str, payload: dict):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        BASE + path, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.status, json.loads(r.read().decode("utf-8"))


def check(name: str, cond: bool, detail: str = "") -> None:
    global ok_count, fail_count
    if cond:
        ok_count += 1
        print(f"  OK   {name}")
    else:
        fail_count += 1
        print(f"  FAIL {name} {detail}")


def main() -> int:
    print("== 静态页面 ==")
    status, html = get("/")
    check("首页返回 HTML", status == 200 and "<div id=\"app\">" in html)
    check("静态资源可访问", "/assets/" in html)

    print("== 元数据 ==")
    status, raw = get("/api/bootstrap")
    boot = json.loads(raw)
    check("bootstrap", status == 200 and len(boot["modules"]) == 11, str(status))
    open_modules = [m for m in boot["modules"] if m["status"] == "open"]
    check("四个章节已开放", len(open_modules) == 4, str([m["id"] for m in open_modules]))

    for mid in ("intro", "linear-list", "stack-queue"):
        _, raw = get(f"/api/modules/{mid}")
        mod = json.loads(raw)
        check(f"{mid} 知识点/模板/题目", len(mod["knowledge"]) > 0 and
              len(mod["templates"]) > 0 and len(mod["problemRefs"]) > 0,
              f"k={len(mod['knowledge'])} t={len(mod['templates'])} p={len(mod['problemRefs'])}")
        check(f"{mid} 模板带代码", all(t["code"] for t in mod["templates"]))

    # 上机真题关卡只有题目，没有知识点和代码模板
    _, raw = get("/api/modules/exam-lab")
    exam = json.loads(raw)
    check("上机真题关卡有题目", len(exam["problemRefs"]) >= 6, str(len(exam["problemRefs"])))

    _, raw = get("/api/problems/ll-01")
    p = json.loads(raw)
    check("题目详情不含隐藏测试数据", "tests" not in p)
    check("题目带样例与提示", len(p["samples"]) > 0 and len(p["hints"]) > 0)

    print("== 判题 ==")
    good = (
        "#include <iostream>\nusing namespace std;\nint main(){int n;cin>>n;int a[105];"
        "for(int i=0;i<n;i++)cin>>a[i];int pos,x;cin>>pos>>x;"
        "if(pos<1||pos>n+1){cout<<\"error\\n\";return 0;}"
        "for(int j=n;j>=pos;j--)a[j]=a[j-1];a[pos-1]=x;n++;"
        "for(int i=0;i<n;i++)cout<<a[i]<<(i+1==n?'\\n':' ');return 0;}"
    )
    _, res = post("/api/judge", {"problemId": "ll-01", "code": good, "lang": "cpp"})
    check("正确代码 AC", res["verdict"] == "AC", res["verdict"])
    check("AC 有经验奖励", res.get("xpGained", 0) > 0, str(res.get("xpGained")))

    bad = "#include <iostream>\nint main(){int n;std::cin>>n;return 0;}"
    _, res2 = post("/api/judge", {"problemId": "ll-01", "code": bad, "lang": "cpp"})
    check("错误代码 WA", res2["verdict"] == "WA", res2["verdict"])
    check("失败时给出测试点对比", bool(res2.get("firstFail", {}).get("expected")))
    check("失败时记录错题", any(w["problem_id"] == "ll-01" for w in
                          json.loads(get("/api/wrongbook")[1])["items"]))

    ce = "#include <iostream>\nint main(){ int a = ; }"
    _, res3 = post("/api/judge", {"problemId": "ll-01", "code": ce, "lang": "cpp"})
    check("编译错误 CE", res3["verdict"] == "CE", res3["verdict"])
    check("CE 给中文解释", any(i["title"] for i in res3["compile"]["issues"]))

    print("== C 语言判题 ==")
    c_code = (
        "#include <stdio.h>\nint main(){int n,i,a[105],pos,x;scanf(\"%d\",&n);"
        "for(i=0;i<n;i++)scanf(\"%d\",&a[i]);scanf(\"%d%d\",&pos,&x);"
        "if(pos<1||pos>n+1){printf(\"error\\n\");return 0;}"
        "for(i=n;i>=pos;i--)a[i]=a[i-1];a[pos-1]=x;n++;"
        "for(i=0;i<n;i++)printf(\"%d%c\",a[i],i+1==n?'\\n':' ');return 0;}"
    )
    _, res4 = post("/api/judge", {"problemId": "ll-01", "code": c_code, "lang": "c"})
    check("C 代码也能 AC", res4["verdict"] == "AC", res4["verdict"])

    print("== 学习记录 ==")
    _, raw = get("/api/progress")
    prog = json.loads(raw)
    check("进度已保存", "ll-01" in prog["problemsSolved"], str(prog.get("problemsSolved")))
    _, res5 = post("/api/progress/knowledge", {"moduleId": "linear-list", "knowledgeId": "seqlist"})
    check("知识点打卡", res5["xpGained"] >= 0)
    _, raw = get("/api/stats")
    stats = json.loads(raw)
    check("统计接口", stats["problemsSolved"] >= 1 and stats["totalProblems"] == 24)

    print("== AI（未配置 Key 时应优雅降级） ==")
    _, res6 = post("/api/ai/coach", {"problemId": "ll-01", "code": good, "level": 2})
    check("未配置 Key 时返回提示而不是崩溃", res6.get("ok") is False and "API Key" in res6.get("error", ""),
          str(res6)[:120])
    _, raw = get("/api/ai/budget")
    budget = json.loads(raw)
    check("额度接口", "remaining" in budget and "limit" in budget)

    print()
    print(f"通过 {ok_count} 项，失败 {fail_count} 项")
    return 0 if fail_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
