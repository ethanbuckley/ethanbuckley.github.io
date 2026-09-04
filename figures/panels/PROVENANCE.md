# Panel provenance

> [!NOTE]
> Drafted by an LLM-based AI tool (Claude Code/Opus 5).

## The state of these two files

`production-ratio-panel.png` and `intervention-effects-panel.png` were lifted as pixels out of the original figure masters. Unlike everything else in `figures/`, they have no source, so nothing on disk records which model fit produced them.

`render_panels.py` now provides the missing source for the production-ratio panel. It is not yet wired into `render.sh`, because which model is canonical is a decision, not a lookup. See below.

## The published panel does not match the current VG14 fit

Checked 2026-07-31 against `output/models/VG14-age-understood-spoken-signed-ds/production_rate.csv` in the `vocabulary-growth` repo. That file has exactly the columns and the age grid the panel plots (8.0 to 115.0 months; median plus 50, 75 and 90% HDI), so it is the same quantity from the same pipeline. The values are not the same:

| Age        | Published panel | Current VG14 fit | Difference |
| ---------- | --------------- | ---------------- | ---------- |
| 4 years    | 0.524           | 0.529            | +0.005     |
| 7 years    | 0.846           | 0.841            | −0.005     |
| 7½ years   | 0.858           | 0.877            | +0.019     |
| 8 years    | 0.878           | 0.909            | +0.031     |
| 115 months | 0.918           | 0.966            | +0.048     |

Panel figures were read off the image against its own gridlines, so they carry roughly ±0.01. The divergence at the top is well beyond that, and the shapes differ too: the VG14 curve has a shoulder around 20 to 30 months that the published curve does not.

The likely explanation is that the panel came from a joint understood-and-spoken model without signing, or from an earlier fit. VG14 includes a signed outcome, which changes how the spoken cell is defined, so its production ratio is not the same quantity. Neither VG10 nor VG12 has a local fit, so this could not be settled from what is on disk.

## Why nothing was changed

The number on this panel is quoted in `index.html` in three places: the `og:image:alt`, the chart's own `alt` text, and the body prose ("about 86% by seven and a half"). Regenerating from VG14 would move that to about 88% and require all three to change, on a public page, on the strength of a model that may be answering a slightly different question.

So the panel is untouched and the decision is open:

1. **Confirm which model is canonical** for this figure. If it is a joint DS understood-and-spoken model, it needs fitting before the panel can be regenerated.
2. **Then run `render_panels.py --out production-ratio-panel.png`** and re-check the three places in `index.html`, plus the explainer prose.

Until then the panel stays as published, and the mismatch is recorded here rather than left to be rediscovered.

## Style

`render_panels.py` also fixes what the panel looks like, which is the one place on the site still showing matplotlib defaults: a grey ground, a boxed legend, DejaVu Sans, and `q(a) = p_S(a) / p_U(a)` as a y-axis label. The replacement uses the site's tokens and type, a hairline horizontal grid only, an unframed legend, age in years across the top because that is how the finding is quoted, and prose labels. Run it with `--csv` to see a preview without touching the published file.

```bash
/opt/miniconda3/envs/dse-vocab-growth/bin/python figures/panels/render_panels.py \
  --csv ~/Documents/GitHub/dseinternational/vocabulary-growth/output/models/VG14-age-understood-spoken-signed-ds/production_rate.csv
```

Previews are written to `*.preview.png` and are gitignored.

## The forest plot

`intervention-effects-panel.png` now has a source: `render_effects_panel.py`, which reads `itt_vs_joint_tau-2026-07-21.csv`. That file is a dated copy of `output/statistical_models/comparison/itt_vs_joint_tau.csv` from the `language-reading-predictors` repository, written by its `compare_statistical_models.py` on 2026-07-21 from the reporting-tier fits. The panel plots the single-outcome intention-to-treat rows (`lrp-rli-itt-005` to `-010`) and leaves out the joint model (`-012`).

The bounds are equal-tailed central quantiles at the coverage each fit's `config.json` records, `ci_prob = 0.89`. The plate and the pages that describe it used to say 95%; they were corrected on 2026-09-04, and the script takes the coverage as an argument so the label cannot drift from the data again. Regenerate with:

```bash
python figures/panels/render_effects_panel.py --coverage 0.89 --out intervention-effects-panel.png
```

If the study is refitted, replace the dated CSV with a new dated copy, check `ci_prob` in the new fits, and re-run.
