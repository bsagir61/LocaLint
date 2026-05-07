# LocaLint

**Catch broken game localization files before your players do.**

LocaLint is a small local localization QA tool for game localization files.

It helps catch missing translations, broken placeholders, duplicate keys, suspicious unchanged text, length expansion risks, whitespace issues, punctuation drift, line break mismatches, and encoding problems before release.

LocaLint v0.1.1 is intentionally small, local-first, and focused on CSV/JSON localization QA.

No login.  
No database.  
No paid APIs.  
No cloud upload required.  
Your localization files stay on your machine.

---

## Why LocaLint?

Localization bugs often hide in data files instead of code.

A single missing `{count}`, renamed placeholder, duplicated key, or oversized button label can quietly break a menu, HUD, quest screen, dialogue line, or release build.

LocaLint gives small teams a fast pre-release localization QA pass before players discover those issues.

It is not a translation platform.  
It does not generate translations.  
It checks whether your existing localization files are structurally safe, consistent, and ready to review.

---

## Who Is It For?

LocaLint is built for:

- Indie game developers
- Game jam teams
- Godot developers using CSV-style translation tables
- Unity developers working with exported localization tables
- Small localization teams
- Steam and itch.io developers preparing multilingual releases
- Developers who want a quick local QA check before sending files to translators or shipping a build

LocaLint currently focuses on exported CSV and JSON localization data, not native engine plugin integration.

---

## Quick Start

Choose a writable folder first, such as Desktop or Documents.

### Windows PowerShell

```powershell
cd "$HOME\Desktop"
git clone https://github.com/bsagir61/LocaLint.git
cd LocaLint
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

### macOS / Linux

```bash
cd ~/Desktop
git clone https://github.com/bsagir61/LocaLint.git
cd LocaLint
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal, usually:

```text
http://localhost:8501
```

---

## Features

- CSV localization tables with a `key` column and locale columns
- Flat JSON localization dictionaries
- Automatic language detection
- Source language selector, defaulting to `en` when available
- Toggleable QA checks
- Severity levels: `CRITICAL`, `WARNING`, and `INFO`
- Severity, locale, and key filters
- Searchable issue table
- Prioritized next-fix suggestions
- File preview before review
- Report downloads as CSV and Markdown
- Clean summary downloads as Markdown or HTML
- Built-in broken sample file for demos

---

## QA Checks

LocaLint currently detects:

| Check | What it catches |
|---|---|
| Missing translations | Empty target-language cells |
| Placeholder mismatches | Missing or extra `{name}`, `{count}`, `%s`, `%d`, tags, and similar tokens |
| Duplicate keys | Repeated localization keys |
| Empty or invalid keys | Blank keys or keys with suspicious formatting |
| Suspicious unchanged strings | Target text that appears to be copied from the source |
| Length expansion risk | Translations that may overflow UI labels, buttons, menus, or HUD elements |
| Line break mismatches | Source and target strings with different line break structure |
| Leading/trailing whitespace | Accidental spaces before or after text |
| Punctuation drift | Changed or missing `?`, `!`, `:`, or similar ending punctuation |
| CSV encoding / BOM warnings | Potential UTF-8 BOM issues, especially relevant for some CSV workflows |

Severity levels:

- **CRITICAL**: likely to break localization quality or runtime formatting
- **WARNING**: should be reviewed before release
- **INFO**: cleanup, formatting, or consistency improvement

---

## Supported Input Formats

### CSV

Example:

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

### JSON

Example:

```json
{
  "START_GAME": {
    "en": "Start Game",
    "tr": "Oyuna Başla"
  },
  "COINS": {
    "en": "You have {count} coins",
    "tr": "{count} jetonun var"
  }
}
```

---

## Setup

Clone the repository:

```bash
git clone https://github.com/bsagir61/LocaLint.git
cd LocaLint
```

Create a virtual environment:

```bash
python -m venv .venv
```

Install dependencies:

### Windows PowerShell

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### macOS / Linux

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows with uv

```powershell
uv venv .venv
uv pip install --python .\.venv\Scripts\python.exe -r requirements.txt
```

---

## Run

### Windows PowerShell

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

### macOS / Linux

```bash
source .venv/bin/activate
python -m streamlit run app.py
```

Or, if your virtual environment is already activated and `streamlit` is available:

```bash
streamlit run app.py
```

Then open the local Streamlit URL shown in your terminal, usually:

```text
http://localhost:8501
```

---

## Test

### Windows PowerShell

```powershell
.\.venv\Scripts\python.exe -m pytest
```

### macOS / Linux

```bash
source .venv/bin/activate
python -m pytest
```

Or, if your virtual environment is already activated and `pytest` is available:

```bash
pytest
```

Last local verification:

```text
16 passed
```

---

## Sample Data

The `sample_data/` folder includes:

- `godot_sample.csv`: a small clean Godot-style CSV file
- `broken_sample.csv`: a demo file with missing translations, placeholder mismatches, duplicate keys, long target text, unchanged target text, whitespace issues, line break mismatches, punctuation drift, and an invalid key
- `sample.json`: a flat JSON localization dictionary

The built-in broken sample is useful for quickly testing the app and demonstrating the report output.

---

## App Sections

### Overview

Shows total keys, detected languages, total issues, severity counts, and a 0-100 localization health score.

### Issues

Displays a filtered QA issue report with severity labels, affected keys, locales, messages, suggestions, source text, and target text.

### File Preview

Shows the uploaded localization table before or after analysis.

### Export

Generates CSV, Markdown, and HTML summaries that can be shared with translators, developers, or teammates.

### Validation Notes

Includes target users, positioning notes, validation questions, and outreach ideas for indie game development communities.

---

## Troubleshooting

### `streamlit` is not recognized

Use the Python module form instead:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

On macOS / Linux, activate the environment first:

```bash
source .venv/bin/activate
python -m streamlit run app.py
```

### `pytest` is not recognized

Use:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Or on macOS / Linux:

```bash
source .venv/bin/activate
python -m pytest
```

### `Permission denied` while cloning

You may be trying to clone into a protected system folder.

Choose a writable folder first:

```powershell
cd "$HOME\Desktop"
git clone https://github.com/bsagir61/LocaLint.git
```

### Linux: `venv` is missing

On some Linux distributions, you may need to install the Python venv package first.

Ubuntu / Debian:

```bash
sudo apt install python3-venv
```

---

## MVP Limitations

LocaLint is an MVP and intentionally keeps its scope narrow.

Current limitations:

- `.po` parsing is currently a TODO placeholder
- No batch ZIP upload yet
- No glossary or terminology consistency checks yet
- No screenshot-based text overflow prediction yet
- No login, database, payments, telemetry, or AI API
- CSV parser expects the first column or a `key` column to contain localization keys
- Unity, Unreal, Steam, and itch.io support currently means exported CSV/JSON-style localization data, not native engine or platform integration

---

## Validation Plan

The fastest validation path is to share LocaLint with developers who are close to releasing a localized game and ask them to test it on real localization files.

Useful validation questions:

- Did LocaLint find an issue you would have missed manually?
- Is the report clear enough to send to a translator or teammate?
- Which file format should be supported next?
- Would batch checking multiple files save time?
- Which engine workflow matters most: Godot, Unity, Unreal, or generic CSV/JSON?
- Are the severity levels useful, or should they be adjusted?
- Which check would make this more useful in a real release pipeline?

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
- Optional CI workflow for automated tests

---

## Tech Stack

- Python
- Streamlit
- pandas
- pydantic
- pytest

---

## Project Status

LocaLint is an early MVP.

It is not a translation platform.  
It does not generate translations.  
It focuses on localization QA: finding broken or risky localization entries before release.

The current goal is to validate whether indie developers find this kind of local QA tool useful in real game localization workflows.

---

## License

MIT License