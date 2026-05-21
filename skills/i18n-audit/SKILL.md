---
name: i18n Audit & Synchronization
description: >
  Use whenever translation keys are added, removed, or modified in locales/*.json,
  or when i18n.py changes. Verifies all 16 locale files have identical keys to
  en.json (baseline), checks SUPPORTED set in i18n.py, and issues a Parity Certificate.
version: 1.0.0
---

# i18n Audit & Synchronization Protocol

**Role**: i18n Expert (`agents/i18n.md`) — mandatory after any locale or i18n.py change.

## Trigger Conditions

Execute this protocol whenever:
- A key is added, renamed, or removed in `locales/en.json`
- Any `locales/<lang>.json` file is modified
- `i18n.py` `SUPPORTED` set changes
- A new language is added

## Steps

### Step 1 — Master Key Extraction
Read `locales/en.json` and extract the full key list (baseline: **56 keys**).

### Step 2 — Parity Check
Run the audit command:
```bash
python -c "
import json, pathlib, sys
base = json.loads(pathlib.Path('locales/en.json').read_text(encoding='utf-8'))
failed = False
for p in sorted(pathlib.Path('locales').glob('*.json')):
    other = json.loads(p.read_text(encoding='utf-8'))
    missing = set(base) - set(other)
    extra   = set(other) - set(base)
    if missing or extra:
        print(f'FAIL: {p.name} missing={missing} extra={extra}')
        failed = True
    else:
        print(f'OK:   {p.name}')
sys.exit(1 if failed else 0)
"
```

### Step 3 — SUPPORTED Set Verification
Verify `i18n.py` `SUPPORTED` set matches the locale files on disk:
```bash
python -c "
import i18n, pathlib
on_disk = {p.stem for p in pathlib.Path('locales').glob('*.json')}
in_code  = i18n.SUPPORTED
missing  = on_disk - in_code
extra    = in_code - on_disk
print('On disk :', sorted(on_disk))
print('In code :', sorted(in_code))
if missing: print('MISSING from SUPPORTED:', missing)
if extra:   print('EXTRA in SUPPORTED (no file):', extra)
"
```

### Step 4 — Run pytest i18n Suite
```bash
pytest tests/test_i18n.py -v
```
Must pass all 14 tests including `test_all_locales_have_same_keys`.

## Supported Languages (16)

| Code | Language | Code | Language |
|------|----------|------|----------|
| `en` | English (baseline) | `ko` | Korean |
| `ja` | Japanese | `zh-CN` | Chinese Simplified |
| `zh-TW` | Chinese Traditional | `de` | German |
| `es` | Spanish | `fr` | French |
| `pt` | Portuguese | `vi` | Vietnamese |
| `ms` | Malay | `id` | Indonesian |
| `th` | Thai | `ru` | Russian |
| `it` | Italian | `ar` | Arabic |

## Output

### L10N Parity Certificate (all PASS)
```
✅ L10N PARITY CERTIFICATE
───────────────────────────
Date      : YYYY-MM-DD
Languages : 16/16 PASS
Keys      : 56 (en.json baseline)
pytest    : 14 passed, 0 failed
SUPPORTED : matches locale files
Issued by : i18n-audit skill
```

### L10N Fail Report
```
❌ L10N PARITY FAIL
───────────────────────────
Failed locales : [th.json, ru.json]
Missing keys   : {'ui.queue_empty', 'ui.queue_title'}
Action         : Add missing keys to all failed locale files
```

## Adding a New Language

1. Create `locales/<code>.json` with all 56 keys translated
2. Add `<code>` to `i18n.py` `SUPPORTED` set
3. Re-run this audit protocol
4. Issue L10N Parity Certificate
