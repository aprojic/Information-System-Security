**Jezik:** [English](README.md) · Hrvatski

<!-- kicker: Vježba 03 · napadni pa obrani · Sigurnost informacijskih sustava -->
# Vježba 03 — Mrežni promet: presretanje i detekcija

*Na nešifriranoj vezi ništa nije privatno. Presretni tuđu prijavu, pa nauči prepoznati napadača u vlastitom prometu.*

`~90 min` · `Kali · Wireshark · nmap` · `razina: početna` · `predaja: Merlin`

> [!WARNING]
> **Etika i opseg.** Snimaj i analiziraj isključivo promet prema meti u svom lab okruženju. Presretanje tuđeg prometa na stvarnim mrežama je kazneno djelo.

**Scenarij.** Flicker je pustio internu aplikaciju na običnom HTTP-u "jer je samo interno". Ti si na istoj mreži: prvo **napadač** koji iz prometa čita prijave, a onda **branitelj** koji u snimci prepoznaje skeniranje i predlaže zaštitu.

## Ishodi učenja

- Snimiti i filtrirati mrežni promet Wiresharkom/tsharkom.
- Iz nešifriranog HTTP prometa izvući prijavne podatke.
- Prepoznati potpis skeniranja portova u snimci.
- Objasniti kako TLS i mrežni nadzor mijenjaju ishod.

## Preduvjeti

- [ ] [Vježba 00](../lab-00-setup/README.hr.md) odrađena — Kali + Docker rade.
- [ ] Alati `wireshark`, `tshark`, `tcpdump`, `nmap`, `curl` (na Kaliju su).
- [ ] Tvoj **matični broj** (koristiš ga kao biljeg u prometu).

## Priprema · ~10 min

Podigni metu i otvori je (`http://localhost:4280`, prijava `admin` / `password`, pa *Create / Reset Database*):

```bash
docker compose up -d
```

Pokreni Wireshark, snimaj na sučelju **`lo`**, filtar prikaza: `http || tcp.flags.syn==1`.

## Dio 1 — Ofenzivno: presretanje · ~40 min

### 1.1 Presretni prijavu
Dok snimaš, prijavi se u DVWA. Nađi POST prijave i pročitaj prijavne podatke u čistom tekstu.

> [!NOTE]
> **Očekivano.** POST s tijelom poput `username=admin&password=password`. Čitljivo jer HTTP nije šifriran.

### 1.2 Tvoj osobni biljeg
Pošalji zahtjev koji nosi tvoj matični broj i pronađi ga u snimci:

```bash
curl "http://localhost:4280/?student=<MB>"
```

**U izvještaj:** screenshot presretnute prijave i paketa u kojem se vidi tvoj matični broj — dokaz da si snimio vlastiti promet.

### 1.3 Skeniranje mete
```bash
sudo nmap -sS -p 1-1000 localhost
```

> [!TIP]
> **Čest problem.** Ne vidiš promet prema `localhost:4280` na `lo`? Provjeri da snimaš baš `lo`. `tcp.flags.syn==1 && tcp.flags.ack==0` izdvoji SYN pakete.

## Dio 2 — Defenzivno: detekcija i zaštita · ~30 min

### 2.1 Prepoznaj skeniranje
Spremi snimku (`cap.pcapng`) i prebroji SYN pakete po izvoru i portu:

```bash
tshark -r cap.pcapng -Y 'tcp.flags.syn==1 && tcp.flags.ack==0' -T fields -e ip.src -e tcp.dstport | sort | uniq -c | sort -rn | head
```

> [!NOTE]
> **Očekivano.** Jedan izvor šalje SYN na stotine portova u kratkom vremenu, bez dovršenih rukovanja — potpis SYN skeniranja.

### 2.2 Zašto obrana radi
Kratko (3–5 rečenica): zašto bi **TLS** učinio prijavu iz 1.1 nečitljivom, i kako bi **IDS/vatrozid** primijetio skeniranje.

### 2.3 Preporuke
**U izvještaj:** 3 konkretne preporuke za Flicker (npr. TLS + HSTS svugdje, segmentacija, nadzor/IDS s pragom na broj SYN-ova).

### Za brze — bonus
- Usporedi `nmap -sS` i `nmap -sT` u snimci na razini paketa.
- Napiši jedno `tshark` pravilo koje javlja izvor s > 100 SYN-ova.

## Predaja

- `vjezba02_<MB>.pdf` — screenshotovi presretanja i paketa s matičnim brojem, izlaz `tshark` brojanja, obrambeni osvrt.
- Snimka `cap.pcapng` (ili isječak).
- **[asciinema](https://asciinema.org/) snimka** rada (`asciinema rec vjezba.cast`, zaustavi s `Ctrl-D`) — obavezna; flag samo pokazuje čiji je rad, snimka je dokaz da je odrađen.

## Bodovanje

| Stavka | Bodovi |
|---|:-:|
| Presretnuta prijava + osobni biljeg u prometu | 3 |
| Skeniranje izvedeno i vidljivo u snimci | 2 |
| Detekcija skeniranja (tshark brojanje) | 3 |
| Obrambeni osvrt i preporuke | 2 |
| Bonus | +1 |
