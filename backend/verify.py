"""内容自检脚本：python backend/verify.py

它做三件事：
1. 用每道题自带的参考解（solution）真的编译、运行，逐个测试点比对标准输出。
   —— 这保证题目数据不会自相矛盾，也不会出现"参考解都过不了"的题。
2. 检查内容字段是否齐全（标题、提示、知识点引用……）。
3. 把代码库里的所有模板编译一遍，保证贴给学生的代码是能编译的。

改完内容之后跑一下，全绿再提交。
"""

from __future__ import annotations

import shutil
import sys
import traceback
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent
for extra in (BACKEND_DIR / "vendor", BACKEND_DIR):
    if str(extra) not in sys.path:
        sys.path.insert(0, str(extra))

from app import judge  # noqa: E402
from app.content import library  # noqa: E402

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def ok(msg: str) -> None:
    print(f"{GREEN}  ✓ {msg}{RESET}")


def bad(msg: str) -> None:
    print(f"{RED}  ✗ {msg}{RESET}")


def warn(msg: str) -> None:
    print(f"{YELLOW}  ! {msg}{RESET}")


def verify_problems() -> int:
    failures = 0
    total_tests = 0
    for module in library.modules:
        for ref in module["problemRefs"]:
            problem = library.problem(ref["id"])
            pid = problem["id"]
            print(f"\n[{pid}] {problem['title']}  ({len(problem.get('tests', []))} 个测试点)")

            for field in ("statement", "inputFormat", "outputFormat", "hints", "solution", "starterCode"):
                if not problem.get(field):
                    bad(f"缺少字段 {field}")
                    failures += 1
            if len(problem.get("tests", [])) < 3:
                bad("测试点少于 3 个，覆盖不够")
                failures += 1
            for kid in problem.get("knowledgeIds", []):
                if not any(k["id"] == kid for k in module["knowledge"]):
                    warn(f"knowledgeIds 里的 {kid} 在本章找不到")

            solution = problem.get("solution", "")
            compiled = judge.compile_source(solution, "cpp")
            if not compiled.ok:
                bad("参考解编译失败：")
                for issue in compiled.issues[:4]:
                    print(f"      第{issue['line']}行 {issue['title']}: {issue['message']}")
                print(compiled.raw[:800])
                failures += 1
                continue

            mismatched = 0
            for index, case in enumerate(problem["tests"], start=1):
                total_tests += 1
                run = judge.run_program(
                    compiled.exe,
                    case.get("input", ""),
                    int(problem.get("timeLimitMs") or 2000),
                    int(problem.get("memoryLimitMb") or 256),
                )
                expected = case.get("output", "")
                if run.status != "ok":
                    bad(f"测试点 {index}（{case.get('name','')}）运行状态：{run.status}")
                    mismatched += 1
                elif judge.normalize(run.stdout) != judge.normalize(expected):
                    bad(f"测试点 {index}（{case.get('name','')}）输出不一致")
                    exp = judge.normalize(expected).splitlines()
                    act = judge.normalize(run.stdout).splitlines()
                    for i in range(max(len(exp), len(act))):
                        e = exp[i] if i < len(exp) else "<没有这一行>"
                        a = act[i] if i < len(act) else "<没有这一行>"
                        if e != a:
                            print(f"      第 {i+1} 行  期望：{e!r}")
                            print(f"              实际：{a!r}")
                            break
                    mismatched += 1
            if mismatched == 0:
                ok(f"{len(problem['tests'])} 个测试点全部通过")
            else:
                failures += 1
            if compiled.exe is not None:
                shutil.rmtree(compiled.exe.parent, ignore_errors=True)

    print(f"\n共 {total_tests} 个测试点")
    return failures


def verify_templates() -> int:
    failures = 0
    for module in library.modules:
        for tpl in module["templates"]:
            lang = tpl.get("lang", "cpp")
            compiled = judge.compile_source(tpl.get("code", ""), lang)
            label = f"[{module['id']}/{tpl['id']}] {tpl['title']}"
            if compiled.ok:
                ok(label)
            else:
                bad(f"{label} 编译失败")
                for issue in compiled.issues[:3]:
                    print(f"      第{issue['line']}行 {issue['title']}: {issue['message']}")
                failures += 1
            if compiled.exe is not None:
                shutil.rmtree(compiled.exe.parent, ignore_errors=True)
    return failures


def verify_links() -> int:
    """检查模板里引用的知识点 id 是否真实存在。"""
    failures = 0
    for module in library.modules:
        ids = {k["id"] for k in module["knowledge"]}
        for tpl in module["templates"]:
            for kid in tpl.get("relatedKnowledge", []):
                if kid not in ids:
                    warn(f"{module['id']}/{tpl['id']} 引用了不存在的知识点 {kid}")
                    failures += 1
        # 模板里的 anchor 必须真的能在代码里找到，否则前端高亮会失效
        for tpl in module["templates"]:
            code = tpl.get("code", "")
            for exp in tpl.get("explanations", []):
                if exp.get("anchor") and exp["anchor"] not in code:
                    warn(f"{module['id']}/{tpl['id']} 的 anchor 找不到：{exp['anchor'][:40]}")
                    failures += 1
            for note in tpl.get("lineNotes", []):
                if note.get("anchor") and note["anchor"] not in code:
                    warn(f"{module['id']}/{tpl['id']} 的逐行注释 anchor 找不到：{note['anchor'][:40]}")
                    failures += 1
    return failures


def main() -> int:
    print("=" * 60)
    print("DS Quest 内容自检")
    print("=" * 60)

    failures = 0
    print("\n--- 题目与测试数据 ---")
    failures += verify_problems()
    print("\n--- 代码模板编译 ---")
    failures += verify_templates()
    print("\n--- 引用与高亮锚点 ---")
    failures += verify_links()

    print("\n" + "=" * 60)
    if failures == 0:
        print(f"{GREEN}全部通过，可以放心发布。{RESET}")
    else:
        print(f"{RED}有 {failures} 处问题需要修复。{RESET}")
    print("=" * 60)
    return 0 if failures == 0 else 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:  # noqa: BLE001
        traceback.print_exc()
        sys.exit(2)
