@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\pythonw.exe" (
    ".venv\Scripts\pythonw.exe" desktop.py
) else if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" desktop.py
) else (
    echo [경고] .venv를 찾을 수 없습니다. python install.py 를 먼저 실행하세요.
    pause
)
