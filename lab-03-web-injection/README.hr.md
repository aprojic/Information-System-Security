**Jezik:** [English](README.md) · Hrvatski

<!-- kicker: Vježba 03 · napadni pa obrani · Sigurnost informacijskih sustava -->
# Vježba 03 — Web napadi I: injection i XSS

*Dva najstarija web napada koja i danas rade: izvući bazu kroz polje za pretragu i oteti sesiju kroz polje za komentar.*

`~90 min` · `Kali · DVWA · preglednik` · `razina: srednja` · `predaja: Merlin`

> [!WARNING]
> **Etika i opseg.** Napadaj isključivo DVWA metu u svom lab okruženju. Isti postupci na tuđem webu su kazneno djelo.

**Scenarij.** Flickerova web aplikacija vjeruje korisničkom unosu. Ti si prvo **napadač** koji kroz SQL injection čita cijelu bazu i kroz XSS krade sesiju, a onda **programer** koji popravlja kod tako da isti unos postane bezopasan.

## Ishodi učenja

- Izvesti SQL injection i izvući podatke iz baze.
- Izvesti reflektirani i pohranjeni XSS te oteti kolačić sesije.
- U ranjivom kodu prepoznati uzrok (spajanje unosa u upit / neizlazno ispisivanje).
- Popraviti ranjivost parametriziranim upitom i izlaznim kodiranjem.

## Preduvjeti

- [ ] [Vježba 00](../lab-00-okruzenje/README.hr.md) odrađena — Kali + Docker rade.
- [ ] Osnove HTTP-a i HTML-a; pojam "sesija / kolačić".
- [ ] (Korisno) Burp Suite ili preglednikov DevTools.

## Priprema · ~10 min

```bash
docker compose up -d
```

Otvori `http://localhost:4280`, prijavi se (`admin`/`password`), *Create / Reset Database*, pa **DVWA Security → Low**.

## Dio 1 — Ofenzivno: injection i XSS · ~45 min

### 1.1 SQL injection — izvuci bazu
U *SQL Injection* modulu (polje `User ID`) ubaci payload koji vraća sve retke (uvjet koji je uvijek istinit, pa `UNION SELECT` za korisnička imena i hasheve lozinki).

> [!NOTE]
> **Očekivano.** Umjesto jednog korisnika, aplikacija ispiše sve — uključujući korisnička imena i hasheve iz tablice `users`.

**U izvještaj:** payload, popis izvučenih korisnika i hasheva. **Razbij jedan hash** (hashcat, kao u Vježbi 01) i priloži rezultat.

### 1.2 XSS — otmi sesiju
U *XSS (Reflected)* ubaci skriptu koja ispisuje `document.cookie`. Zatim u *XSS (Stored)* spremi payload koji kolačić šalje na tvoj slušatelj; uključi i svoj matični broj u payload:

```bash
nc -lvnp 8000     # na Kaliju, slušatelj za ukradeni kolačić
```

**U izvještaj:** reflektirani XSS koji ispiše kolačić (screenshot) i pohranjeni XSS koji ga pošalje na tvoj `nc` (screenshot s vidljivim matičnim brojem).

### 1.3 Podigni razinu
Prebaci **DVWA Security → Medium** i ponovi. Objasni što je filtar blokirao i kako si ga zaobišao.

> [!TIP]
> **Čest problem.** Medium čisti neke znakove/ključne riječi — promijeni velika/mala slova, kodiranje ili strukturu. Nema kolačića na `nc`? Provjeri da meta doseže tvoj Kali IP/port.

## Dio 2 — Defenzivno: popravi kod · ~30 min

### 2.1 Pronađi uzrok
U DVWA-u klikni **View Source** za oba modula. Pokaži točan redak gdje se unos **spaja u SQL upit** i gdje se **ispisuje bez kodiranja** u HTML.

### 2.2 Popravi
**U izvještaj:**
- **SQL:** ispravljeni upit kao **parametrizirani / prepared statement** (isječak).
- **XSS:** izlazno kodiranje/escaping unosa (spomeni ulaznu validaciju i `Content-Security-Policy`).

### 2.3 Preporuke
3 konkretne preporuke za siguran razvoj (parametrizirani upiti svugdje, kodiranje po kontekstu izlaza, CSP, najmanje ovlasti za DB korisnika).

### Za brze — bonus
- Automatiziraj 1.1 sa `sqlmap` (`-u` + kolačić sesije) i izvuci imena tablica.
- Postavi minimalni CSP header koji bi zaustavio tvoj pohranjeni XSS i obrazloži zašto.

## Predaja

- `vjezba03_<MB>.pdf` — payloadi, izvučeni podaci, screenshot XSS-a s matičnim brojem, ispravljeni isječci koda, osvrt.

## Bodovanje

| Stavka | Bodovi |
|---|:-:|
| SQL injection (izvučeni podaci + razbijen hash) | 3 |
| XSS (reflektirani + pohranjeni, kolačić na slušatelj) | 3 |
| Ispravljeni kod (parametrizirani upit + kodiranje) | 3 |
| Medium razina i preporuke | 1 |
| Bonus | +1 |
