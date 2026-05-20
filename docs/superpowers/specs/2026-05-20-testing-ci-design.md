# QuickDL — Group C: Testing & CI Design Spec

**Date:** 2026-05-20
**Scope:** U-3 (test_i18n.py), U-4 (test_app.py), U-5 (GitHub Actions), M-5 (i18n audit CI)

---

## Overview

Establish automated test coverage for the i18n module and Flask API, then wire them into a GitHub Actions CI pipeline that runs on every PR. The i18n key audit (M-5) becomes a non-optional CI gate.

No new runtime dependencies. Test-only dependencies: none beyond stdlib (Flask test client is built-in).

---

## U-3: `test_i18n.py` — i18n Unit Tests

### Coverage

```python
# test_i18n.py
import os
import sys
import json
import pytest  # optional — plain assert if pytest not installed

sys.path.insert(0, '.')
import i18n

def test_init_default_lang():
    i18n.init()
    assert i18n.get_lang() in i18n.SUPPORTED

def test_init_explicit_lang():
    i18n.init('ko')
    assert i18n.get_lang() == 'ko'

def test_init_unsupported_lang_falls_back_to_en():
    i18n.init('xx')
    assert i18n.get_lang() == 'en'

def test_t_returns_translation():
    i18n.init('en')
    assert i18n.t('cli.fetching') != 'cli.fetching'

def test_t_returns_key_on_missing():
    i18n.init('en')
    assert i18n.t('nonexistent.key') == 'nonexistent.key'

def test_t_format_substitution():
    i18n.init('en')
    result = i18n.t('cli.error', e='test error')
    assert 'test error' in result

def test_t_format_missing_kwarg_does_not_raise():
    i18n.init('en')
    result = i18n.t('cli.error')  # missing 'e' kwarg
    assert isinstance(result, str)

def test_detect_lang_env_override(monkeypatch):
    monkeypatch.setenv('QUICKDL_LANG', 'ja')
    i18n.init()
    assert i18n.get_lang() == 'ja'

def test_detect_lang_unsupported_env_falls_back(monkeypatch):
    monkeypatch.setenv('QUICKDL_LANG', 'zz')
    i18n.init()
    assert i18n.get_lang() == 'en'

def test_get_all_returns_dict():
    i18n.init('en')
    all_t = i18n.get_all()
    assert isinstance(all_t, dict)
    assert len(all_t) > 0

def test_all_locales_have_same_keys():
    """All locale files must have identical key sets to en.json."""
    from pathlib import Path
    # Use __file__-relative path so tests work regardless of CWD
    root = Path(__file__).parent
    base = json.loads((root / 'locales' / 'en.json').read_text(encoding='utf-8'))
    for p in sorted((root / 'locales').glob('*.json')):
        other = json.loads(p.read_text(encoding='utf-8'))
        missing = set(base) - set(other)
        extra = set(other) - set(base)
        assert not missing, f'{p.name} missing keys: {missing}'
        assert not extra, f'{p.name} has extra keys: {extra}'

if __name__ == '__main__':
    # Run without pytest: plain assert
    import traceback
    tests = [v for k, v in globals().items() if k.startswith('test_')]
    passed = failed = 0
    for test in tests:
        try:
            if 'monkeypatch' in test.__code__.co_varnames:
                continue  # skip monkeypatch tests without pytest
            test()
            print(f'  PASS  {test.__name__}')
            passed += 1
        except Exception:
            print(f'  FAIL  {test.__name__}')
            traceback.print_exc()
            failed += 1
    print(f'\n{passed} passed, {failed} failed')
```

Note: `monkeypatch` tests require pytest. Without pytest, those tests are skipped in plain-assert mode — this is explicitly documented in the `if __name__ == '__main__'` block.

---

## U-4: `test_app.py` — Flask API Tests

### Design

Use Flask's built-in test client. Mock `download_service` to avoid real network calls.

```python
# test_app.py
import json
import sys
import threading
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, '.')

class TestAppAPI(unittest.TestCase):
    # Prerequisites: test_app.py requires Groups A and B to be implemented first.
    # - _completed (Group A: S-3/S-4 file serving registry)
    # - _cancel_events (Group B: U-2 cancellation)
    # - URL validation (Group A: S-1) for test_*_invalid_scheme tests
    # Run this file only after Groups A and B are merged.

    def setUp(self):
        import app as app_module
        app_module.app.config['TESTING'] = True
        self.client = app_module.app.test_client()
        self.app_module = app_module
        # Reset shared state between tests to prevent inter-test pollution
        app_module._jobs.clear()
        app_module._completed.clear()
        app_module._cancel_events.clear()

    def tearDown(self):
        self.app_module._jobs.clear()
        self.app_module._completed.clear()
        self.app_module._cancel_events.clear()

    # --- /api/info ---

    def test_info_missing_url(self):
        r = self.client.post('/api/info',
            json={},
            content_type='application/json')
        self.assertEqual(r.status_code, 400)

    def test_info_invalid_scheme(self):
        # Prerequisite: requires Group A (S-1 URL validation) to be implemented in app.py
        r = self.client.post('/api/info',
            json={'url': 'file:///etc/passwd'},
            content_type='application/json')
        self.assertEqual(r.status_code, 400)
        data = json.loads(r.data)
        self.assertIn('error', data)

    def test_info_success(self):
        mock_info = {'title': 'Test', 'thumbnail': 'http://t', 'duration': '3:00', 'channel': 'Ch'}
        with patch('app.get_video_info', return_value=mock_info):
            r = self.client.post('/api/info',
                json={'url': 'https://youtube.com/watch?v=test'},
                content_type='application/json')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(json.loads(r.data)['title'], 'Test')

    # --- /api/download ---

    def test_download_missing_url(self):
        r = self.client.post('/api/download',
            json={},
            content_type='application/json')
        self.assertEqual(r.status_code, 400)

    def test_download_invalid_scheme(self):
        # Prerequisite: requires Group A (S-1 URL validation) to be implemented in app.py
        r = self.client.post('/api/download',
            json={'url': 'ftp://bad.com'},
            content_type='application/json')
        self.assertEqual(r.status_code, 400)

    def test_download_returns_job_id(self):
        # Use a blocking event so the background thread doesn't race the assertions
        block = threading.Event()
        def slow_download(*args, **kwargs):
            block.wait()
            return '/downloads/test.mp4'
        with patch('app.download_video', side_effect=slow_download):
            r = self.client.post('/api/download',
                json={'url': 'https://youtube.com/watch?v=test'},
                content_type='application/json')
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertIn('job_id', data)
        self.assertEqual(data['status'], 'pending')
        block.set()  # unblock thread so it can exit cleanly

    # --- /api/status ---

    def test_status_not_found(self):
        r = self.client.get('/api/status/nonexistent-job-id')
        self.assertEqual(r.status_code, 404)

    def test_status_returns_progress(self):
        import uuid
        job_id = str(uuid.uuid4())
        # Schema matches the full _jobs structure after Group A + Group B are applied
        self.app_module._jobs[job_id] = {
            'status': 'running',
            'progress': 50,
            'speed': None,
            'eta': None,
            'filename': None,  # renamed from 'filepath' in Group B (M-4)
            'error': None,
        }
        r = self.client.get(f'/api/status/{job_id}')
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertEqual(data['progress'], 50)

    # --- /api/file ---

    def test_file_not_found(self):
        r = self.client.get('/api/file/nonexistent-job-id')
        self.assertEqual(r.status_code, 404)

if __name__ == '__main__':
    unittest.main()
```

---

## U-5: GitHub Actions CI

### File: `.github/workflows/ci.yml`

```yaml
name: CI

on:
  push:
    branches: [master]
  pull_request:
    branches: [master]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.8", "3.10", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          pip install flask yt-dlp flask-cors pytest
          # pywebview and pystray are excluded — they require a display
          # test_env.py is skipped in CI for this reason

      - name: i18n key audit
        run: python -c "
import json, sys
from pathlib import Path
base = json.loads(Path('locales/en.json').read_text(encoding='utf-8'))
failed = False
for p in sorted(Path('locales').glob('*.json')):
    other = json.loads(p.read_text(encoding='utf-8'))
    missing = set(base) - set(other)
    extra = set(other) - set(base)
    if missing or extra:
        print(f'FAIL {p.name}: missing={missing} extra={extra}')
        failed = True
    else:
        print(f'OK   {p.name}')
sys.exit(1 if failed else 0)
"

      - name: Run i18n unit tests
        run: pytest test_i18n.py -v

      - name: Run API tests
        run: python test_app.py
```

---

## M-5: i18n Key Audit as CI Gate

The `i18n key audit` step in the CI workflow (above) runs `sys.exit(1)` on any key mismatch, blocking PR merge. This replaces the manual audit command from `agents.md`.

The same audit script is used in local development via:
```bash
python -c "<audit script>"
```

---

## File Map

| File | Action |
|------|--------|
| `test_i18n.py` | Create |
| `test_app.py` | Rewrite (current version has no assertions) |
| `.github/workflows/ci.yml` | Create |

---

## Verification

```bash
# Local test run
python test_i18n.py
# Expected: all PASS lines, "N passed, 0 failed"

python test_app.py
# Expected: OK (N tests)

# Simulate CI audit failure
echo '{}' > locales/test_bad.json
python -c "<audit script>"
# Expected: exit code 1, "FAIL test_bad.json: missing=..."
rm locales/test_bad.json
```
