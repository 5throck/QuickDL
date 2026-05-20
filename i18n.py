"""QuickDL i18n module — language detection and translation lookup."""
import json
import locale
import os
from pathlib import Path
from typing import Optional

SUPPORTED = {"ko", "en", "ja", "zh-TW", "zh-CN", "de", "es", "fr", "pt", "vi", "ms", "id", "th", "ru"}
DEFAULT_LANG = "en"
_LOCALES_DIR = Path(__file__).parent / "locales"
_translations: dict = {}
_lang: str = DEFAULT_LANG


def _detect_lang() -> str:
    # Priority 1: explicit env override
    override = os.environ.get("QUICKDL_LANG", "").strip()
    if override in SUPPORTED:
        return override

    # Priority 2: OS locale
    try:
        loc, _ = locale.getdefaultlocale()  # e.g. "ko_KR", "zh_TW"
        if loc:
            lang = loc.replace("_", "-")  # "zh_TW" → "zh-TW"
            if lang in SUPPORTED:
                return lang
            short = lang.split("-")[0]  # "ko-KR" → "ko"
            if short in SUPPORTED:
                return short
    except Exception:
        pass

    return DEFAULT_LANG


def init(lang: Optional[str] = None) -> None:
    """Initialise translations. Call once at app startup."""
    global _lang, _translations
    _lang = lang if (lang and lang in SUPPORTED) else _detect_lang()
    path = _LOCALES_DIR / f"{_lang}.json"
    if not path.exists():
        _lang = DEFAULT_LANG
        path = _LOCALES_DIR / f"{DEFAULT_LANG}.json"
    with open(path, encoding="utf-8") as f:
        _translations = json.load(f)


def t(key: str, **kwargs) -> str:
    """Return translated string for key, with optional format substitution."""
    text = _translations.get(key, key)
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, IndexError):
            pass
    return text


def get_lang() -> str:
    """Return current active language code."""
    return _lang


def get_all() -> dict:
    """Return all translations dict (for Flask template injection)."""
    return dict(_translations)
