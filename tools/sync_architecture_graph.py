#!/usr/bin/env python3
"""Generate a Mermaid graph for imports between project-internal modules."""

from __future__ import annotations

import argparse
import ast
import hashlib
import re
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="同步 Markdown 文档中的项目内部模块依赖图。",
    )
    parser.add_argument(
        "--source",
        required=True,
        type=Path,
        help="要扫描的 Python 包目录。",
    )
    parser.add_argument(
        "--document",
        required=True,
        type=Path,
        help="包含目标 Mermaid 章节的 Markdown 文档。",
    )
    parser.add_argument(
        "--section",
        required=True,
        help="包含依赖图的 Markdown 标题，例如“### 项目内部模块依赖”。",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="只检查文档是否最新，不写入文件。",
    )
    return parser.parse_args()


def module_name(source: Path, path: Path) -> str:
    relative = path.relative_to(source).with_suffix("")
    parts = [source.name, *relative.parts]
    if parts[-1] == "__init__":
        parts.pop()
    return ".".join(parts)


def visible_label(source: Path, path: Path) -> str:
    return path.relative_to(source).as_posix()


def resolve_relative_import(
    current_module: str,
    is_package_init: bool,
    level: int,
    imported_module: str | None,
) -> str:
    if level == 0:
        return imported_module or ""

    current_package = (
        current_module
        if is_package_init
        else current_module.rsplit(".", maxsplit=1)[0]
    )
    package_parts = current_package.split(".")
    keep_count = len(package_parts) - (level - 1)
    base_parts = package_parts[: max(keep_count, 0)]
    if imported_module:
        base_parts.extend(imported_module.split("."))
    return ".".join(base_parts)


def match_internal_module(
    imported_name: str,
    known_modules: set[str],
) -> str | None:
    if imported_name in known_modules:
        return imported_name
    candidates = [
        name
        for name in known_modules
        if imported_name.startswith(f"{name}.")
    ]
    return max(candidates, key=len) if candidates else None


def imported_modules(
    path: Path,
    current_module: str,
    known_modules: set[str],
) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    dependencies: set[str] = set()

    for node in ast.walk(tree):
        candidates: list[str] = []
        if isinstance(node, ast.Import):
            candidates.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            base = resolve_relative_import(
                current_module=current_module,
                is_package_init=path.name == "__init__.py",
                level=node.level,
                imported_module=node.module,
            )
            candidates.extend(
                f"{base}.{alias.name}" if base else alias.name
                for alias in node.names
            )
            if base:
                candidates.append(base)

        for candidate in candidates:
            dependency = match_internal_module(candidate, known_modules)
            if dependency and dependency != current_module:
                dependencies.add(dependency)

    return dependencies


def mermaid_node_id(module: str) -> str:
    readable = re.sub(r"[^a-zA-Z0-9_]", "_", module)
    digest = hashlib.sha1(module.encode("utf-8")).hexdigest()[:8]
    return f"m_{readable}_{digest}"


def build_generated_block(source: Path) -> str:
    python_files = sorted(
        path
        for path in source.rglob("*.py")
        if "__pycache__" not in path.parts
    )
    if not python_files:
        raise ValueError(f"源码目录中没有 Python 文件：{source}")

    module_paths = {module_name(source, path): path for path in python_files}
    visible_modules = {
        module: path
        for module, path in module_paths.items()
        if path.name != "__init__.py"
    }
    known_modules = set(module_paths)
    edges: set[tuple[str, str]] = set()

    for module, path in visible_modules.items():
        for dependency in imported_modules(path, module, known_modules):
            if dependency in visible_modules:
                edges.add((module, dependency))

    lines = ["```mermaid", "flowchart LR"]
    for module, path in sorted(visible_modules.items()):
        lines.append(
            f'    {mermaid_node_id(module)}["{visible_label(source, path)}"]'
        )
    for source_module, target_module in sorted(edges):
        lines.append(
            f"    {mermaid_node_id(source_module)} --> "
            f"{mermaid_node_id(target_module)}"
        )
    lines.append("```")
    return "\n".join(lines)


def replace_generated_block(
    document: str,
    generated_block: str,
    section_heading: str,
) -> str:
    heading_match = re.search(
        rf"(?m)^{re.escape(section_heading)}[ \t]*$",
        document,
    )
    if heading_match is None:
        raise ValueError(f"文档中没有找到目标标题：{section_heading}")
    level_match = re.match(r"^(#{1,6})\s+", section_heading)
    if level_match is None:
        raise ValueError("section 必须包含 Markdown 标题级别，例如 ### 标题")

    heading_level = len(level_match.group(1))
    content_start = heading_match.end()
    next_heading = re.search(
        rf"(?m)^#{{1,{heading_level}}}\s+",
        document[content_start:],
    )
    section_end = (
        content_start + next_heading.start()
        if next_heading is not None
        else len(document)
    )
    fence_start = document.find("```mermaid", content_start, section_end)
    if fence_start == -1:
        raise ValueError("目标章节中没有找到 Mermaid 代码块")
    fence_end = document.find("```", fence_start + len("```mermaid"), section_end)
    if fence_end == -1:
        raise ValueError("目标章节中的 Mermaid 代码块没有结束标记")
    fence_end += len("```")
    return f"{document[:fence_start]}{generated_block}{document[fence_end:]}"


def main() -> int:
    args = parse_args()
    source = args.source.resolve()
    document_path = args.document.resolve()

    if not source.is_dir():
        print(f"源码目录不存在：{source}", file=sys.stderr)
        return 2
    if not document_path.is_file():
        print(f"架构文档不存在：{document_path}", file=sys.stderr)
        return 2

    try:
        original = document_path.read_text(encoding="utf-8")
        generated_block = build_generated_block(source)
        updated = replace_generated_block(
            original,
            generated_block,
            args.section,
        )
    except (OSError, SyntaxError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if updated == original:
        print("模块依赖图已是最新。")
        return 0
    if args.check:
        print("模块依赖图已过期，请运行同步命令。", file=sys.stderr)
        return 1

    document_path.write_text(updated, encoding="utf-8")
    print(f"已更新模块依赖图：{document_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
