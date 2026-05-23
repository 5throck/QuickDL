# Changelog

All notable changes to QuickDL are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added
- **[2026-05-23]**: `.githooks/pre-commit`: Markdown date auto-bumper 및 CHANGELOG auto-dating 로직 추가. 커밋 시 스테이징된 `.md` 파일의 `Last Updated:` 날짜를 자동으로 갱신하며, `CHANGELOG.md`의 미기재 항목에 날짜를 주입.
- **[2026-05-23]**: `docs/context.md`: Agents 테이블에 `security-monitor` (Security group) 추가.
- **[2026-05-23]**: `AGENTS.md`: 전체 Agent Roster에 `security-monitor` 요원 정식 등록.

### Changed
- **[2026-05-23]**: Default Branch: 프로젝트 기본 브랜치를 `master`에서 워크스페이스 표준인 `main`으로 성공적으로 마이그레이션 및 동기화 완료.

### Removed
- **[2026-05-23]**: `README.md` / `README_ko.md`: 더 이상 필요 없는 수동 킥오프 안내 문구 일괄 제거.


### Changed
- **[2026-05-23]**: Standardize session start checklist in CLAUDE.md to 6-step format (git config, CONSTITUTION, context, AGENTS, memory, skills)
- **[2026-05-23]**: Expand GEMINI.md with tool safeguards, Planning Mode artifacts, Subagent orchestration; remove duplicate Session Start section

### Added (2026-05-23 Antigravity CLI native config)
- **[2026-05-23]**: `QuickDL` and `templates/`: Map Antigravity write/edit tools to `.gemini/settings.json` PostToolUse hook
- **[2026-05-23]**: `QuickDL` and `templates/`: Copy `.claude/commands/` to `.gemini/commands/` for native slash command support
- **[2026-05-23]**: `QuickDL`: Update `GEMINI.md` to reflect new native features and tools

### Fixed (2026-05-23 Documentation Consistency)
- **[2026-05-23]**: `agents/*.md`: Fix test execution paths to use `tests/` prefix
- **[2026-05-23]**: `CLAUDE.md`: Align Subagent Pattern with 6-phase harness workflow
- **[2026-05-23]**: `.claude/commands/changelog.md`: Add missing YAML frontmatter
- **[2026-05-23]**: `scripts/sync-md.sh` / `.ps1`: Update skip paths to use `docs/specs` and `docs/plans`
- **[2026-05-23]**: `.github/pull_request_template.md`: Standardize project test command placeholder
### Fixed (2026-05-23 Audit Script — Relative Link Filter)
- **[2026-05-23]**: `scripts/audit.sh` / `audit.ps1`: Add `../../` relative-path exclusion to markdown link checker — GitHub Security Advisory links (`../../security/advisories/new`) are cross-repo relative URLs, not local file paths, and must be excluded from broken-link validation


### Added (2026-05-23 Project Structure Compliance)
- **[2026-05-23]**: `SECURITY.md`: Security vulnerability reporting policy (CONSTITUTION §1 required file)
- **[2026-05-23]**: `.github/pull_request_template.md`: Standard PR body template (CONSTITUTION §1 required file)
- **[2026-05-23]**: `.env.sample`: Environment variable template (CONSTITUTION §1 required file)
- **[2026-05-23]**: `.gemini/settings.json`: Gemini CLI project settings (CONSTITUTION §1 required file)
- **[2026-05-23]**: `scripts/git-sync.sh` / `git-sync.ps1`: Cross-platform git sync script pair (CONSTITUTION §3 script parity rule)

### Changed
- **[2026-05-23]**: Add ## Environment Setup, fix GEMINI.md absolute paths, clarify branching strategy in docs/context.md

### Changed
- **[2026-05-23]**: Add standard slash commands, smart pre-commit hook (memory/ exclusion), and Coding Guidelines section to docs/context.md

### Fixed (2026-05-22 Skill Command Wrappers)
- **[2026-05-23]**: `.claude/commands/i18n-audit.md`: New wrapper — registers `i18n-audit` skill for Skill tool invocation
- **[2026-05-23]**: `.claude/commands/post-write.md`: Converted from standalone duplicate to thin wrapper delegating to `skills/post-write-check/SKILL.md`

### Fixed (2026-05-22)
- **[2026-05-23]**: `core.hooksPath` set to `.githooks` — CHANGELOG pre-commit hook was inactive (hooks were in `.githooks/` but hooksPath was not configured)
- **[2026-05-23]**: `scripts/sync-md.sh` / `sync-md.ps1`: Skip audit hook for temporary/generated MD files via `CLAUDE_FILE_PATHS` env var check

### Changed
- **[2026-05-23]**: `desktop.py` — change window close behavior to fully quit the application instead of minimizing to the system tray
- **[2026-05-23]**: `install.py` — add cross-platform `ffmpeg` auto-installation logic (`winget`, `brew`, `apt`) and add new i18n keys to all 16 locales
- **[2026-05-23]**: Fix outdated test paths (`tests/`) in `skills/post-write-check/SKILL.md`, `skills/i18n-audit/SKILL.md`, `AGENTS.md`, and `docs/context.md`
- **[2026-05-23]**: Generalize AI `Co-Authored-By` rule in `docs/context.md` to be platform-agnostic
- **[2026-05-23]**: `ytdl.sh` — improve macOS/Linux launcher: add `pythonw` detection, 16-language error messages (th, ru, it, ar added), redirect error to stderr, use `exec` for clean process handoff
- **[2026-05-23]**: Rewrite `README.md` and `README_ko.md`: reflect current project structure (`tests/`, `locales/`, `i18n.py`, download queue, dark/light mode, 16 languages, CI badge, test/audit commands)
- **[2026-05-23]**: Fix `GEMINI.md`: replace broken `docs/agent-config/` references with `docs/context.md`; align response language to Korean; update agent role links to `agents/*.md`
- **[2026-05-23]**: Update `agents/qa.md`: replace `test_app.py`/`test_i18n.py` direct references with `tests/` paths; update test count to 23; update run command to `pytest tests/ -v`
- **[2026-05-23]**: Update `memory/MEMORY.md`: reflect all PRs since initial entry
- **[2026-05-23]**: Rewrite `CLAUDE.md`: add Doc intent header, CLI vs Desktop App hook matrix table, Claude Code Settings section, Git Hooks table — aligned with abap_vibe_coding reference structure
- **[2026-05-23]**: Move test files to `tests/` directory; add `pytest.ini` with `testpaths = tests`; add `tests/conftest.py` for automatic sys.path setup
- **[2026-05-23]**: Remove `docs/agent-config/` (merged Coding Conventions and Git strategy into `docs/context.md`); remove `docs/superpowers/` (Superpowers plugin artifacts)
- **[2026-05-23]**: Remove legacy root-level test files (`test_app.py`, `test_i18n.py`, `test_env.py`, `test_api.py`)
- **[2026-05-23]**: Move manual integration script to `tests/manual/test_api.py`
- **[2026-05-23]**: Simplify CI: single `pytest tests/ -v` step replaces separate i18n and API test steps
- **[2026-05-23]**: Update `CLAUDE.md` to reference `docs/context.md` as SSoT; remove Superpowers workflow section
- **[2026-05-23]**: Clean up `scripts/audit.sh` and `audit.ps1` to remove now-deleted `docs/superpowers` exclusion rules

### Fixed
- **[2026-05-23]**: `download_service.py` — use glob to find actual merged `.mp4` on disk instead of relying on `prepare_filename()` pre-merge path
- **[2026-05-23]**: `app.py` — replace `request.json` with `request.get_json(silent=True) or {}` to prevent `AttributeError` on missing `Content-Type` header
- **[2026-05-23]**: `app.py` — add `threading.Lock` guarding all accesses to `_jobs`, `_completed`, and `_cancel_events` to eliminate data races
- **[2026-05-23]**: `app.py` — SSRF protection: block private, loopback, and link-local IP literals in `_validate_url()`
- **[2026-05-23]**: `static/js/script.js` — fix memory leak in download queue: remove `<li>` element and delete `queue` Map entry after download link click
- **[2026-05-23]**: `scripts/audit.sh` — fix locale key-parity check to use Python process exit code instead of stdout capture
- **[2026-05-23]**: `.github/workflows/ci.yml` — run API tests via `pytest test_app.py -v` for consistent output and exit code

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
