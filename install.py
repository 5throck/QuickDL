#!/usr/bin/env python3
"""QuickDL 설치 스크립트 — Windows / macOS / Linux 공통"""
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from i18n import init as i18n_init, t

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
        print(t("install.python_bad"))
        sys.exit(1)
    print(t("install.python_ok", version=sys.version.split()[0]))


def check_ffmpeg():
    if shutil.which("ffmpeg"):
        print(t("install.ffmpeg_ok"))
    else:
        print(t("install.ffmpeg_missing"))
        if SYSTEM == "Windows":
            print(t("install.ffmpeg_win"))
        elif SYSTEM == "Darwin":
            print(t("install.ffmpeg_mac"))
        else:
            print(t("install.ffmpeg_linux"))


def create_venv():
    py = python_in_venv()
    if VENV.exists():
        if py.exists():
            print(t("install.venv_exists", path=VENV))
            return
        print(t("install.venv_broken", path=VENV))
        shutil.rmtree(VENV)
    print(t("install.venv_creating", path=VENV))
    run([sys.executable, "-m", "venv", str(VENV)])


def install_packages():
    print(t("install.packages_installing"))
    py = str(python_in_venv())
    run([py, "-m", "pip", "install", "--upgrade", "pip"])
    run([py, "-m", "pip", "install", "-r", str(ROOT / "requirements.txt")])
    print(t("install.packages_done"))


def set_env_windows():
    """Windows: PYTHONIOENCODING을 사용자 환경변수로 설정 (UTF-8 콘솔 출력)."""
    current = os.environ.get("PYTHONIOENCODING", "")
    if current.lower() == "utf-8":
        print(t("install.env_already"))
        return
    run(["setx", "PYTHONIOENCODING", "utf-8"])
    print(t("install.env_set_win"))


def set_env_unix():
    """macOS/Linux: ~/.bashrc 또는 ~/.zshrc에 PYTHONIOENCODING 추가."""
    shell_rc = Path.home() / (".zshrc" if SYSTEM == "Darwin" else ".bashrc")
    line = 'export PYTHONIOENCODING=utf-8\n'
    content = shell_rc.read_text(encoding="utf-8", errors="replace") if shell_rc.exists() else ""
    if "PYTHONIOENCODING" in content:
        print(t("install.env_already"))
        return
    with open(shell_rc, "a", encoding="utf-8") as f:
        f.write(f"\n# QuickDL\n{line}")
    print(t("install.env_set_unix", rc=shell_rc))
    print(t("install.env_source", rc=shell_rc))


def set_environment():
    print(t("install.env_setting"))
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
    print(t("install.done_title"))
    print(t("install.done_desktop", cmd=run_cmd))
    print(t("install.done_cli", cmd=cli_cmd))
    print("=" * 50)


if __name__ == "__main__":
    i18n_init()
    print(t("install.start"))
    print(t("install.os_info", system=SYSTEM, version=sys.version.split()[0]))
    check_python_version()
    check_ffmpeg()
    create_venv()
    install_packages()
    set_environment()
    print_done()
