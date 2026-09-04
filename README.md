# ethanbuckley.github.io

> [!NOTE]
> Drafted by an LLM-based AI tool (Claude Code/Fable 5.1).

My portfolio site. Hand-written HTML and CSS, system fonts, no build step. It works opened from disk and on GitHub Pages at https://ethanbuckley.github.io.

## What is here

| File | What it is |
| --- | --- |
| `index.html` | The front page: about, research, engineering, projects, approach, contact |
| `cv.html`, `assets/ethan-buckley-cv.pdf` | My CV as a page and as a one-page PDF printed from it |
| `vocabulary-growth-explainer.html`, `vocabulary-growth-modelling-explainer.html` | Study 1: plain-language and technical explainers |
| `reading-language-predictors-explainer.html`, `reading-language-predictors-modelling-explainer.html` | Study 2: plain-language and technical explainers |
| `asset-generation-explainer.html` | Technical note on the teaching-material pipelines |
| `sp-500-stock-screener-explainer.html`, `epidemic-cellular-automaton-explainer.html` | Deep dives for the two independent projects |
| `vocabulary-growth-demo.html` | An interactive posterior, drawn on a canvas |
| `*.pdf` | The three research showcase decks |
| `figures/` | Sources for every chart, Open Graph card and showcase deck, and `render.sh` to rebuild them. `figures/panels/` holds the two plot panels with the scripts that draw them from model output, and the script that rebuilds the demo page's data |
| `assets/site.css`, `assets/theme.js` | The design tokens, type and light/dark switch shared by every page. Loaded after each page's own styles, so a change here applies everywhere |
| `assets/` | Rendered figures, cards, favicon and the CV PDF |

The investment thesis linked from the projects section lives in its own repository, `ethanbuckley/computable-world`.

## Editing rules

- The design system is `assets/site.css` and `assets/theme.js`, linked from every page after its own `<style>`. Tokens (white ground, near-black ink, one blue accent, system sans, mono for numbers only), the dark palette and the theme switch live there, so a colour or type change is made once. Page-level styles handle layout only.
- Dark mode follows the system until the visitor chooses. The choice is stored in `localStorage` under `theme` and applied as `data-theme` on `<html>` before first paint.
- Figures are never hand-patched. Edit the source in `figures/` and run `figures/render.sh`, which renders through headless Chrome and writes the PNG, WebP and PDF outputs.
- After editing `cv.html`, reprint the PDF and check it is still one page:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless --disable-gpu --no-pdf-header-footer --blink-settings=preferredColorScheme=1 --print-to-pdf="$PWD/assets/ethan-buckley-cv.pdf" "file://$PWD/cv.html" && pdfinfo assets/ethan-buckley-cv.pdf | grep Pages
```

- Nothing public carries a phone number or a grade of any kind.
- The DSE material was cleared for description in general terms. It carries no money figures, no provider or model names, no generated images and no claim about image quality.
- The same fact should appear once per page and read the same on every page. Before pushing, grep for the numbers that recur (children, studies, items, nodes) and check they agree.
- No em-dashes in prose.
- The "Now" line under the hero is dated. Update it when the month changes, or remove it; a stale one is worse than none.
- The two plot panels are drawn from model output by `figures/panels/render_panels.py` and `render_effects_panel.py`; the demo page's data comes from `render_demo_data.py`. `figures/panels/PROVENANCE.md` names the fit each one currently shows. Do not edit the PNGs or the `DATA` block by hand.

## Publishing

The default branch is `main` and GitHub Pages serves it directly. Changes are live within a minute or two of a push.
