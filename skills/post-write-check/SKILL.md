---
name: Post-Write Quality Check
description: >
  Use after ANY Write or Edit operation on QuickDL source files. Enforces the
  mandatory quality gate: workspace audit → full pytest suite. Trigger automatically
  after every code change, or manually when hooks are unavailable.
version: 1.1.0
last_reviewed: 2026-11-19
status: active
owner: qa
---
scope: variant

> ⚠️ **Desktop App / Gemini CLI**: `PostToolUse` hooks may not fire automatically.
> Run `/post-write` manually after every Write or Edit in those environments.

# Post-Write Quality Check

Applies to all tools: **Claude Code CLI, Gemini CLI, Desktop App**

After ANY Write or Edit to Python source files, run these steps in order:

| Step | Command | Pass Condition |
|------|---------|----------------|
| 1 | `bun scripts/audit.ts --skip-memory` | Exit 0 — full workspace gate suite |
| 2 | `pytest tests/ -q` | 0 failures (111 tests) |

## When to Run

- After any change to `src/*.py`
- After any change to `src/locales/*.json`
- After any change to `src/static/js/script.js` or `src/templates/index.html`
- Before every `/sync`

## Output Format

Report each step clearly:

```
✅ audit      — PASSED (workspace gate suite, exit 0)
✅ pytest     — PASSED (111 passed, 0 failed)
```

If any step fails:

```
❌ audit      — FAILED
  [!] locales/th.json: missing keys = {'ui.queue_empty'}
Action required: Fix locale files before proceeding.
```

## PASS Certificate

If all steps pass, issue this certificate in the task log:

```
✅ POST-WRITE PASS CERTIFICATE
──────────────────────────────
Date    : YYYY-MM-DD HH:MM
Gates   : 3/3 PASSED
  audit   : OK — workspace gate suite, exit 0
  pytest  : 111 passed, 0 failed
Issued by: post-write-check skill
```

## FAIL Certificate

```
❌ POST-WRITE FAIL — REJECTED
──────────────────────────────
Gate Failed : [Gate N — Name]
Reason      : [exact error message]
Action      : Fix and re-run before /sync
```

## Rules

1. Never skip the audit gate — even for "trivial" one-line changes.
2. If the audit fails, fix before running tests.
3. If `pytest` fails, do not run `tests/test_app.py` until the i18n issue is fixed.
4. All 3 gates must PASS before `/sync`.
