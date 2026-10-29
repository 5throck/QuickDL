# Changelog

All notable changes to QuickDL are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.0.0/).

---

## [Unreleased]

### Added (2026-10-29 Production-Hardened Downloads)
- **[2026-10-29]**: `download_service.py` / `verification.py` (new) / `cli.py`: Reflect production-validated download features as native capabilities — `--quality best|cap:N` (best-available mode: probe per video, no artificial height cap, h264/aac preferred at equal resolution via `format_sort`), `--write-subs` / `--sub-langs` (WebVTT subtitle sidecars, manual preferred over auto-generated, configurable language priority), `--verify` (post-download gates: >1 MB size, duration ±5%, audio mean ≥ −60 dB, oEmbed title identity, resolution vs probed max), `--manifest PATH` (auditable JSON batch manifest with per-video records + totals + tool info), `--id-names` (ID-keyed output filenames), and multi-URL batch support with per-video failure isolation. Exit codes: 0 success / 1 download failure / 2 verification failure. All new modes are opt-in; existing default flows unchanged. **Provenance**: the gates and practices mirror the co-deck workspace's validated download workflow — [ADR-0002](../../../ai_workspace/Projects/co-deck/docs/adr/0002-deck-video-asset-verification-and-injector-binding.md) (deck video asset verification: volumedetect ≥ −60 dB silence gate, oEmbed/ID identity check, clean per-video download folder) as proven in the 2026-10 18-video production deck run (0 failures). for quality modes, subtitle options, ID-keyed naming, verification gates, and manifest totals (suite: 23 → 60 tests).
- **[2026-10-29]**: `locales/*.json`: 13 new `cli.*` keys across all 16 locales (baseline 59 → 72 keys).

### Added (2026-10-30 Co-deck Rounds 4–6 — Original-Audio Forcing & Caption Fallback Chain)
- **[2026-10-30]**: `download_service.py` / `cli.py`: **Original-audio forcing (anti-dubbing)** — new `--audio-lang auto|<code>` (default `auto`). YouTube auto-dubbing makes plain `bestaudio` silently pick a DUB track (real production failures: an English seminar delivered with Japanese audio; a Korean news clip with Korean-dubbed audio). The probe now collects each video's audio-track languages (`audio_tracks` / format `language` fields), resolves the ORIGINAL spoken track (`audio_is_original` → `language_preference` → video `language`), and the format selector's first alternative gains `bestaudio[language^=<code>]` with graceful fallback to any audio when no matching track exists (a manifest warning records the mismatch). The merged MP4 gets `-metadata:s:a:0 language=<code>` stamped so the tag survives remux. Manifest per-video entries gain `audio_language` (and `audio_languages_available` when the video offers multiple audio languages).
- **[2026-10-30]**: `download_service.py` / `cli.py`: **Caption language configuration + translated-caption acquisition with honest fallback chain** — new `--captions-langs "ko,en"` (implies `--write-subs`): BOTH requested languages are planned per video (gap-fill, not first-found) via `manual → auto-generated → YouTube auto-TRANSLATED` (`automatic_captions` translation keys like `en-ko`) → `failed`; unavailable languages are not requested at all but recorded honestly. Manifest `subtitles[]` entries are now objects `{path, lang, source}` with `source ∈ manual | auto | translated | failed | unknown` (plain `--write-subs`/`--sub-langs` runs get the same tagging; when a probe exposes no caption data the legacy pattern string is passed through byte-for-byte). **Documented limitation**: YouTube's translation endpoint rate-limits (HTTP 429) — a robust pipeline should fall back to an external translation step keyed off the manifest's `failed` records (translation itself intentionally not implemented).
- **[2026-10-30]**: **Provenance**: reflects co-deck workspace validated rounds 4–6 of its deck-video pipeline — [ADR-0002 amendments](../../../ai_workspace/Projects/co-deck/docs/adr/0002-deck-video-asset-verification-and-injector-binding.md) (round 4: caption language selection config + YouTube auto-translated sidecars with `manual | auto | translated` source vocabulary; round 5: original-audio forcing against YouTube auto-dubbing; round 6: external LLM translation fallback when the translation endpoint 429s — QuickDL implements the acquisition + honest `failed` tagging so an external step can key off the manifest).
- **[2026-10-30]**: `locales/*.json`: 3 new `cli.*` keys across all 16 locales (baseline 72 → 75 keys).

### Added (2026-10-30 Co-deck Rounds 7–8 — Caption Coverage Gate, Cleaning Pipeline, Swap/Retire Provenance)
- **[2026-10-30]**: `verification.py` / `cli.py`: **Caption duration-coverage gate** — every manifest `subtitles[]` entry with a sidecar gains `coverage` (0–1: last VTT cue end ÷ video duration, clamped; null when the duration or cues are unknown). Coverage below the 0.95 threshold is a manifest WARNING by default; the new `--require-caption-coverage` flag (with `--verify`) turns it into a hard gate — any sidecar below the threshold, or a requested language whose source is `failed` (no captions at all), fails verification (exit code 2) so batch consumers can enforce "full-coverage captions or don't use this video". Catches the invisible production defect of a source caption track that stops mid-video (co-deck: captions covering only 0:00–5:22 of an 8:50 video, found only when a client watched past 5:22). Without `--verify`, the probe duration still annotates coverage + warnings into the manifest.
- **[2026-10-30]**: `download_service.py` / `cli.py`: **Caption cleaning pipeline** — every downloaded sidecar VTT is automatically cleaned in place before the manifest entry is built: inline `<c>`/timestamp markup stripped (entity-decoded), consecutive duplicate cue texts dropped (YouTube rolling-window ASR dedup, windows merged so no caption time is lost), and overlapping cue intervals clipped at the next cue's start (500 ms minimum window, so players never stack two cues). The raw grab is transient (overwritten); manifest `subtitles[]` entries record `cleaned: true` + the final cue count. Unreadable sidecars are left untouched and simply get no cleaned/cues fields — nothing is guessed.
- **[2026-10-30]**: `verification.py` / `cli.py`: **Swap/retire provenance** — new repeatable `--swap OLD_ID:NEW_URL` flag (plus optional `--swap-reason`): the batch entry matching the old 11-char video id is REMOVED from `videos[]` and moved to a top-level manifest `retired[]` list (same record shape as the co-deck video-manifest: `video_id`, `title`, `url`, `path`, `size_mb`, `duration_min`, `status`, plus `retired` date and `reason`); the replacement entry (matched by URL) is tagged `swapped_from` + `swap {date, reason}`. The exact swap directives are also recorded under `tool.swaps`. Swap directives whose old id is not in the batch are ignored. Fully additive: plain batches keep the exact previous manifest schema (no `retired` key unless swaps were requested).
- **[2026-10-30]**: **Provenance**: reflects co-deck workspace validated rounds 7–8 of its deck-video pipeline — [ADR-0002 amendments](../../../ai_workspace/Projects/co-deck/docs/adr/0002-deck-video-asset-verification-and-injector-binding.md) (rounds 5–7: caption coverage measurement exposing a swapped video whose source captions covered only 0:00–5:22 of 8:50, the tag-strip + rolling-dedup + overlap-clip cleaning pipeline that turned raw ASR grabs into clean 424-cue files, and the swap-with-retired-audit-trail manifest practice; round 8: the same records finalized in the production video-manifest). QuickDL implements the measurement, the cleaning, and the swap/retire manifest records natively.
- **[2026-10-30]**: `locales/*.json`: 3 new `cli.*` keys across all 16 locales (baseline 75 → 78 keys).

### Added
- **[2026-05-23]**: `.githooks/pre-commit`: Add Markdown date auto-bumper and CHANGELOG auto-dating logic. Automatically updates `Last Updated:` date in staged `.md` files upon commit, and injects date into undated `CHANGELOG.md` entries.
- **[2026-05-23]**: `docs/context.md`: Add `security-monitor` (Security group) to Agents table.
- **[2026-05-23]**: `AGENTS.md`: Register `security-monitor` agent formally in the global Agent Roster.

### Changed
- **[2026-05-23]**: Default Branch: Successfully migrated and synced the default project branch from `master` to the workspace standard `main`.

### Removed
- **[2026-05-23]**: `README.md` / `README_ko.md`: Remove obsolete manual kickoff instruction text.


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
