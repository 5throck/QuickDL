# QuickDL — Multi-Agent Harness Engineering Design

## Context

QuickDL is a cross-platform YouTube downloader with a Flask web UI, desktop app (pywebview), system tray (pystray), and CLI. The project supports 10 languages via a flat-JSON i18n system. Development is carried out using multiple AI coding tools independently: Claude Code, Codex (OpenAI), and Gemini CLI. This spec defines the harness engineering configuration to ensure consistent conventions, shared project context, and well-defined agent roles across all tools.

## Goals

1. Each AI tool can be used independently with full project context from a single entry-point config file.
2. Project conventions, directory structure, i18n system, and Git rules are defined once in a shared core and referenced by all tool configs.
3. Agent roles (PM, Designer, Frontend Developer, i18n Expert, Security Officer, Backend Developer, QA Engineer) are defined in a single authoritative file and shared across all tools.
4. Adding Malaysian (ms) and Indonesian (id) locale support completes the language set to 12.

## Non-Goals

- Automated agent-to-agent communication or orchestration pipelines.
- CI/CD integration.
- Changing the existing Flask/pywebview architecture.

---

## Architecture

### File Layout

```
C:/git/youtube/
├── CLAUDE.md                        # Claude Code — project-level config
├── AGENTS.md                        # Codex — project-level config
├── GEMINI.md                        # Gemini CLI — project-level config
├── docs/
│   └── agent-config/
│       ├── shared.md                # Shared: project context + conventions
│       └── agents.md                # Shared: agent role definitions
│   └── superpowers/
│       ├── specs/                   # Design specs (this file lives here)
│       └── plans/                   # Implementation plans
├── locales/
│   ├── ms.json                      # NEW: Malay
│   └── id.json                      # NEW: Indonesian
├── i18n.py                          # Add "ms", "id" to SUPPORTED set
├── ytdl.bat                         # Add ms/id warning strings
└── ytdl.sh                          # Add ms/id warning strings
```

### Reference Chain

```
CLAUDE.md ──┐
AGENTS.md ──┼──▶ docs/agent-config/shared.md ──▶ docs/agent-config/agents.md
GEMINI.md ──┘
```

Each tool-specific file (`CLAUDE.md`, `AGENTS.md`, `GEMINI.md`) declares the shared core path at the top, then adds only tool-specific sections below. This ensures:
- Any tool used independently gets the full project context.
- Agent role definitions are maintained in one place.
- Tool-specific behavior (e.g., Codex sandbox constraints, Gemini `@` syntax) stays isolated.

---

## Component Designs

### 1. `docs/agent-config/shared.md`

**Purpose:** Single source of truth for project knowledge shared across all tools.

**Sections:**
- **Project Overview** — QuickDL purpose, tech stack (Flask, pywebview, pystray, yt-dlp, Pillow)
- **Directory Structure** — annotated file tree with each file's role
- **i18n System** — how `i18n.py` works, `locales/` layout, 12 supported languages, `QUICKDL_LANG` env var
- **Coding Conventions** — Python 3.8+ (`Optional[str]` not `str | None`), UTF-8 everywhere, single-responsibility functions, no bare `except`
- **Git Conventions** — commit messages in English, imperative mood, co-author trailer for AI commits
- **Running the Project** — `python app.py`, `python cli.py <URL>`, `python desktop.py`, `python install.py`
- **Testing** — `python test_api.py`, `python test_env.py`; no test framework installed, plain `assert`-based scripts

### 2. `docs/agent-config/agents.md`

**Purpose:** Authoritative definition of all agent roles used in multi-agent development.

**Agents defined:**

| Role | ID | Responsibilities |
|------|----|-----------------|
| Project Manager | `pm` | Decompose features into tasks, maintain task list, resolve blockers, sign off on deliverables |
| Designer | `designer` | UI/UX decisions for web UI and desktop window, HTML/CSS structure, accessibility |
| Frontend Developer | `frontend` | `templates/index.html`, `static/js/script.js`, `static/css/` — implement Designer specs |
| i18n Expert | `i18n` | Maintain `locales/*.json`, `i18n.py`, shell script locale strings; ensure translation quality |
| Security Officer | `security` | Review for injection risks, path traversal, unsafe subprocess calls, dependency CVEs |
| Backend Developer | `backend` | `app.py`, `download_service.py`, `desktop.py`, `cli.py`, `install.py` — Flask routes and download logic |
| QA Engineer | `qa` | Write and run test scripts, verify cross-platform behavior, validate i18n completeness |

**Per-agent entry includes:**
- Role ID and display name
- Scope (which files/directories owned)
- Entry criteria (when to engage this agent)
- Output contract (what deliverables are expected)
- Collaboration points (which other roles to hand off to)

### 3. `CLAUDE.md` (project-level)

**Purpose:** Claude Code configuration for this project.

**Sections:**
- Reference to `docs/agent-config/shared.md` and `docs/agent-config/agents.md`
- Superpowers workflow: brainstorming → writing-plans → subagent implementation
- Plan mode entry conditions
- Task tracking (TaskCreate/TaskUpdate before/after each task)
- Subagent review pattern (spec compliance + code quality per task)
- Language: respond in Korean (matching user preference)

### 4. `AGENTS.md` (Codex)

**Purpose:** Codex configuration for this project.

**Sections:**
- Reference to `docs/agent-config/shared.md` and `docs/agent-config/agents.md`
- Sandbox constraints: no outbound network → yt-dlp actual downloads unavailable; use mock/stub
- Never modify `.venv/` contents
- Test after every change: run `python test_api.py` and `python test_env.py`
- Prefer editing existing files over creating new ones
- Language: respond in English

### 5. `GEMINI.md` (Gemini CLI)

**Purpose:** Gemini CLI configuration for this project.

**Sections:**
- Reference to `docs/agent-config/shared.md` and `docs/agent-config/agents.md`
- `@` file reference syntax for loading context (e.g., `@docs/agent-config/shared.md`)
- Tool name mapping: Read→read_file, Edit→edit, Bash→shell, Grep→grep
- i18n workflow: always use `locales/en.json` as the reference baseline; diff against other locales to find missing keys
- Language: respond in English

### 6. i18n Additions (ms, id)

**`locales/ms.json`** — Malay translations of all 49 keys. Based on `locales/en.json` baseline.

**`locales/id.json`** — Indonesian translations of all 49 keys. Based on `locales/en.json` baseline.

**`i18n.py` change:**
```python
# Before
SUPPORTED = {"ko", "en", "ja", "zh-TW", "zh-CN", "de", "es", "fr", "pt", "vi"}
# After
SUPPORTED = {"ko", "en", "ja", "zh-TW", "zh-CN", "de", "es", "fr", "pt", "vi", "ms", "id"}
```

**`ytdl.bat` additions:**
```bat
if "%QUICKDL_LANG%"=="ms" set "MSG=[Amaran] .venv tidak dijumpai. Sila jalankan dahulu: python install.py"
if "%QUICKDL_LANG%"=="id" set "MSG=[Peringatan] .venv tidak ditemukan. Jalankan terlebih dahulu: python install.py"
```

**`ytdl.sh` additions:**
```sh
ms) MSG="[Amaran] .venv tidak dijumpai. Sila jalankan dahulu: python install.py" ;;
id) MSG="[Peringatan] .venv tidak ditemukan. Jalankan terlebih dahulu: python install.py" ;;
```

---

## Implementation Order

1. `docs/agent-config/shared.md` — foundation; all other files depend on it
2. `docs/agent-config/agents.md` — role definitions; referenced by tool configs
3. `CLAUDE.md` (project-level) — Claude Code config
4. `AGENTS.md` — Codex config
5. `GEMINI.md` — Gemini CLI config
6. `locales/ms.json` + `locales/id.json` — new locale files
7. `i18n.py` — add ms/id to SUPPORTED
8. `ytdl.bat` + `ytdl.sh` — add ms/id warning strings
9. Git commit + push

---

## Validation

- Open `CLAUDE.md` in a fresh Claude Code session → can work on QuickDL without needing other context
- Open `AGENTS.md` in Codex → project structure and constraints clear; agent roles accessible
- Open `GEMINI.md` in Gemini CLI → `@docs/agent-config/shared.md` loads full context
- `QUICKDL_LANG=ms python cli.py --help` → Malay output
- `QUICKDL_LANG=id python cli.py --help` → Indonesian output
- All 12 locale files have exactly the same 49 keys (no missing keys)
