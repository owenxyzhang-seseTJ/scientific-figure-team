# Statistical Figure Demo

This demo extends `scientific-figure-team` with realistic statistical figure examples that are common in chemistry, materials, catalysis, and adsorption projects.

All figure text is in English. The plotting code keeps Chinese line-end comments on visual-affecting lines.

## Demo scope

- `boxplot_co2_uptake`: replicate-level `CO$_2$` uptake comparison with boxplots, jittered raw points, and mean `±` SD error bars.
- `grouped_boxplot_breakthrough_time`: grouped boxplots for dry and humid breakthrough times with raw points and mean `±` SD.
- `violinplot_crystal_size`: crystal-size distributions across modulator conditions using violin plots, quartile lines, medians, and raw points.

## Workflow status

- Raw data: synthetic demo CSV files in `data_raw/`
- Method search packet: `method_search_packet.md`
- Figure plan: `figure_plan.md`
- Processed outputs: written to `data_processed/`
- Rendered outputs: written to `outputs/`

## Run

```bash
python3 generate_raw_data.py
python3 plot_statistical_figures.py
python3 ../skills/scientific-figure-team/scripts/validate_python_comments.py plot_statistical_figures.py
python3 ../skills/scientific-figure-team/scripts/audit_rendered_figure.py outputs/boxplot_co2_uptake.svg plot_statistical_figures.py
python3 ../skills/scientific-figure-team/scripts/audit_rendered_figure.py outputs/grouped_boxplot_breakthrough_time.svg plot_statistical_figures.py
python3 ../skills/scientific-figure-team/scripts/audit_rendered_figure.py outputs/violinplot_crystal_size.svg plot_statistical_figures.py
```

## Notes

- These CSV files are synthetic and are only for demonstrating the skill workflow and style system.
- The preprocessing stage writes summary tables but does not overwrite the raw input files.
- The figures follow the same hard rules as the MOF templates: no gridlines, no boxed remarks, one actual font family, larger readable text, adaptive labels, and final audit before delivery.
