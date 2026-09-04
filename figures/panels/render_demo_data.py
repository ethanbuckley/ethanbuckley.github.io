#!/usr/bin/env python3
"""Rebuild the interactive demo's embedded posterior from a fitted VG14 output folder.

`vocabulary-growth-demo.html` carries its data inline as `const DATA = {...}`: the
production ratio with 50, 75 and 90% bands, posterior-predictive word counts for
words understood, spoken and signed, and the spoken over-dispersion kappa, all on
a 64-point age grid from 8 to 115 months. Until now that block had no source. This
script writes it from the CSVs the fit pipeline emits, interpolating the pipeline's
500-point grid onto the demo's.

Usage:
    python figures/panels/render_demo_data.py --fit-dir <output>/models/<VG14 run> \
        --html vocabulary-growth-demo.html --label "VG14 test-tier fit, September 2026"

Built by an LLM-based AI tool (Claude Code/Fable 5.1).
"""

from __future__ import annotations

import argparse
import csv
import json
import re
from pathlib import Path

import numpy as np

N_POINTS = 64
AGE_LO_M, AGE_HI_M = 8.0, 115.0


def cols(path: Path) -> dict[str, np.ndarray]:
    with path.open(newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    return {k: np.array([float(r[k]) for r in rows]) for k in rows[0]}


def onto(grid_m: np.ndarray, age_m: np.ndarray, y: np.ndarray, nd: int) -> list[float]:
    return [round(float(v), nd) for v in np.interp(grid_m, age_m, y)]


def build(fit_dir: Path) -> dict:
    grid_m = np.linspace(AGE_LO_M, AGE_HI_M, N_POINTS)
    q = cols(fit_dir / "production_rate.csv")
    u = cols(fit_dir / "posterior_predictive_median_trend_u.csv")
    s = cols(fit_dir / "posterior_predictive_median_trend_s.csv")
    g = cols(fit_dir / "posterior_predictive_median_trend_sign.csv")
    k = cols(fit_dir / "posterior_kappa_s.csv")

    def counts(t: dict[str, np.ndarray], bands: bool = True) -> dict:
        out = {"m": onto(grid_m, t["age_months"], t["median"], 1),
               "lo90": onto(grid_m, t["age_months"], t["p05"], 1),
               "hi90": onto(grid_m, t["age_months"], t["p95"], 1)}
        if bands:
            out["lo50"] = onto(grid_m, t["age_months"], t["p25"], 1)
            out["hi50"] = onto(grid_m, t["age_months"], t["p75"], 1)
        return out

    return {
        "age": [round(float(v) / 12.0, 3) for v in grid_m],
        "ratio": {
            "m": onto(grid_m, q["age_months"], q["q_median"], 4),
            "lo90": onto(grid_m, q["age_months"], q["hdi_lo"], 4),
            "hi90": onto(grid_m, q["age_months"], q["hdi_hi"], 4),
            "lo75": onto(grid_m, q["age_months"], q["hdi75_lo"], 4),
            "hi75": onto(grid_m, q["age_months"], q["hdi75_hi"], 4),
            "lo50": onto(grid_m, q["age_months"], q["hdi50_lo"], 4),
            "hi50": onto(grid_m, q["age_months"], q["hdi50_hi"], 4),
        },
        "understood": counts(u),
        "spoken": counts(s),
        "signed": counts(g, bands=False),
        "kappa_spoken": onto(grid_m, k["age_months"], k["kappa_median"], 4),
    }


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--fit-dir", type=Path, required=True)
    ap.add_argument("--html", type=Path, required=True)
    ap.add_argument("--label", required=True, help="how the page should name the fit, e.g. 'VG14 test-tier fit, September 2026'")
    args = ap.parse_args(argv)

    data = build(args.fit_dir)
    html = args.html.read_text(encoding="utf-8")
    new_block = "const DATA = " + json.dumps(data, separators=(",", ":")) + ";\n"
    html, n = re.subn(r"const DATA = \{.*?\};\n", new_block, html, count=1, flags=re.S)
    if n != 1:
        raise SystemExit("could not find the `const DATA = {...};` block")
    html, m = re.subn(r"\(VG14 [^;]*?fit[^)]*?; findings preliminary\)",
                      f"({args.label}; findings preliminary)", html, count=1)
    args.html.write_text(html, encoding="utf-8")
    print(f"rewrote DATA in {args.html} from {args.fit_dir.name}; caption updated: {bool(m)}")
    i48 = int(np.argmin(np.abs(np.array(data['age']) - 4.0)))
    print(f"  check: ratio at ~4y = {data['ratio']['m'][i48]}, understood median = {data['understood']['m'][i48]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
