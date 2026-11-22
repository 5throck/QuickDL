# QuickDL — co-utility Configuration

> Extends docs/context.md. This file IS the customization layer for this project.
> context.md is pipeline-maintained — all project-specific changes belong HERE.
>
> Read order for all AI tools:
>   1. docs/context.md              —pipeline-maintained shared reference (immutable)
>   2. docs/co-utility.context.md   —THIS FILE —QuickDL stack, doctrine, workflow
>
> Variant: **co-utility** (doctrine per `variant.json`; delivered from workspace
> template 0.30.0; rebase from co-develop completed 2026-11-19).

---

## Project Overview

**QuickDL** is a cross-platform YouTube video downloader with three interfaces: a
Flask web UI, a pywebview desktop app, and a CLI. Core download logic is powered
by yt-dlp. Quality modes, caption sidecars, verification gates, download
manifests, and original-audio forcing are first-class product capabilities
documented in `README.md` and `CHANGELOG.md`.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Language | Python 3.8+ |
| Web backend | Flask |
| Download engine | yt-dlp |
| Desktop shell | pywebview + pystray |
| Frontend | Vanilla JS + Jinja2 templates |
| i18n | Custom `src/i18n.py` (flat JSON locale files) |
| Tests | pytest + unittest (`tests/`, 111 tests) |
| CI | GitHub Actions (`.github/workflows/ci.yml`) —Python 3.8/3.10/3.12 |

---

## Utility Doctrine Instantiation

The co-utility variant doctrine applied to QuickDL's concrete shape:

| Doctrine area | QuickDL instantiation |
|---------------|----------------------|
| **Multi-interface surface matrix** | Core service `src/download_service.py`; adapters: web UI (`src/app.py` + `src/templates/`), desktop shell (`src/desktop.py`, pywebview + pystray), CLI (`src/cli.py`) |
| **Runtime-output isolation** | `downloads/` at repo root (gitignored, never source); `.venv/` repo-level; output root resolved from the `src/` file anchors one level under the repo root |
| **Locale-matrix i18n** | 16 locales (`src/locales/*.json`), `en.json` baseline key parity; runtime loader `src/i18n.py` (`SUPPORTED` set mirrors the directory); detection chain `QUICKDL_LANG` env → OS locale → `en` |
| **External-input security** | URL handling (yt-dlp), path construction from video titles/IDs, no subprocess with user strings; double-audited at Phase 1 and Phase 4 |
| **Cross-platform script pairing** | `ytdl.sh` / `ytdl.bat` launchers change together |

---

## Architecture

```
quickdl/
├── src/                         # Application package root
│   ├── app.py                   # Flask server —routes, job queue, file serving
│   ├── download_service.py      # yt-dlp wrapper (get_video_info, download_video)
│   ├── desktop.py               # Desktop entry point (pywebview + pystray + Flask thread)
│   ├── cli.py                   # CLI entry point (argparse)
│   ├── install.py               # Cross-platform installer (.venv setup)
│   ├── i18n.py                  # i18n: init(), t(), get_all(), get_lang(), format_duration()
│   ├── verification.py          # Post-download verification gates
│   ├── locales/                 # 16 flat JSON locale files (en.json is the baseline)
│   ├── templates/index.html     # Web UI (Jinja2)
│   └── static/
│       ├── css/styles.css       # UI styles (dark + light mode, responsive)
│       └── js/script.js         # Frontend JS (fetch API, download queue, polling)
├── requirements.txt             # Python dependencies
├── ytdl.bat / ytdl.sh           # One-click launchers (Windows / macOS+Linux)
├── tests/                       # pytest + unittest suite (111 tests)
├── agents/                      # Agent definitions (pm, backend, frontend, i18n-specialist, qa, security)
├── docs/                        # Pipeline-maintained context + this customization layer
├── scripts/                     # Workspace-standard tooling (audit.ts, dev-sync.ts, ...)
├── memory/                      # Session development logs + MEMORY.md index
├── .claude/                     # settings.json, commands/, agents/ mirrors
└── .github/workflows/ci.yml     # GitHub Actions CI
```

### Key Files

| File | Purpose |
|------|---------|
| `src/app.py` | Flask routes: `/api/info`, `/api/download`, `/api/status/<id>`, `/api/file/<id>` |
| `src/download_service.py` | `get_video_info(url)`, `download_video(url, dir, progress_hook, cancel_event)` |
| `src/i18n.py` | `init()`, `t(key)`, `get_all()`, `get_lang()`, `format_duration(seconds)` |
| `src/locales/en.json` | i18n baseline —all other locales must match its key set exactly (parity is asserted by `tests/test_i18n.py`) |
| `tests/test_i18n.py` | Locale key parity + format_duration tests |
| `tests/test_app.py` | Flask API endpoint tests (unittest) |
| `tests/manual/test_api.py` | Manual integration test —requires live server at :5000 |
| `memory/MEMORY.md` | Index of all development session logs |
| `CHANGELOG.md` | Keep-a-Changelog format; `[Unreleased]` section updated before each release |

---

## Agents

<!-- context-proximity: agent roles summarized here for AI context window efficiency; authoritative definitions in agents/*.md -->

| Agent | File | Role | Tier | Status |
|-------|------|------|------|--------|
| PM (Orchestrator) | `agents/pm.md` | Workflow management, dispatch, quality gates | high | active |
| Backend | `agents/backend.md` | Core service, Flask API, CLI, installer | high | active |
| Frontend | `agents/frontend.md` | Web UI logic, API wiring, i18n in templates, desktop shell | medium | active |
| I18N Specialist | `agents/i18n-specialist.md` | Locale config/formatting/layout (common extends-stub); QuickDL specifics: §i18n System below | medium | active |
| QA | `agents/qa.md` | Test suite ownership (`tests/`), cross-platform validation | medium | active |
| Security | `agents/security.md` | External-input audits (read-only) + ongoing dependency/secret monitoring | high | active |

Note: the roster may be dynamically expanded by the PM during the Kickoff Phase
based on emerging requirements (PM Team-Management Authority, ADR-0080).

## Skills

| Skill | Source | Trigger |
|-------|--------|---------|
| `post-write-check` | variant-exclusive (`skills/post-write-check/`) | After any Write/Edit to source files |
| `i18n-audit` | common 1.0.2 (Runtime Loader Sync included) | After any locale file or `src/i18n.py` change |
| common set (sync, security-scan, ci-triage, lifecycle managers, …) | `templates/common` via `inherits_common` | Per workspace `VERSION_MANIFEST.md` |

---

## Environment Setup

```bash
# Python 3.8+
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
.venv\Scripts\activate           # Windows

pip install -r requirements.txt

# Activate git hooks
git config core.hooksPath .githooks

# Run development server
python src/app.py                # Web UI at http://localhost:5000

# Run tests
pytest tests/ -q                 # 111 tests
```

Required env keys: none —no external API keys required (see `.env.sample` for the
placeholder convention).

### Running the Project

```bash
python src/app.py                # Web UI at http://localhost:5000
python src/desktop.py            # Desktop app (pywebview + tray)
python src/cli.py <URL>          # CLI download
```

---

## Development Workflow

```
1. /new-task "description"    —create task
2. Design (if non-trivial)    —write spec to docs/designs/<spec-id>-design.md, register via spec-register
3. Implement                  —edit files; post-write-check skill gates every edit
4. /memlog                    —write session log to memory/YYYY-MM-DD.md
5. /sync "feat: description"  —audit → commit → PR branch → gh pr create
```

**PR rule:** All changes reach `main` via Pull Request —never direct push.

**Quality gates (all must pass before merge)** — carried from the legacy project
constitution:

| Gate | Command | Standard |
|------|---------|----------|
| Workspace audit | `bun scripts/audit.ts --skip-memory` | Exit 0 |
| Tests | `pytest tests/ -q` | 111 passed |

**Read-first rule** (from the legacy constitution): before starting any task, load
in order — `docs/context.md` → this file → `memory/MEMORY.md` →
`src/locales/en.json` (for i18n/UI work).

**Tracking management:**
- `CHANGELOG.md`: end-user release notes — *what* changed (English).
- `memory/` logs: developers and AI agents — *how* and *why* (English). Agents
  MUST append a session summary after significant work and may update the
  architecture sections of this file when a significant architectural decision lands.

### Branching Strategy

Use `/sync "type: description"` (the governed dev-sync pipeline) — it auto-creates
the `pr/<YYYYMMDD-HHmmss>-<slug>` branch, commits, pushes, and opens a PR.

Manual branches: `feature/<name>`, `fix/<name>`, `chore/<name>` — merge into
`main` via PR only; no force push.

---

## Guidelines

### Coding Guidelines (QuickDL)

- **Python version:** 3.8+ —use `Optional[str]` from `typing`, NOT `str | None`
- **Encoding:** UTF-8 (no BOM) everywhere; files opened with `encoding="utf-8"`;
  script outputs specify the encoding explicitly
- **Function size:** single responsibility; split functions that exceed ~30 lines
- **Error handling:** no bare `except:`; catch specific exceptions
- **Imports:** stdlib → third-party → local, separated by blank lines
- **SOLID + unit tests** when creating functional code

### Git Conventions (QuickDL)

- **Commit messages:** English, imperative mood ("Add feature", not "Added feature")
- **AI commits:** append the respective AI Co-Authored-By tag (see `CLAUDE.md`, `GEMINI.md`, or `AGENTS.md`)
- **Stage specific files** —avoid `git add -A` or `git add .` (the /sync pipeline is the sanctioned exception)
- **No force push to `main`**

### Security Rules (from the legacy constitution)

- Never expose or log secrets (API keys, tokens). No `.env` in the repo —only the
  placeholder `.env.sample` convention. Never commit private key material.
- Do not modify CI/CD pipelines (`.github/workflows/`, `.githooks/`) without
  explicit user permission.
- Vulnerabilities are reported privately per `SECURITY.md` (GitHub Security
  Advisory) —never as public issues.
- The `security` agent audits new external-input paths (injection, path traversal,
  CORS, dependencies) during Phase 1 and re-audits in Phase 4.

### Language Policy (project application)

English-only documentation: all `.md` files, commit messages, PR titles and bodies
are written in English. `README_ko.md` is the sanctioned Korean translation zone
(`lang: ko`, `lang_reason: source-material`) and must stay in sync with `README.md`.

---

## File Organization Policy

Application source, templates, static assets, and locale files live under
`src/`; tests under `tests/`; project documentation under `docs/`; session logs
under `memory/`; runtime output in repo-level gitignored directories (never
`__file__`-relative). Root-level files are repo meta only (README, CHANGELOG,
launchers, requirements).

---

## Domain Rules

### i18n System

- **16 languages:** en, ko, ja, zh-TW, zh-CN, de, es, fr, pt, vi, ms, id, th, ru, it, ar
- **Detection priority:** `QUICKDL_LANG` env var → OS locale → `en` fallback
- **Baseline:** `src/locales/en.json` —all other files must match its key set exactly (count asserted by `tests/test_i18n.py`, never hardcoded here)
- **Web UI injection:** `render_template('index.html', i18n=get_all(), lang=get_lang())`
- **Runtime loader contract (`src/i18n.py`):** `SUPPORTED` set lists the 16 shipped
  locales and must match the `src/locales/*.json` directory exactly — the common
  `i18n-audit` skill's Runtime Loader Sync step verifies this; adding a locale means
  updating `SUPPORTED`, dropping the JSON file, extending `format_duration` rules,
  and `tests/test_i18n.py` expectations together
- **`t(key)`** returns the translation for the active language with `en` fallback;
  **`format_duration(seconds)`** carries per-locale pluralization/duration word rules
- **JS access:** `window.I18N['key']`

### Utility Doctrine Rules

1. **One core service** — every interface adapter calls `src/download_service.py`;
   duplicated logic across interfaces is a defect.
2. **Runtime output never lands in source** — `downloads/` stays repo-level and
   gitignored; agents never modify it or `.venv/`.
3. **Locale changes are atomic** — locale file + `SUPPORTED` + language selector +
   `tests/test_i18n.py` expectations in one change.
4. **External-input sinks are double-audited** — URL, path, subprocess (Phase 1 + Phase 4).
5. **Launcher pairs move together** — `ytdl.sh` and `ytdl.bat` change in the same commit.
