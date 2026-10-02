**Language:** English · [Hrvatski](README.hr.md)

<!-- kicker: Lab 04 · attack then defend · Information System Security -->
# Lab 04 — Web Attacks II: Authentication & Access

*You're logged in as you — but can you see other people's data? Attacks on access control and tokens often need no exploit, just curiosity.*

`~90 min` · `Kali · Juice Shop · DevTools/Burp` · `level: intermediate` · `submit: Merlin`

> [!WARNING]
> **Ethics & scope.** Only against the Juice Shop target in the lab environment.

**Scenario.** Flicker acquired a web shop. Test its access control: first as the **attacker** who reaches other users' data and plays with the session token, then as the **engineer** who explains how this is checked on the server.

## Learning outcomes

- Find hidden functionality and understand how a SPA talks to its API.
- Exploit broken access control (IDOR) to reach other users' data.
- Analyse and modify a JWT session token.
- Explain correct authorization and token verification on the server.

## Prerequisites

- [ ] [Lab 00](../lab-00-okruzenje/README.md) completed — Kali + Docker working.
- [ ] Browser DevTools (Network and Application tabs) or Burp Suite.
- [ ] Concepts: session, token, Base64, JSON.

## Setup · ~10 min

```bash
docker compose up -d
```

Open `http://localhost:3000`. **Register an account with an email containing your student ID** (e.g. `<ID>@flicker.test`) — so everything you do is tied to you.

## Part 1 — Offensive: access & tokens · ~45 min

### 1.1 Find the hidden function
Find the hidden *Score Board* page (Juice Shop tracks solved challenges). Explain how you found it (inspecting the client-side code / routes).

### 1.2 Broken access control (IDOR)
Logged in as your user, use the API to reach data that isn't yours (e.g. another user's basket) by changing an identifier in the request.

> [!NOTE]
> **Expected.** The server returns someone else's data because it only checks that you're logged in, not that the resource is yours.

### 1.3 The JWT session token
In DevTools (Application → Storage) find the JWT. Decode its three parts (Base64) and show the header and `payload`. Explain the `alg` field and why the signature is critical.

> [!TIP]
> **Common pitfall.** A JWT is not encrypted — Base64 is not a secret. Anyone can *read* a token; the security is in the **signature**. Don't try to break cryptography; show you understand the structure and the risk of a weak/omitted signature.

**In the report:** how you found the Score Board, proof of IDOR (request + other user's data), the decoded JWT with field explanations, and a Score Board screenshot showing your ID account.

## Part 2 — Defensive: correct authorization · ~30 min

### 2.1 Why it worked
Explain (3–5 sentences) why IDOR works (authorization relies on a client-supplied identifier) and the correct approach: **the server checks the logged-in user is allowed that specific resource**.

### 2.2 The fix
**In the report:**
- **Access:** a server-side resource-ownership check (e.g. `resource.owner == current_user`); never trust the ID from the request.
- **Token:** the correct JWT checks (signature, `alg` allowlist, expiry, issuer) and why the secret must be strong.

### 2.3 Recommendations
3 concrete recommendations (authorize on every request, "deny by default", short token lifetime + rotation, never put sensitive data in the token).

### Bonus
- Solve one more Score Board challenge and describe the vulnerability.
- Show how switching `alg` to "none" is stopped by a proper algorithm allowlist.

## Submission

- `lab04_<ID>.pdf` — findings, decoded JWT, Score Board screenshot with your ID account, defensive write-up.
- An **[asciinema](https://asciinema.org/) recording** of your work (`asciinema rec lab.cast`, stop with `Ctrl-D`) — required; the flag only identifies you, this recording is the proof of work.

## Grading

| Item | Points |
|---|:-:|
| Hidden function + API understanding | 2 |
| IDOR to other users' data | 3 |
| JWT token analysis | 2 |
| Defensive write-up (authorization + token) and recommendations | 2 |
| Bonus | +1 |
