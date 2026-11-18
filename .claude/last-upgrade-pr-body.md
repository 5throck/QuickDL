## Upgrade delivery

Auto-composed from `.claude/last-upgrade-delivery.json` at delivery time — this body describes exactly the merged content.

- Variant: co-develop
- Template: 0.30.0 → 0.30.0
- Delivered: 10 file(s) at 2026-11-18T19:13:48.183Z

### Delivery footprint

- scripts/ — 3 file(s)
- (root) — 2 file(s)
- .agents/ — 1 file(s)
- .claude/ — 1 file(s)
- .codex/ — 1 file(s)
- .gemini/ — 1 file(s)
- .hermes/ — 1 file(s)

### Decisions

- INFO: 119 / WARN: 105 / ERROR: 3

**Unresolved ERROR dispositions** (CONFLICT/TOMBSTONED: delivery skipped, project copy preserved; BEHAVIOR_REGRESSION: delivered, new sibling-test failure):
- `agents/architect.md` (SYNC_IF_NEWER: agents/) — equal-version drift on project-evolved content — CONFLICT disposition: restore-to-canonical SKIPPED, project copy preserved
- `agents/i18n-specialist.md` (SYNC_IF_NEWER: agents/) — equal-version drift on project-evolved content — CONFLICT disposition: restore-to-canonical SKIPPED, project copy preserved
- `.mcp.json` (TEMPLATE TREE SYNC) — project deleted a previously delivered file — delivery REFUSED (severity ERROR): confirm with --tombstone <path>, or restore the project copy and re-run

_Full inventory: `.claude/last-upgrade-delivery.json` (dev-sync Step 3.9 auto-E5 diff attribution; ERROR dispositions block auto-E5 until resolved)._
