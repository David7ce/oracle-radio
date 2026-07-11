---
name: radio-oracle
description: Interpret Oracle Radio STT transcript logs as an oracle. Reads the captured radio fragments and decodes a combined "message", then answers the six questions — who, how, where, when, why, and what-for. Use when the user wants to analyze, decode, interpret, or "divine" meaning from radio transcript logs (oracle-*.log or a --log file), or asks what the radio is "telling" them.
---

# Radio Oracle

Oracle Radio zaps between live stations and transcribes 2–5s fragments. Each
line looks like:

```
[HH:MM:SS] [Station Name] transcribed fragment text
```

Stitched together, these unrelated fragments form an accidental collage. This
skill reads that collage two ways — grounded first, playful second — and
answers the classic six questions.

## 1. Find the input

- If the user gives a path, use it.
- Otherwise take the newest `oracle-*.log` in the working directory
  (Glob `oracle-*.log`, pick the most recent by name/mtime).
- If none exists, tell the user to run `python oracle.py` (transcripts are
  saved on exit) or pass `--log FILE`, and stop.

Read the whole file. Note how many fragments, the time span (first–last
timestamp), and which languages/stations appear.

## 2. Two-layer reading

**Literal layer (grounded — do this first, never skip).**
Summarize what the fragments *actually* are: ads, news headlines, song lyrics,
sports, chatter. Pull out any concrete facts genuinely present in the text —
named places, dates, numbers, people, events. This is the honest signal.

**Oracle layer (interpretive).**
Treat the stitched fragments as a single cryptic augury and offer a reading.
Be evocative but disciplined: every claim must trace back to actual words in
the log — quote the fragment you drew it from. No invented text.

## 3. Answer the six questions

For each, give the **grounded** answer (what the text supports) and, where the
text is silent, a clearly-labelled **oracle** inference. Cite the fragment.

| Question | Look for |
|----------|----------|
| **Who** (quién) | named people, speakers, the addressee ("you", "colombianos en Madrid"), implied audience |
| **How** (cómo) | manner, method, tone, imperatives ("cuida la energía") |
| **Where** (dónde) | place names, station cities, geographies mentioned |
| **When** (cuándo) | timestamps, dates, "el viernes", seasons, tense |
| **Why** (por qué) | stated causes, motives, the emotional undercurrent |
| **What-for** (para qué) | purpose, call to action, what the "message" seems to want |

## 4. Output

```
🔮 RADIO ORACLE — <logfile>
<N fragments · HH:MM–HH:MM · langs>

The message:
<2–4 sentence decoded reading, quoting real fragments>

Who ......... <grounded> | oracle: <inference>
How ......... ...
Where ....... ...
When ........ ...
Why ......... ...
What-for .... ...

Literal note: <one line — what this really was: ads/news/songs>
```

## Honesty

The oracle layer is divination for fun, not fact — say so once, plainly. The
literal layer and any quoted fragments are real. Never fabricate transcript
text, place names, or dates that aren't in the log; if the log is too sparse to
answer a question, say "silent" rather than inventing.
