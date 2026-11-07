"""填空判题的端到端检查：正确填空应 AC，错误填空应不通过，答案不能泄露。"""
import json
import urllib.request

BASE = "http://127.0.0.1:8000"


def get(path):
    with urllib.request.urlopen(BASE + path, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))


def post(path, payload):
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        BASE + path, data=data, headers={"Content-Type": "application/json"}, method="POST"
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode("utf-8"))


problem = get("/api/problems/ll-08")
print("type:", problem.get("type"))
print("blanks:", [(b["id"], b["placeholder"]) for b in problem.get("blanks", [])])
print("泄露答案？", any("answer" in b for b in problem.get("blanks", [])))
print("有 fillCode？", bool(problem.get("fillCode")))

good = {"1": "n + 1", "2": "a[j - 1]", "3": "pos - 1"}
res = post("/api/judge/fill", {"problemId": "ll-08", "answers": good})
print("正确填空 ->", res["verdict"], f"{res['passed']}/{res['total']}")

bad = {"1": "n", "2": "a[j]", "3": "pos"}
res2 = post("/api/judge/fill", {"problemId": "ll-08", "answers": bad})
print("错误填空 ->", res2["verdict"], f"{res2['passed']}/{res2['total']}")
print("有测试点对比：", bool(res2.get("firstFail", {}).get("expected")))

partial = {"1": "n + 1", "2": "a[j - 1]", "3": ""}
res3 = post("/api/judge/fill", {"problemId": "ll-08", "answers": partial})
print("漏填一个 ->", res3["verdict"])
