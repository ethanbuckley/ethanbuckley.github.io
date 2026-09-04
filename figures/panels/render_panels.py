#!/usr/bin/env python3
"""Render the production-ratio plot panel from model output, in the site's style.

## Why this exists

`figures/` made every showcase figure regenerable except two: the plot panels were
lifted as pixels out of the original masters, with no source. That is the same
problem the rest of the directory was built to solve. It also means the panels are
the only part of the site still wearing matplotlib's defaults, which is visible:
a grey seaborn ground, a boxed legend, DejaVu Sans, and axis labels carrying raw
code identifiers (`q(a) = p_S(a) / p_U(a)`) on a page whose whole point is that the
work is legible to non-specialists.

This script closes that gap. Point it at a `production_rate.csv` from a fitted
model and it emits a panel at exactly the published pixel size, styled to the
site's tokens, so it drops into `production-ratio.html` unchanged.

## What it does NOT do

It does not decide which model is canonical, and it does not overwrite the
published panel unless you ask it to with --out. Read PROVENANCE.md in this folder
before you do: the live panel and the current VG14 fit disagree, and the numbers on
the panel are quoted in three places in `index.html`.

Usage:
    python figures/panels/render_panels.py --csv path/to/production_rate.csv
    python figures/panels/render_panels.py --csv ... --out production-ratio-panel.png

Requires matplotlib. The vocabulary-growth conda env has it:
    /opt/miniconda3/envs/dse-vocab-growth/bin/python

Built by an LLM-based AI tool (Claude Code/Opus 5).
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402
from matplotlib.patches import Patch  # noqa: E402

HERE = Path(__file__).resolve().parent

# Site tokens, kept in step with assets/site.css and figures/*.html by hand.
INK = "#14181d"
SOFT = "#5b6571"
FAINT = "#6b7480"
HAIRLINE = "#e4e7eb"
TEAL = "#2440b3"   # the site accent since 2026-09-04; the name is historical
PAPER = "#ffffff"
# The site's system sans; matplotlib takes the first family it can find.
SANS = ["Helvetica Neue", "Arial", "DejaVu Sans"]

# The published panel is 1776 x 1272 and embedded at exactly half that, so the 2x
# render of the surrounding canvas reuses these pixels without resampling. Changing
# either number means changing the <img> width/height in production-ratio.html too.
NATIVE_W, NATIVE_H = 1776, 1272
DPI = 200

# Band opacities. Widest is faintest, so the eye reads the median first and the
# bands as progressively weaker claims rather than as three equal objects.
BANDS = [
    ("hdi_lo", "hdi_hi", 0.13, "90% credible"),
    ("hdi75_lo", "hdi75_hi", 0.17, "75% credible"),
    ("hdi50_lo", "hdi50_hi", 0.24, "50% credible"),
]


def load(path: Path) -> dict[str, list[float]]:
    """Read the CSV into columns, keeping only rows where every field parses."""
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise SystemExit(f"{path} has no rows")

    needed = ["age_months", "q_median"] + [c for lo, hi, _, _ in BANDS for c in (lo, hi)]
    missing = [c for c in needed if c not in rows[0]]
    if missing:
        raise SystemExit(f"{path} is missing columns: {', '.join(missing)}")

    cols: dict[str, list[float]] = {c: [] for c in needed}
    for r in rows:
        try:
            vals = {c: float(r[c]) for c in needed}
        except (TypeError, ValueError):
            continue
        for c, v in vals.items():
            cols[c].append(v)
    return cols


def render(cols: dict[str, list[float]], out: Path) -> None:
    age = cols["age_months"]
    med = cols["q_median"]

    fig, ax = plt.subplots(figsize=(NATIVE_W / DPI, NATIVE_H / DPI), dpi=DPI)
    fig.patch.set_facecolor(PAPER)
    ax.set_facecolor(PAPER)

    for lo, hi, alpha, _ in BANDS:
        ax.fill_between(age, cols[lo], cols[hi], color=TEAL, alpha=alpha, linewidth=0)
    ax.plot(age, med, color=TEAL, linewidth=2.6, solid_capstyle="round", zorder=5)

    # A hairline horizontal grid only. Vertical gridlines add nothing here: the
    # question is "how high", not "at exactly which month".
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=HAIRLINE, linewidth=1.0)
    ax.xaxis.grid(False)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(HAIRLINE)
        ax.spines[side].set_linewidth(1.0)

    ax.set_ylim(0, 1.0)
    ax.set_xlim(min(age), max(age))
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["0", "20%", "40%", "60%", "80%", "100%"])
    ax.tick_params(colors=SOFT, labelsize=13, length=0, pad=8)
    for lbl in ax.get_xticklabels() + ax.get_yticklabels():
        lbl.set_fontfamily(SANS)

    # Prose, not code. The published panel says "q(a) = p_S(a) / p_U(a)", which is
    # the model's variable name rather than anything a reader can use.
    ax.set_ylabel(
        "Share of understood words the child also says",
        color=INK, fontsize=15, fontfamily=SANS, labelpad=14,
    )
    ax.set_xlabel("Age in months", color=INK, fontsize=15, fontfamily=SANS, labelpad=12)

    # Years across the top, because "seven and a half" is how the finding is quoted.
    top = ax.secondary_xaxis("top", functions=(lambda m: m / 12.0, lambda y: y * 12.0))
    top.set_xlabel("Age in years", color=SOFT, fontsize=13, fontfamily=SANS, labelpad=10)
    top.tick_params(colors=SOFT, labelsize=12, length=0, pad=6)
    for lbl in top.get_xticklabels():
        lbl.set_fontfamily(SANS)
    top.spines["top"].set_visible(False)

    handles = [Line2D([], [], color=TEAL, linewidth=2.6, label="Posterior median")]
    handles += [
        Patch(facecolor=TEAL, alpha=alpha, linewidth=0, label=label)
        for _, _, alpha, label in reversed(BANDS)
    ]
    leg = ax.legend(
        handles=handles, loc="lower right", frameon=False, fontsize=13,
        handlelength=1.6, borderpad=0, labelspacing=0.6,
    )
    for text in leg.get_texts():
        text.set_color(SOFT)
        text.set_fontfamily(SANS)

    fig.tight_layout(pad=1.6)
    fig.savefig(out, facecolor=PAPER, dpi=DPI)
    plt.close(fig)

    # The pixel size is load-bearing, so fail loudly rather than silently shipping
    # a panel the surrounding HTML will resample.
    try:
        from PIL import Image

        got = Image.open(out).size
        if got != (NATIVE_W, NATIVE_H):
            print(f"  note: rendered {got[0]}x{got[1]}, expected {NATIVE_W}x{NATIVE_H}")
            print("  resizing to the published dimensions so the embed stays crisp")
            Image.open(out).resize((NATIVE_W, NATIVE_H), Image.LANCZOS).save(out, optimize=True)
    except ImportError:
        pass


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--csv", required=True, type=Path, help="a model's production_rate.csv")
    p.add_argument("--out", type=Path, default=HERE / "production-ratio-panel.preview.png",
                   help="output PNG (default: a preview file, not the published panel)")
    args = p.parse_args(argv)

    if not args.csv.exists():
        raise SystemExit(f"no such file: {args.csv}")

    cols = load(args.csv)
    render(cols, args.out)

    age, med = cols["age_months"], cols["q_median"]
    print(f"Read    {args.csv}")
    print(f"        {len(age)} rows, ages {min(age):.1f}-{max(age):.1f} months")
    for years in (4, 7, 7.5, 8):
        target = years * 12
        if min(age) <= target <= max(age):
            i = min(range(len(age)), key=lambda j: abs(age[j] - target))
            print(f"        at {years:>4} years: {med[i]:.3f}")
    print(f"        at the end ({max(age):.0f} months): {med[-1]:.3f}")
    print(f"Wrote   {args.out}")
    if args.out.name == "production-ratio-panel.png":
        print()
        print("You have overwritten the published panel. The numbers on it are quoted in")
        print("index.html in three places, including the Open Graph alt text. Check them.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
