Status: CONFIRMED
Figure objective: Provide several realistic statistical figure templates that can be reused for chemistry, materials, and adsorption manuscripts while preserving raw-data visibility.
Raw data files:
- data_raw/boxplot_co2_uptake.csv
- data_raw/grouped_boxplot_breakthrough_time.csv
- data_raw/violinplot_crystal_size.csv
Preprocessing steps:
- Validate workflow gates from `method_search_packet.md` and this plan before any preprocessing.
- Read tidy raw CSV files and enforce the planned group order.
- Write group-level summary tables to `data_processed/` without editing the raw CSV files.
Visual mapping:
- Figure text in English.
- Python comments in Chinese on all visual-affecting lines.
- Arial-first single-font selection with DejaVu Sans fallback.
- Pastel project palette shared across all demo figures.
- Native subscripts for labels such as `CO$_2$`.
- No gridlines, no boxed remarks, and adaptive label placement.
Figures to generate:
- `boxplot_co2_uptake`: compare three MOF batches at 298 K using boxplots, raw points, and mean `±` SD.
- `grouped_boxplot_breakthrough_time`: compare dry and humid dynamic breakthrough times across three sorbents using grouped boxplots and mean `±` SD.
- `violinplot_crystal_size`: compare crystal-size distributions for three modulator conditions using violins, quartiles, medians, and raw points.
Export formats:
- SVG
- PDF
- TIFF
- PNG
Limitations:
- The datasets are synthetic demos for workflow validation rather than experimental conclusions.
