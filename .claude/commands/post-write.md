---
name: post-write
description: Run the Post-Write quality gate chain (audit → pytest → test_app) manually. Use after any Write or Edit when hooks are unavailable (Desktop App, Gemini CLI).
argument-hint: "[changed file]"
allowed-tools: ["Bash"]
---

# /post-write — Manual Quality Gate

Run the Post-Write quality gate chain for QuickDL.

Use this command after any Write or Edit when `PostToolUse` hooks do not fire automatically (Desktop App, Gemini CLI sessions).

## Steps (in order — stop if any step fails)

1. **Audit** — Run `bash scripts/audit.sh`. Must exit 0.
2. **i18n tests** — Run `pytest test_i18n.py -v`. Must pass 14 tests.
3. **API tests** — Run `python test_app.py`. Must pass 9 tests.

```bash
bash scripts/audit.sh && pytest test_i18n.py -v && python test_app.py
```

## Output format

```
✅ audit      — PASSED
✅ pytest     — PASSED (14 passed, 0 failed)
✅ test_app   — PASSED (9 passed, 0 failed)
```

If any step fails, report the error and stop. Do not run `/sync` until all gates pass.

See `skills/post-write-check/SKILL.md` for the full PASS/FAIL certificate format.
