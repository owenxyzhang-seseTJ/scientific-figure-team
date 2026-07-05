#!/usr/bin/env python3
"""Create a minimal Python-first scientific figure project."""

from __future__ import annotations

import argparse
from pathlib import Path


PLOT_TEMPLATE = '''#!/usr/bin/env python3
"""Starter script for a Python-first scientific figure."""

from pathlib import Path

import matplotlib as mpl
mpl.set_loglevel("error")  # 仅保留 Matplotlib 严重错误日志，避免 Arial 数学字体查找日志干扰模板运行结果
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import to_rgba
from matplotlib import font_manager


OUT_DIR = Path("outputs")
OUT_DIR.mkdir(exist_ok=True)

PREFERRED_FONT_FAMILY = ["Arial", "DejaVu Sans"]  # 优先使用 Arial；如果系统未安装则统一退回 DejaVu Sans，保证普通文字、数字和上下标不混用字体


def select_single_typeface():
    available_families = {item.name for item in font_manager.fontManager.ttflist}  # 读取当前环境真实可用字体，避免系统字体缺失时混用多个字体
    for family in PREFERRED_FONT_FAMILY:  # 按候选顺序选择一个真实存在的字体
        if family in available_families:
            return family
    return "DejaVu Sans"


FIGURE_TYPEFACE = select_single_typeface()  # 为普通文字、数字和上下标统一选择同一个字体

def mathtext_rcparams(figure_typeface: str):
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


STYLE_PARAMS = {  # 设置全局出版级绘图参数，保证后续所有面板风格一致
    "font.family": FIGURE_TYPEFACE,  # 使用单一真实字体，便于论文和汇报中保持清爽可读
    "font.sans-serif": [FIGURE_TYPEFACE],  # 只使用一个真实可用字体，避免英文、数字和上下标混用不同字体
    "svg.fonttype": "none",  # 保留 SVG 文字为可编辑文本，方便后续在 AI/Inkscape 中微调
    "pdf.fonttype": 42,  # 让 PDF 嵌入 TrueType 字体，减少投稿系统中的文字兼容问题
    "font.size": 9,  # 设置基础字号，默认略大以提升英文图面可读性
    "axes.labelsize": 10,  # 设置坐标轴标题字号，保证英文轴标题清楚
    "legend.fontsize": 8.8,  # 设置图例字号，兼顾可读性和紧凑排版
    "axes.spines.right": False,  # 隐藏右侧坐标轴边框，让统计图更简洁
    "axes.spines.top": False,  # 隐藏顶部坐标轴边框，减少无信息线条
    "axes.linewidth": 0.8,  # 设置坐标轴线宽，控制图面边界的视觉重量
    "legend.frameon": False,  # 去掉图例外框，降低图例对数据的干扰
}
STYLE_PARAMS.update(mathtext_rcparams(FIGURE_TYPEFACE))  # 根据实际选中的字体设置数学上下标字体，避免下标数字和英文字体不一致
mpl.rcParams.update(STYLE_PARAMS)  # 应用字体、字号、边框和导出参数，保证整张图只有一个实际字体

PALETTE = {  # 定义全图统一配色，后续面板都应复用这些语义颜色
    "hero": "#5DA9A6",  # 核心结果或本文方法颜色，改这里会影响主视觉系列
    "baseline": "#9AA4B2",  # 对照组或基线颜色，保持低调中性
    "accent": "#D99A8B",  # 强调色，用于关键差异、阈值或重点标注
    "soft": "#CFE8E6",  # 浅色辅助背景，用于置信区间或模块底色
    "ink": "#27323A",  # 主文字与轴线颜色，控制整体阅读对比度
}


def build_demo_data():
    x = np.arange(5)
    baseline = np.array([1.0, 1.2, 1.3, 1.35, 1.42])
    treatment = np.array([1.0, 1.35, 1.62, 1.82, 1.95])
    return x, baseline, treatment


def add_gradient_between(ax, x, y_lower, y_upper, color, alpha_top=0.32, alpha_bottom=0.03):
    x_array = np.asarray(x)
    lower = np.asarray(y_lower)
    upper = np.asarray(y_upper)
    y_min = float(min(lower.min(), upper.min()))
    y_max = float(max(lower.max(), upper.max()))
    rgba = np.array(to_rgba(color))  # 将十六进制颜色转换为 RGBA，作为渐变填色的主色
    gradient = np.ones((256, 1, 4))
    gradient[:, :, :3] = rgba[:3]
    gradient[:, :, 3] = np.linspace(alpha_bottom, alpha_top, 256)[:, None]
    clip = ax.fill_between(x_array, lower, upper, color=color, alpha=0.0)  # 创建透明裁剪区域，用于限制渐变填色范围
    image = ax.imshow(gradient, extent=[x_array.min(), x_array.max(), y_min, y_max], origin="lower", aspect="auto", zorder=0.2)  # 添加轻微纵向渐变填色，避免单色块压过数据线
    image.set_clip_path(clip.get_paths()[0], transform=ax.transData)
    return image


def save_publication_figure(fig, stem: str):
    fig.savefig(OUT_DIR / f"{stem}.svg", bbox_inches="tight")  # 导出可编辑 SVG，适合论文排版和后期文字微调
    fig.savefig(OUT_DIR / f"{stem}.pdf", bbox_inches="tight")  # 导出矢量 PDF，适合投稿和印刷
    fig.savefig(OUT_DIR / f"{stem}.tiff", dpi=600, bbox_inches="tight")  # 导出 600 dpi TIFF，满足常见期刊位图要求
    fig.savefig(OUT_DIR / f"{stem}.png", dpi=300, bbox_inches="tight")  # 导出 PNG 预览图，方便快速检查和汇报


def main():
    x, baseline, treatment = build_demo_data()

    fig, ax = plt.subplots(figsize=(3.6, 2.8), constrained_layout=True)  # 设置单栏图尺寸并自动优化边距
    ax.plot(x, baseline, color=PALETTE["baseline"], lw=1.4, marker="o", ms=3.0, label="Baseline")  # 绘制对照组曲线并设置颜色、线宽和点大小
    ax.plot(x, treatment, color=PALETTE["hero"], lw=1.8, marker="o", ms=3.2, label="Treatment")  # 绘制处理组曲线并用主色突出核心结果
    add_gradient_between(ax, x, baseline, treatment, color=PALETTE["hero"], alpha_top=0.28, alpha_bottom=0.04)  # 用轻微渐变填色强调两组差异区域，避免单色填充显得笨重

    ax.set_xlabel("Time (a.u.)", labelpad=4)  # 设置横轴标题和标题距离，说明时间或过程维度
    ax.set_ylabel("Response (a.u.)", labelpad=4)  # 设置纵轴标题和标题距离，说明响应变量
    ax.set_xticks(x)  # 固定横轴刻度位置，保证每个时间点都可见
    ax.tick_params(axis="both", labelsize=8.5, length=3, width=0.8, colors=PALETTE["ink"])  # 调整刻度字号、长度、粗细和颜色，避免导出后文字过小
    ax.spines["left"].set_color(PALETTE["ink"])  # 设置左侧轴线颜色，让坐标轴和文字颜色一致
    ax.spines["bottom"].set_color(PALETTE["ink"])  # 设置底部轴线颜色，让坐标轴和文字颜色一致
    ax.legend(loc="upper left", fontsize=8.5, handlelength=1.8)  # 设置图例位置、字号和线段长度，避免遮挡主要趋势且不低于最小可读字号
    ax.text(0.98, 0.08, "replace demo data", transform=ax.transAxes, ha="right", va="bottom", fontsize=8.5, color=PALETTE["accent"])  # 添加右下角无框提示文字，提醒替换示例数据

    save_publication_figure(fig, "figure_demo")
    plt.close(fig)


if __name__ == "__main__":
    main()
'''


README_TEMPLATE = """# Figure Job

This folder was generated by `scientific-figure-team`.

Files:

- `plot_figure.py`: Python-first starter figure script with Chinese comments on visual-affecting lines.
- `outputs/`: exported SVG/PDF/TIFF/PNG files after running the script.

Recommended commands:

```bash
python3 plot_figure.py
python3 ../skills/scientific-figure-team/scripts/validate_python_comments.py plot_figure.py
python3 ../skills/scientific-figure-team/scripts/audit_rendered_figure.py outputs/figure_demo.svg plot_figure.py
```
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a scientific figure project scaffold.")
    parser.add_argument("project_dir", help="Output project directory")
    args = parser.parse_args()

    project_dir = Path(args.project_dir).expanduser().resolve()
    project_dir.mkdir(parents=True, exist_ok=True)
    (project_dir / "outputs").mkdir(exist_ok=True)
    (project_dir / "plot_figure.py").write_text(PLOT_TEMPLATE, encoding="utf-8")
    (project_dir / "README.md").write_text(README_TEMPLATE, encoding="utf-8")
    print(f"Created figure project: {project_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
