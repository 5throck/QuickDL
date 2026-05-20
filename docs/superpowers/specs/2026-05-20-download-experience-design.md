# QuickDL — Group B: Download Experience Design Spec

**Date:** 2026-05-20
**Scope:** U-1 (progress), U-2 (cancel), M-1 (queue UI), M-4 (dependency injection)

---

## Overview

Four tightly coupled improvements that together transform single-shot downloads into a full download queue with real-time progress and cancellation. All items share the same job data structure and touch the same files, so they are designed and implemented together.

---

## M-4: Dependency Injection for `download_service.py`

This is the foundation that enables U-1, U-2, and later testing (U-3, U-4). Implement first.

### Problem
`download_video()` creates `yt_dlp.YoutubeDL` internally — untestable without real network calls, and no hook injection point.

### Design

```python
# download_service.py
from typing import Optional, Callable
import threading

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

`get_video_info()` gets the same `ydl_class` injection for testability:
```python
def get_video_info(url: str, ydl_class=None) -> dict:
    import yt_dlp as _yt_dlp
    if ydl_class is None:
        ydl_class = _yt_dlp.YoutubeDL
    ...
```

---

## U-1: Download Progress

### Problem
Downloads show only a spinner — no percentage, no feedback for long videos.

### Design

**Job schema update:**
```python
_jobs[job_id] = {
    "status": "pending",
    "filename": None,
    "error": None,
    "progress": 0,       # 0–100 integer
    "speed": None,       # e.g. "1.2 MiB/s" or None
    "eta": None,         # seconds remaining or None
}
```

**Progress hook in `app.py` download thread:**
```python
def make_progress_hook(job_id):
    def hook(d):
        if d['status'] == 'downloading':
            # _percent_str is deprecated in yt-dlp ≥2024; use byte counts instead
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            if total:
                _jobs[job_id]['progress'] = int(downloaded * 100 / total)
            _jobs[job_id]['speed'] = d.get('_speed_str')
            _jobs[job_id]['eta'] = d.get('eta')
    return hook
```

Passed to `download_video(..., progress_hook=make_progress_hook(job_id), ...)`.

**`/api/status/<job_id>` response now includes:**
```json
{"status": "running", "progress": 47, "speed": "1.2 MiB/s", "eta": 32}
```

**Frontend (`script.js`):** Replace the static spinner with a `<progress>` element + speed/ETA text during polling:
```javascript
} else if (statusData.status === 'running') {
    const pct = statusData.progress || 0;
    progressEl.value = pct;
    progressEl.max = 100;
    speedEl.textContent = statusData.speed || '';
}
```

**New i18n keys:**
```json
"ui.progress_label": "Downloading... {pct}%",
"ui.progress_speed": "{speed} — {eta}s remaining"
```

---

## U-2: Download Cancellation

### Problem
Once started, a download cannot be stopped from the UI.

### Design

**Cancel event stored per job:**
```python
_cancel_events: dict = {}  # job_id → threading.Event
```

In the `download()` handler:
```python
cancel_event = threading.Event()
_cancel_events[job_id] = cancel_event
# pass to download_video(... cancel_event=cancel_event ...)
```

**New endpoint:**
```python
@app.route('/api/status/<job_id>', methods=['DELETE'])
def cancel_job(job_id):
    event = _cancel_events.get(job_id)  # peek, do NOT pop — thread still needs _jobs alive
    if not event:
        return jsonify({'error': 'Job not found or already finished'}), 404
    event.set()  # signals the cancel hook; thread catches exception and sets "cancelled" status
    return jsonify({'cancelled': True})
```

**Download thread — updated run() with cancel-aware error handling:**
```python
def run():
    _jobs[job_id]["status"] = "running"
    try:
        filepath = download_video(url, DOWNLOAD_DIR,
                                  progress_hook=make_progress_hook(job_id),
                                  cancel_event=cancel_event)
        filename = os.path.basename(filepath)
        _completed[job_id] = filename           # (1) write _completed first (GIL safety — see S-3/S-4)
        _jobs[job_id].update({"status": "done", "filename": filename})  # (2) then mark done
    except Exception as e:
        if cancel_event.is_set():
            _jobs[job_id].update({"status": "cancelled", "error": "Download cancelled by user"})
        else:
            _jobs[job_id].update({"status": "error", "error": str(e)})
    finally:
        _cancel_events.pop(job_id, None)  # always clean up, regardless of outcome
```

Rationale: the cancel endpoint must NOT pop `_jobs[job_id]` — the background thread still holds the `job_id` reference and will crash with KeyError if `_jobs[job_id]` is absent when the exception handler runs. The thread itself owns the `_cancel_events` cleanup via `finally`.

**Frontend:** Cancel button in each queue item sends `DELETE /api/status/<job_id>`.

**New i18n key:**
```json
"ui.btn_cancel": "Cancel"
```

---

## M-1: Download Queue UI

### Problem
Current UI supports only one download at a time; the download panel is a single card with no history.

### Design

**HTML structure** (new section in `templates/index.html`, below the video card):
```html
<section id="queue-panel" class="hidden">
  <h2 data-i18n="ui.queue_title"></h2>
  <ul id="queue-list"></ul>
</section>
```

Each queue item template (created by JS):
```
┌──────────────────────────────────────────────┐
│ [thumbnail] Title                  [Cancel]  │
│             Channel · Duration               │
│             ████████░░░░░░ 47% · 1.2 MiB/s  │
└──────────────────────────────────────────────┘
```
On completion → cancel button replaced with download anchor (from Group A S-4 design).
On error → red error message, retry button (optional for v1).

**State management in `script.js`:**
```javascript
const queue = new Map(); // jobId → {item el, pollTimer, cancelled}

function addToQueue(jobId, videoInfo) { ... }
function updateQueueItem(jobId, statusData) { ... }
function removeFromQueue(jobId) { ... }
```

The "Download MP4" button adds to queue without clearing the video info card, allowing multiple jobs.

**New i18n keys:**
```json
"ui.queue_title": "Download Queue",
"ui.queue_empty": "No downloads in queue.",
"ui.btn_cancel": "Cancel"
```

---

## File Map

| File | Changes |
|------|---------|
| `download_service.py` | Add `ydl_class`, `progress_hook`, `cancel_event` params to `download_video()` and `ydl_class` to `get_video_info()` |
| `app.py` | Add `_cancel_events` dict; `make_progress_hook()`; update download thread; `DELETE /api/status/<job_id>`; cleanup on terminal state. **Breaking change:** `_jobs[job_id]["filepath"]` is renamed to `"filename"` — `script.js` must be updated simultaneously (see below). |
| `templates/index.html` | Add `#queue-panel` and `#queue-list` structure |
| `static/js/script.js` | Queue Map, `addToQueue/updateQueueItem/removeFromQueue` helpers, progress element, cancel button. **Breaking:** replace `statusData.filepath` reference with `statusData.filename`. |
| `locales/*.json` (12 files) | Add `ui.progress_label`, `ui.progress_speed`, `ui.queue_title`, `ui.queue_empty`, `ui.btn_cancel` |

> **Deployment note:** `app.py` and `static/js/script.js` must be deployed atomically. The `filepath` → `filename` rename in `_jobs` will break the existing JS if backend is deployed alone. Deploy `script.js` first or both simultaneously.

---

## Verification

```python
# test_download_service.py (Group C will formalize this)
import threading
from unittest.mock import MagicMock

# 1. Progress hook called with percentage
progress_calls = []
def hook(d): progress_calls.append(d)
mock_ydl = MagicMock()
mock_ydl.return_value.__enter__ = lambda s: mock_ydl.return_value
mock_ydl.return_value.extract_info.return_value = {'title': 'test', 'ext': 'mp4'}
mock_ydl.return_value.prepare_filename.return_value = '/tmp/test.mp4'
download_video('http://example.com', '/tmp', ydl_class=mock_ydl, progress_hook=hook)
# ydl_opts['progress_hooks'] should contain hook

# 2. Cancel event stops download
event = threading.Event()
event.set()
# When passed as cancel_event, hook raises Exception("Download cancelled")
```

Manual:
```bash
# Start a large download, then cancel
curl -X POST http://localhost:5000/api/download -d '{"url":"<long-video>"}' -H 'Content-Type: application/json'
# → {"job_id": "abc"}
curl -X DELETE http://localhost:5000/api/status/abc
# → {"cancelled": true}
curl http://localhost:5000/api/status/abc
# → {"error": "Job not found"}  404
```
