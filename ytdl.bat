@echo off
REM One-click desktop launcher (Windows) — pairs with ytdl.sh (macOS/Linux).
REM Uses goto labels (not parenthesized blocks) so %MSG% set inside the branch
REM is expanded after the set, and setlocal keeps MSG out of the caller shell.
setlocal
chcp 65001 >nul
cd /d "%~dp0"

if exist ".venv\Scripts\pythonw.exe" (
    ".venv\Scripts\pythonw.exe" src\desktop.py
    goto :end
)
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" src\desktop.py
    goto :end
)

set "MSG=[Warning] .venv not found. Please run: python src\install.py"
if /i "%QUICKDL_LANG%"=="ko" set "MSG=[경고] .venv를 찾을 수 없습니다. python src\install.py 를 먼저 실행하세요."
if /i "%QUICKDL_LANG%"=="ja" set "MSG=[警告] .venvが見つかりません。python src\install.pyを実行してください。"
if /i "%QUICKDL_LANG%"=="zh-TW" set "MSG=[警告] 找不到 .venv，請先執行：python src\install.py"
if /i "%QUICKDL_LANG%"=="zh-CN" set "MSG=[警告] 找不到 .venv，请先运行：python src\install.py"
if /i "%QUICKDL_LANG%"=="de" set "MSG=[Warnung] .venv nicht gefunden. Bitte zuerst ausfuehren: python src\install.py"
if /i "%QUICKDL_LANG%"=="es" set "MSG=[Advertencia] No se encontro .venv. Ejecute primero: python src\install.py"
if /i "%QUICKDL_LANG%"=="fr" set "MSG=[Avertissement] .venv introuvable. Veuillez d'abord executer : python src\install.py"
if /i "%QUICKDL_LANG%"=="pt" set "MSG=[Aviso] .venv nao encontrado. Execute primeiro: python src\install.py"
if /i "%QUICKDL_LANG%"=="vi" set "MSG=[Canh bao] Khong tim thay .venv. Hay chay truoc: python src\install.py"
if /i "%QUICKDL_LANG%"=="ms" set "MSG=[Amaran] .venv tidak dijumpai. Sila jalankan dahulu: python src\install.py"
if /i "%QUICKDL_LANG%"=="id" set "MSG=[Peringatan] .venv tidak ditemukan. Jalankan terlebih dahulu: python src\install.py"
if /i "%QUICKDL_LANG%"=="th" set "MSG=[Warning-TH] .venv not found. Run: python src\install.py"
if /i "%QUICKDL_LANG%"=="ru" set "MSG=[Warning-RU] .venv not found. Run: python src\install.py"
if /i "%QUICKDL_LANG%"=="it" set "MSG=[Avviso] .venv non trovato. Eseguire prima: python src\install.py"
if /i "%QUICKDL_LANG%"=="ar" set "MSG=[Warning-AR] .venv not found. Run: python src\install.py"

echo %MSG%
pause
exit /b 1

:end
endlocal
