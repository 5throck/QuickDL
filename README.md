# QuickDL

A lightweight YouTube video downloader with a desktop app, system tray, and CLI.

![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)
![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)

[한국어 문서 보기](README_ko.md)

## Features

- **Desktop App** — Double-click to launch. No terminal needed.
- **System Tray** — Minimize to tray, reopen anytime.
- **CLI** — `python cli.py <URL>` for quick terminal downloads.
- **Best Quality** — Automatically downloads the highest-quality MP4.
- **Cross-Platform** — Windows, macOS, Linux.

## Requirements

- Python 3.8+
- ffmpeg (optional, required for high-quality video/audio merging)
  - Windows: `winget install ffmpeg` or https://ffmpeg.org/download.html
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`

## Installation

```bash
git clone https://github.com/5throck/QuickDL.git
cd QuickDL
python install.py
```

`install.py` automatically:
- Verifies Python version (3.8+)
- Creates a virtual environment (`.venv/`)
- Installs all dependencies
- Sets required environment variables (`PYTHONIOENCODING=utf-8`)

## Usage

### Desktop App (recommended)

**Windows** — double-click `ytdl.bat`

**macOS / Linux:**
```bash
./ytdl.sh
```

Or run directly:
```bash
python desktop.py
```

The app opens a window with the full UI and adds a tray icon.
Closing the window keeps the app running in the tray — right-click the tray icon to reopen or quit.

### CLI

```bash
# Basic download (saved to ./downloads/)
python cli.py <YouTube URL>

# Custom output folder
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
├── ytdl.bat            # Windows one-click launcher
├── ytdl.sh             # macOS/Linux one-click launcher
├── requirements.txt    # Python dependencies
├── templates/          # HTML templates
└── static/             # CSS, JS assets
```

## License

This project is licensed under the [GNU Affero General Public License v3.0](LICENSE).
