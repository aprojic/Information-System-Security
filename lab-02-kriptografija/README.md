**Language:** English · [Hrvatski](README.hr.md)

<!-- kicker: Lab 02 · attack then defend · Information System Security -->
# Lab 02 — Cryptography: Breaking Weak Crypto

*"We encrypt everything" means nothing if the encryption is homemade. First you break Flicker's, then you build one that holds.*

`~75 min` · `Kali · openssl · python3 · xxd` · `level: intro` · `submit: Merlin`

> [!WARNING]
> **Ethics & scope.** Work only on the files you are given in this lab, inside the lab environment. Attacking encryption you are not authorised to is a criminal offence.

**Scenario.** After the breach in Lab 01, **Flicker** promised to "encrypt" its secrets — but a developer rolled their own scheme instead of using a vetted library. You are first the **attacker** who shows the homemade crypto is worthless, then the **engineer** who replaces it with authenticated encryption that actually holds.

- **Offensive:** read structure out of an ECB-encrypted blob, and recover a secret from Flicker's "XOR encryption" with a known-plaintext attack.
- **Defensive:** re-encrypt with AES-GCM and a key-derivation function, and prove it resists the same tricks.

## Learning outcomes

- Explain why **encoding ≠ encryption** and why "rolling your own" crypto fails.
- Show how **ECB mode** leaks plaintext structure, and recover data from **repeating-key XOR** with known plaintext.
- Use **authenticated encryption (AES-GCM)** with a proper **KDF**, a random nonce, and an integrity tag.
- Recommend concrete, correct choices for encrypting data in an application.

## Prerequisites

- [ ] [Lab 00](../lab-00-okruzenje/README.md) completed — Kali working.
- [ ] `openssl`, `xxd`, `python3` (standard on Kali); the Python `cryptography` package is installed in Setup below.
- [ ] Your **student ID (matični broj)**.

## Setup · ~5 min

From Merlin, download the lab folder (it contains `ecb_demo.bin`) and **your** file `vault_<ID>.b64` (Flicker's "encrypted" secret). Install the one extra package and check your tools:

```bash
sudo apt install -y python3-cryptography   # needed for Part 2
openssl version
python3 -c "import cryptography; print('cryptography', cryptography.__version__)"
```

## Part 1 — Offensive: breaking weak crypto · ~40 min

### 1.1 ECB leaks structure

Flicker encrypted an internal note with AES in **ECB mode**. You don't have the key — and you won't need it to see the problem. Look at the ciphertext one 16-byte block per row:

```bash
xxd -c 16 ecb_demo.bin
```

> [!NOTE]
> **Expected.** Three rows of 16 bytes — and **row 1 and row 3 are identical**. ECB encrypts each block independently, so identical plaintext blocks become identical ciphertext blocks: the ciphertext leaks that the note repeats a block, without any key.

**In the report:** paste the `xxd` output, point out the repeated block, and explain in 2–3 sentences what an attacker learns from it (this is the classic "ECB penguin").

### 1.2 Break Flicker's "XOR encryption"

Your file `vault_<ID>.b64` is Base64. Decode it and look at the raw bytes:

```bash
base64 -d vault_<ID>.b64 | xxd
```

The plaintext is a flag of the **known form** `ASPIRA{sis_crypto_XXXXXX}` (6 hex chars). Flicker "encrypted" it by XOR-ing with a **short repeating key**, then Base64-ing the result. Because you already know the first 18 bytes of plaintext (`ASPIRA{sis_crypto_`), you can recover the key by XOR-ing known plaintext against the ciphertext — a **known-plaintext attack**:

```python
import base64
ct = base64.b64decode(open("vault_<ID>.b64").read().strip())
known = b"ASPIRA{sis_crypto_"                    # the public flag prefix (18 bytes)
ks = bytes(c ^ p for c, p in zip(ct, known))     # recovered keystream for those 18 bytes
print(ks.hex())   # look closely: the bytes start repeating
```

> [!TIP]
> **Find the period.** The recovered bytes repeat — at what offset does the pattern restart? That offset is your **key length**. Take that many bytes as the key and XOR it (repeating) over the *whole* ciphertext to decrypt everything — including the 6 hex characters you didn't know.

**In the report:** the recovered key (hex), **your flag**, and the commands/code you used (your asciinema recording is the process log).

## Part 2 — Defensive: encryption that holds · ~25 min

### 2.1 Why Flicker's crypto failed

Briefly (3–4 sentences): give at least two reasons the scheme is broken — e.g. **pattern leakage / no diffusion** (ECB), **short repeating key + known plaintext** (XOR), and **no integrity** (nothing detects tampering).

### 2.2 Do it right: AES-GCM with a KDF

Encrypt a short message properly with **AES-256-GCM**, deriving the key from a passphrase with **PBKDF2** and using a **random nonce**:

```python
import os, base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

salt  = os.urandom(16)
key   = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt,
                   iterations=200_000).derive(b"a strong passphrase")
nonce = os.urandom(12)
aes   = AESGCM(key)
ct    = aes.encrypt(nonce, b"Flicker internal: launch 2026-11-01", None)
print("nonce:", base64.b64encode(nonce).decode())
print("ct   :", base64.b64encode(ct).decode())
print("plain:", aes.decrypt(nonce, ct, None).decode())
```

> [!NOTE]
> **Expected.** Run it twice → the ciphertext is **different each time** (random salt + nonce), unlike ECB/XOR, and `xxd` shows no repeating blocks.

### 2.3 Prove integrity

Flip one byte of the ciphertext and try to decrypt:

```python
bad = bytearray(ct); bad[-1] ^= 1
aes.decrypt(nonce, bytes(bad), None)   # raises cryptography.exceptions.InvalidTag
```

> [!NOTE]
> **Expected.** Decryption raises **`InvalidTag`** — GCM authenticates the data, so tampering is detected instead of silently returning garbage.

### 2.4 Recommendations

**In the report:** 3 concrete rules for encrypting data in an application; for at least one give a concrete parameter (e.g. AES-256-GCM or ChaCha20-Poly1305; PBKDF2 ≥ 200k iterations, or scrypt/argon2; a unique random nonce per message, never reused with the same key).

### Bonus

- **Keystream reuse.** Using your Part 1 attack, explain why encrypting two messages with the **same** XOR key (or reusing a GCM nonce) is catastrophic: XOR-ing the two ciphertexts cancels the keystream (`c1 ⊕ c2 = p1 ⊕ p2`).
- **TLS in two commands.** Generate a self-signed certificate and read it back:
  ```bash
  openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 7 -nodes -subj "/CN=flicker.test"
  openssl x509 -in cert.pem -noout -text | head -n 15
  ```
  In 2 sentences: what does the certificate bind together, and why does a self-signed one still trigger a browser warning?

## Submission

- `lab02_<ID>.pdf` — report with the `xxd` ECB finding, the recovered key and **your flag**, the AES-GCM output, the integrity test, and the defensive write-up.
- An **[asciinema](https://asciinema.org/) recording** of your work (`asciinema rec lab02.cast`, stop with `Ctrl-D`) — required; the flag only identifies you, this recording is the proof of work.

## Grading

| Item | Points |
|---|:-:|
| ECB block-repetition finding + explanation | 2 |
| Recovered XOR key + personal flag | 3 |
| AES-GCM with KDF + nonce (working output) | 2 |
| Integrity test (`InvalidTag`) + why weak crypto failed | 2 |
| Recommendations | 1 |
| Bonus | +1 |
