"""Nastavnikov checker — točni flagovi za cijeli kolegij iz jedne naredbe.

    ISS_SECRET='<tajna>' python checker.py roster.txt > KEY.csv

`roster.txt` = popis matičnih brojeva upisanih u kolegij (jedan po retku), koji
već imaš. Ispisuje CSV: matični broj + flag za svaku vježbu sa self-seed flagom
(Lab 01, 05, 06, 07). Isti `ISS_SECRET` mora se koristiti i u metama (`.env`).
KEY.csv drži samo za sebe.
"""
import csv
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # _lab-env na path
from flaglib import make_flag  # noqa: E402

LABS = ["lab01", "lab02", "lab06", "lab07", "lab08"]


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: ISS_SECRET=... python checker.py roster.txt > KEY.csv")
    secret = os.environ.get("ISS_SECRET")
    if not secret:
        sys.exit("error: postavi ISS_SECRET (tajni seed)")
    roster = [l.strip() for l in Path(sys.argv[1]).read_text().splitlines() if l.strip()]
    w = csv.writer(sys.stdout)
    w.writerow(["maticni_broj", *LABS])
    for mb in roster:
        w.writerow([mb, *[make_flag(lab, mb, secret) for lab in LABS]])


if __name__ == "__main__":
    main()
