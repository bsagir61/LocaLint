# LocaLint

**A local QA tool for CSV/JSON localization files.**

LocaLint checks localization files before release and catches the boring mistakes that are easy to miss: missing translations, broken placeholders, duplicate keys, unchanged strings, long UI text, whitespace issues, punctuation drift, line break mismatches, and encoding warnings.

It runs locally.

No login.  
No cloud upload.  
No database.  
No AI API.  
No telemetry.  
Your files stay on your machine.

---

## Why?

Localization bugs often hide in plain sight.

A missing `{count}` can break a runtime string.  
A duplicate key can override a translation.  
A long translated label can overflow a button.  
A line can stay untranslated without anyone noticing until release.

LocaLint is a small pre-release check for those problems.

It does not translate text.  
It checks the structure and safety of existing localization files.

---

## What it supports

LocaLint currently supports:

- CSV localization tables
- JSON localization dictionaries
- Streamlit web UI
- CLI mode
- Markdown, JSON, CSV, and text reports

It is useful for game localization workflows, especially Godot-style CSV tables, but the checks are generic enough for other CSV/JSON localization files too.

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

Then open:

```text
http://localhost:8501
```

---

## CLI Usage

LocaLint can also run from the terminal.

Basic scan:

```bash
python -m localint.cli sample_data/broken_sample.csv --source en
```

Export a Markdown report:

```bash
python -m localint.cli sample_data/broken_sample.csv --source en --format markdown --out report.md
```

Export JSON:

```bash
python -m localint.cli sample_data/broken_sample.csv --source en --format json --out report.json
```

Use it in stricter workflows:

```bash
python -m localint.cli sample_data/broken_sample.csv --source en --fail-on-critical
```

Show version:

```bash
python -m localint.cli --version
```

---

## CLI Exit Codes

- `0` — scan completed normally
- `1` — critical issues found with `--fail-on-critical`
- `2` — invalid input, parsing error, unsupported file, or usage error

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

- `EXIT` is missing a Turkish translation
- `PLAYER` is missing the `{name}` placeholder
- the file receives a health score
- the report lists the issues by severity

---

## Checks

LocaLint currently detects:

| Check | What it catches |
|---|---|
| Missing translations | Empty target-language cells |
| Placeholder mismatches | Missing or extra `{name}`, `{count}`, `%s`, `%d`, tags, and similar tokens |
| Duplicate keys | Repeated localization keys |
| Invalid keys | Empty keys or suspicious key names |
| Unchanged strings | Target text that still matches the source |
| Length expansion | Text that may overflow UI labels, buttons, or menus |
| Line break drift | Different line break structure between source and target |
| Whitespace issues | Leading or trailing spaces |
| Punctuation drift | Missing or changed ending punctuation |
| CSV encoding warnings | Possible UTF-8 BOM issues |

Severity levels:

- **CRITICAL** — likely to break localization quality or formatting
- **WARNING** — should be reviewed before release
- **INFO** — cleanup or consistency note

---

## Tests

### Windows PowerShell

```powershell
.\.venv\Scripts\python.exe -m pytest
```

If Windows blocks pytest temp folders, use:

```powershell
New-Item -ItemType Directory -Force .pytest-tmp
.\.venv\Scripts\python.exe -m pytest --basetemp=.pytest-tmp
```

### macOS / Linux

```bash
source .venv/bin/activate
python -m pytest
```

Last local verification:

```text
21 passed
```

---

## Sample Files

The `sample_data/` folder includes:

- `godot_sample.csv` — small clean CSV example
- `broken_sample.csv` — intentionally broken demo file
- `sample.json` — flat JSON localization example

---

## Troubleshooting

### `streamlit` is not recognized

Use the Python module form:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

### `pytest` is not recognized

Use:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

### `Permission denied` while cloning

You are probably trying to clone into a protected folder such as `System32`.

Move to Desktop or Documents first:

```powershell
cd "$HOME\Desktop"
```

### Linux: `venv` is missing

Ubuntu / Debian:

```bash
sudo apt install python3-venv
```

---

## Current Limits

LocaLint is still small on purpose.

Not included yet:

- `.po` support
- batch ZIP reports
- glossary consistency checks
- screenshot-based overflow prediction
- native Godot/Unity/Unreal plugins
- hosted web demo

For now, LocaLint focuses on local CSV/JSON localization QA.

---

## Roadmap

Possible next steps:

- `.po` file support
- glossary consistency checks
- batch reports
- Godot-specific CSV preset
- Unity String Table export support
- GitHub Actions / CI example
- public hosted demo

---

## Tech Stack

- Python
- Streamlit
- pandas
- pydantic
- pytest
- argparse

---

## License

MIT License