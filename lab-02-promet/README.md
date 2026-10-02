<!-- kicker: Lab 02 · attack then defend · Information System Security -->
# Lab 02 — Network Traffic: Interception & Detection

*On an unencrypted connection nothing is private. Intercept someone's login, then learn to spot the attacker in your own traffic.*

`~90 min` · `Kali · Wireshark · nmap` · `level: intro` · `submit: Merlin`

> [!WARNING]
> **Ethics & scope.** Capture and analyse only traffic to the target in your lab environment. Intercepting other people's traffic on real networks is a criminal offence.

**Scenario.** Flicker shipped an internal app over plain HTTP "because it's internal only". You're on the same network: first the **attacker** who reads logins off the wire, then the **defender** who spots a scan and proposes protection.

## Learning outcomes

- Capture and filter network traffic with Wireshark/tshark.
- Extract login credentials from unencrypted HTTP traffic.
- Recognise the signature of a port scan in a capture.
- Explain how TLS and network monitoring change the outcome.

## Prerequisites

- [ ] [Lab 00](../lab-00-okruzenje/README.md) completed — Kali + Docker working.
- [ ] Tools `wireshark`, `tshark`, `tcpdump`, `nmap`, `curl` (present on Kali).
- [ ] Your **student ID** (you'll use it as a marker in the traffic).

## Setup · ~10 min

Bring up the target and open it (`http://localhost:4280`, login `admin` / `password`, then *Create / Reset Database*):

```bash
docker compose up -d
```

Start Wireshark capturing on interface **`lo`**, display filter: `http || tcp.flags.syn==1`.

## Part 1 — Offensive: interception · ~40 min

### 1.1 Intercept the login
While capturing, log in to DVWA. Find the login POST and read the credentials in cleartext.

> [!NOTE]
> **Expected.** A POST with a body like `username=admin&password=password`. Readable because HTTP is not encrypted.

### 1.2 Your personal marker
Send a request carrying your student ID and find it in the capture:

```bash
curl "http://localhost:4280/?student=<ID>"
```

**In the report:** a screenshot of the intercepted login and of the packet showing your ID — proof you captured your own traffic.

### 1.3 Scan the target
```bash
nmap -sS -p 1-1000 localhost
```

> [!TIP]
> **Common pitfall.** No traffic to `localhost:4280` on `lo`? Make sure you capture `lo`. `tcp.flags.syn==1 && tcp.flags.ack==0` isolates SYN packets.

## Part 2 — Defensive: detection & protection · ~30 min

### 2.1 Spot the scan
Save the capture (`cap.pcapng`) and count SYNs per source and port:

```bash
tshark -r cap.pcapng -Y 'tcp.flags.syn==1 && tcp.flags.ack==0' -T fields -e ip.src -e tcp.dstport | sort | uniq -c | sort -rn | head
```

> [!NOTE]
> **Expected.** One source sends SYNs to hundreds of ports in a short time, with no completed handshakes — the signature of a SYN scan.

### 2.2 Why the defence works
Briefly (3–5 sentences): why **TLS** would make the login from 1.1 unreadable, and how an **IDS/firewall** would notice the scan.

### 2.3 Recommendations
**In the report:** 3 concrete recommendations for Flicker (e.g. TLS + HSTS everywhere, segmentation, monitoring/IDS with a SYN-count threshold).

### Bonus
- Compare `nmap -sS` and `nmap -sT` at the packet level in the capture.
- Write one `tshark` rule that flags a source with > 100 SYNs.

## Submission

- `lab02_<ID>.pdf` — screenshots of the interception and the ID packet, the `tshark` count output, the defensive write-up.
- The capture `cap.pcapng` (or an excerpt).

## Grading

| Item | Points |
|---|:-:|
| Intercepted login + personal ID in traffic | 3 |
| Scan performed and visible in the capture | 2 |
| Scan detection (tshark count) | 3 |
| Defensive write-up and recommendations | 2 |
| Bonus | +1 |
