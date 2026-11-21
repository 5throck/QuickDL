## Upgrade delivery

Auto-composed from `.claude/last-upgrade-delivery.json` at delivery time — this body describes exactly the merged content.

- Variant: co-utility
- Template: 0.30.0 → 0.30.0
- Delivered: 106 file(s) at 2026-11-21T18:13:29.493Z

### Delivery footprint

- .claude/ — 15 file(s)
- .gemini/ — 15 file(s)
- .agents/ — 14 file(s)
- .codex/ — 14 file(s)
- .hermes/ — 14 file(s)
- scripts/ — 14 file(s)
- skills/ — 14 file(s)
- (root) — 3 file(s)
- docs/ — 3 file(s)

### Decisions

- INFO: 139 / WARN: 103 / ERROR: 2

**Unresolved ERROR dispositions** (CONFLICT/TOMBSTONED: delivery skipped, project copy preserved; BEHAVIOR_REGRESSION: delivered, new sibling-test failure):
- `agents/i18n-specialist.md` (SYNC_IF_NEWER: agents/) — equal-version drift on project-evolved content — CONFLICT disposition: restore-to-canonical SKIPPED, project copy preserved
- `PROMOTION_CHECKLIST.md` (TEMPLATE TREE SYNC) — project deleted a previously delivered file — delivery REFUSED (severity ERROR): confirm with --tombstone <path>, or restore the project copy and re-run

_Full inventory: `.claude/last-upgrade-delivery.json` (dev-sync Step 3.9 auto-E5 diff attribution; ERROR dispositions block auto-E5 until resolved)._
