---
name: scientific-figure-team
description: Python-first scientific figure workflow with subagent-style roles for raw-data-gated quantitative plotting, literature/method-search-backed preprocessing, English pre-plot plan confirmation, publication-ready matplotlib/seaborn outputs, Chinese inline explanations on visual-affecting Python code, QA, final rendered-image audit, and readability gates for MOF plots including PXRD, TGA, gas adsorption, Qst, IAST, breakthrough curves, mechanism schematics, workflow diagrams, multi-panel paper figures, figure redesigns, text-overlap fixes, small-font fixes, and unclear figure repair. Use when the user asks for 科研绘图, MOF 绘图, PXRD, 热重, 气体吸附, Qst, IAST, 穿透曲线, 论文图表, 论文配图, 出图, Python plotting, publication figures, mechanism figures, chart selection, figure polish, text overlap, 字体太小, 文字重叠, 图不清晰, or journal-ready SVG/PDF/TIFF outputs.
---

# Scientific Figure Team

This is a Python-first research figure workflow. Use it to turn raw data, manuscript text, mechanisms, processes, or style references into method-grounded preprocessing plans, English figure plans, Python plotting code, exported figures, QA reports, and final rendered-image audit.

## Operating Rule

Default to Python for all drawing, previewing, exporting, and visual QA. Use `matplotlib`, `seaborn`, `numpy`, `pandas`, and standard Python imaging/data tools as needed. Do not switch to R or another plotting backend unless the user explicitly leaves this skill and asks for a non-Python workflow.

Default typography is Arial-first but single-font only: check whether Arial is actually available in the runtime, use it for normal text, numbers, and mathtext when available, and otherwise use one unified DejaVu Sans family. Never set a visible multi-font fallback chain that can mix normal labels and subscript/superscript digits.

Default fill treatment is gradient-first: when an area, confidence band, module, or background needs fill color, use a subtle low-contrast gradient instead of a flat solid fill unless the confirmed plan explicitly justifies a solid fill.

For quantitative figures, enforce this gate order:

1. Require raw machine-readable data (`csv`, `xlsx`, `txt`, instrument export, or equivalent). Do not plot quantitative claims from screenshots or prose-only summaries.
2. Search relevant literature, instrument/software documentation, or user-provided methods before preprocessing. If live search is unavailable and no user method is provided, stop and ask for method references.
3. Write a `method_search_packet` with searched sources, chosen preprocessing method, assumptions, and rejected alternatives.
4. Produce an English pre-plot figure plan for user confirmation.
5. Preprocess data only after the method rationale is documented; produce final plots only after the plan is confirmed.

Before drawing, establish the figure contract:

1. Core conclusion: the one-sentence claim or message the figure must defend.
2. Evidence chain: which data/text supports each panel and what must not be invented.
3. Figure lane: data/result figure, mechanism/schematic, workflow/process figure, composite multi-panel figure, style-aligned redesign, or direct execution.
4. Export contract: intended use, dimensions, editable text, required formats, raw-data/preprocessing files, and source-data/statistics notes.
5. Review risk: missing fields, unsupported claims, image-integrity risks, and visual ambiguity.

## Team Workflow

When subagents or team tools are available, the lead agent should dispatch these roles rather than simulating everything in one voice:

- `figure-task-router`: classify the task lane and identify only blocking missing inputs.
- `figure-execution-planner`: create the method-grounded execution pack: preprocessing plan, panel map, layout, palette, annotations, caption draft, and drawing brief.
- `figure-python-plotter`: preprocess after method rationale, write and run Python plotting code, export SVG/PDF/TIFF/PNG, and keep all visual-affecting code lines Chinese-commented.
- `figure-qa-reviewer`: audit scientific logic, visual clarity, export quality, and code-comment compliance.
- `figure-image-final-auditor`: inspect final rendered images for visible unit, subscript/superscript, redundant guide-line, PXRD/Raman/FTIR direct-label placement, CV scan-rate placement, guide-line/text overlap, small-font, text-overflow, boxed-remark, gridline, panel-label, overlap, and MOF-convention issues. If it returns `FAIL_AND_REDRAW`, the figure must be sent back to `figure-python-plotter` for redraw before delivery.

If subagents are unavailable, perform the same stages explicitly in separate sections and keep the role boundaries intact.

## Routing Defaults

- Data/result figures: require raw machine-readable data, method search, preprocessing rationale, and a confirmed English plan before plotting.
- MOF figures: for PXRD, TGA, gas adsorption, Qst, IAST, breakthrough curves, CV/electrochemical plots, stacked Raman/FTIR spectra, and common MOF plots, read `references/mof-templates.md` and prefer the bundled template script.
- Mechanism/schematic figures: compress prose into objects, modules, arrows, causal order, boundaries, and labels. Do not invent mechanism certainty.
- Workflow/process figures: show stage order, inputs/outputs, decisions, and experiment conditions with consistent shapes and spacing.
- Composite paper figures: use one claim-driven panel order, stable color semantics, and consistent typography across panels.
- Existing-figure optimization: diagnose information structure, palette, layout, annotation, legend, fonts, and visual focus before editing.
- Confirmed execution: proceed to Python generation only when raw-data, method-search, preprocessing, and plan-confirmation gates are satisfied.

Ask only the minimum blocking question when correctness would otherwise fail, such as missing group identities, ambiguous comparison direction, unreadable files, or absent source data for a claimed result.

## Required References

Open only the references needed for the current task:

- `references/figure-contract.md`: use for routing, execution-pack structure, and figure contract details.
- `references/method-search-and-preprocessing.md`: always use before preprocessing quantitative raw data.
- `references/mof-templates.md`: use for PXRD, TGA, gas adsorption, Qst, IAST, breakthrough, and common MOF plots.
- `references/style-system.md`: use when choosing palette, layout, panel style, or matching the default reference-image aesthetic.
- `references/python-code-comment-rules.md`: always use before writing or modifying plotting code.
- `references/qa-checklist.md`: use before final delivery, especially when exporting figures or reviewing existing code.
- `scripts/audit_rendered_figure.py`: run on exported SVG files and plotting scripts when checking text size, overflow, boxed remarks, gridlines, and panel-label placement.

## Python Code Rule

Every Python line that affects figure position, color, formatting, dimensions, fonts, axes, labels, legends, annotations, layout, or export must end with a Chinese explanation comment. Examples:

```python
fig, ax = plt.subplots(figsize=(7.2, 4.8), constrained_layout=True)  # 控制整张图尺寸并自动压紧面板间距
ax.plot(x, y, color="#2F6F73", lw=1.8, marker="o")  # 设置主曲线颜色、线宽和数据点标记
fig.savefig("figure.svg", bbox_inches="tight")  # 导出可编辑 SVG 并裁掉多余白边
```

Run `scripts/validate_python_comments.py <plot_script.py>` before delivering generated plotting code. If it fails, fix the comments before final response.

## Execution Artifacts

For a real drawing task, deliver as many of these as the input supports:

- Method search packet and preprocessing rationale.
- English pre-plot figure plan and confirmation status.
- Processed data files saved separately from raw data.
- Figure contract and execution pack.
- Python plotting script with Chinese line-end explanations.
- Exported SVG/PDF/TIFF and PNG preview when runtime and dependencies allow.
- Figure caption draft that does not invent data or statistical significance.
- QA report listing checked items, limitations, and any missing source-data/statistics details.
- Rendered-readability audit from `audit_rendered_figure.py` when SVG exports are available.
- Final rendered-image audit result; do not deliver final figures when this audit fails unless the user explicitly accepts a blocked limitation.

For new figure projects, use:

```bash
python3 skills/scientific-figure-team/scripts/scaffold_figure_project.py figure_job
```

Then adapt `figure_job/plot_figure.py` to the user's data and run the comment validator before export.

For MOF templates, use:

```bash
python3 skills/scientific-figure-team/scripts/mof_figure_templates.py init mof_job
```

Then follow `mof_job/figure_plan.md` and `mof_job/method_search_packet.md` before preprocessing or plotting.
