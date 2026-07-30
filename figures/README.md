# Figure sources

> [!NOTE]
> Drafted by an LLM-based AI tool (Claude Code/Fable 5).

## Why this exists

The four "showcase" research figures on the site (`assets/vocab-production-ratio.*`, `assets/vocab-method.*`, `assets/reading-intervention-effects.*`, `assets/reading-causal-design.*`) were originally assembled as one-off PNGs with no source on disk, so every copy fix meant repainting pixels and the images drifted stale (588 vs 576 children, 800 vs 810 words, "locked 19-node DAG" vs the revised 20-node DAG). This directory is the regenerable source of truth: each figure is a self-contained HTML file that headless Chrome screenshots at 2x.

## Layout

| Source                      | Published asset (do not rename)        |
| --------------------------- | -------------------------------------- |
| `production-ratio.html`     | `assets/vocab-production-ratio.*`      |
| `vocab-method.html`         | `assets/vocab-method.*`                |
| `intervention-effects.html` | `assets/reading-intervention-effects.*`|
| `causal-design.html`        | `assets/reading-causal-design.*`       |

Each HTML file is a fixed 1600 x 1000 CSS px canvas. Rendering at a device scale factor of 2 produces the 3200 x 2000 PNG master that `index.html` links to; the script then emits the two 1600px-wide derivatives the page actually loads (`<name>-1600.webp` and a palettised `<name>-1600.png` fallback).

`panels/` holds the two real plot panels (`production-ratio-panel.png`, `intervention-effects-panel.png`), extracted from the original masters. They are model output, embedded as `<img>`; do not try to redraw them in CSS. If the models are re-fitted, replace these PNGs and re-render.

## Regenerating

```bash
./figures/render.sh
```

Requirements: Google Chrome (the script uses its headless screenshot mode; override the binary with `RENDER_CHROME`) and a Python with Pillow for the derivatives. The default Python path baked into the script is the temporary venv used for the first build; once that is gone, set `RENDER_PYTHON=/path/to/python` (any Python 3 with `pip install Pillow` works) or have a Pillow-equipped `python3` on `PATH`.

## Editing rules

- Keep the canvas exactly 1600 x 1000 (`body{margin:0}`, `overflow:hidden` on the root div) or the screenshot will crop or letterbox.
- Design tokens (colours, type stacks) are declared at the top of each file and match the site's `index.html`; change them in step with the site.
- No em dashes anywhere; en dashes only inside numeric ranges; British spelling.
- The forest-plot panel carries its own labels and axis title; do not add duplicate labels around it.
