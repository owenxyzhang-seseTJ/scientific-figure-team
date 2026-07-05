# MOF Figure Project

Workflow:

1. Put raw machine-readable data in `data_raw/`.
2. Search relevant literature, instrument/software docs, or user-provided methods.
3. Fill `method_search_packet.md` and keep `Status: READY_FOR_PREPROCESSING`.
4. Fill `figure_plan.md` in English and wait for user confirmation.
5. Preprocess raw data into `data_processed/`.
6. Change `figure_plan.md` to `Status: CONFIRMED` after approval.
7. Plot into `outputs/`.
8. Run final rendered-image audit; if it fails, redraw and re-audit before delivery.

Example commands:

```bash
python3 path/to/mof_figure_templates.py preprocess pxrd data_raw/pxrd_raw.csv data_processed/pxrd_processed.csv --method-packet method_search_packet.md
python3 path/to/mof_figure_templates.py plot pxrd data_processed/pxrd_processed.csv outputs --plan figure_plan.md
```
