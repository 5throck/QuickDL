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
- **CLI** — `python cli.py <URL>` for quick terminal downloads, with batch support.
- **Best Quality** — Automatically merges best video + audio into MP4 (requires ffmpeg).
- **Best-Available Mode** — `--quality best` probes each video, downloads the max resolution with no artificial cap, and prefers h264/aac at equal quality for browser/device compatibility.
- **Subtitle Sidecars** — `--write-subs` saves manual (or auto-generated fallback) WebVTT subtitles next to the video.
- **Caption Fallback Chain** — `--captions-langs "ko,en"` fetches BOTH requested languages per video via an honest per-language chain: manual → auto-generated → YouTube auto-translated; each sidecar is tagged `manual | auto | translated | failed` in the manifest. YouTube's translation endpoint rate-limits (429), so a robust pipeline uses the manifest to drive an external translation step for `failed` languages.
- **Caption Cleaning Pipeline** — every downloaded sidecar is automatically cleaned before being finalized: inline `<c>`/timestamp tags stripped, rolling duplicate cues merged, overlapping cue windows clipped (raw YouTube ASR grabs become clean cue files). The manifest records `cleaned: true` + the final cue count per sidecar.
- **Caption Coverage Gate** — each sidecar is measured against the video duration (`coverage` 0–1 in the manifest, null when unknown); coverage below 0.95 is a manifest warning by default, and `--require-caption-coverage` (with `--verify`) fails the download — full-coverage captions or don't use this video. Catches the invisible defect of a source track that stops mid-video.
- **Swap / Retire Provenance** — `--swap OLD_ID:NEW_URL` (repeatable) retires a prior batch video into the manifest's top-level `retired[]` list with a date and reason, and tags the replacement entry `swapped_from` + `swap {date, reason}` — a complete audit trail for batch re-runs.
- **Original-Audio Forcing** — `--audio-lang auto` (default) detects each video's original spoken track and refuses YouTube auto-dubbed audio (a real failure mode: English seminars downloaded with Japanese dubs); `--audio-lang en|ko|…` forces a specific track, and the language tag is stamped into the merged MP4.
- **Verification Gates** — `--verify` checks file size, duration, audio loudness, oEmbed title identity, and resolution after each download.
- **Download Manifest** — `--manifest out.json` writes an auditable JSON report per batch (per-video status + totals).
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

# Best-available quality (no height cap, h264/aac preferred at equal quality)
python cli.py <URL> --quality best

# Cap resolution at 720p
python cli.py <URL> --quality cap:720

# Subtitle sidecars (.vtt) — manual preferred, language priority configurable
python cli.py <URL> --write-subs --sub-langs "ko.*,en.*"

# Caption fallback chain for BOTH languages (manual → auto → auto-translated,
# each tagged manual|auto|translated|failed in the manifest)
python cli.py <URL> --write-subs --captions-langs "ko,en"

# Strict caption coverage gate (with --verify): a sidecar covering less than
# 0.95 of the video duration FAILS the download instead of only warning
python cli.py <URL> --write-subs --verify --require-caption-coverage

# Swap out a video that failed a downstream requirement (e.g. partial
# captions): the old entry moves to the manifest's retired[] list (date +
# reason) and the replacement is tagged swapped_from
python cli.py <URL_OLD> <URL_NEW> --manifest batch.json \
    --swap dQw4w9WgXcQ:https://youtu.be/<new_id> \
    --swap-reason "source captions cover only 62% of the video"

# Avoid YouTube auto-dubbing: 'auto' picks the original spoken track
# (multi-language videos), or force one explicitly
python cli.py <URL> --audio-lang auto
python cli.py <URL> --audio-lang en

# Full production batch: verify each download and write a JSON manifest
python cli.py <URL1> <URL2> --quality best --write-subs --verify \
    --manifest batch.json --id-names

# Force a specific language
QUICKDL_LANG=ko python cli.py <URL>   # macOS/Linux
set QUICKDL_LANG=ko && python cli.py <URL>  # Windows
```

CLI exit codes: `0` success · `1` download failure · `2` verification failure
(with `--verify`). One failed URL in a batch does not abort the remaining ones.

---

## Project Structure

```
QuickDL/
├── app.py                  # Flask server — routes, job queue, file serving
├── download_service.py     # yt-dlp wrapper (get_video_info, download_video)
├── verification.py         # Post-download gates + batch manifest builder
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
│   ├── test_app.py               # Flask API tests (9 tests — unittest)
│   ├── test_i18n.py              # i18n tests (14 tests — pytest)
│   ├── test_download_service.py  # service-layer tests (pytest, mocked yt-dlp)
│   ├── test_verification.py      # verification gate tests (pytest, mocked)
│   └── test_env.py               # Dependency check
├── scripts/
│   ├── audit.sh / audit.ps1        # Quality gate
│   └── dev-sync.sh / dev-sync.ps1  # PR pipeline
└── docs/context.md         # Project context for AI tools
```

---

## Running Tests

```bash
pytest tests/ -v        # All 111 tests
bash scripts/audit.sh   # Quality gate (CHANGELOG, i18n parity, broken links)
```

---

## License

This project is licensed under the [GNU Affero General Public License v3.0](LICENSE).
