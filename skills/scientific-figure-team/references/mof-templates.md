# MOF Plot Templates

Use this reference for MOF quantitative figures. Figure text defaults to English, while Python code comments remain Chinese.

## Shared Requirements

- Require raw machine-readable data.
- Search or receive accepted processing methods before preprocessing.
- Save processed CSV files in `data_processed/`.
- Keep one pastel palette across a project.
- Use native matplotlib mathtext for labels: `CO$_2$`, `N$_2$`, `Q$_{st}$`, `cm$^3$ g$^{-1}$`, `m$^2$ g$^{-1}$`.

## PXRD

Raw long CSV columns:

```text
sample,state,two_theta,intensity
```

Default preprocessing:

- Normalize each pattern independently to max intensity 100.
- Canonical state order: `simulated`, `as-synthesized`, `solvent-exchanged`, `activated`.
- Add vertical offsets in that order.
- Place direct labels above each trace near the curve's right end, inside the axes and close to the corresponding line. Do not move all labels to the plot's top-right corner or outside the axes.
- Do not compare absolute intensity after normalization.

## TGA

Raw CSV columns:

```text
sample,state,temperature,mass
```

Optional columns:

```text
segment,baseline_start
```

Default preprocessing:

- Normalize selected starting point to 100%.
- For ordinary samples, use the first point as baseline.
- If activated phase includes hold/cooling/reheating, use the first reheating point after cooling as 100%.
- If the activated baseline is ambiguous, stop and ask for a segment marker or baseline start point.

## Gas Adsorption

Raw CSV columns:

```text
sample,gas,branch,pressure,uptake
```

Optional columns:

```text
pressure_unit
```

Default plotting:

- Scatter plot.
- Adsorption branch: filled markers.
- Desorption branch: hollow markers.
- The x-axis defaults to `P/P$_0$`; if raw data provide `pressure_unit`, use that unit instead of forcing relative pressure.
- Keep sample colors stable across all gas adsorption, Qst, and IAST panels.

## Qst

Raw/preprocessed CSV columns:

```text
sample,loading,qst
```

Default plotting:

- Plot `Q$_{st}$` vs loading.
- Do not compute Qst unless multi-temperature isotherms, model choice, gas constant/temperature units, and fitting assumptions are confirmed.

## IAST

Raw/preprocessed CSV columns:

```text
sample,gas_pair,composition,pressure,selectivity
```

Required metadata:

- gas pair
- composition basis
- temperature
- pressure unit
- selectivity definition

## Breakthrough Curves

Raw CSV columns:

```text
sample,component,time,c_over_c0
```

Optional columns:

```text
bed_volume,cycle,time_unit,threshold,show_threshold
```

Default plotting:

- Plot `C/C$_0$` vs time or bed volume.
- Gas components must render with native molecule subscripts, such as `CO$_2$`, `N$_2$`, `CH$_4$`, and `H$_2$`.
- The x-axis defaults to `Time (min/g)` for breakthrough data unless raw data specify another `time_unit`; if raw data use `min g^-1`, render it as `min g$^{-1}$`.
- Support multiple components with stable pastel colors.
- Add threshold/reference markers only when `show_threshold` is explicitly true or the user confirms the marker in the plan; do not add a dashed threshold line by default.

## Common Auxiliary MOF Plots

Use generic templates for:

- pore-size distributions
- BET surface area comparisons
- cycling stability
- selectivity/bar comparisons
- uptake vs pressure or temperature
- CV/electrochemical multi-scan comparisons
- stacked Raman, FTIR, UV-Vis, or other spectra

For every auxiliary plot, record whether values are raw, fitted, or copied from instrument/software outputs.

For stacked spectra, label each trace directly above the line near its right end or another locally flat end segment when this is readable. Keep labels close to their trace, but do not lock labels to a default coordinate: if they overlap peaks, dashed guide lines, axes, legends, or other labels, move them to the nearest whitespace lane and use a subtle leader line when needed. Peak labels should be offset from dashed or vertical guide lines; the line must not run through the text.

For CV/electrochemical multi-scan plots, document the smoothing or denoising method before applying it. Use light smoothing that preserves peak positions and relative peak heights unless the method packet justifies stronger processing. Put scan-rate labels inside each panel's axes box by default, in the least obstructive corner, and keep panel labels outside the axes.
