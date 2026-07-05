# Figure QA Checklist

Use this before final delivery or when auditing an existing figure.

## Scientific Logic

- Core claim is visible and evidence-bounded.
- Raw machine-readable data are present for quantitative plots.
- Method search or user-provided method references are documented before preprocessing.
- Preprocessing assumptions and rejected alternatives are recorded.
- English pre-plot plan is confirmed before final plotting.
- Each panel supports a distinct part of the claim.
- No invented values, significance, sample size, mechanisms, or missing controls.
- Baselines, treatment groups, time windows, and units are clear.
- Caption distinguishes observed data from proposed interpretation.

## Visual Clarity

- Panel order matches the reading logic.
- Color semantics are stable across panels.
- Main conclusion is visually emphasized without hiding contradictory or null results.
- Labels, ticks, legends, and annotations remain readable at final figure size.
- Visible text is not too small: no text below 8 pt, and no default figure text below 8.5 pt unless a documented exception is accepted.
- No text-text overlap, text-axis overlap, text-legend overlap, or text-image overlap is detected in the exported/rendered figure.
- Text does not overflow the canvas, touch the edge, or get clipped by `bbox_inches="tight"`.
- Multi-panel labels (`a`, `b`, `c`) sit outside the plotting area at each subplot's upper-left; they do not cover data, axes, or titles.
- Annotation remarks are not enclosed in boxes by default; no `bbox=dict(...)`, rounded callout box, bordered note box, or framed legend is used unless explicitly justified.
- Gridlines are absent by default; any gridline must be subtle, plan-confirmed, and less prominent than the data.
- Molecule names and scientific units use native sub/superscripts where needed, such as `CO$_2$`, `N$_2$`, `P/P$_0$`, `C/C$_0$`, `Q$_{st}$`, and `min g$^{-1}$`; breakthrough defaults to `min/g` when no raw unit is provided.
- Subscript/superscript digits visually match the English label font. Matplotlib scripts using mathtext must configure mathtext from the selected single font: Arial custom mathtext when Arial is available, otherwise DejaVu Sans mathtext.
- Only one actual font family is used across the visible figure. Prefer Arial when available; otherwise use DejaVu Sans consistently rather than mixing fallback fonts.
- Axis units match raw-data metadata when provided; defaults are allowed only when the raw data do not specify units.
- Redundant threshold, guide, or reference lines are absent unless explicitly confirmed.
- PXRD/Raman/FTIR stacked traces are labelled directly above each corresponding curve near the curve's right end or a locally flat end segment when this is readable; if the default position overlaps anything, labels move to the nearest whitespace lane with a short leader line when needed.
- Peak/guide-line labels do not sit on top of dashed or vertical guide lines; no guide line runs through readable text.
- CV/electrochemical scan-rate labels are inside the relevant axes box by default and do not cover the CV loops.
- Filled areas, confidence bands, module fills, and background fills use subtle gradients by default rather than heavy flat color blocks.
- Red/green is not the only encoding for critical distinctions.
- Gridlines, borders, and decorative elements do not compete with data.

## Final Rendered-Image Gate

- Run `figure-image-final-auditor` or perform the equivalent rendered-image inspection after normal QA.
- Run `scripts/audit_rendered_figure.py` on exported SVG files and plotting scripts when available; treat failures as redraw blockers.
- Treat overlap and overflow as zero-tolerance failures: no text-text, text-legend, text-data, text-axis, text-tick, text-image, or guide-line/text overlap; no clipped, cropped, outside-canvas, or edge-crowded labels.
- If the final image audit returns `FAIL_AND_REDRAW`, send exact required fixes back to the Python plotter, redraw, rerun overlap/export checks, and repeat the final image audit.
- Do not deliver a final quantitative figure with a failed rendered-image audit unless the user explicitly accepts a documented blocker.

## Python And Export

- Generated plotting code passes `validate_python_comments.py`.
- Overlap checks are run with the bundled checker or an equivalent rendered inspection.
- SVG text remains editable with `svg.fonttype = "none"`.
- PDF text uses TrueType embedding with `pdf.fonttype = 42`.
- At least SVG and PNG preview are exported when dependencies allow; add PDF/TIFF for paper-ready delivery.
- Figure is closed after saving to avoid memory and state bleed.
- Output filenames are clear and do not overwrite user originals.

## Existing Image Integrity

- Cropping, contrast changes, pseudo-coloring, stitching, or reused image regions are documented.
- Scale bars are present when needed and not invented when pixel scale is unknown.
- Do not make microscopy/blot/image edits that alter scientific content unless the user explicitly requests a transparent presentation-only adjustment.

## Final Report

Return:

- Files generated or modified.
- Export formats and paths.
- Raw data files and processed data files.
- Method search packet and plan-confirmation status.
- Any limitations or missing information.
- Whether code-comment validation passed.
- Whether final rendered-image audit passed or the redraw loop remains blocked.
