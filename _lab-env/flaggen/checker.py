"""Nastavnikov checker — točni flagovi za cijeli kolegij iz jedne naredbe.

    ISS_SECRET='<tajna>' python checker.py roster.txt > KEY.csv

`roster.txt` = popis matičnih brojeva upisanih u kolegij (jedan po retku), koji
već imaš. Ispisuje CSV: matični broj + flag za svaku vježbu sa self-seed flagom
(Lab 01, 05, 06, 07). Isti `ISS_SECRET` mora se koristiti i u metama (`.env`).
KEY.csv drži samo za sebe.

    ISS_SECRET='<tajna>' python checker.py --lab07 roster.txt > KEY_lab07.csv

`--lab07` ispisuje ključ za analizu zapisnika u Lab 07: uz flag i IP napadača,
broj neuspjelih prijava te vremena prvog zahtjeva, prijave i iznošenja podataka.
Računa ih isti kôd koji studentu generira zapisnik (`lab-07-ctf/make_incident.py`).
"""
import csv
import importlib.util
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # _lab-env na path
from flaglib import make_flag  # noqa: E402

LABS = ["lab01", "lab02", "lab06", "lab07", "lab08"]


def lab07_key(roster, secret):
    """Ključ za Lab 07 iz generatora zapisnika (isti kôd, pa isti odgovori kao u studentovom logu)."""
    path = Path(__file__).resolve().parents[2] / "lab-07-ctf" / "make_incident.py"
    spec = importlib.util.spec_from_file_location("make_incident", path)
    gen = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True      # bez __pycache__ u mapi vježbe
    spec.loader.exec_module(gen)
    cols = ["flag", "attacker_ip", "failed_logins", "first_seen", "login_time", "exfil_time"]
    w = csv.writer(sys.stdout)
    w.writerow(["maticni_broj", *cols])
    for mb in roster:
        answers = gen.build(mb, secret)[1]
        w.writerow([mb, *[answers[c] for c in cols]])


def main():
    args = sys.argv[1:]
    lab07 = args[:1] == ["--lab07"]
    if lab07:
        args = args[1:]
    if len(args) != 1:
        sys.exit("usage: ISS_SECRET=... python checker.py [--lab07] roster.txt > KEY.csv")
    secret = os.environ.get("ISS_SECRET")
    if not secret:
        sys.exit("error: postavi ISS_SECRET (tajni seed)")
    roster = [l.strip() for l in Path(args[0]).read_text().splitlines() if l.strip()]
    if lab07:
        return lab07_key(roster, secret)
    w = csv.writer(sys.stdout)
    w.writerow(["maticni_broj", *LABS])
    for mb in roster:
        w.writerow([mb, *[make_flag(lab, mb, secret) for lab in LABS]])


if __name__ == "__main__":
    main()
