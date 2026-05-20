# QuickDL — 16-Item Improvement Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement all 16 improvement items (S-1~S-5, U-1~U-6, M-1~M-6) derived from the multi-agent design discussion, transforming QuickDL into a secure, responsive, testable download manager with queue UI and CI.

**Architecture:** Five independent but ordered groups. Group D (i18n utils) is self-contained. Group A (security) lays the foundational `_completed` registry and URL validation that Groups B and C depend on. Group B (download experience) builds a queue with progress and cancellation on top of Group A. Group E (UI polish) is mostly independent — the `.queue-item` breakpoint is a forward reference to Group B's queue panel. Group C (testing/CI) tests the fully-assembled system and ships last.

**Tech Stack:** Python/Flask (backend), vanilla JS (frontend), CSS custom properties (theme), yt-dlp (download), pytest (testing), GitHub Actions (CI)

---

## Implementation Order

| Task | Item(s) | Group | Prerequisite |
|------|---------|-------|--------------|
| 1 | U-6: format_duration | D | — |
| 2 | S-1: URL validation | A | — |
| 3 | S-2 + S-5: debug + threaded | A | — |
| 4 | S-3 + S-4: file serving + path removal | A | — |
| 5 | M-4: dependency injection | B | — |
| 6 | U-1: download progress | B | Tasks 4, 5 |
| 7 | U-2: download cancellation | B | Task 6 |
| 8 | M-1: queue UI | B | Tasks 6, 7 |
| 9 | M-2: light mode support | E | — |
| 10 | M-3: mobile responsive | E | — |
| 11 | M-6: downloads cleanup | E | — |
| 12 | U-3: test_i18n.py (remainder) | C | Task 1 |
| 13 | U-4: test_app.py | C | Tasks 2, 4, 6, 7 |
| 14 | U-5 + M-5: GitHub Actions CI | C | Tasks 12, 13 |

## File Map

| File | Tasks | Changes |
|------|-------|---------|
| `i18n.py` | 1 | Add `format_duration()` |
| `download_service.py` | 1, 5 | Use `format_duration`; add DI params |
| `app.py` | 2, 3, 4, 6, 7, 11 | URL validation, debug/threaded, `_completed`, `serve_file`, progress hook, cancel events, cleanup |
| `static/js/script.js` | 4, 8 | Download anchor; full queue state rewrite |
| `templates/index.html` | 8 | Queue panel HTML |
| `static/css/styles.css` | 8, 9, 10 | Queue styles; light mode media query; responsive breakpoints |
| `locales/*.json` (×12) | 2, 4, 6, 7, 8 | +7 keys, −1 key → net 56 keys |
| `test_i18n.py` | 1, 12 | Create (Task 1); expand (Task 12) |
| `test_app.py` | 13 | Create |
| `.github/workflows/ci.yml` | 14 | Create |

---

## Task 1: U-6 — `format_duration()` in `i18n.py`

**Spec:** `docs/superpowers/specs/2026-05-20-i18n-utils-design.md`

**Files:**
- Modify: `i18n.py` — add `format_duration()` after `get_all()`
- Modify: `download_service.py:13-14` — replace `t("seconds_suffix")` fallback
- Create: `test_i18n.py` — format_duration tests (more tests added in Task 12)

- [ ] **Step 1.1: Create `test_i18n.py` with failing format_duration tests**

```python
# test_i18n.py
import sys
import json
sys.path.insert(0, '.')
import i18n


def test_format_duration_english():
    i18n.init('en')
    assert i18n.format_duration(0) == '0:00'
    assert i18n.format_duration(45) == '0:45'
    assert i18n.format_duration(225) == '3:45'
    assert i18n.format_duration(3665) == '1:01:05'


def test_format_duration_korean():
    i18n.init('ko')
    assert i18n.format_duration(45) == '45초'
    assert i18n.format_duration(225) == '3분 45초'
    assert i18n.format_duration(3665) == '1시간 1분 5초'


def test_format_duration_japanese():
    i18n.init('ja')
    assert i18n.format_duration(225) == '3分45秒'


if __name__ == '__main__':
    import traceback
    tests = [v for k, v in globals().items() if k.startswith('test_')]
    passed = failed = 0
    for test in tests:
        try:
            test()
            print(f'  PASS  {test.__name__}')
            passed += 1
        except Exception:
            print(f'  FAIL  {test.__name__}')
            traceback.print_exc()
            failed += 1
    print(f'\n{passed} passed, {failed} failed')
```

- [ ] **Step 1.2: Run tests to confirm they fail**

```
python test_i18n.py
```
Expected: `FAIL test_format_duration_english` — `AttributeError: module 'i18n' has no attribute 'format_duration'`

- [ ] **Step 1.3: Add `format_duration()` to `i18n.py` (append after `get_all()`)**

```python
def format_duration(seconds: int) -> str:
    """Return a locale-appropriate duration string for the current language.

    Precondition: seconds >= 0. Caller must validate (None/negative values
    should be treated as missing and skip this function entirely).
    Thread safety: reads module-level _lang set once at startup via init().
    Per-request reinit is not supported.
    """
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    lang = _lang  # set once at startup

    if lang in ('ko',):
        if h:
            return f"{h}시간 {m}분 {s}초"
        if m:
            return f"{m}분 {s}초"
        return f"{s}초"

    if lang in ('ja',):
        if h:
            return f"{h}時間{m}分{s}秒"
        if m:
            return f"{m}分{s}秒"
        return f"{s}秒"

    if lang in ('zh-TW', 'zh-CN'):
        if h:
            return f"{h}時{m}分{s}秒" if lang == 'zh-TW' else f"{h}时{m}分{s}秒"
        if m:
            return f"{m}分{s}秒"
        return f"{s}秒"

    # Default: HH:MM:SS or MM:SS (universal)
    # All languages not explicitly listed (en, de, es, fr, pt, vi, ms, id)
    # fall through here intentionally.
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"
```

- [ ] **Step 1.4: Run tests to confirm they pass**

```
python test_i18n.py
```
Expected: all PASS

- [ ] **Step 1.5: Update `download_service.py` — replace `t("seconds_suffix")` with `format_duration()`**

Change line 3:
```python
# Before:
from i18n import t

# After:
from i18n import t, format_duration
```

Change lines 13-14:
```python
# Before:
if not duration and info_dict.get('duration'):
    duration = str(info_dict.get('duration')) + t("seconds_suffix")

# After:
raw_dur = info_dict.get('duration')
if not duration and raw_dur:
    duration = format_duration(int(raw_dur))
```

- [ ] **Step 1.6: Commit**

```bash
git add i18n.py download_service.py test_i18n.py
git commit -m "feat(i18n): add format_duration() helper; use in download_service fallback (U-6)"
```

---

## Task 2: S-1 — URL Validation

**Spec:** `docs/superpowers/specs/2026-05-20-security-hardening-design.md` (S-1)

**Files:**
- Modify: `app.py` — add `_validate_url()`, apply to `get_info()` and `download()`
- Modify: `locales/*.json` (×12) — add `app.error_invalid_url`

- [ ] **Step 2.1: Add `app.error_invalid_url` to all 12 locale files**

Add at the end of each file (before the closing `}`). Values:

| Locale | Value |
|--------|-------|
| en | `"Invalid URL. Only http:// and https:// links are supported."` |
| ko | `"잘못된 URL입니다. http:// 또는 https:// 링크만 지원합니다."` |
| ja | `"無効なURLです。http://またはhttps://リンクのみ対応しています。"` |
| zh-TW | `"無效的URL。僅支援 http:// 和 https:// 連結。"` |
| zh-CN | `"无效的URL。仅支持 http:// 和 https:// 链接。"` |
| de | `"Ungültige URL. Nur http:// und https://-Links werden unterstützt."` |
| es | `"URL no válida. Solo se admiten enlaces http:// y https://."` |
| fr | `"URL invalide. Seuls les liens http:// et https:// sont pris en charge."` |
| pt | `"URL inválida. Apenas links http:// e https:// são suportados."` |
| vi | `"URL không hợp lệ. Chỉ hỗ trợ liên kết http:// và https://."` |
| ms | `"URL tidak sah. Hanya pautan http:// dan https:// disokong."` |
| id | `"URL tidak valid. Hanya tautan http:// dan https:// yang didukung."` |

- [ ] **Step 2.2: Add `_validate_url()` to `app.py` and apply it**

After the import block (after line 6), add:
```python
_URL_PATTERN = re.compile(r'^https?://', re.IGNORECASE)

def _validate_url(url: str) -> bool:
    return bool(url and _URL_PATTERN.match(url))
```

In `get_info()`, after `url = data.get('url')`, replace the existing `if not url:` block with:
```python
if not url:
    return jsonify({'error': t('app.error_url_required')}), 400
if not _validate_url(url):
    return jsonify({'error': t('app.error_invalid_url')}), 400
```

Apply the same pattern in `download()` (after `url = data.get('url')`).

- [ ] **Step 2.3: Run i18n audit — verify 51 keys, all locales match**

```bash
python -c "
import json
from pathlib import Path
base = json.loads(Path('locales/en.json').read_text(encoding='utf-8'))
print(f'Keys: {len(base)}')
for p in sorted(Path('locales').glob('*.json')):
    other = json.loads(p.read_text(encoding='utf-8'))
    missing = set(base) - set(other)
    extra = set(other) - set(base)
    print(p.name, 'OK' if not missing and not extra else f'FAIL missing={missing} extra={extra}')
"
```
Expected: `Keys: 51`, all locales `OK`

- [ ] **Step 2.4: Manual smoke test**

```bash
# In one terminal:
python app.py
# In another:
curl -s -X POST http://localhost:5000/api/info \
  -H 'Content-Type: application/json' \
  -d '{"url":"file:///etc/passwd"}' | python -m json.tool
```
Expected: `{"error": "Invalid URL. Only http:// and https:// links are supported."}` with HTTP 400

- [ ] **Step 2.5: Commit**

```bash
git add app.py locales/
git commit -m "feat(security): S-1 URL scheme validation — reject non-http/https"
```

---

## Task 3: S-2 + S-5 — Debug Isolation + Threaded Mode

**Spec:** `docs/superpowers/specs/2026-05-20-security-hardening-design.md` (S-2, S-5)

**Files:**
- Modify: `app.py:72` — change `app.run()` call

- [ ] **Step 3.1: Replace `app.run()` in the `if __name__ == '__main__':` block**

```python
# Before (line 72):
app.run(debug=True, host='0.0.0.0', port=5000)

# After:
debug = os.environ.get('FLASK_DEBUG', '0') == '1'
app.run(debug=debug, threaded=True, host='0.0.0.0', port=5000)
```

- [ ] **Step 3.2: Verify debug is off by default**

```bash
python app.py
```
Expected: Flask startup output must NOT contain `Debugger PIN:`.

- [ ] **Step 3.3: Commit**

```bash
git add app.py
git commit -m "fix(security): S-2/S-5 debug mode off by default; enable threaded=True"
```

---

## Task 4: S-3 + S-4 — Path Exposure Removal + File Serving

**Spec:** `docs/superpowers/specs/2026-05-20-security-hardening-design.md` (S-3, S-4)

**Files:**
- Modify: `app.py` — add `send_from_directory` import, `_completed` dict, update thread, update `job_status()`, add `serve_file()`
- Modify: `static/js/script.js:116-118` — replace filepath success with download anchor
- Modify: `locales/*.json` (×12) — remove `ui.success`, add `ui.success_download`

> **Deploy atomically:** `app.py` and `script.js` must be committed together.
> The `filepath` field in `_jobs` is renamed to `filename` — old JS references `statusData.filepath` which will break if backend deploys alone.

- [ ] **Step 4.1: Update locale files — remove `ui.success`, add `ui.success_download`**

Remove the `"ui.success"` key from all 12 locale files.

Add `"ui.success_download"`:

| Locale | Value |
|--------|-------|
| en | `"✅ Download ready — click to save"` |
| ko | `"✅ 다운로드 완료 — 클릭하여 저장"` |
| ja | `"✅ ダウンロード完了 — クリックして保存"` |
| zh-TW | `"✅ 下載完成 — 點擊儲存"` |
| zh-CN | `"✅ 下载完成 — 点击保存"` |
| de | `"✅ Download bereit — zum Speichern klicken"` |
| es | `"✅ Descarga lista — clic para guardar"` |
| fr | `"✅ Téléchargement prêt — cliquer pour sauvegarder"` |
| pt | `"✅ Download pronto — clique para salvar"` |
| vi | `"✅ Đã tải xong — nhấp để lưu"` |
| ms | `"✅ Muat turun siap — klik untuk simpan"` |
| id | `"✅ Unduhan siap — klik untuk simpan"` |

- [ ] **Step 4.2: Add `send_from_directory` to Flask import in `app.py`**

```python
# Change line 5:
from flask import Flask, render_template, request, jsonify, send_from_directory
```

- [ ] **Step 4.3: Add `_completed` dict after `_jobs` in `app.py`**

```python
_jobs: dict = {}
_completed: dict = {}  # job_id → filename; persists after _jobs entry is removed
```

- [ ] **Step 4.4: Update the `_jobs` initialization and download thread `run()` in `download()`**

Change `_jobs[job_id]` initialization:
```python
_jobs[job_id] = {"status": "pending", "filename": None, "error": None}
```

Replace the `run()` inner function:
```python
def run():
    _jobs[job_id]["status"] = "running"
    try:
        filepath = download_video(url, DOWNLOAD_DIR)
        filename = os.path.basename(filepath)
        _completed[job_id] = filename           # (1) write _completed FIRST (GIL ordering)
        _jobs[job_id].update({"status": "done", "filename": filename})  # (2) then mark done
    except Exception as e:
        _jobs[job_id].update({"status": "error", "error": str(e)})
```

- [ ] **Step 4.5: Add `serve_file()` endpoint to `app.py` (after `job_status()`)**

```python
@app.route('/api/file/<job_id>', methods=['GET'])
def serve_file(job_id):
    filename = _completed.get(job_id)
    if not filename:
        return jsonify({'error': 'File not found or already downloaded'}), 404
    _completed.pop(job_id, None)  # one-time link: consumed on first successful serve
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)
```

- [ ] **Step 4.6: Update `static/js/script.js` — replace `status === 'done'` branch**

Find and replace the `done` branch inside the `pollTimer` interval callback (currently lines 116-118):

```javascript
// Before:
if (statusData.status === 'done') {
    stopPolling();
    showStatus(window.I18N['ui.success'].replace('{filepath}', statusData.filepath), 'success');
}

// After:
if (statusData.status === 'done') {
    stopPolling();
    const link = document.createElement('a');
    link.href = `/api/file/${jobId}`;
    link.textContent = window.I18N['ui.success_download'];
    link.download = '';
    link.addEventListener('click', () => {
        setTimeout(() => link.remove(), 100);  // disable after first click
    });
    statusMessage.replaceChildren(link);
    statusMessage.className = '';
    statusMessage.classList.add('status-success');
    statusMessage.classList.remove('hidden');
}
```

- [ ] **Step 4.7: Run i18n audit**

```bash
python -c "
import json
from pathlib import Path
base = json.loads(Path('locales/en.json').read_text(encoding='utf-8'))
assert 'ui.success' not in base, 'ui.success should be removed'
assert 'ui.success_download' in base
assert 'app.error_invalid_url' in base
print(f'Total keys: {len(base)}')
for p in sorted(Path('locales').glob('*.json')):
    other = json.loads(p.read_text(encoding='utf-8'))
    ok = set(base) == set(other)
    print(p.name, 'OK' if ok else f'FAIL')
"
```
Expected: `Total keys: 51`, all locales OK

- [ ] **Step 4.8: Manual end-to-end file serving test**

```bash
python app.py
JOB=$(curl -s -X POST http://localhost:5000/api/download \
  -H 'Content-Type: application/json' \
  -d '{"url":"<valid-youtube-url>"}' | python -c "import sys,json; print(json.load(sys.stdin)['job_id'])")
# Poll until done:
curl -s http://localhost:5000/api/status/$JOB | python -m json.tool
# → {"status": "done", "filename": "title.mp4"}  (no absolute path)
curl -O http://localhost:5000/api/file/$JOB
# → Downloads the file
curl -s http://localhost:5000/api/file/$JOB | python -m json.tool
# → {"error": "File not found or already downloaded"}  HTTP 404 (one-time link)
```

- [ ] **Step 4.9: Commit atomically (app.py + script.js + locales)**

```bash
git add app.py static/js/script.js locales/
git commit -m "feat(security): S-3/S-4 file serving endpoint; remove absolute path from API responses"
```

---

## Task 5: M-4 — Dependency Injection for `download_service.py`

**Spec:** `docs/superpowers/specs/2026-05-20-download-experience-design.md` (M-4)

**Files:**
- Modify: `download_service.py` — full rewrite with DI params

- [ ] **Step 5.1: Rewrite `download_service.py` with DI params**

```python
import os
import threading
from typing import Optional, Callable
from i18n import t, format_duration


def get_video_info(url: str, ydl_class=None) -> dict:
    import yt_dlp as _yt_dlp
    if ydl_class is None:
        ydl_class = _yt_dlp.YoutubeDL
    ydl_opts = {
        'skip_download': True,
        'extract_flat': False,
    }
    with ydl_class(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        duration = info_dict.get('duration_string')
        raw_dur = info_dict.get('duration')
        if not duration and raw_dur:
            duration = format_duration(int(raw_dur))
        return {
            'title': info_dict.get('title'),
            'thumbnail': info_dict.get('thumbnail'),
            'duration': duration,
            'channel': info_dict.get('uploader')
        }


def download_video(
    url: str,
    output_dir: str,
    ydl_class=None,
    progress_hook: Optional[Callable] = None,
    cancel_event: Optional[threading.Event] = None,
) -> str:
    import yt_dlp as _yt_dlp
    if ydl_class is None:
        ydl_class = _yt_dlp.YoutubeDL

    hooks = []
    if progress_hook:
        hooks.append(progress_hook)
    if cancel_event:
        def _cancel_hook(d):
            if cancel_event.is_set():
                raise Exception("Download cancelled")
        hooks.append(_cancel_hook)

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(output_dir, '%(title).100s.%(ext)s'),
        'merge_output_format': 'mp4',
        'windowsfilenames': True,
        'nocheckcertificate': True,
        'progress_hooks': hooks,
    }
    with ydl_class(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        base, _ = os.path.splitext(filename)
        return base + '.mp4'
```

- [ ] **Step 5.2: Commit**

```bash
git add download_service.py
git commit -m "refactor(download): M-4 DI params — ydl_class, progress_hook, cancel_event"
```

---

## Task 6: U-1 — Download Progress

**Spec:** `docs/superpowers/specs/2026-05-20-download-experience-design.md` (U-1)

**Files:**
- Modify: `app.py` — expand `_jobs` schema, add `make_progress_hook()`, pass to thread
- Modify: `locales/*.json` (×12) — add `ui.progress_label`, `ui.progress_speed`

- [ ] **Step 6.1: Add `ui.progress_label` and `ui.progress_speed` to all 12 locale files**

| Locale | `ui.progress_label` | `ui.progress_speed` |
|--------|---------------------|---------------------|
| en | `"Downloading... {pct}%"` | `"{speed} — {eta}s remaining"` |
| ko | `"다운로드 중... {pct}%"` | `"{speed} — 남은 시간 {eta}초"` |
| ja | `"ダウンロード中... {pct}%"` | `"{speed} — 残り{eta}秒"` |
| zh-TW | `"下載中... {pct}%"` | `"{speed} — 剩餘{eta}秒"` |
| zh-CN | `"下载中... {pct}%"` | `"{speed} — 剩余{eta}秒"` |
| de | `"Herunterladen... {pct}%"` | `"{speed} — noch {eta}s"` |
| es | `"Descargando... {pct}%"` | `"{speed} — {eta}s restantes"` |
| fr | `"Téléchargement... {pct}%"` | `"{speed} — {eta}s restantes"` |
| pt | `"Baixando... {pct}%"` | `"{speed} — {eta}s restantes"` |
| vi | `"Đang tải... {pct}%"` | `"{speed} — còn {eta}s"` |
| ms | `"Memuat turun... {pct}%"` | `"{speed} — {eta}s lagi"` |
| id | `"Mengunduh... {pct}%"` | `"{speed} — {eta}s lagi"` |

- [ ] **Step 6.2: Expand `_jobs` schema in `download()` to include progress fields**

```python
_jobs[job_id] = {
    "status": "pending",
    "filename": None,
    "error": None,
    "progress": 0,
    "speed": None,
    "eta": None,
}
```

- [ ] **Step 6.3: Add `make_progress_hook()` to `app.py` (before the `download()` route)**

```python
def make_progress_hook(job_id):
    def hook(d):
        if d['status'] == 'downloading':
            # _percent_str is deprecated in yt-dlp ≥2024; use byte counts
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            if total:
                _jobs[job_id]['progress'] = int(downloaded * 100 / total)
            _jobs[job_id]['speed'] = d.get('_speed_str')
            _jobs[job_id]['eta'] = d.get('eta')
    return hook
```

- [ ] **Step 6.4: Pass `progress_hook` to `download_video()` in the download thread**

In `run()` inside `download()`:
```python
filepath = download_video(url, DOWNLOAD_DIR, progress_hook=make_progress_hook(job_id))
```

- [ ] **Step 6.5: Run i18n audit**

```bash
python -c "
import json; from pathlib import Path
base = json.loads(Path('locales/en.json').read_text(encoding='utf-8'))
print(f'Keys: {len(base)}')  # expect 53
for p in sorted(Path('locales').glob('*.json')):
    other = json.loads(p.read_text(encoding='utf-8'))
    print(p.name, 'OK' if set(base) == set(other) else 'FAIL')
"
```

- [ ] **Step 6.6: Commit**

```bash
git add app.py locales/
git commit -m "feat(ux): U-1 download progress — percent, speed, ETA via /api/status"
```

---

## Task 7: U-2 — Download Cancellation

**Spec:** `docs/superpowers/specs/2026-05-20-download-experience-design.md` (U-2)

**Files:**
- Modify: `app.py` — add `_cancel_events`, update `download()` thread, add `DELETE /api/status/<job_id>`
- Modify: `locales/*.json` (×12) — add `ui.btn_cancel`

- [ ] **Step 7.1: Add `ui.btn_cancel` to all 12 locale files**

| Locale | Value |
|--------|-------|
| en | `"Cancel"` |
| ko | `"취소"` |
| ja | `"キャンセル"` |
| zh-TW | `"取消"` |
| zh-CN | `"取消"` |
| de | `"Abbrechen"` |
| es | `"Cancelar"` |
| fr | `"Annuler"` |
| pt | `"Cancelar"` |
| vi | `"Hủy"` |
| ms | `"Batal"` |
| id | `"Batal"` |

- [ ] **Step 7.2: Add `_cancel_events` dict to `app.py` (after `_completed`)**

```python
_cancel_events: dict = {}  # job_id → threading.Event
```

- [ ] **Step 7.3: Update `download()` — create cancel_event and pass to thread**

Before `threading.Thread(...)`:
```python
cancel_event = threading.Event()
_cancel_events[job_id] = cancel_event
```

Replace the `run()` function:
```python
def run():
    _jobs[job_id]["status"] = "running"
    try:
        filepath = download_video(
            url, DOWNLOAD_DIR,
            progress_hook=make_progress_hook(job_id),
            cancel_event=cancel_event,
        )
        filename = os.path.basename(filepath)
        _completed[job_id] = filename           # (1) write _completed FIRST
        _jobs[job_id].update({"status": "done", "filename": filename})  # (2) then done
    except Exception as e:
        if cancel_event.is_set():
            _jobs[job_id].update({"status": "cancelled", "error": "Download cancelled by user"})
        else:
            _jobs[job_id].update({"status": "error", "error": str(e)})
    finally:
        _cancel_events.pop(job_id, None)  # always clean up cancel event
```

- [ ] **Step 7.4: Add `cancel_job()` endpoint to `app.py` (after `serve_file()`)**

```python
@app.route('/api/status/<job_id>', methods=['DELETE'])
def cancel_job(job_id):
    event = _cancel_events.get(job_id)  # peek — do NOT pop, thread still uses _jobs
    if not event:
        return jsonify({'error': 'Job not found or already finished'}), 404
    event.set()  # signals cancel hook; thread catches exception and sets 'cancelled' status
    return jsonify({'cancelled': True})
```

- [ ] **Step 7.5: Run i18n audit**

```bash
python -c "
import json; from pathlib import Path
base = json.loads(Path('locales/en.json').read_text(encoding='utf-8'))
print(f'Keys: {len(base)}')  # expect 54
for p in sorted(Path('locales').glob('*.json')):
    other = json.loads(p.read_text(encoding='utf-8'))
    print(p.name, 'OK' if set(base) == set(other) else 'FAIL')
"
```

- [ ] **Step 7.6: Manual cancel smoke test**

```bash
python app.py
JOB=$(curl -s -X POST http://localhost:5000/api/download \
  -H 'Content-Type: application/json' \
  -d '{"url":"https://www.youtube.com/watch?v=dQw4w9WgXcQ"}' \
  | python -c "import sys,json; print(json.load(sys.stdin)['job_id'])")
curl -s -X DELETE http://localhost:5000/api/status/$JOB | python -m json.tool
# → {"cancelled": true}
```

- [ ] **Step 7.7: Commit**

```bash
git add app.py locales/
git commit -m "feat(ux): U-2 download cancellation — DELETE /api/status/<job_id>"
```

---

## Task 8: M-1 — Download Queue UI

**Spec:** `docs/superpowers/specs/2026-05-20-download-experience-design.md` (M-1)

**Files:**
- Modify: `templates/index.html` — add `#queue-panel` and `#queue-list`
- Modify: `static/css/styles.css` — add queue item styles
- Modify: `static/js/script.js` — full rewrite with queue Map state management
- Modify: `locales/*.json` (×12) — add `ui.queue_title`, `ui.queue_empty`

- [ ] **Step 8.1: Add `ui.queue_title` and `ui.queue_empty` to all 12 locale files**

`ui.queue_title`:

| Locale | Value |
|--------|-------|
| en | `"Download Queue"` |
| ko | `"다운로드 대기열"` |
| ja | `"ダウンロードキュー"` |
| zh-TW | `"下載佇列"` |
| zh-CN | `"下载队列"` |
| de | `"Download-Warteschlange"` |
| es | `"Cola de descarga"` |
| fr | `"File d'attente"` |
| pt | `"Fila de download"` |
| vi | `"Hàng đợi tải xuống"` |
| ms | `"Giliran Muat Turun"` |
| id | `"Antrian Unduhan"` |

`ui.queue_empty`:

| Locale | Value |
|--------|-------|
| en | `"No downloads in queue."` |
| ko | `"대기 중인 다운로드가 없습니다."` |
| ja | `"ダウンロード待ちはありません。"` |
| zh-TW | `"佇列中沒有下載項目。"` |
| zh-CN | `"队列中没有下载项目。"` |
| de | `"Keine Downloads in der Warteschlange."` |
| es | `"No hay descargas en cola."` |
| fr | `"Aucun téléchargement en attente."` |
| pt | `"Nenhum download na fila."` |
| vi | `"Không có tải xuống trong hàng đợi."` |
| ms | `"Tiada muat turun dalam giliran."` |
| id | `"Tidak ada unduhan dalam antrian."` |

- [ ] **Step 8.2: Add queue panel to `templates/index.html`**

Inside `<main>`, after `<div id="status-message" class="hidden"></div>` (line 58), insert:
```html
<section id="queue-panel" class="hidden">
    <h2>{{ i18n['ui.queue_title'] }}</h2>
    <ul id="queue-list"></ul>
</section>
```

- [ ] **Step 8.3: Add queue styles to `static/css/styles.css`**

Append before the existing `@media (max-width: 600px)` block:
```css
/* Queue Panel */
#queue-panel {
    margin-top: 24px;
}

#queue-panel h2 {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-secondary);
    margin-bottom: 12px;
}

#queue-list {
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 12px;
}

.queue-item {
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: 12px;
    padding: 16px;
    display: grid;
    grid-template-columns: 1fr auto;
    gap: 8px;
    align-items: center;
}

.queue-item-title {
    font-size: 14px;
    font-weight: 500;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
}

.queue-item-progress {
    grid-column: 1 / -1;
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.queue-item-progress progress {
    width: 100%;
    height: 4px;
    border-radius: 2px;
}

.queue-item-speed {
    font-size: 12px;
    color: var(--text-secondary);
}

.queue-cancel-btn {
    background: transparent;
    border: 1px solid var(--glass-border);
    color: var(--text-secondary);
    border-radius: 8px;
    padding: 6px 12px;
    font-size: 13px;
    cursor: pointer;
    min-height: 44px;
    transition: all 0.2s ease;
}

.queue-cancel-btn:hover {
    border-color: var(--primary-color);
    color: var(--primary-color);
}

.queue-download-link {
    grid-column: 1 / -1;
    color: var(--primary-color);
    text-decoration: none;
    font-size: 14px;
    font-weight: 500;
}
```

- [ ] **Step 8.4: Rewrite `static/js/script.js` with queue state management**

Replace the entire file with:

```javascript
document.addEventListener('DOMContentLoaded', () => {
    const urlForm = document.getElementById('url-form');
    const urlInput = document.getElementById('url-input');
    const fetchBtn = document.getElementById('fetch-btn');

    const loading = document.getElementById('loading');
    const loadingText = document.getElementById('loading-text');

    const videoCard = document.getElementById('video-card');
    const videoThumbnail = document.getElementById('video-thumbnail');
    const videoTitle = document.getElementById('video-title');
    const videoChannel = document.getElementById('video-channel');
    const videoDuration = document.getElementById('video-duration');

    const downloadBtn = document.getElementById('download-btn');
    const statusMessage = document.getElementById('status-message');
    const queuePanel = document.getElementById('queue-panel');
    const queueList = document.getElementById('queue-list');

    let currentUrl = '';
    let currentVideoTitle = '';

    // queue Map: jobId → { li: HTMLElement, pollTimer: number }
    const queue = new Map();

    urlForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const url = urlInput.value.trim();
        if (!url) return;

        hideStatus();
        videoCard.classList.add('hidden');
        loading.classList.remove('hidden');
        loadingText.textContent = window.I18N['ui.loading_info'];
        fetchBtn.disabled = true;
        currentUrl = url;

        try {
            const response = await fetch('/api/info', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url })
            });

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || window.I18N['ui.error_info']);
            }

            videoThumbnail.src = data.thumbnail;
            videoTitle.textContent = data.title;
            videoChannel.textContent = data.channel;
            videoDuration.textContent = data.duration || '';
            currentVideoTitle = data.title;

            loading.classList.add('hidden');
            videoCard.classList.remove('hidden');

        } catch (error) {
            loading.classList.add('hidden');
            showStatus(error.message, 'error');
        } finally {
            fetchBtn.disabled = false;
        }
    });

    downloadBtn.addEventListener('click', async () => {
        if (!currentUrl) return;

        try {
            const response = await fetch('/api/download', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: currentUrl })
            });

            const data = await response.json();

            if (!response.ok) {
                showStatus(data.error || window.I18N['ui.error_download'], 'error');
                return;
            }

            addToQueue(data.job_id, currentVideoTitle);

        } catch (error) {
            showStatus(error.message, 'error');
        }
    });

    function addToQueue(jobId, title) {
        queuePanel.classList.remove('hidden');

        const li = document.createElement('li');
        li.className = 'queue-item';
        li.dataset.jobId = jobId;

        const titleEl = document.createElement('div');
        titleEl.className = 'queue-item-title';
        titleEl.textContent = title || jobId;

        const cancelBtn = document.createElement('button');
        cancelBtn.className = 'queue-cancel-btn';
        cancelBtn.textContent = window.I18N['ui.btn_cancel'];
        cancelBtn.addEventListener('click', () => cancelJob(jobId, cancelBtn));

        const progressWrapper = document.createElement('div');
        progressWrapper.className = 'queue-item-progress';

        const progressEl = document.createElement('progress');
        progressEl.value = 0;
        progressEl.max = 100;

        const speedEl = document.createElement('div');
        speedEl.className = 'queue-item-speed';

        progressWrapper.append(progressEl, speedEl);
        li.append(titleEl, cancelBtn, progressWrapper);
        queueList.appendChild(li);

        const pollTimer = setInterval(() => pollJob(jobId), 2000);
        queue.set(jobId, { li, pollTimer });
    }

    async function pollJob(jobId) {
        try {
            const res = await fetch(`/api/status/${jobId}`);
            const data = await res.json();
            updateQueueItem(jobId, data);
        } catch (_) {
            stopJobPolling(jobId);
        }
    }

    function updateQueueItem(jobId, statusData) {
        const entry = queue.get(jobId);
        if (!entry) return;
        const { li } = entry;

        const progressEl = li.querySelector('progress');
        const speedEl = li.querySelector('.queue-item-speed');
        const cancelBtn = li.querySelector('.queue-cancel-btn');

        if (statusData.status === 'running') {
            const pct = statusData.progress || 0;
            if (progressEl) progressEl.value = pct;
            if (speedEl) {
                speedEl.textContent = statusData.speed
                    ? window.I18N['ui.progress_speed']
                        .replace('{speed}', statusData.speed)
                        .replace('{eta}', statusData.eta ?? '?')
                    : window.I18N['ui.progress_label'].replace('{pct}', pct);
            }
        } else if (statusData.status === 'done') {
            stopJobPolling(jobId);
            if (cancelBtn) cancelBtn.remove();
            li.querySelector('.queue-item-progress')?.remove();

            const link = document.createElement('a');
            link.href = `/api/file/${jobId}`;
            link.textContent = window.I18N['ui.success_download'];
            link.className = 'queue-download-link';
            link.download = '';
            link.addEventListener('click', () => setTimeout(() => link.remove(), 100));
            li.appendChild(link);

        } else if (statusData.status === 'error' || statusData.status === 'cancelled') {
            stopJobPolling(jobId);
            if (cancelBtn) cancelBtn.remove();
            const msg = document.createElement('span');
            msg.className = 'queue-item-speed';
            msg.style.color = 'var(--primary-color)';
            msg.textContent = statusData.error || statusData.status;
            li.querySelector('.queue-item-progress')?.remove();
            li.appendChild(msg);
        }
    }

    async function cancelJob(jobId, cancelBtn) {
        cancelBtn.disabled = true;
        try {
            await fetch(`/api/status/${jobId}`, { method: 'DELETE' });
        } catch (_) { /* ignore */ }
    }

    function stopJobPolling(jobId) {
        const entry = queue.get(jobId);
        if (entry?.pollTimer) {
            clearInterval(entry.pollTimer);
        }
    }

    function showStatus(message, type) {
        statusMessage.textContent = message;
        statusMessage.className = '';
        statusMessage.classList.add('status-' + type);
        statusMessage.classList.remove('hidden');
    }

    function hideStatus() {
        statusMessage.classList.add('hidden');
    }
});
```

- [ ] **Step 8.5: Run i18n audit**

```bash
python -c "
import json; from pathlib import Path
base = json.loads(Path('locales/en.json').read_text(encoding='utf-8'))
print(f'Keys: {len(base)}')  # expect 56
for p in sorted(Path('locales').glob('*.json')):
    other = json.loads(p.read_text(encoding='utf-8'))
    print(p.name, 'OK' if set(base) == set(other) else 'FAIL')
"
```

- [ ] **Step 8.6: Manual queue test**

```bash
python app.py
# Open http://localhost:5000
# Paste URL → Fetch → Download MP4
# Queue panel appears below, shows progress bar + cancel button
# On completion: cancel button removed, download link appears
# Clicking download link saves file; second click removes the link
```

- [ ] **Step 8.7: Commit**

```bash
git add templates/index.html static/js/script.js static/css/styles.css locales/
git commit -m "feat(ux): M-1 download queue UI — progress, cancel, multi-download support"
```

---

## Task 9: M-2 — Light Mode Support

**Spec:** `docs/superpowers/specs/2026-05-20-ui-polish-design.md` (M-2)

**Files:**
- Modify: `static/css/styles.css` — append `@media (prefers-color-scheme: light)` block

> The app defaults to dark glassmorphism (`:root` has `--bg-color: #0d0f17`).
> Light mode is added as an override, not the other way around.

- [ ] **Step 9.1: Append light mode media query to end of `static/css/styles.css`**

```css
@media (prefers-color-scheme: light) {
  :root {
    --bg-color: #f0f2f5;
    --glass-bg: rgba(255, 255, 255, 0.65);
    --glass-border: rgba(0, 0, 0, 0.08);
    --text-primary: #1a1a2e;
    --text-secondary: rgba(26, 26, 46, 0.6);
    /* --primary-color and --primary-color-hover intentionally unchanged */
  }

  .glass-container {
    background: rgba(255, 255, 255, 0.6);
    box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.15);
  }

  .card-glass {
    background: rgba(255, 255, 255, 0.5);
  }

  .download-action {
    background: rgba(0, 0, 0, 0.04);
    color: var(--text-primary);
  }

  .download-action:hover {
    background: rgba(0, 0, 0, 0.08);
    border-color: rgba(0, 0, 0, 0.15);
  }

  #url-input:focus {
    border-color: rgba(255, 59, 48, 0.4);
    background: rgba(255, 255, 255, 0.8);
    box-shadow: 0 0 0 4px rgba(255, 59, 48, 0.08);
  }

  #url-input::placeholder {
    color: rgba(0, 0, 0, 0.3);
  }

  .spinner {
    border-color: rgba(0, 0, 0, 0.1);
    border-top-color: var(--primary-color);
  }
}
```

- [ ] **Step 9.2: Test in browser with OS light mode**

Switch OS to Light mode (Windows: Settings → Personalization → Colors → Light).
Open http://localhost:5000 — background should be light grey, text dark, red accent unchanged.
Switch back to Dark — original dark theme should return.

- [ ] **Step 9.3: Commit**

```bash
git add static/css/styles.css
git commit -m "feat(ui): M-2 light mode via prefers-color-scheme: light"
```

---

## Task 10: M-3 — Mobile Responsive Layout

**Spec:** `docs/superpowers/specs/2026-05-20-ui-polish-design.md` (M-3)

**Files:**
- Modify: `static/css/styles.css` — touch targets, tablet breakpoint

> Viewport meta tag already present in `templates/index.html` line 5 — no action required.

- [ ] **Step 10.1: Add minimum touch target height to buttons in `styles.css`**

After the `#fetch-btn:active` rule (around line 165), add:
```css
#fetch-btn,
#download-btn,
.queue-cancel-btn {
    min-height: 44px;
}
```

- [ ] **Step 10.2: Add tablet breakpoint for `#video-card` layout**

Add before the existing `@media (max-width: 600px)` block:
```css
@media (min-width: 600px) {
  #video-card .card-glass {
    flex-direction: row;
  }

  /* .queue-item tablet layout — grid-template-columns defined here */
  .queue-item {
    grid-template-columns: 1fr auto;
  }
}
```

- [ ] **Step 10.3: Verify at mobile viewport**

Open Chrome DevTools → Toggle device toolbar → iPhone SE (375×667).
Check:
- No horizontal scroll
- Input and Fetch button stack vertically (existing breakpoint handles this)
- Download MP4 and Cancel buttons are ≥44px tall
- Queue items display correctly

- [ ] **Step 10.4: Commit**

```bash
git add static/css/styles.css
git commit -m "feat(ui): M-3 mobile responsive — touch targets min-height, tablet breakpoint"
```

---

## Task 11: M-6 — Downloads Folder Cleanup

**Spec:** `docs/superpowers/specs/2026-05-20-ui-polish-design.md` (M-6)

**Files:**
- Modify: `app.py` — add `_cleanup_downloads()`, add `time`/`Path` imports, call at startup

- [ ] **Step 11.1: Add `time` and `Path` to imports in `app.py`**

```python
import time
from pathlib import Path
```

- [ ] **Step 11.2: Add `_cleanup_downloads()` function before `app = Flask(__name__)`**

```python
def _cleanup_downloads(directory: str, keep_hours: int = 24) -> None:
    """Delete files in directory older than keep_hours. keep_hours=0 disables cleanup."""
    if keep_hours == 0:
        return
    p_dir = Path(directory)
    if not p_dir.exists():
        return  # directory not yet created — safe skip
    cutoff = time.time() - keep_hours * 3600
    for p in p_dir.iterdir():
        if p.is_file() and p.stat().st_mtime < cutoff:
            try:
                p.unlink()
            except OSError:
                pass  # file in use (Windows) or already gone — skip silently
```

- [ ] **Step 11.3: Call `_cleanup_downloads()` at startup (inside `if __name__ == '__main__':`, after `os.makedirs`)**

The `if __name__ == '__main__':` block should become:
```python
if __name__ == '__main__':
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    _keep_hours = int(os.environ.get('QUICKDL_KEEP_HOURS', '24'))
    _cleanup_downloads(DOWNLOAD_DIR, _keep_hours)
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(debug=debug, threaded=True, host='0.0.0.0', port=5000)
```

Note: `os.makedirs(DOWNLOAD_DIR, exist_ok=True)` is currently at module level (line 16). Keep it there for WSGI/Gunicorn compatibility. The `__main__` block's call is a second guard — redundant but harmless, and ensures cleanup runs after the directory exists.

- [ ] **Step 11.4: Test cleanup function**

```bash
python -c "
import os, time
from pathlib import Path
from app import _cleanup_downloads

os.makedirs('downloads', exist_ok=True)

# Test deletion of old file
p = Path('downloads/test_old.mp4')
p.write_text('test')
os.utime(p, (0, 0))  # set mtime to Unix epoch (very old)
_cleanup_downloads('downloads', keep_hours=1)
assert not p.exists(), 'Old file was not deleted'
print('Deletion test OK')

# Test keep_hours=0 disables cleanup
p.write_text('test')
os.utime(p, (0, 0))
_cleanup_downloads('downloads', keep_hours=0)
assert p.exists(), 'File deleted when keep_hours=0'
p.unlink()
print('keep_hours=0 (no-op) test OK')
"
```

- [ ] **Step 11.5: Commit**

```bash
git add app.py
git commit -m "feat(ops): M-6 downloads cleanup on startup — QUICKDL_KEEP_HOURS env var"
```

---

## Task 12: U-3 — Expand `test_i18n.py`

**Spec:** `docs/superpowers/specs/2026-05-20-testing-ci-design.md` (U-3)

**Prerequisite:** Task 1 (created `test_i18n.py` with format_duration tests).

**Files:**
- Modify: `test_i18n.py` — add remaining 10 test functions

- [ ] **Step 12.1: Add remaining tests to `test_i18n.py`**

Insert these functions **before** the existing `if __name__ == '__main__':` block (they must be defined before the block can discover them). Then replace the `if __name__` block with the updated version below.

```python
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


def test_get_all_returns_dict():
    i18n.init('en')
    all_t = i18n.get_all()
    assert isinstance(all_t, dict)
    assert len(all_t) > 0


def test_all_locales_have_same_keys():
    """All locale files must have identical key sets to en.json."""
    from pathlib import Path as _Path
    root = _Path(__file__).parent
    base = json.loads((root / 'locales' / 'en.json').read_text(encoding='utf-8'))
    for p in sorted((root / 'locales').glob('*.json')):
        other = json.loads(p.read_text(encoding='utf-8'))
        missing = set(base) - set(other)
        extra = set(other) - set(base)
        assert not missing, f'{p.name} missing keys: {missing}'
        assert not extra, f'{p.name} has extra keys: {extra}'


# pytest-only tests (use monkeypatch fixture):
def test_detect_lang_env_override(monkeypatch):
    monkeypatch.setenv('QUICKDL_LANG', 'ja')
    i18n.init()
    assert i18n.get_lang() == 'ja'


def test_detect_lang_unsupported_env_falls_back(monkeypatch):
    monkeypatch.setenv('QUICKDL_LANG', 'zz')
    i18n.init()
    assert i18n.get_lang() == 'en'
```

Also update the `if __name__ == '__main__':` block to skip monkeypatch tests:
```python
if __name__ == '__main__':
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

- [ ] **Step 12.2: Run tests with pytest**

```bash
pytest test_i18n.py -v
```
Expected: all PASS (including monkeypatch tests)

- [ ] **Step 12.3: Commit**

```bash
git add test_i18n.py
git commit -m "test(i18n): U-3 complete i18n unit test suite — 13 tests"
```

---

## Task 13: U-4 — Create `test_app.py`

**Spec:** `docs/superpowers/specs/2026-05-20-testing-ci-design.md` (U-4)

**Prerequisite:** Groups A (Tasks 2–4) and B (Tasks 5–7) fully implemented.

**Files:**
- Create: `test_app.py`

- [ ] **Step 13.1: Create `test_app.py`**

```python
# test_app.py
import json
import sys
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, '.')


class TestAppAPI(unittest.TestCase):
    # Prerequisites: Groups A (S-1, S-3/S-4) and B (U-1, U-2) must be implemented.
    # Specifically: _completed, _cancel_events, _validate_url must exist in app.py.

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
        r = self.client.post('/api/info', json={}, content_type='application/json')
        self.assertEqual(r.status_code, 400)

    def test_info_invalid_scheme(self):
        # Requires Group A S-1 URL validation
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
        r = self.client.post('/api/download', json={}, content_type='application/json')
        self.assertEqual(r.status_code, 400)

    def test_download_invalid_scheme(self):
        # Requires Group A S-1 URL validation
        r = self.client.post('/api/download',
            json={'url': 'ftp://bad.com'},
            content_type='application/json')
        self.assertEqual(r.status_code, 400)

    def test_download_returns_job_id(self):
        # Block the background thread to avoid race on status assertion
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
        block.set()  # let background thread complete cleanly

    # --- /api/status ---

    def test_status_not_found(self):
        r = self.client.get('/api/status/nonexistent-job-id')
        self.assertEqual(r.status_code, 404)

    def test_status_returns_progress(self):
        import uuid
        job_id = str(uuid.uuid4())
        # Schema matches the full _jobs structure after Groups A + B
        self.app_module._jobs[job_id] = {
            'status': 'running',
            'progress': 50,
            'speed': None,
            'eta': None,
            'filename': None,
            'error': None,
        }
        r = self.client.get(f'/api/status/{job_id}')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(json.loads(r.data)['progress'], 50)

    # --- /api/file ---

    def test_file_not_found(self):
        r = self.client.get('/api/file/nonexistent-job-id')
        self.assertEqual(r.status_code, 404)


if __name__ == '__main__':
    unittest.main()
```

- [ ] **Step 13.2: Run tests**

```bash
python test_app.py
```
Expected: `OK (9 tests)` with no failures

- [ ] **Step 13.3: Commit**

```bash
git add test_app.py
git commit -m "test(api): U-4 Flask API unit tests with mocks"
```

---

## Task 14: U-5 + M-5 — GitHub Actions CI

**Spec:** `docs/superpowers/specs/2026-05-20-testing-ci-design.md` (U-5, M-5)

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 14.1: Create `.github/workflows/ci.yml`**

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
          # pywebview and pystray excluded — require a display

      - name: i18n key audit
        run: |
          python -c "
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

- [ ] **Step 14.2: Verify YAML is valid**

```bash
python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml')); print('YAML OK')"
# If yaml not installed: pip install pyyaml
```

- [ ] **Step 14.3: Commit**

```bash
git add .github/
git commit -m "ci: U-5/M-5 GitHub Actions CI — i18n audit gate + unit tests on 3.8/3.10/3.12"
```

---

## Final Verification

```bash
# 1. All tests pass
pytest test_i18n.py -v
python test_app.py

# 2. i18n audit — all 12 locales have 56 keys
python -c "
import json
from pathlib import Path
base = json.loads(Path('locales/en.json').read_text(encoding='utf-8'))
print(f'Total keys: {len(base)}')  # expect 56
for p in sorted(Path('locales').glob('*.json')):
    other = json.loads(p.read_text(encoding='utf-8'))
    print(p.name, 'OK' if set(base) == set(other) else 'FAIL')
"

# 3. Key assertions
python -c "
import json
from pathlib import Path
en = json.loads(Path('locales/en.json').read_text(encoding='utf-8'))
assert 'ui.success' not in en, 'should be removed'
assert 'ui.success_download' in en
assert 'app.error_invalid_url' in en
assert 'ui.progress_label' in en
assert 'ui.progress_speed' in en
assert 'ui.queue_title' in en
assert 'ui.queue_empty' in en
assert 'ui.btn_cancel' in en
print('All key assertions pass')
"

# 4. Server smoke test
python app.py &
sleep 2
curl -s http://localhost:5000/ | grep -q 'YouTube Fetcher' && echo 'Server OK'
curl -s -X POST http://localhost:5000/api/info \
  -H 'Content-Type: application/json' \
  -d '{"url":"file:///etc"}' | python -c "import sys,json; d=json.load(sys.stdin); assert 'error' in d; print('URL validation OK')"
kill %1
```
