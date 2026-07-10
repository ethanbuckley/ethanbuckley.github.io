# ethanbuckley.github.io — personal portfolio site

> [!NOTE]
> Drafted by an LLM-based AI tool (Claude Code/Opus 4.8), from the vetted explainers and showcase documents in the parent folder. Review before publishing.

A single-page static portfolio: plain HTML + CSS, system fonts, no JavaScript, no build step. Works opened straight from disk (`index.html`) and on GitHub Pages.

## Contents

| File | What it is |
| --- | --- |
| `index.html` | The portfolio page |
| `vocabulary-growth-explainer.html` | Study 1 — plain-language explainer |
| `vocabulary-growth-modelling-explainer.html` | Study 1 — technical explainer |
| `reading-language-predictors-explainer.html` | Study 2 — plain-language explainer |
| `reading-language-predictors-modelling-explainer.html` | Study 2 — technical explainer |
| `dse-research-showcase.pdf` | Six-page merged research showcase (the main download) |
| `vocabulary-growth-showcase.pdf`, `reading-language-showcase.pdf` | Per-study showcase PDFs |
| `assets/` | Figures (PNG) and favicon |
| `README.md` | This file — not linked from the site, safe to keep |

## Before you deploy — one edit

Replace the email placeholder in `index.html`: search for `[ your email ]` (in the Contact section) and swap in your address, e.g. `<a href="mailto:you@example.com">you@example.com</a>`. Delete the adjacent "replace before publishing" note too.

## Deploy to GitHub Pages (free, no domain needed)

1. On github.com, create a new **public** repository named exactly `ethanbuckley.github.io` (no README, no .gitignore — completely empty).
2. Then, from this folder:

```bash
cd /Users/ethanbuckley/Documents/Internships-and-Careers/DSE/portfolio-site
git init
git add -A
git commit -m "Portfolio site"
git branch -M main
git remote add origin https://github.com/ethanbuckley/ethanbuckley.github.io.git
git push -u origin main
```

3. That's it. For a repo named `<username>.github.io`, GitHub Pages serves the default branch automatically; check **Settings → Pages** if it hasn't appeared. The site goes live at **https://ethanbuckley.github.io** within a few minutes.

The free `.github.io` URL needs no domain purchase. A custom domain (for example `ethanbuckley.co.uk`, roughly £10/yr) is optional, not required — it can be added later under Settings → Pages → Custom domain without changing anything in the site.

## Updating later

Edit the files, then:

```bash
git add -A && git commit -m "Update site" && git push
```

Changes appear on the live site within a minute or two.
