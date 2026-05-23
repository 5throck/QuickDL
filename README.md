# QuickDL

A lightweight YouTube video downloader with a desktop app, system tray, web UI, and CLI.

![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)
![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)
![CI](https://github.com/5throck/QuickDL/actions/workflows/ci.yml/badge.svg)

[한국어 문서 보기](README_ko.md)

---

## Features

- **Desktop App** — Double-click to launch. No terminal needed.
- **System Tray** — Quick access tray icon for managing the app.
- **Web UI** — Full browser interface with real-time download queue and progress.
- **CLI** — `python cli.py <URL>` for quick terminal downloads.
- **Best Quality** — Automatically merges best video + audio into MP4 (requires ffmpeg).
- **Dark / Light Mode** — Follows your OS theme.
- **Download Queue** — Start multiple downloads simultaneously; track progress per item.
- **16 Languages** — Auto-detects OS locale (en, ko, ja, zh-TW, zh-CN, de, es, fr, pt, vi, ms, id, th, ru, it, ar).
- **Cross-Platform** — Windows, macOS, Linux.

---

## Requirements

- Python 3.8+
- ffmpeg (required for high-quality video/audio merging)
  - Windows: `winget install ffmpeg` or https://ffmpeg.org/download.html
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`

---

## Installation

```bash
git clone https://github.com/5throck/QuickDL.git
cd QuickDL
python install.py
```

`install.py` automatically:
- Verifies Python version (3.8+)
- Creates a virtual environment (`.venv/`)
- Installs all dependencies from `requirements.txt`
- Installs `ffmpeg` via package manager (winget, brew, apt) if missing
- Sets required environment variables (`PYTHONIOENCODING=utf-8`)

---

## Usage

### Desktop App (recommended)

**Windows** — double-click `ytdl.bat`

**macOS / Linux:**
```bash
chmod +x ytdl.sh
./ytdl.sh
```

Or run directly:
```bash
python desktop.py
```

The app opens a window with the full web UI and adds a tray icon.  
Closing the window will completely exit the application. You can also quit via the tray icon.

### Web UI (browser)

```bash
python app.py
# Open http://localhost:5000
```

Paste a YouTube URL, click **Download**, and watch the real-time progress queue.  
When complete, a download link appears — click to save the file.

### CLI

```bash
# Basic download (saved to ./downloads/)
python cli.py <YouTube URL>

# Custom output folder
python cli.py <YouTube URL> --output /path/to/folder

# Force a specific language
QUICKDL_LANG=ko python cli.py <URL>   # macOS/Linux
set QUICKDL_LANG=ko && python cli.py <URL>  # Windows
```

---

## Project Structure

```
QuickDL/
├── app.py                  # Flask server — routes, job queue, file serving
├── download_service.py     # yt-dlp wrapper (get_video_info, download_video)
├── desktop.py              # Desktop entry point (pywebview + pystray)
├── cli.py                  # CLI entry point (argparse)
├── install.py              # Cross-platform installer
├── i18n.py                 # i18n: init(), t(), get_all(), format_duration()
├── requirements.txt        # Python dependencies
├── ytdl.bat                # Windows one-click launcher
├── ytdl.sh                 # macOS/Linux one-click launcher
├── locales/                # 16 flat JSON translation files (en.json is baseline)
├── templates/index.html    # Web UI (Jinja2)
├── static/
│   ├── css/styles.css      # UI styles (dark + light, responsive)
│   └── js/script.js        # Frontend JS (fetch, queue, polling)
├── tests/
│   ├── test_app.py         # Flask API tests (9 tests — unittest)
│   ├── test_i18n.py        # i18n tests (14 tests — pytest)
│   └── test_env.py         # Dependency check
├── scripts/
│   ├── audit.sh / audit.ps1        # Quality gate
│   └── dev-sync.sh / dev-sync.ps1  # PR pipeline
└── docs/context.md         # Project context for AI tools
```

---

## Running Tests

```bash
pytest tests/ -v        # All 23 tests
bash scripts/audit.sh   # Quality gate (CHANGELOG, i18n parity, broken links)
```

---

## License

This project is licensed under the [GNU Affero General Public License v3.0](LICENSE).


## 🤖 Multi-Agent Kickoff (Recommended)
Before writing any code or beginning a new major feature, ask the AI to start a PM-led kickoff meeting:
> *"Let's start the PM agent kickoff meeting for this project."*
This will trigger the Phase 0 Dynamic Team Assembly process to align roles and skills.
