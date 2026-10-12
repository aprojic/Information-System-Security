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

## Pozadina — mrežni promet u minuti

Mreža je zajednička infrastruktura: tvoji paketi putuju kroz switcheve, routere i pristupne točke do odredišta, a na zajedničkoj ili otvorenoj vezi svatko tko je na tom putu može snimiti svaki paket koji prođe. Obični **HTTP** sve nosi kao čitljiv tekst — uključujući korisničko ime i lozinku iz obrasca za prijavu — pa pasivni slušatelj tvoje podatke pročita ravno sa žice, bez ikakvog razbijanja ili trika. **TLS** (ono `S` u HTTPS-u) iste bajtove zamota u enkripciju, pa sniffer vidi samo šifrat i prijava prestaje biti čitljiva. Nije teoretski: poznati Firefox dodatak **Firesheep** to je pretvorio u salonski trik — na otvorenom Wi-Fiju pokupio bi session cookieje ljudi na istoj mreži i omogućio da se prijaviš kao oni, jer su stranice šifrirale samo korak prijave pa se za ostatak sesije vraćale na obični HTTP. Rješenje je bilo cijelu sesiju držati na HTTPS-u, što je danas norma.

Kad već slušaš mrežu, u njoj vidiš i napadača. TCP veza se otvara trosmjernim **rukovanjem** (handshake) — SYN → SYN-ACK → ACK — a skener portova to zloupotrebljava: odapne SYN na stotine portova i rukovanje nikad ne dovrši, pa se snimka napuni samim SYN paketima bez ijedne dovršene veze, **potpisom** koji branitelj jednostavno prebroji. Cijela vježba vrti se oko jedne poluge: enkripcija odlučuje je li tvoja prijava uopće čitljiva, a nadzor odlučuje hoće li se skeniranje ikad primijetiti.

```mermaid
flowchart LR
  subgraph presretni["Presretni prijavu (napadač na putu)"]
    direction LR
    L["paket prijave"] -->|obični HTTP| R["podaci čitljivi"]
    L -->|HTTPS / TLS| C["samo šifrat"]
  end
  subgraph detekcija["Otkrij skeniranje (branitelj sluša)"]
    direction LR
    S["skener portova"] -->|mnogo SYN-ova| H{"rukovanje dovršeno?"}
    H -->|ne| D["potpis skeniranja"]
  end
```

Igraš obje uloge: u Dijelu 1 pročitaš prijavu koju je obični HTTP ostavio na vidjelu, a u Dijelu 2 prebrojiš osamljene SYN-ove koji odaju skeniranje.

## Dio 1 — Ofenzivno: presretanje · ~40 min

### 1.1 Presretni prijavu
Dok snimaš, prijavi se u DVWA. Nađi POST prijave i pročitaj prijavne podatke u čistom tekstu.

To je cijeli problem u jednom paketu. HTTP stavlja polja obrasca ravno u tijelo zahtjeva, pa je lozinka izložena čim napusti preglednik — nema se što dešifrirati ni razbijati, jer nikad nije ni bila zaštićena.

> [!NOTE]
> **Očekivano.** POST s tijelom poput `username=admin&password=password`. Čitljivo jer HTTP nije šifriran.

### 1.2 Tvoj osobni biljeg
Pošalji zahtjev koji nosi tvoj matični broj i pronađi ga u snimci:

```bash
curl "http://localhost:4280/?student=<MB>"
```

Matični broj u query stringu daje ti jedinstveni token za pretragu snimke, pa možeš dokazati koji su od mnogih `lo` paketa baš tvoji. Usput pokazuje i da cijeli URL putuje u čistom tekstu — ne samo tijela obrazaca, nego i query stringovi, zaglavlja i cookieji.

**U izvještaj:** screenshot presretnute prijave i paketa u kojem se vidi tvoj matični broj — dokaz da si snimio vlastiti promet.

### 1.3 Skeniranje mete
```bash
sudo nmap -sS -p 1-1000 localhost
```

`-sS` je SYN (half-open) skeniranje: nmap pošalje SYN na svaki port i iz odgovora razluči otvoreno od zatvorenog, ali nikad ne pošalje završni ACK da dovrši vezu. To ga čini brzim i tišim prema osnovnom logiranju — ali ostavlja točno onaj otisak koji loviš u Dijelu 2: rafal SYN-ova bez ijednog dovršenog rukovanja.

> [!TIP]
> **Čest problem.** Ne vidiš promet prema `localhost:4280` na `lo`? Provjeri da snimaš baš `lo`. `tcp.flags.syn==1 && tcp.flags.ack==0` izdvoji SYN pakete.

## Dio 2 — Defenzivno: detekcija i zaštita · ~30 min

### 2.1 Prepoznaj skeniranje
Spremi snimku (`cap.pcapng`) i prebroji SYN pakete po izvoru i portu:

```bash
tshark -r cap.pcapng -Y 'tcp.flags.syn==1 && tcp.flags.ack==0' -T fields -e ip.src -e tcp.dstport | sort | uniq -c | sort -rn | head
```

Filtar zadržava samo pakete sa SYN zastavicom i bez ACK-a — prvi paket svake veze — pa ih prebroji po izvoru i odredišnom portu. Normalan klijent otvori šačicu veza; skener se istakne kao jedan izvor koji dira stotine portova, i zato ga sortiranje po broju odmah izbaci na vrh.

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
