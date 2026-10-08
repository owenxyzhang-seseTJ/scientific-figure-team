#!/usr/bin/env python3
"""Generate deterministic synthetic raw data for statistical figure demos."""

from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data_raw"
RAW_DIR.mkdir(exist_ok=True)

RNG = np.random.default_rng(20260705)


def clipped_normal(mean: float, sd: float, size: int, lower: float) -> np.ndarray:
    values = RNG.normal(mean, sd, size)
    return np.clip(values, lower, None)


def make_boxplot_co2() -> pd.DataFrame:
    groups = [
        ("UiO-66", 3.18, 0.18, 9),
        ("UiO-66-NH2", 3.72, 0.22, 9),
        ("Activated composite", 4.09, 0.24, 9),
    ]
    records = []
    for sample_group, mean, sd, count in groups:
        for replicate_index, value in enumerate(clipped_normal(mean, sd, count, 2.4), start=1):
            records.append(
                {
                    "sample_group": sample_group,
                    "replicate_id": f"R{replicate_index:02d}",
                    "co2_uptake_mmol_g": round(float(value), 3),
                }
            )
    return pd.DataFrame(records)


def make_grouped_breakthrough() -> pd.DataFrame:
    groups = [
        ("Sorbent A", "Dry", 42.0, 2.8, 8),
        ("Sorbent A", "Humid", 31.5, 2.5, 8),
        ("Sorbent B", "Dry", 56.0, 3.2, 8),
        ("Sorbent B", "Humid", 46.0, 2.7, 8),
        ("Sorbent C", "Dry", 68.0, 3.5, 8),
        ("Sorbent C", "Humid", 57.2, 3.1, 8),
    ]
    records = []
    for material, feed_condition, mean, sd, count in groups:
        for replicate_index, value in enumerate(clipped_normal(mean, sd, count, 20.0), start=1):
            records.append(
                {
                    "material": material,
                    "feed_condition": feed_condition,
                    "replicate_id": f"R{replicate_index:02d}",
                    "breakthrough_time_min_g": round(float(value), 2),
                }
            )
    return pd.DataFrame(records)


def make_violin_crystal_size() -> pd.DataFrame:
    groups = [
        ("0 eq modulator", np.log(155.0), 0.28, 36),
        ("20 eq modulator", np.log(112.0), 0.24, 36),
        ("40 eq modulator", np.log(79.0), 0.22, 36),
    ]
    records = []
    for condition, log_mean, log_sigma, count in groups:
        values = np.exp(RNG.normal(log_mean, log_sigma, count))
        values = np.clip(values, 28.0, 260.0)
        for particle_index, value in enumerate(values, start=1):
            records.append(
                {
                    "condition": condition,
                    "particle_id": f"P{particle_index:02d}",
                    "crystal_size_nm": round(float(value), 1),
                }
            )
    return pd.DataFrame(records)


def main() -> None:
    make_boxplot_co2().to_csv(RAW_DIR / "boxplot_co2_uptake.csv", index=False)
    make_grouped_breakthrough().to_csv(RAW_DIR / "grouped_boxplot_breakthrough_time.csv", index=False)
    make_violin_crystal_size().to_csv(RAW_DIR / "violinplot_crystal_size.csv", index=False)


if __name__ == "__main__":
    main()
