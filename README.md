# LocaLint

LocaLint is a local localization QA tool for game localization files.

It helps catch missing translations, broken placeholders, duplicate keys, suspicious unchanged text, length expansion risks, whitespace issues, line break mismatches, punctuation drift, and CSV encoding warnings before a game ships.

LocaLint v0.1.1 is intentionally small and local-first.

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
streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal, usually:

```text
http://localhost:8501
```

## What LocaLint Is

LocaLint is a localization QA checker. It reviews existing CSV/JSON localization files and reports risky entries with clear severity levels:

- `CRITICAL`: likely release blocker, such as missing translations or broken placeholders.
- `WARNING`: should be reviewed before release, such as duplicate-looking content or major length expansion.
- `INFO`: cleanup or consistency note, such as extra whitespace.

It is useful for indie teams preparing Godot, Unity, Unreal, Steam, itch.io, or generic game localization data for release.

## What LocaLint Is Not

LocaLint is not a translation generator.

It does not translate text, rewrite strings, or call AI services. It does not include native Godot, Unity, or Unreal plugin integration in this version.

Current engine support means exported CSV/JSON-style localization files only. Native plugins may be future roadmap items, but they are not current functionality.

## Privacy / Local-First

LocaLint runs locally on your machine.

- No login.
- No database.
- No cloud upload.
- No telemetry.
- No analytics.
- No AI APIs.
- Files are processed locally by the Streamlit app.

## Supported Input Formats

### CSV

Expected shape:

```csv
key,en,tr,es
START_GAME,Start Game,Oyuna Basla,Iniciar juego
COINS,You have {count} coins,{count} jetonun var,Tienes {count} monedas
```

CSV requirements:

- A `key` column is recommended.
- If there is no `key` column, the first column is treated as the key column.
- At least one language column is required.
- For target QA checks, use at least two language columns, such as `en` and `tr`.

### JSON

Expected flat dictionary shape:

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

`.po` support is planned, but not included in v0.1.1.

## Windows PowerShell Setup, Run, Test

Create the virtual environment:

```powershell
python -m venv .venv
```

Install dependencies:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Run the app:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Run tests:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Optional activation:

```powershell
.\.venv\Scripts\Activate.ps1
streamlit run app.py
pytest
```

If activation is blocked by PowerShell policy, use the explicit `.venv\Scripts\python.exe -m ...` commands above.

## macOS / Linux Setup, Run, Test

Create and activate the virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
streamlit run app.py
```

Run tests:

```bash
pytest
```

## Sample Data

The `sample_data/` folder includes:

- `godot_sample.csv`: small clean sample.
- `broken_sample.csv`: demo file with missing translations, placeholder mismatch, duplicate key, long target text, unchanged target text, whitespace, line break mismatch, punctuation drift, and invalid key.
- `sample.json`: flat JSON localization dictionary.

The app also has a one-click **Load Demo Sample** button.

## Troubleshooting

### `streamlit` is not recognized

Your virtual environment is probably not activated, or dependencies are not installed.

Use:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Or install dependencies first:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### `pytest` is not recognized

Run pytest through the virtual environment:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

### Virtual environment not activated

Activation is optional on Windows if you use explicit commands:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
.\.venv\Scripts\python.exe -m pytest
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

### Windows PowerShell command usage

PowerShell uses `.\` for local executables. Use:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py
```

Do not use Unix-style `source .venv/bin/activate` in PowerShell.

### Missing dependencies

Install requirements from the project root:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

macOS/Linux:

```bash
pip install -r requirements.txt
```

### Wrong working directory

Run commands from the repository root, the folder that contains `app.py`, `requirements.txt`, and `README.md`.

Check your current folder:

```powershell
Get-Location
```

Then move into the project:

```powershell
cd path\to\LocaLint
```

## Current Limitations

- No translation generation.
- No AI API usage.
- No login, payments, database, telemetry, analytics, or cloud upload.
- No native Godot, Unity, or Unreal plugin integration yet.
- No batch ZIP upload yet.
- No glossary consistency checks yet.
- No screenshot-based UI overflow prediction yet.

## Roadmap

Possible future work:

- Batch ZIP upload.
- `.po` support.
- Godot plugin.
- Unity editor extension.
- Unreal localization workflow support.
- Glossary consistency.
- Steam store localization checker.
- Screenshot text overflow prediction.

## Development

Run tests before release:

```powershell
.\.venv\Scripts\python.exe -m pytest
```

Repository:

https://github.com/bsagir61/LocaLint

## License

MIT License
