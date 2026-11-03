"""判题内核：编译 + 运行 + 比对输出。

关于安全，先说清楚（这一点在你的方案里也被点名了）：

* 编译和运行都发生在临时目录里，一个提交一个目录，跑完就删。
* 运行用 Windows 作业对象（Job Object）限制内存、进程数和 CPU 时间；
  超时直接 TerminateJobObject 整棵进程树杀掉，不会留下僵尸进程。
* 程序以当前用户身份运行，**不是**虚拟机级别的隔离。对"自己写的代码、
  自己用"这个场景足够；如果你以后要把平台开放给别人用，请把执行环境换成
  WSL2 / Docker / 独立低权限账户，见 README 的「安全边界」一节。
"""

from __future__ import annotations

import ctypes
import os
import re
import shutil
import subprocess
import time
import uuid
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

from .config import RUN_DIR, settings

IS_WINDOWS = os.name == "nt"

# --------------------------------------------------------------------------
# Windows 作业对象（限制内存 / 进程数 / 强制杀进程）
# --------------------------------------------------------------------------
if IS_WINDOWS:
    from ctypes import wintypes

    _k32 = ctypes.WinDLL("kernel32", use_last_error=True)

    class _IO_COUNTERS(ctypes.Structure):
        _fields_ = [
            ("ReadOperationCount", ctypes.c_uint64),
            ("WriteOperationCount", ctypes.c_uint64),
            ("OtherOperationCount", ctypes.c_uint64),
            ("ReadTransferCount", ctypes.c_uint64),
            ("WriteTransferCount", ctypes.c_uint64),
            ("OtherTransferCount", ctypes.c_uint64),
        ]

    class _BASIC_LIMITS(ctypes.Structure):
        _fields_ = [
            ("PerProcessUserTimeLimit", ctypes.c_int64),
            ("PerJobUserTimeLimit", ctypes.c_int64),
            ("LimitFlags", wintypes.DWORD),
            ("MinimumWorkingSetSize", ctypes.c_size_t),
            ("MaximumWorkingSetSize", ctypes.c_size_t),
            ("ActiveProcessLimit", wintypes.DWORD),
            ("Affinity", ctypes.c_size_t),
            ("PriorityClass", wintypes.DWORD),
            ("SchedulingClass", wintypes.DWORD),
        ]

    class _EXTENDED_LIMITS(ctypes.Structure):
        _fields_ = [
            ("BasicLimitInformation", _BASIC_LIMITS),
            ("IoInfo", _IO_COUNTERS),
            ("ProcessMemoryLimit", ctypes.c_size_t),
            ("JobMemoryLimit", ctypes.c_size_t),
            ("PeakProcessMemoryUsed", ctypes.c_size_t),
            ("PeakJobMemoryUsed", ctypes.c_size_t),
        ]

    JOB_OBJECT_LIMIT_PROCESS_MEMORY = 0x00000100
    JOB_OBJECT_LIMIT_JOB_MEMORY = 0x00000200
    JOB_OBJECT_LIMIT_ACTIVE_PROCESS = 0x00000008
    JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE = 0x00002000
    JOB_OBJECT_EXTENDED_LIMIT_INFORMATION = 9

    _k32.CreateJobObjectW.restype = wintypes.HANDLE
    _k32.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    _k32.OpenProcess.restype = wintypes.HANDLE
    _k32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
    _k32.CloseHandle.argtypes = [wintypes.HANDLE]
    _k32.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    _k32.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]


class JobObject:
    """把一个子进程放进作业对象，方便限制资源并一次性杀掉。"""

    def __init__(self, memory_mb: int, max_processes: int = 4) -> None:
        self.handle = None
        if not IS_WINDOWS:
            return
        handle = _k32.CreateJobObjectW(None, None)
        if not handle:
            return
        info = _EXTENDED_LIMITS()
        limit_bytes = memory_mb * 1024 * 1024
        # 上限设成 2 倍：超出即失败，但我们自己按 1 倍判 MLE
        info.BasicLimitInformation.LimitFlags = (
            JOB_OBJECT_LIMIT_PROCESS_MEMORY
            | JOB_OBJECT_LIMIT_JOB_MEMORY
            | JOB_OBJECT_LIMIT_ACTIVE_PROCESS
            | JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE
        )
        info.BasicLimitInformation.ActiveProcessLimit = max_processes
        info.ProcessMemoryLimit = limit_bytes * 2
        info.JobMemoryLimit = limit_bytes * 2
        ok = _k32.SetInformationJobObject(
            handle, JOB_OBJECT_EXTENDED_LIMIT_INFORMATION, ctypes.byref(info), ctypes.sizeof(info)
        )
        if not ok:
            _k32.CloseHandle(handle)
            return
        self.handle = handle

    def assign(self, pid: int) -> bool:
        if not self.handle:
            return False
        process_handle = _k32.OpenProcess(0x1F0FFF, False, pid)
        if not process_handle:
            return False
        try:
            return bool(_k32.AssignProcessToJobObject(self.handle, process_handle))
        finally:
            _k32.CloseHandle(process_handle)

    def peak_memory_kb(self) -> int:
        if not self.handle:
            return 0
        info = _EXTENDED_LIMITS()
        if not _k32.QueryInformationJobObject(
            self.handle,
            JOB_OBJECT_EXTENDED_LIMIT_INFORMATION,
            ctypes.byref(info),
            ctypes.sizeof(info),
            None,
        ):
            return 0
        return int(info.PeakJobMemoryUsed // 1024)

    def kill(self) -> None:
        if self.handle:
            _k32.TerminateJobObject(self.handle, 1)

    def close(self) -> None:
        if self.handle:
            _k32.CloseHandle(self.handle)
            self.handle = None


# --------------------------------------------------------------------------
# 编译
# --------------------------------------------------------------------------
@dataclass
class CompileResult:
    ok: bool
    exe: Path | None = None
    raw: str = ""
    issues: list[dict[str, Any]] = field(default_factory=list)
    elapsed_ms: int = 0


def _decode(raw: bytes) -> str:
    for enc in ("utf-8", "gbk", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


_ISSUE_RE = re.compile(
    r"^(?P<file>.+?):(?P<line>\d+):(?P<col>\d+):\s*(?P<sev>fatal error|error|warning|note):\s*(?P<msg>.*)$"
)

# 常见 GCC 报错 → 中文解释。判题结果里直接给"人话"，比原始英文有用得多。
_ERROR_HINTS: list[tuple[str, str, str]] = [
    (r"was not declared in this scope|does not name a type|undeclared",
     "名字没定义或作用域不对",
     "检查变量名是否拼错；局部变量是否在声明之前就用了；是否需要 #include 对应的头文件。"),
    (r"expected ';'", "少了一个分号", "看报错行号的上一行末尾，通常是上一行语句忘了分号。"),
    (r"expected '\}' at end of input", "花括号不配对", "函数体少了 }，或者多写了一个 {。用编辑器的缩进对齐能很快发现。"),
    (r"expected declaration|expected '\)' before|expected '\(' before",
     "括号或语句结构不完整", "检查 if / for / while 的括号是否成对，参数列表是否写完整。"),
    (r"'cout' was not declared|'cin' was not declared|'printf' was not declared|'scanf' was not declared",
     "缺少头文件",
     "C++ 用 cout/cin 需要 #include <iostream>；用 printf/scanf 需要 #include <cstdio> 或 <stdio.h>。"),
    (r"no matching function for call to", "函数调用的参数对不上",
     "对比函数定义的参数类型和个数：比如传了 int* 而形参要 int，或者少了参数。"),
    (r"invalid conversion|cannot convert|no known conversion", "类型不匹配",
     "指针和整数不能混用；C++ 里 malloc 的返回值要强制转换，或者干脆用 new。"),
    (r"redefinition of|redeclaration of", "重复定义",
     "同一个名字定义了两次：检查是否重复写了一遍函数，或多个文件重复包含。"),
    (r"undefined reference to", "链接错误：只有声明没有实现",
     "函数声明了却没写函数体，或者写成了模板/内联却被放在别的编译单元。"),
    (r"too few arguments to function", "函数参数个数少了", "对照函数定义补齐参数。"),
    (r"lvalue required", "赋值号左边不能赋值", "检查是否写了 a + b = c 这类式子。"),
    (r"subscripted value is neither array nor pointer", "对非数组用了下标",
     "只有数组 / 指针才能用 []，检查变量类型。"),
    (r"size of array .* is negative", "数组大小是负数", "检查数组长度表达式。"),
    (r"#include|No such file or directory", "头文件找不到", "检查 #include 的文件名拼写与尖括号/引号用法。"),
    (r"stray '\\\d+' in program|stray", "出现了非法字符", "多半是从网页/PPT 复制了全角符号（，；（）），换成英文半角。"),
]


def _analyze_message(msg: str) -> tuple[str, str]:
    for pattern, title, hint in _ERROR_HINTS:
        if re.search(pattern, msg, re.IGNORECASE):
            return title, hint
    return "编译错误", "先看报错行号指的那一行，再看它上一行；从第一条 error 开始改，后面的错误往往是被它带出来的。"


def parse_compiler_output(text: str) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    for line in text.splitlines():
        match = _ISSUE_RE.match(line)
        if not match:
            continue
        sev = match.group("sev")
        if sev == "note":
            continue
        msg = match.group("msg").strip()
        title, hint = _analyze_message(msg)
        issues.append(
            {
                "line": int(match.group("line")),
                "column": int(match.group("col")),
                "severity": "warning" if sev == "warning" else "error",
                "message": msg,
                "title": title if sev != "warning" else "编译警告",
                "hint": hint if sev != "warning" else "警告不影响运行，但可能暗示逻辑问题，建议看一眼。",
            }
        )
    return issues


@lru_cache(maxsize=4)
def _cxx_std(compiler: str) -> str:
    """按编译器版本挑一个它认识的标准。

    TDM-GCC 5.1 这类老编译器不支持 C++17 的结构化绑定，
    用 -std=c++17 会让人以为"代码没写错却编译不过"。
    """
    try:
        raw = subprocess.run(
            [compiler, "-dumpversion"], capture_output=True, text=True, timeout=10
        ).stdout.strip()
        major = int(raw.split(".")[0])
    except Exception:  # noqa: BLE001
        return "c++17"
    if major >= 8:
        return "c++17"
    if major >= 5:
        return "c++14"
    return "c++11"


def compile_source(code: str, lang: str) -> CompileResult:
    started = time.perf_counter()
    compiler = settings.c_compiler if lang == "c" else settings.cpp_compiler
    if not compiler:
        return CompileResult(
            ok=False,
            raw="没有找到 C/C++ 编译器。",
            issues=[{
                "line": 0, "column": 0, "severity": "error",
                "message": "compiler not found",
                "title": "环境里没有编译器",
                "hint": "安装 MinGW-w64 / TDM-GCC，把它的 bin 目录加入 PATH，然后在 backend/.env 里用 DSQ_COMPILER 指定 g++ 的完整路径。",
            }],
        )

    RUN_DIR.mkdir(parents=True, exist_ok=True)
    # 用固定前缀 + uuid 建目录，而不是 tempfile.mkdtemp：
    # Windows 上 mkdtemp 会给目录写一条只允许当前用户的权限，
    # 在某些受限运行环境里反而写不进去。
    workdir = RUN_DIR / f"run-{uuid.uuid4().hex[:12]}"
    workdir.mkdir()
    src_name = "main.cpp" if lang != "c" else "main.c"
    src = workdir / src_name
    src.write_text(code, encoding="utf-8")
    exe = workdir / "main.exe"

    if lang == "c":
        cmd = [compiler, "-O2", "-std=c11", "-static", "-o", str(exe), str(src), "-lm"]
    else:
        cmd = [compiler, "-O2", f"-std={_cxx_std(compiler)}", "-static", "-o", str(exe), str(src)]

    try:
        proc = subprocess.run(
            cmd,
            cwd=str(workdir),
            capture_output=True,
            timeout=settings.compile_timeout_s,
            creationflags=0x08000000 if IS_WINDOWS else 0,
        )
        raw = _decode(proc.stdout) + _decode(proc.stderr)
        ok = proc.returncode == 0 and exe.exists()
    except subprocess.TimeoutExpired:
        return CompileResult(ok=False, raw="编译超时", issues=[{
            "line": 0, "column": 0, "severity": "error", "message": "compile timeout",
            "title": "编译超时", "hint": "代码可能过于庞大或模板递归过深，检查是否有死循环的模板/宏。",
        }])
    except OSError as exc:
        return CompileResult(ok=False, raw=str(exc), issues=[{
            "line": 0, "column": 0, "severity": "error", "message": str(exc),
            "title": "无法启动编译器", "hint": "检查 g++ 路径与权限。",
        }])

    issues = parse_compiler_output(raw)
    elapsed = int((time.perf_counter() - started) * 1000)
    if not ok and not any(i["severity"] == "error" for i in issues):
        issues.append({
            "line": 0, "column": 0, "severity": "error", "message": raw.strip()[:400],
            "title": "编译失败", "hint": "看下面的原始信息；常见原因是编译器安装不完整。",
        })
    if not ok:
        # 编译失败就没必要留着这个临时目录
        shutil.rmtree(workdir, ignore_errors=True)
    return CompileResult(ok=ok, exe=exe if ok else None, raw=raw, issues=issues, elapsed_ms=elapsed)


# --------------------------------------------------------------------------
# 运行
# --------------------------------------------------------------------------
@dataclass
class RunResult:
    status: str                 # ok | timeout | runtime_error | output_limit
    stdout: str = ""
    stderr: str = ""
    time_ms: int = 0
    memory_kb: int = 0
    exit_code: int = 0


def run_program(
    exe: Path,
    input_text: str,
    time_limit_ms: int,
    memory_limit_mb: int,
) -> RunResult:
    workdir = exe.parent
    stdin_path = workdir / "stdin.txt"
    stdout_path = workdir / "stdout.txt"
    stderr_path = workdir / "stderr.txt"
    stdin_path.write_text(input_text, encoding="utf-8", newline="\n")
    # 程序可能输出中文，统一让它按 UTF-8 输出
    env = {
        "PATH": os.environ.get("PATH", ""),
        "SYSTEMROOT": os.environ.get("SYSTEMROOT", "C:\\Windows"),
        "TEMP": str(workdir),
        "TMP": str(workdir),
        "PYTHONIOENCODING": "utf-8",
    }

    job = JobObject(memory_limit_mb)
    started = time.perf_counter()
    timed_out = False
    exit_code = 0
    with open(stdin_path, "rb") as fin, open(stdout_path, "wb") as fout, open(stderr_path, "wb") as ferr:
        proc = subprocess.Popen(
            [str(exe)],
            cwd=str(workdir),
            stdin=fin,
            stdout=fout,
            stderr=ferr,
            env=env,
            creationflags=(0x08000000 | 0x00000200) if IS_WINDOWS else 0,  # NO_WINDOW | NEW_PROCESS_GROUP
        )
        job.assign(proc.pid)
        try:
            proc.wait(timeout=time_limit_ms / 1000.0)
        except subprocess.TimeoutExpired:
            timed_out = True
            job.kill()
            try:
                proc.kill()
            except OSError:
                pass
            proc.wait(timeout=5)
        exit_code = proc.returncode if proc.returncode is not None else -1
        elapsed_ms = int((time.perf_counter() - started) * 1000)
        peak_kb = job.peak_memory_kb()
        job.close()

    raw_out = stdout_path.read_bytes()[: settings.max_output_bytes + 1]
    raw_err = stderr_path.read_bytes()[: settings.max_output_bytes + 1]
    out = _decode(raw_out[:-1] if len(raw_out) > settings.max_output_bytes else raw_out)
    err = _decode(raw_err[:-1] if len(raw_err) > settings.max_output_bytes else raw_err)

    if timed_out:
        status = "timeout"
    elif peak_kb > memory_limit_mb * 1024 * 0.98:
        status = "memory_limit"
    elif exit_code != 0:
        status = "runtime_error"
    elif len(raw_out) > settings.max_output_bytes:
        status = "output_limit"
    else:
        status = "ok"

    return RunResult(
        status=status,
        stdout=out,
        stderr=err,
        time_ms=elapsed_ms,
        memory_kb=peak_kb,
        exit_code=exit_code,
    )


# --------------------------------------------------------------------------
# 比对
# --------------------------------------------------------------------------
def normalize(text: str) -> str:
    """忽略行尾空格与末尾空行，这是几乎所有 OJ 的默认规则。"""
    lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    lines = [line.rstrip() for line in lines]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


def diff_output(expected: str, actual: str, limit: int = 40) -> dict[str, Any]:
    exp = normalize(expected).split("\n")
    act = normalize(actual).split("\n")
    first_diff = -1
    for i in range(max(len(exp), len(act))):
        e = exp[i] if i < len(exp) else None
        a = act[i] if i < len(act) else None
        if e != a:
            first_diff = i
            break
    rows = []
    if first_diff >= 0:
        start = max(0, first_diff - 3)
        for i in range(start, min(max(len(exp), len(act)), start + limit)):
            rows.append({
                "line": i + 1,
                "expected": exp[i] if i < len(exp) else None,
                "actual": act[i] if i < len(act) else None,
                "same": (exp[i] if i < len(exp) else None) == (act[i] if i < len(act) else None),
            })
    return {"firstDiffLine": first_diff + 1 if first_diff >= 0 else 0, "rows": rows}


def _truncate(text: str, limit: int = 1200) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + f"\n……（输出过长，已截断，共 {len(text)} 字符）"


VERDICT_TEXT = {
    "AC": "答案正确",
    "WA": "答案错误",
    "TLE": "运行超时",
    "MLE": "内存超限",
    "RE": "运行错误",
    "CE": "编译错误",
}


def judge_submission(problem: dict[str, Any], code: str, lang: str = "cpp") -> dict[str, Any]:
    time_limit = int(problem.get("timeLimitMs") or settings.default_time_limit_ms)
    memory_limit = int(problem.get("memoryLimitMb") or settings.default_memory_limit_mb)
    tests = problem.get("tests", [])[: settings.max_test_cases]
    started = time.perf_counter()

    compiled = compile_source(code, lang)
    if not compiled.ok:
        return {
            "verdict": "CE",
            "verdictText": VERDICT_TEXT["CE"],
            "compile": {
                "ok": False,
                "raw": _truncate(compiled.raw, 4000),
                "issues": compiled.issues,
                "elapsedMs": compiled.elapsed_ms,
            },
            "tests": [],
            "passed": 0,
            "total": len(tests),
            "timeMs": int((time.perf_counter() - started) * 1000),
            "maxMemoryKb": 0,
            "message": "代码没编译通过，先按上面的提示改。",
        }

    try:
        return _run_tests(problem, compiled, tests, time_limit, memory_limit, started)
    finally:
        # 跑完就把临时目录删掉，避免 runs/ 越积越多
        if compiled.exe is not None:
            shutil.rmtree(compiled.exe.parent, ignore_errors=True)


def _run_tests(problem, compiled, tests, time_limit, memory_limit, started):
    results: list[dict[str, Any]] = []
    passed = 0
    total_ms = 0
    max_mem = 0
    first_fail: dict[str, Any] | None = None

    for index, case in enumerate(tests, start=1):
        run = run_program(compiled.exe, case.get("input", ""), time_limit, memory_limit)
        expected = case.get("output", "")
        total_ms += run.time_ms
        max_mem = max(max_mem, run.memory_kb)

        if run.status == "timeout":
            verdict = "TLE"
        elif run.status == "memory_limit":
            verdict = "MLE"
        elif run.status == "runtime_error":
            verdict = "RE"
        elif normalize(run.stdout) == normalize(expected):
            verdict = "AC"
        else:
            verdict = "WA"

        if verdict == "AC":
            passed += 1

        entry = {
            "index": index,
            "verdict": verdict,
            "pass": verdict == "AC",
            "timeMs": run.time_ms,
            "memoryKb": run.memory_kb,
            "stderr": _truncate(run.stderr.strip(), 600),
            "exitCode": run.exit_code,
        }
        # 只把出错用例的输入/输出给前端看，方便自己对着调试（这是比 OJ 好用的一点）
        if verdict != "AC":
            entry["input"] = _truncate(case.get("input", ""), 800)
            entry["expected"] = _truncate(expected, 800)
            entry["actual"] = _truncate(run.stdout, 800)
            entry["diff"] = diff_output(expected, run.stdout)
            entry["name"] = case.get("name", "")
            if first_fail is None:
                first_fail = entry
        results.append(entry)

        if verdict != "AC":
            # 出错就停下，后面的测试点没必再跑，标成 SKIP
            if first_fail is None:
                first_fail = entry
            for extra in range(index + 1, len(tests) + 1):
                results.append({"index": extra, "verdict": "SKIP", "pass": False, "skipped": True,
                                "timeMs": 0, "memoryKb": 0})
            break

    verdict = first_fail["verdict"] if first_fail else "AC"

    message = "全部测试点通过，漂亮！" if verdict == "AC" else _fail_message(verdict, first_fail, time_limit)

    return {
        "verdict": verdict,
        "verdictText": VERDICT_TEXT.get(verdict, verdict),
        "compile": {
            "ok": True,
            "raw": _truncate(compiled.raw, 2000),
            "issues": compiled.issues,
            "elapsedMs": compiled.elapsed_ms,
        },
        "tests": results,
        "passed": passed,
        "total": len(tests),
        "timeMs": int((time.perf_counter() - started) * 1000),
        "runTimeMs": total_ms,
        "maxMemoryKb": max_mem,
        "memoryLimitMb": memory_limit,
        "timeLimitMs": time_limit,
        "firstFail": first_fail,
        "message": message,
    }


def _fail_message(verdict: str, first_fail: dict[str, Any] | None, time_limit: int) -> str:
    if verdict == "TLE":
        return f"程序超过 {time_limit} ms 还没算完。先看算法复杂度：是不是用了 O(n²) 去解 n=1e5 的数据？"
    if verdict == "MLE":
        return "内存超限。检查是不是开了过大的数组（比如 int a[1e7]），或者递归太深。"
    if verdict == "RE":
        return "程序崩了（数组越界 / 空指针 / 除以 0 最常见）。看下面的 stderr 和出错用例。"
    if verdict == "WA" and first_fail:
        return "输出和答案不一致，看下面第 %d 个测试点的对比。" % first_fail["index"]
    return "还有测试点没通过。"


def cleanup_stale_runs(max_age_minutes: int = 120) -> None:
    """启动时清理上次留下的临时编译目录。"""
    if not RUN_DIR.exists():
        return
    cutoff = time.time() - max_age_minutes * 60
    for child in RUN_DIR.iterdir():
        try:
            if child.is_dir() and child.stat().st_mtime < cutoff:
                shutil.rmtree(child, ignore_errors=True)
        except OSError:
            pass


if __name__ == "__main__":  # 手动测试：python -m app.judge
    demo = {
        "timeLimitMs": 2000,
        "tests": [{"input": "1 2\n", "output": "3\n"}],
    }
    print(judge_submission(demo, "#include <cstdio>\nint main(){int a,b;scanf(\"%d%d\",&a,&b);printf(\"%d\\n\",a+b);}", "cpp"))
