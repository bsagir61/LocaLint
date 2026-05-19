from __future__ import annotations

import html as html_lib
from pathlib import Path

import pandas as pd
import streamlit as st

from localint.checks import CHECKS, run_checks
from localint.parsers import ParserError, parse_upload, table_to_frame
from localint.report import (
    issues_to_dataframe,
    report_to_markdown,
    summarize,
    summary_to_html,
    summary_to_markdown,
)


ROOT = Path(__file__).parent
SAMPLE_PATH = ROOT / "sample_data" / "broken_sample.csv"
REPOSITORY_URL = "https://github.com/bsagir61/LocaLint"

SEVERITY_ORDER = {"CRITICAL": 0, "WARNING": 1, "INFO": 2}
SEVERITY_META = {
    "CRITICAL": {"class": "critical", "label": "CRITICAL", "hint": "Can break runtime strings or ship missing text."},
    "WARNING": {"class": "warning", "label": "WARNING", "hint": "Likely quality or layout issue. Review before release."},
    "INFO": {"class": "info", "label": "INFO", "hint": "Low-risk cleanup or consistency note."},
}
CHECK_EXPLANATIONS = {
    "Missing translation": "A target locale is blank, so players may see empty UI or fallback text.",
    "Placeholder mismatch": "Variables, printf tokens, or markup differ from the source and may break runtime formatting.",
    "Duplicate keys": "The same key appears more than once, making the loaded translation ambiguous.",
    "Empty or invalid keys": "Keys should be stable identifiers without spaces so engines and tools can resolve them safely.",
    "Suspicious untranslated text": "The target equals the source and does not look like a brand, URL, number, or code token.",
    "Length expansion risk": "The target text is much longer than the source and may overflow UI labels/buttons.",
    "Line break mismatch": "The target changed the number of line breaks, which can alter layout.",
    "Leading/trailing whitespace": "Extra spaces around text often create subtle UI alignment bugs.",
    "Punctuation mismatch": "Prompt or emphasis punctuation changed at the end of the string.",
    "CSV encoding/BOM warning": "UTF-8 BOM can trip up Godot CSV localization imports in some workflows.",
}


st.set_page_config(page_title="LocaLint", page_icon="LC", layout="wide")

st.markdown(
    """
    <style>
      .block-container { padding-top: 1.75rem; }
      .loca-header {
        overflow: visible;
        margin: 0 0 .85rem;
        padding: .1rem 0 .15rem;
      }
      .loca-title {
        display: block;
        overflow: visible;
        font-size: 2.55rem;
        line-height: 1.18;
        font-weight: 850;
        margin: 0 0 .1rem;
        padding: .05rem 0 .1rem;
        letter-spacing: 0;
      }
      .loca-subtitle { color: #9aa4af; font-size: 1.08rem; line-height: 1.35; margin: 0 0 .55rem; }
      .loca-hero-line { font-size: 1.25rem; line-height: 1.35; font-weight: 720; margin: .35rem 0 0; }
      .hero-strip {
        border: 1px solid rgba(125, 133, 144, .18);
        border-radius: 8px;
        padding: 16px 18px;
        background: rgba(125, 133, 144, .08);
        margin: 12px 0 18px;
      }
      div[data-testid="stMetric"] {
        background: rgba(125, 133, 144, .10);
        border: 1px solid rgba(125, 133, 144, .18);
        border-radius: 8px;
        padding: 14px 16px;
      }
      .severity-badge {
        display: inline-flex;
        align-items: center;
        border-radius: 999px;
        padding: 3px 9px;
        font-size: .76rem;
        line-height: 1.2;
        font-weight: 800;
        letter-spacing: 0;
      }
      .severity-badge.critical { background: rgba(255, 82, 82, .18); color: #ff8a8a; border: 1px solid rgba(255, 82, 82, .35); }
      .severity-badge.warning { background: rgba(247, 185, 85, .18); color: #ffd27a; border: 1px solid rgba(247, 185, 85, .35); }
      .severity-badge.info { background: rgba(119, 167, 255, .16); color: #9fc0ff; border: 1px solid rgba(119, 167, 255, .32); }
      .issue-card {
        border: 1px solid rgba(125, 133, 144, .18);
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 10px;
        background: rgba(22, 27, 34, .28);
      }
      .issue-title { font-weight: 780; margin-left: 8px; }
      .issue-meta { color: #9aa4af; font-size: .86rem; margin-top: 6px; }
      .issue-text { margin-top: 9px; }
      .muted { color: #9aa4af; }
      .trust-note { font-size: .92rem; line-height: 1.45; color: #c7d0d9; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="loca-header">
      <div class="loca-title">LocaLint</div>
      <div class="loca-subtitle">CSV/JSON localization QA before release.</div>
      <div class="loca-hero-line">Catch broken localization files before they reach a build.</div>
    </div>
    """,
    unsafe_allow_html=True,
)

if "load_demo_sample" not in st.session_state:
    st.session_state.load_demo_sample = False

with st.sidebar:
    st.header("QA Setup")
    st.markdown(
        """
        <div class="trust-note">
        <strong>CSV/JSON localization QA</strong><br>
        Runs locally. No cloud upload. No login.<br>
        Standalone tool, not a Godot plugin yet.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.link_button("GitHub repository", REPOSITORY_URL, use_container_width=True)
    st.divider()
    upload = st.file_uploader("Upload CSV or JSON", type=["csv", "json"])
    if st.button("Load Demo Sample", use_container_width=True, type="primary"):
        st.session_state.load_demo_sample = True
    if upload is not None:
        st.session_state.load_demo_sample = False

    st.divider()
    st.caption("Checks")
    enabled_checks = []
    for check_id, label in CHECKS.items():
        if st.toggle(label, value=True, key=f"check_{check_id}"):
            enabled_checks.append(check_id)

    length_warning_ratio = st.slider(
        "Length warning ratio",
        min_value=1.2,
        max_value=2.5,
        value=1.8,
        step=0.1,
        help="Warn when a target string is this many times longer than the source.",
    )


def load_input() -> tuple[str, bytes] | None:
    if upload is not None:
        return upload.name, upload.getvalue()
    if st.session_state.load_demo_sample and SAMPLE_PATH.exists():
        return SAMPLE_PATH.name, SAMPLE_PATH.read_bytes()
    return None


loaded = load_input()
if loaded is None:
    st.markdown(
        """
        <div class="hero-strip">
          <strong>Start with a real file or the demo sample.</strong><br>
          <span class="muted">LocaLint checks CSV/JSON localization tables locally. No login, no cloud upload, no AI API.</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button("Load Demo Sample", type="primary"):
        st.session_state.load_demo_sample = True
        st.rerun()
    st.info("Or upload a localization CSV/JSON file from the sidebar.")
    st.stop()

filename, data = loaded
try:
    table = parse_upload(filename, data)
except ParserError as exc:
    st.error(str(exc))
    st.info("Tip: use a CSV with a key column and at least one language column, or a JSON object shaped like {'KEY': {'en': 'Text'}}.")
    st.stop()

if not table.languages:
    st.error("No language columns were detected. Add at least one locale column such as en, tr, or es.")
    st.stop()

default_source_index = table.languages.index("en") if "en" in table.languages else 0
with st.sidebar:
    source_language = st.selectbox("Source language", options=table.languages, index=default_source_index)

if source_language not in table.languages:
    st.error(f"Source language '{source_language}' was not found in this file.")
    st.stop()

target_languages = table.target_languages(source_language)
if not target_languages:
    st.warning("No target languages are available for this source language. Add another locale column to run target QA checks.")

all_translation_values = [value for row in table.rows for value in row.translations.values()]
if all_translation_values and all(not value.strip() for value in all_translation_values):
    st.warning("All translation cells appear to be empty. LocaLint can still preview the file, but there is no text to QA yet.")

issues = run_checks(
    table,
    source_language=source_language,
    enabled_checks=enabled_checks,
    length_warning_ratio=length_warning_ratio,
)
summary = summarize(table, issues, source_language)
issues_frame = issues_to_dataframe(issues)
preview_frame = table_to_frame(table)


def esc(value: object) -> str:
    return html_lib.escape(str(value or ""))

overview_tab, issues_tab, preview_tab, export_tab, validation_tab = st.tabs(
    ["Overview", "Issues", "File Preview", "Export", "Validation Notes"]
)

with overview_tab:
    st.subheader("Overview")
    st.markdown(
        """
        <div class="hero-strip">
          This report prioritizes release-risk issues first: missing strings, broken variables, duplicate keys, then layout and cleanup risks.
        </div>
        """,
        unsafe_allow_html=True,
    )
    metric_cols = st.columns(7)
    metric_cols[0].metric("Total keys", summary["total_keys"])
    metric_cols[1].metric("Languages", len(summary["languages_detected"]))
    metric_cols[2].metric("Total issues", summary["total_issues"])
    metric_cols[3].metric("Critical", summary["critical_issues"])
    metric_cols[4].metric("Warning", summary["warning_issues"])
    metric_cols[5].metric("Info", summary["info_issues"])
    metric_cols[6].metric("Health", f"{summary['health_score']}/100")

    st.progress(int(summary["health_score"]) / 100)
    st.write(f"**Source file:** `{filename}`")
    st.write(f"**Detected languages:** {', '.join(table.languages)}")
    st.write(f"**Target languages:** {', '.join(target_languages) or 'None'}")

    if summary["critical_issues"]:
        st.error("Critical localization issues need attention before release.")
        st.write(
            "**What this means:** the file has at least one issue that can produce missing text, broken variables, or ambiguous keys in-game. Fix these before recording a release build."
        )
    elif summary["warning_issues"]:
        st.warning("No critical issues found, but warnings should be reviewed.")
        st.write(
            "**What this means:** the file is probably loadable, but some strings may look unfinished, overflow UI, or behave differently from the source."
        )
    else:
        st.success("No critical or warning issues found.")
        st.write("**What this means:** the selected checks did not find release-blocking localization problems.")

    st.subheader("Next Fixes")
    if not issues:
        st.write("No fixes needed for the selected checks.")
    else:
        top_issues = sorted(issues, key=lambda issue: (SEVERITY_ORDER[issue.severity.value], issue.key, issue.locale))[:5]
        for index, issue in enumerate(top_issues, start=1):
            meta = SEVERITY_META[issue.severity.value]
            locale_suffix = f"({esc(issue.locale)})" if issue.locale else ""
            st.markdown(
                f"""
                <div class="issue-card">
                  <span class="severity-badge {meta['class']}">{meta['label']}</span>
                  <span class="issue-title">{index}. {esc(issue.key)} {locale_suffix}</span>
                  <div class="issue-meta">{esc(issue.check)}</div>
                  <div class="issue-text">{esc(issue.message)}<br><span class="muted">{esc(issue.suggestion)}</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )

with issues_tab:
    st.subheader("Issues")
    with st.expander("Issue Type Guide", expanded=False):
        guide_records = [{"Issue type": label, "Why it matters": CHECK_EXPLANATIONS.get(label, "")} for label in CHECKS.values()]
        st.dataframe(pd.DataFrame(guide_records), use_container_width=True, hide_index=True)

    if issues_frame.empty:
        st.success("No issues found for the selected checks.")
    else:
        filters = st.columns([1, 1, 2])
        severity_options = sorted(issues_frame["severity"].dropna().unique().tolist())
        locale_options = sorted(locale for locale in issues_frame["locale"].dropna().unique().tolist() if locale)
        selected_severities = filters[0].multiselect("Severity", severity_options, default=severity_options)
        selected_locales = filters[1].multiselect("Locale", locale_options, default=locale_options)
        key_search = filters[2].text_input("Search by key")

        filtered = issues_frame.copy()
        if selected_severities:
            filtered = filtered[filtered["severity"].isin(selected_severities)]
        if selected_locales:
            filtered = filtered[(filtered["locale"].isin(selected_locales)) | (filtered["locale"] == "")]
        if key_search:
            filtered = filtered[filtered["key"].str.contains(key_search, case=False, na=False, regex=False)]

        st.caption(f"Showing {len(filtered)} of {len(issues_frame)} issues.")

        sorted_filtered = filtered.assign(
            severity_order=filtered["severity"].map(SEVERITY_ORDER).fillna(9),
            locale_sort=filtered["locale"].fillna(""),
        ).sort_values(["severity_order", "key", "locale_sort", "check"])

        def color_severity(row: pd.Series) -> list[str]:
            color = {
                "CRITICAL": "background-color: rgba(255, 80, 80, .22); color: #ffd6d6; font-weight: 800;",
                "WARNING": "background-color: rgba(247, 185, 85, .22); color: #ffe7b3; font-weight: 800;",
                "INFO": "background-color: rgba(119, 167, 255, .18); color: #d8e5ff; font-weight: 800;",
            }.get(row["severity"], "")
            return [color if column == "severity" else "" for column in row.index]

        readable_columns = ["severity", "key", "locale", "check", "message", "suggestion", "source_text", "target_text"]
        st.dataframe(
            sorted_filtered[readable_columns].style.apply(color_severity, axis=1),
            use_container_width=True,
            hide_index=True,
            column_config={
                "severity": st.column_config.TextColumn("Severity", width="small"),
                "key": st.column_config.TextColumn("Key", width="medium"),
                "locale": st.column_config.TextColumn("Locale", width="small"),
                "check": st.column_config.TextColumn("Check", width="medium"),
                "message": st.column_config.TextColumn("Message", width="large"),
                "suggestion": st.column_config.TextColumn("Suggestion", width="large"),
                "source_text": st.column_config.TextColumn("Source", width="medium"),
                "target_text": st.column_config.TextColumn("Target", width="medium"),
            },
        )

        st.subheader("Issue Cards")
        for _, row in sorted_filtered.head(25).iterrows():
            meta = SEVERITY_META.get(row["severity"], SEVERITY_META["INFO"])
            locale_label = f" / {esc(row['locale'])}" if row["locale"] else ""
            st.markdown(
                f"""
                <div class="issue-card">
                  <span class="severity-badge {meta['class']}">{meta['label']}</span>
                  <span class="issue-title">{esc(row['key'])}{locale_label}</span>
                  <div class="issue-meta">{esc(row['check'])} - {esc(meta['hint'])}</div>
                  <div class="issue-text">{esc(row['message'])}<br><span class="muted">{esc(row['suggestion'])}</span></div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        if len(sorted_filtered) > 25:
            st.caption("Showing the first 25 issue cards. Use the table above for the full filtered set.")

with preview_tab:
    st.subheader("File Preview")
    st.dataframe(preview_frame, use_container_width=True, hide_index=True)

with export_tab:
    st.subheader("Exports")
    st.caption("Export the current QA result for a teammate, translator, or release checklist.")
    report_csv = issues_frame.to_csv(index=False).encode("utf-8")
    report_md = report_to_markdown(table, issues, source_language).encode("utf-8")
    summary_md = summary_to_markdown(table, issues, source_language).encode("utf-8")
    summary_html = summary_to_html(table, issues, source_language).encode("utf-8")

    col_a, col_b, col_c = st.columns(3)
    col_a.download_button("Download report CSV", report_csv, "localint_report.csv", "text/csv")
    col_b.download_button("Download report Markdown", report_md, "localint_report.md", "text/markdown")
    col_c.download_button("Download summary HTML", summary_html, "localint_summary.html", "text/html")
    st.download_button("Download summary Markdown", summary_md, "localint_summary.md", "text/markdown")

with validation_tab:
    st.subheader("Who this is for")
    st.markdown(
        """
- Developers working with CSV/JSON localization files
- Indie developers and small teams
- Teams using spreadsheet-style localization workflows
- Translators or teammates reviewing localization tables
- Developers who want a local pre-release QA pass

LocaLint is not a native Godot, Unity, or Unreal plugin yet. Current support means exported CSV/JSON localization files.
        """
    )

    st.subheader("What to validate")
    st.markdown(
        """
- Did LocaLint catch an issue you would have missed manually?
- Is the report clear enough to send to a translator or teammate?
- Are the severity levels useful?
- Is the CLI useful for your workflow?
- Which file format matters most next: `.po`, more CSV variants, or something else?
- Would batch checking multiple files save time?
- Would glossary consistency checks be useful?
- Would this be better as a CLI-first tool, a web UI, or both?
        """
    )

    st.subheader("Current positioning")
    st.markdown(
        """
LocaLint is a local-first QA tool for CSV/JSON localization files.

It does not translate text. It does not use AI. It does not upload files. It checks existing localization files for release-risk issues.
        """
    )

    st.subheader("Future directions")
    st.markdown(
        """
- `.po` support
- Batch reports
- Glossary consistency checks
- Engine-specific presets
- GitHub Actions / CI example
- Public hosted demo
- Native plugins later, only if there is real demand
        """
    )

    st.subheader("Feedback")
    st.write(
        "If you use localization files in a real project, the most useful feedback is where the current checks fail, which formats are missing, and whether the report helps before release."
    )
