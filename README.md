# LocaLint

Local-first QA for CSV/JSON/PO localization files.

LocaLint checks existing localization files before release. It looks for problems that are easy to miss in tables and exported string files:

- missing translations
- broken placeholders
- duplicate keys
- unchanged target strings
- long UI text
- formatting drift
- JSON structure issues
- CSV encoding warnings
- PO msgid/msgstr issues

LocaLint runs on your machine. It does not translate text, use AI, upload files, require login, store data in a database, or send telemetry.

---

## What it is for

Localization files can look fine until they reach a build. A missing `{count}` can break a runtime string. A duplicate key can override the right text. A long label can overflow a button. An empty cell can make it all the way to release.

LocaLint gives you a local QA pass for those issues.

It was built with game localization workflows in mind, but it works for other CSV, JSON, and PO localization files too.

---

## Supported files

LocaLint currently supports:

- CSV localization tables
- JSON localization dictionaries
- PO files with common `msgid` / `msgstr` entries
- common locale codes and variants such as `en`, `en-US`, `pt-BR`, `zh-TW`, and `en_US`
- Streamlit web UI
- command-line usage
- text, Markdown, JSON, and CSV reports

It is not a native Godot, Unity, or Unreal plugin.

---

## Release Gate

Every scan returns a release gate:

- **PASS**: no critical, warning, or info issues
- **REVIEW**: warnings or info notes exist, but no critical issues
- **BLOCK**: critical issues exist

The gate appears in the app, CLI text output, Markdown reports, and JSON reports.

---

## Locale handling

LocaLint keeps original column names for reading files, but normalizes locale labels for display. For example, `en_US` is shown as `en-US`.

It recognizes common language and locale variants, including `pt-BR`, `pt-PT`, `zh-CN`, `zh-TW`, `zh-Hans`, and `zh-Hant`. Obvious CSV metadata columns such as `notes`, `context`, `screenshot`, and `max_length` are not treated as target locales.

Unknown locale codes are left as-is.

---

## Quick start

Use a normal writable folder such as Desktop or Documents.

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

If the repository is already cloned:

```powershell
cd "$HOME\Desktop\LocaLint"
.\.venv\Scripts\python.exe -m streamlit run app.py
```

You can also use the Windows launcher:

```powershell
.\run-localint-windows.bat
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

## CLI usage

Run these commands from the repository root after installing dependencies.

On Windows PowerShell, use `.\.venv\Scripts\python.exe` instead of `python` if the virtual environment is not active.

Basic scan:

```bash
python -m localint.cli sample_data/broken_sample.csv --source en
```

Scan JSON:

```bash
python -m localint.cli sample_data/sample.json --source en
```

Use a locale variant as source:

```bash
python -m localint.cli path/to/strings.csv --source en-US
```

Scan PO:

```bash
python -m localint.cli sample_data/sample.po
```

Limit terminal output:

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

Fail the command when critical issues are found:

```bash
python -m localint.cli sample_data/broken_sample.csv --source en --fail-on-critical
```

Create a starter config:

```bash
python -m localint.cli --init-config
```

Use a config file:

```bash
python -m localint.cli sample_data/broken_sample.csv --config .localint.toml
```

Save a baseline of known issues:

```bash
python -m localint.cli sample_data/broken_sample.csv --source en --write-baseline .localint-baseline.json
```

Compare against a baseline:

```bash
python -m localint.cli sample_data/broken_sample.csv --source en --baseline .localint-baseline.json
```

Fail only on new critical issues:

```bash
python -m localint.cli sample_data/broken_sample.csv --source en --baseline .localint-baseline.json --fail-on-new-critical
```

Show the installed version:

```bash
python -m localint.cli --version
```

### Exit codes

- `0`: scan completed
- `1`: critical issues were found with `--fail-on-critical`
- `2`: invalid input, parse error, unsupported file, or usage error

---

## Checks

| Check | What it catches |
| --- | --- |
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
| PO parsing notes | PO files are mapped to source/target rows for QA |

Severity levels:

- **CRITICAL**: likely to break formatting or release quality
- **WARNING**: should be reviewed before release
- **INFO**: cleanup or consistency note

---

## Example CSV

```csv
key,en,tr
START_GAME,Start Game,Oyuna Basla
EXIT,Exit,
COINS,You have {count} coins,{count} jetonun var
PLAYER,Player: {name},Oyuncu:
SETTINGS,Settings,Ayarlar
```

LocaLint would report that:

- `EXIT` is missing a Turkish translation
- `PLAYER` is missing the `{name}` placeholder
- the file has release-risk issues to fix before shipping

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
Release gate: BLOCK
```

---

## Sample files

The `sample_data/` folder includes:

- `godot_sample.csv`: clean CSV example
- `broken_sample.csv`: intentionally broken demo file
- `sample.json`: flat JSON localization example
- `sample.po`: clean PO example
- `broken_sample.po`: intentionally broken PO example

---

## Tests

### Windows PowerShell

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
54 tests
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

You are probably cloning into a protected system folder. Use Desktop or Documents instead:

```powershell
cd "$HOME\Desktop"
```

### Linux: `venv` is missing

Ubuntu / Debian:

```bash
sudo apt install python3-venv
```

---

## Current scope

LocaLint is focused on local QA for CSV/JSON/PO localization files.

It does not currently include:

- full gettext coverage
- advanced PO plural-form evaluation
- batch reports
- glossary consistency checks
- screenshot-based overflow prediction
- native Godot, Unity, or Unreal plugins
- hosted file upload or cloud analysis

An inactive GitHub Actions example is available at `docs/github-actions-example.yml`.

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
