# QuickDL — Shared Agent Configuration

> This file is the single source of truth for all AI tools working on QuickDL.
> It is referenced by `CLAUDE.md`, `AGENTS.md`, and `GEMINI.md`.
> Read this file before starting any task.

---

## Project Overview

**QuickDL** is a cross-platform YouTube video downloader with three interfaces:
- **Desktop app** — pywebview window launched by `desktop.py`; system tray via pystray
- **Web UI** — Flask app (`app.py`) at `http://localhost:5000`
- **CLI** — `cli.py <URL>` for terminal-based downloads

Core download logic lives in `download_service.py` (yt-dlp wrapper). The installer (`install.py`) sets up a `.venv/` virtual environment and environment variables cross-platform.

**Tech stack:** Python 3.8+, Flask, pywebview, pystray, yt-dlp, Pillow

---

## Directory Structure

```
QuickDL/
├── app.py                  # Flask web server — routes, API endpoints
├── download_service.py     # yt-dlp download logic (get_video_info, download_video)
├── desktop.py              # Desktop app entry point (pywebview + pystray + Flask thread)
├── cli.py                  # CLI entry point (argparse)
├── install.py              # Cross-platform installer (venv, packages, env vars)
├── i18n.py                 # i18n core: init(), t(), get_all(), get_lang()
├── requirements.txt        # Python dependencies
├── ytdl.bat                # Windows one-click launcher
├── ytdl.sh                 # macOS/Linux one-click launcher
├── locales/                # Translation files (flat JSON, one per language)
│   ├── en.json             # English (baseline — always complete)
│   ├── ko.json             # Korean
│   ├── ja.json             # Japanese
│   ├── zh-TW.json          # Traditional Chinese (Taiwan)
│   ├── zh-CN.json          # Simplified Chinese
│   ├── de.json             # German
│   ├── es.json             # Spanish
│   ├── fr.json             # French
│   ├── pt.json             # Portuguese
│   ├── vi.json             # Vietnamese
│   ├── ms.json             # Malay
│   └── id.json             # Indonesian
├── templates/
│   └── index.html          # Main web UI template (Jinja2)
├── static/
│   ├── js/script.js        # Frontend JS — fetch, download, i18n via window.I18N
│   └── css/                # Stylesheets
├── docs/
│   └── agent-config/
│       ├── shared.md       # THIS FILE
│       └── agents.md       # Agent role definitions
└── .venv/                  # Virtual environment — NEVER modify contents
```

---

## i18n System

**Module:** `i18n.py`

**Language detection priority:**
1. `QUICKDL_LANG` environment variable (e.g., `QUICKDL_LANG=ja`)
2. OS locale via `locale.getdefaultlocale()` (e.g., `ko_KR` → `ko`)
3. Falls back to `"en"`

**Supported languages (12):**

| Code | Language |
|------|----------|
| `en` | English (baseline fallback) |
| `ko` | 한국어 Korean |
| `ja` | 日本語 Japanese |
| `zh-TW` | 繁體中文 Traditional Chinese |
| `zh-CN` | 简体中文 Simplified Chinese |
| `de` | Deutsch German |
| `es` | Español Spanish |
| `fr` | Français French |
| `pt` | Português Portuguese |
| `vi` | Tiếng Việt Vietnamese |
| `ms` | Bahasa Melayu Malay |
| `id` | Bahasa Indonesia Indonesian |

**Usage:**
```python
from i18n import init as i18n_init, t
i18n_init()          # call once at startup
t("cli.fetching")    # returns translated string
t("cli.error", e=e)  # with format substitution
```

**Web UI:** Flask injects translations via template:
```python
render_template('index.html', i18n=get_all(), lang=get_lang())
```
```html
<script>window.I18N = {{ i18n | tojson }};</script>
```

**All locale files must have exactly the same 49 keys as `locales/en.json`.**

---

## Coding Conventions

- **Python version:** 3.8+ — use `Optional[str]` from `typing`, NOT `str | None`
- **Encoding:** UTF-8 everywhere; files opened with `encoding="utf-8"`
- **Function size:** single responsibility; if a function exceeds ~30 lines, split it
- **Error handling:** no bare `except:`; catch specific exceptions
- **Imports:** stdlib → third-party → local, separated by blank lines
- **No modification of `.venv/`** — never touch virtual environment internals

---

## Git Conventions

- **Commit messages:** always in English, imperative mood ("Add feature", not "Added feature")
- **AI commits:** append trailer `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`
- **Stage specific files** — avoid `git add -A` or `git add .`
- **No force push to master/main**
- Remote: `https://github.com/5throck/QuickDL.git`

### Branching Strategy

All changes go through a feature branch → Pull Request → merge workflow:

```bash
# 1. Create a branch for each feature or fix
git checkout -b feature/<feature-name>   # new feature
git checkout -b fix/<bug-name>           # bug fix
git checkout -b chore/<task-name>        # maintenance (docs, deps, config)

# 2. Commit work on the branch
git add <specific files>
git commit -m "Add/Fix/Update <what and why>"

# 3. Push and open a PR
git push -u origin feature/<feature-name>
gh pr create --title "<title>" --body "<description>"

# 4. After review, merge into master via GitHub UI or:
gh pr merge --squash
```

**Branch naming examples:**
- `feature/thai-locale` — add Thai language support
- `fix/tray-icon-crash` — fix pystray crash on macOS
- `chore/update-yt-dlp` — bump yt-dlp dependency version

**Never commit directly to `master`** after the initial setup.

---

## Running the Project

```bash
# Web UI (browser)
python app.py
# → open http://localhost:5000

# Desktop app
python desktop.py

# CLI
python cli.py <YouTube URL>
python cli.py <YouTube URL> --output /path/to/folder

# Installer (first-time setup)
python install.py

# Test scripts (plain assert, no framework)
python test_api.py
python test_env.py

# Force a specific language
QUICKDL_LANG=ms python cli.py <URL>   # macOS/Linux
set QUICKDL_LANG=id && python cli.py <URL>  # Windows
```

---

## Agent Roles

See `docs/agent-config/agents.md` for the full definition of each agent role (PM, Designer, Frontend Developer, i18n Expert, Security Officer, Backend Developer, QA Engineer).
