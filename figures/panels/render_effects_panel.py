#!/usr/bin/env python3
"""Render the reading-intervention forest panel from the study's own comparison table.

`intervention-effects-panel.png` was lifted as pixels out of the July 2026 figure
master and had no source. This script supplies one. It reads the per-outcome
treatment effects that `compare_statistical_models.py` writes in the
language-reading-predictors repository (`itt_vs_joint_tau.csv`; a dated copy sits
beside this file), keeps the single-outcome intention-to-treat fits, and draws them
in the site's style at the panel's published pixel size, so the render drops into
`intervention-effects.html` unchanged.

The effects are on the logit scale: the coefficient on the intervention arm in a
Beta-Binomial model of each skill score. Right of zero favours the teaching. The
bounds are equal-tailed central quantiles at the coverage the study reports, which
is passed in with --coverage so the label cannot drift from the data.

Usage:
    python figures/panels/render_effects_panel.py            # preview file
    python figures/panels/render_effects_panel.py --out intervention-effects-panel.png

Built by an LLM-based AI tool (Claude Code/Fable 5.1).
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.lines import Line2D  # noqa: E402

HERE = Path(__file__).resolve().parent

INK = "#14181d"
SOFT = "#5b6571"
HAIRLINE = "#e4e7eb"
ACCENT = "#2440b3"
GREY = "#8d97a3"
PAPER = "#ffffff"
SANS = ["Helvetica Neue", "Helvetica", "Arial", "DejaVu Sans"]

# The published panel is 1780 x 830 px, embedded at half size in the 1600 x 1000
# plate, so the 2x render of the plate reuses these pixels without resampling.
NATIVE_W, NATIVE_H = 2944, 1560   # fills the 1600x1000 plate at 2x
DPI = 200

JOINT = "lrp-rli-itt-012"

# Rows from top to bottom, with the group each sits in.
ROWS = [
    ("L", "Letter-sound knowledge", "Decoding and phonics, taught directly"),
    ("B", "Blending", "Decoding and phonics, taught directly"),
    ("W", "Word reading", "Decoding and phonics, taught directly"),
    ("R", "Receptive vocabulary", "Broad, untaught vocabulary"),
    ("E", "Expressive vocabulary", "Broad, untaught vocabulary"),
]


def load(path: Path, config: str) -> dict[str, tuple[float, float, float]]:
    """Single-outcome fits only: one effect per outcome code."""
    out: dict[str, tuple[float, float, float]] = {}
    with path.open(newline="", encoding="utf-8") as fh:
        for r in csv.DictReader(fh):
            if r["config"] != config or r["source"] == JOINT:
                continue
            if r.get("converged", "True") != "True":
                raise SystemExit(f"{r['source']} did not converge; refusing to plot it")
            out[r["outcome"]] = (float(r["tau_median"]), float(r["tau_lo"]), float(r["tau_hi"]))
    missing = [code for code, _, _ in ROWS if code not in out]
    if missing:
        raise SystemExit(f"{path} has no single-outcome row for: {', '.join(missing)}")
    return out


def render(effects: dict[str, tuple[float, float, float]], coverage: float, out: Path) -> None:
    plt.rcParams["font.family"] = "sans-serif"
    plt.rcParams["font.sans-serif"] = SANS

    fig = plt.figure(figsize=(NATIVE_W / DPI, NATIVE_H / DPI), dpi=DPI, facecolor=PAPER)
    ax = fig.add_axes([0.24, 0.16, 0.73, 0.80])
    ax.set_facecolor(PAPER)

    # Group headings take a slot of their own, so rows are laid out top to bottom
    # with a gap before each new group.
    y = 0.0
    slots: list[tuple[float, str, str | None]] = []
    last_group = None
    for code, label, group in ROWS:
        if group != last_group:
            if last_group is not None:
                y -= 0.55
            slots.append((y, "", group))
            y -= 0.85
            last_group = group
        slots.append((y, code, None))
        y -= 1.0

    for yy, code, group in slots:
        if group is not None:
            ax.text(-0.02, yy, group, transform=ax.get_yaxis_transform(), ha="right", va="center",
                    fontsize=11, color=SOFT)
            continue
        med, lo, hi = effects[code]
        clear = lo > 0 or hi < 0
        colour = ACCENT if clear else GREY
        ax.plot([lo, hi], [yy, yy], color=colour, linewidth=3.0, solid_capstyle="round", zorder=3)
        ax.plot([med], [yy], marker="o", markersize=8, color=colour, markeredgecolor=PAPER,
                markeredgewidth=1.4, zorder=4)
        name = next(lbl for c, lbl, _ in ROWS if c == code)
        ax.text(-0.02, yy, name, transform=ax.get_yaxis_transform(), ha="right", va="center",
                fontsize=13, color=INK)

    ax.axvline(0, color=INK, linewidth=0.8, linestyle=(0, (3, 3)), zorder=2)
    ax.set_ylim(y + 0.4, 0.6)
    lo_all = min(v[1] for v in effects.values())
    hi_all = max(v[2] for v in effects.values())
    pad = 0.06 * (hi_all - lo_all)
    ax.set_xlim(min(lo_all, -0.2) - pad, hi_all + pad)

    ax.set_yticks([])
    for side in ("left", "right", "top"):
        ax.spines[side].set_visible(False)
    ax.spines["bottom"].set_color(HAIRLINE)
    ax.tick_params(axis="x", colors=SOFT, labelsize=12, length=0, pad=8)
    ax.grid(axis="x", color=HAIRLINE, linewidth=0.7, zorder=1)
    ax.set_xlabel("Intervention effect, log-odds. Right of the dashed line favours the teaching.",
                  color=SOFT, fontsize=13, labelpad=10)

    pct = f"{coverage * 100:.0f}"
    handles = [
        Line2D([0], [0], color=ACCENT, marker="o", markersize=4.5, linewidth=2.0,
               markeredgecolor=PAPER, label=f"{pct}% interval clear of zero"),
        Line2D([0], [0], color=GREY, marker="o", markersize=4.5, linewidth=2.0,
               markeredgecolor=PAPER, label=f"{pct}% interval spans zero"),
    ]
    leg = ax.legend(handles=handles, loc="lower right", frameon=False, fontsize=12,
                    handlelength=2.2, borderaxespad=0.2)
    for t in leg.get_texts():
        t.set_color(SOFT)

    fig.savefig(out, dpi=DPI, facecolor=PAPER)
    plt.close(fig)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--csv", type=Path, default=HERE / "itt_vs_joint_tau-2026-07-21.csv")
    ap.add_argument("--config", default="reporting", help="which sampling tier's rows to read")
    ap.add_argument("--coverage", type=float, required=True,
                    help="the ci_prob the study used for tau_lo and tau_hi, e.g. 0.89")
    ap.add_argument("--out", type=Path, default=HERE / "intervention-effects-panel.preview.png")
    args = ap.parse_args(argv)
    effects = load(args.csv, args.config)
    render(effects, args.coverage, args.out)
    from PIL import Image  # noqa: PLC0415
    w, h = Image.open(args.out).size
    if (w, h) != (NATIVE_W, NATIVE_H):
        print(f"warning: rendered {w}x{h}, expected {NATIVE_W}x{NATIVE_H}")
    print(f"wrote {args.out} ({w}x{h})")
    for code, label, _ in ROWS:
        med, lo, hi = effects[code]
        print(f"  {label:<24} {med:+.3f}  [{lo:+.3f}, {hi:+.3f}]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
