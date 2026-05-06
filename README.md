# LocaLint

**Catch broken game localization files before your players do.**

LocaLint is a local Streamlit web app for indie game developers working with CSV or JSON localization tables for engines and platforms like Godot, Unity, Steam, and itch.io.

Upload a localization file, choose your source language, and get a clear QA report for missing translations, broken placeholders, duplicate keys, UI overflow risks, suspicious unchanged strings, whitespace issues, punctuation drift, and line break mismatches.

No login.  
No database.  
No paid APIs.  
No cloud upload required.

---

## Why LocaLint?

Localization bugs are easy to miss because they often hide in data files instead of code.

A single missing `{count}`, duplicate key, or oversized button label can break a quest screen, HUD, menu, store page, or release build.

LocaLint gives small teams a quick pre-release localization QA check before shipping.

---

## Features

- CSV localization tables with a `key` column and locale columns
- JSON flat dictionaries shaped like:

```json
{
  "START_GAME": {
    "en": "Start Game",
    "tr": "Oyuna Başla"
  }
}
```

- Automatic language detection
- Source language selector, defaulting to `en` when present
- Toggleable QA checks
- Severity filters, locale filters, and key search
- Report downloads as CSV and Markdown
- Cleaned summary downloads as Markdown or HTML
- Built-in broken sample file for demos

---

## QA Checks

LocaLint currently detects:

- Missing translations
- Placeholder mismatches
- Duplicate keys
- Empty or invalid keys
- Suspicious unchanged strings
- Length expansion and possible UI overflow risks
- Line break mismatches
- Leading or trailing whitespace
- Punctuation drift
- CSV encoding / UTF-8 BOM warnings

Severity levels:

- **CRITICAL**: likely to break localization or release quality
- **WARNING**: should be reviewed before shipping
- **INFO**: cleanup or consistency improvement

---

## Setup

Clone the repository:

```bash
git clone https://github.com/bsagir61/LocaLint.git
cd LocaLint
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Or with `uv` on Windows:

```bash
uv venv .venv
uv pip install --python .\.venv\Scripts\python.exe -r requirements.txt
```

---

## Run

```bash
streamlit run app.py
```

Then open the local Streamlit URL shown in your terminal.

Usually:

```text
http://localhost:8501
```

---

## Test

```bash
pytest
```

Current verification:

```text
10 passed
```

---

## Sample Data

The `sample_data/` folder includes:

- `godot_sample.csv`: a small clean Godot-style CSV
- `broken_sample.csv`: a demo file with missing translations, placeholder mismatches, duplicate keys, long target text, unchanged target text, whitespace issues, line break mismatches, punctuation drift, and an invalid key
- `sample.json`: a flat JSON localization dictionary

---

## Example CSV

```csv
key,en,tr
START_GAME,Start Game,Oyuna Başla
EXIT,Exit,
COINS,You have {count} coins,{count} jetonun var
PLAYER,Player: {name},Oyuncu:
SETTINGS,Settings,Ayarlar
```

LocaLint reports:

- `EXIT` has a missing Turkish translation
- `PLAYER` is missing the `{name}` placeholder in Turkish
- The file receives a localization health score
- The developer gets a prioritized fix list

---

## App Sections

### Overview

Shows total keys, detected languages, total issues, severity counts, and a 0-100 health score.

### Issues

Displays a color-coded issue report with filters for severity, locale, and key search.

### File Preview

Shows the uploaded localization table before analysis.

### Export

Generates CSV, Markdown, and HTML summaries for sharing with translators or developers.

### Validation Notes

Includes target users, positioning notes, validation questions, and outreach ideas for Godot, Unity, Steam, and itch.io indie developers.

---

## MVP Limitations

- `.po` parsing is currently a TODO placeholder
- No batch ZIP upload yet
- No glossary or terminology consistency checks yet
- No screenshot-based text overflow prediction yet
- No login, database, payments, or AI API
- CSV parser expects the first column or a `key` column to contain localization keys
- Unity, Unreal, Steam, and itch.io support currently means exported CSV/JSON-style localization data, not native engine or platform integration

---

## Validation Plan

The fastest validation path is to share LocaLint with Godot, Unity, Steam, and itch.io developers who are close to release and ask them to test it on real localization files.

Useful validation questions:

- Did LocaLint find an issue you would have missed manually?
- Is the report clear enough to send to a translator or teammate?
- Which file format should be supported next?
- Would batch checking multiple files save time?
- Which engine workflow matters most: Godot, Unity, Unreal, or generic CSV/JSON?
- Are the severity levels useful, or should they be adjusted?

---

## Roadmap

Planned improvements:

- Batch ZIP upload
- `.po` file support
- Godot-specific CSV preset
- Unity String Table export support
- Unreal `.po` localization support
- Glossary consistency checks
- Steam store localization checker
- Screenshot-based text overflow prediction
- Public hosted demo

---

## Tech Stack

- Python
- Streamlit
- pandas
- pydantic
- pytest

---

## Project Status

LocaLint is an MVP.

It is not a translation platform.  
It does not generate translations.  
It focuses on localization QA: finding broken or risky localization entries before release.

---

## License

MIT License