#!/usr/bin/env bash
# Render the four figure sources in figures/ to the site assets in assets/,
# plus the four Open Graph cards, then re-print the three showcase-deck PDFs
# that embed the plate renders.
#
# For each figure this renders the 1600x1000 CSS px HTML at a 2x device scale
# factor (giving the 3200x2000 PNG master the site links to), then emits the
# two 1600px-wide derivatives the page actually loads:
#   assets/<name>.png           3200x2000 master
#   assets/<name>-1600.webp     1600px WebP (quality 88)
#   assets/<name>-1600.png      1600px palettised PNG fallback
#
# Requirements:
#   - Google Chrome (headless screenshot mode)
#   - a Python with Pillow, for the derivatives; set RENDER_PYTHON to override

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(dirname "$SCRIPT_DIR")"
ASSETS_DIR="$REPO_DIR/assets"

CHROME="${RENDER_CHROME:-/Applications/Google Chrome.app/Contents/MacOS/Google Chrome}"

# Default to the venv used when these figures were first built; fall back to
# any python3 on PATH. Either way it must have Pillow importable.
PYTHON_DEFAULT="/private/tmp/claude-501/-Users-ethanbuckley-Documents-GitHub-dseinternational-vocabulary-growth--claude-worktrees-quirky-joliot-84e243/57cd0658-2c06-487b-b127-72154ef17a69/scratchpad/venv/bin/python"
PYTHON="${RENDER_PYTHON:-$PYTHON_DEFAULT}"
if [ ! -x "$PYTHON" ]; then
  PYTHON="$(command -v python3 || true)"
fi
if [ -z "${PYTHON}" ] || ! "$PYTHON" -c "import PIL" >/dev/null 2>&1; then
  echo "error: need a Python with Pillow; set RENDER_PYTHON=/path/to/python" >&2
  exit 1
fi
if [ ! -x "$CHROME" ]; then
  echo "error: Google Chrome not found at: $CHROME (set RENDER_CHROME)" >&2
  exit 1
fi

# source HTML basename -> published asset basename (referenced by index.html;
# do not rename these).
FIGURES=(
  "production-ratio:vocab-production-ratio"
  "vocab-method:vocab-method"
  "intervention-effects:reading-intervention-effects"
  "causal-design:reading-causal-design"
)

for pair in "${FIGURES[@]}"; do
  src="${pair%%:*}"
  out="${pair##*:}"
  master="$ASSETS_DIR/$out.png"

  echo "==> $src.html -> $out"
  "$CHROME" --headless --disable-gpu \
    --hide-scrollbars --force-device-scale-factor=2 --window-size=1600,1000 \
    --screenshot="$master" "file://$SCRIPT_DIR/$src.html"

  "$PYTHON" - "$master" "$ASSETS_DIR/$out" <<'PY'
import sys
from PIL import Image

master, base = sys.argv[1], sys.argv[2]
im = Image.open(master).convert("RGB")
if im.size != (3200, 2000):
    raise SystemExit(f"error: {master} is {im.size}, expected (3200, 2000)")
r = im.resize((1600, round(im.height*1600/im.width)), Image.LANCZOS)
r.save(base + "-1600.webp", format="WEBP", quality=88, method=6)
r.convert("P", palette=Image.ADAPTIVE, colors=256).save(base + "-1600.png", format="PNG", optimize=True)
print(f"    {base}-1600.webp / -1600.png written")
PY
done

# The Open Graph cards are a different shape from the four plates: 1200 x 630 CSS px,
# the 1.91:1 ratio Facebook, LinkedIn and Slack all crop to. They get no -1600
# derivatives because nothing on the site loads them; only link unfurlers fetch them.
OG_CARDS=(
  "og-card-production-ratio"
  "og-card-intervention-effects"
  "og-card-vocab-method"
  "og-card-asset-generation"
)
for src in "${OG_CARDS[@]}"; do
  echo "==> $src.html -> $src (1200x630 Open Graph card)"
  OG_MASTER="$ASSETS_DIR/$src.png"
  "$CHROME" --headless --disable-gpu \
    --hide-scrollbars --force-device-scale-factor=2 --window-size=1200,630 \
    --blink-settings=preferredColorScheme=1 \
    --screenshot="$OG_MASTER" "file://$SCRIPT_DIR/$src.html"

  "$PYTHON" - "$OG_MASTER" <<'PY'
import sys
from PIL import Image

p = sys.argv[1]
im = Image.open(p).convert("RGB")
if im.size != (2400, 1260):
    raise SystemExit(f"error: {p} is {im.size}, expected (2400, 1260)")
im.resize((1200, 630), Image.LANCZOS).save(p, optimize=True)
print("    written at 1200x630")
PY
done

# The three showcase decks embed the plate masters rendered above, so they are
# re-printed here whenever the plates change. Each source is a multi-sheet HTML
# file in figures/; Chrome prints one PDF per deck into the repo root, under the
# filenames index.html links (do not rename them).
DECKS=(
  "showcase-dse-research:dse-research-showcase"
  "showcase-vocabulary-growth:vocabulary-growth-showcase"
  "showcase-reading-language:reading-language-showcase"
)
for pair in "${DECKS[@]}"; do
  src="${pair%%:*}"
  out="${pair##*:}"
  echo "==> $src.html -> $out.pdf"
  "$CHROME" --headless --disable-gpu --no-pdf-header-footer \
    --print-to-pdf="$REPO_DIR/$out.pdf" "file://$SCRIPT_DIR/$src.html"
done

echo "Done. Rendered ${#FIGURES[@]} figures plus ${#OG_CARDS[@]} Open Graph cards into $ASSETS_DIR, and ${#DECKS[@]} showcase PDFs into $REPO_DIR"
