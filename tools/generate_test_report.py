#!/usr/bin/env python3
"""Run pytest and synchronize an evidence block in a Markdown test report."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class TestResult:
    status: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="运行 pytest 并同步 Markdown 测试报告中的执行事实。",
    )
    parser.add_argument(
        "--project-root",
        required=True,
        type=Path,
        help="运行 pytest 时使用的工作目录。",
    )
    parser.add_argument(
        "--tests",
        nargs="+",
        required=True,
        help="相对于 project-root 的测试路径。",
    )
    parser.add_argument(
        "--output",
        required=True,
        type=Path,
        help="要更新的 Markdown 测试报告。",
    )
    parser.add_argument(
        "--section",
        required=True,
        help="要更新的 Markdown 标题，例如“## 一眼结论”。",
    )
    parser.add_argument(
        "--python",
        default=sys.executable,
        help="用于运行 pytest 的 Python 解释器，默认使用当前解释器。",
    )
    return parser.parse_args()


def run_command(command: list[str], cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )


def parse_junit(
    xml_path: Path,
) -> tuple[list[TestResult], str, str]:
    root = ET.parse(xml_path).getroot()
    suite = root if root.tag == "testsuite" else root.find("testsuite")
    if suite is None:
        raise ValueError("pytest 没有生成可识别的 testsuite")

    results: list[TestResult] = []
    for testcase in suite.iter("testcase"):
        if testcase.find("failure") is not None:
            status = "失败"
        elif testcase.find("error") is not None:
            status = "错误"
        elif testcase.find("skipped") is not None:
            status = "跳过"
        else:
            status = "通过"
        results.append(
            TestResult(
                status=status,
            )
        )

    return (
        results,
        suite.attrib.get("timestamp", "未记录"),
        suite.attrib.get("time", "未记录"),
    )


def interpreter_version(python: str, project_root: Path) -> str:
    completed = run_command(
        [python, "-c", "import platform; print(platform.python_version())"],
        project_root,
    )
    return completed.stdout.strip() if completed.returncode == 0 else "未知"


def pytest_version(python: str, project_root: Path) -> str:
    completed = run_command([python, "-m", "pytest", "--version"], project_root)
    if completed.returncode != 0:
        return "未知"
    return completed.stdout.splitlines()[0].strip()


def format_timestamp(timestamp: str) -> str:
    try:
        parsed = datetime.fromisoformat(timestamp)
    except ValueError:
        return timestamp
    offset = parsed.strftime("%z")
    formatted_offset = (
        f"UTC{offset[:3]}:{offset[3:]}" if offset else "本地时区"
    )
    return f"{parsed:%Y-%m-%d %H:%M:%S}（{formatted_offset}）"


def build_generated_block(
    results: list[TestResult],
    timestamp: str,
    duration: str,
    python_version: str,
    pytest_version_text: str,
    tests: list[str],
) -> str:
    counts = {
        status: sum(result.status == status for result in results)
        for status in ("通过", "失败", "错误", "跳过")
    }
    command = f"python -m pytest {' '.join(tests)}"
    passed_all = counts["通过"] == len(results) and bool(results)
    conclusion = (
        f"✅ 全部通过：`{counts['通过']}/{len(results)}` 项"
        if passed_all
        else (
            f"❌ 未全部通过：通过 `{counts['通过']}` 项，失败 `{counts['失败']}` 项，"
            f"错误 `{counts['错误']}` 项，跳过 `{counts['跳过']}` 项"
        )
    )
    lines = [
        f"**最近一次验证：{conclusion}**",
        "",
        "| 项目 | 结果 |",
        "|---|---|",
        f"| 验证时间 | {format_timestamp(timestamp)} |",
        f"| 自动化测试 | 共 {len(results)} 项，通过 {counts['通过']} 项 |",
        f"| 未通过情况 | 失败 {counts['失败']} 项，错误 {counts['错误']} 项，跳过 {counts['跳过']} 项 |",
        f"| 验证环境 | Python {python_version}；{pytest_version_text} |",
        f"| 执行命令 | `{command}` |",
        f"| 执行耗时 | {duration} 秒 |",
    ]
    return "\n".join(lines)


def replace_section_body(
    report: str,
    generated_block: str,
    section_heading: str,
) -> str:
    heading_match = re.search(
        rf"(?m)^{re.escape(section_heading)}[ \t]*$",
        report,
    )
    if heading_match is None:
        raise ValueError(f"测试报告中没有找到目标标题：{section_heading}")
    level_match = re.match(r"^(#{1,6})\s+", section_heading)
    if level_match is None:
        raise ValueError("section 必须包含 Markdown 标题级别，例如 ## 标题")

    heading_level = len(level_match.group(1))
    body_start = heading_match.end()
    next_heading = re.search(
        rf"(?m)^#{{1,{heading_level}}}\s+",
        report[body_start:],
    )
    body_end = (
        body_start + next_heading.start()
        if next_heading is not None
        else len(report)
    )
    return (
        f"{report[:body_start]}\n\n{generated_block}\n\n"
        f"{report[body_end:].lstrip()}"
    )


def main() -> int:
    args = parse_args()
    project_root = args.project_root.resolve()
    output_path = args.output.resolve()
    python_argument = Path(args.python).expanduser()
    python = (
        str(python_argument.absolute())
        if python_argument.is_absolute() or python_argument.parent != Path(".")
        else args.python
    )
    if not project_root.is_dir():
        print(f"项目运行目录不存在：{project_root}", file=sys.stderr)
        return 2
    if not output_path.is_file():
        print(f"测试报告不存在：{output_path}", file=sys.stderr)
        return 2

    try:
        original = output_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(str(exc), file=sys.stderr)
        return 2

    with tempfile.TemporaryDirectory(prefix="pytest-report-") as temporary_dir:
        xml_path = Path(temporary_dir) / "pytest.xml"
        command = [
            python,
            "-m",
            "pytest",
            *args.tests,
            "-q",
            "-p",
            "no:cacheprovider",
            "--color=no",
            f"--junitxml={xml_path}",
        ]
        completed = run_command(command, project_root)
        if not xml_path.is_file():
            print(completed.stdout, file=sys.stderr)
            print("pytest 未生成 JUnit XML，测试报告未更新。", file=sys.stderr)
            return completed.returncode or 2
        try:
            results, timestamp, duration = parse_junit(xml_path)
            generated_block = build_generated_block(
                results=results,
                timestamp=timestamp,
                duration=duration,
                python_version=interpreter_version(python, project_root),
                pytest_version_text=pytest_version(python, project_root),
                tests=args.tests,
            )
            updated = replace_section_body(
                original,
                generated_block,
                args.section,
            )
            output_path.write_text(updated, encoding="utf-8")
        except (ET.ParseError, OSError, ValueError) as exc:
            print(str(exc), file=sys.stderr)
            return 2

    print(f"已更新测试报告：{output_path}")
    print(completed.stdout.rstrip())
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
