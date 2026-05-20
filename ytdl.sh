#!/usr/bin/env bash
set -e
DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$DIR"

if [ -f ".venv/bin/python" ]; then
    ".venv/bin/python" desktop.py
else
    echo "[경고] .venv를 찾을 수 없습니다. python install.py 를 먼저 실행하세요."
    exit 1
fi
