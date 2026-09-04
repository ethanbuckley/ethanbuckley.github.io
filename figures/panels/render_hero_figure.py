#!/usr/bin/env python3
"""Write the front page's hero figure as inline SVG from a fitted VG14 output folder.

The figure shows posterior-predictive medians of words understood and words spoken
by age for children with Down syndrome, each with its 50% band, from the same fit
folder the panel and demo use. It is written straight into index.html between two
marker comments, as SVG that reads the page's CSS variables, so it follows light
and dark mode without a second render.

Usage:
    python figures/panels/render_hero_figure.py --fit-dir figures/panels/vg14-test-2026-09-04 --html index.html

Built by an LLM-based AI tool (Claude Code/Fable 5.1).
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path

W, H = 560, 360
L, R, T, B = 44, 16, 26, 44          # plot margins
AGE_LO, AGE_HI = 8.0, 72.0           # months
Y_MAX = 800.0

START = "<!-- hero-figure:start -->"
END = "<!-- hero-figure:end -->"


def cols(path: Path) -> dict[str, list[float]]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return {k: [float(r[k]) for r in rows] for k in rows[0]}


def x(m: float) -> float:
    return L + (m - AGE_LO) / (AGE_HI - AGE_LO) * (W - L - R)


def y(v: float) -> float:
    return T + (1 - min(v, Y_MAX) / Y_MAX) * (H - T - B)


def path(ages, vals) -> str:
    pts = [(x(a), y(v)) for a, v in zip(ages, vals) if AGE_LO <= a <= AGE_HI]
    return "M" + " L".join(f"{px:.1f} {py:.1f}" for px, py in pts)


def band(ages, lo, hi) -> str:
    keep = [(a, l, h) for a, l, h in zip(ages, lo, hi) if AGE_LO <= a <= AGE_HI]
    top = " L".join(f"{x(a):.1f} {y(h):.1f}" for a, _, h in keep)
    bottom = " L".join(f"{x(a):.1f} {y(l):.1f}" for a, l, _ in reversed(keep))
    return f"M{top} L{bottom} Z"


def build(fit_dir: Path) -> str:
    u = cols(fit_dir / "posterior_predictive_median_trend_u.csv")
    s = cols(fit_dir / "posterior_predictive_median_trend_s.csv")
    lbl = 'font-family:var(--sans);font-size:13px;fill:var(--ink-soft)'
    parts = [
        f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" '
        'aria-label="Two rising curves of vocabulary size against age for children with Down syndrome: '
        'words understood climbs from near zero at eight months to a median of about 500 by six years, '
        'and words spoken follows below it, reaching about 300. Each curve carries a 50% credible band.">',
    ]
    # horizontal grid and y labels
    for v in (0, 200, 400, 600, 800):
        parts.append(f'<line x1="{L}" y1="{y(v):.1f}" x2="{W-R}" y2="{y(v):.1f}" style="stroke:var(--fig-grid)" stroke-width="1"/>')
        parts.append(f'<text x="{L-8}" y="{y(v)+4:.1f}" text-anchor="end" style="{lbl}">{v}</text>')
    # x ticks in years
    for yr in range(1, 7):
        m = yr * 12
        parts.append(f'<text x="{x(m):.1f}" y="{H-B+18}" text-anchor="middle" style="{lbl}">{yr}</text>')
    parts.append(f'<text x="{(L+W-R)/2:.1f}" y="{H-6}" text-anchor="middle" style="{lbl}">Age in years</text>')
    parts.append(f'<text x="{L}" y="{T-10}" style="{lbl}">Words, out of 810</text>')
    # bands then medians
    parts.append(f'<path d="{band(u["age_months"], u["ci50_lo"], u["ci50_hi"])}" style="fill:var(--accent)" opacity="0.14"/>')
    parts.append(f'<path d="{band(s["age_months"], s["ci50_lo"], s["ci50_hi"])}" style="fill:var(--ink-soft)" opacity="0.16"/>')
    parts.append(f'<path d="{path(u["age_months"], u["median"])}" fill="none" style="stroke:var(--accent)" stroke-width="2.2" stroke-linecap="round"/>')
    parts.append(f'<path d="{path(s["age_months"], s["median"])}" fill="none" style="stroke:var(--ink-soft)" stroke-width="2.2" stroke-linecap="round"/>')
    # end labels
    def last(series):
        pairs = [(a, v) for a, v in zip(series["age_months"], series["median"]) if a <= AGE_HI]
        return pairs[-1][1]
    parts.append(f'<text x="{W-R-4}" y="{y(last(u))-8:.1f}" text-anchor="end" style="font-family:var(--sans);font-size:14px;font-weight:600;fill:var(--accent)">Understood</text>')
    parts.append(f'<text x="{W-R-4}" y="{y(last(s))+16:.1f}" text-anchor="end" style="font-family:var(--sans);font-size:14px;font-weight:600;fill:var(--ink-soft)">Spoken</text>')
    parts.append("</svg>")
    return "\n".join(parts)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--fit-dir", type=Path, required=True)
    ap.add_argument("--html", type=Path, required=True)
    args = ap.parse_args(argv)
    svg = build(args.fit_dir)
    html = args.html.read_text(encoding="utf-8")
    if START not in html or END not in html:
        raise SystemExit("index.html needs the hero-figure marker comments")
    html = re.sub(re.escape(START) + r".*?" + re.escape(END), START + "\n" + svg + "\n" + END, html, count=1, flags=re.S)
    args.html.write_text(html, encoding="utf-8")
    print(f"hero figure written into {args.html} ({len(svg)} bytes of SVG)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
