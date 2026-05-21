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
│   ├── context.md          # THIS FILE
│   ├── agent-config/       # Legacy agent + shared config (see agents/pm.md)
│   └── superpowers/        # Design specs + implementation plans
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
| Designer | `docs/agent-config/agents.md` | HTML structure, CSS, accessibility |
| Frontend | `docs/agent-config/agents.md` | JS logic, API wiring, i18n in templates |
| i18n Expert | `docs/agent-config/agents.md` | locale files, i18n.py, launcher scripts |
| Security Officer | `docs/agent-config/agents.md` | Read-only audit, injection/path risks |
| Backend Developer | `docs/agent-config/agents.md` | Flask routes, download logic, CLI, installer |
| QA Engineer | `docs/agent-config/agents.md` | test_*.py, cross-platform validation |

---

## Skills

| Skill | Trigger |
|-------|---------|
| `superpowers:brainstorming` | New feature or non-trivial change — design first |
| `superpowers:writing-plans` | After brainstorming spec is approved |
| `superpowers:subagent-driven-development` | Executing an implementation plan task-by-task |
| `superpowers:finishing-a-development-branch` | After all tasks complete — verify, present options, merge/PR |

---

## Development Workflow

```
1. /new-task "description"       → create task
2. superpowers:brainstorming     → design spec → docs/superpowers/specs/
3. superpowers:writing-plans     → impl plan   → docs/superpowers/plans/
4. subagent-driven-development   → execute task-by-task with review
5. /memlog                       → write session log to memory/YYYY-MM-DD.md
6. /sync "feat: description"     → audit → commit → PR branch → gh pr create
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
| `test_i18n.py` | 14 tests — format_duration + locale key parity (pytest) |
| `test_app.py` | 9 tests — Flask API endpoints (unittest) |
| `.github/workflows/ci.yml` | i18n audit + pytest + test_app.py on Python 3.8/3.10/3.12 |
| `memory/MEMORY.md` | Index of all development session logs |
| `CHANGELOG.md` | Keep-a-Changelog format; `[Unreleased]` section updated before each release |

---

## i18n System

- **16 languages:** en, ko, ja, zh-TW, zh-CN, de, es, fr, pt, vi, ms, id, th, ru, it, ar
- **Detection priority:** `QUICKDL_LANG` env var → OS locale → `en` fallback
- **Baseline:** `locales/en.json` (56 keys) — all other files must match exactly
- **Web UI injection:** `render_template('index.html', i18n=get_all(), lang=get_lang())`
- **JS access:** `window.I18N['key']`

## Running the Project

```bash
python app.py            # Web UI at http://localhost:5000
python desktop.py        # Desktop app (pywebview + tray)
python cli.py <URL>      # CLI download

python test_app.py       # API tests (9 tests)
pytest test_i18n.py -v   # i18n tests (14 tests)

bash scripts/audit.sh    # Quality gate check
```
