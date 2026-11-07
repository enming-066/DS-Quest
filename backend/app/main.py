"""FastAPI 入口：把内容、判题、AI、学习记录四块拼起来。

启动：
    python backend/run.py            # 或者 scripts/start.ps1
接口文档：
    http://127.0.0.1:8000/docs
"""

from __future__ import annotations

import contextlib
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from . import ai, store
from .config import PROJECT_DIR, settings
from .content import library
from .judge import cleanup_stale_runs, judge_submission


@contextlib.asynccontextmanager
async def lifespan(_: FastAPI):
    store.init_db()
    # 启动时把上次残留的编译目录清干净（此时不会有判题在跑）
    cleanup_stale_runs(max_age_minutes=0)
    yield


app = FastAPI(title="DS Quest API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5173", "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

XP_KNOWLEDGE = 10
XP_PROBLEM_BASE = 20
XP_MODULE_CLEAR = 100


# --------------------------------------------------------------------- 模型
class JudgeRequest(BaseModel):
    problemId: str
    code: str = Field(min_length=1, max_length=200_000)
    lang: str = "cpp"


class CoachRequest(BaseModel):
    problemId: str
    code: str = ""
    level: int = 2
    question: str = ""
    verdict: str | None = None
    result: dict[str, Any] | None = None


class KnowledgeDone(BaseModel):
    moduleId: str
    knowledgeId: str


class ProblemDone(BaseModel):
    problemId: str


class NoteRequest(BaseModel):
    note: str = ""


# --------------------------------------------------------------------- 基础
@app.get("/api/health")
def health() -> dict[str, Any]:
    return {
        "ok": True,
        "compiler": settings.cpp_compiler or None,
        "cCompiler": settings.c_compiler or None,
        "ai": settings.ai_enabled,
        "modules": len(library.modules),
        "problems": len(library.problems),
    }


def _module_summary(module: dict[str, Any], progress: dict[str, Any]) -> dict[str, Any]:
    solved = set(progress.get("problemsSolved", []))
    read = set(progress.get("knowledgeRead", []))
    knowledge_total = len(module["knowledge"])
    knowledge_done = sum(1 for k in module["knowledge"] if f"{module['id']}/{k['id']}" in read)
    # 拓展题不计入章节进度（课件不要求，不应当影响「通关」判定）
    problem_ids = [p["id"] for p in module["problemRefs"] if not p.get("optional")]
    problem_done = sum(1 for pid in problem_ids if pid in solved)
    problem_total = len(problem_ids)
    units_total = knowledge_total + problem_total
    units_done = knowledge_done + problem_done
    percent = round(units_done / units_total * 100) if units_total else 0
    return {
        "id": module["id"],
        "order": module["order"],
        "title": module["title"],
        "subtitle": module.get("subtitle", ""),
        "description": module.get("description", ""),
        "icon": module.get("icon", "dot"),
        "color": module.get("color", "#6366f1"),
        "status": module.get("status", "open"),
        "estimatedMinutes": module["estimatedMinutes"],
        "knowledgeTotal": knowledge_total,
        "knowledgeDone": knowledge_done,
        "problemTotal": problem_total,
        "problemDone": problem_done,
        "percent": percent,
        "cleared": module["id"] in progress.get("moduleCleared", []),
    }


@app.get("/api/bootstrap")
def bootstrap() -> dict[str, Any]:
    progress = store.get_progress()
    modules = [_module_summary(m, progress) for m in library.modules]
    xp = int(progress.get("xp", 0))
    return {
        "modules": modules,
        "progress": progress,
        "level": 1 + xp // 200,
        "xpInLevel": xp % 200,
        "xpToNext": 200,
        "ai": ai.budget(),
        "compiler": {"cpp": bool(settings.cpp_compiler), "c": bool(settings.c_compiler)},
        "wrongCount": len([w for w in store.list_wrong() if not w["resolved"]]),
        "totalProblems": len(library.problems),
    }


@app.get("/api/guide")
def guide() -> dict[str, Any]:
    """C++ 语法路标 + 术语对照，供前端一次性加载。"""
    return {
        "cpp": library.guide.get("cpp", []),
        "terms": library.guide.get("terms", []),
    }


@app.get("/api/modules/{module_id}")
def get_module(module_id: str) -> dict[str, Any]:
    module = library.module_public(module_id)
    if not module:
        raise HTTPException(404, "章节不存在")
    progress = store.get_progress()
    solved = set(progress.get("problemsSolved", []))
    problem_refs = [
        {**ref, "solved": ref["id"] in solved} for ref in module["problemRefs"]
    ]
    return {**module, "problemRefs": problem_refs, "summary": _module_summary(library.module(module_id), progress)}


@app.get("/api/problems/{problem_id}")
def get_problem(problem_id: str) -> dict[str, Any]:
    problem = library.public_problem(problem_id)
    if not problem:
        raise HTTPException(404, "题目不存在")
    progress = store.get_progress()
    problem["solved"] = problem_id in progress.get("problemsSolved", [])
    problem["savedCode"] = store.last_code(problem_id)
    # 前端要展示"这题考的是哪个知识点"的跳转
    module = library.module(problem.get("moduleId", ""))
    if module:
        titles = {k["id"]: k["title"] for k in module["knowledge"]}
        problem["knowledgeRefs"] = [
            {"id": kid, "title": titles.get(kid, kid)} for kid in problem.get("knowledgeIds", [])
        ]
    return problem


# --------------------------------------------------------------------- 判题
def _award(problem: dict[str, Any], progress: dict[str, Any], result: dict[str, Any]) -> dict[str, Any]:
    """通过后加经验、清错题、判断整章是否通关。"""
    pid = problem["id"]
    gained = 0
    solved = set(progress.get("problemsSolved", []))
    if result["verdict"] == "AC" and pid not in solved:
        gained = XP_PROBLEM_BASE + int(problem.get("difficulty", 1)) * 10
        solved.add(pid)
        progress["problemsSolved"] = sorted(solved)
        store.resolve_wrong(pid)

        module = library.module(problem.get("moduleId", ""))
        if module and module["id"] not in progress.get("moduleCleared", []):
            all_ids = {p["id"] for p in module["problemRefs"] if not p.get("optional")}
            read = set(progress.get("knowledgeRead", []))
            all_read = all(f"{module['id']}/{k['id']}" in read for k in module["knowledge"])
            if all_ids and all_ids.issubset(solved) and all_read:
                progress.setdefault("moduleCleared", []).append(module["id"])
                gained += XP_MODULE_CLEAR

        progress["xp"] = int(progress.get("xp", 0)) + gained
        store.save_progress(progress)
    return {"xpGained": gained, "xp": int(progress.get("xp", 0))}


@app.post("/api/judge")
def do_judge(request: JudgeRequest) -> dict[str, Any]:
    problem = library.problem(request.problemId)
    if not problem:
        raise HTTPException(404, "题目不存在")
    lang = request.lang if request.lang in ("cpp", "c") else "cpp"
    result = judge_submission(problem, request.code, lang)

    submission_id = store.record_submission(
        problem["id"], lang, request.code, result["verdict"],
        result["passed"], result["total"], result["timeMs"],
    )
    result["submissionId"] = submission_id

    if result["verdict"] == "AC":
        progress = store.get_progress()
        result.update(_award(problem, progress, result))
    else:
        reason = (result.get("firstFail") or {}).get("verdict") or result["verdict"]
        store.touch_wrong(problem["id"], result["verdict"], str(reason))

    progress = store.get_progress()
    result["progress"] = {
        "xp": int(progress.get("xp", 0)),
        "solved": problem["id"] in progress.get("problemsSolved", []),
        "moduleCleared": problem.get("moduleId") in progress.get("moduleCleared", []),
    }
    # 免费的本土错因检查，前端可以直接展示，不消耗 API
    result["staticReview"] = ai.static_review(request.code, result["verdict"], result, problem)
    result["hints"] = ai.local_hints(problem, result["verdict"])
    return result


# ----------------------------------------------------------------------- AI
@app.get("/api/ai/budget")
def ai_budget() -> dict[str, Any]:
    return ai.budget()


@app.post("/api/ai/coach")
def ai_coach(request: CoachRequest) -> dict[str, Any]:
    problem = library.problem(request.problemId)
    if not problem:
        raise HTTPException(404, "题目不存在")
    payload = ai.coach(
        problem=problem,
        code=request.code,
        level=request.level,
        result=request.result,
        question=request.question,
    )
    payload["staticReview"] = ai.static_review(
        request.code, request.verdict, request.result, problem
    )
    return JSONResponse(payload)


# ------------------------------------------------------------------- 学习记录
@app.post("/api/progress/knowledge")
def mark_knowledge(body: KnowledgeDone) -> dict[str, Any]:
    progress = store.get_progress()
    key = f"{body.moduleId}/{body.knowledgeId}"
    read = set(progress.get("knowledgeRead", []))
    gained = 0
    if key not in read:
        read.add(key)
        progress["knowledgeRead"] = sorted(read)
        gained = XP_KNOWLEDGE
        progress["xp"] = int(progress.get("xp", 0)) + gained
        store.save_progress(progress)
    return {"xpGained": gained, "xp": int(progress.get("xp", 0)), "knowledgeRead": sorted(read)}


@app.post("/api/progress/problem")
def mark_problem(body: ProblemDone) -> dict[str, Any]:
    progress = store.get_progress()
    solved = set(progress.get("problemsSolved", []))
    if body.problemId not in solved:
        return {"ok": False, "message": "这题还没通过，不能手动标记。"}
    return {"ok": True, "solved": sorted(solved)}


@app.get("/api/progress")
def get_progress() -> dict[str, Any]:
    return store.get_progress()


@app.get("/api/wrongbook")
def wrongbook() -> dict[str, Any]:
    rows = store.list_wrong()
    problems = []
    for row in rows:
        ref = library.problem(row["problem_id"])
        if not ref:
            continue
        problems.append(
            {
                **row,
                "title": ref.get("title", row["problem_id"]),
                "difficulty": ref.get("difficulty", 1),
                "tags": ref.get("tags", []),
                "moduleId": ref.get("moduleId", ""),
            }
        )
    return {"items": problems, "unresolved": len([p for p in problems if not p["resolved"]])}


@app.post("/api/wrongbook/{problem_id}/note")
def wrong_note(problem_id: str, body: NoteRequest) -> dict[str, Any]:
    store.set_note(problem_id, body.note[:2000])
    return {"ok": True}


@app.post("/api/wrongbook/{problem_id}/resolve")
def wrong_resolve(problem_id: str) -> dict[str, Any]:
    store.resolve_wrong(problem_id)
    return {"ok": True}


@app.get("/api/stats")
def stats() -> dict[str, Any]:
    progress = store.get_progress()
    recent = store.recent_submissions(12)
    wrong = store.list_wrong()
    return {
        "xp": progress.get("xp", 0),
        "knowledgeRead": len(progress.get("knowledgeRead", [])),
        "problemsSolved": len(progress.get("problemsSolved", [])),
        "totalProblems": len(library.problems),
        "moduleCleared": progress.get("moduleCleared", []),
        "wrongTotal": len(wrong),
        "wrongOpen": len([w for w in wrong if not w["resolved"]]),
        "recent": recent,
        "ai": ai.budget(),
    }


# --------------------------------------------------------------- 静态前端
DIST = PROJECT_DIR / "frontend" / "dist"

if DIST.exists():
    app.mount("/assets", StaticFiles(directory=str(DIST / "assets")), name="assets")

    @app.get("/{full_path:path}")
    def spa(full_path: str):
        if full_path.startswith("api/"):
            raise HTTPException(404, "接口不存在")
        candidate = DIST / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        index = DIST / "index.html"
        if index.exists():
            return FileResponse(index)
        raise HTTPException(404, "前端还没构建：请先运行 pnpm build")

else:
    @app.get("/")
    def no_frontend() -> dict[str, Any]:
        return {
            "message": "后端已启动，但前端还没有构建。",
            "steps": [
                "cd frontend && pnpm install && pnpm build",
                "或者用 scripts/dev.ps1 同时启动前后端开发服务器（http://127.0.0.1:5173）",
            ],
            "docs": "/docs",
        }
