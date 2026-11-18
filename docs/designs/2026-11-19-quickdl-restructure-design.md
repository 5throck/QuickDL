# QuickDL restructure: src/ layout, graft→trail, lean roster, doc pruning — design

- **Spec ID**: 2026-11-19-quickdl-restructure-design
- **Status**: Implemented (2026-11-19)
- **Date**: 2026-11-19
- **Scope**: QuickDL project (L3, co-develop 0.30.0) + upstream reflection into ai_workspace templates

## 1. Problem

The workspace adoption (2026-11-19) delivered the full co-develop surface onto a small
utility project. Four friction areas emerged: (a) flat root layout mixing Python app code
with repo meta; (b) graft-era residue after the vendor renamed to trail (0.28–0.29);
(c) a 16-agent roster where 10 template-generic agents duplicate QuickDL's domain team;
(d) delivered design-system/procedure/engagement docs with no bearing on a utility app.

## 2. Decisions

1. **src/ layout**: all Python modules + runtime assets (`locales/`, `templates/`, `static/`)
   move under `src/`. Flask default discovery keeps working (app.py adjacent to its
   templates). `downloads/` and `.venv`/`requirements.txt` stay at the repo root —
   runtime output and environment are repo-level, not source. `i18n.py` resolves
   `locales/` via `__file__`, so co-locating locales under `src/` requires no code change.
2. **graft → trail (R2.4)**: `trail init --yes` rewrites AGENTS/GEMINI markers, MCP entries
   and hooks; graft permissions/cache removed. `.mcp.json` deletion is confirmed via the
   upgrade engine's tombstone mechanism (trail MCP lives in `.claude/settings.json`).
3. **Roster**: keep pm, backend, frontend, qa, security (security-monitor absorbed as an
   ongoing-monitoring section of security.md); use the delivered workspace-standard
   `i18n-specialist` instead of QuickDL's `i18n` (fork-avoidance). The 10 template-generic
   agents are tombstoned, not deleted-locally — later waves skip them.
4. **i18n knowledge upstream**: QuickDL's runtime-loader sync check (i18n.py `SUPPORTED`
   ↔ `locales/*.json`) is generalized into common `i18n-audit` 1.0.2 ("Runtime Loader
   Sync" step); project-specific locale doctrine stays in `docs/context.md` §i18n System.
5. **Doc pruning**: design-system/procedure/engagement assets tombstoned (list in §3);
   gate-referenced docs (VERSION_MANIFEST, skill-graph, workspace-schema, phase-definitions,
   standards/, governance/) retained.
6. **designLint**: disabled via `variant.json designLint {enabled:false}` — QuickDL ships
   deliberately token-free vanilla CSS; the design-token gate presumes a design-system
   variant posture.
7. **co-utility variant** (upstream): new `templates/co-utility` (beta, variant_type
   `utility` registered) carrying the utility doctrine (from the archived QuickDL
   CONSTITUTION.md) + specialization areas, WITHOUT re-delivering the pruned doc set.

## 3. Tombstone set

docs/{design-foundation.md, design-tokens.template.css, components.template.md,
screen-patterns.template.md, benchmark-fixtures/, stack-profile.json,
privacy-design-checklist.md, privacy-design-checklist_ko.md, country-profiles.md,
procedure-schema-spec.md, user-guide.md, user-guide_ko.md, README.template.md,
README_ko.template.md, handoff-spec.md, handoff-spec_ko.md}, .mcp.json,
agents/{architect,code-writer,test-runner,stack-setup,designer,automation-engineer,
design-system-lead,contract-gate-engineer,i18n,security-monitor}.md.

## 4. Verification

- `bun scripts/audit.ts` (full) exit 0; `pytest tests/ -q` 111 passed
- `trail check` clean; co-deck `download-videos.ts selftest` OK against src/ layout
- tombstone paths skip silently-but-visibly (TOMBSTONED_SKIP) at the next upgrade wave
