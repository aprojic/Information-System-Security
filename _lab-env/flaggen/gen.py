#!/usr/bin/env python3
"""Per-student hash + flag generator for ISS Lab 01 (password hashing & cracking).

Each student gets a personal file `hashes_<MB>.txt` (MB = matični broj studenta) containing five MD5/bcrypt
hashes. Three are common passwords (crackable with a rockyou dictionary attack),
one is a bcrypt hash of a strong password (should NOT crack in lab time — the
defensive lesson), and one is the student's personal FLAG:

    ASPIRA{sis_<6 hex chars>}

hashed with MD5. The 6 hex chars are derived with HMAC from the student's MB
and a secret seed only the instructor knows, so the flag is unique per student and
unpredictable, yet deterministic (regenerate any time to verify). Students recover
it with a mask / brute-force attack because the format is given in the handout —
a chatbot cannot produce their hex, only running the crack can.

Run (needs the bcrypt package):
    ISS_SECRET='<your secret>' uv run --with bcrypt python gen.py roster.txt
where roster.txt has one MB per line. Output lands in ./out/ plus an
instructor answer key KEY_instructor.csv. Keep the secret and the key off Merlin.
"""
import csv
import hashlib
import hmac
import os
import sys
from pathlib import Path

import bcrypt

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # _lab-env on path
from flaglib import make_flag  # noqa: E402  (shared flag formula, matches checker.py)

# Common passwords present in the rockyou wordlist — crackable by dictionary.
WEAK_POOL = [
    "password1", "qwerty123", "letmein1", "iloveyou2", "sunshine3",
    "dragon12", "monkey99", "football7", "princess5", "superman8",
    "trustno1", "whatever9", "babygirl4", "master12", "shadow77",
]
# Strong passwords for the bcrypt hash — not in any practical wordlist.
STRONG_POOL = [
    "T7#qZ!m2rLx9$Vd", "9pG@wK4^nB1&eUa", "Hx2!vR8$cM6#qZt",
    "kL5&dN0@yW3!bFs", "Qa7#zE2$rT9^mVx", "3bU!gH6&wP1@nKd",
]


def prng(secret: bytes, mb: str, tag: str) -> int:
    """Deterministic unsigned int from (secret, mb, tag)."""
    mac = hmac.new(secret, f"{mb}:{tag}".encode(), hashlib.sha256).digest()
    return int.from_bytes(mac[:8], "big")


def pick(pool, secret, mb, tag, count):
    out, i = [], 0
    while len(out) < count:
        item = pool[prng(secret, mb, f"{tag}{i}") % len(pool)]
        if item not in out:
            out.append(item)
        i += 1
    return out


def md5(s: str) -> str:
    return hashlib.md5(s.encode()).hexdigest()


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: ISS_SECRET=... python gen.py roster.txt")
    secret = os.environ.get("ISS_SECRET")
    if not secret:
        sys.exit("error: set ISS_SECRET environment variable (instructor seed)")
    secret_str = secret
    secret = secret.encode()

    roster = [l.strip() for l in Path(sys.argv[1]).read_text().splitlines() if l.strip()]
    out = Path("out")
    out.mkdir(exist_ok=True)
    key_rows = []

    for mb in roster:
        flag = make_flag("lab01", mb, secret_str)   # isti flag kao checker.py
        weak = pick(WEAK_POOL, secret, mb, "weak", 3)
        strong = STRONG_POOL[prng(secret, mb, "strong") % len(STRONG_POOL)]

        bc = bcrypt.hashpw(strong.encode(), bcrypt.gensalt(rounds=10)).decode()
        lines = [md5(w) for w in weak] + [bc, md5(flag)]
        # Shuffle deterministically so the flag isn't always last.
        order = sorted(range(len(lines)), key=lambda i: prng(secret, mb, f"ord{i}"))
        lines = [lines[i] for i in order]

        (out / f"hashes_{mb}.txt").write_text("\n".join(lines) + "\n")
        key_rows.append([mb, flag, *weak, strong])

    with (Path("KEY_instructor.csv")).open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["MB", "FLAG", "weak1", "weak2", "weak3", "strong(bcrypt)"])
        w.writerows(key_rows)

    print(f"OK: {len(roster)} student files in out/, answer key in KEY_instructor.csv")


if __name__ == "__main__":
    main()
