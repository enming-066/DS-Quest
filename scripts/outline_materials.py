"""把提取出来的 PPT 文本压成「每页标题 + 前几行」的大纲，方便快速通读全部课件。

用法：python scripts/outline_materials.py [提取目录]
输出：materials/outlines/*.md
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

PAGE_RE = re.compile(r"^## 第 (\d+) 页\s*$")

# 这些行是纯数字/符号，多半是插图里的残片，丢掉
NOISE = re.compile(r"^[\s\d\.\-—·、%()（）:：/|]+$")


def outline(path: Path, keep: int = 3) -> str:
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    out: list[str] = [f"# {path.stem}", ""]
    current: list[str] | None = None
    page_no = 0

    def flush() -> None:
        nonlocal current
        if current is None:
            return
        body = []
        for line in current:
            text = line.strip()
            if not text or NOISE.match(text):
                continue
            if text.startswith("[备注]"):
                continue
            body.append(text)
            if len(body) >= keep:
                break
        if body:
            out.append(f"P{page_no}: " + " / ".join(body))
        current = None

    for line in lines:
        match = PAGE_RE.match(line)
        if match:
            flush()
            page_no = int(match.group(1))
            current = []
            continue
        if current is not None:
            current.append(line)
    flush()
    return "\n".join(out) + "\n"


def main() -> int:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("materials/extracted")
    dst = Path("materials/outlines")
    dst.mkdir(parents=True, exist_ok=True)
    count = 0
    for path in sorted(src.glob("*.md")):
        text = outline(path)
        (dst / path.name).write_text(text, encoding="utf-8")
        count += 1
        print(f"[ok] {path.name}: {len(text.splitlines())} 行大纲")
    print(f"\n共 {count} 个文件 -> {dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
