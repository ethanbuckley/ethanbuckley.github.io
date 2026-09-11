#!/usr/bin/env python3
"""One definition of how a figure on this site looks.

The conventions here are the DSE research style, copied from
``dse_research_utils.plot.styles`` (``DEFAULT_STYLE_DICT``), which is what
renders the figures in the vocabulary-growth report. The site cannot import that
package — it is a static site with no Python dependencies — so the values are
copied, and this docstring is the record of where they came from. If the shared
package changes, this file has to be updated by hand.

What the research style does, and why each part reads as scientific rather than
decorative:

* a grid on **both** axes, hairline (0.25pt) and light grey, so a reader can
  take a value off either scale without the grid competing with the data;
* **no spines at all** — the grid already bounds the plot, so a frame is a
  second statement of the same thing;
* a **framed** legend, which is a caption for the marks rather than a floating
  label, and reads as part of the figure;
* text at ``#333333`` rather than near-black, and axis labels at medium weight.

Two things deliberately differ from the shared package. The accent stays the
site's ``#2440b3`` rather than the report's ``#014b7f``, so a figure sits inside
the page it is embedded in. And the canvas stays in pixels rather than the
package's A-series inches, because each plate embeds its panel at exactly half
size and the pixel dimensions are load-bearing.

``Source Sans 3`` heads the font stack to match the research style, but nothing
on this machine has it — the report falls back to Helvetica too, so the two
already agree in practice.

Built by an LLM-based AI tool (Claude Code/Opus 5).
"""

from __future__ import annotations

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402

# ---------------------------------------------------------------- palette ----

# From the research style.
TEXT = "#333333"       # all text: labels, ticks, annotations
LINE = "#c0c0c0"       # the hairline grid
PAPER = "#ffffff"

# The site's own accent, kept instead of the report's dark blue so a figure
# belongs to the page it is embedded in.
ACCENT = "#2440b3"
MUTED = "#8d97a3"      # a series the reader should weigh less, e.g. spans zero
SOFT = "#5b6571"       # secondary text where it must sit quieter than TEXT

# The research style names this first; nothing here has it, so Helvetica wins.
SANS = ["Source Sans 3", "Helvetica Neue LT Std", "Helvetica Neue", "Helvetica",
        "Arial", "DejaVu Sans"]

# The panels render at 2x and embed at half size, so these run larger than the
# research style's 12pt, which is set for A5 at 300dpi.
#
# "group" is deliberately smaller than "label": a group heading is a quiet aside
# above the rows it covers, not a peer of them. It is also bounded rather than
# merely tasteful — the forest plot draws its headings in the left margin, and
# at 14 the longest ("Decoding and phonics, taught directly") overflows the
# canvas. 13 is the largest that fits.
SIZE = {"tick": 14, "label": 15, "annot": 14, "legend": 14, "group": 13}


def use() -> None:
    """Set every default we rely on, so no drawing call has to restate it."""
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": SANS,
        "text.color": TEXT,
        "axes.labelcolor": TEXT,
        "axes.labelsize": SIZE["label"],
        "axes.labelweight": "medium",
        "axes.titleweight": "medium",
        "axes.facecolor": PAPER,
        "axes.edgecolor": LINE,
        "axes.linewidth": 0,          # the grid bounds the plot; a frame repeats it
        "axes.axisbelow": True,
        "axes.grid": True,
        "axes.grid.which": "major",
        "figure.facecolor": PAPER,
        "savefig.facecolor": PAPER,
        "grid.linestyle": "-",
        "grid.color": LINE,
        "grid.linewidth": 0.25,
        "grid.alpha": 1,
        "xtick.color": TEXT,
        "ytick.color": TEXT,
        "xtick.labelsize": SIZE["tick"],
        "ytick.labelsize": SIZE["tick"],
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.size": 0,
        "ytick.major.size": 0,
        "legend.fontsize": SIZE["legend"],
        "legend.frameon": True,
        "legend.numpoints": 1,
        "legend.scatterpoints": 1,
        "lines.solid_capstyle": "round",
        "patch.edgecolor": "#ffffffff",
        "patch.linewidth": 0.75,
    })


def style_axes(ax, *, grid: str = "both") -> None:
    """Apply the research treatment: hairline grid on both axes, no spines.

    ``grid`` is an escape hatch for a plot where one direction carries no scale
    worth reading against, but "both" is the house default.
    """
    ax.grid(grid in ("both", "y"), axis="y")
    ax.grid(grid in ("both", "x"), axis="x")
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)
    ax.tick_params(length=0, pad=8)


def pad_limits(ax, lo: float, hi: float, *, frac: float = 0.035, axis: str = "x") -> None:
    """Set limits with breathing room at each end.

    Pinning an axis to ``min(data), max(data)`` is what put the production
    ratio's last marker on the right spine and clipped its label.
    """
    pad = (hi - lo) * frac
    if axis == "x":
        ax.set_xlim(lo - pad, hi + pad)
    else:
        ax.set_ylim(lo - pad, hi + pad)


def legend(ax, handles, *, loc: str = "upper left"):
    """A framed legend in the research style: hairline border, white ground."""
    leg = ax.legend(handles=handles, loc=loc, frameon=True,
                    handlelength=1.8, borderpad=0.7, labelspacing=0.6,
                    facecolor=PAPER, edgecolor=LINE, framealpha=1.0)
    leg.get_frame().set_linewidth(0.5)
    for text in leg.get_texts():
        text.set_color(TEXT)
    return leg
