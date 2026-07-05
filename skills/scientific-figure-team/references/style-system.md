# Style System

Use this reference when choosing palette, layout, typography, and reference-style adaptation.

## Default Aesthetic

The default style is academic, clean, dense but orderly:

- Light background, fresh pastel low-saturation palette, thin lines, clear English labels.
- Multi-panel layouts with unified margins, stable panel labels, and consistent font hierarchy.
- Statistics panels use clean axes, no gridlines by default, and minimal decorative effects.
- Mechanism and workflow panels use modular cards, rounded borders, thin arrows, and enough whitespace.
- Use visual emphasis to highlight the main conclusion rather than giving every element equal weight.

The user's preferred reference direction is represented by these image names when available: `IMG_3426 2.JPG`, `IMG_3751.JPG`, `IMG_3752.JPG`, `IMG_3753.JPG`, `IMG_3754.JPG`.

## Palette Defaults

Use one unified fresh pastel palette per project. Keep the same sample/state color across PXRD, adsorption, Qst, IAST, and breakthrough panels.

```python
PALETTE = {
    "simulated": "#9AA4B2",
    "as_synthesized": "#83B6C8",
    "solvent_exchanged": "#A6C98F",
    "activated": "#E6B07E",
    "hero": "#5DA9A6",
    "hero_soft": "#CFE8E6",
    "accent": "#D99A8B",
    "accent_soft": "#F3D1C9",
    "positive": "#8FBC8F",
    "negative": "#D48A8A",
    "ink": "#27323A",
    "muted": "#70777F",
    "panel_bg": "#F7FAF8"
}
```

Keep semantic meaning stable across panels. Do not use rainbow colormaps for scientific emphasis unless the data are genuinely cyclic/spectral and the mapping is documented.

## Layout Rules

- Prefer one hero panel plus subordinate evidence panels for composite figures.
- Use direct labels when the category position is fixed and the legend would slow reading.
- Direct-label positions are adaptive, not fixed. Start near the relevant line/curve end, but move labels to nearby whitespace or add a subtle leader line whenever the default position overlaps data, guide lines, axes, legends, or other labels.
- Keep panel labels lowercase (`a`, `b`, `c`) for Nature-style figures unless the user requests uppercase.
- Place multi-panel labels outside the plotting area at the upper-left of each subplot, such as `x=-0.10, y=1.04` in axes coordinates or with `fig.text`; do not place panel letters inside the data rectangle.
- Use white plot backgrounds; use black backgrounds only for microscopy or image plates where the source modality benefits.
- Keep figure dimensions explicit and publication-oriented. Typical starts: single panel 3.4 x 2.6 inches, double-column panel group 7.2 x 4.8 inches, complex composite 7.2 x 7.0 inches.
- Use `svg.fonttype = "none"` and `pdf.fonttype = 42` so text remains editable.
- Default figure text is English. Code comments and editable-code explanations are Chinese.
- Use one actual font family across the entire figure. Prefer `Arial` when it is installed; if it is unavailable, select one unified `DejaVu Sans` family. Do not set a long fallback chain that makes normal text, numbers, and mathtext render in different fonts.
- Configure matplotlib mathtext to match the selected single font. With `DejaVu Sans`, set `mathtext.fontset = "dejavusans"` and `mathtext.default = "regular"`; with Arial, use `mathtext.fontset = "custom"` and map `mathtext.rm`, `mathtext.it`, and `mathtext.bf` to explicit Arial style patterns such as `Arial:style=normal`. This keeps subscript/superscript digits visually consistent with English labels.
- Use slightly larger text by default: base 9 pt, axis labels 10 pt, legends 8.5-9 pt, panel labels 11 pt bold.
- Treat visible text below 8 pt as unreadable and text below 8.5 pt as a default failure unless the figure is a deliberate thumbnail-free vector export with a documented exception.
- If a multi-panel figure cannot fit labels at readable sizes, enlarge the figure, reduce panel count, externalize legends/annotations, or split the figure; do not shrink text to force the layout.
- For in-panel legends such as CV scan-rate labels, choose the least obstructive corner inside the axes box when the scientific convention or user request requires in-box labels.
- Use native matplotlib mathtext for subscript/superscript labels, for example `CO$_2$`, `N$_2$`, `m$^2$ g$^{-1}$`, and `cm$^3$ g$^{-1}$`.
- Do not use gridlines by default. Add subtle gridlines only when the confirmed plan says they are essential for reading quantitative values.
- Do not put annotation text inside framed, rounded, or bordered boxes by default. Prefer unboxed direct labels, short leader lines, or a separate annotation lane outside the data region.
- When an area, band, card, module, or background needs fill color, use a subtle low-contrast gradient rather than a flat solid block. Keep the gradient quiet enough that data, labels, and axes remain dominant.

## Mechanism And Workflow Rules

- Convert long text to short labels, not paragraph boxes.
- Arrows must encode direction or causality; avoid arrows as decoration.
- Use dashed arrows for inferred/speculative relations and solid arrows for supported steps.
- Keep module boundaries visible through subtle fills or borders.
- Use gentle gradient fills for modules that need color fill; avoid heavy flat color panels.
- Link schematic colors to data panels when both appear in one figure.
