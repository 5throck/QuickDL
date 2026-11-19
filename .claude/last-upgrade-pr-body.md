## Upgrade delivery

Auto-composed from `.claude/last-upgrade-delivery.json` at delivery time — this body describes exactly the merged content.

- Variant: co-utility
- Template: 0.30.0 → 0.30.0
- Delivered: 45 file(s) at 2026-11-19T18:33:00.334Z

### Delivery footprint

- scripts/ — 14 file(s)
- .claude/ — 8 file(s)
- .codex/ — 7 file(s)
- .gemini/ — 7 file(s)
- agents/ — 4 file(s)
- (root) — 3 file(s)
- docs/ — 2 file(s)

### Decisions

- INFO: 150 / WARN: 104 / ERROR: 3

**Unresolved ERROR dispositions** (CONFLICT/TOMBSTONED: delivery skipped, project copy preserved; BEHAVIOR_REGRESSION: delivered, new sibling-test failure):
- `docs/phase-definitions.md` (DOCS_OVERWRITE) — project-evolved since the last delivery AND template changed — CONFLICT disposition: delivery SKIPPED, project copy preserved
- `agents/i18n-specialist.md` (SYNC_IF_NEWER: agents/) — equal-version drift on project-evolved content — CONFLICT disposition: restore-to-canonical SKIPPED, project copy preserved
- `PROMOTION_CHECKLIST.md` (TEMPLATE TREE SYNC) — project deleted a previously delivered file — delivery REFUSED (severity ERROR): confirm with --tombstone <path>, or restore the project copy and re-run

_Full inventory: `.claude/last-upgrade-delivery.json` (dev-sync Step 3.9 auto-E5 diff attribution; ERROR dispositions block auto-E5 until resolved)._
