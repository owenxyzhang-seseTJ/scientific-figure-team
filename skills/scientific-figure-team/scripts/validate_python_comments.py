#!/usr/bin/env python3
"""Validate Chinese line-end explanations on visual-affecting Python plotting code."""

from __future__ import annotations

import argparse
import re
from pathlib import Path


CHINESE_RE = re.compile(r"[\u4e00-\u9fff]")

VISUAL_RE = re.compile(
    r"\b("
    r"figsize|dpi|savefig|bbox_inches|tight_layout|constrained_layout|subplots_adjust|"
    r"rcParams|style\.use|subplot_mosaic|GridSpec|add_subplot|subplots|"
    r"color\s*=|colors\s*=|cmap\s*=|facecolor|facecolors|edgecolor|edgecolors|alpha\s*=|"
    r"font|fontsize|fontweight|labelpad|set_title|set_xlabel|set_ylabel|axes\.labelsize|legend\.fontsize|"
    r"set_xlim|set_ylim|set_xticks|set_yticks|set_xticklabels|set_yticklabels|tick_params|"
    r"spines|grid|legend\.|colorbar|annotate|arrow|FancyArrowPatch|"
    r"fill_between|"
    r"linewidth|line_width|lw|markersize|marker|s=|width|height|wspace|hspace|pad"
    r")\b",
    re.IGNORECASE,
)

CALL_RE = re.compile(
    r"(\.plot\(|\.scatter\(|\.bar\(|\.barh\(|\.imshow\(|\.fill_between\(|"
    r"\.errorbar\(|\.boxplot\(|\.violinplot\(|\.legend\(|\.text\(|"
    r"plt\.subplots\(|plt\.figure\(|sns\.heatmap\(|axhline\(|axvline\()",
    re.IGNORECASE,
)
MARKDOWN_FIELD_RE = re.compile(r"^[A-Za-z][A-Za-z0-9 /_-]*:\s")


def visual_line_needs_comment(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        return False
    if "figure-comment-exempt" in line:
        return False
    if MARKDOWN_FIELD_RE.match(stripped):
        return False
    if stripped.startswith(("import ", "from ")):
        return False
    if stripped.startswith(("def ", "class ", "return ", "raise ", "print(")):
        return False
    if stripped.startswith(("legend =", "artists =", "items =", "issues =", "paths =")):
        return False
    if ".get_legend(" in stripped or ".get_text" in stripped or ".get_window_extent" in stripped:
        return False
    return bool(VISUAL_RE.search(line) or CALL_RE.search(line))


def has_chinese_line_end_comment(line: str) -> bool:
    if "#" not in line:
        return False
    comment = line.split("#", 1)[1]
    return bool(CHINESE_RE.search(comment))


def validate_file(path: Path) -> list[tuple[int, str]]:
    failures: list[tuple[int, str]] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if visual_line_needs_comment(line) and not has_chinese_line_end_comment(line):
            failures.append((lineno, line.rstrip()))
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check that visual-affecting Python plotting lines have Chinese comments."
    )
    parser.add_argument("paths", nargs="+", help="Python plotting scripts to validate")
    args = parser.parse_args()

    all_failures: list[tuple[Path, int, str]] = []
    for raw_path in args.paths:
        path = Path(raw_path).expanduser().resolve()
        if not path.is_file():
            all_failures.append((path, 0, "file not found"))
            continue
        for lineno, line in validate_file(path):
            all_failures.append((path, lineno, line))

    if all_failures:
        print("Chinese visual-comment validation failed:")
        for path, lineno, line in all_failures:
            if lineno == 0:
                print(f"- {path}: {line}")
            else:
                print(f"- {path}:{lineno}: missing Chinese line-end explanation")
                print(f"  {line}")
        return 1

    print("Chinese visual-comment validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
