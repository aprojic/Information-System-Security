#!/bin/zsh
# Build a Merlin PDF from a lab's GitHub README (single source).
# Usage (from repo root):  tools/build-pdf.sh lab-01-hashiranje/README.md
#        Croatian:         tools/build-pdf.sh lab-01-hashiranje/README.hr.md
# Output: <same dir>/README.pdf (or README.hr.pdf). PDFs are git-ignored.
# Needs: apex, Google Chrome, python3.
set -euo pipefail
ROOT=${0:A:h:h}            # repo root (tools/ -> ..)
MD=${1:A}
case "$MD" in
  *.hr.md) COURSE="Sigurnost informacijskih sustava" ;;
  *)       COURSE="Information System Security" ;;
esac
TITLE=$(sed -n 's/^# //p' "$MD" | head -1)
PDF=${MD:r}.pdf
STYLED=$(mktemp /tmp/iss-styled-XXXX.md)
HTML=$(mktemp /tmp/iss-styled-XXXX.html)

python3 "$ROOT/tools/ghmd2styled.py" "$MD" "$COURSE" > "$STYLED"
apex -s --no-image-captions --css "$ROOT/tools/handout.css" --embed-css \
  --base-dir "$ROOT" "$STYLED" -o "$HTML"
python3 - "$HTML" "$ROOT" <<'PY'
import base64, mimetypes, re, sys
from pathlib import Path
html, base = Path(sys.argv[1]), Path(sys.argv[2])
def inline(m):
    src = m.group(2)
    f = base / src
    if src.startswith(("data:", "http")) or not f.exists():
        return m.group(0)
    mime = mimetypes.guess_type(f.name)[0] or "application/octet-stream"
    return f'{m.group(1)}data:{mime};base64,{base64.b64encode(f.read_bytes()).decode()}"'
html.write_text(re.sub(r'(<img[^>]*?src=")([^"]+)"', inline, html.read_text(encoding="utf-8")),
                encoding="utf-8")
PY
sed -i '' "s|<title>Document|<title>${TITLE}|" "$HTML"
timeout 90 "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --headless=new \
  --disable-gpu --no-pdf-header-footer --run-all-compositor-stages-before-draw \
  --print-to-pdf="$PDF" "$HTML" 2>/dev/null
rm -f "$STYLED" "$HTML"
echo "OK: ${PDF}"
