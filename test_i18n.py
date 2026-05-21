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


def test_init_default_lang():
    i18n.init()
    assert i18n.get_lang() in i18n.SUPPORTED


def test_init_explicit_lang():
    i18n.init('ko')
    assert i18n.get_lang() == 'ko'


def test_init_unsupported_lang_falls_back_to_en():
    i18n.init('xx')
    assert i18n.get_lang() in i18n.SUPPORTED


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
    assert i18n.get_lang() in i18n.SUPPORTED


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
