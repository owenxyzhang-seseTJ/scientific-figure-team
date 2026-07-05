#!/usr/bin/env python3
"""MOF-oriented raw-data preprocessing and plotting templates."""

from __future__ import annotations

import argparse
import csv
import math
import re
import sys
from collections import defaultdict
from pathlib import Path


STATE_ORDER = ["simulated", "as-synthesized", "solvent-exchanged", "activated"]
STATE_ALIASES = {
    "sim": "simulated",
    "simulated": "simulated",
    "as synthesis": "as-synthesized",
    "as-synthesis": "as-synthesized",
    "as synthesized": "as-synthesized",
    "as-synthesized": "as-synthesized",
    "assynthesized": "as-synthesized",
    "solvent exchange": "solvent-exchanged",
    "solvent-exchanged": "solvent-exchanged",
    "solvent exchanged": "solvent-exchanged",
    "activated": "activated",
    "activation": "activated",
}

PALETTE = {  # 设置全项目清新淡雅配色，所有 MOF 模板默认复用这些语义颜色
    "simulated": "#9AA4B2",
    "as-synthesized": "#83B6C8",
    "solvent-exchanged": "#A6C98F",
    "activated": "#E6B07E",
    "hero": "#5DA9A6",
    "accent": "#D99A8B",
    "muted": "#70777F",
    "ink": "#27323A",
    "panel_bg": "#F7FAF8",
}

PREFERRED_FONT_FAMILY = ["Arial", "DejaVu Sans"]  # 优先使用 Arial；如果系统未安装则统一退回 DejaVu Sans，保证普通文字、数字和上下标不混用字体
BASE_FONT_SIZE = 9  # 设置基础字号，默认比紧凑论文图略大以提升可读性
AXIS_LABEL_SIZE = 10  # 设置坐标轴标题字号，保证英文轴标题清楚
LEGEND_FONT_SIZE = 8.8  # 设置图例字号，兼顾可读性和紧凑排版
PANEL_LABEL_SIZE = 11  # 设置面板标号字号，适合多面板论文图


def formula_label(value: str) -> str:
    text = str(value).strip()
    if not text:
        return text
    parts = re.split(r"([/\\-])", text)
    formatted = []
    for part in parts:
        if part in {"/", "\\", "-"}:
            formatted.append(part)
        else:
            formatted.append(re.sub(r"([A-Za-z\)])(\d+)", r"\1$_{\2}$", part))
    return "".join(formatted)


def pressure_axis_label(unit: str | None) -> str:
    cleaned = (unit or "P/P0").strip()
    normalized = cleaned.lower().replace(" ", "")
    if normalized in {"p/p0", "p/p₀", "relative", "relativepressure"}:
        return r"$P/P_0$"
    return f"Pressure ({cleaned})"


def time_axis_label(unit: str | None) -> str:
    cleaned = (unit or "min/g").strip()
    normalized = cleaned.lower().replace(" ", "")
    if normalized == "min/g":
        return "Time (min/g)"
    if normalized in {"ming^-1", "ming-1", "min*g^-1"}:
        return r"Time (min g$^{-1}$)"
    if normalized in {"min", "minute", "minutes"}:
        return "Time (min)"
    return f"Time ({cleaned})"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def as_float(row: dict[str, str], key: str) -> float:
    value = row.get(key, "")
    if value is None or str(value).strip() == "":
        raise ValueError(f"missing numeric value in column `{key}`")
    return float(str(value).strip())


def require_columns(rows: list[dict[str, str]], columns: list[str], label: str) -> None:
    if not rows:
        raise ValueError(f"{label}: raw data are empty")
    available = set(rows[0])
    missing = [column for column in columns if column not in available]
    if missing:
        raise ValueError(f"{label}: missing required columns: {', '.join(missing)}")


def canonical_state(raw_state: str) -> str:
    key = (raw_state or "").strip().lower().replace("_", "-")
    return STATE_ALIASES.get(key, key or "sample")


def canonical_branch(raw_branch: str) -> str:
    key = (raw_branch or "").strip().lower()
    if key in {"ads", "adsorption", "adsorb"}:
        return "adsorption"
    if key in {"des", "desorption", "desorb"}:
        return "desorption"
    return key


def check_method_packet(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    required = ["Status: READY_FOR_PREPROCESSING", "Sources searched:", "Chosen preprocessing method:", "Rationale:"]
    missing = [item for item in required if item not in text]
    if missing:
        raise ValueError(f"method packet is not ready; missing {', '.join(missing)}")


def check_confirmed_plan(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "Status: CONFIRMED" not in text:
        raise ValueError("figure plan is not confirmed; expected `Status: CONFIRMED`")


def preprocess_pxrd(input_path: Path, output_path: Path) -> None:
    rows = read_csv(input_path)
    require_columns(rows, ["sample", "state", "two_theta", "intensity"], "PXRD")
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for row in rows:
        sample = row.get("sample", "sample").strip() or "sample"
        state = canonical_state(row.get("state", "sample"))
        grouped[(sample, state)].append(
            {
                "sample": sample,
                "state": state,
                "two_theta": as_float(row, "two_theta"),
                "intensity": as_float(row, "intensity"),
            }
        )

    processed: list[dict[str, object]] = []
    ordered_keys = sorted(
        grouped,
        key=lambda item: (item[0], STATE_ORDER.index(item[1]) if item[1] in STATE_ORDER else 99, item[1]),
    )
    for key in ordered_keys:
        values = sorted(grouped[key], key=lambda item: float(item["two_theta"]))
        max_intensity = max(float(item["intensity"]) for item in values)
        if max_intensity <= 0:
            raise ValueError(f"PXRD pattern {key} has non-positive maximum intensity")
        state = key[1]
        offset_index = STATE_ORDER.index(state) if state in STATE_ORDER else len(STATE_ORDER)
        y_offset = offset_index * 115.0
        for item in values:
            norm = float(item["intensity"]) / max_intensity * 100.0
            processed.append(
                {
                    "sample": item["sample"],
                    "state": state,
                    "two_theta": item["two_theta"],
                    "intensity_raw": item["intensity"],
                    "intensity_norm": round(norm, 6),
                    "y_offset": y_offset,
                    "intensity_offset": round(norm + y_offset, 6),
                    "state_label": state,
                }
            )
    write_csv(
        output_path,
        processed,
        ["sample", "state", "two_theta", "intensity_raw", "intensity_norm", "y_offset", "intensity_offset", "state_label"],
    )


def row_is_true(row: dict[str, str], key: str) -> bool:
    return str(row.get(key, "")).strip().lower() in {"1", "true", "yes", "y"}


def preprocess_tga(input_path: Path, output_path: Path) -> None:
    rows = read_csv(input_path)
    require_columns(rows, ["sample", "state", "temperature", "mass"], "TGA")
    grouped: dict[tuple[str, str], list[dict[str, object]]] = defaultdict(list)
    for index, row in enumerate(rows):
        sample = row.get("sample", "sample").strip() or "sample"
        state = canonical_state(row.get("state", "sample"))
        grouped[(sample, state)].append(
            {
                "row_index": index,
                "sample": sample,
                "state": state,
                "temperature": as_float(row, "temperature"),
                "mass": as_float(row, "mass"),
                "segment": row.get("segment", "").strip().lower(),
                "baseline_start": row_is_true(row, "baseline_start"),
            }
        )

    processed: list[dict[str, object]] = []
    for key, values in grouped.items():
        values = sorted(values, key=lambda item: int(item["row_index"]))
        state = key[1]
        segment_names = {str(item["segment"]) for item in values if item.get("segment")}
        baseline_rows = [item for item in values if item["baseline_start"]]
        if not baseline_rows and state == "activated" and {"hold", "cooling"} & segment_names:
            baseline_rows = [item for item in values if str(item["segment"]) in {"reheating", "heating-after-cooling", "heating_after_cooling"}]
            if not baseline_rows:
                raise ValueError("TGA activated sample has hold/cooling markers but no reheating baseline marker")
        baseline = float((baseline_rows[0] if baseline_rows else values[0])["mass"])
        if baseline == 0:
            raise ValueError(f"TGA baseline mass is zero for {key}")
        for item in values:
            processed.append(
                {
                    "sample": item["sample"],
                    "state": state,
                    "temperature": item["temperature"],
                    "mass_raw": item["mass"],
                    "mass_percent": round(float(item["mass"]) / baseline * 100.0, 6),
                    "segment": item["segment"],
                    "baseline_used": baseline,
                }
            )
    write_csv(output_path, processed, ["sample", "state", "temperature", "mass_raw", "mass_percent", "segment", "baseline_used"])


def preprocess_adsorption(input_path: Path, output_path: Path) -> None:
    rows = read_csv(input_path)
    require_columns(rows, ["sample", "gas", "branch", "pressure", "uptake"], "gas adsorption")
    processed: list[dict[str, object]] = []
    for row in rows:
        branch = canonical_branch(row.get("branch", "adsorption"))
        processed.append(
            {
                "sample": row.get("sample", "sample").strip() or "sample",
                "gas": row.get("gas", "").strip(),
                "branch": branch,
                "pressure": as_float(row, "pressure"),
                "pressure_unit": row.get("pressure_unit", "P/P0").strip() or "P/P0",
                "uptake": as_float(row, "uptake"),
                "marker_fill": "filled" if branch == "adsorption" else "hollow",
            }
        )
    processed.sort(key=lambda item: (str(item["sample"]), str(item["gas"]), str(item["branch"]), float(item["pressure"])))
    write_csv(output_path, processed, ["sample", "gas", "branch", "pressure", "pressure_unit", "uptake", "marker_fill"])


def preprocess_qst(input_path: Path, output_path: Path) -> None:
    rows = read_csv(input_path)
    require_columns(rows, ["sample", "loading", "qst"], "Qst")
    processed = [
        {"sample": row.get("sample", "sample").strip() or "sample", "loading": as_float(row, "loading"), "qst": as_float(row, "qst")}
        for row in rows
    ]
    processed.sort(key=lambda item: (str(item["sample"]), float(item["loading"])))
    write_csv(output_path, processed, ["sample", "loading", "qst"])


def preprocess_iast(input_path: Path, output_path: Path) -> None:
    rows = read_csv(input_path)
    require_columns(rows, ["sample", "gas_pair", "composition", "pressure", "selectivity"], "IAST")
    processed = [
        {
            "sample": row.get("sample", "sample").strip() or "sample",
            "gas_pair": row.get("gas_pair", "").strip(),
            "composition": as_float(row, "composition"),
            "pressure": as_float(row, "pressure"),
            "selectivity": as_float(row, "selectivity"),
        }
        for row in rows
    ]
    processed.sort(key=lambda item: (str(item["sample"]), str(item["gas_pair"]), float(item["pressure"])))
    write_csv(output_path, processed, ["sample", "gas_pair", "composition", "pressure", "selectivity"])


def preprocess_breakthrough(input_path: Path, output_path: Path) -> None:
    rows = read_csv(input_path)
    require_columns(rows, ["sample", "component", "time", "c_over_c0"], "breakthrough")
    processed: list[dict[str, object]] = []
    for row in rows:
        processed.append(
            {
                "sample": row.get("sample", "sample").strip() or "sample",
                "component": row.get("component", "").strip(),
                "time": as_float(row, "time"),
                "time_unit": row.get("time_unit", "min/g").strip() or "min/g",
                "bed_volume": row.get("bed_volume", "").strip(),
                "c_over_c0": as_float(row, "c_over_c0"),
                "threshold": row.get("threshold", "").strip(),
                "show_threshold": row.get("show_threshold", "").strip(),
            }
        )
    processed.sort(key=lambda item: (str(item["sample"]), str(item["component"]), float(item["time"])))
    write_csv(output_path, processed, ["sample", "component", "time", "time_unit", "bed_volume", "c_over_c0", "threshold", "show_threshold"])


PREPROCESSORS = {
    "pxrd": preprocess_pxrd,
    "tga": preprocess_tga,
    "adsorption": preprocess_adsorption,
    "qst": preprocess_qst,
    "iast": preprocess_iast,
    "breakthrough": preprocess_breakthrough,
}


def import_matplotlib():
    try:
        import matplotlib as mpl
        mpl.use("Agg")
        mpl.set_loglevel("error")  # 仅保留 Matplotlib 严重错误日志，避免 Arial 数学字体查找日志干扰模板运行结果
        import matplotlib.pyplot as plt
    except ModuleNotFoundError as exc:
        raise RuntimeError("matplotlib is required for plotting; preprocessing can still run without it") from exc
    return mpl, plt


def select_single_typeface() -> str:
    from matplotlib import font_manager

    available_families = {item.name for item in font_manager.fontManager.ttflist}  # 读取当前环境真实可用字体，避免系统字体缺失时混用多个字体
    for family in PREFERRED_FONT_FAMILY:  # 按候选顺序选择一个真实存在的字体
        if family in available_families:
            return family
    return "DejaVu Sans"


def mathtext_rcparams(figure_typeface: str) -> dict[str, str]:
    if figure_typeface == "DejaVu Sans":
        return {
            "mathtext.fontset": "dejavusans",  # 使用 DejaVu Sans 数学字体集，保证无 Arial 时上下标和正文同族
            "mathtext.default": "regular",  # 设置数学上下标为常规字形，避免默认斜体影响单位和分子式
        }
    return {
        "mathtext.fontset": "custom",  # 使用自定义数学字体映射，让 Arial 环境下上下标也使用同一字体
        "mathtext.default": "regular",  # 设置数学上下标为常规字形，保证分子式和单位风格统一
        "mathtext.rm": f"{figure_typeface}:style=normal",  # 设置数学正文字体为当前选中字体的常规字形
        "mathtext.it": f"{figure_typeface}:style=italic",  # 设置数学斜体字体为当前选中字体的斜体字形
        "mathtext.bf": f"{figure_typeface}:weight=bold",  # 设置数学粗体字体为当前选中字体的粗体字形
    }


def apply_style(mpl) -> None:
    figure_typeface = select_single_typeface()  # 为普通文字、数字和上下标统一选择同一个字体
    style_params = {  # 设置全局图面风格，确保同一项目内所有模板视觉一致
        "font.family": figure_typeface,  # 使用单一真实字体，适合英文科研图且避免字体混用
        "font.sans-serif": [figure_typeface],  # 只使用一个真实可用字体，避免英文、数字和上下标混用不同字体
        "svg.fonttype": "none",  # 保留 SVG 文字为原生文本，方便后续编辑上下标
        "pdf.fonttype": 42,  # 让 PDF 使用可编辑 TrueType 字体，提升投稿兼容性
        "font.size": BASE_FONT_SIZE,  # 设置全局基础字号，默认略大提高可读性
        "axes.labelsize": AXIS_LABEL_SIZE,  # 设置坐标轴标题字号，让英文单位清楚可读
        "legend.fontsize": LEGEND_FONT_SIZE,  # 设置图例字号，避免图例过小
        "axes.spines.right": False,  # 隐藏右侧坐标轴边框，减少冗余线条
        "axes.spines.top": False,  # 隐藏顶部坐标轴边框，保持学术图简洁
        "axes.linewidth": 0.9,  # 设置坐标轴线宽，让边界清晰但不过重
        "legend.frameon": False,  # 去掉图例边框，降低视觉干扰
    }
    style_params.update(mathtext_rcparams(figure_typeface))  # 根据实际选中的字体设置数学上下标字体，避免下标数字和英文字体不一致
    mpl.rcParams.update(style_params)  # 应用字体、字号、边框和导出参数，保证后续所有面板使用同一风格


def unique_values(rows: list[dict[str, str]], key: str) -> list[str]:
    seen: list[str] = []
    for row in rows:
        value = str(row.get(key, ""))
        if value not in seen:
            seen.append(value)
    return seen


def state_color(state: str) -> str:
    return PALETTE.get(state, PALETTE["hero"])


def right_end_trace_label_position(x: list[float], y: list[float], y_gap: float) -> tuple[float, float]:
    x_span = max(x) - min(x) if x else 1.0
    target_x = max(x) - x_span * 0.035
    idx = min(range(len(x)), key=lambda item: abs(x[item] - target_x))
    return x[idx], y[idx] + y_gap


def check_figure_overlaps(fig) -> list[str]:
    fig.canvas.draw()  # 渲染画布以获得文字和图像的真实边界框
    renderer = fig.canvas.get_renderer()
    items = []
    for ax_index, ax in enumerate(fig.axes):
        artists = [("title", ax.title), ("xlabel", ax.xaxis.label), ("ylabel", ax.yaxis.label)]
        artists.extend(("xtick", item) for item in ax.get_xticklabels())
        artists.extend(("ytick", item) for item in ax.get_yticklabels())
        artists.extend(("text", item) for item in ax.texts)
        legend = ax.get_legend()
        if legend is not None:
            artists.extend(("legend", item) for item in legend.get_texts())
        for kind, artist in artists:
            if artist.get_visible() and artist.get_text():
                items.append((kind, f"axis{ax_index}:{artist.get_text()}", artist.get_window_extent(renderer=renderer)))
    issues: list[str] = []
    for i, (kind_a, label_a, box_a) in enumerate(items):
        for kind_b, label_b, box_b in items[i + 1 :]:
            if {kind_a, kind_b} == {"xtick", "ytick"}:
                continue
            if box_a.overlaps(box_b):
                issues.append(f"text overlap: {label_a} <-> {label_b}")
    return issues


def save_figure(fig, output_dir: Path, stem: str, dpi: int = 600) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = [
        output_dir / f"{stem}.svg",
        output_dir / f"{stem}.pdf",
        output_dir / f"{stem}.tiff",
        output_dir / f"{stem}.png",
    ]
    fig.savefig(paths[0], bbox_inches="tight")  # 导出可编辑 SVG，保留英文文字和原生上下标
    fig.savefig(paths[1], bbox_inches="tight")  # 导出矢量 PDF，适合论文投稿和排版
    fig.savefig(paths[2], dpi=dpi, bbox_inches="tight")  # 导出高分辨率 TIFF，满足常见期刊位图要求
    fig.savefig(paths[3], dpi=300, bbox_inches="tight")  # 导出 PNG 预览图，方便快速检查图面
    return paths


def plot_pxrd(input_path: Path, output_dir: Path) -> None:
    mpl, plt = import_matplotlib()
    apply_style(mpl)
    rows = read_csv(input_path)
    fig, ax = plt.subplots(figsize=(4.6, 3.2), constrained_layout=True)  # 设置 PXRD 单图尺寸和自动边距
    for state in STATE_ORDER:
        state_rows = [row for row in rows if row.get("state") == state]
        if not state_rows:
            continue
        x = [float(row["two_theta"]) for row in state_rows]
        y = [float(row["intensity_offset"]) for row in state_rows]
        ax.plot(x, y, lw=1.35, color=state_color(state), label=state)  # 绘制归一化并上下错开的 PXRD 曲线
        label_x, label_y = right_end_trace_label_position(x, y, 9.0)
        ax.text(label_x, label_y, state, va="bottom", ha="right", fontsize=LEGEND_FONT_SIZE, color=state_color(state), fontweight="bold")  # 在每条谱线最右端附近的曲线上方直接标注状态，避免标签脱离对应曲线
    ax.set_xlabel(r"2$\theta$ (degree)", labelpad=5)  # 设置 PXRD 横轴英文标签和原生希腊/上标格式
    ax.set_ylabel("Normalized intensity (a.u.)", labelpad=5)  # 设置纵轴英文标签，说明强度已归一化
    ax.set_yticks([])  # 隐藏 y 轴刻度，避免错峰 PXRD 被误读为绝对强度比较
    ax.set_xlim(left=min(float(row["two_theta"]) for row in rows), right=max(float(row["two_theta"]) for row in rows) + 0.4)  # 仅保留少量右侧余量，让谱线标签贴近曲线右端
    paths = save_figure(fig, output_dir, "pxrd")
    issues = check_figure_overlaps(fig)
    (output_dir / "pxrd_overlap_report.txt").write_text("\n".join(issues) if issues else "No overlap detected.", encoding="utf-8")
    plt.close(fig)
    print("PXRD outputs:", ", ".join(str(path) for path in paths))


def plot_tga(input_path: Path, output_dir: Path) -> None:
    mpl, plt = import_matplotlib()
    apply_style(mpl)
    rows = read_csv(input_path)
    fig, ax = plt.subplots(figsize=(3.8, 3.0), constrained_layout=True)  # 设置 TGA 图尺寸和自动边距
    for state in unique_values(rows, "state"):
        state_rows = [row for row in rows if row.get("state") == state]
        x = [float(row["temperature"]) for row in state_rows]
        y = [float(row["mass_percent"]) for row in state_rows]
        ax.plot(x, y, lw=1.6, color=state_color(state), label=state)  # 绘制以 100% 起点归一化后的热重曲线
    ax.set_xlabel("Temperature (°C)", labelpad=5)  # 设置温度横轴英文标签
    ax.set_ylabel("Mass (%)", labelpad=5)  # 设置质量百分比纵轴标签
    ax.set_ylim(bottom=0, top=105)  # 固定 TGA y 轴范围，突出 100% 起点和失重区间
    ax.legend(loc="best")  # 自动选择图例位置，降低遮挡曲线的风险
    paths = save_figure(fig, output_dir, "tga")
    issues = check_figure_overlaps(fig)
    (output_dir / "tga_overlap_report.txt").write_text("\n".join(issues) if issues else "No overlap detected.", encoding="utf-8")
    plt.close(fig)
    print("TGA outputs:", ", ".join(str(path) for path in paths))


def plot_adsorption(input_path: Path, output_dir: Path) -> None:
    mpl, plt = import_matplotlib()
    apply_style(mpl)
    rows = read_csv(input_path)
    fig, ax = plt.subplots(figsize=(3.8, 3.0), constrained_layout=True)  # 设置气体吸附散点图尺寸和自动边距
    pressure_units = [row.get("pressure_unit", "P/P0") for row in rows if row.get("pressure_unit")]
    for sample in unique_values(rows, "sample"):
        sample_rows = [row for row in rows if row.get("sample") == sample]
        color = PALETTE["hero"] if sample == unique_values(rows, "sample")[0] else PALETTE["accent"]  # 设置当前样品散点颜色，保证吸附和脱附分支语义一致
        for branch in ["adsorption", "desorption"]:
            branch_rows = [row for row in sample_rows if row.get("branch") == branch]
            x = [float(row["pressure"]) for row in branch_rows]
            y = [float(row["uptake"]) for row in branch_rows]
            if branch == "adsorption":
                ax.scatter(x, y, s=24, facecolors=color, edgecolors=color, linewidths=0.9, label=f"{sample} ads.")  # 绘制吸附支实心散点
            else:
                ax.scatter(x, y, s=24, facecolors="none", edgecolors=color, linewidths=0.9, label=f"{sample} des.")  # 绘制脱附支空心散点
    ax.set_xlabel(pressure_axis_label(pressure_units[0] if pressure_units else "P/P0"), labelpad=5)  # 按原始数据压力单位设置横轴，默认使用 P/P0 且 0 为下标
    ax.set_ylabel(r"Uptake (cm$^3$ g$^{-1}$)", labelpad=5)  # 设置吸附量纵轴标签，使用原生上下标单位
    ax.legend(loc="best", ncol=1)  # 设置图例位置，区分吸附和脱附分支
    paths = save_figure(fig, output_dir, "gas_adsorption")
    issues = check_figure_overlaps(fig)
    (output_dir / "gas_adsorption_overlap_report.txt").write_text("\n".join(issues) if issues else "No overlap detected.", encoding="utf-8")
    plt.close(fig)
    print("Gas adsorption outputs:", ", ".join(str(path) for path in paths))


def plot_qst(input_path: Path, output_dir: Path) -> None:
    mpl, plt = import_matplotlib()
    apply_style(mpl)
    rows = read_csv(input_path)
    fig, ax = plt.subplots(figsize=(3.6, 2.9), constrained_layout=True)  # 设置 Qst 图尺寸和自动边距
    for sample in unique_values(rows, "sample"):
        sample_rows = [row for row in rows if row.get("sample") == sample]
        x = [float(row["loading"]) for row in sample_rows]
        y = [float(row["qst"]) for row in sample_rows]
        ax.plot(x, y, lw=1.5, marker="o", ms=4, color=PALETTE["hero"], label=sample)  # 绘制 Qst 随负载量变化曲线
    ax.set_xlabel(r"Loading (mmol g$^{-1}$)", labelpad=5)  # 设置负载量横轴标签，使用原生上标单位
    ax.set_ylabel(r"Q$_{st}$ (kJ mol$^{-1}$)", labelpad=5)  # 设置 Qst 纵轴标签，使用原生下标和上标
    ax.legend(loc="best")  # 设置图例位置，说明样品名称
    paths = save_figure(fig, output_dir, "qst")
    issues = check_figure_overlaps(fig)
    (output_dir / "qst_overlap_report.txt").write_text("\n".join(issues) if issues else "No overlap detected.", encoding="utf-8")
    plt.close(fig)
    print("Qst outputs:", ", ".join(str(path) for path in paths))


def plot_iast(input_path: Path, output_dir: Path) -> None:
    mpl, plt = import_matplotlib()
    apply_style(mpl)
    rows = read_csv(input_path)
    fig, ax = plt.subplots(figsize=(3.6, 2.9), constrained_layout=True)  # 设置 IAST 选择性图尺寸和自动边距
    for sample in unique_values(rows, "sample"):
        sample_rows = [row for row in rows if row.get("sample") == sample]
        x = [float(row["pressure"]) for row in sample_rows]
        y = [float(row["selectivity"]) for row in sample_rows]
        ax.plot(x, y, lw=1.5, marker="o", ms=4, color=PALETTE["hero"], label=sample)  # 绘制 IAST 选择性随压力变化曲线
    ax.set_xlabel("Pressure (bar)", labelpad=5)  # 设置压力横轴英文标签
    ax.set_ylabel("IAST selectivity", labelpad=5)  # 设置 IAST 选择性纵轴英文标签
    ax.legend(loc="best")  # 设置图例位置，说明样品名称
    paths = save_figure(fig, output_dir, "iast")
    issues = check_figure_overlaps(fig)
    (output_dir / "iast_overlap_report.txt").write_text("\n".join(issues) if issues else "No overlap detected.", encoding="utf-8")
    plt.close(fig)
    print("IAST outputs:", ", ".join(str(path) for path in paths))


def plot_breakthrough(input_path: Path, output_dir: Path) -> None:
    mpl, plt = import_matplotlib()
    apply_style(mpl)
    rows = read_csv(input_path)
    fig, ax = plt.subplots(figsize=(3.8, 3.0), constrained_layout=True)  # 设置穿透曲线图尺寸和自动边距
    colors = [PALETTE["hero"], PALETTE["accent"], PALETTE["activated"], PALETTE["solvent-exchanged"]]  # 设置穿透曲线多组分配色，保持清新淡雅且可区分
    time_units = [row.get("time_unit", "min/g") for row in rows if row.get("time_unit")]
    for idx, component in enumerate(unique_values(rows, "component")):
        comp_rows = [row for row in rows if row.get("component") == component]
        x = [float(row["time"]) for row in comp_rows]
        y = [float(row["c_over_c0"]) for row in comp_rows]
        ax.plot(x, y, lw=1.5, color=colors[idx % len(colors)], label=formula_label(component))  # 绘制各组分 C/C0 随时间变化曲线，并用原生上下标显示气体分子
    thresholds = [float(row["threshold"]) for row in rows if row.get("threshold") and str(row.get("show_threshold", "")).lower() in {"1", "true", "yes", "y"}]
    if thresholds:
        ax.axhline(thresholds[0], lw=0.9, ls="--", color=PALETTE["muted"], alpha=0.8)  # 添加确认过的穿透阈值参考线
    ax.set_xlabel(time_axis_label(time_units[0] if time_units else "min/g"), labelpad=5)  # 按原始数据时间单位设置横轴，默认使用 min/g
    ax.set_ylabel(r"C/C$_0$", labelpad=5)  # 设置穿透曲线纵轴标签，使用原生下标
    ax.set_ylim(-0.03, 1.05)  # 固定 C/C0 范围，避免曲线贴边
    ax.legend(loc="best")  # 设置图例位置，区分不同气体组分
    paths = save_figure(fig, output_dir, "breakthrough")
    issues = check_figure_overlaps(fig)
    (output_dir / "breakthrough_overlap_report.txt").write_text("\n".join(issues) if issues else "No overlap detected.", encoding="utf-8")
    plt.close(fig)
    print("Breakthrough outputs:", ", ".join(str(path) for path in paths))


PLOTTERS = {
    "pxrd": plot_pxrd,
    "tga": plot_tga,
    "adsorption": plot_adsorption,
    "qst": plot_qst,
    "iast": plot_iast,
    "breakthrough": plot_breakthrough,
}


def synthetic_rows(kind: str) -> tuple[list[dict[str, object]], list[str]]:
    if kind == "pxrd":
        rows = []
        for state in STATE_ORDER:
            center = {"simulated": 9.5, "as-synthesized": 9.7, "solvent-exchanged": 9.6, "activated": 9.55}[state]
            for i in range(90):
                two_theta = 5.0 + i * 0.2
                peak = math.exp(-((two_theta - center) ** 2) / 0.9) * 1000
                rows.append({"sample": "MOF-1", "state": state, "two_theta": round(two_theta, 3), "intensity": round(peak + 30, 3)})
        return rows, ["sample", "state", "two_theta", "intensity"]
    if kind == "tga":
        rows = []
        for i in range(80):
            temp = 30 + i * 8
            segment = "reheating" if i >= 8 else "cooling"
            baseline_start = "yes" if i == 8 else ""
            rows.append({"sample": "MOF-1", "state": "activated", "temperature": temp, "mass": round(12.4 - i * 0.035, 4), "segment": segment, "baseline_start": baseline_start})
        return rows, ["sample", "state", "temperature", "mass", "segment", "baseline_start"]
    if kind == "adsorption":
        rows = []
        for branch in ["adsorption", "desorption"]:
            for i in range(12):
                pressure = i / 11
                uptake = 180 * pressure / (0.12 + pressure) if branch == "adsorption" else 170 * pressure / (0.14 + pressure)
                rows.append({"sample": "MOF-1", "gas": "N2", "branch": branch, "pressure": round(pressure, 5), "pressure_unit": "P/P0", "uptake": round(uptake, 4)})
        return rows, ["sample", "gas", "branch", "pressure", "pressure_unit", "uptake"]
    if kind == "qst":
        rows = [{"sample": "MOF-1", "loading": round(0.2 + i * 0.25, 3), "qst": round(42 - i * 1.6, 3)} for i in range(10)]
        return rows, ["sample", "loading", "qst"]
    if kind == "iast":
        rows = [{"sample": "MOF-1", "gas_pair": "CO2/N2", "composition": 0.15, "pressure": round(0.1 + i * 0.2, 3), "selectivity": round(38 - i * 1.2, 3)} for i in range(10)]
        return rows, ["sample", "gas_pair", "composition", "pressure", "selectivity"]
    if kind == "breakthrough":
        rows = []
        for component in ["CO2", "N2"]:
            for i in range(40):
                time = i * 2
                midpoint = 38 if component == "CO2" else 10
                value = 1 / (1 + math.exp(-(time - midpoint) / 4))
                rows.append({"sample": "MOF-1", "component": component, "time": time / 20, "time_unit": "min/g", "bed_volume": "", "c_over_c0": round(value, 5), "threshold": "", "show_threshold": ""})
        return rows, ["sample", "component", "time", "time_unit", "bed_volume", "c_over_c0", "threshold", "show_threshold"]
    raise ValueError(f"unknown template kind: {kind}")


METHOD_PACKET_TEMPLATE = """Status: READY_FOR_PREPROCESSING
Search date: replace with current date after literature/method search
Figure type: MOF quantitative figure
Material/system: replace with sample name
Sources searched:
- Replace with peer-reviewed paper, instrument/software documentation, or user-provided Methods/SI.
Chosen preprocessing method:
- Replace with the selected method before preprocessing.
Rationale:
- Explain why this method matches the raw data and figure type.
Rejected alternatives:
- List methods considered but not used.
Assumptions and limits:
- State baseline, normalization, branch, fitting, or model assumptions.
Fields required from raw data:
- See the CSV templates in data_raw/.
Fields produced after preprocessing:
- See data_processed/ after running preprocessing.
"""


FIGURE_PLAN_TEMPLATE = """Status: WAITING_FOR_USER_CONFIRMATION
Figure objective: Replace with the English figure message.
Raw data files: data_raw/*.csv
Preprocessing steps: Replace after method search.
Visual mapping: English labels, pastel palette, Arial-first single selected font family, native subscripts/superscripts.
Export formats: SVG, PDF, TIFF, PNG.
Limitations: Replace with missing units, assumptions, or unconfirmed processing choices.

Change the first line to `Status: CONFIRMED` only after user approval.
"""


PROJECT_README = """# MOF Figure Project

Workflow:

1. Put raw machine-readable data in `data_raw/`.
2. Search relevant literature, instrument/software docs, or user-provided methods.
3. Fill `method_search_packet.md` and keep `Status: READY_FOR_PREPROCESSING`.
4. Fill `figure_plan.md` in English and wait for user confirmation.
5. Preprocess raw data into `data_processed/`.
6. Change `figure_plan.md` to `Status: CONFIRMED` after approval.
7. Plot into `outputs/`.
8. Run final rendered-image audit; if it fails, redraw and re-audit before delivery.

Example commands:

```bash
python3 path/to/mof_figure_templates.py preprocess pxrd data_raw/pxrd_raw.csv data_processed/pxrd_processed.csv --method-packet method_search_packet.md
python3 path/to/mof_figure_templates.py plot pxrd data_processed/pxrd_processed.csv outputs --plan figure_plan.md
```
"""


def init_project(project_dir: Path) -> None:
    project_dir.mkdir(parents=True, exist_ok=True)
    for folder in ["data_raw", "data_processed", "outputs", "scripts"]:
        (project_dir / folder).mkdir(exist_ok=True)
    for kind in PREPROCESSORS:
        rows, fields = synthetic_rows(kind)
        write_csv(project_dir / "data_raw" / f"{kind}_raw.csv", rows, fields)
    (project_dir / "method_search_packet.md").write_text(METHOD_PACKET_TEMPLATE, encoding="utf-8")
    (project_dir / "figure_plan.md").write_text(FIGURE_PLAN_TEMPLATE, encoding="utf-8")
    (project_dir / "README.md").write_text(PROJECT_README, encoding="utf-8")
    print(f"Created MOF figure project: {project_dir}")


def main() -> int:
    parser = argparse.ArgumentParser(description="MOF figure preprocessing and plotting templates.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create a MOF figure project with raw-data templates")
    init_parser.add_argument("project_dir")

    preprocess_parser = subparsers.add_parser("preprocess", help="Preprocess raw MOF data")
    preprocess_parser.add_argument("kind", choices=sorted(PREPROCESSORS))
    preprocess_parser.add_argument("input_csv")
    preprocess_parser.add_argument("output_csv")
    preprocess_parser.add_argument("--method-packet", required=True, help="Path to method_search_packet.md")

    plot_parser = subparsers.add_parser("plot", help="Plot preprocessed MOF data")
    plot_parser.add_argument("kind", choices=sorted(PLOTTERS))
    plot_parser.add_argument("processed_csv")
    plot_parser.add_argument("output_dir")
    plot_parser.add_argument("--plan", required=True, help="Path to confirmed figure_plan.md")

    args = parser.parse_args()

    try:
        if args.command == "init":
            init_project(Path(args.project_dir))
            return 0
        if args.command == "preprocess":
            check_method_packet(Path(args.method_packet))
            PREPROCESSORS[args.kind](Path(args.input_csv), Path(args.output_csv))
            print(f"Processed {args.kind}: {args.output_csv}")
            return 0
        if args.command == "plot":
            check_confirmed_plan(Path(args.plan))
            PLOTTERS[args.kind](Path(args.processed_csv), Path(args.output_dir))
            return 0
    except (RuntimeError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    raise ValueError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
