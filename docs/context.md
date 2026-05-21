# QuickDL — Project Context

> Single source of truth shared by all AI tools (Claude Code, Gemini CLI, Codex).
> Read this file before starting any task on QuickDL.

---

## Project Overview

**QuickDL** is a cross-platform YouTube video downloader with three interfaces: a Flask web UI, a pywebview desktop app, and a CLI. Core download logic is powered by yt-dlp.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.8+ |
| Web backend | Flask |
| Download engine | yt-dlp |
| Desktop shell | pywebview + pystray |
| Frontend | Vanilla JS + Jinja2 templates |
| i18n | Custom `i18n.py` (flat JSON locale files) |
| Tests | pytest (`test_i18n.py`) + unittest (`test_app.py`) |
| CI | GitHub Actions (`.github/workflows/ci.yml`) — Python 3.8/3.10/3.12 |

---

## Architecture

```
quickdl/
├── app.py                  # Flask server — routes, job queue, file serving
├── download_service.py     # yt-dlp wrapper (get_video_info, download_video)
├── desktop.py              # Desktop entry point (pywebview + pystray + Flask thread)
├── cli.py                  # CLI entry point (argparse)
├── install.py              # Cross-platform installer (.venv setup)
├── i18n.py                 # i18n: init(), t(), get_all(), get_lang(), format_duration()
├── requirements.txt        # Python dependencies
├── ytdl.bat / ytdl.sh      # One-click launchers (Windows / macOS+Linux)
├── locales/                # 16 flat JSON locale files (en.json is the baseline)
├── templates/index.html    # Web UI (Jinja2)
├── static/
│   ├── css/styles.css      # UI styles (dark + light mode, responsive)
│   └── js/script.js        # Frontend JS (fetch API, download queue, polling)
├── agents/pm.md            # PM orchestrator agent definition
├── docs/
│   └── context.md          # THIS FILE — single source of truth for all AI tools
├── scripts/
│   ├── audit.sh / audit.ps1        # Quality gate (CHANGELOG + i18n key parity)
│   └── dev-sync.sh / dev-sync.ps1  # Full PR pipeline
├── memory/                 # Session development logs
│   └── MEMORY.md           # Log index
├── .claude/
│   ├── settings.json       # PostToolUse audit hook (committed)
│   ├── settings.local.json # Personal git/gh permissions (gitignored)
│   └── commands/           # /sync, /memlog, /new-task slash commands
└── .github/workflows/ci.yml  # GitHub Actions CI
```

---

## Agents

| Agent | File | Role |
|-------|------|------|
| PM | `agents/pm.md` | Orchestrates all work — planning, specs, task tracking, PR |
| Designer | `agents/designer.md` | HTML structure, CSS, accessibility |
| Frontend | `agents/frontend.md` | JS logic, API wiring, i18n in templates |
| i18n Expert | `agents/i18n.md` | locale files, i18n.py, launcher scripts |
| Security Officer | `agents/security.md` | Read-only audit, injection/path risks |
| Backend Developer | `agents/backend.md` | Flask routes, download logic, CLI, installer |
| QA Engineer | `agents/qa.md` | tests/, cross-platform validation |

---

## Skills

| Skill | File | Trigger |
|-------|------|---------|
| `post-write-check` | `skills/post-write-check/SKILL.md` | After any Write/Edit to Python/JS files |
| `i18n-audit` | `skills/i18n-audit/SKILL.md` | After any locale file or i18n.py change |

---

## Development Workflow

```
1. /new-task "description"   → create task
2. Design (if non-trivial)   → write spec to docs/specs/YYYY-MM-DD-<topic>.md
3. Implement                 → edit files; PostToolUse hook runs audit.sh automatically
4. /memlog                   → write session log to memory/YYYY-MM-DD.md
5. /sync "feat: description" → audit → commit → PR branch → gh pr create
```

**PR rule:** All changes reach `master` via Pull Request — never direct push.

**Audit gate** (`scripts/audit.sh` runs after every Write/Edit):
- CHANGELOG.md must exist
- All 16 locale files must have identical keys to `locales/en.json`

---

## Key Files

| File | Purpose |
|------|---------|
| `app.py` | Flask routes: `/api/info`, `/api/download`, `/api/status/<id>`, `/api/file/<id>` |
| `download_service.py` | `get_video_info(url)`, `download_video(url, dir, progress_hook, cancel_event)` |
| `i18n.py` | `init()`, `t(key)`, `get_all()`, `get_lang()`, `format_duration(seconds)` |
| `locales/en.json` | i18n baseline — 56 keys, all other locales must match exactly |
| `tests/test_i18n.py` | 14 tests — format_duration + locale key parity (pytest) |
| `tests/test_app.py` | 9 tests — Flask API endpoints (unittest) |
| `tests/manual/test_api.py` | Manual integration test — requires live server at :5000 |
| `.github/workflows/ci.yml` | i18n audit + pytest tests/ on Python 3.8/3.10/3.12 |
| `memory/MEMORY.md` | Index of all development session logs |
| `CHANGELOG.md` | Keep-a-Changelog format; `[Unreleased]` section updated before each release |

---

## i18n System

- **16 languages:** en, ko, ja, zh-TW, zh-CN, de, es, fr, pt, vi, ms, id, th, ru, it, ar
- **Detection priority:** `QUICKDL_LANG` env var → OS locale → `en` fallback
- **Baseline:** `locales/en.json` (56 keys) — all other files must match exactly
- **Web UI injection:** `render_template('index.html', i18n=get_all(), lang=get_lang())`
- **JS access:** `window.I18N['key']`

## Coding Conventions

- **Python version:** 3.8+ — use `Optional[str]` from `typing`, NOT `str | None`
- **Encoding:** UTF-8 everywhere; files opened with `encoding="utf-8"`
- **Function size:** single responsibility; split functions that exceed ~30 lines
- **Error handling:** no bare `except:`; catch specific exceptions
- **Imports:** stdlib → third-party → local, separated by blank lines

---

## Git Conventions

- **Commit messages:** English, imperative mood ("Add feature", not "Added feature")
- **AI commits:** append `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`
- **Stage specific files** — avoid `git add -A` or `git add .`
- **No force push to master**

### Branching Strategy

```bash
git checkout -b feature/<name>  # new feature
git checkout -b fix/<name>      # bug fix
git checkout -b chore/<name>    # maintenance (docs, deps, config)
# → push + gh pr create → merge into master via PR only
```

---

## Running the Project

```bash
python app.py            # Web UI at http://localhost:5000
python desktop.py        # Desktop app (pywebview + tray)
python cli.py <URL>      # CLI download

pytest tests/ -v         # All tests (23 tests)
bash scripts/audit.sh    # Quality gate check
```
