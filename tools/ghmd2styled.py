#!/usr/bin/env python3
"""GitHub-flavoured lab README -> styled markdown for the PDF build.

Single source: each lab is authored as a clean GitHub `README.md` (and
`README.hr.md`). GitHub renders it natively; this script turns the same file
into the styled markdown that `tools/handout.css` expects, so `build-pdf.sh`
can produce the Merlin PDF. Only the presentation is transformed, never the text.

Conventions in the source (both render fine on GitHub):
  <!-- kicker: Lab 01 · attack then defend · Information System Security -->
  # Lab 01 — Title
  *one-line italic subtitle*
  `~90 min` · `Kali · hashcat` · `level: intro` · `submit: Merlin`
  ...
  > [!WARNING]  -> ethics blockquote
  > [!NOTE]     -> green "expected" box
  > [!TIP]      -> amber "pitfall" box
  > [!IMPORTANT]-> red "deliver" box
  ## Part 1 — ... · ~40 min   -> red part divider
  ### Bonus                   -> purple bonus box

Usage: python ghmd2styled.py README.md "Course name" > _styled.md
"""
import re
import sys
from pathlib import Path

ALERT = {
    "NOTE": ("expected", "Expected"),
    "TIP": ("hint", "Heads up"),
    "IMPORTANT": ("deliver", "In the report"),
    "CAUTION": ("note", "Note"),
}
BONUS_HEADINGS = ("Bonus", "Za brze", "Za brze — bonus", "For the fast")


def main():
    src = Path(sys.argv[1]).read_text(encoding="utf-8")
    course = sys.argv[2] if len(sys.argv) > 2 else "Information System Security"
    lines = src.splitlines()

    # --- front matter: kicker / title / subtitle / pills ---
    kicker = next((l[len("<!-- kicker:"):].strip(" ->") for l in lines
                   if l.strip().startswith("<!-- kicker:")), course)
    title = next((l[2:].strip() for l in lines if l.startswith("# ")), "")
    body_start = next(i for i, l in enumerate(lines) if l.startswith("# ")) + 1
    rest = lines[body_start:]
    subtitle, pills = "", []
    i = 0
    while i < len(rest):
        s = rest[i].strip()
        if not s:
            i += 1
            continue
        if s.startswith("*") and s.endswith("*") and not subtitle:
            subtitle = s.strip("*").strip()
            i += 1
            continue
        if s.startswith("`") and "·" in s and not pills:
            pills = [p.strip().strip("`") for p in s.split("·")]
            i += 1
            break
        break
    body = rest[i:]

    # kicker = "Lab NN · <tagline> · Course"  ->  masthead "Course · Lab NN", hero ".n" = tagline
    kparts = [p.strip() for p in kicker.split("·")]
    lab_no = kparts[0]
    course_k = kparts[-1] if len(kparts) > 1 else course
    tagline = " · ".join(kparts[1:-1]) if len(kparts) > 2 else lab_no

    out = []
    out.append('<div class="masthead">')
    out.append('<img src="tools/logo.png" alt="Aspira" class="logo">')
    out.append(f'<div class="kicker">{course_k} · {lab_no}</div>')
    out.append('</div>\n')
    out.append('<div class="lab-hero">')
    out.append(f'<div class="n">{lab_no} · {tagline}</div>')
    out.append(f'<div class="t">{title.split("—", 1)[-1].strip() if "—" in title else title}</div>')
    if subtitle:
        out.append(f'<div class="s">{subtitle}</div>')
    if pills:
        out.append('<div class="meta">' + "".join(f"<span>{p}</span>" for p in pills) + '</div>')
    out.append('</div>\n')

    # --- body: alerts, part dividers, bonus boxes ---
    n = 0
    while n < len(body):
        line = body[n]
        m = re.match(r"^> \[!(\w+)\]\s*$", line)
        if m:
            kind = m.group(1).upper()
            n += 1
            block = []
            while n < len(body) and body[n].startswith(">"):
                block.append(re.sub(r"^>\s?", "", body[n]))
                n += 1
            text = "\n".join(block).strip()
            if kind == "WARNING":
                out.append("> " + text.replace("\n", "\n> ") + "\n")
            else:
                cls, deflabel = ALERT.get(kind, ("note", "Note"))
                mlab = re.match(r"^\*\*([^*]+?)\.?\*\*\s*", text)   # label = leading bold (localised)
                label = mlab.group(1) if mlab else deflabel
                bodytext = text[mlab.end():].strip() if mlab else text
                out.append(f'<div class="{cls}">')
                out.append(f'<p>{label}</p>\n')
                out.append(bodytext + "\n")
                out.append('</div>\n')
            continue
        m = re.match(r"^## (Part .+?|Dio .+?)\s*·\s*(~?.+?)\s*$", line)
        if m:
            out.append(f'<div class="part">{m.group(1)} <span class="t2">· {m.group(2)}</span></div>\n')
            n += 1
            continue
        m = re.match(r"^### (.+)$", line)
        if m and any(m.group(1).startswith(b) for b in BONUS_HEADINGS):
            n += 1
            inner = []
            while n < len(body) and not re.match(r"^#{1,3} ", body[n]):
                inner.append(body[n])
                n += 1
            out.append('<div class="stretch">')
            out.append(f'<p>{m.group(1)}</p>')
            out.append("\n".join(inner).strip() + "\n")
            out.append('</div>\n')
            continue
        out.append(line)
        n += 1

    # rubric table: tag the grading table so CSS can centre the points column
    text = "\n".join(out)
    text = text.replace("| Item | Points |", '<div class="rubric">\n\n| Item | Points |')
    text = text.replace("| Stavka | Bodovi |", '<div class="rubric">\n\n| Stavka | Bodovi |')
    # close rubric div at end of doc if opened
    if '<div class="rubric">' in text:
        text = text.rstrip() + "\n\n</div>"
    text += f'\n\n<p class="small footer-note">{course} · Aspira · submit via Merlin</p>\n'
    sys.stdout.write(text)


if __name__ == "__main__":
    main()
