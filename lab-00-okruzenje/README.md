**Language:** English · [Hrvatski](README.hr.md)

<!-- kicker: Lab 00 · setup · Information System Security -->
# Lab 00 — Set up your lab

*An isolated Kali as the attacker, Docker for the vulnerable targets. Set it up once — use it all semester.*

`~45–60 min` · `VirtualBox · Docker` · `once at the start` · `prerequisite for Lab 01`

In this course you run both offensive and defensive techniques, but **never on real systems**. So you build a closed lab: Kali Linux as the attacker machine and Docker containers as deliberately vulnerable targets. Everything stays on your computer and touches nothing outside it.

## Learning outcomes

- Run Kali Linux in VirtualBox and log in.
- Verify that the security tools and wordlists are available.
- Install Docker inside Kali and bring up your first vulnerable target (OWASP Juice Shop).
- Take a clean-state snapshot to roll back to.

## Prerequisites

- [ ] An x86-64 computer with ≥ 8 GB RAM and ≥ 40 GB free disk.
- [ ] Virtualization (VT-x / AMD-V) enabled in BIOS/UEFI.
- [ ] Internet for the first download (works offline afterwards).
- [ ] [VirtualBox](https://www.virtualbox.org/wiki/Downloads) installed.

> [!NOTE]
> On the Aspira lab machines the environment is usually prepared already. If you work on your own laptop, follow the steps from the start.

## Part 1 — Kali in VirtualBox · ~25 min

1. At [kali.org/get-kali](https://www.kali.org/get-kali/) → **Virtual Machines**, download the prebuilt VirtualBox image (`.7z`, e.g. `kali-linux-2026.2-virtualbox-amd64.7z`).
2. Extract the `.7z`. You get a folder with a `.vbox` and a `.vdi` file.
3. In VirtualBox: **Machine → Add…** and select the `.vbox` file. (This is a ready-made machine — do *not* use "Import Appliance" or "New".)
4. Start the machine and log in — user **kali**, password **kali**.
5. Open a terminal and check the tools are present:

```bash
hashcat --version
john --version
nmap --version
```

> [!TIP]
> **Common pitfall.** If the machine won't start or is slow, enable virtualization (VT-x / AMD-V) in BIOS/UEFI. If a tool is missing, pull the default set: `sudo apt update && sudo apt install -y kali-linux-default`.

6. **Clean-state snapshot** (so you can always roll back): in VirtualBox, with the machine running → **Machine → Take Snapshot…**, name it `clean`.

## Part 2 — Docker inside Kali · ~20 min

Targets (from Lab 03 onward) run as Docker containers inside Kali.

1. Install Docker and start the service:

```bash
sudo apt update && sudo apt install -y docker.io
sudo systemctl enable docker --now
sudo usermod -aG docker $USER
```

2. **Log out and back in** (to apply the `docker` group), then check:

```bash
docker run hello-world
```

3. Smoke-test a real target — bring up OWASP Juice Shop, open `http://localhost:3000`, then stop it with `Ctrl-C`:

```bash
docker run --rm -p 3000:3000 bkimminich/juice-shop
```

> [!TIP]
> **Common pitfall.** `permission denied` on `docker` → you didn't log out/in after `usermod` (or run with `sudo`). Port 3000 busy → use `-p 3001:3000` and open `:3001`.

## Stay up to date (optional, 1 min)

On the [course repository](https://github.com/aprojic/Information-System-Security), top right:

1. Click **⭐ Star** — a bookmark, so the labs are always under *Your stars* on your profile.
2. Click **Watch → Custom**, tick **Releases**, then **Apply** — GitHub emails you when a new lab is published. (A star alone sends no notifications.)

## Check — are you ready for Lab 01

- [ ] Kali boots and you log in (`kali`/`kali`).
- [ ] `hashcat --version` and `john --version` print a version.
- [ ] `docker run hello-world` passes.
- [ ] Juice Shop opens at `http://localhost:3000`.
- [ ] A `clean` snapshot exists.
- [ ] (Optional) You starred the repo and watch its releases.

Lab 00 is not graded, but it is a **prerequisite** for Lab 01. If something doesn't work, tell the instructor at the start of the session.
