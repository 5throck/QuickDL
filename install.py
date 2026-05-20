#!/usr/bin/env python3
"""QuickDL 설치 스크립트 — Windows / macOS / Linux 공통"""
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
VENV = ROOT / ".venv"
SYSTEM = platform.system()  # "Windows" | "Darwin" | "Linux"


def run(cmd, **kwargs):
    print(f"  $ {' '.join(str(c) for c in cmd)}")
    subprocess.run(cmd, check=True, **kwargs)


def python_in_venv():
    if SYSTEM == "Windows":
        return VENV / "Scripts" / "python.exe"
    return VENV / "bin" / "python"



def check_python_version():
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 이상이 필요합니다.")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} 감지됨")


def check_ffmpeg():
    if shutil.which("ffmpeg"):
        print("✅ ffmpeg 감지됨")
    else:
        print("⚠️  ffmpeg가 설치되지 않았습니다. 고화질 MP4 병합이 제한될 수 있습니다.")
        if SYSTEM == "Windows":
            print("   설치: https://ffmpeg.org/download.html 또는 'winget install ffmpeg'")
        elif SYSTEM == "Darwin":
            print("   설치: brew install ffmpeg")
        else:
            print("   설치: sudo apt install ffmpeg  (또는 배포판 패키지 매니저)")


def create_venv():
    py = python_in_venv()
    if VENV.exists():
        if py.exists():
            print(f"✅ 가상환경 이미 존재: {VENV}")
            return
        print(f"⚠️  가상환경이 손상됨. 재생성 중: {VENV}")
        shutil.rmtree(VENV)
    print(f"📦 가상환경 생성 중: {VENV}")
    run([sys.executable, "-m", "venv", str(VENV)])


def install_packages():
    print("📦 패키지 설치 중...")
    py = str(python_in_venv())
    run([py, "-m", "pip", "install", "--upgrade", "pip"])
    run([py, "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")])
    print("✅ 패키지 설치 완료")


def set_env_windows():
    """Windows: PYTHONIOENCODING을 사용자 환경변수로 설정 (UTF-8 콘솔 출력)."""
    current = os.environ.get("PYTHONIOENCODING", "")
    if current.lower() == "utf-8":
        print("✅ PYTHONIOENCODING=utf-8 이미 설정됨")
        return
    run(["setx", "PYTHONIOENCODING", "utf-8"])
    print("✅ PYTHONIOENCODING=utf-8 설정됨 (재로그인 후 적용)")


def set_env_unix():
    """macOS/Linux: ~/.bashrc 또는 ~/.zshrc에 PYTHONIOENCODING 추가."""
    shell_rc = Path.home() / (".zshrc" if SYSTEM == "Darwin" else ".bashrc")
    line = 'export PYTHONIOENCODING=utf-8\n'
    content = shell_rc.read_text(encoding="utf-8", errors="replace") if shell_rc.exists() else ""
    if "PYTHONIOENCODING" in content:
        print("✅ PYTHONIOENCODING 이미 설정됨")
        return
    with open(shell_rc, "a", encoding="utf-8") as f:
        f.write(f"\n# QuickDL\n{line}")
    print(f"✅ PYTHONIOENCODING=utf-8 → {shell_rc} 에 추가됨")
    print(f"   적용: source {shell_rc}")


def set_environment():
    print("🔧 환경변수 설정 중...")
    if SYSTEM == "Windows":
        set_env_windows()
    else:
        set_env_unix()


def print_done():
    if SYSTEM == "Windows":
        run_cmd = "ytdl.bat  (더블클릭) 또는  python desktop.py"
        cli_cmd = "python cli.py <URL>"
    else:
        run_cmd = "./ytdl.sh  또는  python desktop.py"
        cli_cmd = "python cli.py <URL>"
    print()
    print("=" * 50)
    print("🎉 QuickDL 설치 완료!")
    print(f"   데스크톱 앱: {run_cmd}")
    print(f"   CLI:         {cli_cmd}")
    print("=" * 50)


if __name__ == "__main__":
    print("🚀 QuickDL 설치를 시작합니다...")
    print(f"   OS: {SYSTEM} / Python: {sys.version.split()[0]}")
    check_python_version()
    check_ffmpeg()
    create_venv()
    install_packages()
    set_environment()
    print_done()
