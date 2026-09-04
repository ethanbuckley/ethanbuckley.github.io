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
model (the dated copy under `vg14-test-2026-09-04/` is the one published) and it emits a panel at exactly the published pixel size, styled to the
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
SANS = ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"]

# The published panel is 1776 x 1272 and embedded at exactly half that, so the 2x
# render of the surrounding canvas reuses these pixels without resampling. Changing
# either number means changing the <img> width/height in production-ratio.html too.
NATIVE_W, NATIVE_H = 2944, 1380   # fills the 1600x1000 plate at 2x, under a two-line title and a source line
DPI = 200

# Band opacities. Widest is faintest, so the eye reads the median first and the
# bands as progressively weaker claims rather than as three equal objects.
# Since the pipeline's 2026-08 output schema the CSV carries two equal-tailed
# intervals: the inner 50% and the 89% that dse_research_utils reports by default.
BANDS = [
    ("ci_lo", "ci_hi", 0.14, "89% credible"),
    ("ci50_lo", "ci50_hi", 0.28, "50% credible"),
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


def _style_axes(ax):
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=HAIRLINE, linewidth=1.0)
    ax.xaxis.grid(False)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(HAIRLINE)
        ax.spines[side].set_linewidth(1.0)
    ax.tick_params(colors=SOFT, labelsize=14, length=0, pad=9)
    for lbl in ax.get_xticklabels() + ax.get_yticklabels():
        lbl.set_fontfamily(SANS)


def _years_axis(ax, lo_m: float, hi_m: float):
    ax.set_xlim(lo_m, hi_m)
    years = [y for y in range(1, 10) if lo_m <= 12 * y <= hi_m]
    ax.set_xticks([12 * y for y in years])
    ax.set_xticklabels([str(y) for y in years])
    ax.set_xlabel("Age (years)", color=INK, fontsize=15, fontfamily=SANS, labelpad=12)


def _legend(ax, handles):
    leg = ax.legend(handles=handles, loc="upper left", frameon=False, fontsize=14,
                    handlelength=1.6, borderpad=0.4, labelspacing=0.6)
    for text in leg.get_texts():
        text.set_color(SOFT)
        text.set_fontfamily(SANS)


def _check_size(out: Path) -> None:
    """The pixel size is load-bearing: the plate embeds the panel at exactly half size."""
    try:
        from PIL import Image
        got = Image.open(out).size
        if got != (NATIVE_W, NATIVE_H):
            print(f"  note: rendered {got[0]}x{got[1]}, expected {NATIVE_W}x{NATIVE_H}; resizing")
            Image.open(out).resize((NATIVE_W, NATIVE_H), Image.LANCZOS).save(out, optimize=True)
    except ImportError:
        pass


def load_generic(path: Path) -> dict[str, list[float]]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return {k: [float(r[k]) for r in rows] for k in rows[0]}


def render(cols: dict[str, list[float]], out: Path) -> None:
    """The production ratio by age, annotated at one, four and six years."""
    import bisect
    age, med = cols["age_months"], cols["q_median"]
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = SANS
    fig, ax = plt.subplots(figsize=(NATIVE_W / DPI, NATIVE_H / DPI), dpi=DPI)
    fig.patch.set_facecolor(PAPER)
    ax.set_facecolor(PAPER)
    for lo, hi, alpha, _ in BANDS:
        ax.fill_between(age, cols[lo], cols[hi], color=TEAL, alpha=alpha, linewidth=0)
    ax.plot(age, med, color=TEAL, linewidth=2.6, solid_capstyle="round", zorder=5)
    _style_axes(ax)
    _years_axis(ax, min(age), max(age))
    ax.set_ylim(0, 1.0)
    ax.set_yticks([0, 0.2, 0.4, 0.6, 0.8, 1.0])
    ax.set_yticklabels(["0", "20%", "40%", "60%", "80%", "100%"])
    ax.set_ylabel("Share of understood words the child also says", color=INK, fontsize=15, fontfamily=SANS, labelpad=14)
    for yr in (1, 4, 6):
        m = 12 * yr
        if m < min(age) or m > max(age) + 1.0:   # the grid ends a fraction short of 72 months
            continue
        i = min(bisect.bisect_left(age, m), len(age) - 1)
        q = med[i]
        ax.plot([m], [q], marker="o", markersize=7, color=TEAL, markeredgecolor=PAPER, markeredgewidth=1.5, zorder=6)
        label = f"{q * 100:.0f}% at {yr} year" + ("" if yr == 1 else "s")
        ax.annotate(label, (m, q), textcoords="offset points", xytext=(-12, 14), ha="right",
                    fontsize=14, color=INK, fontfamily=SANS, annotation_clip=False)
    _legend(ax, [Line2D([], [], color=TEAL, linewidth=2.6, label="Posterior median")]
            + [Patch(facecolor=TEAL, alpha=alpha, linewidth=0, label=label) for _, _, alpha, label in reversed(BANDS)])
    fig.tight_layout(pad=1.4)
    fig.savefig(out, facecolor=PAPER, dpi=DPI)
    plt.close(fig)
    _check_size(out)


def render_counts(fit_dir: Path, out: Path) -> None:
    """Words understood and words spoken by age: posterior-predictive medians with 50% bands."""
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = SANS
    u = load_generic(fit_dir / "posterior_predictive_median_trend_u.csv")
    s_ = load_generic(fit_dir / "posterior_predictive_median_trend_s.csv")
    hi_m = max(u["age_months"])
    fig, ax = plt.subplots(figsize=(NATIVE_W / DPI, NATIVE_H / DPI), dpi=DPI)
    fig.patch.set_facecolor(PAPER)
    ax.set_facecolor(PAPER)
    for series, colour in ((u, TEAL), (s_, FAINT)):
        keep = [i for i, a in enumerate(series["age_months"]) if a <= hi_m]
        a = [series["age_months"][i] for i in keep]
        ax.fill_between(a, [series["ci50_lo"][i] for i in keep], [series["ci50_hi"][i] for i in keep], color=colour, alpha=0.16, linewidth=0)
        ax.plot(a, [series["median"][i] for i in keep], color=colour, linewidth=2.6, solid_capstyle="round", zorder=5)
    _style_axes(ax)
    _years_axis(ax, min(u["age_months"]), hi_m)
    ax.set_ylim(0, 810)
    ax.set_yticks([0, 200, 400, 600, 810])
    ax.set_ylabel("Words, out of the 810 on the checklist", color=INK, fontsize=15, fontfamily=SANS, labelpad=14)
    _legend(ax, [Line2D([], [], color=TEAL, linewidth=2.6, label="Words understood, median"),
                 Line2D([], [], color=FAINT, linewidth=2.6, label="Words spoken, median"),
                 Patch(facecolor=SOFT, alpha=0.18, linewidth=0, label="50% credible bands")])
    fig.tight_layout(pad=1.4)
    fig.savefig(out, facecolor=PAPER, dpi=DPI)
    plt.close(fig)
    _check_size(out)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--kind", choices=("ratio", "counts"), default="ratio",
                   help="ratio: the production-ratio panel; counts: words understood and spoken by age")
    p.add_argument("--fit-dir", type=Path, default=HERE / "vg14-test-2026-09-04",
                   help="a fit's output folder (the dated copy beside this script by default)")
    p.add_argument("--csv", type=Path, default=None, help="override: a production_rate.csv (ratio only)")
    p.add_argument("--out", type=Path, default=None,
                   help="output PNG (default: a preview file, not the published panel)")
    args = p.parse_args(argv)

    if args.kind == "counts":
        out = args.out or HERE / "vocabulary-counts-panel.preview.png"
        render_counts(args.fit_dir, out)
        print(f"Wrote   {out}")
        return 0

    csv_path = args.csv or (args.fit_dir / "production_rate.csv")
    if not csv_path.exists():
        raise SystemExit(f"no such file: {csv_path}")
    out = args.out or HERE / "production-ratio-panel.preview.png"
    cols = load(csv_path)
    render(cols, out)
    age, med = cols["age_months"], cols["q_median"]
    print(f"Read    {csv_path}")
    print(f"        {len(age)} rows, ages {min(age):.1f}-{max(age):.1f} months")
    for years in (1, 4, 6):
        target = years * 12
        if min(age) <= target <= max(age) + 1.0:
            i = min(range(len(age)), key=lambda j: abs(age[j] - target))
            print(f"        at {years:>4} years: {med[i]:.3f}")
    print(f"Wrote   {out}")
    if out.name == "production-ratio-panel.png":
        print()
        print("You have overwritten the published panel. The numbers on it are quoted in")
        print("index.html and the plate. Check them.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
