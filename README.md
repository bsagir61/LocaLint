# LocaLint

**Catch broken game localization files before your players do.**

LocaLint is a local localization QA tool for CSV/JSON game localization files. It can run as a Streamlit web app or as a command-line tool.

LocaLint checks existing localization files for missing translations, placeholder mismatches, duplicate keys, suspicious unchanged text, length expansion risks, whitespace issues, line break mismatches, punctuation drift, and CSV encoding warnings.

It is not a translation generator.

## What LocaLint Is

LocaLint is a localization QA checker for developers and small game teams preparing exported localization files for release.

It supports Godot, Unity, Unreal, Steam, itch.io, and generic workflows through exported CSV/JSON-style localization data. It does not include native engine plugin integration in this version.

## What LocaLint Is Not

- Not a translation generator.
- No AI APIs.
- No login.
- No payments.
- No database.
- No telemetry or analytics.
- No cloud upload.
- No native Godot, Unity, or Unreal plugin code.
- No `.po` support in v0.2.0

Native plugins and `.po` support may be future roadmap items, but they are not current functionality.

## Privacy / Local-First

LocaLint runs locally on your machine. Uploaded files in the Streamlit app and files scanned by the CLI are processed locally.

There is no login, no database, no cloud upload, and no telemetry.

## Quick Start

Windows PowerShell:

```powershell
git clone https://github.com/bsagir61/LocaLint.git
cd LocaLint
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

macOS / Linux:

```bash
git clone https://github.com/bsagir61/LocaLint.git
cd LocaLint
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m streamlit run app.py
```

## CLI Usage

Basic scan:

```powershell
.\.venv\Scripts\python.exe -m localint.cli sample_data/broken_sample.csv
```

Choose source language:

```powershell
.\.venv\Scripts\python.exe -m localint.cli sample_data/broken_sample.csv --source en
```

Export Markdown report:

```powershell
.\.venv\Scripts\python.exe -m localint.cli sample_data/broken_sample.csv --format markdown --out report.md
```

Export JSON report:

```powershell
.\.venv\Scripts\python.exe -m localint.cli sample_data/broken_sample.csv --format json --out report.json
```

Export CSV report:

```powershell
.\.venv\Scripts\python.exe -m localint.cli sample_data/broken_sample.csv --format csv --out report.csv
```

Fail on critical issues for CI-style usage:

```powershell
.\.venv\Scripts\python.exe -m localint.cli sample_data/broken_sample.csv --fail-on-critical
```

Print version:

```powershell
.\.venv\Scripts\python.exe -m localint.cli --version
```

CLI exit codes:

- `0`: analysis completed.
- `1`: critical issues found and `--fail-on-critical` was enabled.
- `2`: invalid input, unsupported file, parsing error, or CLI usage error.

## Supported Input Formats

### CSV

```csv
key,en,tr,es
START_GAME,Start Game,Oyuna Basla,Iniciar juego
COINS,You have {count} coins,{count} jetonun var,Tienes {count} monedas
```

CSV notes:

- A `key` column is recommended.
- If there is no `key` column, the first column is treated as the key column.
- At least one language column is required.
- For target QA checks, use at least two language columns, such as `en` and `tr`.

### JSON

```json
{
  "START_GAME": {
    "en": "Start Game",
    "tr": "Oyuna Basla"
  },
  "COINS": {
    "en": "You have {count} coins",
    "tr": "{count} jetonun var"
  }
}
```

Expected shape: a flat dictionary where each localization key maps to locale values.

## Streamlit App

Run:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Then open the local URL shown in the terminal, usually:

```text
http://localhost:8501
```

The app includes upload, source-language selection, issue filters, file preview, report exports, and a one-click demo sample.

## Tests

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

macOS / Linux:

```bash
source .venv/bin/activate
python -m pytest
```

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

### Virtual environment not activated

Activation is optional on Windows if you use explicit commands:

```powershell
.\.venv\Scripts\python.exe -m localint.cli sample_data/broken_sample.csv
.\.venv\Scripts\python.exe -m streamlit run app.py
```

### Missing dependencies

Run from the repository root:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Wrong working directory

Run commands from the folder that contains `app.py`, `requirements.txt`, and `README.md`.

Windows PowerShell:

```powershell
Get-Location
cd path\to\LocaLint
```

## Sample Data

- `sample_data/godot_sample.csv`: small clean sample.
- `sample_data/broken_sample.csv`: demo file with common localization QA issues.
- `sample_data/sample.json`: flat JSON localization dictionary.

## Project Status

LocaLint v0.2.0 is an early local-first MVP with both Streamlit and CLI modes.

The current focus is reliable localization QA for CSV/JSON files. It does not generate translations, call AI APIs, upload files, or integrate as a native engine plugin.

## Roadmap

Possible future work:

- Batch ZIP upload.
- `.po` support.
- Godot plugin.
- Unity editor extension.
- Glossary consistency checks.
- Steam store localization checker.
- Screenshot text overflow prediction.

## License

MIT License
