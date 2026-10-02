**Jezik:** [English](README.md) · Hrvatski

<!-- kicker: Vježba 04 · napadni pa obrani · Sigurnost informacijskih sustava -->
# Vježba 04 — Web napadi II: autentifikacija i pristup

*Prijavljen si kao ti — ali vidiš li tuđe podatke? Napadi na kontrolu pristupa i tokene često ne traže nijedan exploit, samo znatiželju.*

`~90 min` · `Kali · Juice Shop · DevTools/Burp` · `razina: srednja` · `predaja: Merlin`

> [!WARNING]
> **Etika i opseg.** Isključivo na Juice Shop meti u lab okruženju.

**Scenarij.** Flicker je preuzeo web trgovinu. Provjeri kontrolu pristupa: prvo kao **napadač** dođeš do tuđih podataka i poigraš se tokenom, a onda kao **inženjer** objasniš kako se to provjerava na poslužitelju.

## Ishodi učenja

- Pronaći skrivene funkcije i razumjeti kako SPA razgovara s API-jem.
- Iskoristiti neispravnu kontrolu pristupa (IDOR) za tuđe podatke.
- Analizirati i izmijeniti JWT token sesije.
- Objasniti ispravnu autorizaciju i provjeru tokena na poslužitelju.

## Preduvjeti

- [ ] [Vježba 00](../lab-00-okruzenje/README.hr.md) odrađena — Kali + Docker rade.
- [ ] Preglednikov DevTools (Network i Application) ili Burp Suite.
- [ ] Pojmovi: sesija, token, Base64, JSON.

## Priprema · ~10 min

```bash
docker compose up -d
```

Otvori `http://localhost:3000`. **Registriraj račun s e-mailom koji sadrži tvoj matični broj** (npr. `<MB>@flicker.test`) — tako je sve povezano s tobom.

## Dio 1 — Ofenzivno: pristup i tokeni · ~45 min

### 1.1 Pronađi skrivenu funkciju
Pronađi skrivenu *Score Board* stranicu (Juice Shop prati riješene izazove). Objasni kako si je našao (pregled klijentskog koda / rute).

### 1.2 Neispravna kontrola pristupa (IDOR)
Prijavljen kao svoj korisnik, kroz API dođi do podataka koji nisu tvoji (npr. tuđa košarica) mijenjajući identifikator u zahtjevu.

> [!NOTE]
> **Očekivano.** Poslužitelj vraća tuđe podatke jer provjerava samo da si prijavljen, a ne da je resurs tvoj.

### 1.3 JWT token sesije
U DevToolsu (Application → Storage) nađi JWT. Dekodiraj tri dijela (Base64) i pokaži zaglavlje i `payload`. Objasni polje `alg` i zašto je potpis ključan.

> [!TIP]
> **Čest problem.** JWT nije šifriran — Base64 nije tajna. Svatko ga može *pročitati*; sigurnost je u **potpisu**. Ne pokušavaj probiti kriptografiju; pokaži razumijevanje strukture i rizika slabog/izostavljenog potpisa.

**U izvještaj:** kako si našao Score Board, dokaz IDOR-a (zahtjev + tuđi podaci), dekodirani JWT s objašnjenjem polja, i screenshot Score Boarda s tvojim računom.

## Dio 2 — Defenzivno: ispravna autorizacija · ~30 min

### 2.1 Zašto je prošlo
Objasni (3–5 rečenica) zašto IDOR radi (autorizacija se oslanja na klijentski identifikator) i ispravan pristup: **poslužitelj provjerava smije li prijavljeni korisnik baš taj resurs**.

### 2.2 Popravak
**U izvještaj:**
- **Pristup:** provjera vlasništva resursa na poslužitelju (npr. `resource.owner == current_user`); ne vjeruj ID-u iz zahtjeva.
- **Token:** ispravne provjere JWT-a (potpis, `alg` allowlist, istek, izdavatelj) i zašto tajna mora biti jaka.

### 2.3 Preporuke
3 konkretne preporuke (autorizacija po svakom zahtjevu, "deny by default", kratki rok tokena + rotacija, nikad osjetljivi podaci u tokenu).

### Za brze — bonus
- Riješi još jedan Score Board izazov i opiši ranjivost.
- Pokaži kako bi se promjena `alg` na "none" zaustavila ispravnom allowlistom.

## Predaja

- `vjezba04_<MB>.pdf` — nalazi, dekodirani JWT, screenshot Score Boarda s tvojim računom, obrambeni osvrt.
- **[asciinema](https://asciinema.org/) snimka** rada (`asciinema rec vjezba.cast`, zaustavi s `Ctrl-D`) — obavezna; flag samo pokazuje čiji je rad, snimka je dokaz da je odrađen.

## Bodovanje

| Stavka | Bodovi |
|---|:-:|
| Skrivena funkcija + razumijevanje API-ja | 2 |
| IDOR do tuđih podataka | 3 |
| Analiza JWT tokena | 2 |
| Obrambeni osvrt (autorizacija + token) i preporuke | 2 |
| Bonus | +1 |
