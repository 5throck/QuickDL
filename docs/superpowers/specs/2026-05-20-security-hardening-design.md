# QuickDL — Group A: Security Hardening Design Spec

**Date:** 2026-05-20
**Scope:** S-1~S-5 — URL validation, debug isolation, path exposure removal, file serving endpoint, threaded mode

---

## Overview

Five targeted security and correctness fixes to `app.py` and `static/js/script.js`. No new dependencies. All changes are backward-compatible with desktop app and CLI modes.

---

## S-1: URL Input Validation

**Problem:** `/api/info` and `/api/download` pass any string directly to yt-dlp, including `file://`, `ftp://` schemes.

**Scope of fix:** Scheme-level validation only (`http://` and `https://`). SSRF via valid HTTP URLs (e.g., `http://localhost`, `http://169.254.169.254`) is out of scope for this fix — yt-dlp itself rejects non-video URLs, providing a second layer of defense.

**Design:**
```python
import re
_URL_PATTERN = re.compile(r'^https?://', re.IGNORECASE)

def _validate_url(url: str) -> bool:
    return bool(url and _URL_PATTERN.match(url))
```

Applied at the top of both `get_info()` and `download()` handlers, before any other processing. Returns HTTP 400 with `t('app.error_invalid_url')` on failure.

**New i18n key** (added to all 12 locales):
```json
"app.error_invalid_url": "Invalid URL. Only http:// and https:// links are supported."
```

---

## S-2: Debug Mode Isolation + S-5: Threaded Mode

**Problem:** `app.run(debug=True)` hardcoded — enables Flask Debugger (remote code execution risk) in any environment. Single-threaded mode causes `/api/status` polling requests to queue behind the download thread.

**Design:**
```python
if __name__ == '__main__':
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(debug=debug, threaded=True, host='0.0.0.0', port=5000)
```

`FLASK_DEBUG=1 python app.py` for development. Default (no env var) is safe mode. `threaded=True` enables concurrent request handling.

---

## S-3 + S-4: Path Removal + File Serving Endpoint

These two items share a single data flow and must be implemented together.

### Problem
- S-3: Job status response exposes server filesystem path (`C:\git\quickdl\downloads\title.mp4`)
- S-4: Web UI users receive "done" status but cannot download the file

### Data Flow Design

**Two registries in `app.py`:**
```python
_jobs: dict = {}       # job_id → {status, filename, error} — live job state
_completed: dict = {}  # job_id → filename — persists after _jobs entry is removed
```

**Download thread write order** (critical — `_completed` must be written BEFORE `_jobs` status is set to `"done"`, so `job_status()` never sees `"done"` without the filename being available in `_completed`):
```python
def run():
    _jobs[job_id]["status"] = "running"
    try:
        filepath = download_video(url, DOWNLOAD_DIR)
        filename = os.path.basename(filepath)
        _completed[job_id] = filename        # (1) write to _completed first
        _jobs[job_id].update({"status": "done", "filename": filename})  # (2) then mark done
    except Exception as e:
        _jobs[job_id].update({"status": "error", "error": str(e)})
```

Thread safety note: CPython's GIL ensures individual dict operations (`__setitem__`, `update`) are atomic. The ordered writes above (1) then (2) guarantee `_completed` is populated before any polling thread can observe `"done"` in `_jobs`. No explicit `threading.Lock` is required under CPython.

**`job_status()` — status endpoint:**
```python
@app.route('/api/status/<job_id>', methods=['GET'])
def job_status(job_id):
    job = _jobs.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    if job["status"] in ("done", "error"):
        _jobs.pop(job_id, None)
    return jsonify(job)
# Response on done: {"status": "done", "filename": "title.mp4"}
# No absolute path in response
```

The one-time-link guarantee is enforced entirely by `_completed.pop` inside `serve_file()`, not by `job_status()`. A client that polls twice and receives two "done" responses is harmless — both will return the same payload, and only the first `/api/file/<job_id>` request will succeed.

**`serve_file()` — file download endpoint:**
```python
from flask import send_from_directory  # add to existing Flask import line

@app.route('/api/file/<job_id>', methods=['GET'])
def serve_file(job_id):
    filename = _completed.get(job_id)
    if not filename:
        return jsonify({'error': 'File not found or already downloaded'}), 404
    _completed.pop(job_id, None)  # one-time link: removed after first successful serve
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)
```

`send_from_directory` prevents path traversal — it only serves files inside `DOWNLOAD_DIR`.

**One-time link behavior:** The `/api/file/<job_id>` link is intentionally single-use. After the first successful GET, the entry is removed from `_completed`. The frontend must disable/remove the download anchor after first click to prevent a broken second request. See frontend change below.

**Threat model note:** `job_id` is UUID-v4 (~122 bits entropy); brute-force is impractical. Since `host='0.0.0.0'` is used, LAN peers can reach `/api/file/<job_id>` if they observe network traffic — this is acceptable for a local desktop tool.

**Deployment note:** `app.py` and `static/js/script.js` changes must be deployed atomically (or `script.js` first). Deploying the backend alone causes the existing `statusData.filepath` reference in the old JS to resolve to `undefined`.

### i18n changes
- Remove `"ui.success"` key (and `{filepath}` placeholder) from all 12 locale files — this key is obsolete after S-3/S-4.
- Add `"ui.success_download"` and `"app.error_invalid_url"` keys to all 12 locale files.

---

## Frontend Change (`static/js/script.js`)

On `status === 'done'`, replace the filepath text display with a single-use download anchor:
```javascript
if (statusData.status === 'done') {
    stopPolling();
    const link = document.createElement('a');
    link.href = `/api/file/${jobId}`;
    link.textContent = window.I18N['ui.success_download'];
    link.download = '';
    link.addEventListener('click', () => {
        // Disable after first click to prevent broken second request
        setTimeout(() => link.remove(), 100);
    });
    statusMessage.replaceChildren(link);
    statusMessage.className = 'status-success';
    statusMessage.classList.remove('hidden');
}
```

**New i18n keys:**
```json
"ui.success_download": "✅ Download ready — click to save",
"app.error_invalid_url": "Invalid URL. Only http:// and https:// links are supported."
```

---

## File Map

| File | Changes |
|------|---------|
| `app.py` | Import `send_from_directory`; add `_validate_url()`; add `_completed` dict; update download thread write order; update `job_status()` response (filename only); add `serve_file()`; fix debug/threaded |
| `static/js/script.js` | Replace success filepath display with download anchor; disable anchor after first click |
| `locales/*.json` (12 files) | Remove `ui.success`; add `ui.success_download`; add `app.error_invalid_url` |

---

## Verification

```bash
# 1. URL validation — invalid scheme
curl -s -X POST http://localhost:5000/api/info \
  -H 'Content-Type: application/json' \
  -d '{"url":"file:///etc/passwd"}' | python -m json.tool
# Expected: {"error": "Invalid URL..."}  HTTP 400

# 2. URL validation — /api/download endpoint also covered
curl -s -X POST http://localhost:5000/api/download \
  -H 'Content-Type: application/json' \
  -d '{"url":"ftp://example.com/video"}' | python -m json.tool
# Expected: {"error": "Invalid URL..."}  HTTP 400

# 3. Debug mode off by default
python app.py
# Flask output should NOT contain the Werkzeug debugger PIN line

# 4. Full download flow — no absolute path in response
curl -s -X POST http://localhost:5000/api/download \
  -H 'Content-Type: application/json' \
  -d '{"url":"<valid-youtube-url>"}' | python -m json.tool
# Returns: {"job_id": "...", "status": "pending"}  (no filepath)

JOB_ID=<job_id from above>
curl -s http://localhost:5000/api/status/$JOB_ID | python -m json.tool
# Eventually: {"status": "done", "filename": "title.mp4"}  (filename only, no path)

# 5. File download
curl -O http://localhost:5000/api/file/$JOB_ID
# Downloads title.mp4 locally

# Second request to same URL
curl -s http://localhost:5000/api/file/$JOB_ID | python -m json.tool
# Expected: {"error": "File not found or already downloaded"}  HTTP 404

# 6. i18n audit (net +1 key: 50 current → 51 after removing ui.success and adding 2 new keys)
python -c "
import json
from pathlib import Path
base = json.loads(Path('locales/en.json').read_text(encoding='utf-8'))
assert 'ui.success' not in base, 'ui.success should be removed'
assert 'ui.success_download' in base, 'ui.success_download missing'
assert 'app.error_invalid_url' in base, 'app.error_invalid_url missing'
for p in sorted(Path('locales').glob('*.json')):
    other = json.loads(p.read_text(encoding='utf-8'))
    missing = set(base) - set(other)
    extra = set(other) - set(base)
    print(p.name, 'OK' if not missing and not extra else f'FAIL missing={missing} extra={extra}')
"
```
