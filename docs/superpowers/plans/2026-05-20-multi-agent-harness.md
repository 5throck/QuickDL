# Multi-Agent Harness Engineering Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Set up shared agent-config docs and per-tool MD files (Claude Code, Codex, Gemini CLI) so any AI tool can be used independently with full project context, plus add Malay (ms) and Indonesian (id) locale support.

**Architecture:** A shared core (`docs/agent-config/shared.md` + `agents.md`) holds all project knowledge and agent role definitions. Three tool-specific entry-point files (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`) at the project root reference this shared core and add only tool-specific behavior on top. Locale files follow the existing flat-JSON pattern in `locales/`.

**Tech Stack:** Markdown (config docs), Python 3.8+ (i18n.py), JSON (locale files), Windows Batch + Bash (launcher scripts).

---

## File Map

| Action | Path | Responsibility |
|--------|------|----------------|
| Create | `docs/agent-config/shared.md` | Project context, conventions, stack, i18n, Git rules — shared by all tools |
| Create | `docs/agent-config/agents.md` | Agent role definitions (PM, Designer, Frontend, i18n, Security, Backend, QA) |
| Create | `CLAUDE.md` | Claude Code project-level config — references shared core, adds Superpowers workflow |
| Create | `AGENTS.md` | Codex project-level config — references shared core, adds sandbox constraints |
| Create | `GEMINI.md` | Gemini CLI project-level config — references shared core, adds @ syntax guide |
| Create | `locales/ms.json` | Malay translations for all 49 keys |
| Create | `locales/id.json` | Indonesian translations for all 49 keys |
| Modify | `i18n.py` line 8 | Add `"ms"` and `"id"` to `SUPPORTED` set |
| Modify | `ytdl.bat` lines 18-19 | Add ms/id warning strings before `echo %MSG%` |
| Modify | `ytdl.sh` lines 18-19 | Add ms/id case entries before `*)` fallback |

---

## Task 1: Create `docs/agent-config/shared.md`

**Files:**
- Create: `docs/agent-config/shared.md`

- [ ] **Step 1: Create the directory and file**

```bash
mkdir -p docs/agent-config
```

Create `docs/agent-config/shared.md` with this exact content:

```markdown
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
```

- [ ] **Step 2: Verify the file exists and is readable**

```bash
python -c "
with open('docs/agent-config/shared.md', encoding='utf-8') as f:
    lines = f.readlines()
print(f'OK: {len(lines)} lines')
"
```

Expected output: `OK: <N> lines` (no error)

- [ ] **Step 3: Commit**

```bash
git add docs/agent-config/shared.md
git commit -m "Add shared agent-config core (shared.md)"
```

---

## Task 2: Create `docs/agent-config/agents.md`

**Files:**
- Create: `docs/agent-config/agents.md`

- [ ] **Step 1: Create the file**

Create `docs/agent-config/agents.md` with this exact content:

```markdown
# QuickDL — Agent Role Definitions

> Referenced by `CLAUDE.md`, `AGENTS.md`, and `GEMINI.md`.
> When asked to act as a specific role, apply the scope, responsibilities, and output contract defined here.

---

## Agent Roster

| ID | Role | Primary Files |
|----|------|---------------|
| `pm` | Project Manager | `docs/`, task lists, specs, plans |
| `designer` | Designer | `templates/index.html`, `static/css/` |
| `frontend` | Frontend Developer | `templates/index.html`, `static/js/script.js` |
| `i18n` | i18n Expert | `locales/*.json`, `i18n.py`, `ytdl.bat`, `ytdl.sh` |
| `security` | Security Officer | All files (read-only audit) |
| `backend` | Backend Developer | `app.py`, `download_service.py`, `desktop.py`, `cli.py`, `install.py` |
| `qa` | QA Engineer | `test_api.py`, `test_env.py`, manual test checklists |

---

## Role Definitions

### PM — Project Manager

**Responsibilities:**
- Decompose feature requests into discrete, estimable tasks
- Maintain task list (create, update, resolve tasks)
- Write specs (`docs/superpowers/specs/`) and implementation plans (`docs/superpowers/plans/`)
- Resolve blockers by coordinating between roles
- Sign off on deliverables before merge

**Entry criteria:** New feature request, bug report, or planning session

**Output contract:**
- Spec document (`YYYY-MM-DD-<topic>-design.md`)
- Implementation plan (`YYYY-MM-DD-<feature>.md`) with bite-sized tasks and checkboxes
- Updated task list

**Hands off to:** Designer (UI changes), Backend Developer (logic changes), i18n Expert (translation changes)

---

### Designer

**Responsibilities:**
- Define UI/UX for the web interface (`templates/index.html`) and desktop window layout
- Specify HTML structure, CSS class naming, component hierarchy
- Ensure accessibility (ARIA labels, contrast, keyboard nav)
- Produce annotated mockups or HTML sketches for Frontend Developer to implement

**Scope:** `templates/index.html` (structure only, no JS logic), `static/css/`

**Entry criteria:** New UI component, layout change, or visual bug

**Output contract:**
- Annotated HTML skeleton or diff showing structural changes
- CSS class/variable naming spec
- Accessibility checklist

**Hands off to:** Frontend Developer (implementation), i18n Expert (new visible strings)

---

### Frontend Developer

**Responsibilities:**
- Implement Designer specs in `templates/index.html` and `static/js/script.js`
- Wire up API calls to Flask endpoints (`/api/info`, `/api/download`)
- Use `window.I18N['key']` for all user-visible strings in JS
- Use `{{ i18n['key'] }}` Jinja2 syntax for all static strings in HTML
- Never hardcode user-visible text in English directly

**Scope:** `templates/index.html`, `static/js/script.js`, `static/css/`

**Entry criteria:** Designer hands off spec, or JS bug reported

**Output contract:**
- Working implementation matching Designer spec
- All new strings added to `locales/en.json` with appropriate key
- Notify i18n Expert of new keys

**Hands off to:** i18n Expert (new translation keys), QA Engineer (testing)

---

### i18n Expert

**Responsibilities:**
- Maintain all files in `locales/` — ensure every locale has exactly the same keys as `locales/en.json`
- Update `i18n.py` `SUPPORTED` set when adding a new language
- Add new language strings to `ytdl.bat` and `ytdl.sh`
- Review translation quality (not just machine-translate)
- Audit for missing keys: `locales/en.json` is always the baseline

**Scope:** `locales/*.json`, `i18n.py`, `ytdl.bat`, `ytdl.sh`

**Entry criteria:** New language requested, new translation keys added by Frontend/Backend, i18n bug reported

**Key audit command:**
```bash
python -c "
import json, pathlib
base = json.loads(pathlib.Path('locales/en.json').read_text(encoding='utf-8'))
for p in sorted(pathlib.Path('locales').glob('*.json')):
    other = json.loads(p.read_text(encoding='utf-8'))
    missing = set(base) - set(other)
    extra = set(other) - set(base)
    status = 'OK' if not missing and not extra else f'MISSING={missing} EXTRA={extra}'
    print(f'{p.name}: {status}')
"
```

**Output contract:**
- All locale files have identical key sets to `en.json`
- `SUPPORTED` set in `i18n.py` matches the set of locale files
- Shell scripts updated for new languages

**Hands off to:** QA Engineer (validation)

---

### Security Officer

**Responsibilities:**
- Audit code for injection risks (URL params passed to subprocess, path traversal)
- Review `download_service.py` for unsafe yt-dlp option handling
- Check `app.py` for missing input validation on API endpoints
- Scan `requirements.txt` for known-vulnerable dependency versions
- Flag issues; does NOT implement fixes (hands off to Backend Developer)

**Scope:** All Python files (read-only audit)

**Entry criteria:** New feature touching external input or file system, periodic security review, dependency update

**Output contract:**
- Security audit report with severity (Critical / High / Medium / Low)
- Specific file + line references for each finding
- Recommended fix per finding

**Hands off to:** Backend Developer (fixes), PM (severity triage)

---

### Backend Developer

**Responsibilities:**
- Implement Flask routes in `app.py`
- Maintain download logic in `download_service.py` (yt-dlp integration)
- Manage desktop app lifecycle in `desktop.py` (Flask thread, pywebview, pystray queue)
- Maintain `cli.py` (argparse interface) and `install.py` (cross-platform setup)
- Ensure Python 3.8 compatibility (`Optional[str]`, no walrus operator in hot paths, etc.)

**Scope:** `app.py`, `download_service.py`, `desktop.py`, `cli.py`, `install.py`, `i18n.py`

**Entry criteria:** New API endpoint, download logic change, desktop app bug, installer issue

**Output contract:**
- Passing `python test_api.py` and `python test_env.py`
- No new bare `except:` clauses
- New user-visible strings use `t()` — not hardcoded

**Hands off to:** i18n Expert (new keys), QA Engineer (testing), Security Officer (new external input)

---

### QA Engineer

**Responsibilities:**
- Write and maintain test scripts (`test_api.py`, `test_env.py`)
- Validate cross-platform behavior (document Windows vs macOS/Linux differences)
- Run i18n completeness audit (see i18n Expert audit command)
- Verify installer idempotency (run `install.py` twice, confirm no errors)
- Test CLI with valid and invalid URLs

**Scope:** `test_api.py`, `test_env.py`, manual test checklists

**Entry criteria:** After any Backend or Frontend change, before release

**Test checklist template:**
```
[ ] python test_api.py  — all assertions pass
[ ] python test_env.py  — all assertions pass
[ ] QUICKDL_LANG=en python cli.py --help  — English output
[ ] QUICKDL_LANG=ko python cli.py --help  — Korean output
[ ] python install.py (second run)  — reports "already exists", no errors
[ ] All locale files: same 49 keys as en.json
[ ] ytdl.bat exists and has correct .venv check logic
[ ] ytdl.sh exists and is executable
```

**Output contract:**
- Test run output (pass/fail per test)
- List of any cross-platform issues found

**Hands off to:** Backend Developer or Frontend Developer (bug fixes), PM (release decision)
```

- [ ] **Step 2: Verify the file**

```bash
python -c "
with open('docs/agent-config/agents.md', encoding='utf-8') as f:
    content = f.read()
roles = ['pm', 'designer', 'frontend', 'i18n', 'security', 'backend', 'qa']
for r in roles:
    assert r in content, f'Missing role: {r}'
print('OK: all 7 roles present')
"
```

Expected: `OK: all 7 roles present`

- [ ] **Step 3: Commit**

```bash
git add docs/agent-config/agents.md
git commit -m "Add agent role definitions (agents.md)"
```

---

## Task 3: Create `CLAUDE.md` (project-level)

**Files:**
- Create: `CLAUDE.md`

Note: `C:/git/CLAUDE.md` is the workspace-level config. This file is the **project-level** override at `C:/git/youtube/CLAUDE.md`.

- [ ] **Step 1: Create the file**

Create `CLAUDE.md` at the project root with this content:

```markdown
# CLAUDE.md — QuickDL (Project-Level)

> **Shared context:** Read `docs/agent-config/shared.md` first.
> **Agent roles:** See `docs/agent-config/agents.md`.

---

## Claude Code — Project-Specific Behavior

### Superpowers Workflow

Always follow the Superpowers skill hierarchy:
1. **brainstorming** → design spec (`docs/superpowers/specs/`)
2. **writing-plans** → implementation plan (`docs/superpowers/plans/`)
3. **subagent-driven-development** → execute plan task-by-task

Do NOT skip brainstorming for non-trivial changes. Even "simple" tasks need a design.

### Plan Mode

Enter plan mode (`EnterPlanMode`) when:
- User requests a new feature or significant refactor
- The change touches more than 2 files
- The correct approach is unclear

### Task Tracking

- Call `TaskCreate` before starting any multi-step work
- Set status `in_progress` before beginning a task
- Set status `completed` immediately after finishing
- Never leave tasks `in_progress` at end of session

### Subagent Pattern

Each implementation task:
1. Fresh subagent executes the task
2. Spec-compliance review subagent checks the result
3. Code-quality review subagent checks for issues
4. Fix and re-review if issues found (max 3 iterations)

### Response Language

Respond in **Korean** unless the user writes in English.

### Git

Follow conventions in `docs/agent-config/shared.md`.
Append to AI commits: `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`
```

- [ ] **Step 2: Verify**

```bash
python -c "
with open('CLAUDE.md', encoding='utf-8') as f:
    c = f.read()
assert 'docs/agent-config/shared.md' in c
assert 'docs/agent-config/agents.md' in c
print('OK: references present')
"
```

- [ ] **Step 3: Commit**

```bash
git add CLAUDE.md
git commit -m "Add project-level CLAUDE.md for Claude Code"
```

---

## Task 4: Create `AGENTS.md` (Codex)

**Files:**
- Create: `AGENTS.md`

- [ ] **Step 1: Create the file**

Create `AGENTS.md` at the project root:

```markdown
# AGENTS.md — QuickDL (Codex)

> **Shared context:** Read `docs/agent-config/shared.md` first.
> **Agent roles:** See `docs/agent-config/agents.md`.

---

## Codex — Project-Specific Behavior

### Sandbox Constraints

Codex runs without outbound internet access. This means:
- `download_service.download_video()` cannot actually download files — use mocks/stubs in tests
- `download_service.get_video_info()` cannot call YouTube — return fixture data in tests
- Do NOT attempt to `pip install` additional packages; use what is in `requirements.txt`

### Never Modify

- `.venv/` — virtual environment contents are off-limits
- `downloads/` — output directory; do not create test files here

### After Every Change

Run both test scripts and confirm they pass:
```bash
python test_api.py
python test_env.py
```

If a test script does not exist yet for the feature being added, write one.

### Editing Rules

- Prefer editing existing files over creating new ones
- When creating a new file, verify the parent directory exists first
- All user-visible strings must use `t('key')` — never hardcode English text

### Response Language

Respond in **English**.

### Git

Follow conventions in `docs/agent-config/shared.md`.
Append to AI commits: `Co-Authored-By: Codex <noreply@openai.com>`
```

- [ ] **Step 2: Verify**

```bash
python -c "
with open('AGENTS.md', encoding='utf-8') as f:
    c = f.read()
assert 'docs/agent-config/shared.md' in c
assert 'docs/agent-config/agents.md' in c
assert 'Sandbox' in c
print('OK')
"
```

- [ ] **Step 3: Commit**

```bash
git add AGENTS.md
git commit -m "Add project-level AGENTS.md for Codex"
```

---

## Task 5: Create `GEMINI.md` (Gemini CLI)

**Files:**
- Create: `GEMINI.md`

- [ ] **Step 1: Create the file**

Create `GEMINI.md` at the project root:

```markdown
# GEMINI.md — QuickDL (Gemini CLI)

> **Shared context:** Read `docs/agent-config/shared.md` first.
> **Agent roles:** See `docs/agent-config/agents.md`.
>
> In Gemini CLI, load context files with `@` syntax:
> ```
> @docs/agent-config/shared.md
> @docs/agent-config/agents.md
> ```

---

## Gemini CLI — Project-Specific Behavior

### Tool Name Mapping

Gemini CLI uses different tool names from Claude Code:

| Claude Code | Gemini CLI |
|-------------|-----------|
| `Read` | `read_file` |
| `Edit` | `edit` |
| `Write` | `write_file` |
| `Bash` | `shell` |
| `Grep` | `grep` |
| `Glob` | `find_files` |

### Loading Context

Always load shared context at the start of a session:
```
@docs/agent-config/shared.md
```

For i18n work, also load the baseline locale:
```
@locales/en.json
```

### i18n Workflow

When working on translations:
1. Load `@locales/en.json` as the baseline
2. Run the key audit to find missing keys (see i18n Expert in `agents.md`)
3. Add missing keys to the target locale file — do not remove or rename existing keys
4. Never machine-translate without review

### Editing Files

- Use `edit` for modifying existing files (preferred)
- Use `write_file` for creating new files
- Always `read_file` before editing to get current content

### Response Language

Respond in **English**.

### Git

Follow conventions in `docs/agent-config/shared.md`.
Append to AI commits: `Co-Authored-By: Gemini <noreply@google.com>`
```

- [ ] **Step 2: Verify**

```bash
python -c "
with open('GEMINI.md', encoding='utf-8') as f:
    c = f.read()
assert 'docs/agent-config/shared.md' in c
assert 'docs/agent-config/agents.md' in c
assert '@' in c
print('OK')
"
```

- [ ] **Step 3: Commit**

```bash
git add GEMINI.md
git commit -m "Add project-level GEMINI.md for Gemini CLI"
```

---

## Task 6: Add Malay and Indonesian locale files

**Files:**
- Create: `locales/ms.json`
- Create: `locales/id.json`

- [ ] **Step 1: Create `locales/ms.json`**

```json
{
  "cli.description": "QuickDL — Pemuat turun video YouTube",
  "cli.help_output": "Folder output (lalai: ./downloads)",
  "cli.fetching": "📥 Mendapatkan maklumat video...",
  "cli.error": "❌ Ralat: {e}",
  "cli.unknown": "Tidak diketahui",
  "cli.title_line": "🎦 Tajuk: {title} ({duration})",
  "cli.channel_line": "   Saluran: {channel}",
  "cli.downloading": "⬇️  Memuat turun...",
  "cli.saved": "✅ Disimpan: {saved_path}",
  "cli.done": "✅ Muat turun selesai. Disimpan ke: {output}",
  "cli.download_failed": "❌ Muat turun gagal: {e}",

  "install.start": "🚀 Memulakan pemasangan QuickDL...",
  "install.os_info": "   OS: {system} / Python: {version}",
  "install.python_ok": "✅ Python {version} dikesan",
  "install.python_bad": "❌ Python 3.8 atau lebih tinggi diperlukan.",
  "install.ffmpeg_ok": "✅ ffmpeg dikesan",
  "install.ffmpeg_missing": "⚠️  ffmpeg tidak dijumpai. Penggabungan MP4 berkualiti tinggi mungkin terhad.",
  "install.ffmpeg_win": "   Pasang: https://ffmpeg.org/download.html atau 'winget install ffmpeg'",
  "install.ffmpeg_mac": "   Pasang: brew install ffmpeg",
  "install.ffmpeg_linux": "   Pasang: sudo apt install ffmpeg  (atau pengurus pakej distro anda)",
  "install.venv_exists": "✅ Persekitaran maya sudah wujud: {path}",
  "install.venv_broken": "⚠️  Persekitaran maya rosak. Mencipta semula: {path}",
  "install.venv_creating": "📦 Mencipta persekitaran maya: {path}",
  "install.packages_installing": "📦 Memasang pakej...",
  "install.packages_done": "✅ Pakej berjaya dipasang",
  "install.env_setting": "🔧 Menetapkan pemboleh ubah persekitaran...",
  "install.env_already": "✅ PYTHONIOENCODING sudah ditetapkan kepada utf-8",
  "install.env_set_win": "✅ PYTHONIOENCODING=utf-8 ditetapkan (berkuat kuasa selepas log masuk semula)",
  "install.env_set_unix": "✅ PYTHONIOENCODING=utf-8 → ditambah ke {rc}",
  "install.env_source": "   Guna: source {rc}",
  "install.done_title": "🎉 Pemasangan QuickDL selesai!",
  "install.done_desktop": "   Apl desktop: {cmd}",
  "install.done_cli": "   CLI:         {cmd}",

  "desktop.server_error_msg": "Gagal memulakan pelayan.",
  "desktop.server_error_print": "RALAT: Pelayan gagal dimulakan",
  "desktop.tray_open": "Buka Tetingkap",
  "desktop.tray_quit": "Keluar",

  "app.error_url_required": "URL diperlukan.",
  "app.download_complete": "Muat turun selesai.",

  "ui.subtitle": "Pemuat turun video YouTube yang moden dan pantas",
  "ui.placeholder": "Tampal pautan YouTube di sini...",
  "ui.btn_fetch": "Dapatkan",
  "ui.btn_download": "Muat Turun MP4",
  "ui.loading_info": "Memuatkan maklumat video...",
  "ui.error_info": "Gagal memuatkan maklumat video.",
  "ui.downloading": "Memuat turun...",
  "ui.error_download": "Muat turun gagal.",
  "ui.success": "✅ Berjaya! Fail disimpan ke: {filepath}",

  "shell.venv_missing": "[Amaran] .venv tidak dijumpai. Sila jalankan dahulu: python install.py"
}
```

- [ ] **Step 2: Create `locales/id.json`**

```json
{
  "cli.description": "QuickDL — Pengunduh video YouTube",
  "cli.help_output": "Folder output (default: ./downloads)",
  "cli.fetching": "📥 Mengambil informasi video...",
  "cli.error": "❌ Kesalahan: {e}",
  "cli.unknown": "Tidak diketahui",
  "cli.title_line": "🎦 Judul: {title} ({duration})",
  "cli.channel_line": "   Saluran: {channel}",
  "cli.downloading": "⬇️  Mengunduh...",
  "cli.saved": "✅ Tersimpan: {saved_path}",
  "cli.done": "✅ Unduhan selesai. Disimpan ke: {output}",
  "cli.download_failed": "❌ Unduhan gagal: {e}",

  "install.start": "🚀 Memulai instalasi QuickDL...",
  "install.os_info": "   OS: {system} / Python: {version}",
  "install.python_ok": "✅ Python {version} terdeteksi",
  "install.python_bad": "❌ Python 3.8 atau lebih tinggi diperlukan.",
  "install.ffmpeg_ok": "✅ ffmpeg terdeteksi",
  "install.ffmpeg_missing": "⚠️  ffmpeg tidak ditemukan. Penggabungan MP4 berkualitas tinggi mungkin terbatas.",
  "install.ffmpeg_win": "   Instal: https://ffmpeg.org/download.html atau 'winget install ffmpeg'",
  "install.ffmpeg_mac": "   Instal: brew install ffmpeg",
  "install.ffmpeg_linux": "   Instal: sudo apt install ffmpeg  (atau manajer paket distro Anda)",
  "install.venv_exists": "✅ Lingkungan virtual sudah ada: {path}",
  "install.venv_broken": "⚠️  Lingkungan virtual rusak. Membuat ulang: {path}",
  "install.venv_creating": "📦 Membuat lingkungan virtual: {path}",
  "install.packages_installing": "📦 Menginstal paket...",
  "install.packages_done": "✅ Paket berhasil diinstal",
  "install.env_setting": "🔧 Mengatur variabel lingkungan...",
  "install.env_already": "✅ PYTHONIOENCODING sudah diatur ke utf-8",
  "install.env_set_win": "✅ PYTHONIOENCODING=utf-8 diatur (berlaku setelah login ulang)",
  "install.env_set_unix": "✅ PYTHONIOENCODING=utf-8 → ditambahkan ke {rc}",
  "install.env_source": "   Terapkan: source {rc}",
  "install.done_title": "🎉 Instalasi QuickDL selesai!",
  "install.done_desktop": "   Aplikasi desktop: {cmd}",
  "install.done_cli": "   CLI:              {cmd}",

  "desktop.server_error_msg": "Gagal memulai server.",
  "desktop.server_error_print": "ERROR: Server gagal dimulai",
  "desktop.tray_open": "Buka Jendela",
  "desktop.tray_quit": "Keluar",

  "app.error_url_required": "URL diperlukan.",
  "app.download_complete": "Unduhan selesai.",

  "ui.subtitle": "Pengunduh video YouTube yang modern dan cepat",
  "ui.placeholder": "Tempel tautan YouTube di sini...",
  "ui.btn_fetch": "Ambil",
  "ui.btn_download": "Unduh MP4",
  "ui.loading_info": "Memuat informasi video...",
  "ui.error_info": "Gagal memuat informasi video.",
  "ui.downloading": "Mengunduh...",
  "ui.error_download": "Unduhan gagal.",
  "ui.success": "✅ Berhasil! File disimpan ke: {filepath}",

  "shell.venv_missing": "[Peringatan] .venv tidak ditemukan. Jalankan terlebih dahulu: python install.py"
}
```

- [ ] **Step 3: Verify key count matches en.json**

```bash
python -c "
import json
from pathlib import Path
base = json.loads(Path('locales/en.json').read_text(encoding='utf-8'))
for lang in ['ms', 'id']:
    other = json.loads(Path(f'locales/{lang}.json').read_text(encoding='utf-8'))
    missing = set(base) - set(other)
    extra = set(other) - set(base)
    if missing or extra:
        print(f'{lang}: MISSING={missing} EXTRA={extra}')
    else:
        print(f'{lang}: OK ({len(other)} keys)')
"
```

Expected:
```
ms: OK (49 keys)
id: OK (49 keys)
```

- [ ] **Step 4: Commit**

```bash
git add locales/ms.json locales/id.json
git commit -m "Add Malay (ms) and Indonesian (id) locale files"
```

---

## Task 7: Update `i18n.py` and shell scripts

**Files:**
- Modify: `i18n.py` line 8
- Modify: `ytdl.bat`
- Modify: `ytdl.sh`

- [ ] **Step 1: Update `SUPPORTED` in `i18n.py`**

Change line 8 of `i18n.py`:

```python
# Before
SUPPORTED = {"ko", "en", "ja", "zh-TW", "zh-CN", "de", "es", "fr", "pt", "vi"}

# After
SUPPORTED = {"ko", "en", "ja", "zh-TW", "zh-CN", "de", "es", "fr", "pt", "vi", "ms", "id"}
```

- [ ] **Step 2: Verify i18n.py accepts ms and id**

```bash
python -c "
import sys; sys.path.insert(0, '.')
import i18n
i18n.init('ms')
print('ms:', i18n.t('cli.fetching'))
i18n.init('id')
print('id:', i18n.t('cli.fetching'))
"
```

Expected:
```
ms: 📥 Mendapatkan maklumat video...
id: 📥 Mengambil informasi video...
```

- [ ] **Step 3: Update `ytdl.bat`**

Add two lines before `echo %MSG%` in the else block (after the `vi` line):

```bat
    if "%QUICKDL_LANG%"=="ms" set "MSG=[Amaran] .venv tidak dijumpai. Sila jalankan dahulu: python install.py"
    if "%QUICKDL_LANG%"=="id" set "MSG=[Peringatan] .venv tidak ditemukan. Jalankan terlebih dahulu: python install.py"
```

- [ ] **Step 4: Update `ytdl.sh`**

Add two lines before `*)` fallback in the case block (after the `vi)` line):

```sh
        ms)    MSG="[Amaran] .venv tidak dijumpai. Sila jalankan dahulu: python install.py" ;;
        id)    MSG="[Peringatan] .venv tidak ditemukan. Jalankan terlebih dahulu: python install.py" ;;
```

- [ ] **Step 5: Verify shell scripts contain ms and id**

```bash
python -c "
for fname in ['ytdl.bat', 'ytdl.sh']:
    with open(fname, encoding='utf-8') as f:
        content = f.read()
    for lang in ['ms', 'id']:
        assert lang in content, f'{fname} missing {lang}'
    print(f'{fname}: OK')
"
```

- [ ] **Step 6: Commit**

```bash
git add i18n.py ytdl.bat ytdl.sh
git commit -m "Add ms/id language support to i18n.py and shell launchers"
```

---

## Task 8: Final validation and push

- [ ] **Step 1: Run full i18n audit**

```bash
python -c "
import json
from pathlib import Path
base = json.loads(Path('locales/en.json').read_text(encoding='utf-8'))
all_ok = True
for p in sorted(Path('locales').glob('*.json')):
    other = json.loads(p.read_text(encoding='utf-8'))
    missing = set(base) - set(other)
    extra = set(other) - set(base)
    status = 'OK' if not missing and not extra else f'FAIL missing={missing} extra={extra}'
    print(f'{p.name:15} {status}')
    if 'FAIL' in status:
        all_ok = False
print()
print('All locales OK' if all_ok else 'ISSUES FOUND')
"
```

Expected: all 12 locale files show `OK`.

- [ ] **Step 2: Verify all config files exist**

```bash
python -c "
import pathlib
files = [
    'CLAUDE.md', 'AGENTS.md', 'GEMINI.md',
    'docs/agent-config/shared.md',
    'docs/agent-config/agents.md',
]
for f in files:
    p = pathlib.Path(f)
    print(f'{f}: {\"OK\" if p.exists() else \"MISSING\"}'  )
"
```

Expected: all 5 files show `OK`.

- [ ] **Step 3: Verify SUPPORTED languages match locale files**

```bash
python -c "
import sys; sys.path.insert(0, '.')
import i18n, pathlib
locale_files = {p.stem for p in pathlib.Path('locales').glob('*.json')}
missing_from_supported = locale_files - i18n.SUPPORTED
missing_locale_files = i18n.SUPPORTED - locale_files
print('In locales/ but not SUPPORTED:', missing_from_supported or 'none')
print('In SUPPORTED but no locale file:', missing_locale_files or 'none')
"
```

Expected: both lines show `none`.

- [ ] **Step 4: Push to remote**

```bash
git push origin master
```
