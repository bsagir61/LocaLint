# LocaLint

LocaLint checks CSV/JSON localization files before release.

It looks for the kinds of problems that are easy to miss in localization tables:

- missing translations
- broken placeholders
- duplicate keys
- unchanged target strings
- long UI text
- formatting drift
- JSON structure issues
- CSV encoding warnings

LocaLint runs locally. Files are not uploaded anywhere.
No AI API requirement.
Your files stay on your machine.

---

## What LocaLint catches

| Check | What it finds |
|---|---|
| Missing translations | Empty target-language cells |
| Placeholder mismatches | Missing or extra `{count}`, `{name}`, `%s`, `%d`, tags, or similar tokens |
| Duplicate keys | Repeated localization keys |
| Invalid keys | Empty or suspicious key names |
| Unchanged strings | Target text that still matches the source |
| Length expansion | Text that may overflow buttons, labels, menus, or HUD elements |
| Line break drift | Different line break structure between source and target |
| Whitespace issues | Leading or trailing spaces |
| Punctuation drift | Missing or changed ending punctuation |
| CSV encoding warnings | Possible UTF-8 BOM issues |

Severity levels:

- **CRITICAL**: likely to break formatting or release quality
- **WARNING**: should be checked before release
- **INFO**: cleanup or consistency note
=======
No AI API.

---

## Why

Localization files often look harmless until they reach a build.

A missing `{count}` can break a runtime string.  
A duplicate key can override the right translation.  
A long translated label can overflow a button.  
An untranslated line can survive until release.

LocaLint is a local check for those issues.

It does not translate text.  
It checks existing localization files and reports release-risk problems.
>>>>>>> 820b1e6 (Update README)

---

## What LocaLint is

LocaLint is:

<<<<<<< HEAD
- a local QA tool for localization files
- useful before sending files to translators or shipping a build
- built for CSV/JSON localization workflows
- usable through a Streamlit web UI
- usable from the command line
- designed to keep files on your machine

LocaLint is not:
=======
- CSV localization tables
- JSON localization dictionaries
- Streamlit web UI
- command-line usage
- text, Markdown, JSON, and CSV reports

It was built with game localization workflows in mind, but the checks are useful for other CSV/JSON localization files too.
>>>>>>> 820b1e6 (Update README)

- a translation generator
- an AI writing tool
- a cloud service
- a native Godot, Unity, or Unreal plugin
- a replacement for human localization review

It was built with game localization workflows in mind, but the checks are generic enough for other CSV/JSON localization tables too.

---

## Quick start

<<<<<<< HEAD
Pick a normal writable folder first, such as Desktop or Documents.
=======
Choose a normal writable folder first, such as Desktop or Documents.
>>>>>>> 820b1e6 (Update README)

### Windows PowerShell

```powershell
cd "$HOME\Desktop"
git clone https://github.com/bsagir61/LocaLint.git
cd LocaLint
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Then open:

```text
http://localhost:8501
```

If you already cloned the repository:

```powershell
cd "$HOME\Desktop\LocaLint"
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Or use the Windows launcher:

```powershell
.\run-localint-windows.bat
```

---

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

<<<<<<< HEAD
## Windows launcher

On Windows, you can also start the app by double-clicking:

```text
run-localint-windows.bat
```

The launcher creates the virtual environment if needed, installs dependencies, and starts the Streamlit app.

---

## CLI usage

Run a basic scan:
=======
## CLI usage

Basic scan:
>>>>>>> 820b1e6 (Update README)

```bash
python -m localint.cli sample_data/broken_sample.csv --source en
```

Show fewer issues in the terminal:

```bash
python -m localint.cli sample_data/broken_sample.csv --source en --max-issues 5
```

Export a Markdown report:

```bash
python -m localint.cli sample_data/broken_sample.csv --source en --format markdown --out report.md
```

Export JSON:

```bash
python -m localint.cli sample_data/broken_sample.csv --source en --format json --out report.json
```

Export CSV:

```bash
python -m localint.cli sample_data/broken_sample.csv --source en --format csv --out report.csv
```

Fail when critical issues are found:

```bash
python -m localint.cli sample_data/broken_sample.csv --source en --fail-on-critical
```

Show version:

```bash
python -m localint.cli --version
```

---

## CLI exit codes

- `0` means the scan completed normally
- `1` means critical issues were found with `--fail-on-critical`
- `2` means invalid input, parsing error, unsupported file, or usage error
<<<<<<< HEAD
=======

---

## Checks

| Check | What it catches |
|---|---|
| Missing translations | Empty target-language cells |
| Placeholder mismatches | Missing or extra `{count}`, `{name}`, `%s`, `%d`, tags, or similar tokens |
| Duplicate keys | Repeated localization keys |
| Invalid keys | Empty or suspicious key names |
| Unchanged strings | Target text that still matches the source |
| Length expansion | Text that may overflow buttons, labels, menus, or HUD elements |
| Line break drift | Different line break structure between source and target |
| Whitespace issues | Leading or trailing spaces |
| Punctuation drift | Missing or changed ending punctuation |
| JSON structure issues | JSON files that do not match the expected localization shape |
| CSV encoding warnings | Possible UTF-8 BOM issues |

Severity levels:

- **CRITICAL**: likely to break formatting or release quality
- **WARNING**: should be checked before release
- **INFO**: cleanup or consistency note
>>>>>>> 820b1e6 (Update README)

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

LocaLint would report that:

- `EXIT` is missing a Turkish translation
- `PLAYER` is missing the `{name}` placeholder
- the file has release-risk issues
- issues should be fixed by severity

---

## Example terminal output

```text
LocaLint report
File: sample_data\broken_sample.csv
Source language: en
Target languages: tr, es
Total keys: 11
Total issues: 10
Critical: 5
Warning: 3
Info: 2
Health score: 23/100
```

---

## Sample files

The `sample_data/` folder includes:

<<<<<<< HEAD
- `godot_sample.csv`: a small clean CSV example
- `broken_sample.csv`: an intentionally broken demo file
- `sample.json`: a flat JSON localization example
=======
- `godot_sample.csv`: clean CSV example
- `broken_sample.csv`: intentionally broken demo file
- `sample.json`: flat JSON localization example
>>>>>>> 820b1e6 (Update README)

---

## Tests

### Windows PowerShell

```powershell
.\.venv\Scripts\python.exe -m pytest
```

<<<<<<< HEAD
If Windows blocks pytest temp folders, run:
=======
If Windows blocks pytest temp folders:
>>>>>>> 820b1e6 (Update README)

```powershell
New-Item -ItemType Directory -Force .pytest-tmp
.\.venv\Scripts\python.exe -m pytest --basetemp=.pytest-tmp
Remove-Item .pytest-tmp -Recurse -Force -ErrorAction SilentlyContinue
```

### macOS / Linux

```bash
source .venv/bin/activate
python -m pytest
```

Current test suite:

```text
21 tests
```

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

You are probably trying to clone into a protected system folder.

Use Desktop or Documents instead:

```powershell
cd "$HOME\Desktop"
```

### Linux: `venv` is missing

Ubuntu / Debian:

```bash
sudo apt install python3-venv
```

---

## Current limits

LocaLint is focused on CSV/JSON localization QA.

Not included yet:

- `.po` support
- batch reports
- glossary consistency checks
- screenshot-based overflow prediction
- native Godot, Unity, or Unreal plugins
- hosted web demo

---

## Roadmap

Likely next steps:

- `.po` support
- glossary consistency checks
- batch reports
- engine-specific presets
- GitHub Actions / CI example
- hosted demo

---

## Tech stack

- Python
- Streamlit
- pandas
- pydantic
- pytest
- argparse

---

## License

MIT License