**Jezik:** [English](README.md) · Hrvatski

<!-- kicker: Vježba 06 · napadni pa obrani · Sigurnost informacijskih sustava -->
# Vježba 06 — Eksploatacija i eskalacija privilegija

*Od slabe lozinke do roota u tri koraka. Rijetko je u pitanju genijalni exploit — češće slaba lozinka i jedna loša konfiguracija.*

`~90 min` · `Kali · nmap · hydra · SSH` · `razina: srednja` · `predaja: Merlin`

> [!WARNING]
> **Etika i opseg.** Isključivo na ovoj namjerno ranjivoj meti u lab okruženju. Dictionary napadi i eskalacija na stvarnim sustavima bez pisanog dopuštenja su kazneno djelo.

**Scenarij.** Flicker ima zaboravljeni poslužitelj na mreži. Ti si prvo **napadač** koji probija slabu lozinku, ulazi i postaje root, a onda **administrator** koji zatvara svaki korak tog lanca.

## Ishodi učenja

- Otkriti servis i izvesti dictionary napad na prijavu.
- Dobiti pristup i enumerirati mogućnosti eskalacije privilegija.
- Iskoristiti sudo pogrešku u konfiguraciji za root i pročitati zaštićeni flag.
- Objasniti kako se svaki korak lanca sprječava.

## Preduvjeti

- [ ] [Vježba 00](../lab-00-okruzenje/README.hr.md) odrađena — Kali + Docker rade.
- [ ] Alati `nmap`, `hydra`, `ssh` (na Kaliju su).
- [ ] Osnove Linuxa i pojam SUID/sudo.

## Priprema · ~10 min

Kopiraj `.env.example` u `.env` te upiši **svoj matični broj** i `ISS_SECRET` (daje nastavnik), pa sagradi metu:

```bash
cp .env.example .env     # uredi: MB=<tvoj matični broj>, ISS_SECRET=<od nastavnika>
docker compose up -d --build
```

SSH meta sluša na `localhost:2222`. Priložena je mala lista lozinki `passwords.txt`. Flag u `/root/flag.txt` izveden je iz tvog matičnog broja — zato je tvoj.

## Dio 1 — Ofenzivno: od lozinke do roota · ~45 min

### 1.1 Otkrij servis
```bash
nmap -sV -p 2222 localhost
```
> [!NOTE]
> **Očekivano.** Port `2222` otvoren, servis OpenSSH.

### 1.2 Dictionary napad na prijavu
Korisnik je `flicker`. Probij lozinku ciljanom listom:
```bash
hydra -l flicker -P passwords.txt -t 4 -s 2222 ssh://localhost
```
> [!TIP]
> **Čest problem.** Napad preko mreže je spor — zato koristiš malu, ciljanu listu, ne cijeli rockyou. Ako hydra javi više pogodaka, provjeri ručno sa `ssh`.

### 1.3 Uđi i enumeriraj
```bash
ssh flicker@localhost -p 2222
sudo -l
```
> [!NOTE]
> **Očekivano.** `sudo -l` pokazuje da `flicker` smije pokrenuti jedan program kao root bez lozinke (`NOPASSWD`).

### 1.4 Eskalacija do roota
Taj program (vidi [GTFOBins](https://gtfobins.github.io/)) može pokrenuti ljusku. Iskoristi ga da dobiješ root ljusku i pročitaš `/root/flag.txt`.

**U izvještaj:** pronađena lozinka, izlaz `sudo -l`, naredba kojom si dobio root, sadržaj `/root/flag.txt`, i `id` koji pokazuje `uid=0(root)`.

## Dio 2 — Defenzivno: zatvori lanac · ~30 min

### 2.1 Zašto je svaki korak prošao
Za svaki korak (slaba lozinka → SSH → sudo misconfig) objasni u jednoj rečenici zašto je uspio.

### 2.2 Popravak
**U izvještaj:**
- **Prijava:** SSH ključevi umjesto lozinki (ili jake lozinke + `fail2ban` + rate-limiting).
- **Ovlasti:** ukloni `NOPASSWD` i ne dopuštaj preko `sudo` programe koji pokreću ljusku; najmanje ovlasti.
- **Nadzor:** logiranje `sudo`/prijava i upozorenja.

### 2.3 Preporuke
3 konkretne preporuke za Flicker, poredane po učinku.

### Za brze — bonus
- Izvedi isti ulazak preko Metasploita (`ssh_login` modul) i usporedi s hydrom.
- Napiši minimalni ispravan `sudoers` redak koji i dalje daje `flickeru` potrebnu funkciju, ali bez puta do roota.

## Predaja

- `vjezba05_<MB>.pdf` — cijeli lanac s izlazima, `/root/flag.txt`, `id` kao root, obrambeni osvrt.
- **[asciinema](https://asciinema.org/) snimka** rada (`asciinema rec vjezba.cast`, zaustavi s `Ctrl-D`) — obavezna; flag samo pokazuje čiji je rad, snimka je dokaz da je odrađen.

## Bodovanje

| Stavka | Bodovi |
|---|:-:|
| Otkrivanje servisa + probijena lozinka | 3 |
| Eskalacija do roota + pročitan flag | 3 |
| Obrana svakog koraka lanca | 3 |
| Preporuke po učinku | 1 |
| Bonus | +1 |
