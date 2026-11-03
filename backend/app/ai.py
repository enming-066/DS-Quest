"""DeepSeek AI 助教（被动调用）。

省钱的三条原则：
1. **只有你点按钮才会调用**：打开页面、切换知识点、运行代码都不会消耗额度。
2. **能本地算的绝不用 API**：分层提示的第 1、2 层和"参考代码"直接来自题库内容，
   静态检查（格式串、数组大小、输出行数）也是本地规则，0 成本。
3. **缓存 + 每日上限**：同样的代码问同一个问题会直接命中缓存，每天最多 N 次调用。

Key 只放在后端环境变量里，前端永远拿不到。
"""

from __future__ import annotations

import hashlib
import json
import re
import urllib.error
import urllib.request
from typing import Any

from . import store
from .config import settings

SYSTEM_PROMPT = """你是一名数据结构课程的助教，学生在做编程练习题时卡住了。

你的原则：
1. 用中文回答，语气像一个耐心的师兄，不要客套话，直接讲重点。
2. 学生要的是"想明白"，不是"抄答案"。除非学生明确要求参考代码，否则绝不要输出完整可运行的程序。
3. 先判断他代码里的问题，再解释背后的数据结构原理。
4. 指出问题时必须引用具体变量名或具体代码片段，不要泛泛而谈。
5. 如果信息不足（比如看不到具体错误输出），先说明你的推测，并告诉学生还需要检查什么。
6. 控制在 350 字以内，多用短句和分点。

回答一律使用下面的三段式 Markdown，不要加别的一级标题：

### 我的判断
（一到两句话，指出最可能的问题）

### 你应该先检查
- （可执行的检查项，2~4 条）

### 原理提示
（把这个问题和数据结构课上的概念联系起来，1~3 句）"""


def _problem_brief(problem: dict[str, Any]) -> str:
    parts = [
        f"题目：{problem.get('title', '')}",
        f"题目描述：{problem.get('statement', '')}",
        f"输入格式：{problem.get('inputFormat', '')}",
        f"输出格式：{problem.get('outputFormat', '')}",
    ]
    if problem.get("constraints"):
        parts.append(f"数据范围：{problem['constraints']}")
    return "\n".join(parts)


def _failure_brief(result: dict[str, Any] | None) -> str:
    if not result:
        return "（学生还没提交）"
    lines = [f"判题结果：{result.get('verdict')}（{result.get('verdictText', '')}）"]
    if result.get("message"):
        lines.append(f"系统提示：{result['message']}")
    for issue in (result.get("compile", {}) or {}).get("issues", [])[:5]:
        lines.append(f"编译信息 第{issue.get('line')}行：{issue.get('message')}")
    fail = result.get("firstFail")
    if fail:
        lines.append(f"出错的测试点 #{fail.get('index')}")
        if fail.get("input"):
            lines.append(f"该点输入：\n{fail['input'][:400]}")
        if fail.get("expected"):
            lines.append(f"期望输出：\n{fail['expected'][:400]}")
        if fail.get("actual"):
            lines.append(f"实际输出：\n{fail['actual'][:400]}")
        if fail.get("stderr"):
            lines.append(f"stderr：\n{fail['stderr'][:300]}")
    return "\n".join(lines)


LEVEL_INSTRUCTIONS = {
    2: "学生只想要一个方向。**不要**指出具体哪一行、也不要给修改方案，只用提问的方式引导他自查。",
    3: "学生已经自己试过了，请明确指出问题所在（引用变量名/代码片段），解释原因，但**不要**给出完整代码。",
    4: "学生明确要求了参考解法。给出思路 + 关键代码片段（不超过 15 行），并说明为什么这样写。仍然不要贴完整 AC 程序。",
}


def local_hints(problem: dict[str, Any], verdict: str | None) -> list[str]:
    """题库自带的免费分层提示（第 1 层）。"""
    hints = problem.get("hints") or []
    return [str(h) for h in hints]


def static_review(code: str, verdict: str | None, result: dict[str, Any] | None,
                  problem: dict[str, Any]) -> list[dict[str, str]]:
    """本地静态检查，不花钱，覆盖学生最常犯的低级错误。"""
    notes: list[dict[str, str]] = []
    fail = (result or {}).get("firstFail") or {}

    # 1. 用 %d 读 long long
    if re.search(r"\blong\s+long\b", code) and re.search(r'scanf\s*\(\s*"%d', code):
        notes.append({
            "title": "格式符和类型不匹配",
            "detail": "代码里有 long long，但 scanf 用的是 %d。long long 必须用 %lld 读入，否则高位会被截断，大数据的测试点必挂。",
        })

    # 2. 用了 gets
    if re.search(r"\bgets\s*\(", code):
        notes.append({
            "title": "gets 已经不安全",
            "detail": "gets 不检查长度，容易越界。C 用 fgets(buf, sizeof(buf), stdin)，C++ 用 getline(cin, s)。",
        })

    # 3. 固定大小数组 vs 题目数据范围
    max_n = problem.get("maxN")
    sizes = [int(m) for m in re.findall(r"\[\s*(\d{2,9})\s*\]", code)]
    if max_n and sizes and max(sizes) < max_n:
        notes.append({
            "title": "数组可能开小了",
            "detail": f"题目数据范围到 {max_n}，但代码里最大的数组只有 {max(sizes)}。建议开到 max_n + 5。",
        })

    # 4. 完全没输出
    if verdict == "WA" and fail and not (fail.get("actual") or "").strip():
        notes.append({
            "title": "程序没有任何输出",
            "detail": "输出是空的。检查是否所有分支都有输出；是不是在 return 之前就退出了；输出语句是否被 if 包住了。",
        })

    # 5. 行数不一致
    if verdict == "WA" and fail:
        exp_lines = len((fail.get("expected") or "").strip().splitlines())
        act_lines = len((fail.get("actual") or "").strip().splitlines())
        if abs(exp_lines - act_lines) >= 1 and (fail.get("actual") or "").strip():
            direction = "少" if act_lines < exp_lines else "多"
            notes.append({
                "title": f"输出行数{direction}了",
                "detail": f"标准答案 {exp_lines} 行，你的程序 {act_lines} 行。常见原因：循环边界差一（< 写成 <=）、每组数据后多/少一个换行、漏了最后一项。",
            })

    # 6. TLE 且有两层循环
    if verdict == "TLE" and len(re.findall(r"\bfor\s*\(", code)) >= 2:
        notes.append({
            "title": "复杂度可能偏高",
            "detail": "代码里至少有两层 for 循环，如果是 O(n²) 而 n 到了 1e5，时间一定不够。看看能不能用二分、前缀和或者一次遍历解决。",
        })

    # 7. RE 常见原因
    if verdict == "RE":
        notes.append({
            "title": "运行时崩溃的排查顺序",
            "detail": "① 数组下标是否越界（尤其循环写成 i<=n 时）；② 递归有没有终止条件；③ 是否对空指针/空结构体取元素；④ 有没有除以 0。",
        })

    return notes


def _cache_key(problem_id: str, level: int, code: str, verdict: str | None, question: str) -> str:
    raw = json.dumps(
        {"p": problem_id, "l": level, "c": code, "v": verdict, "q": question, "m": settings.model},
        ensure_ascii=False,
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _call_deepseek(messages: list[dict[str, str]]) -> dict[str, Any]:
    url = f"{settings.api_base}/chat/completions"
    body = json.dumps(
        {
            "model": settings.model,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": settings.ai_max_tokens,
            "stream": False,
        },
        ensure_ascii=False,
    ).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {settings.api_key}",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=settings.ai_timeout_s) as response:
        payload = json.loads(response.read().decode("utf-8"))
    content = payload["choices"][0]["message"]["content"]
    usage = payload.get("usage", {})
    return {"content": content, "usage": usage}


def coach(
    problem: dict[str, Any],
    code: str,
    level: int,
    result: dict[str, Any] | None = None,
    question: str = "",
) -> dict[str, Any]:
    level = max(2, min(4, int(level)))
    problem_id = problem.get("id", "")
    verdict = (result or {}).get("verdict")

    # 第 4 层：题库里有参考解就直接给，不花钱
    if level == 4 and problem.get("solution"):
        return {
            "ok": True,
            "level": 4,
            "cached": True,
            "source": "local",
            "content": problem["solution"],
            "remaining": max(0, settings.ai_daily_limit - store.ai_usage_today()),
            "dailyLimit": settings.ai_daily_limit,
        }

    if not settings.ai_enabled:
        return {
            "ok": False,
            "error": "还没有配置 DeepSeek API Key。",
            "hint": "在 backend/.env 里填上 DEEPSEEK_API_KEY 再重启服务，就能使用 AI 分析。免费的分层提示和本地错因检查不受影响。",
            "remaining": 0,
            "dailyLimit": settings.ai_daily_limit,
        }

    key = _cache_key(problem_id, level, code, verdict, question)
    cached = store.ai_cache_get(key)
    if cached:
        cached["cached"] = True
        cached["remaining"] = max(0, settings.ai_daily_limit - store.ai_usage_today())
        return cached

    used = store.ai_usage_today()
    if used >= settings.ai_daily_limit:
        return {
            "ok": False,
            "error": f"今天的 AI 额度已用完（{used}/{settings.ai_daily_limit}）。",
            "hint": "明天自动重置；也可以在 backend/.env 里调大 DSQ_AI_DAILY_LIMIT。先用免费的分层提示和本地错因检查吧。",
            "remaining": 0,
            "dailyLimit": settings.ai_daily_limit,
        }

    user_prompt = "\n\n".join(
        [
            _problem_brief(problem),
            f"学生的代码（{problem.get('langHint', 'C++')}）：\n```\n{code[:6000]}\n```",
            "判题系统给出的结果：\n" + _failure_brief(result),
            LEVEL_INSTRUCTIONS[level],
        ]
    )
    if question.strip():
        user_prompt += f"\n\n学生补充的问题：{question.strip()[:500]}"

    try:
        reply = _call_deepseek(
            [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ]
        )
    except urllib.error.HTTPError as exc:
        detail = ""
        try:
            detail = exc.read().decode("utf-8", errors="replace")[:300]
        except Exception:  # noqa: BLE001
            pass
        return {
            "ok": False,
            "error": f"DeepSeek 接口返回 {exc.code}。",
            "hint": "401/402 一般是 Key 无效或余额不足；429 是请求太频繁；5xx 是官方服务波动，稍后再试。" + detail,
            "remaining": max(0, settings.ai_daily_limit - used),
            "dailyLimit": settings.ai_daily_limit,
        }
    except urllib.error.URLError as exc:
        return {
            "ok": False,
            "error": "连不上 DeepSeek 服务器。",
            "hint": f"{exc.reason}。检查网络/代理设置。",
            "remaining": max(0, settings.ai_daily_limit - used),
            "dailyLimit": settings.ai_daily_limit,
        }
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": "调用 AI 时发生未知错误。", "hint": str(exc)[:300]}

    calls = store.ai_usage_inc()
    payload = {
        "ok": True,
        "level": level,
        "cached": False,
        "source": "deepseek",
        "content": reply["content"],
        "usage": reply.get("usage", {}),
        "model": settings.model,
        "remaining": max(0, settings.ai_daily_limit - calls),
        "dailyLimit": settings.ai_daily_limit,
    }
    store.ai_cache_put(key, payload)
    return payload


def budget() -> dict[str, Any]:
    used = store.ai_usage_today()
    return {
        "enabled": settings.ai_enabled,
        "model": settings.model,
        "used": used,
        "limit": settings.ai_daily_limit,
        "remaining": max(0, settings.ai_daily_limit - used),
    }
