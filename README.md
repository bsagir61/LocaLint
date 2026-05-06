# LocaLint

**Catch broken game localization files before your players do.**

LocaLint is a local Streamlit web app for indie game developers shipping Godot, Unity, Steam, or itch.io localization files. Upload a CSV or JSON table, choose your source language, and get a clear QA report for missing translations, broken placeholders, duplicate keys, UI overflow risks, suspicious unchanged strings, whitespace issues, and punctuation or line break drift.

## Why Indie Game Developers Need It

Localization bugs are easy to miss because they often hide in data files instead of code. A single missing `{count}`, duplicate key, or oversized button label can break a quest screen, store page, HUD, or release build. LocaLint gives small teams a quick pre-release check without auth, a database, paid APIs, or cloud upload.

## Features

- CSV localization tables with a `key` column and locale columns.
- JSON flat dictionaries shaped like `{"KEY": {"en": "...", "tr": "..."}}`.
- Automatic language detection.
- Source language selector, defaulting to `en` when present.
- Toggleable QA checks.
- Severity filters, locale filters, and key search.
- Report downloads as CSV and Markdown.
- Cleaned summary downloads as Markdown or HTML.
- Built-in broken sample file for demos.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
streamlit run app.py
```

Then open the local Streamlit URL shown in your terminal.

## Test

```bash
pytest
```

## Sample Data

The `sample_data/` folder includes:

- `godot_sample.csv`: a small clean Godot-style CSV.
- `broken_sample.csv`: a demo file with missing translations, placeholder mismatch, duplicate keys, long target text, untranslated target text, whitespace, line break mismatch, punctuation drift, and an invalid key.
- `sample.json`: a flat JSON localization dictionary.

## Example Screenshot Description

Overview tab: summary metric cards show total keys, detected languages, total issues, severity counts, and a 0-100 health score.

Issues tab: a color-coded table highlights CRITICAL rows in red, WARNING rows in orange, and INFO rows in blue, with filters for severity, locale, and key search.

Export tab: download buttons generate CSV, Markdown, and HTML summaries for sharing with a translator or developer.

Sell This MVP tab: includes simple pricing tiers and outreach templates for Godot, Unity, and Steam/itch.io indie developers.

## MVP Limitations

- `.po` parsing is intentionally left as a TODO placeholder.
- No batch ZIP upload yet.
- No glossary or terminology consistency checks.
- No screenshot-based text overflow prediction.
- No login, database, payments, or AI API.
- CSV parser assumes the first column or `key` column contains localization keys.

## Monetization Plan

- Free: up to 100 rows.
- Indie: $9 one-time report.
- Pro: $29 lifetime small studio license.
- Agency: $19/month for batch reports.

The fastest validation path is to offer free checks to Godot and Unity developers who are close to release, then sell a downloadable report or small studio license after the report proves useful.

## Next Features

- Batch ZIP upload.
- Godot plugin.
- Unity editor extension.
- Glossary consistency.
- Steam store localization checker.
- Screenshots text overflow prediction.
