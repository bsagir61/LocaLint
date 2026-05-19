# LocaLint

**Local-first QA for CSV/JSON localization files.**

Localization files rarely fail loudly.

They fail late.

A missing `{count}` breaks a runtime string.  
A duplicate key overrides the right translation.  
A long translated label pushes a button out of shape.  
An untranslated line survives until someone finally sees it in a build.

LocaLint is a local check for those quiet mistakes.

It scans existing CSV/JSON localization files and reports release-risk issues before they reach a build.

No login.  
No cloud upload.  
No database.  
No telemetry.  
No AI API.  
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

---

## What LocaLint is

LocaLint is:

- a local QA tool for localization files
- useful before sending files to translators or shipping a build
- built for CSV/JSON localization workflows
- usable through a Streamlit web UI
- usable from the command line
- designed to keep files on your machine

LocaLint is not:

- a translation generator
- an AI writing tool
- a cloud service
- a native Godot, Unity, or Unreal plugin
- a replacement for human localization review

It was built with game localization workflows in mind, but the checks are generic enough for other CSV/JSON localization tables too.

---

## Quick start

Pick a normal writable folder first, such as Desktop or Documents.

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

## Windows launcher

On Windows, you can also start the app by double-clicking:

```text
run-localint-windows.bat
```

The launcher creates the virtual environment if needed, installs dependencies, and starts the Streamlit app.

---

## CLI usage

Run a basic scan:

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

- `godot_sample.csv`: a small clean CSV example
- `broken_sample.csv`: an intentionally broken demo file
- `sample.json`: a flat JSON localization example

---

## Tests

### Windows PowerShell

```powershell
.\.venv\Scripts\python.exe -m pytest
```

If Windows blocks pytest temp folders, run:

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

- `.po` file support
- glossary consistency checks
- batch reports
- engine-specific presets
- GitHub Actions / CI example
- public hosted demo

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