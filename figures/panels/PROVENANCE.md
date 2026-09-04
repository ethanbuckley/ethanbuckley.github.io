# Panel provenance

> [!NOTE]
> Drafted by an LLM-based AI tool (Claude Code/Opus 5).

## The state of these two files

`production-ratio-panel.png` and `intervention-effects-panel.png` were lifted as pixels out of the original figure masters. Unlike everything else in `figures/`, they have no source, so nothing on disk records which model fit produced them.

`render_panels.py` and `render_effects_panel.py` provide the sources. Neither is wired into `render.sh`, on purpose: a re-render of the plates should not silently swap the model behind a number that is quoted in prose.

## The production-ratio panel: now drawn from a dated fit

Until 2026-09-04 the published panel was pixels from the July 2026 figure master, from a fit nothing on disk recorded, and it disagreed with the only VG14 output then on disk (a June development-tier run) by up to 0.05 at the top of the age range. On 2026-09-04 VG14 was refitted at test tier from the current pipeline and data, and the panel is now rendered from that fit:

```bash
python figures/panels/render_panels.py --csv figures/panels/vg14-test-2026-09-04/production_rate.csv --out production-ratio-panel.png
```

`vg14-test-2026-09-04/` holds the small CSVs the panel and the demo page read, plus the fit's `fit_manifest.json`, `diagnostics_summary.json` and `descriptive_statistics.csv`, so the numbers on the site can be traced without the trace file. Three things about that fit belong on the record:

| | |
| --- | --- |
| Data | 14 datasets, 1,424 assessments (976 with a comprehension count, 1,421 spoken, 685 signed), ages 8 to 115 months; the September 2026 masking rules |
| Sampling | `test` tier, 4 chains, nutpie; R-hat max 1.005, minimum ESS 1,609, BFMI 0.83 to 0.91 |
| Gate | **not met**: 3 divergent transitions in 8,000 draws. Everything else passed. The site says so on the plate footer |

The pipeline now reports comprehension-derived quantities, the production ratio among them, only to 72 months (`report_max_age_understood`), because comprehension data above six years are thin. So the old headline, about 86% by seven and a half years, cannot be reproduced by design, and the site now quotes about 44% at four years and 64% at six, the oldest age the model reports. That is a material change to a public claim, which is why it went out as a pull request rather than straight to `main`.

The demo page (`vocabulary-growth-demo.html`) embeds the same fit through `render_demo_data.py`, on a 64-point grid from 8 to 72 months, with 50% and 89% bands. Its previous data block came from the June development-tier run.

The comparisons with typically-developing children quoted beside these figures (the 13-point gap at 50 to 150 understood words, the spoken-vocabulary lag at age two) still come from the July 2026 fits, and the study meta line on the front page says so. Regenerating them needs the typically-developing models refitted alongside.

## Layout, 2026-09-04

The plates were redrawn chart-first at Ethan's request (the slide-deck apparatus read as machine-made). Panels are now 2944 x 1380 px, embedded at half size; the production-ratio panel carries its quoted numbers as annotations at one, four and six years; a new `--kind counts` panel (`vocabulary-counts-panel.png`, words understood and spoken by age) replaced the boxed-equation method plate; the causal plate kept its diagram and lost its callout box. The source line on each plate names the fit and its date.

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
