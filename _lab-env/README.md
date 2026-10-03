# `_lab-env/` — shared flag tooling

Per-student flags for the labs are derived from the student's **student ID (matični broj)** and a secret seed the instructor sets once, so the same material works for everyone while each student's flag is unique.

| File | What it does |
|---|---|
| `flaglib.py` | the flag formula `f(ISS_SECRET, student-id)` → `ASPIRA{...}`, shared by the targets and the checker |
| `flaggen/checker.py` | over a roster of student IDs → a CSV of every correct flag (Lab 01/02/06/07/08), for grading |
| `flaggen/gen.py` | generates the Lab 01 personal hash files from the roster |
| `flaggen/gencrypto.py` | generates the Lab 02 personal ciphertext files (`vault_<id>.b64`) from the roster |
| `.env.example` | copy to `.env` and set `ISS_SECRET` (the instructor's secret seed) |

How each lab gets its flag:

- **Lab 01** — the instructor runs `gen.py` once over the roster and hands out `hashes_<id>.txt`; the student cracks it.
- **Lab 02** — the instructor runs `gencrypto.py` once over the roster and hands out `vault_<id>.b64` (plus the shared `ecb_demo.bin`); the student breaks the weak crypto to recover the flag.
- **Lab 06 / 08** — the target computes the flag at runtime from the student ID you provide.
- **Lab 07** — `make_incident.py <student-id>` builds your personalised log.

The real `.env` (the secret) and the answer-key CSV are **git-ignored** and never published. Students submit a PDF report with their flag plus an [asciinema](https://asciinema.org/) recording; no flag means no live-defence check is needed.
