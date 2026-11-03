"""把 materials/ 里的 PPT / Word 转成纯文本，方便阅读和整理。

用法：
    python scripts/extract_materials.py [源目录] [输出目录]

默认读 数据结构/，写到 materials/extracted/。
不依赖 LibreOffice，直接用 python-pptx / python-docx 读压缩包里的 XML。
"""

from __future__ import annotations

import sys
from pathlib import Path

try:
    from pptx import Presentation
    from pptx.enum.shapes import MSO_SHAPE_TYPE
except ImportError:
    print("缺少 python-pptx，请先 pip install python-pptx")
    raise SystemExit(1)

try:
    import docx
except ImportError:
    docx = None


def iter_shapes(shapes):
    """递归展开组合形状。"""
    for shape in shapes:
        if shape.shape_type == MSO_SHAPE_TYPE.GROUP:
            yield from iter_shapes(shape.shapes)
        else:
            yield shape


def pptx_to_text(path: Path) -> str:
    prs = Presentation(str(path))
    out = [f"# {path.name}", ""]
    for index, slide in enumerate(prs.slides, start=1):
        out.append(f"\n## 第 {index} 页\n")
        for shape in iter_shapes(slide.shapes):
            if shape.has_text_frame:
                text = "\n".join(
                    para.text for para in shape.text_frame.paragraphs if para.text.strip()
                )
                if text.strip():
                    out.append(text.strip())
            if getattr(shape, "has_table", False) and shape.has_table:
                rows = []
                for row in shape.table.rows:
                    cells = [cell.text.strip().replace("\n", " ") for cell in row.cells]
                    rows.append(" | ".join(cells))
                if rows:
                    out.append("[表格]\n" + "\n".join(rows))
        # 备注页里可能有老师补充的说明
        if slide.has_notes_slide:
            notes = slide.notes_slide.notes_text_frame.text.strip()
            if notes:
                out.append(f"[备注] {notes}")
    return "\n\n".join(out)


def docx_to_text_fallback(path: Path) -> str:
    """python-docx 打不开时（有的老师文件里有坏的 rels），直接读 XML。"""
    import zipfile

    from lxml import etree

    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    with zipfile.ZipFile(path) as z:
        xml = z.read("word/document.xml")
    root = etree.fromstring(xml)
    out = [f"# {path.name}", ""]
    body = root.find("w:body", ns)
    if body is None:
        return "\n".join(out)

    for child in body:
        tag = etree.QName(child).localname
        if tag == "p":
            text = "".join(node.text or "" for node in child.iter() if etree.QName(node).localname == "t")
            if text.strip():
                out.append(text.strip())
        elif tag == "tbl":
            rows = []
            for tr in child.iter():
                if etree.QName(tr).localname != "tr":
                    continue
                cells = []
                for tc in tr:
                    if etree.QName(tc).localname != "tc":
                        continue
                    text = "".join(n.text or "" for n in tc.iter()
                                   if etree.QName(n).localname == "t")
                    cells.append(text.strip().replace("\n", " "))
                rows.append(" | ".join(cells))
            if rows:
                out.append("[表格]\n" + "\n".join(rows))
    return "\n\n".join(out)


def docx_to_text(path: Path) -> str:
    if docx is None:
        return f"# {path.name}\n（缺少 python-docx，跳过）"
    try:
        document = docx.Document(str(path))
    except Exception:  # noqa: BLE001
        return docx_to_text_fallback(path)
    out = [f"# {path.name}", ""]
    body = document.element.body
    for child in body.iterchildren():
        tag = child.tag.split("}")[-1]
        if tag == "p":
            text = "".join(node.text or "" for node in child.iter() if node.tag.endswith("}t"))
            if text.strip():
                out.append(text.strip())
        elif tag == "tbl":
            rows = []
            for tr in child.iterchildren():
                if not tr.tag.endswith("}tr"):
                    continue
                cells = []
                for tc in tr.iterchildren():
                    if tc.tag.endswith("}tc"):
                        text = "".join(n.text or "" for n in tc.iter() if n.tag.endswith("}t"))
                        cells.append(text.strip().replace("\n", " "))
                rows.append(" | ".join(cells))
            if rows:
                out.append("[表格]\n" + "\n".join(rows))
    return "\n\n".join(out)


def main() -> int:
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("数据结构")
    dst = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("materials/extracted")
    if not src.exists():
        print(f"找不到源目录：{src}")
        return 1
    dst.mkdir(parents=True, exist_ok=True)

    count = 0
    for path in sorted(src.rglob("*")):
        if path.suffix.lower() == ".pptx":
            try:
                text = pptx_to_text(path)
            except Exception as exc:  # noqa: BLE001
                print(f"[跳过] {path.name}: {exc}")
                continue
        elif path.suffix.lower() == ".docx":
            try:
                text = docx_to_text(path)
            except Exception as exc:  # noqa: BLE001
                print(f"[跳过] {path.name}: {exc}")
                continue
        else:
            continue

        target = dst / (path.stem + ".md")
        target.write_text(text, encoding="utf-8")
        count += 1
        print(f"[ok] {path.name} -> {target}  ({len(text)} 字符)")

    print(f"\n共处理 {count} 个文件，输出目录：{dst}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
