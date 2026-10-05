# Network Pulse

A keep-in-touch tracker built from a LinkedIn data export. It scores every connection, keeps the useful ones on a reminder cycle (7 days for the top tier, 30 for everyone else), drafts messages with AI, and lists recruiter emails.

This repository holds the **code only**. Your own data stays on your machine: `data/contacts.json`, `data/emails.json`, `dist/` and the raw LinkedIn CSVs are git-ignored, because they contain other people's names, employers and message snippets.

## Quick start

```bash
python pipeline/build.py      # builds dist/network-pulse.html from the sample data
open dist/network-pulse.html  # or double-click it
```

## Use your own LinkedIn data

1. On LinkedIn: Settings → Data privacy → Get a copy of your data. Download `Connections.csv` and `messages.csv` into `pipeline/`.
2. Set your own profile URL at the top of `pipeline/feat.py`.
3. Run:

```bash
cd pipeline
python feat.py      # message history per person
python score.py     # first-pass table
python rescore.py   # seniority-weighted scores, location inference, cadence
python export.py    # -> data/contacts.json
python build.py     # -> dist/network-pulse.html
```

Optional: copy `notes.example.py` to `notes.py` to add hand-written context and score overrides for key people.

## Running the built file

- **Storage:** activity (touches, drafts, snoozes, location corrections) is saved in the browser's localStorage. Standalone settings has "Copy my activity as JSON" and "Import activity file" for backups and moving between browsers.
- **AI buttons:** paste an Anthropic API key under Standalone settings. It stays in the browser and is sent only to `api.anthropic.com`.
- Do not publish `dist/network-pulse.html` (for example with GitHub Pages): it embeds your contacts.

## How scoring works

| Signal | Effect |
|---|---|
| Executive, director, principal, staff, manager, founder | Large boost, with or without message history |
| Employer relevant to AI/LLM roles | Boost by tier |
| In-house recruiter, university career services | Boost |
| AI/ML in the title | Small boost |
| Real two-way message thread | Boost by depth |
| Student, intern, non-technical role | Low, still tracked |
| Staffing agency | Not tracked |
| Employer or title points to India | Set aside until marked otherwise |

Everyone else is tracked. Score 70+ comes due every 7 days, the rest every 30.

Location is inferred, because the LinkedIn export has no location field. A connection made in 2024 or earlier with nothing pointing elsewhere is marked "location unverified" and tracked only from score 30 up. Correct mistakes in the app with "Mark as outside India" / "Mark as in India". The company lists and the India rule in `pipeline/rescore.py` reflect one person's job search; edit them for yours.

## Layout

- `src/app_template.html` app source (`__DATA__` and `__EMAILS__` are filled by `build.py`)
- `pipeline/` scoring and build scripts
- `data/*.sample.json` sample data so the app builds out of the box
