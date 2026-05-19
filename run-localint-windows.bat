@echo off
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    py -m venv .venv
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
)

echo Starting LocaLint...
".venv\Scripts\python.exe" -m streamlit run app.py

pause