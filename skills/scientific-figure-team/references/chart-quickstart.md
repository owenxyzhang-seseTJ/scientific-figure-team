# General Chart Quickstart Presets

Use these presets for common non-MOF scientific charts. They follow the same style system (`references/style-system.md`) and code-comment rules (`references/python-code-comment-rules.md`). For quantitative data, the raw-data and method-search gates in `references/method-search-and-preprocessing.md` still apply before preprocessing or plotting.

## Bar Chart (summarized group data)

- Use bars only when values are group summaries; overlay individual points when raw replicates exist.
- Bars: `width=0.55`, semantic color from the project palette, thin edge (`edgecolor` matching `ink` at `lw=0.6`).
- Error bars: `ax.errorbar(..., fmt="none", elinewidth=1.0, capsize=3)`; state what the error represents (SD, SEM, CI) in the caption — never invent it.
- Baseline at zero; do not truncate the y-axis on bar charts.

## Box / Violin / Dot Plot (raw replicate data)

- Prefer these over bars whenever raw replicate data are available.
- Box: show median and IQR; add jittered points (`jitter width <= 0.08`) or a swarm overlay at `alpha=0.7`.
- Violin: `inner="quart"`; avoid kernel outlines when n < 5 per group.
- Annotate n per group; use the unboxed annotation style (no `bbox=`).

## Heatmap (matrix / multidimensional data)

- Use a perceptually uniform colormap (`viridis`, `cividis`) unless the data are genuinely cyclic/spectral; document the mapping otherwise.
- Annotate cells only when the matrix is small enough that values remain readable at >= 8 pt.
- Order rows/columns deliberately (clustered, or in stated experimental order); never leave arbitrary ordering unexplained.

## Scatter with Fit (correlations)

- Fit a model only when justified (linear/Pearson for linear relations; state the model otherwise).
- Draw the fit line with `ax.plot`, and render the confidence band with `ax.fill_between(..., alpha=0.2)` — subtle, not flat.
- Report r, R², n, and p in the figure or caption only when computed from supplied data; do not estimate them visually.
- Do not imply causation from a correlation panel.

## Time Series / Trajectory

- Line plots for trends; add individual trajectories or uncertainty bands (`fill_between`, `alpha=0.15-0.25`) when raw data permit.
- State the time unit from raw metadata; no default units.

## Shared Rules

- Default figure text is English; code comments are Chinese, per `references/python-code-comment-rules.md`.
- No gridlines by default; no boxed annotations; panel labels outside each subplot's upper-left.
- Visible text >= 8.5 pt; never below 8 pt.
- Colors come from the project palette (or `PALETTE_COLORBLIND_SAFE` when colorblind-safe encoding is required), with stable semantics across panels.
