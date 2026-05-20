# QuickDL Desktop App Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Flask 웹 앱을 더블클릭으로 실행 가능한 데스크톱 앱으로 전환하고, 시스템 트레이 아이콘·CLI·크로스플랫폼 설치 스크립트·문서·라이선스를 갖춘 GitHub 공개 프로젝트로 완성한다.

**Architecture:** 기존 Flask 앱(`app.py`, `download_service.py`)은 수정하지 않는다. `desktop.py`가 Flask를 백그라운드 스레드로 실행하고 pywebview 창과 pystray 트레이를 통합한다. `cli.py`는 Flask 없이 `download_service`를 직접 호출한다. `install.py`가 OS를 감지해 가상환경 생성·패키지 설치·환경변수 설정을 자동화한다.

**Tech Stack:** Python, Flask, pywebview, pystray, Pillow, argparse, gh CLI (GitHub 등록)

---

## File Map

| 파일 | 상태 | 역할 |
|------|------|------|
| `requirements.txt` | 수정 | pywebview, pystray, pillow 추가 |
| `desktop.py` | 신규 | 데스크톱 앱 진입점 |
| `cli.py` | 신규 | CLI 진입점 |
| `install.py` | 신규 | 크로스플랫폼 설치 스크립트 (OS 감지, venv, 패키지, 환경변수) |
| `ytdl.bat` | 신규 | Windows 원클릭 실행 |
| `ytdl.sh` | 신규 | macOS/Linux 원클릭 실행 |
| `README.md` | 재작성 | 영문 문서 (설치·사용법·라이선스) |
| `README_ko.md` | 신규 | 한국어 문서 |
| `LICENSE` | 신규 | AGPL-3.0 전문 |
| `.gitignore` | 신규 | Python/venv/OS 제외 목록 |
| `download_service.py` | 변경 없음 | 다운로드 로직 (재사용) |
| `app.py` | 변경 없음 | Flask 라우팅 (재사용) |

---

## Task 0: 디렉토리 이름 변경

- [ ] **Step 1: 디렉토리 rename**

  Windows 탐색기 또는 Git Bash:
  ```bash
  mv "C:/git/youtube" "C:/git/QuickDL"
  cd "C:/git/QuickDL"
  ```

- [ ] **Step 2: 확인**
  ```bash
  ls
  ```
  Expected: `app.py`, `download_service.py`, `templates/`, `static/`, `requirements.txt` 등 기존 파일 확인

---

## Task 1: requirements.txt 업데이트

- [ ] **Step 1: requirements.txt 수정**

  기존 내용에 아래 3줄 추가:
  ```
  pywebview
  pystray
  pillow
  ```

---

## Task 2: 크로스플랫폼 설치 스크립트 (`install.py`)

Python이 이미 설치된 환경에서 `python install.py` 한 번으로 venv 생성, 패키지 설치, 필요한 환경변수 설정까지 완료한다.

- [ ] **Step 1: `install.py` 작성**

  ```python
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


  def pip_in_venv():
      if SYSTEM == "Windows":
          return VENV / "Scripts" / "pip.exe"
      return VENV / "bin" / "pip"


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
      if VENV.exists():
          print(f"✅ 가상환경 이미 존재: {VENV}")
          return
      print(f"📦 가상환경 생성 중: {VENV}")
      run([sys.executable, "-m", "venv", str(VENV)])


  def install_packages():
      print("📦 패키지 설치 중...")
      run([str(pip_in_venv()), "install", "--upgrade", "pip"])
      run([str(pip_in_venv()), "install", "-r", str(ROOT / "requirements.txt")])
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
      content = shell_rc.read_text() if shell_rc.exists() else ""
      if "PYTHONIOENCODING" in content:
          print("✅ PYTHONIOENCODING 이미 설정됨")
          return
      with open(shell_rc, "a") as f:
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
  ```

- [ ] **Step 2: 수동 테스트 — Windows**

  ```bash
  python install.py
  ```

  Expected:
  - Python 버전 확인 출력
  - ffmpeg 감지 여부 출력
  - `.venv/` 폴더 생성
  - 패키지 설치 완료
  - 환경변수 설정 완료
  - 완료 메시지 출력

- [ ] **Step 3: 수동 테스트 — 재실행 시 멱등성 확인**

  ```bash
  python install.py
  ```

  Expected: "이미 존재" / "이미 설정됨" 메시지 출력, 오류 없음

---

## Task 3: 실행 스크립트 (`ytdl.bat`, `ytdl.sh`)

- [ ] **Step 1: `ytdl.bat` 작성 (Windows)**

  ```bat
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
  ```

- [ ] **Step 2: `ytdl.sh` 작성 (macOS/Linux)**

  ```bash
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
  ```

- [ ] **Step 3: `ytdl.sh` 실행 권한 부여**

  ```bash
  chmod +x ytdl.sh
  ```

---

## Task 4: CLI 구현 (`cli.py`)

- [ ] **Step 1: `cli.py` 작성**

  ```python
  #!/usr/bin/env python3
  import argparse
  import os
  import sys
  from pathlib import Path

  sys.path.insert(0, str(Path(__file__).parent))
  import download_service


  def main():
      parser = argparse.ArgumentParser(description="QuickDL — YouTube 영상 다운로더")
      parser.add_argument("url", help="YouTube URL")
      parser.add_argument(
          "--output",
          default=str(Path(__file__).parent / "downloads"),
          help="저장 폴더 (기본: ./downloads)",
      )
      args = parser.parse_args()

      os.makedirs(args.output, exist_ok=True)

      print("📥 영상 정보 조회 중...")
      try:
          info = download_service.get_video_info(args.url)
      except Exception as e:
          print(f"❌ 오류: {e}")
          sys.exit(1)

      duration = info.get("duration", 0)
      minutes, seconds = divmod(duration, 60)
      print(f"🎬 제목: {info.get('title', '알 수 없음')} ({minutes}:{seconds:02d})")
      print(f"   채널: {info.get('channel', '알 수 없음')}")
      print("⬇️  다운로드 중...")

      try:
          saved_path = download_service.download_video(args.url, args.output)
      except Exception as e:
          print(f"❌ 다운로드 실패: {e}")
          sys.exit(1)

      if saved_path and os.path.exists(saved_path):
          print(f"✅ 저장됨: {saved_path}")
      else:
          print(f"✅ 다운로드 완료. 저장 위치: {args.output}")


  if __name__ == "__main__":
      main()
  ```

- [ ] **Step 2: 테스트**

  ```bash
  python cli.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  python cli.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --output C:\Temp\test_dl
  python cli.py "not-a-url"   # 오류 메시지 확인
  ```

---

## Task 5: 데스크톱 앱 구현 (`desktop.py`)

- [ ] **Step 1: `desktop.py` 작성**

  ```python
  import queue
  import socket
  import sys
  import threading
  import time
  from pathlib import Path

  import webview
  from PIL import Image, ImageDraw
  import pystray

  sys.path.insert(0, str(Path(__file__).parent))
  from app import app as flask_app

  APP_NAME = "QuickDL"


  def find_free_port(preferred=5000):
      for port in [preferred]:
          try:
              with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                  s.bind(("127.0.0.1", port))
                  return port
          except OSError:
              pass
      with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
          s.bind(("127.0.0.1", 0))
          return s.getsockname()[1]


  def wait_for_server(port, timeout=5.0):
      deadline = time.time() + timeout
      while time.time() < deadline:
          try:
              with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                  return True
          except OSError:
              time.sleep(0.1)
      return False


  def make_tray_icon():
      img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
      draw = ImageDraw.Draw(img)
      draw.ellipse([4, 4, 124, 124], fill="#FF0000")
      draw.polygon([(48, 36), (48, 92), (96, 64)], fill="white")
      return img


  def run_flask(port):
      flask_app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False, threaded=True)


  def main():
      port = find_free_port()
      url = f"http://127.0.0.1:{port}"

      flask_thread = threading.Thread(target=run_flask, args=(port,), daemon=True)
      flask_thread.start()

      if not wait_for_server(port):
          try:
              import tkinter.messagebox as mb
              mb.showerror(APP_NAME, "서버를 시작하지 못했습니다.")
          except Exception:
              print("ERROR: 서버 시작 실패")
          sys.exit(1)

      event_queue = queue.Queue()

      def create_window():
          win = webview.create_window(
              APP_NAME, url, width=900, height=700, min_size=(600, 500)
          )
          # 창이 닫혀도 앱을 종료하지 않음 — 트레이에서 계속 접근 가능.
          # pywebview 백엔드에 따라 창만 사라지고 프로세스는 유지됨.
          # 완전 종료는 트레이 "종료" 메뉴를 통해서만 수행.
          win.events.closed += lambda: event_queue.put("closed")
          return win

      def tray_open(_icon, _item):
          event_queue.put("show")

      def tray_quit(_icon, _item):
          event_queue.put("quit")

      tray_icon = pystray.Icon(
          APP_NAME,
          make_tray_icon(),
          APP_NAME,
          menu=pystray.Menu(
              pystray.MenuItem(APP_NAME, None, enabled=False),
              pystray.Menu.SEPARATOR,
              pystray.MenuItem("창 열기", tray_open),
              pystray.MenuItem("종료", tray_quit),
          ),
      )
      threading.Thread(target=tray_icon.run, daemon=True).start()

      def poll_queue():
          while True:
              time.sleep(0.1)
              try:
                  event = event_queue.get_nowait()
              except queue.Empty:
                  continue
              if event == "show":
                  # pywebview가 poll_queue를 GUI 스레드에서 실행하므로 여기서 create_window() 호출 가능.
                  # 백엔드에 따라 threading 오류 발생 시: webview.create_window() 대신
                  # webview.windows[0].show() 를 시도하거나 pywebview 버전을 확인할 것.
                  create_window()
              elif event == "quit":
                  tray_icon.stop()
                  sys.exit(0)

      create_window()
      webview.start(poll_queue)


  if __name__ == "__main__":
      main()
  ```

- [ ] **Step 2: 테스트**

  ```bash
  python desktop.py
  ```

  확인 항목:
  1. 창이 열리고 기존 UI 표시
  2. 트레이 아이콘 등장
  3. 창 닫기 → 트레이 유지
  4. 트레이 `창 열기` → 재오픈
  5. 트레이 `종료` → 완전 종료
  6. 포트 5000 점유 상태에서 실행 → 대체 포트로 정상 동작

---

## Task 6: 라이선스 파일 (`LICENSE`)

- [ ] **Step 1: AGPL-3.0 전문 작성**

  `LICENSE` 파일에 AGPL-3.0 전문을 작성한다. 내용은 https://www.gnu.org/licenses/agpl-3.0.txt 와 동일한 표준 전문이며, 첫 줄은 아래와 같다:

  ```
  GNU AFFERO GENERAL PUBLIC LICENSE
  Version 3, 19 November 2007
  ...
  ```

  전체 전문을 `LICENSE` 파일로 저장한다 (약 660줄).

---

## Task 7: `.gitignore` 생성

- [ ] **Step 1: `.gitignore` 작성**

  ```gitignore
  # Python
  __pycache__/
  *.py[cod]
  *.pyo
  .venv/
  venv/
  env/
  dist/
  build/
  *.egg-info/

  # Downloads
  downloads/

  # OS
  .DS_Store
  Thumbs.db
  desktop.ini

  # IDE
  .vscode/
  .idea/

  # Superpowers
  .superpowers/
  ```

---

## Task 8: README 문서 작성

- [ ] **Step 1: `README.md` (영문) 작성**

  ```markdown
  # QuickDL

  A lightweight YouTube video downloader with a desktop app, system tray, and CLI.

  ![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)
  ![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)

  ## Features

  - **Desktop App** — Double-click to launch. No terminal needed.
  - **System Tray** — Minimize to tray, reopen anytime.
  - **CLI** — `python cli.py <URL>` for quick terminal downloads.
  - **Best Quality** — Automatically downloads the highest-quality MP4.
  - **Cross-Platform** — Windows, macOS, Linux.

  ## Requirements

  - Python 3.8+
  - ffmpeg (optional, required for high-quality video/audio merging)

  ## Installation

  ```bash
  git clone https://github.com/<your-username>/QuickDL.git
  cd QuickDL
  python install.py
  ```

  `install.py` will:
  - Verify Python version
  - Create a virtual environment (`.venv/`)
  - Install all dependencies
  - Set required environment variables

  ## Usage

  ### Desktop App

  **Windows:**
  ```
  Double-click ytdl.bat
  ```

  **macOS / Linux:**
  ```bash
  ./ytdl.sh
  ```

  Or directly:
  ```bash
  python desktop.py
  ```

  ### CLI

  ```bash
  python cli.py <YouTube URL>
  python cli.py <YouTube URL> --output /path/to/folder
  ```

  ### Web UI (browser)

  ```bash
  python app.py
  # Open http://localhost:5000
  ```

  ## Project Structure

  ```
  QuickDL/
  ├── app.py              # Flask web server
  ├── download_service.py # Download logic (yt-dlp)
  ├── desktop.py          # Desktop app entry point
  ├── cli.py              # CLI entry point
  ├── install.py          # Cross-platform installer
  ├── ytdl.bat            # Windows launcher
  ├── ytdl.sh             # macOS/Linux launcher
  ├── requirements.txt
  ├── templates/
  └── static/
  ```

  ## License

  This project is licensed under the [GNU Affero General Public License v3.0](LICENSE).
  ```

- [ ] **Step 2: `README_ko.md` (한국어) 작성**

  ```markdown
  # QuickDL

  데스크톱 앱, 시스템 트레이, CLI를 갖춘 경량 YouTube 영상 다운로더입니다.

  ![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)
  ![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)

  ## 주요 기능

  - **데스크톱 앱** — 더블클릭으로 실행. 터미널 불필요.
  - **시스템 트레이** — 트레이로 최소화 후 언제든 재오픈.
  - **CLI** — `python cli.py <URL>`로 빠른 터미널 다운로드.
  - **최고 화질** — 자동으로 최고 화질 MP4 다운로드.
  - **크로스플랫폼** — Windows, macOS, Linux 지원.

  ## 시스템 요구사항

  - Python 3.8 이상
  - ffmpeg (선택, 고화질 영상/오디오 병합 시 필요)

  ## 설치

  ```bash
  git clone https://github.com/<your-username>/QuickDL.git
  cd QuickDL
  python install.py
  ```

  `install.py`가 자동으로 수행하는 작업:
  - Python 버전 확인
  - 가상환경(`.venv/`) 생성
  - 의존성 패키지 설치
  - 필요한 환경변수 설정

  ## 사용법

  ### 데스크톱 앱

  **Windows:**
  ```
  ytdl.bat 더블클릭
  ```

  **macOS / Linux:**
  ```bash
  ./ytdl.sh
  ```

  또는 직접 실행:
  ```bash
  python desktop.py
  ```

  ### CLI

  ```bash
  python cli.py <YouTube URL>
  python cli.py <YouTube URL> --output /저장/경로
  ```

  ### 웹 UI (브라우저)

  ```bash
  python app.py
  # http://localhost:5000 열기
  ```

  ## 프로젝트 구조

  ```
  QuickDL/
  ├── app.py              # Flask 웹 서버
  ├── download_service.py # 다운로드 로직 (yt-dlp)
  ├── desktop.py          # 데스크톱 앱 진입점
  ├── cli.py              # CLI 진입점
  ├── install.py          # 크로스플랫폼 설치 스크립트
  ├── ytdl.bat            # Windows 실행 스크립트
  ├── ytdl.sh             # macOS/Linux 실행 스크립트
  ├── requirements.txt
  ├── templates/
  └── static/
  ```

  ## 라이선스

  이 프로젝트는 [GNU Affero General Public License v3.0](LICENSE) 라이선스를 따릅니다.
  ```

---

## Task 9: GitHub 등록

**전제조건 확인:**
```bash
gh --version       # GitHub CLI 설치 확인. 없으면 https://cli.github.com 에서 설치
gh auth status     # 로그인 상태 확인. 미인증 시: gh auth login
```

`gh` CLI (GitHub CLI)를 사용한다.

- [ ] **Step 1: git 초기화 및 첫 커밋**

  ```bash
  cd "C:/git/QuickDL"
  git init
  git add .
  git commit -m "feat: initial QuickDL release

  - Desktop app with pywebview + pystray tray icon
  - CLI via cli.py
  - Cross-platform installer (install.py)
  - Windows/macOS/Linux launchers
  - AGPL-3.0 license
  - README (EN + KO)"
  ```

- [ ] **Step 2: GitHub 원격 저장소 생성 및 push**

  ```bash
  gh repo create QuickDL \
    --public \
    --description "Lightweight YouTube downloader with desktop app, tray, and CLI" \
    --source=. \
    --remote=origin \
    --push
  ```

  Expected: 저장소 URL 출력 (예: `https://github.com/<username>/QuickDL`)

- [ ] **Step 3: GitHub에서 확인**

  출력된 URL을 브라우저에서 열어 파일·라이선스·README 표시 확인

---

## Task 10: 최종 검증

- [ ] **Step 1: 설치 스크립트 전체 흐름**

  새 터미널에서:
  ```bash
  python install.py
  ```
  Expected: venv 생성 → 패키지 설치 → 환경변수 설정 → 완료 메시지

- [ ] **Step 2: CLI 동작 확인**

  ```bash
  python cli.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  ```

- [ ] **Step 3: 데스크톱 앱 동작 확인**

  `ytdl.bat` 더블클릭 → 창 열기 → 다운로드 → 트레이 → 종료

- [ ] **Step 4: GitHub 저장소 최종 확인**

  - `README.md`, `README_ko.md`, `LICENSE` 표시 여부
  - AGPL-3.0 라이선스 뱃지 확인
