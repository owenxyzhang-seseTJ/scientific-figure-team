Status: READY_FOR_PREPROCESSING
Search date: 2026-07-05
Figure type: Quantitative statistical figures for materials and adsorption research
Material/system: Synthetic demo datasets representing common chemistry and MOF workflows
Sources searched:
- Matplotlib boxplot API: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.boxplot.html
- Matplotlib violinplot API: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.violinplot.html
- Matplotlib errorbar API: https://matplotlib.org/stable/api/_as_gen/matplotlib.pyplot.errorbar.html
- Weissgerber TL et al. Beyond Bar and Line Graphs: Time for a New Data Presentation Paradigm. PLoS Biology 2015. https://journals.plos.org/plosbiology/article?id=10.1371%2Fjournal.pbio.1002128
Chosen preprocessing method:
- Keep replicate-level raw values unchanged except for tidy-format harmonization and explicit group ordering.
- Summarize each group with n, mean, standard deviation, median, Q1, Q3, minimum, and maximum in `data_processed/`.
- Use boxplots or violin plots to display distributions, overlay raw points for sample visibility, and overlay mean `±` SD error bars where requested.
Rationale:
- Boxplots and violin plots preserve distributional information that simple bars would hide.
- Overlaying replicate points is appropriate for common chemistry/materials sample sizes and makes scatter, spread, and outliers visible.
- Mean `±` SD overlays support readers who still expect central-tendency and spread markers in quantitative materials figures.
Rejected alternatives:
- Bar charts with only mean `±` error bars were rejected because they suppress distribution shape and outlier visibility.
- Automated normality testing and parametric significance annotation were rejected because no hypothesis-testing goal was defined for the demo.
- KDE smoothing outside the violin estimator was rejected to avoid introducing extra assumptions into small-n boxplot examples.
Assumptions and limits:
- The raw CSV files are synthetic demo data rather than measured experiments.
- Error bars represent sample standard deviation rather than SEM unless a future plan explicitly changes that choice.
- No p-values or significance stars are added because the demo focuses on distribution-aware presentation rather than statistical inference claims.
Fields required from raw data:
- `boxplot_co2_uptake.csv`: `sample_group`, `replicate_id`, `co2_uptake_mmol_g`
- `grouped_boxplot_breakthrough_time.csv`: `material`, `feed_condition`, `replicate_id`, `breakthrough_time_min_g`
- `violinplot_crystal_size.csv`: `condition`, `particle_id`, `crystal_size_nm`
Fields produced after preprocessing:
- Per-group summary CSV files containing `n`, `mean`, `sd`, `median`, `q1`, `q3`, `min`, and `max`
