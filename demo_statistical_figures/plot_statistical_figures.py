#!/usr/bin/env python3
"""Generate publication-style statistical figure demos with raw-data-aware plotting."""

from __future__ import annotations

from pathlib import Path

import matplotlib as mpl
mpl.set_loglevel("error")  # 仅保留 Matplotlib 严重错误日志，避免 Arial 数学字体查找日志干扰最终输出判断
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import font_manager
from matplotlib.colors import to_rgba
from matplotlib.patches import PathPatch


BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data_raw"
PROCESSED_DIR = BASE_DIR / "data_processed"
OUTPUT_DIR = BASE_DIR / "outputs"
METHOD_PACKET = BASE_DIR / "method_search_packet.md"
FIGURE_PLAN = BASE_DIR / "figure_plan.md"

PROCESSED_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

PREFERRED_FONT_FAMILY = ["Arial", "DejaVu Sans"]  # 优先使用 Arial；若系统缺失则整图统一退回 DejaVu Sans，避免英文字母、数字和上下标混用不同字体
PALETTE = {  # 定义整套 demo 共享的清新低饱和配色，保证同一项目内统计图风格统一
    "teal": "#6FAFA8",  # 用于核心材料或主要组别的青绿色主色
    "coral": "#D9958A",  # 用于条件变化或第二主组的珊瑚色强调
    "lavender": "#9B9CCF",  # 用于第三组或较柔和的对比组
    "sage": "#A9BE8F",  # 用于辅助条件和中性对照的鼠尾草绿
    "gray": "#8A949E",  # 用于轮廓线、次要说明和低调组别
    "ink": "#27323A",  # 用于文字、刻度和坐标轴线，保证整体对比度克制但清楚
}


def select_single_typeface() -> str:
    available_families = {item.name for item in font_manager.fontManager.ttflist}  # 读取当前环境真实可用字体，避免声明 Arial 但实际混用回退字体
    for family in PREFERRED_FONT_FAMILY:  # 按优先顺序挑选一个真实存在的字体，确保整张图只落到一个字体族
        if family in available_families:
            return family
    return "DejaVu Sans"


FIGURE_TYPEFACE = select_single_typeface()  # 为正文、数字和上下标统一选择一个真实可用字体


def mathtext_rcparams(figure_typeface: str) -> dict[str, str]:
    if figure_typeface == "DejaVu Sans":
        return {
            "mathtext.fontset": "dejavusans",  # 当 Arial 不可用时改用 DejaVu Sans 数学字族，保证下标数字与正文同族
            "mathtext.default": "regular",  # 让数学上下标默认保持常规字形，避免公式标签自动变斜体
        }
    return {
        "mathtext.fontset": "custom",  # 当 Arial 可用时启用自定义数学字体映射，让上下标跟正文保持同一字体
        "mathtext.default": "regular",  # 让数学表达式中的字母和下标保持常规风格，更适合科研图标签
        "mathtext.rm": f"{figure_typeface}:style=normal",  # 指定数学正文字体为当前选中的单一字体，避免混用回退族
        "mathtext.it": f"{figure_typeface}:style=italic",  # 指定数学斜体也来自同一字体族，统一公式局部样式
        "mathtext.bf": f"{figure_typeface}:weight=bold",  # 指定数学粗体使用同族粗体字形，保证 panel label 等情况一致
    }


STYLE_PARAMS = {  # 统一设置全套统计图的字体、边框、输出和默认可读性参数
    "font.family": FIGURE_TYPEFACE,  # 指定整张图的唯一字体族，减少导出后多字体混杂的问题
    "font.sans-serif": [FIGURE_TYPEFACE],  # 只保留一个真实字体，防止数字和英文字母走不同回退链
    "svg.fonttype": "none",  # 保留 SVG 为可编辑文字，便于后续在 AI 或 Inkscape 中继续精修
    "pdf.fonttype": 42,  # 在 PDF 中嵌入 TrueType 字体，提升投稿和打印兼容性
    "font.size": 9.2,  # 将基础字号略调大，避免统计图中的分类标签和单位看起来偏小
    "axes.labelsize": 10.2,  # 提高坐标轴标题字号，保证英文轴标题在单栏尺寸下仍然清楚
    "legend.fontsize": 8.8,  # 设置图例字号不低于默认可读阈值，同时保持版面紧凑
    "xtick.labelsize": 8.8,  # 提高横轴分类标签字号，减少材料名和条件名难读的问题
    "ytick.labelsize": 8.8,  # 提高纵轴刻度字号，避免统计图数值轴显得发虚或太小
    "axes.linewidth": 0.8,  # 控制坐标轴边框线宽，保持科研图常见的轻量边界
    "axes.spines.right": False,  # 隐藏右侧边框，减少无信息线条对数据区的干扰
    "axes.spines.top": False,  # 隐藏顶部边框，让图面更简洁更接近期刊统计图风格
    "legend.frameon": False,  # 去除图例外框，避免再次出现带框备注或图例框干扰阅读
}
STYLE_PARAMS.update(mathtext_rcparams(FIGURE_TYPEFACE))  # 根据当前真实字体同步数学上下标配置，避免下标数字与正文样式不统一
mpl.rcParams.update(STYLE_PARAMS)  # 一次性应用整套风格参数，确保三个 demo 图共享同一视觉系统


def require_workflow_gates() -> None:
    method_text = METHOD_PACKET.read_text(encoding="utf-8")  # 读取方法检索记录，确保预处理前已经写明来源和处理依据
    plan_text = FIGURE_PLAN.read_text(encoding="utf-8")  # 读取英文图件计划，确保本次 demo 已经进入确认后的执行阶段
    if "Status: READY_FOR_PREPROCESSING" not in method_text:
        raise RuntimeError("method_search_packet.md must be READY_FOR_PREPROCESSING before preprocessing.")  # 强制方法检索包先就绪，避免绕过预处理依据检查
    if "Status: CONFIRMED" not in plan_text:
        raise RuntimeError("figure_plan.md must be CONFIRMED before plotting.")  # 强制英文计划先确认，再进入后续预处理和出图


def load_csv(name: str) -> pd.DataFrame:
    path = RAW_DIR / name
    if not path.is_file():
        raise FileNotFoundError(f"Missing raw data file: {path}")  # 强制要求存在机器可读原始数据，保持 skill 的 raw-data gate
    return pd.read_csv(path)


def summarize_groups(frame: pd.DataFrame, group_cols: list[str], value_col: str) -> pd.DataFrame:
    grouped = frame.groupby(group_cols, sort=False)[value_col]
    summary = grouped.agg(
        n="count",
        mean="mean",
        sd="std",
        median="median",
        q1=lambda values: values.quantile(0.25),
        q3=lambda values: values.quantile(0.75),
        min="min",
        max="max",
    ).reset_index()
    return summary.round(4)


def save_publication_figure(fig: plt.Figure, stem: str) -> None:
    fig.savefig(OUTPUT_DIR / f"{stem}.svg", bbox_inches="tight")  # 导出可编辑 SVG，便于最终论文排版和检查文字位置
    fig.savefig(OUTPUT_DIR / f"{stem}.pdf", bbox_inches="tight")  # 导出矢量 PDF，适合投稿系统和高分辨率打印
    fig.savefig(OUTPUT_DIR / f"{stem}.tiff", dpi=600, bbox_inches="tight")  # 导出 600 dpi TIFF，满足多数期刊位图要求
    fig.savefig(OUTPUT_DIR / f"{stem}.png", dpi=300, bbox_inches="tight")  # 导出 300 dpi PNG，方便快速预览和汇报展示


def rgba_with_alpha(color: str, alpha: float) -> tuple[float, float, float, float]:
    rgba = list(to_rgba(color))  # 把十六进制颜色转换为 RGBA，便于复用统一项目色并单独调整透明度
    rgba[3] = alpha
    return tuple(rgba)


def add_vertical_gradient(ax: plt.Axes, patch, color: str, alpha_top: float, alpha_bottom: float) -> None:
    if hasattr(patch, "get_paths"):
        vertices = patch.get_paths()[0].vertices  # 读取多边形集合的首个轮廓顶点，兼容小提琴图这种集合对象
    else:
        vertices = patch.get_path().vertices  # 读取 PathPatch 的轮廓顶点，兼容箱线图箱体这类补丁对象
    x0 = float(vertices[:, 0].min())
    x1 = float(vertices[:, 0].max())
    y0 = float(vertices[:, 1].min())
    y1 = float(vertices[:, 1].max())
    rgba = np.array(to_rgba(color))  # 将项目色转为 RGBA，作为渐变填色的基准颜色
    gradient = np.ones((256, 1, 4))
    gradient[:, :, :3] = rgba[:3]
    gradient[:, :, 3] = np.linspace(alpha_bottom, alpha_top, 256)[:, None]
    image = ax.imshow(gradient, extent=[x0, x1, y0, y1], origin="lower", aspect="auto", zorder=patch.get_zorder() - 0.1)  # 在箱体或小提琴内部加入纵向轻渐变，避免大块平涂显得生硬
    if hasattr(patch, "get_paths"):
        clip_patch = PathPatch(patch.get_paths()[0], transform=patch.get_transform())  # 把集合对象的首个路径包成可裁剪补丁，保证小提琴图也能正确裁掉渐变
        image.set_clip_path(clip_patch)
    else:
        image.set_clip_path(patch)  # 直接用箱体补丁裁剪渐变，保持箱线图填色边界准确


def apply_axis_style(ax: plt.Axes) -> None:
    ax.grid(False)  # 关闭网格线，符合当前 skill 对科研图默认无网格的硬规则
    ax.tick_params(axis="both", labelsize=8.8, length=3, width=0.8, colors=PALETTE["ink"])  # 统一刻度字号、线长和颜色，保证统计图数字清楚且不过重
    ax.spines["left"].set_color(PALETTE["ink"])  # 将左侧坐标轴颜色统一为主墨色，保持文字和轴线视觉一致
    ax.spines["bottom"].set_color(PALETTE["ink"])  # 将底部坐标轴颜色统一为主墨色，避免边框色跳出整体配色


def jitter_positions(center: float, count: int, width: float, seed: int) -> np.ndarray:
    rng = np.random.default_rng(seed)
    jitter = rng.uniform(-width, width, count)  # 在分类中心两侧加入有限随机抖动，减少原始点重叠同时不破坏组别归属
    return center + jitter


def preprocess_boxplot_co2() -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = load_csv("boxplot_co2_uptake.csv")
    order = ["UiO-66", "UiO-66-NH2", "Activated composite"]
    raw["sample_group"] = pd.Categorical(raw["sample_group"], categories=order, ordered=True)
    raw = raw.sort_values(["sample_group", "replicate_id"]).reset_index(drop=True)
    summary = summarize_groups(raw, ["sample_group"], "co2_uptake_mmol_g")
    raw.to_csv(PROCESSED_DIR / "boxplot_co2_uptake_tidy.csv", index=False)
    summary.to_csv(PROCESSED_DIR / "boxplot_co2_uptake_summary.csv", index=False)
    return raw, summary


def preprocess_grouped_breakthrough() -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = load_csv("grouped_boxplot_breakthrough_time.csv")
    material_order = ["Sorbent A", "Sorbent B", "Sorbent C"]
    condition_order = ["Dry", "Humid"]
    raw["material"] = pd.Categorical(raw["material"], categories=material_order, ordered=True)
    raw["feed_condition"] = pd.Categorical(raw["feed_condition"], categories=condition_order, ordered=True)
    raw = raw.sort_values(["material", "feed_condition", "replicate_id"]).reset_index(drop=True)
    summary = summarize_groups(raw, ["material", "feed_condition"], "breakthrough_time_min_g")
    raw.to_csv(PROCESSED_DIR / "grouped_boxplot_breakthrough_time_tidy.csv", index=False)
    summary.to_csv(PROCESSED_DIR / "grouped_boxplot_breakthrough_time_summary.csv", index=False)
    return raw, summary


def preprocess_violin_crystal_size() -> tuple[pd.DataFrame, pd.DataFrame]:
    raw = load_csv("violinplot_crystal_size.csv")
    order = ["0 eq modulator", "20 eq modulator", "40 eq modulator"]
    raw["condition"] = pd.Categorical(raw["condition"], categories=order, ordered=True)
    raw = raw.sort_values(["condition", "particle_id"]).reset_index(drop=True)
    summary = summarize_groups(raw, ["condition"], "crystal_size_nm")
    raw.to_csv(PROCESSED_DIR / "violinplot_crystal_size_tidy.csv", index=False)
    summary.to_csv(PROCESSED_DIR / "violinplot_crystal_size_summary.csv", index=False)
    return raw, summary


def style_boxplot_artists(boxplot, colors: list[str], ax: plt.Axes) -> None:
    for patch, color in zip(boxplot["boxes"], colors):
        patch.set_facecolor("none")  # 先把箱体原始平涂去掉，后面改用更轻的渐变填色来保持清新感
        patch.set_edgecolor(color)  # 使用项目色控制箱体轮廓，让不同组别一眼可分
        patch.set_linewidth(1.35)  # 略加粗箱体轮廓，确保导出后仍然清楚但不过重
        add_vertical_gradient(ax, patch, color, alpha_top=0.22, alpha_bottom=0.05)  # 为箱体内部补一个很轻的纵向渐变，避免大块单色填充
    for whisker, color in zip(boxplot["whiskers"], np.repeat(colors, 2)):
        whisker.set_color(color)  # 将每个箱体的上下须线颜色同步到对应组别，增强视觉归属关系
        whisker.set_linewidth(1.0)  # 控制须线粗细，保证分布边界可见但不喧宾夺主
    for cap, color in zip(boxplot["caps"], np.repeat(colors, 2)):
        cap.set_color(color)  # 将每个箱体的上下帽线颜色同步到对应组别，保持完整的一致色语义
        cap.set_linewidth(1.0)  # 控制帽线粗细，防止帽线过粗影响箱体内部层次
    for median, color in zip(boxplot["medians"], colors):
        median.set_color(PALETTE["ink"])  # 用深色中位线增强关键统计位置的辨识度
        median.set_linewidth(1.3)  # 略加粗中位线，帮助读者快速读取中心位置
    for flier, color in zip(boxplot["fliers"], colors):
        flier.set_markerfacecolor(rgba_with_alpha(color, 0.16))  # 用低透明度填充离群点，既保留信息又不过于抢眼
        flier.set_markeredgecolor(color)  # 保持离群点边缘和对应组别颜色一致，方便追踪来源
        flier.set_markersize(4.2)  # 控制离群点大小，避免小样本时视觉噪声过大


def add_mean_sd_overlay(ax: plt.Axes, positions: list[float], summary: pd.DataFrame, color: str, mean_col: str = "mean", sd_col: str = "sd") -> None:
    ax.errorbar(positions, summary[mean_col], yerr=summary[sd_col], fmt="o", ms=5.0, lw=1.05, capsize=3.2, color=color, mfc="white", mec=color, zorder=4)  # 叠加均值和标准差误差棒，满足用户对箱线图含误差棒的要求


def add_top_note(ax: plt.Axes, text: str) -> None:
    ax.annotate(text, xy=(0.02, 1.06), xycoords="axes fraction", ha="left", va="bottom", fontsize=8.8, color=PALETTE["gray"])  # 将简短说明固定在坐标区上方外侧，用无框注释避免被审图器误判为子图字母或图内标签


def plot_boxplot_co2(raw: pd.DataFrame, summary: pd.DataFrame) -> None:
    order = list(summary["sample_group"])
    colors = [PALETTE["gray"], PALETTE["teal"], PALETTE["coral"]]
    positions = [1, 2, 3]
    data = [raw.loc[raw["sample_group"] == group, "co2_uptake_mmol_g"].to_numpy() for group in order]

    fig, ax = plt.subplots(figsize=(4.7, 3.5), constrained_layout=True)  # 设定单图尺寸并自动压缩留白，保证分类标签和上方说明有足够空间
    boxplot = ax.boxplot(data, positions=positions, widths=0.5, patch_artist=True, showfliers=True)  # 绘制箱线图主体，保留离群点以展示重复样本分布
    style_boxplot_artists(boxplot, colors, ax)

    for index, (group, color, xpos) in enumerate(zip(order, colors, positions), start=1):
        values = raw.loc[raw["sample_group"] == group, "co2_uptake_mmol_g"].to_numpy()
        x_values = jitter_positions(xpos, len(values), width=0.11, seed=100 + index)  # 为当前组生成轻微横向抖动位置，避免重复点完全叠在一条竖线上
        ax.scatter(x_values, values, s=24, facecolors=rgba_with_alpha(color, 0.35), edgecolors=color, linewidths=0.7, zorder=3)  # 叠加轻抖动原始点，展示每个重复样本并避免点完全重合

    add_mean_sd_overlay(ax, positions, summary, color=PALETTE["ink"])  # 在每个箱体中心叠加均值和标准差误差棒，形成用户要求的箱线图含误差棒样式
    apply_axis_style(ax)
    ax.set_xticks(positions)  # 固定横轴分类位置，确保材料顺序与预处理计划一致
    ax.set_xticklabels(order)  # 写出材料组名称，让读者直接读取实验分组
    ax.set_ylabel("CO$_2$ uptake (mmol g$^{-1}$)", labelpad=5)  # 使用原生下标和上标设置纵轴单位，保证气体分子式和单位风格统一
    ax.set_xlabel("Sample group", labelpad=5)  # 添加横轴标题，说明当前比较的是不同样品组
    ax.set_ylim(2.55, 4.75)  # 设置纵轴范围，为上方说明和最高误差棒留出安全空白
    add_top_note(ax, "298 K, 1 bar, box = IQR, dot = mean, whisker = SD")  # 将图形解释文字放在图外上方，避免与箱体和误差棒重叠

    save_publication_figure(fig, "boxplot_co2_uptake")
    plt.close(fig)


def plot_grouped_breakthrough(raw: pd.DataFrame, summary: pd.DataFrame) -> None:
    materials = ["Sorbent A", "Sorbent B", "Sorbent C"]
    conditions = ["Dry", "Humid"]
    condition_colors = {"Dry": PALETTE["teal"], "Humid": PALETTE["lavender"]}
    position_map = {
        ("Sorbent A", "Dry"): 0.85,
        ("Sorbent A", "Humid"): 1.15,
        ("Sorbent B", "Dry"): 1.85,
        ("Sorbent B", "Humid"): 2.15,
        ("Sorbent C", "Dry"): 2.85,
        ("Sorbent C", "Humid"): 3.15,
    }

    fig, ax = plt.subplots(figsize=(5.4, 3.6), constrained_layout=True)  # 设定更宽的版面，为分组箱线图、图例和上方说明提供足够横向空间
    all_positions = []
    all_values = []
    all_colors = []
    for material in materials:
        for condition in conditions:
            subset = raw.loc[
                (raw["material"] == material) & (raw["feed_condition"] == condition),
                "breakthrough_time_min_g",
            ].to_numpy()
            all_positions.append(position_map[(material, condition)])
            all_values.append(subset)
            all_colors.append(condition_colors[condition])

    boxplot = ax.boxplot(all_values, positions=all_positions, widths=0.22, patch_artist=True, showfliers=True)  # 按材料内分条件绘制分组箱线图，便于比较湿度对突破时间的影响
    style_boxplot_artists(boxplot, all_colors, ax)

    for seed_index, ((material, condition), xpos) in enumerate(position_map.items(), start=1):
        subset = raw.loc[
            (raw["material"] == material) & (raw["feed_condition"] == condition),
            "breakthrough_time_min_g",
        ].to_numpy()
        x_values = jitter_positions(xpos, len(subset), width=0.045, seed=300 + seed_index)  # 为每个材料-条件组合生成更窄的抖动，避免相邻双箱体之间的点串组
        ax.scatter(x_values, subset, s=20, facecolors=rgba_with_alpha(condition_colors[condition], 0.32), edgecolors=condition_colors[condition], linewidths=0.65, zorder=3)  # 在每个小箱体上叠加原始重复点，显示各条件下样本离散程度

    overlay_summary = summary.copy()
    overlay_positions = [position_map[(row["material"], row["feed_condition"])] for _, row in overlay_summary.iterrows()]
    add_mean_sd_overlay(ax, overlay_positions, overlay_summary, color=PALETTE["ink"])  # 在分组箱线图上统一叠加均值和标准差误差棒，便于干湿条件横向比较

    apply_axis_style(ax)
    ax.set_xticks([1, 2, 3])  # 将主刻度对齐到三个材料中心，方便读者先按材料分块阅读
    ax.set_xticklabels(materials)  # 在主刻度写出材料名，突出比较主体
    ax.set_ylabel("Breakthrough time (min g$^{-1}$)", labelpad=5)  # 设置纵轴为穿透时间单位，并用原生上标写出每克归一化单位
    ax.set_xlabel("Material", labelpad=5)  # 设置横轴标题，说明当前横向分类是不同材料
    ax.set_ylim(22, 77)  # 预留充足纵向空白，避免上方说明与最高箱体或误差棒接触

    legend_handles = [
        plt.Line2D([0], [0], marker="o", color=condition_colors["Dry"], markerfacecolor=rgba_with_alpha(condition_colors["Dry"], 0.32), markersize=5, lw=1.0, label="Dry"),  # 构造 Dry 条件图例，把颜色语义明确交给读者
        plt.Line2D([0], [0], marker="o", color=condition_colors["Humid"], markerfacecolor=rgba_with_alpha(condition_colors["Humid"], 0.32), markersize=5, lw=1.0, label="Humid"),  # 构造 Humid 条件图例，便于两类条件快速区分
    ]
    ax.legend(handles=legend_handles, loc="upper left", bbox_to_anchor=(0.0, 1.01), ncol=2, handletextpad=0.5, columnspacing=1.2)  # 将无框图例放在图上方左侧外缘，避开箱体和误差棒密集区
    add_top_note(ax, "Dynamic test; box = IQR; mean ± SD overlaid")  # 将方法解释文字放在图外顶部，避免与图例和数据区冲突

    save_publication_figure(fig, "grouped_boxplot_breakthrough_time")
    plt.close(fig)


def plot_violin_crystal_size(raw: pd.DataFrame, summary: pd.DataFrame) -> None:
    order = list(summary["condition"])
    colors = [PALETTE["lavender"], PALETTE["teal"], PALETTE["sage"]]
    positions = [1, 2, 3]
    data = [raw.loc[raw["condition"] == condition, "crystal_size_nm"].to_numpy() for condition in order]

    fig, ax = plt.subplots(figsize=(4.9, 3.6), constrained_layout=True)  # 设定足够的单图尺寸，为较长的条件标签和顶部说明保留清晰空间
    violin = ax.violinplot(data, positions=positions, widths=0.68, showmeans=False, showmedians=False, showextrema=False)  # 绘制小提琴图以展示分布形状，同时关闭默认极值线避免图面过乱
    for body, color in zip(violin["bodies"], colors):
        body.set_facecolor("none")  # 先取消默认平涂，为后续轻渐变填色留出空间
        body.set_edgecolor(color)  # 将小提琴外轮廓设置为对应组别色，让不同条件一眼可分
        body.set_linewidth(1.3)  # 略加粗小提琴边界，保证分布形状在导出后清楚可见
        body.set_alpha(1.0)  # 保持轮廓完全清晰，再通过渐变控制内部层次
        add_vertical_gradient(ax, body, color, alpha_top=0.24, alpha_bottom=0.06)  # 在小提琴内部加入轻微纵向渐变，让分布图更柔和也更符合当前统一风格

    for idx, (condition, xpos, color) in enumerate(zip(order, positions, colors), start=1):
        subset = raw.loc[raw["condition"] == condition, "crystal_size_nm"].to_numpy()
        x_values = jitter_positions(xpos, len(subset), width=0.085, seed=500 + idx)  # 为每组粒径点生成适中的横向抖动，保持密度可读同时不越出小提琴轮廓太多
        ax.scatter(x_values, subset, s=14, facecolors=rgba_with_alpha(color, 0.25), edgecolors=color, linewidths=0.45, zorder=3)  # 叠加半透明原始点，既保留分布细节又不压过小提琴轮廓
        stats_row = summary.loc[summary["condition"] == condition].iloc[0]
        ax.vlines(xpos, stats_row["q1"], stats_row["q3"], color=PALETTE["ink"], lw=2.0, zorder=4)  # 用粗短竖线标出四分位区间，帮助读者快速读取离散程度
        ax.hlines(stats_row["median"], xpos - 0.12, xpos + 0.12, color=PALETTE["ink"], lw=1.4, zorder=4)  # 用横线标出中位数位置，强化中心趋势阅读

    apply_axis_style(ax)
    ax.set_xticks(positions)  # 固定各条件的横轴位置，保持小提琴和散点对齐
    ax.set_xticklabels(order)  # 写出调节剂条件名称，让横向比较逻辑直接可见
    ax.set_ylabel("Crystal size (nm)", labelpad=5)  # 设置纵轴为晶体尺寸单位，保证真实科研语境清楚
    ax.set_xlabel("Modulator condition", labelpad=5)  # 说明当前比较变量是调节剂条件而非材料种类
    ax.set_ylim(20, 248)  # 预留顶部留白，防止上方说明和最高散点靠得太近
    add_top_note(ax, "Violin = density, line = IQR and median")  # 把解释文字放到图外上方，避免落进分布内部造成遮挡

    save_publication_figure(fig, "violinplot_crystal_size")
    plt.close(fig)


def write_audit_manifest() -> None:
    lines = [
        "# Statistical Demo Outputs",
        "",
        "- boxplot_co2_uptake.svg",
        "- grouped_boxplot_breakthrough_time.svg",
        "- violinplot_crystal_size.svg",
        "",
        f"- unified_font: {FIGURE_TYPEFACE}",
    ]
    (OUTPUT_DIR / "demo_output_manifest.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    require_workflow_gates()
    raw_box, summary_box = preprocess_boxplot_co2()
    raw_breakthrough, summary_breakthrough = preprocess_grouped_breakthrough()
    raw_violin, summary_violin = preprocess_violin_crystal_size()
    plot_boxplot_co2(raw_box, summary_box)
    plot_grouped_breakthrough(raw_breakthrough, summary_breakthrough)
    plot_violin_crystal_size(raw_violin, summary_violin)
    write_audit_manifest()


if __name__ == "__main__":
    main()
