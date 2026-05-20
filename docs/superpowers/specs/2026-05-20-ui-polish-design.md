# QuickDL — Group E: UI Polish Design Spec

**Date:** 2026-05-20
**Scope:** M-2 (dark mode), M-3 (mobile responsive), M-6 (downloads folder cleanup)

---

## Overview

Three UI and housekeeping improvements. M-2 and M-3 are purely CSS/HTML changes with no backend impact. M-6 is a backend-only change with no UI component.

---

## M-2: Light Mode Support (Adaptive Theme)

### Problem
The app uses a fixed dark glassmorphism theme regardless of the user's OS preference. Users who prefer light mode see a dark UI that does not match their system.

### Analysis: Default Theme is Already Dark

`static/css/styles.css` already defines dark-mode CSS custom properties on `:root`:
```css
:root {
  --bg-color: #0d0f17;          /* near-black background */
  --glass-bg: rgba(255,255,255,0.03);
  --glass-border: rgba(255,255,255,0.08);
  --primary-color: #ff3b30;     /* red accent — shared across modes */
  --primary-color-hover: #ff4d44;
  --text-primary: #ffffff;
  --text-secondary: rgba(255,255,255,0.6);
}
```

The existing glassmorphism elements also use inline `rgba()` values (`rgba(20, 22, 30, 0.6)`, `rgba(0,0,0,0.2)`) that cannot be fully tokenized as simple `var()` without `color-mix()`. The decorative blob gradients (`#ff3b30`, `#4f46e5`, `#9333ea`) are intentionally dark-mode and are not changed.

### Design

**The correct approach:** keep the existing dark `:root` as the default and add a `@media (prefers-color-scheme: light)` block that overrides the CSS variables and glassmorphism inline colors for light mode.

No renaming of existing variables. No new variable names. Minimal diff.

**Add to the end of `styles.css`:**
```css
@media (prefers-color-scheme: light) {
  :root {
    --bg-color: #f0f2f5;
    --glass-bg: rgba(255, 255, 255, 0.65);
    --glass-border: rgba(0, 0, 0, 0.08);
    --text-primary: #1a1a2e;
    --text-secondary: rgba(26, 26, 46, 0.6);
    /* --primary-color and --primary-color-hover intentionally unchanged (red accent) */
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

No JavaScript required. No new dependencies. System preference is respected automatically.

---

## M-3: Mobile Responsive Layout

### Problem
Layout is designed for desktop (fixed widths, no viewport scaling).

### Design

**Step 1: Viewport meta tag** — already present in `templates/index.html` line 5. No action required.

**Step 2: Fluid container**
```css
.container {
  width: 100%;
  max-width: 800px;
  padding: 0 1rem;
  margin: 0 auto;
}
```

**Step 3: Responsive breakpoints**
```css
/* Mobile-first base styles already apply to small screens */

/* Tablet and up: 600px+ */
@media (min-width: 600px) {
  /* #video-card uses an ID selector in the current CSS (not .video-card) */
  #video-card {
    flex-direction: row;
  }
  /* .queue-item is a forward reference to Group B (M-1 queue panel)
     Add this rule when Group B is implemented, not before. */
}
```

**Step 4: Queue panel (from Group B)** — `.queue-item` CSS class does not exist yet. It will be added in Group B (M-1). When Group B ships, add grid breakpoint:
```css
@media (min-width: 600px) {
  .queue-item {
    grid-template-columns: 120px 1fr auto;
  }
}
```

Touch targets: all buttons must be at least 44×44px on mobile (add `min-height: 44px` to button styles).

---

## M-6: Downloads Folder Cleanup

### Problem
`downloads/` grows indefinitely. Disk space is never reclaimed.

### Design

**Environment variable:** `QUICKDL_KEEP_HOURS` (default: `24`). Files older than this many hours are deleted on startup.

**Implementation in `app.py`:**
```python
def _cleanup_downloads(directory: str, keep_hours: int = 24) -> None:
    import time
    if keep_hours == 0:
        return  # 0 = keep forever, skip cleanup
    p_dir = Path(directory)
    if not p_dir.exists():
        return  # directory not yet created — safe to skip
    cutoff = time.time() - keep_hours * 3600
    for p in p_dir.iterdir():
        if p.is_file() and p.stat().st_mtime < cutoff:
            try:
                p.unlink()
            except OSError:
                pass  # file in use or already deleted — skip silently
```

**Placement in `app.py` — inside `if __name__ == '__main__':`, AFTER `os.makedirs`:**
```python
if __name__ == '__main__':
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)   # already present
    _keep_hours = int(os.environ.get('QUICKDL_KEEP_HOURS', '24'))
    _cleanup_downloads(DOWNLOAD_DIR, _keep_hours)   # ← add here
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(debug=debug, threaded=True, host='0.0.0.0', port=5000)
```

**Why inside `if __name__ == '__main__':`:** placing cleanup at module top-level would run it during unit tests (`import app`) and Gunicorn worker forking, causing unintended test side-effects and slow startup. The `if __name__ == '__main__':` guard restricts it to direct execution only.

**Why after `os.makedirs`:** `_cleanup_downloads` calls `Path(directory).iterdir()`. If called before `os.makedirs`, `FileNotFoundError` would be raised when `downloads/` does not yet exist. The function's existence guard (`if not p_dir.exists(): return`) provides a secondary safety net.

**Constraints:**
- Only deletes files older than the cutoff — no risk to in-progress downloads (which are written to the directory but not yet 24h old).
- `OSError` is silently ignored — file-in-use on Windows is non-fatal.
- Called at startup only (not periodically) — simple and predictable.
- `QUICKDL_KEEP_HOURS=0` disables cleanup (keep forever).

---

## File Map

| File | Changes |
|------|---------|
| `static/css/styles.css` | Add `@media (prefers-color-scheme: light)` block with light-mode overrides for existing CSS variables; adjust responsive breakpoints |
| `templates/index.html` | Verify viewport meta tag; adjust container markup if needed |
| `app.py` | Add `_cleanup_downloads()`; call at startup; read `QUICKDL_KEEP_HOURS` |

---

## Verification

```bash
# M-2: Dark mode
# Open http://localhost:5000 in a browser with dark mode enabled (OS setting)
# All text, backgrounds, borders should be in dark palette
# No hardcoded white/black remaining in the page

# M-3: Mobile responsive
# Open http://localhost:5000, resize browser to 375px width (iPhone SE)
# Video card should stack vertically
# Buttons should be full-width or comfortably tappable
# No horizontal scroll

# M-6: Cleanup
# Note: QUICKDL_KEEP_HOURS=0 disables cleanup (keep forever) — do NOT use 0 to test deletion.
# Use keep_hours=1 and set mtime to epoch (far older than 1 hour).
python -c "
import os, time
from pathlib import Path
from app import _cleanup_downloads  # import the function directly — no side-effects

os.makedirs('downloads', exist_ok=True)

# Create a fake old file (mtime = Unix epoch, i.e., ~56 years old)
p = Path('downloads/test_old.mp4')
p.write_text('test')
os.utime(p, (0, 0))

_cleanup_downloads('downloads', keep_hours=1)
assert not p.exists(), 'Old file should have been deleted'
print('M-6 cleanup OK')
"

# Also verify keep_hours=0 skips cleanup (no deletion):
python -c "
import os
from pathlib import Path
from app import _cleanup_downloads

os.makedirs('downloads', exist_ok=True)
p = Path('downloads/test_forever.mp4')
p.write_text('test')
os.utime(p, (0, 0))

_cleanup_downloads('downloads', keep_hours=0)
assert p.exists(), 'File should NOT be deleted when keep_hours=0'
p.unlink()
print('M-6 keep_hours=0 (no-op) OK')
"
```
