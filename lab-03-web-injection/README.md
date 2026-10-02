**Language:** English · [Hrvatski](README.hr.md)

<!-- kicker: Lab 03 · attack then defend · Information System Security -->
# Lab 03 — Web Attacks I: Injection & XSS

*The two oldest web attacks that still work today: dump a database through a search field, and steal a session through a comment box.*

`~90 min` · `Kali · DVWA · browser` · `level: intermediate` · `submit: Merlin`

> [!WARNING]
> **Ethics & scope.** Attack only the DVWA target in your lab environment. The same techniques against someone else's website are a criminal offence.

**Scenario.** Flicker's web app trusts user input. You're first the **attacker** who reads the whole database via SQL injection and steals a session via XSS, then the **developer** who fixes the code so the same input becomes harmless.

## Learning outcomes

- Perform SQL injection and extract data from a database.
- Perform reflected and stored XSS and steal a session cookie.
- Identify the root cause in vulnerable code (input concatenated into a query / unescaped output).
- Fix the vulnerability with a parameterized query and output encoding.

## Prerequisites

- [ ] [Lab 00](../lab-00-okruzenje/README.md) completed — Kali + Docker working.
- [ ] HTTP and HTML basics; the idea of "session / cookie".
- [ ] (Useful) Burp Suite or the browser's DevTools.

## Setup · ~10 min

```bash
docker compose up -d
```

Open `http://localhost:4280`, log in (`admin`/`password`), *Create / Reset Database*, then **DVWA Security → Low**.

## Part 1 — Offensive: injection & XSS · ~45 min

### 1.1 SQL injection — dump the database
In the *SQL Injection* module (`User ID` field), inject a payload that returns every row (an always-true condition, then a `UNION SELECT` for usernames and password hashes).

> [!NOTE]
> **Expected.** Instead of one user, the app prints all of them — including usernames and password hashes from the `users` table.

**In the report:** the payload, the extracted users and hashes. **Crack one hash** (hashcat, as in Lab 01) and attach the result.

### 1.2 XSS — steal a session
In *XSS (Reflected)* inject a script that prints `document.cookie`. Then in *XSS (Stored)* save a payload that sends the cookie to your listener; include your student ID in the payload:

```bash
nc -lvnp 8000     # on Kali, listener for the stolen cookie
```

**In the report:** a reflected XSS printing the cookie (screenshot) and a stored XSS sending it to your `nc` (screenshot with your ID visible).

### 1.3 Raise the bar
Switch **DVWA Security → Medium** and repeat. Explain what the filter blocked and how you bypassed it.

> [!TIP]
> **Common pitfall.** Medium strips some characters/keywords — change case, encoding or structure. No cookie at `nc`? The XSS runs in **your browser**, so it (not the DVWA container) must reach your listener — put your Kali IP, not `localhost`, in the payload.

## Part 2 — Defensive: fix the code · ~30 min

### 2.1 Find the root cause
In DVWA click **View Source** for both modules. Point to the exact line where input is **concatenated into the SQL query** and where it is **printed without encoding** into HTML.

### 2.2 Fix it
**In the report:**
- **SQL:** the fixed query as a **parameterized / prepared statement** (snippet).
- **XSS:** output encoding/escaping of the user input (mention input validation and `Content-Security-Policy`).

### 2.3 Recommendations
3 concrete secure-development recommendations (parameterized queries everywhere, context-aware output encoding, CSP, least privilege for the DB user).

### Bonus
- Automate 1.1 with `sqlmap` (`-u` + the session cookie) and extract the table names.
- Define a minimal CSP header that would stop your stored XSS, and explain why.

## Submission

- `lab03_<ID>.pdf` — payloads, extracted data, XSS screenshot with your ID, fixed code snippets, write-up.
- An **[asciinema](https://asciinema.org/) recording** of your work (`asciinema rec lab.cast`, stop with `Ctrl-D`) — required; the flag only identifies you, this recording is the proof of work.

## Grading

| Item | Points |
|---|:-:|
| SQL injection (extracted data + cracked hash) | 3 |
| XSS (reflected + stored, cookie to listener) | 3 |
| Fixed code (parameterized query + encoding) | 3 |
| Medium level and recommendations | 1 |
| Bonus | +1 |
