**Jezik:** [English](README.md) · Hrvatski

<!-- kicker: Vježba 00 · postavljanje · Sigurnost informacijskih sustava -->
# Vježba 00 — Postavi svoj laboratorij

*Izolirani Kali kao napadač, Docker za ranjive mete. Postaviš ga jednom — koristiš cijeli semestar.*

`~45–60 min` · `VirtualBox · Docker` · `jednom na početku` · `preduvjet za Vježbu 01`

U ovom kolegiju izvodiš i napadačke i obrambene tehnike, ali **nikad na stvarnim sustavima**. Zato gradimo zatvoreni laboratorij: Kali Linux kao napadačka mašina i Docker kontejneri kao namjerno ranjive mete. Sve ostaje na tvom računalu i ne dira ništa izvan njega.

## Ishodi učenja

- Pokrenuti Kali Linux u VirtualBoxu i prijaviti se.
- Provjeriti da su sigurnosni alati i wordliste dostupni.
- Instalirati Docker u Kaliju i podići prvu ranjivu metu (OWASP Juice Shop).
- Napraviti snapshot čistog stanja za povratak.

## Preduvjeti

- [ ] Računalo x86-64, ≥ 8 GB RAM-a i ≥ 40 GB slobodnog diska.
- [ ] Virtualizacija (VT-x / AMD-V) omogućena u BIOS/UEFI-u.
- [ ] Internet za prvo preuzimanje (poslije radi offline).
- [ ] Instaliran [VirtualBox](https://www.virtualbox.org/wiki/Downloads).

> [!NOTE]
> Na lab računalima Aspire okruženje je obično već pripremljeno. Ako radiš na svom laptopu, slijedi korake od početka.

## Dio 1 — Kali u VirtualBoxu · ~25 min

1. Na [kali.org/get-kali](https://www.kali.org/get-kali/) → **Virtual Machines** preuzmi gotov VirtualBox image (`.7z`, npr. `kali-linux-2026.2-virtualbox-amd64.7z`).
2. Raspakiraj `.7z`. Dobiješ mapu s datotekama `.vbox` i `.vdi`.
3. U VirtualBoxu: **Machine → Add…** i odaberi `.vbox` datoteku. (Ovo je gotova mašina — *ne* koristi "Import Appliance" ni "New".)
4. Pokreni mašinu i prijavi se — korisnik **kali**, lozinka **kali**.
5. Otvori terminal i provjeri da su alati tu:

```bash
hashcat --version
john --version
nmap --version
```

> [!TIP]
> **Čest problem.** Ako se mašina ne pokreće ili je spora, uključi virtualizaciju (VT-x / AMD-V) u BIOS/UEFI-u. Ako neki alat nedostaje: `sudo apt update && sudo apt install -y kali-linux-default`.

6. **Snapshot čistog stanja** (da se uvijek možeš vratiti): u VirtualBoxu dok mašina radi → **Machine → Take Snapshot…**, nazovi ga `clean`.

## Dio 2 — Docker u Kaliju · ~20 min

Mete (od Vježbe 03 nadalje) vrte se kao Docker kontejneri unutar Kalija.

1. Instaliraj Docker i pokreni servis:

```bash
sudo apt update && sudo apt install -y docker.io
sudo systemctl enable docker --now
sudo usermod -aG docker $USER
```

2. **Odjavi se i ponovno prijavi** (da se primijeni grupa `docker`), pa provjeri:

```bash
docker run hello-world
```

3. Smoke-test prave mete — podigni OWASP Juice Shop, otvori `http://localhost:3000`, pa zaustavi s `Ctrl-C`:

```bash
docker run --rm -p 3000:3000 bkimminich/juice-shop
```

> [!TIP]
> **Čest problem.** `permission denied` na `docker` → nisi se odjavio/prijavio nakon `usermod` (ili pokreni sa `sudo`). Port 3000 zauzet → koristi `-p 3001:3000` i otvori `:3001`.

## Provjera — jesi li spreman za Vježbu 01

- [ ] Kali se pokreće i prijaviš se (`kali`/`kali`).
- [ ] `hashcat --version` i `john --version` ispisuju verziju.
- [ ] `docker run hello-world` prolazi.
- [ ] Juice Shop se otvori na `http://localhost:3000`.
- [ ] Postoji snapshot `clean`.

Vježba 00 se ne boduje, ali je **preduvjet** za Vježbu 01. Ako nešto ne radi, javi na početku termina.
