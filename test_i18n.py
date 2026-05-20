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
