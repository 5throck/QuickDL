# QuickDL Project Constitution

These principles govern all work on QuickDL — human or AI. They are distilled
from this repository's own rules (`docs/context.md`, `AGENTS.md`,
`scripts/audit.sh`) and do not override them; when in doubt, the linked
source files are authoritative.

---

## 1. Project Purpose

QuickDL is a cross-platform YouTube video downloader (Python 3.8+, yt-dlp)
with three interfaces: a Flask web UI, a pywebview desktop app, and a CLI.
Core download logic lives in `download_service.py`; quality modes, caption
sidecars, verification gates, download manifests, and original-audio forcing
are first-class product capabilities documented in `README.md` and
`CHANGELOG.md`.

## 2. Required Reading (Read-First Rule)

Before starting any task, AI tools MUST load, in order:

1. `docs/context.md` — single source of truth for all AI tools (architecture,
   workflow, coding guidelines, git conventions).
2. `AGENTS.md` — agent registry and orchestration contract.
3. `memory/MEMORY.md` — session log index (when it exists).
4. `locales/en.json` — i18n baseline (for any i18n or template work).

## 3. Governance Workflow

All work is orchestrated by the PM agent (`agents/pm.md`) through a 6-phase
workflow: **Phase 0** Team Assembly → **Phase 1** Triage & Analysis (parallel
read-only dispatch of `security` + `qa`) → **Phase 2** Design (explicit user
approval gate) → **Phase 3** Implementation (serial writes: backend →
frontend → i18n) → **Phase 4** QA Verification → **Phase 5** Quality Gate →
**Phase 6** Finalization (memlog + PR). PM never edits code directly;
specialists write serially to avoid file-lock conflicts. Skills
(`post-write-check`, `i18n-audit`) run after every relevant write. Session
logs go to `memory/YYYY-MM-DD.md`; significant architecture decisions are
reflected back into `docs/context.md`.

## 4. Quality Gates (all must pass before merge)

| Gate | Command | Standard |
|------|---------|----------|
| Documentation audit | `bash scripts/audit.sh` | Exit 0 |
| Tests | `pytest tests/ -v` | All pass |

`audit.sh` enforces: `CHANGELOG.md` exists **and** contains an `[Unreleased]`
section; `CONSTITUTION.md` is accessible at the repo root; `docs/context.md`
has a `## Coding Guidelines` section; `AGENTS.md` exists; `agents/` contains
at least one agent file; and warns on `.sh`/`.ps1` script-parity gaps and a
missing `.env.sample`.

## 5. i18n Rule

QuickDL ships **16 locales**: en, ko, ja, zh-TW, zh-CN, de, es, fr, pt, vi,
ms, id, th, ru, it, ar. `locales/en.json` is the baseline — every other
locale file must have **identical keys**. The audit gate fails on key parity
violations; run the `i18n-audit` skill after any locale or `i18n.py` change.
Language detection: `QUICKDL_LANG` env var → OS locale → `en` fallback.

## 6. Coding Guidelines

- **Python 3.8+** — use `Optional[str]` from `typing`, not `str | None`.
- **UTF-8 (no BOM)** everywhere; open files with `encoding="utf-8"`. Script
  outputs specify the encoding explicitly.
- Single-responsibility functions (~30 lines max); no bare `except:` — catch
  specific exceptions; imports ordered stdlib → third-party → local.
- Follow SOLID; write unit tests when creating functional code.
- Never modify `.venv/` or `downloads/`; downloaded media is runtime output,
  not source.

## 7. Git & PR Conventions

- **PR-only**: all changes reach `main` via Pull Request — never a direct push.
- Use the project pipeline: `bash scripts/dev-sync.sh "type: description"`
  (memlog → MEMORY.md index → CHANGELOG → audit → branch → commit → push →
  `gh pr create`). Branches follow `pr/<YYYYMMDD-HHmmss>-<slug>`; manual
  branches use `feature/`, `fix/`, `chore/` prefixes.
- **Commit messages: English, imperative mood** ("Add feature", not "Added
  feature"). AI commits append the respective `Co-Authored-By:` tag.
- Stage specific files — avoid `git add -A` for manual commits (the
  dev-sync pipeline is the sanctioned exception). No force push to `main`.
- `CHANGELOG.md` (English) records *what* changed for users; `memory/` logs
  (English) record *how* and *why* for developers.

## 8. Security Rules

- Never expose or log secrets (API keys, tokens). No `.env` in the repo —
  only `.env.sample` as a template. Never commit private key material
  (`.gitignore` blocks `*.pem`, `*.key`, etc.).
- Do not modify CI/CD pipelines (`.github/workflows/`, `.githooks/`) without
  explicit user permission.
- Vulnerabilities are reported privately per `SECURITY.md` (GitHub Security
  Advisory) — never as public issues.
- The `security` agent audits new external input paths (injection, path
  traversal, CORS, dependencies) during Phase 1 and re-audits in Phase 4.

## 9. Documentation Language Policy

English-only documentation: all `.md` files, commit messages, PR titles and
bodies are written in English. `README_ko.md` is the sanctioned Korean
translation zone and must stay in sync with `README.md`.

---

*Adopted 2026-10-30. Derived from QuickDL's existing project rules; amend via
PR with corresponding updates to `docs/context.md` and `AGENTS.md`.*
