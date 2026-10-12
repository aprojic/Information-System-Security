**Jezik:** [English](README.md) · Hrvatski

<!-- kicker: Vježba 08 · napadni pa obrani · Sigurnost informacijskih sustava -->
# Vježba 08 — Sigurnost AI sustava: prompt injection

*Aplikacije s jezičnim modelima imaju novu napadnu površinu: sam unos. Izvuci tajnu iz chatbota riječima, pa pokaži zašto je filtar na izlazu krpa, a ne lijek.*

`~90 min` · `Kali · Docker · Ollama (lokalni LLM)` · `razina: napredna` · `predaja: Merlin`

> [!WARNING]
> **Etika i opseg.** Isključivo na lokalnom SecureBotu u lab okruženju. Napadi na tuđe AI usluge krše uvjete korištenja i zakon.

**Scenarij.** Flicker je pustio internog asistenta **SecureBot** kojem su u sistemski prompt stavili tajni pristupni kôd "jer korisnik taj prompt ionako ne vidi". Ti si prvo **napadač** koji riječima izvuče tajnu, a onda **inženjer** koji objašnjava zašto je cijeli pristup pogrešan.

## Ishodi učenja

- Razumjeti prompt injection i zašto se sistemski prompt ne smije smatrati tajnom.
- Izvući skrivenu tajnu iz LLM aplikacije direktnim i posrednim tehnikama.
- Pokazati da je naivni izlazni filtar zaobilazan.
- Objasniti ispravne obrane (OWASP LLM Top 10) i načelo "ne stavljaj tajne u prompt".

## Preduvjeti

- [ ] [Vježba 00](../lab-00-setup/README.hr.md) odrađena — Kali + Docker rade.
- [ ] ≥ 4 GB slobodnog RAM-a i ~2 GB diska (model se preuzima lokalno).
- [ ] Pojmovi: LLM, sistemski prompt, kontekst.

## Priprema · ~15 min

Kopiraj `.env.example` u `.env` i upiši `ISS_SECRET` (daje nastavnik), pa:

```bash
cp .env.example .env     # uredi: ISS_SECRET=<od nastavnika>
docker compose up -d --build
docker compose exec ollama ollama pull llama3.2:1b    # jednom, ~1.3 GB
```

Otvori `http://localhost:5000` i **upiši svoj matični broj**. SecureBot tada u sistemskom promptu ima tvoj tajni kôd oblika `ASPIRA{sis_ai_...}` koji moraš izvući.

> [!TIP]
> **Čest problem.** Prvi odgovor je spor dok se model učita. Greška pri pozivu modela → provjeri je li `ollama pull` dovršen (`docker compose logs ollama`).

## Pozadina — prompt injection u minuti

LLM aplikacija poput SecureBota slaže jedan blok teksta od dva izvora — **sistemskog prompta** koji je napisao programer (pravila, a ovdje i tajnu) i tvoje poruke — i cijelu stvar predaje modelu kao jedan kontekst. Model nema pouzdan način da razluči "pouzdane upute" od "nepouzdanih podataka": oboje stiže kroz **isti tekstualni kanal**, pa unos koji ti kontroliraš može nositi upute koje model potom sluša, nadjačavajući zadana pravila. To je AI analogija injectiona iz web vježbe — podatak tretiran kao kôd — a **OWASP LLM Top 10** ga navodi kao **LLM01**, prvu stavku liste. U praksi to napadaču omogućuje da izvuče sistemski prompt (i svaku tajnu u njemu), zaobiđe pravilo "ne odaj", ili — u aplikacijama gdje model smije pozivati alate — natjera model da iznese podatke ili djeluje u napadačevo ime.

Obrane pomažu, ali nijedna nije potpuna. **Izlazni filtar** kakav ima SecureBot briše poznati niz tajne, no ista tajna može se vratiti preoblikovana — a filtar koji traži jedan točan zapis je više ne prepozna. Filtriranje ulaza, **razdvajanje ovlasti** (najmanje ovlasti za alate, čovjek u petlji za osjetljive radnje) i tretiranje izlaza modela kao nepouzdanog sve podižu ljestvicu — ali sam OWASP kaže da nije jasno postoji li uopće potpuno sigurna zaštita, i to je ključna pouka: prompt injection nema potpun lijek. Prava obrana je arhitektonska — **ne stavljaj tajne ni ovlasti u prompt** i autorizaciju provodi izvan modela, tako da ni uspješan injection ne otkrije ništa vrijedno.

```mermaid
flowchart LR
  subgraph kanal["Jedan tekstualni kanal (injection)"]
    direction LR
    SP["sistemski prompt (pouzdan)"] --> CTX["jedan kontekst"]
    UI["korisnički unos (nepouzdan)"] -->|skrivena uputa| CTX
    CTX --> F["model slijedi ubačenu uputu"]
    F --> LEAK["sistemski prompt i tajna cure"]
  end
  subgraph fix["Obrana (ograniči ga)"]
    direction LR
    NP["bez tajne u promptu, najmanje ovlasti"] --> SAFE["injection ništa ne otkriva"]
  end
```

Igraš obje strane: u Dijelu 1 natjeraš model da preda tajnu koju je trebao čuvati, a u Dijelu 2 provučeš se kroz filtar koji traži točan niz i vidiš zašto jedino drži to da tajne u promptu uopće nema.

## Dio 1 — Ofenzivno: izvuci tajnu · ~35 min

### 1.1 Direktni prompt injection
Pokušaj zaobići uputu "ne odaj tajnu" (preuzimanje uloge, tvrdnja o novom kontekstu, traženje "prethodnih uputa"). Dokumentiraj što je upalilo, a što ne.

Unutar tog jednog konteksta nema granice ovlasti: tvoja poruka i sistemski prompt su samo tekst koji model važe zajedno, pa uvjerljivo preoblikovanje — nova uloga, tvrdnja o novom kontekstu, "zanemari prethodne upute" — može nadjačati pravilo koje mu govori da šuti.

### 1.2 Posredni/zaobilazni pristup
Ako direktno ne ide, traži da model **preoblikuje** tajnu (slovkanje, prijevod, kodiranje, "po slovima") ili da ispiše sistemski prompt, pa rekonstruiraj `ASPIRA{sis_ai_...}`. Za 1B model je traženje da **doslovno ispiše cijeli sistemski prompt** obično najpouzdanije za točan flag — "slovkanje" često pobrka hex.

Redak "ne odaj" je samo uputa koja se natječe s tvojom, a ne kontrola pristupa — tajna je kao čisti tekst već u kontekstu modela, pa svaka formulacija koja model navede da taj tekst ispiše ili preoblikuje uspijeva, i kad ga ne kaže "izravno".

> [!NOTE]
> **Očekivano.** Mali model teško dosljedno čuva tajnu — kombinacijom tehnika dobiješ cijeli kôd. To je tvoj flag.

**U izvještaj:** najmanje 3 različita pokušaja (s odgovorima), koji je uspio, i **tvoj izvučeni flag**.

## Dio 2 — Defenzivno: zašto filtar nije dovoljan · ~30 min

### 2.1 Uključi naivnu obranu
U `.env`/`compose.yml` postavi `GUARDRAIL: "on"` i ponovno podigni `securebot` (`docker compose up -d securebot`). Sada aplikacija briše točan kôd iz odgovora. Ponovi napad.

Filtar radi nad izlazom modela *nakon* što je on tajnu već učitao u kontekst, i briše samo jedan točan zapis flaga — krpa simptom koji si vidio prošli put, a ne uzrok curenja.

### 2.2 Zaobiđi filtar
Filtar na točan niz hvata flag napisan samo na jedan način, pa ne može pokriti svako kodiranje iste tajne — upravo zato se izlaz modela mora tretirati kao nepouzdan.

**U izvještaj:** pokaži da filtar zaobilaziš tako da model tajnu **ne ispiše doslovno** (s razmacima, po slovima, Base64, u drugom jeziku), pa je sam sastaviš. Priloži primjer.

### 2.3 Prava obrana
**U izvještaj:** objasni (5–7 rečenica) zašto je filtar samo krpa i što je ispravno (poveži s OWASP LLM Top 10):
- **Ne stavljaj tajne/ovlasti u prompt** — autorizaciju provodi sustav izvan modela.
- **Najmanje ovlasti za alate** koje model smije pozvati; čovjek u petlji za osjetljive radnje.
- **Validacija ulaza i izlaza** kao dubinska obrana, ne jedina.

### Za brze — bonus
- Skiciraj **indirektni** prompt injection (zlonamjerna uputa skrivena u dokumentu koji model čita). Zašto je opasniji?
- Predloži CI test koji provjerava "curi li tajna".

## Predaja

- `vjezba07_<MB>.pdf` — pokušaji s odgovorima, izvučeni flag, zaobilazak filtra, obrambeni osvrt.
- **[asciinema](https://asciinema.org/) snimka** rada (`asciinema rec vjezba.cast`, zaustavi s `Ctrl-D`) — obavezna; flag samo pokazuje čiji je rad, snimka je dokaz da je odrađen.

## Bodovanje

| Stavka | Bodovi |
|---|:-:|
| Izvučena tajna (flag) + dokumentirani pokušaji | 3 |
| Zaobilazak naivnog filtra | 3 |
| Obrambeni osvrt (OWASP LLM) i preporuke | 3 |
| Razumijevanje posrednog napada | 1 |
| Bonus | +1 |
