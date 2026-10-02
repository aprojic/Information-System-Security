**Language:** English · [Hrvatski](README.hr.md)

<!-- kicker: Lab 01 · attack then defend · Information System Security -->
# Lab 01 — Password Hashing & Cracking

*How to turn a leaked password database from a disaster into a nuisance — it all comes down to one engineering decision.*

`~90 min` · `Kali · hashcat · john` · `level: intro` · `submit: Merlin`

> [!WARNING]
> **Ethics & scope.** Work only on the hashes you are given in this lab, inside the lab environment. Cracking other people's passwords is a criminal offence.

**Scenario.** The startup **Flicker** has been breached — someone dumped a file of its users' password hashes. You're first the **attacker** who shows how bad that is, then the **engineer** who changes the storage so the next dump is worthless.

- **Offensive:** crack the hashes from Flicker's dump with dictionary and mask attacks.
- **Defensive:** show the same attack fails against bcrypt and fix the storage.

## Learning outcomes

- Identify a hash type and judge whether it's fit for storing passwords.
- Run dictionary and mask attacks with hashcat and crack weak hashes.
- Explain why a *salt* and a *slow* hash function (bcrypt/argon2) defeat the same attack.
- Give concrete recommendations for storing passwords in a web application.

## Prerequisites

- [ ] [Lab 00](../lab-00-okruzenje/README.md) completed — Kali working.
- [ ] Tools `hashcat`, `hashid`, `john` and the `rockyou.txt` wordlist (standard on Kali).
- [ ] Your **student ID (matični broj)**.

## Setup · ~10 min

Download **your** file `hashes_<ID>.txt` from Merlin (five hashes from Flicker's dump) and check the tools:

```bash
hashcat --version
ls -l /usr/share/wordlists/rockyou.txt   # if needed: sudo gunzip /usr/share/wordlists/rockyou.txt.gz
```

## Part 1 — Offensive: cracking passwords · ~40 min

### 1.1 Identify the hashes

For each of the five hashes, determine the likely type with `hashid '<hash>'`. **In the report:** a five-row table (index, hash, type, hashcat mode `-m`). One is bcrypt (`$2b$...`), the rest MD5.

### 1.2 Dictionary attack on the weak hashes

```bash
hashcat -m 0 -a 0 hashes_<ID>.txt /usr/share/wordlists/rockyou.txt
hashcat -m 0 -a 0 hashes_<ID>.txt /usr/share/wordlists/rockyou.txt --show
```

> [!NOTE]
> **Expected.** The three MD5 hashes fall almost instantly. hashcat ignores the bcrypt hash here (it isn't mode 0); you may see a `Token length exception` for that line — expected, it's the bcrypt hash being skipped.

### 1.3 Mask attack on your personal FLAG

One MD5 hash is your personal flag of the form `ASPIRA{sis_XXXXXX}`, where `XXXXXX` is 6 hex characters (`0-9`, `a-f`). The format is known, so use a mask attack:

```bash
hashcat -m 0 -a 3 hashes_<ID>.txt 'ASPIRA{sis_?h?h?h?h?h?h}'
```

> [!TIP]
> **Common pitfall.** `?h` is hashcat's lowercase-hex charset. All 16⁶ combinations take a few seconds for MD5. "Token length exception" → stray whitespace in the line.

**In the report:** the three cracked passwords and **your flag**; attach the `hashcat --show` output as your process log.

## Part 2 — Defensive: secure storage · ~30 min

### 2.1 The same attack against bcrypt

The fifth hash (`$2b$...`) is bcrypt of a strong password — how Flicker *should* store them.

```bash
hashcat -m 3200 -a 0 hashes_<ID>.txt /usr/share/wordlists/rockyou.txt
```

Let it run ~1 minute, then stop (`q`). Record the guesses/second and compare with the MD5 rate.

> [!NOTE]
> **Expected.** MD5: millions/billions of H/s → instant. bcrypt: tens of H/s → a 14-million-word list would take days. The hash **does not crack** in lab time.

### 2.2 Why the defence works

Briefly (3–5 sentences), using your measurements, explain the **salt** (defeats precomputed/rainbow tables) and the **slow function / work factor** (bcrypt/argon2 burn resources, changing the attack economics).

### 2.3 Fix the storage

**In the report:** 3 concrete recommendations for storing passwords in a web app; for at least one give a concrete parameter (e.g. argon2id, bcrypt cost ≥ 12).

### Bonus

- From your measured bcrypt rate, estimate how many years a full attack on a random 10-char `[a-z0-9]` password would take. Show the calculation.
- Add a rule-based attack (`-r /usr/share/hashcat/rules/best64.rule`) on the MD5 hashes and see if it cracks any further variant.

## Submission

- `lab01_<ID>.pdf` — report with both tables, your flag, the speed comparison, the defensive write-up.
- An **[asciinema](https://asciinema.org/) recording** of your work (`asciinema rec lab01.cast`, stop with `Ctrl-D`) — required; also include the `hashcat --show` output in the report.

## Grading

| Item | Points |
|---|:-:|
| Hash identification (table, correct mode) | 2 |
| Cracked weak passwords + personal flag | 3 |
| bcrypt speed comparison (with measurements) | 3 |
| Defensive write-up and recommendations | 2 |
| Bonus | +1 |
