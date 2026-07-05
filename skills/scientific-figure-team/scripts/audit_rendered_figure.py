#!/usr/bin/env python3
"""Audit rendered SVG figures and plotting scripts for readability failures."""

from __future__ import annotations

import argparse
import math
import re
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")
STYLE_RE = re.compile(r"([^:;]+)\s*:\s*([^;]+)")
FONT_SIZE_RE = re.compile(r"font-size\s*:\s*([0-9.]+)px")
SCRIPT_BOX_RE = re.compile(
    r"bbox\s*=\s*dict\(|boxstyle\s*=|FancyBboxPatch|FancyBbox|"
    r"legend\s*\([^)]*frameon\s*=\s*True|frameon\s*=\s*True|framealpha\s*="
)
SCRIPT_GRID_RE = re.compile(r"\.grid\(\s*True|grid\s*=\s*True")
SCRIPT_FONT_RE = re.compile(r"fontsize\s*=\s*([0-9.]+)|[\"']font\.size[\"']\s*:\s*([0-9.]+)")
FONT_SANS_LIST_RE = re.compile(r"[\"']font\.sans-serif[\"']\s*:\s*\[([^\]]+)\]")
SCRIPT_AREA_FILL_RE = re.compile(r"\.fill_between\(|\.axhspan\(|\.axvspan\(")
AXVLINE_X_RE = re.compile(r"\.axvline\(\s*(?:x\s*=\s*)?([-0-9.]+)")
ANNOTATE_XY_RE = re.compile(r"xy\s*=\s*\(\s*([-0-9.]+)")
PANEL_LABEL_RE = re.compile(r"[\"']([A-Za-z])[\"']")
TEXT_ARGS_RE = re.compile(r"\.text\(\s*([-0-9.]+)\s*,\s*([-0-9.]+)")


@dataclass
class TextItem:
    text: str
    font_size: float
    bbox: tuple[float, float, float, float]
    source: str


def parse_style(style: str | None) -> dict[str, str]:
    if not style:
        return {}
    return {key.strip(): value.strip() for key, value in STYLE_RE.findall(style)}


def parse_float(value: str | None, default: float = 0.0) -> float:
    if not value:
        return default
    match = NUMBER_RE.search(value)
    return float(match.group()) if match else default


def svg_size(root: ET.Element) -> tuple[float, float]:
    view_box = root.attrib.get("viewBox")
    if view_box:
        numbers = [float(item) for item in NUMBER_RE.findall(view_box)]
        if len(numbers) == 4:
            return numbers[2], numbers[3]
    return parse_float(root.attrib.get("width"), 0.0), parse_float(root.attrib.get("height"), 0.0)


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def element_text(element: ET.Element) -> str:
    fragments = [part.strip() for part in element.itertext() if part.strip()]
    return "".join(fragments)


def element_font_size(element: ET.Element, inherited: float) -> float:
    style = parse_style(element.attrib.get("style"))
    if "font-size" in style:
        return parse_float(style["font-size"], inherited)
    match = FONT_SIZE_RE.search(element.attrib.get("style", ""))
    if match:
        return float(match.group(1))
    return parse_float(element.attrib.get("font-size"), inherited)


def element_font_family(element: ET.Element) -> str:
    style = parse_style(element.attrib.get("style"))
    return style.get("font-family") or element.attrib.get("font-family", "")


def estimate_text_bbox(element: ET.Element, text: str, font_size: float) -> tuple[float, float, float, float]:
    x = parse_float(element.attrib.get("x"), 0.0)
    y = parse_float(element.attrib.get("y"), 0.0)
    style = parse_style(element.attrib.get("style"))
    anchor = style.get("text-anchor", element.attrib.get("text-anchor", "start"))
    width = max(font_size * 0.56 * max(len(text), 1), font_size)
    height = font_size * 1.25
    if anchor == "middle":
        x0 = x - width / 2
    elif anchor == "end":
        x0 = x - width
    else:
        x0 = x
    y0 = y - height
    transform = element.attrib.get("transform", "")
    if "rotate" in transform:
        angle_values = [float(item) for item in NUMBER_RE.findall(transform)]
        angle = angle_values[0] if angle_values else 0.0
        if abs(abs(angle) - 90) < 5:
            return (x - height / 2, y - width, x + height / 2, y)
    return (x0, y0, x0 + width, y0 + height)


def overlap_area(a: tuple[float, float, float, float], b: tuple[float, float, float, float]) -> float:
    left = max(a[0], b[0])
    top = max(a[1], b[1])
    right = min(a[2], b[2])
    bottom = min(a[3], b[3])
    if right <= left or bottom <= top:
        return 0.0
    return (right - left) * (bottom - top)


def collect_text_items(root: ET.Element, svg_path: Path, default_font_size: float) -> list[TextItem]:
    items: list[TextItem] = []
    for element in root.iter():
        if local_name(element.tag) != "text":
            continue
        text = element_text(element)
        if not text:
            continue
        font_size = element_font_size(element, default_font_size)
        bbox = estimate_text_bbox(element, text, font_size)
        items.append(TextItem(text=text, font_size=font_size, bbox=bbox, source=str(svg_path)))
    return items


def audit_svg(svg_path: Path, min_font_size: float, hard_min_font_size: float, edge_margin: float, check_svg_bbox: bool) -> list[str]:
    try:
        root = ET.parse(svg_path).getroot()
    except ET.ParseError as exc:
        return [f"{svg_path}: cannot parse SVG: {exc}"]

    width, height = svg_size(root)
    items = collect_text_items(root, svg_path, min_font_size)
    issues: list[str] = []

    if width <= 0 or height <= 0:
        issues.append(f"{svg_path}: cannot determine SVG canvas size")

    font_families: set[str] = set()
    for item in items:
        label = item.text[:80].replace("\n", " ")
        if item.font_size < hard_min_font_size:
            issues.append(f"{svg_path}: unreadably small text {item.font_size:.1f} pt: `{label}`")
        elif item.font_size < min_font_size:
            issues.append(f"{svg_path}: text below default minimum {item.font_size:.1f} pt: `{label}`")
    for element in root.iter():
        if local_name(element.tag) not in {"text", "tspan"}:
            continue
        family = element_font_family(element)
        if family:
            families = [part.strip().strip("'\"") for part in family.split(",") if part.strip()]
            font_families.update(families)
            if len(families) > 1:
                issues.append(f"{svg_path}: text uses a font fallback chain instead of one unified font: `{family}`")
    non_generic_families = {item for item in font_families if item.lower() not in {"sans-serif", "serif", "monospace"}}
    if len(non_generic_families) > 1:
        issues.append(f"{svg_path}: multiple text font families detected: {', '.join(sorted(non_generic_families))}")

    if not check_svg_bbox:
        return issues

    for item in items:
        label = item.text[:80].replace("\n", " ")
        x0, y0, x1, y1 = item.bbox
        if width > 0 and height > 0 and (x0 < -edge_margin or y0 < -edge_margin or x1 > width + edge_margin or y1 > height + edge_margin):
            issues.append(f"{svg_path}: text appears outside canvas or clipped: `{label}`")
        elif width > 0 and height > 0 and (x0 < edge_margin or y0 < edge_margin or x1 > width - edge_margin or y1 > height - edge_margin):
            issues.append(f"{svg_path}: text is too close to canvas edge: `{label}`")

    for i, left in enumerate(items):
        for right in items[i + 1 :]:
            area = overlap_area(left.bbox, right.bbox)
            if area <= 1.5:
                continue
            smaller = min(
                max((left.bbox[2] - left.bbox[0]) * (left.bbox[3] - left.bbox[1]), 1.0),
                max((right.bbox[2] - right.bbox[0]) * (right.bbox[3] - right.bbox[1]), 1.0),
            )
            if area / smaller > 0.18:
                a = left.text[:50].replace("\n", " ")
                b = right.text[:50].replace("\n", " ")
                issues.append(f"{svg_path}: possible text overlap: `{a}` <-> `{b}`")

    return issues


def audit_script(script_path: Path, min_font_size: float, hard_min_font_size: float) -> list[str]:
    issues: list[str] = []
    script_text = script_path.read_text(encoding="utf-8")
    lines = script_text.splitlines()
    uses_mathtext = "$_" in script_text or "$^" in script_text or "\\mathregular" in script_text or "\\theta" in script_text
    has_unified_mathtext = "mathtext.fontset" in script_text and ("dejavusans" in script_text or "custom" in script_text) and "mathtext.default" in script_text
    if uses_mathtext and not has_unified_mathtext:
        issues.append(f"{script_path}: mathtext labels are used but unified regular mathtext fonts are not fully configured")
    vertical_guides = {
        float(match.group(1))
        for match in AXVLINE_X_RE.finditer(script_text)
    }
    for lineno, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if "bbox_inches" in stripped:
            continue
        font_sans_match = FONT_SANS_LIST_RE.search(stripped)
        if font_sans_match and "," in font_sans_match.group(1):
            issues.append(f"{script_path}:{lineno}: font.sans-serif must use one selected font, not a multi-font fallback list")
        if SCRIPT_GRID_RE.search(stripped) and "grid-allowed" not in stripped:
            issues.append(f"{script_path}:{lineno}: gridlines are off by default; remove grid or mark a justified exception")
        if SCRIPT_BOX_RE.search(stripped):
            issues.append(f"{script_path}:{lineno}: boxed annotation/legend style is not allowed by default")
        if SCRIPT_AREA_FILL_RE.search(stripped) and "gradient" not in stripped.lower() and "渐变" not in stripped and "fill-solid-allowed" not in stripped:
            issues.append(f"{script_path}:{lineno}: area fills should use a subtle gradient by default")
        for match in SCRIPT_FONT_RE.finditer(stripped):
            raw_size = match.group(1) or match.group(2)
            size = float(raw_size)
            if size < hard_min_font_size:
                issues.append(f"{script_path}:{lineno}: font size {size:.1f} pt is unreadably small")
            elif size < min_font_size:
                issues.append(f"{script_path}:{lineno}: font size {size:.1f} pt is below the default minimum")

    for index, line in enumerate(lines):
        if ".annotate(" not in line:
            continue
        block = "\n".join(lines[index : index + 8])
        if "xytext" in block or "line-text-allowed" in block:
            continue
        xy_match = ANNOTATE_XY_RE.search(block)
        if not xy_match:
            continue
        text_x = float(xy_match.group(1))
        if any(math.isclose(text_x, guide_x, abs_tol=0.5) for guide_x in vertical_guides):
            issues.append(
                f"{script_path}:{index + 1}: annotation text is anchored on a vertical guide line; offset it with xytext/leader line"
            )

    for index, line in enumerate(lines):
        window = "\n".join(lines[index : index + 5])
        if ".text(" not in window or "transform=ax.transAxes" not in window:
            continue
        if not PANEL_LABEL_RE.search(window):
            continue
        coords = TEXT_ARGS_RE.search(window)
        if not coords:
            continue
        x_pos = float(coords.group(1))
        y_pos = float(coords.group(2))
        if x_pos > -0.05 or y_pos < 1.01:
            issues.append(
                f"{script_path}:{index + 1}: panel label appears inside the plotting area; place it outside at x<=-0.08, y>=1.02"
            )
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit rendered SVG readability and boxed annotation risks.")
    parser.add_argument("paths", nargs="+", help="SVG files or Python plotting scripts to audit")
    parser.add_argument("--min-font-size", type=float, default=8.5, help="Default minimum acceptable visible text size")
    parser.add_argument("--hard-min-font-size", type=float, default=8.0, help="Hard failure threshold for visible text size")
    parser.add_argument("--edge-margin", type=float, default=1.0, help="Canvas-edge margin in SVG units")
    parser.add_argument("--check-svg-bbox", action="store_true", help="Enable approximate SVG text bbox overlap/edge checks")
    args = parser.parse_args()

    issues: list[str] = []
    for raw_path in args.paths:
        path = Path(raw_path).expanduser().resolve()
        if not path.exists():
            issues.append(f"{path}: file not found")
            continue
        if path.suffix.lower() == ".svg":
            issues.extend(audit_svg(path, args.min_font_size, args.hard_min_font_size, args.edge_margin, args.check_svg_bbox))
        elif path.suffix.lower() == ".py":
            issues.extend(audit_script(path, args.min_font_size, args.hard_min_font_size))
        else:
            issues.append(f"{path}: unsupported audit input; use SVG or Python script")

    if issues:
        print("Rendered figure readability audit failed:")
        for issue in issues:
            print(f"- {issue}")
        return 1

    print("Rendered figure readability audit passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
