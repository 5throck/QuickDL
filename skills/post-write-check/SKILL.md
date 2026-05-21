---
name: Post-Write Quality Check
description: >
  Use after ANY Write or Edit operation on QuickDL source files. Enforces the
  mandatory quality gate: audit → pytest → test_app. Trigger automatically
  after every code change, or manually when hooks are unavailable.
version: 1.0.0
---

> ⚠️ **Desktop App / Gemini CLI**: `PostToolUse` hooks may not fire automatically.
> Run `/post-write` manually after every Write or Edit in those environments.

# Post-Write Quality Check

Applies to all tools: **Claude Code CLI, Gemini CLI, Desktop App**

After ANY Write or Edit to Python source files, run these steps in order:

| Step | Command | Pass Condition |
|------|---------|----------------|
| 1 | `bash scripts/audit.sh` | Exit 0 — CHANGELOG exists, all locale keys match |
| 2 | `pytest test_i18n.py -v` | 0 failures (14 tests) |
| 3 | `python test_app.py` | 0 failures (9 tests) |

## When to Run

- After any change to `app.py`, `download_service.py`, `i18n.py`
- After any change to `locales/*.json`
- After any change to `static/js/script.js` or `templates/index.html`
- Before every `/sync`

## Output Format

Report each step clearly:

```
✅ audit      — PASSED (CHANGELOG OK, 16 locales OK)
✅ pytest     — PASSED (14 passed, 0 failed)
✅ test_app   — PASSED (9 passed, 0 failed)
```

If any step fails:

```
❌ audit      — FAILED
  [!] locales/th.json: missing keys = {'ui.queue_empty'}
Action required: Fix locale files before proceeding.
```

## PASS Certificate

If all 3 steps pass, issue this certificate in the task log:

```
✅ POST-WRITE PASS CERTIFICATE
──────────────────────────────
Date    : YYYY-MM-DD HH:MM
Gates   : 3/3 PASSED
  audit   : OK — 16 locales, CHANGELOG present
  pytest  : 14 passed, 0 failed
  test_app: 9 passed, 0 failed
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

1. Never skip `audit.sh` — even for "trivial" one-line changes.
2. If `audit.sh` fails, fix before running tests.
3. If `pytest` fails, do not run `test_app.py` until the i18n issue is fixed.
4. All 3 gates must PASS before `/sync`.
