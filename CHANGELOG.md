# Changelog

All notable changes to QuickDL are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Fixed (2026-05-23 Documentation Consistency)
- `agents/*.md`: Fix test execution paths to use `tests/` prefix
- `CLAUDE.md`: Align Subagent Pattern with 6-phase harness workflow
- `.claude/commands/changelog.md`: Add missing YAML frontmatter
- `scripts/sync-md.sh` / `.ps1`: Update skip paths to use `docs/specs` and `docs/plans`
- `.github/pull_request_template.md`: Standardize project test command placeholder
### Fixed (2026-05-23 Audit Script — Relative Link Filter)
- `scripts/audit.sh` / `audit.ps1`: Add `../../` relative-path exclusion to markdown link checker — GitHub Security Advisory links (`../../security/advisories/new`) are cross-repo relative URLs, not local file paths, and must be excluded from broken-link validation


### Added (2026-05-23 Project Structure Compliance)
- `SECURITY.md`: Security vulnerability reporting policy (CONSTITUTION §1 required file)
- `.github/pull_request_template.md`: Standard PR body template (CONSTITUTION §1 required file)
- `.env.sample`: Environment variable template (CONSTITUTION §1 required file)
- `.gemini/settings.json`: Gemini CLI project settings (CONSTITUTION §1 required file)
- `scripts/git-sync.sh` / `git-sync.ps1`: Cross-platform git sync script pair (CONSTITUTION §3 script parity rule)

### Changed
- Add ## Environment Setup, fix GEMINI.md absolute paths, clarify branching strategy in docs/context.md

### Changed
- Add standard slash commands, smart pre-commit hook (memory/ exclusion), and Coding Guidelines section to docs/context.md

### Fixed (2026-05-22 Skill Command Wrappers)
- `.claude/commands/i18n-audit.md`: New wrapper — registers `i18n-audit` skill for Skill tool invocation
- `.claude/commands/post-write.md`: Converted from standalone duplicate to thin wrapper delegating to `skills/post-write-check/SKILL.md`

### Fixed (2026-05-22)
- `core.hooksPath` set to `.githooks` — CHANGELOG pre-commit hook was inactive (hooks were in `.githooks/` but hooksPath was not configured)
- `scripts/sync-md.sh` / `sync-md.ps1`: Skip audit hook for temporary/generated MD files via `CLAUDE_FILE_PATHS` env var check

### Changed
- `desktop.py` — change window close behavior to fully quit the application instead of minimizing to the system tray
- `install.py` — add cross-platform `ffmpeg` auto-installation logic (`winget`, `brew`, `apt`) and add new i18n keys to all 16 locales
- Fix outdated test paths (`tests/`) in `skills/post-write-check/SKILL.md`, `skills/i18n-audit/SKILL.md`, `AGENTS.md`, and `docs/context.md`
- Generalize AI `Co-Authored-By` rule in `docs/context.md` to be platform-agnostic
- `ytdl.sh` — improve macOS/Linux launcher: add `pythonw` detection, 16-language error messages (th, ru, it, ar added), redirect error to stderr, use `exec` for clean process handoff
- Rewrite `README.md` and `README_ko.md`: reflect current project structure (`tests/`, `locales/`, `i18n.py`, download queue, dark/light mode, 16 languages, CI badge, test/audit commands)
- Fix `GEMINI.md`: replace broken `docs/agent-config/` references with `docs/context.md`; align response language to Korean; update agent role links to `agents/*.md`
- Update `agents/qa.md`: replace `test_app.py`/`test_i18n.py` direct references with `tests/` paths; update test count to 23; update run command to `pytest tests/ -v`
- Update `memory/MEMORY.md`: reflect all PRs since initial entry
- Rewrite `CLAUDE.md`: add Doc intent header, CLI vs Desktop App hook matrix table, Claude Code Settings section, Git Hooks table — aligned with abap_vibe_coding reference structure
- Move test files to `tests/` directory; add `pytest.ini` with `testpaths = tests`; add `tests/conftest.py` for automatic sys.path setup
- Remove `docs/agent-config/` (merged Coding Conventions and Git strategy into `docs/context.md`); remove `docs/superpowers/` (Superpowers plugin artifacts)
- Remove legacy root-level test files (`test_app.py`, `test_i18n.py`, `test_env.py`, `test_api.py`)
- Move manual integration script to `tests/manual/test_api.py`
- Simplify CI: single `pytest tests/ -v` step replaces separate i18n and API test steps
- Update `CLAUDE.md` to reference `docs/context.md` as SSoT; remove Superpowers workflow section
- Clean up `scripts/audit.sh` and `audit.ps1` to remove now-deleted `docs/superpowers` exclusion rules

### Fixed
- `download_service.py` — use glob to find actual merged `.mp4` on disk instead of relying on `prepare_filename()` pre-merge path
- `app.py` — replace `request.json` with `request.get_json(silent=True) or {}` to prevent `AttributeError` on missing `Content-Type` header
- `app.py` — add `threading.Lock` guarding all accesses to `_jobs`, `_completed`, and `_cancel_events` to eliminate data races
- `app.py` — SSRF protection: block private, loopback, and link-local IP literals in `_validate_url()`
- `static/js/script.js` — fix memory leak in download queue: remove `<li>` element and delete `queue` Map entry after download link click
- `scripts/audit.sh` — fix locale key-parity check to use Python process exit code instead of stdout capture
- `.github/workflows/ci.yml` — run API tests via `pytest test_app.py -v` for consistent output and exit code

---

## [1.2.0] — 2026-05-20

### Added
- **Multi-agent harness engineering** — project-level config files for Claude Code (`CLAUDE.md`), Codex (`AGENTS.md`), and Gemini CLI (`GEMINI.md`)
- `docs/agent-config/shared.md` — single source of truth for project context, conventions, i18n system, and Git rules shared across all AI tools
- `docs/agent-config/agents.md` — authoritative role definitions for 7 agent types: PM, Designer, Frontend Developer, i18n Expert, Security Officer, Backend Developer, QA Engineer
- **Malay (ms)** locale support — `locales/ms.json` with 49 translated keys
- **Indonesian (id)** locale support — `locales/id.json` with 49 translated keys
- `ytdl.bat` / `ytdl.sh` now display localized warning messages in Malay and Indonesian when `.venv` is missing

### Changed
- `i18n.py` `SUPPORTED` set expanded from 10 to 12 languages (added `ms`, `id`)

---

## [1.1.0] — 2026-05-20

### Added
- **i18n (internationalization)** — full multilingual support across all interfaces (web UI, desktop app, CLI, installer, shell launchers)
- `i18n.py` — language detection module: `QUICKDL_LANG` env var → OS locale → `en` fallback
- `locales/en.json` — English translations (baseline, 49 keys)
- `locales/ko.json` — Korean translations
- `locales/ja.json` — Japanese translations
- `locales/zh-TW.json` — Traditional Chinese (Taiwan) translations
- `locales/zh-CN.json` — Simplified Chinese translations
- `locales/de.json` — German translations
- `locales/es.json` — Spanish translations
- `locales/fr.json` — French translations
- `locales/pt.json` — Portuguese translations
- `locales/vi.json` — Vietnamese translations
- `app.py` — injects `window.I18N` via Flask template for JS-side i18n
- `templates/index.html` — `<html lang>` attribute, Jinja2 i18n for static strings
- `static/js/script.js` — `window.I18N['key']` for all dynamic user-facing strings

### Changed
- `cli.py` — all user-visible strings replaced with `t()` calls
- `install.py` — all user-visible strings replaced with `t()` calls
- `desktop.py` — tray menu labels and error dialogs use `t()` calls
- `ytdl.bat` / `ytdl.sh` — localized `.venv` warning messages via `QUICKDL_LANG`
- `README.md` — clone URL updated to `https://github.com/5throck/QuickDL.git`
- `README_ko.md` — same

---

## [1.0.0] — 2026-05-20

### Added
- **Desktop app** (`desktop.py`) — pywebview window wrapping the Flask web UI; launches with a double-click
- **System tray** — pystray icon with Open Window / Quit menu; closing the window keeps the app alive in the tray
- **CLI** (`cli.py`) — `python cli.py <URL> [--output DIR]` for terminal-based downloads
- **Cross-platform installer** (`install.py`) — creates `.venv/`, installs dependencies, sets `PYTHONIOENCODING=utf-8`; idempotent, works on Windows / macOS / Linux
- **Windows launcher** (`ytdl.bat`) — double-click to start desktop app; warns if `.venv` is missing
- **macOS/Linux launcher** (`ytdl.sh`) — same as above for Unix systems
- `requirements.txt` — added `pywebview`, `pystray`, `Pillow`
- `LICENSE` — GNU Affero General Public License v3.0
- `.gitignore` — Python, venv, OS, IDE exclusions
- `README.md` — English documentation (features, requirements, installation, usage, project structure)
- `README_ko.md` — Korean documentation
- GitHub repository registered at `https://github.com/5throck/QuickDL.git`

---

[Unreleased]: https://github.com/5throck/QuickDL/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/5throck/QuickDL/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/5throck/QuickDL/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/5throck/QuickDL/releases/tag/v1.0.0
