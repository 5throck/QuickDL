# Phase Definitions — QuickDL (co-utility)

This document defines the workflow phases used by this project under the
**co-utility** variant doctrine (multi-interface utility apps over one core
service). It follows the standard workspace phase structure (see
`templates/common/docs/phase-definitions.md`) with QuickDL's actual specialist
agents mapped to each phase, per each agent's `phases:` frontmatter field in
`agents/*.md` and the workflow table in `docs/co-utility.context.md`.

## Phase Map

| Phase | Name | Active Agents | Gate |
|-------|------|---------------|------|
| 0 | Team Assembly & Kickoff | pm | roster confirmed, `AGENTS.md`/context updated for new work types |
| 1 | Triage & Analysis | pm + security, qa (read-only) | acceptance criteria set; new external-input surfaces flagged for double audit |
| 2 | Design | pm (frontend consulted for UI layout specs) | Design Gate: design note registered or E1–E5 exemption; explicit user approval for UI changes |
| 3 | Implementation | backend → frontend → i18n-specialist (serial writes) | post-write-check green after every edit |
| 4 | QA Verification | qa + security | full suite `pytest tests/ -q` (111 tests); security re-audit of new input surfaces |
| 5 | Quality Gate | pm | `bun scripts/audit.ts --skip-memory` exit 0 |
| 6 | Finalization | pm | memlog + CHANGELOG + `/sync` PR |

## Agent-to-Phase Assignments

Per each agent's frontmatter `phases:` field in `agents/*.md`:

- **pm** — orchestrates every phase; never edits code directly (`memory/*.md` and
  `CHANGELOG.md` excepted).
- **backend** (Tier: High) — Phase 3 implementation of `src/download_service.py`,
  `src/app.py`, `src/cli.py`, `src/install.py`.
- **frontend** (Tier: Medium) — Phase 3 implementation of `src/static/js/script.js`,
  `src/templates/index.html`, `src/desktop.py`.
- **i18n-specialist** (Tier: Medium) — Phase 3 on locale deliverables: atomic changes
  across `src/locales/*.json` + `src/i18n.py` `SUPPORTED` + selector + tests.
- **qa** (Tier: Medium) — Phase 1 analysis and Phase 4 verification; writes only under
  `tests/`; the full suite is the acceptance bar.
- **security** (Tier: High) — Phase 1 read-only audit of new external-input surfaces and
  Phase 4 re-audit; ongoing dependency/secret monitoring; SEV-classified findings
  escalate to pm (SEV1/SEV2 block pushes).

## Utility-Specific Phase Rules

1. **Core-service-first ordering (Phase 3)** — a behavior change lands in
   `src/download_service.py` before any adapter (web UI, desktop shell, CLI)
   consumes it; adapters never duplicate service logic.
2. **Atomic locale changes (Phase 3)** — a locale addition or key change is one
   unit of work: locale file, `SUPPORTED` registry, language selector, and
   `tests/test_i18n.py` expectations move together. The common `i18n-audit`
   skill's Runtime Loader Sync step verifies the loader↔directory match.
3. **External-input double audit (Phase 1 + 4)** — URL handling, path
   construction from external names, and any subprocess use are audited at
   triage and re-audited before merge; findings follow the SEV classification.
4. **Runtime-output isolation (every phase)** — `downloads/` and `.venv/` stay
   repo-level and gitignored; output roots resolve from the repo layout, never
   `__file__`.
5. **Launcher pairing (Phase 3)** — `ytdl.sh` and `ytdl.bat` behavior changes
   land in both halves of the pair in the same change.

## Deviations from the Workspace-Standard Phase Model

- The PM role and Phase 0/6 structure follow the workspace standard unchanged.
- Co-utility keeps Design (Phase 2) and Implementation (Phase 3) separate, with
  serial specialist writes instead of a parallel write pool — file-lock safety
  over speed for a small utility team.
- There is no dedicated design agent: Phase 2 specs are PM-authored, with
  frontend consulted for UI layout.
