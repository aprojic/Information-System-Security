**Language:** English · [Hrvatski](README.hr.md)

<!-- kicker: Lab 08 · attack then defend · Information System Security -->
# Lab 08 — AI Security: Prompt Injection

*Apps built on language models have a new attack surface: the input itself. Extract a secret from a chatbot with words, then show why an output filter is a patch, not a cure.*

`~90 min` · `Kali · Docker · Ollama (local LLM)` · `level: advanced` · `submit: Merlin`

> [!WARNING]
> **Ethics & scope.** Only against the local SecureBot in the lab environment. Attacking third-party AI services violates their terms and the law.

**Scenario.** Flicker shipped an internal assistant, **SecureBot**, with a secret access code placed in its system prompt "because the user never sees that prompt anyway". You're first the **attacker** who extracts the secret with words, then the **engineer** who explains why the whole approach is wrong.

## Learning outcomes

- Understand prompt injection and why a system prompt is not a secret.
- Extract a hidden secret from an LLM app using direct and indirect techniques.
- Show that a naive output filter is bypassable.
- Explain the correct defences (OWASP LLM Top 10) and "never put secrets in the prompt".

## Prerequisites

- [ ] [Lab 00](../lab-00-setup/README.md) completed — Kali + Docker working.
- [ ] ≥ 4 GB free RAM and ~2 GB disk (the model downloads locally).
- [ ] Concepts: LLM, system prompt, context.

## Setup · ~15 min

Copy `.env.example` to `.env` and set `ISS_SECRET` (from the instructor), then:

```bash
cp .env.example .env     # edit: ISS_SECRET=<from instructor>
docker compose up -d --build
docker compose exec ollama ollama pull llama3.2:1b    # once, ~1.3 GB
```

Open `http://localhost:5000` and **enter your student ID**. SecureBot then has your secret code of the form `ASPIRA{sis_ai_...}` in its system prompt, which you must extract.

> [!TIP]
> **Common pitfall.** The first reply is slow while the model loads. A model error → check that `ollama pull` finished (`docker compose logs ollama`).

## Part 1 — Offensive: extract the secret · ~35 min

### 1.1 Direct prompt injection
Try to override the "don't reveal" instruction (role-play, claiming a new context, asking for "previous instructions"). Document what worked and what didn't.

### 1.2 Indirect / bypass approach
If direct asking fails, make the model **transform** the secret (spell it out, translate, encode, "letter by letter") or print its system prompt, and reconstruct `ASPIRA{sis_ai_...}`. For a 1B model, asking it to print its **full system prompt verbatim** is usually the most reliable way to get the exact flag — "spell it letter by letter" often mangles the hex.

> [!NOTE]
> **Expected.** A small model struggles to keep the secret consistently — a combination of techniques yields the full code. That is your flag.

**In the report:** at least 3 different attempts (with responses), which succeeded, and **your extracted flag**.

## Part 2 — Defensive: why a filter isn't enough · ~30 min

### 2.1 Turn on the naive defence
In `.env`/`compose.yml` set `GUARDRAIL: "on"` and bring `securebot` back up (`docker compose up -d securebot`). Now the app strips the exact code from responses. Repeat the attack.

### 2.2 Bypass the filter
**In the report:** show you bypass it by making the model **not print the secret verbatim** (spaced out, letter by letter, Base64, another language), then reassemble it. Attach an example.

### 2.3 The real defence
**In the report:** explain (5–7 sentences) why the filter is only a patch and what is correct (tie to OWASP LLM Top 10):
- **Don't put secrets/privileges in the prompt** — enforce authorization outside the model.
- **Least privilege for tools** the model may call; human-in-the-loop for sensitive actions.
- **Input/output validation** as defence-in-depth, not the sole control.

### Bonus
- Sketch an **indirect** prompt injection (a malicious instruction hidden in a document the model reads). Why is it more dangerous?
- Propose a CI test that checks for "secret leakage".

## Submission

- `lab08_<ID>.pdf` — attempts with responses, extracted flag, filter bypass, defensive write-up.
- An **[asciinema](https://asciinema.org/) recording** of your work (`asciinema rec lab.cast`, stop with `Ctrl-D`) — required; the flag only identifies you, this recording is the proof of work.

## Grading

| Item | Points |
|---|:-:|
| Extracted secret (flag) + documented attempts | 3 |
| Bypass of the naive filter | 3 |
| Defensive write-up (OWASP LLM) and recommendations | 3 |
| Understanding of the indirect attack | 1 |
| Bonus | +1 |
