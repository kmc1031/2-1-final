"""Plot raw cross-condition metric deltas from summary_bd_rates.csv.

All plotted values are Proposed - Baseline. For lower-is-better metrics
stored as signed improvements in summary_bd_rates.csv, the sign is flipped
back to the raw delta convention here.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "results" / "full_experiment" / "summary_bd_rates.csv"
OUTPUT = ROOT / "results" / "full_experiment" / "cross_condition_metric_deltas.png"


def _float(value: str) -> float:
    try:
        out = float(value)
    except (TypeError, ValueError):
        return float("nan")
    return out if math.isfinite(out) else float("nan")


def main() -> None:
    rows = []
    with INPUT.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row.get("Method") == "prop":
                rows.append(row)

    videos = ["akiyo", "foreman", "mobile", "stefan"]
    sigmas = [0, 5, 10, 15]
    metrics = [
        ("post_delta_psnrb", "Delta PSNR-B (dB)", "Proposed - Baseline; positive is better", 1.0),
        ("post_delta_msssim", "Delta MS-SSIM", "Proposed - Baseline; positive is better", 1.0),
        ("post_delta_gbim", "Delta GBIM", "Proposed - Baseline; negative is better", -1.0),
        ("post_delta_strred", "Delta STRRED-like", "Proposed - Baseline; negative is better", -1.0),
    ]

    lookup = {
        (row["Video"], int(row["Sigma"])): row
        for row in rows
        if row.get("Sigma", "").isdigit()
    }

    fig, axes = plt.subplots(2, 2, figsize=(13, 8))
    x = np.arange(len(sigmas))
    width = 0.18

    for ax, (key, title, ylabel, sign) in zip(axes.flat, metrics):
        metric_values = {}
        for idx, video in enumerate(videos):
            values = [
                sign * _float(lookup.get((video, sigma), {}).get(key, ""))
                for sigma in sigmas
            ]
            metric_values[video] = values
        series = [
            value
            for values in metric_values.values()
            for value in values
            if math.isfinite(value)
        ]
        span = max(series) - min(series) if series else 1.0
        label_offset = max(span * 0.025, 0.0005)

        for idx, video in enumerate(videos):
            values = metric_values[video]
            offset = (idx - 1.5) * width
            bars = ax.bar(x + offset, values, width, label=video.capitalize())
            for bar, value in zip(bars, values):
                if math.isfinite(value):
                    ax.text(
                        bar.get_x() + bar.get_width() / 2,
                        value + (label_offset if value >= 0 else -label_offset),
                        f"{value:.2f}" if abs(value) >= 0.01 else f"{value:.3f}",
                        ha="center",
                        va="bottom" if value >= 0 else "top",
                        fontsize=7,
                    )
        ax.axhline(0, color="black", linewidth=0.8, alpha=0.7)
        ax.set_title(title, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=10)
        ax.set_xticks(x)
        ax.set_xticklabels(["Clean", "s5", "s10", "s15"])
        ax.grid(axis="y", linestyle="--", alpha=0.35)

    axes[0, 0].legend(fontsize=9, ncol=2)
    fig.suptitle("Raw Metric Deltas — Proposed - Baseline", fontsize=14)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(OUTPUT, dpi=300)
    print(OUTPUT)


if __name__ == "__main__":
    main()
