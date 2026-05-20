# QuickDL — Group D: i18n Utils Design Spec

**Date:** 2026-05-20
**Scope:** U-6 — `format_duration()` helper in `i18n.py`

---

## Overview

Add a `format_duration(seconds: int) -> str` function to `i18n.py` that produces locale-appropriate duration strings for the currently active language. This replaces the current fallback of `str(seconds) + t("seconds_suffix")` in `download_service.py`.

---

## Problem

The current fallback produces `"225s"` (English) or `"225초"` (Korean) — seconds-only, no minutes/hours. The primary `duration_string` from yt-dlp is already formatted (`"3:45"`), so the fallback only triggers when `duration_string` is absent. The fallback should still be human-readable and language-appropriate.

---

## Design

### `format_duration()` in `i18n.py`

**Precondition:** `seconds >= 0`. The caller must validate before calling (negative values from corrupt metadata should be treated as `None` and skip `format_duration`).

**Thread safety:** `format_duration` reads the module-level `_lang` variable, which is set once at startup by `i18n.init()`. Per-request language switching (calling `init()` mid-request) is not supported and would create a race condition. The single-startup-init contract is enforced by `app.py` (calls `i18n.init()` once before the Flask server starts).

```python
def format_duration(seconds: int) -> str:
    """Return a locale-appropriate duration string for the current language."""
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    lang = _lang  # current active language (set once at startup via init())

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
    # All languages not explicitly listed above (en, de, es, fr, pt, vi, ms, id, etc.)
    # fall through here intentionally — this is the correct behaviour, not a missing branch.
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"
```

### Usage in `download_service.py`

```python
# Before (after previous fix):
from i18n import t
duration = str(info_dict.get('duration')) + t("seconds_suffix")

# After:
from i18n import format_duration
raw = info_dict.get('duration')
duration = format_duration(int(raw)) if raw else None
```

The `seconds_suffix` key in locale files becomes unused after this change and should be removed. However, since `seconds_suffix` was added in the previous maintenance cycle, its removal is deferred to avoid churn. This is tracked as a separate low-priority task: **TODO(cleanup): remove `seconds_suffix` from all 12 locale files after U-6 ships.** Create a `TaskCreate` entry when starting the Group D implementation.

---

## Supported Languages

| Language | Format (e.g., 3h 45m 30s) |
|----------|--------------------------|
| en, de, es, fr, pt, vi, ms, id | `3:45:30` / `45:30` |
| ko | `3시간 45분 30초` / `45분 30초` / `30초` |
| ja | `3時間45分30秒` / `45分30秒` / `30秒` |
| zh-TW | `3時45分30秒` / `45分30秒` / `30秒` |
| zh-CN | `3时45分30秒` / `45分30秒` / `30秒` |

---

## File Map

| File | Changes |
|------|---------|
| `i18n.py` | Add `format_duration()` function; add to module `__all__` if applicable |
| `download_service.py` | Replace `t("seconds_suffix")` fallback with `format_duration()` |

---

## Verification

```python
# test_i18n.py — add these test cases

def test_format_duration_english():
    i18n.init('en')
    assert i18n.format_duration(225) == '3:45'
    assert i18n.format_duration(3665) == '1:01:05'
    assert i18n.format_duration(45) == '0:45'

def test_format_duration_korean():
    i18n.init('ko')
    assert i18n.format_duration(225) == '3분 45초'
    assert i18n.format_duration(3665) == '1시간 1분 5초'
    assert i18n.format_duration(45) == '45초'

def test_format_duration_japanese():
    i18n.init('ja')
    assert i18n.format_duration(225) == '3分45秒'

def test_format_duration_zero():
    i18n.init('en')
    assert i18n.format_duration(0) == '0:00'
```
