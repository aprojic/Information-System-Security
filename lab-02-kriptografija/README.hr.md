**Jezik:** [English](README.md) · Hrvatski

<!-- kicker: Vježba 02 · napadni pa obrani · Sigurnost informacijskih sustava -->
# Vježba 02 — Kriptografija: razbijanje slabe kripto

*„Sve enkriptiramo" ne znači ništa ako je enkripcija domaće izrade. Prvo razbiješ Flickerovu, pa izgradiš onu koja drži.*

`~75 min` · `Kali · openssl · python3 · xxd` · `razina: početna` · `predaja: Merlin`

> [!WARNING]
> **Etika i opseg.** Radi se isključivo na datotekama koje dobiješ u ovoj vježbi, u lab okruženju. Napad na enkripciju za koju nemaš ovlaštenje je kazneno djelo.

**Scenarij.** Nakon curenja iz Vježbe 01, **Flicker** je obećao da će „enkriptirati" svoje tajne — ali je programer smislio vlastitu shemu umjesto da koristi provjerenu biblioteku. Večeras si prvo **napadač** koji pokazuje da je domaća kripto bezvrijedna, a onda **inženjer** koji je zamjenjuje autentificiranom enkripcijom koja stvarno drži.

- **Ofenzivno:** iščitavaš strukturu iz bloba šifriranog u ECB načinu i vraćaš tajnu iz Flickerove „XOR enkripcije" napadom s poznatim otvorenim tekstom.
- **Defenzivno:** ponovno enkriptiraš s AES-GCM-om i funkcijom za izvođenje ključa te dokazuješ da odolijeva istim trikovima.

## Ishodi učenja

- Objasniti zašto **kodiranje ≠ enkripcija** i zašto „domaća" kripto propada.
- Pokazati kako **ECB način** otkriva strukturu otvorenog teksta i vratiti podatke iz **XOR-a s ponavljajućim ključem** uz poznati otvoreni tekst.
- Koristiti **autentificiranu enkripciju (AES-GCM)** s ispravnim **KDF-om**, slučajnim nonceom i oznakom integriteta.
- Preporučiti konkretne, ispravne odluke za enkripciju podataka u aplikaciji.

## Preduvjeti

- [ ] [Vježba 00](../lab-00-okruzenje/README.hr.md) odrađena — Kali radi.
- [ ] `openssl`, `xxd`, `python3` (standardno na Kaliju); Python paket `cryptography` instalira se u Pripremi niže.
- [ ] Tvoj **matični broj studenta**.

## Priprema · ~5 min

S Merlina preuzmi mapu vježbe (sadrži `ecb_demo.bin`) i **svoju** datoteku `vault_<MB>.b64` (Flickerova „enkriptirana" tajna). Instaliraj jedan dodatni paket i provjeri alate:

```bash
sudo apt install -y python3-cryptography   # treba za Dio 2
openssl version
python3 -c "import cryptography; print('cryptography', cryptography.__version__)"
```

## Dio 1 — Ofenzivno: razbijanje slabe kripto · ~40 min

### 1.1 ECB otkriva strukturu

Flicker je internu poruku šifrirao AES-om u **ECB načinu**. Nemaš ključ — i neće ti trebati da vidiš problem. Pogledaj šifrat po jedan 16-bajtni blok u retku:

```bash
xxd -c 16 ecb_demo.bin
```

> [!NOTE]
> **Očekivano.** Tri retka po 16 bajtova — i **redak 1 i redak 3 su identični**. ECB svaki blok šifrira neovisno, pa identični blokovi otvorenog teksta postaju identični blokovi šifrata: šifrat odaje da se u poruci ponavlja blok, bez ikakvog ključa.

**U izvještaj:** zalijepi `xxd` izlaz, označi ponovljeni blok i objasni u 2–3 rečenice što napadač iz toga saznaje (to je poznati „ECB pingvin").

### 1.2 Razbij Flickerovu „XOR enkripciju"

Tvoja datoteka `vault_<MB>.b64` je Base64. Dekodiraj je i pogledaj sirove bajtove:

```bash
base64 -d vault_<MB>.b64 | xxd
```

Otvoreni tekst je flag **poznatog oblika** `ASPIRA{sis_crypto_XXXXXX}` (6 heksadekadskih znakova). Flicker ga je „enkriptirao" XOR-anjem s **kratkim ponavljajućim ključem**, pa rezultat Base64-ao. Budući da već znaš prvih 18 bajtova otvorenog teksta (`ASPIRA{sis_crypto_`), ključ možeš vratiti XOR-anjem poznatog otvorenog teksta sa šifratom — **napad s poznatim otvorenim tekstom**:

```python
import base64
ct = base64.b64decode(open("vault_<MB>.b64").read().strip())
known = b"ASPIRA{sis_crypto_"                    # javni prefiks flaga (18 bajtova)
ks = bytes(c ^ p for c, p in zip(ct, known))     # vraćeni keystream za tih 18 bajtova
print(ks.hex())   # pogledaj pažljivo: bajtovi se počinju ponavljati
```

> [!TIP]
> **Nađi period.** Vraćeni bajtovi se ponavljaju — na kojem se offsetu uzorak ponovno pokrene? Taj offset je **duljina ključa**. Uzmi toliko bajtova kao ključ i XOR-aj ga (ponavljajući) preko *cijelog* šifrata da dešifriraš sve — uključujući 6 heksadekadskih znakova koje nisi znao.

**U izvještaj:** vraćeni ključ (hex), **tvoj flag** i naredbe/kôd koje si koristio (asciinema snimka je log procesa).

## Dio 2 — Defenzivno: enkripcija koja drži · ~25 min

### 2.1 Zašto je Flickerova kripto propala

Kratko (3–4 rečenice): navedi barem dva razloga zašto je shema slomljena — npr. **curenje uzorka / bez difuzije** (ECB), **kratak ponavljajući ključ + poznati otvoreni tekst** (XOR) i **bez integriteta** (ništa ne otkriva neovlaštenu izmjenu).

### 2.2 Napravi kako treba: AES-GCM s KDF-om

Enkriptiraj kratku poruku ispravno — **AES-256-GCM**, ključ izveden iz zaporke **PBKDF2-om**, uz **slučajan nonce**:

```python
import os, base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

salt  = os.urandom(16)
key   = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt,
                   iterations=200_000).derive(b"jaka zaporka")
nonce = os.urandom(12)
aes   = AESGCM(key)
ct    = aes.encrypt(nonce, b"Flicker interno: lansiranje 2026-11-01", None)
print("nonce:", base64.b64encode(nonce).decode())
print("ct   :", base64.b64encode(ct).decode())
print("plain:", aes.decrypt(nonce, ct, None).decode())
```

> [!NOTE]
> **Očekivano.** Pokreni dvaput → šifrat je **svaki put drukčiji** (slučajni salt + nonce), za razliku od ECB/XOR-a, i `xxd` ne pokazuje ponavljajuće blokove.

### 2.3 Dokaži integritet

Promijeni jedan bajt šifrata i pokušaj dešifrirati:

```python
bad = bytearray(ct); bad[-1] ^= 1
aes.decrypt(nonce, bytes(bad), None)   # baca cryptography.exceptions.InvalidTag
```

> [!NOTE]
> **Očekivano.** Dešifriranje baca **`InvalidTag`** — GCM autenticira podatke, pa se neovlaštena izmjena otkriva umjesto da se tiho vrati smeće.

### 2.4 Preporuke

**U izvještaj:** 3 konkretna pravila za enkripciju podataka u aplikaciji; za barem jedno navedi konkretan parametar (npr. AES-256-GCM ili ChaCha20-Poly1305; PBKDF2 ≥ 200k iteracija ili scrypt/argon2; jedinstven slučajan nonce po poruci, nikad ponovljen s istim ključem).

### Za brze — bonus

- **Ponavljanje keystreama.** Na temelju napada iz Dijela 1 objasni zašto je enkripcija dviju poruka **istim** XOR ključem (ili ponovljenim GCM nonceom) katastrofa: XOR dvaju šifrata poništava keystream (`c1 ⊕ c2 = p1 ⊕ p2`).
- **TLS u dvije naredbe.** Generiraj self-signed certifikat i pročitaj ga:
  ```bash
  openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 7 -nodes -subj "/CN=flicker.test"
  openssl x509 -in cert.pem -noout -text | head -n 15
  ```
  U 2 rečenice: što certifikat povezuje i zašto self-signed i dalje izazove upozorenje u pregledniku?

## Predaja

- `vjezba02_<MB>.pdf` — izvještaj s `xxd` ECB nalazom, vraćenim ključem i **tvojim flagom**, AES-GCM izlazom, testom integriteta i obrambenim osvrtom.
- **[asciinema](https://asciinema.org/) snimka** rada (`asciinema rec vjezba02.cast`, zaustavi s `Ctrl-D`) — obavezna; flag samo pokazuje čiji je rad, snimka je dokaz da je odrađen.

## Bodovanje

| Stavka | Bodovi |
|---|:-:|
| Nalaz ponavljanja ECB bloka + objašnjenje | 2 |
| Vraćeni XOR ključ + osobni flag | 3 |
| AES-GCM s KDF-om + nonceom (radni izlaz) | 2 |
| Test integriteta (`InvalidTag`) + zašto je slaba kripto pala | 2 |
| Preporuke | 1 |
| Bonus | +1 |
