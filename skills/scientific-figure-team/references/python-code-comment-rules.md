# Python Code Comment Rules

Use this reference before writing, editing, or delivering any Python plotting code.

## Non-Negotiable Rule

Every Python line that affects visual output must end with a Chinese explanation comment. The comment should explain what the line changes and how the user can modify it later.

Required comment scope:

- Figure size, aspect ratio, DPI, export format, `bbox_inches`, and layout padding.
- Colors, palettes, colormaps, alpha, gradients, fills, and background colors.
- Font family, font size, font weight, math text, label padding, title placement, and text color.
- Axes limits, ticks, tick labels, scales, spines, grids, and axis labels.
- Plot geometry: bar width, marker size, line width, scatter size, image extent, heatmap interpolation, arrow width, box positions, subplots, gridspec, and panel spacing.
- Legends, colorbars, annotations, arrows, callouts, panel labels, scale bars, and significance marks.
- `rcParams`, `style.use`, `subplots`, `subplot_mosaic`, `GridSpec`, `tight_layout`, `constrained_layout`, `subplots_adjust`, and `savefig`.

Acceptable comment examples:

```python
FIGSIZE = (7.2, 4.8)  # 控制整张图的宽高，改这里可以整体放大或压缩画布
PALETTE = {"hero": "#2F6F73", "baseline": "#7A7A7A"}  # 设定核心组和对照组颜色，保持所有面板语义一致
ax.tick_params(axis="both", labelsize=8.5, length=3, width=0.8)  # 调整刻度文字大小和刻度线长度/粗细，确保导出后仍清晰可读
```

Weak comments to avoid:

- `# plot`
- `# color`
- `# setting`
- `# 绘图`

The comment must be useful for later editing.

## Validation

Run:

```bash
python3 skills/scientific-figure-team/scripts/validate_python_comments.py path/to/plot_script.py
```

If the validator reports missing comments, fix every flagged line before delivering the code. Use `# figure-comment-exempt: 原因` only for false positives where the line does not affect visual appearance.

## Delivery Rule

When sending code in a response or writing a script, include the Chinese line-end comments directly in the code. Do not put explanations only in surrounding prose.
