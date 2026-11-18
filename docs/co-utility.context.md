# QuickDL — co-utility Configuration

> Extends docs/context.md. This file IS the customization layer for this project.
> context.md is IMMUTABLE —all project-specific changes belong here.
>
> Read order for all AI tools:
>   1. docs/context.md              —immutable project identity (architecture, standards)
>   2. docs/co-utility.context.md   —THIS FILE —utility doctrine instantiation, workflow
>
> Variant: **co-utility** (beta template 0.1.0 doctrine — multi-interface utility
> apps over one core service; rebase from co-develop completed 2026-11-19).

---

## Utility Doctrine Instantiation

The co-utility variant doctrine (see `templates/co-utility/docs/co-utility.context.md`
upstream) applied to QuickDL's concrete shape:

| Doctrine area | QuickDL instantiation |
|---------------|----------------------|
| **Multi-interface surface matrix** | Core service `src/download_service.py`; adapters: web UI (`src/app.py` + `src/templates/`), desktop shell (`src/desktop.py`, pywebview + pystray), CLI (`src/cli.py`) |
| **Runtime-output isolation** | `downloads/` at repo root (gitignored, never source); `.venv/` repo-level; output root resolved from the repo layout, not `__file__` |
| **Locale-matrix i18n** | 16 locales (`src/locales/*.json`), `en.json` baseline key parity; runtime loader `src/i18n.py` (`SUPPORTED` set mirrors the directory); detection chain `QUICKDL_LANG` env → OS locale → `en` |
| **External-input security** | URL handling (yt-dlp), path construction from video titles/IDs, no subprocess with user strings; double-audited at Phase 1 and Phase 4 |
| **Cross-platform script pairing** | `ytdl.sh` / `ytdl.bat` launchers change together |

---

## Agents

<!-- context-proximity: agent roles summarized here for AI context window efficiency; authoritative definitions in agents/*.md -->

| Agent | File | Role | Tier | Status |
|-------|------|------|------|--------|
| PM (Orchestrator) | `agents/pm.md` | Workflow management, dispatch, quality gates | high | active |
| Backend | `agents/backend.md` | Core service, Flask API, CLI, installer | high | active |
| Frontend | `agents/frontend.md` | Web UI logic, API wiring, i18n in templates, desktop shell | medium | active |
| I18N Specialist | `agents/i18n-specialist.md` | Locale config/formatting/layout (common extends-stub); QuickDL specifics: `src/i18n.py`, 16-locale matrix | medium | active |
| QA | `agents/qa.md` | Test suite ownership (`tests/`, 111 tests), cross-platform validation | medium | active |
| Security | `agents/security.md` | External-input audits (read-only) + ongoing dependency/secret monitoring | high | active |

---

## Skills

| Skill | Source | Trigger |
|-------|--------|---------|
| `post-write-check` | variant-exclusive (`skills/post-write-check/`) | After any Write/Edit to source files |
| `i18n-audit` | common 1.0.2 (Runtime Loader Sync included) | After any locale file or `src/i18n.py` change |
| common set (sync, security-scan, ci-triage, lifecycle managers, …) | `templates/common` via `inherits_common` | Per workspace `VERSION_MANIFEST.md` |

---

## Workflow (utility phases)

`user → PM triage → Design Gate (unless exempt) → serial specialist dispatch → QA gate → /sync PR`

| Phase | Work | Agents |
|-------|------|--------|
| 1 Triage | classify, read-only research, acceptance criteria | pm + security, qa |
| 2 Design | design note for substantive changes; user approval gate | pm (frontend consulted for UI specs) |
| 3 Implementation | serial writes: core service → adapters → locales | backend → frontend → i18n-specialist |
| 4 QA Verification | full suite (111 tests); security re-audit of new input surfaces | qa, security |
| 5 Quality Gate | `bun scripts/audit.ts --skip-memory` exit 0 + `pytest tests/ -q` | pm |
| 6 Finalization | memlog, CHANGELOG, `/sync` PR | pm |

Full phase definitions: `docs/phase-definitions.md`.

---

## Domain Rules

1. **One core service** — every interface adapter calls `src/download_service.py`;
   duplicated logic across interfaces is a defect.
2. **Runtime output never lands in source** — `downloads/` stays repo-level and
   gitignored; agents never modify it or `.venv/`.
3. **Locale changes are atomic** — locale file + `SUPPORTED` + language selector +
   `tests/test_i18n.py` expectations in one change.
4. **External-input sinks are double-audited** — URL, path, subprocess (Phase 1 + Phase 4).
5. **Launcher pairs move together** — `ytdl.sh` and `ytdl.bat` change in the same commit.
