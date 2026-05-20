#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

if [ -f ".venv/bin/python" ]; then
    ".venv/bin/python" desktop.py
else
    case "${QUICKDL_LANG:-en}" in
        ko)    MSG="[경고] .venv를 찾을 수 없습니다. python install.py 를 먼저 실행하세요." ;;
        ja)    MSG="[警告] .venvが見つかりません。python install.pyを実行してください。" ;;
        zh-TW) MSG="[警告] 找不到 .venv，請先執行：python install.py" ;;
        zh-CN) MSG="[警告] 找不到 .venv，请先运行：python install.py" ;;
        de)    MSG="[Warnung] .venv nicht gefunden. Bitte zuerst ausführen: python install.py" ;;
        es)    MSG="[Advertencia] No se encontró .venv. Ejecute primero: python install.py" ;;
        fr)    MSG="[Avertissement] .venv introuvable. Veuillez d'abord exécuter : python install.py" ;;
        pt)    MSG="[Aviso] .venv não encontrado. Execute primeiro: python install.py" ;;
        vi)    MSG="[Cảnh báo] Không tìm thấy .venv. Hãy chạy trước: python install.py" ;;
        *)     MSG="[Warning] .venv not found. Please run: python install.py" ;;
    esac
    echo "$MSG"
    exit 1
fi
