"""内容加载：把 backend/content 下的 Markdown / JSON 读成前端可以直接用的结构。

设计目标：内容与代码分离。以后要加章节、加题，只需要改 content 目录，
不用动 Python 代码。

目录约定
--------
content/modules.json                学习地图上的 8 个模块（含未开放的）
content/<module-id>/module.json     模块介绍、代码模板、练习题清单
content/<module-id>/knowledge/*.md  知识点（正文是 Markdown，方便以后从 PPT 抄）
content/<module-id>/problems/*.json 练习题（题目描述 + 测试数据 + 参考解）
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable

from .config import CONTENT_DIR


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _split_front_matter(text: str) -> tuple[dict[str, str], str]:
    """拆出 Markdown 顶部的 --- 元信息块，格式故意做得极简。"""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    raw_meta = text[3:end]
    body = text[end + 4 :].lstrip("\n")
    meta: dict[str, str] = {}
    for line in raw_meta.splitlines():
        if not line.strip() or line.strip().startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        meta[key.strip()] = value.strip()
    return meta, body


def _as_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value]
    if isinstance(value, str):
        return [part.strip() for part in value.split(",") if part.strip()]
    return [str(value)]


class ContentLibrary:
    def __init__(self, root: Path = CONTENT_DIR) -> None:
        self.root = root
        self.modules: list[dict[str, Any]] = []
        self.by_id: dict[str, dict[str, Any]] = {}
        self.problems: dict[str, dict[str, Any]] = {}
        self.load()

    # ------------------------------------------------------------------ load
    def load(self) -> None:
        self.modules = []
        self.by_id = {}
        self.problems = {}

        index_path = self.root / "modules.json"
        if not index_path.exists():
            raise RuntimeError(f"找不到内容索引：{index_path}")
        index = _read_json(index_path)

        for entry in index:
            module_id = entry["id"]
            module = dict(entry)
            module.update(self._load_module(module_id, entry))
            module["order"] = int(entry.get("order", 0))
            self.modules.append(module)
            self.by_id[module_id] = module

        self.modules.sort(key=lambda m: m["order"])

    def _load_module(self, module_id: str, entry: dict[str, Any]) -> dict[str, Any]:
        module_dir = self.root / module_id
        if not module_dir.exists():
            # 还没做内容的章节（地图上标成 locked），这里给出空结构，
            # 保证所有模块的字段形状一致
            return {
                "knowledge": [],
                "templates": [],
                "problemRefs": [],
                "problemCount": 0,
                "estimatedMinutes": 0,
                "goal": "",
                "intro": "",
            }

        meta_path = module_dir / "module.json"
        meta = _read_json(meta_path) if meta_path.exists() else {}

        knowledge = []
        knowledge_dir = module_dir / "knowledge"
        if knowledge_dir.exists():
            for path in sorted(knowledge_dir.glob("*.md")):
                front, body = _split_front_matter(path.read_text(encoding="utf-8"))
                knowledge.append(
                    {
                        "id": front.get("id") or path.stem,
                        "title": front.get("title", path.stem),
                        "summary": front.get("summary", ""),
                        "minutes": int(front.get("minutes", "10") or 10),
                        "tags": _as_list(front.get("tags")),
                        "exam": _as_list(front.get("exam")),
                        "file": path.name,
                        "body": body,
                    }
                )

        templates = []
        tpl_path = module_dir / "templates.json"
        if tpl_path.exists():
            templates = _read_json(tpl_path)
            for tpl in templates:
                # 代码正文放在独立的 .cpp/.c 文件里，json 只放说明，
                # 这样以后编辑器打开就能直接改代码，不用在 JSON 里转义换行。
                code_file = tpl.get("file")
                if code_file:
                    path = module_dir / code_file
                    tpl["code"] = path.read_text(encoding="utf-8") if path.exists() else ""
                tpl.setdefault("code", "")

        problem_refs = []
        problem_dir = module_dir / "problems"
        if problem_dir.exists():
            for path in sorted(problem_dir.glob("*.json")):
                problem = _read_json(path)
                problem.setdefault("moduleId", module_id)
                problem.setdefault("file", path.name)
                problem["tests"] = problem.get("tests", [])
                problem["samples"] = problem.get("samples", [])
                problem.setdefault("timeLimitMs", 0)
                self.problems[problem["id"]] = problem
                problem_refs.append(
                    {
                        "id": problem["id"],
                        "title": problem["title"],
                        "difficulty": int(problem.get("difficulty", 1)),
                        "tags": problem.get("tags", []),
                        "summary": problem.get("summary", ""),
                        "knowledgeIds": problem.get("knowledgeIds", []),
                        "optional": bool(problem.get("optional", False)),
                    }
                )

        return {
            "id": module_id,
            "title": meta.get("title", entry.get("title", module_id)),
            "goal": meta.get("goal", ""),
            "intro": meta.get("intro", ""),
            "knowledge": knowledge,
            "templates": templates,
            "problemRefs": problem_refs,
            "problemCount": len(problem_refs),
            "estimatedMinutes": sum(k["minutes"] for k in knowledge),
        }

    # --------------------------------------------------------------- querying
    def module(self, module_id: str) -> dict[str, Any] | None:
        return self.by_id.get(module_id)

    def problem(self, problem_id: str) -> dict[str, Any] | None:
        return self.problems.get(problem_id)

    def public_problem(self, problem_id: str) -> dict[str, Any] | None:
        """去掉隐藏测试点的完整题目（发给前端）。"""
        problem = self.problems.get(problem_id)
        if not problem:
            return None
        data = {k: v for k, v in problem.items() if k != "tests"}
        data["totalTests"] = len(problem.get("tests", []))
        return data

    def module_public(self, module_id: str) -> dict[str, Any] | None:
        module = self.by_id.get(module_id)
        if not module:
            return None
        data = {k: v for k, v in module.items() if k != "problems"}
        return data

    def all_problem_refs(self) -> Iterable[dict[str, Any]]:
        for module in self.modules:
            for ref in module["problemRefs"]:
                yield {**ref, "moduleId": module["id"], "moduleTitle": module["title"]}


library = ContentLibrary()
