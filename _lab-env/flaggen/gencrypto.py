#!/usr/bin/env python3
"""Per-student ciphertext generator for ISS Lab 02 (cryptography).

Each student gets a personal file `vault_<MB>.b64` (MB = matični broj studenta):
their FLAG

    ASPIRA{sis_crypto_<6 hex chars>}

"encrypted" the way Flicker rolled its own crypto — XOR with a short repeating
key, then Base64. That is deliberately broken: the flag format is public, so the
first 18 bytes of plaintext are known (`ASPIRA{sis_crypto_`). A known-plaintext
attack recovers the key and the flag. The student never gets the key or this
script — only the ciphertext — so breaking it (not inverting the source) is the
exercise. The flag's 6 hex chars come from HMAC(secret, "lab02:MB"), matching
`flaglib.make_flag` and `checker.py`, so it is unique per student yet deterministic.

Run (stdlib only, no extra packages):
    ISS_SECRET='<your secret>' python3 gencrypto.py roster.txt
where roster.txt has one MB per line. Output lands in ./out/ plus an instructor
answer key KEY_crypto.csv. Keep the secret and the key off Merlin.
"""
import base64
import csv
import hashlib
import hmac
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # _lab-env on path
from flaglib import make_flag  # noqa: E402  (shared flag formula, matches checker.py)

KEY_LEN = 12  # shorter than the 18-byte known prefix, so it is fully recoverable


def xor_key(secret: bytes, mb: str) -> bytes:
    """Per-student repeating key, unpredictable without the secret."""
    return hmac.new(secret, f"vault:{mb}".encode(), hashlib.sha256).digest()[:KEY_LEN]


def xor_bytes(data: bytes, key: bytes) -> bytes:
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def main():
    if len(sys.argv) != 2:
        sys.exit("usage: ISS_SECRET=... python3 gencrypto.py roster.txt")
    secret_str = os.environ.get("ISS_SECRET")
    if not secret_str:
        sys.exit("error: set ISS_SECRET environment variable (instructor seed)")
    secret = secret_str.encode()

    roster = [l.strip() for l in Path(sys.argv[1]).read_text().splitlines() if l.strip()]
    out = Path("out")
    out.mkdir(exist_ok=True)
    key_rows = []

    for mb in roster:
        flag = make_flag("lab02", mb, secret_str)      # same flag as checker.py
        key = xor_key(secret, mb)
        b64 = base64.b64encode(xor_bytes(flag.encode(), key)).decode()
        (out / f"vault_{mb}.b64").write_text(b64 + "\n")
        key_rows.append([mb, flag, key.hex()])

    with Path("KEY_crypto.csv").open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["MB", "FLAG", "xor_key_hex"])
        w.writerows(key_rows)

    print(f"OK: {len(roster)} student files in out/, answer key in KEY_crypto.csv")


if __name__ == "__main__":
    main()
