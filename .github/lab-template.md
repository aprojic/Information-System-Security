<!-- kicker: Lab NN · attack then defend · Information System Security -->
# Lab NN — Title of the lab

*One sentence on what students do, shown under the title.*

`~90 min` · `Kali · tools` · `level: intro` · `submit: Merlin`

> [!WARNING]
> **Ethics & scope.** Work only against the included practice target, in your lab environment. The same techniques against real systems are a criminal offence.

**Scenario.** A short, concrete situation (the "Flicker" company) that explains why this lab matters.

- **Offensive:** what you attack.
- **Defensive:** what you fix or detect.

## Learning outcomes

- What students can do after the lab (3–4 bullets, start with a verb).

## Prerequisites

- [ ] [Lab 00](../lab-00-okruzenje/README.md) completed — Kali (+ Docker) working.
- [ ] Your student ID (matični broj).

## Setup · ~10 min

```bash
docker compose up -d   # if the lab has a target
```

Enter your student ID where the lab says, so the target computes **your** flag.

## Part 1 — Offensive: … · ~40 min

### 1.1 First step

Explain the step, then the command.

```bash
command --flag value
```

> [!NOTE]
> **Expected.** What the student should see.

> [!TIP]
> **Common pitfall.** What goes wrong and how to fix it.

**In the report:** what the student records here, including **your flag**.

## Part 2 — Defensive: … · ~30 min

### 2.1 Why it worked, and the fix

What to explain and the concrete mitigation.

### Bonus

- Optional stretch task.

## Submission

- `labNN_<ID>.pdf` — report with your flag and the required steps.
- Process log (`asciinema` recording or a timestamped command history).

## Grading

| Item | Points |
|---|:-:|
| … | 3 |
| … | 3 |
| … | 3 |
| … | 1 |
| Bonus | +1 |
