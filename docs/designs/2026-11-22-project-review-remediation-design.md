# Project review remediation batch (2026-11-22 full review) — design

- **Spec ID**: 2026-11-22-project-review-remediation-design
- **Status**: Implemented (2026-11-22)
- **Date**: 2026-11-22
- **Source**: docs/reports/2026-11-22-project-review-full.md (full review, 4 domain slots + machine battery)

## 1. Problem

The full project review found 6 Critical / 13 High / 22 Moderate findings, most rooted in
the 2026-11-19 rebase residue (co-develop → co-utility + src/ move updated primary
surfaces but left secondary surfaces stale).

## 2. Decisions (fix-now batch, this spec)

1. Untrack `.claude/settings.local.json` (personal grants were shipped to every clone;
   ignore rule ineffective for tracked files).
2. CI i18n audit path `locales/en.json` → `src/locales/en.json` (test job was red on
   every run since the src/ move).
3. Live command surfaces (`/sync` in .claude/.gemini/.codex, qa.md, PR template)
   repointed from archived `dev-sync.sh`/`audit.sh` to the governed `.ts` commands.
4. `variant.json` identity: utility description (was co-develop 7-agent prose); `pm`
   added to `agents[]` (6 entries — matches AGENTS.md/VERSION_MANIFEST/mirrors).
5. `agents/i18n-specialist.md`: `variant: co-utility`, `phases: [3, 4]` (was co-develop /
   [5] contradicting the dispatch tables); dead constitution §-citations → doctrine
   pointers.
6. Doc-truth fixes: i18n baseline "56 keys" → parity-SSOT wording (actual 78), variant
   status wording tied to `variant.json`, output-root doctrine wording aligned with the
   actual `src/`-anchor mechanism (context + phase-definitions).
7. Roster residue: `agents/pm.md` (7-agent persona count, designer/i18n links),
   `agents/frontend.md` (designer route), root `__pycache__/` removed,
   `docs/project.md` identity seed filled, CHANGELOG `[Unreleased]` gains the
   src/-layout + rebase entry.

## 3. Deferred (recorded in the report's Action wiring)

Rebase-residue sweep batch (procedures, skill-graph tombstones, lifecycle records,
platform-doc anchors), launcher/CI hardening batch (ytdl.bat, action pinning,
test:unit, typecheck gate), security-posture batch (bind host, nocheckcertificate,
.env.sample policy, SSRF, SECURITY.md) — each needs either a coordinated pass or an
owner decision; validator-hardening notes recorded for the workspace upstream backlog.

## 4. Verification

`bun scripts/audit.ts --skip-memory` exit 0; `pytest tests/ -q` 111 passed; VERSION_MANIFEST +
agent mirrors + skill-graph regenerated after the agent frontmatter changes.
