#!/usr/bin/env bash
# ytdl.sh — QuickDL launcher for macOS and Linux
# Usage: ./ytdl.sh
#        QUICKDL_LANG=ko ./ytdl.sh

set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

# ── Locate python in .venv ──────────────────────────────────────────────────
PYTHON=""
if [ -f ".venv/bin/pythonw" ]; then
    PYTHON=".venv/bin/pythonw"
elif [ -f ".venv/bin/python" ]; then
    PYTHON=".venv/bin/python"
fi

# ── Run or error ────────────────────────────────────────────────────────────
if [ -n "$PYTHON" ]; then
    exec "$PYTHON" desktop.py
else
    case "${QUICKDL_LANG:-en}" in
        ko)    MSG="[경고] .venv를 찾을 수 없습니다. python install.py 를 먼저 실행하세요." ;;
        ja)    MSG="[警告] .venvが見つかりません。python install.pyを実行してください。" ;;
        zh-TW) MSG="[警告] 找不到 .venv，請先執行：python install.py" ;;
        zh-CN) MSG="[警告] 找不到 .venv，请先运行：python install.py" ;;
        de)    MSG="[Warnung] .venv nicht gefunden. Bitte zuerst ausfuehren: python install.py" ;;
        es)    MSG="[Advertencia] No se encontro .venv. Ejecute primero: python install.py" ;;
        fr)    MSG="[Avertissement] .venv introuvable. Veuillez d abord executer : python install.py" ;;
        pt)    MSG="[Aviso] .venv nao encontrado. Execute primeiro: python install.py" ;;
        vi)    MSG="[Canh bao] Khong tim thay .venv. Hay chay truoc: python install.py" ;;
        ms)    MSG="[Amaran] .venv tidak dijumpai. Sila jalankan dahulu: python install.py" ;;
        id)    MSG="[Peringatan] .venv tidak ditemukan. Jalankan terlebih dahulu: python install.py" ;;
        th)    MSG="[Warning-TH] .venv not found. Run: python install.py" ;;
        ru)    MSG="[Warning-RU] .venv not found. Run: python install.py" ;;
        it)    MSG="[Avviso] .venv non trovato. Eseguire prima: python install.py" ;;
        ar)    MSG="[Warning-AR] .venv not found. Run: python install.py" ;;
        *)     MSG="[Warning] .venv not found. Please run: python install.py" ;;
    esac
    echo "$MSG" >&2
    exit 1
fi
