@echo off
cd /d "%~dp0"

if exist ".venv\Scripts\pythonw.exe" (
    ".venv\Scripts\pythonw.exe" desktop.py
) else if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" desktop.py
) else (
    set "MSG=[Warning] .venv not found. Please run: python install.py"
    if "%QUICKDL_LANG%"=="ko" set "MSG=[경고] .venv를 찾을 수 없습니다. python install.py 를 먼저 실행하세요."
    if "%QUICKDL_LANG%"=="ja" set "MSG=[警告] .venvが見つかりません。python install.pyを実行してください。"
    if "%QUICKDL_LANG%"=="zh-TW" set "MSG=[警告] 找不到 .venv，請先執行：python install.py"
    if "%QUICKDL_LANG%"=="zh-CN" set "MSG=[警告] 找不到 .venv，请先运行：python install.py"
    if "%QUICKDL_LANG%"=="de" set "MSG=[Warnung] .venv nicht gefunden. Bitte zuerst ausfuehren: python install.py"
    if "%QUICKDL_LANG%"=="es" set "MSG=[Advertencia] No se encontro .venv. Ejecute primero: python install.py"
    if "%QUICKDL_LANG%"=="fr" set "MSG=[Avertissement] .venv introuvable. Veuillez d'abord executer : python install.py"
    if "%QUICKDL_LANG%"=="pt" set "MSG=[Aviso] .venv nao encontrado. Execute primeiro: python install.py"
    if "%QUICKDL_LANG%"=="vi" set "MSG=[Canh bao] Khong tim thay .venv. Hay chay truoc: python install.py"
    echo %MSG%
    pause
)
