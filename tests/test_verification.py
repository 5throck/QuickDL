"""Tests for the post-download verification gates and batch manifest.

ffprobe/ffmpeg subprocesses and the oEmbed HTTP call are replaced with
injectable fakes (`run_cmd` / `fetch`) — no network, no external binaries.
"""
import json
import os
from types import SimpleNamespace

import pytest

from verification import (
    SOURCE_CAP_WARNING_PREFIX,
    build_manifest,
    extract_video_id,
    titles_match,
    verify_download,
)


def make_run_cmd(duration=None, height=None, mean_volume=None, fail=False):
    """Build a run_cmd fake answering ffprobe/ffmpeg calls with fixed data."""
    def run_cmd(argv, timeout=None):
        if fail:
            raise OSError('binary not found')
        if argv[0] == 'ffprobe':
            if 'format=duration' in argv:
                stdout = '' if duration is None else '%.3f\n' % duration
            else:
                stdout = '' if height is None else '%d\n' % height
            return SimpleNamespace(returncode=0, stdout=stdout, stderr='')
        if argv[0] == 'ffmpeg':
            stderr = '' if mean_volume is None else \
                '[volumedetect] mean_volume: %.1f dB\n' % mean_volume
            return SimpleNamespace(returncode=0, stdout='', stderr=stderr)
        raise AssertionError('unexpected binary: %s' % argv[0])
    return run_cmd


def make_fetch(title=None):
    """Build a fetch fake returning an oEmbed payload (or simulating no network)."""
    def fetch(url, timeout=None):
        if title is None:
            raise OSError('network unavailable')
        assert url.startswith('https://www.youtube.com/oembed?')
        return json.dumps({'title': title})
    return fetch


@pytest.fixture()
def media_file(tmp_path):
    f = tmp_path / 'video.mp4'
    f.write_bytes(b'x' * (2 * 1024 * 1024))  # 2 MB — above the 1 MB gate
    return str(f)


FULL_GOOD = dict(
    expected_duration_sec=100.0,
    expected_height=1080,
    expected_title='My Video',
    video_id='abc12345678',
    reference_height=1080,
)


# --- hard gates ---

def test_missing_file_fails(tmp_path):
    result = verify_download(str(tmp_path / 'gone.mp4'))
    assert result['status'] == 'failed'
    assert not result['checks']['exists']


def test_tiny_file_fails(tmp_path):
    f = tmp_path / 'tiny.mp4'
    f.write_bytes(b'x' * 100)
    result = verify_download(str(f))
    assert result['status'] == 'failed'
    assert 'too small' in result['reasons'][0]


def test_duration_out_of_tolerance_fails(media_file):
    result = verify_download(
        media_file, run_cmd=make_run_cmd(duration=120.0, height=1080, mean_volume=-20.0),
        fetch=make_fetch('My Video'), **FULL_GOOD,
    )
    assert result['checks']['duration_ok'] is False
    assert result['status'] == 'failed'
    assert any('duration mismatch' in r for r in result['reasons'])


def test_duration_within_tolerance_passes(media_file):
    result = verify_download(
        media_file, run_cmd=make_run_cmd(duration=103.0, height=1080, mean_volume=-20.0),
        fetch=make_fetch('My Video'),
        expected_duration_sec=100.0, expected_height=1080,
        expected_title='My Video', video_id='abc12345678', reference_height=1080,
    )
    assert result['checks']['duration_ok'] is True
    assert result['status'] == 'ok'


def test_silent_audio_fails(media_file):
    result = verify_download(
        media_file, run_cmd=make_run_cmd(duration=100.0, height=1080, mean_volume=-70.0),
        fetch=make_fetch('My Video'), **FULL_GOOD,
    )
    assert result['checks']['audio_ok'] is False
    assert result['status'] == 'failed'
    assert any('silent' in r for r in result['reasons'])


def test_title_mismatch_fails(media_file):
    result = verify_download(
        media_file, run_cmd=make_run_cmd(duration=100.0, height=1080, mean_volume=-20.0),
        fetch=make_fetch('A Completely Different Video'), **FULL_GOOD,
    )
    assert result['checks']['title_ok'] is False
    assert result['status'] == 'failed'
    assert any('title identity mismatch' in r for r in result['reasons'])


# --- soft findings (warnings, not failures) ---

def test_all_gates_pass(media_file):
    result = verify_download(
        media_file, run_cmd=make_run_cmd(duration=100.0, height=1080, mean_volume=-20.0),
        fetch=make_fetch('my   VIDEO '), **FULL_GOOD,
    )
    assert result['status'] == 'ok'
    assert result['size_mb'] == 2.0
    assert result['measured']['height'] == 1080
    assert result['measured']['mean_volume_db'] == -20.0
    assert result['warnings'] == []


def test_title_check_skipped_without_network(media_file):
    result = verify_download(
        media_file, run_cmd=make_run_cmd(duration=100.0, height=1080, mean_volume=-20.0),
        fetch=make_fetch(None), **FULL_GOOD,
    )
    assert result['status'] == 'ok'
    assert result['checks']['title_ok'] is None
    assert any('oEmbed' in w for w in result['warnings'])


def test_missing_ffmpeg_yields_warnings_not_failure(media_file):
    result = verify_download(
        media_file, run_cmd=make_run_cmd(fail=True),
        fetch=make_fetch('My Video'), **FULL_GOOD,
    )
    assert result['status'] == 'ok'
    assert len(result['warnings']) >= 2  # duration + loudness unmeasurable


def test_resolution_below_probed_max_warns(media_file):
    result = verify_download(
        media_file, run_cmd=make_run_cmd(duration=100.0, height=720, mean_volume=-20.0),
        fetch=make_fetch('My Video'), **FULL_GOOD,
    )
    assert result['status'] == 'ok'
    assert result['checks']['resolution_ok'] is False
    assert any('below the probed maximum' in w for w in result['warnings'])


# --- already-max semantics ---

def test_source_ceiling_below_reference_is_already_max(media_file):
    result = verify_download(
        media_file, run_cmd=make_run_cmd(duration=100.0, height=720, mean_volume=-20.0),
        fetch=make_fetch('My Video'),
        expected_duration_sec=100.0, expected_height=720,
        expected_title='My Video', video_id='abc12345678', reference_height=1080,
    )
    assert result['status'] == 'already-max'
    assert result['warnings'][0].startswith(SOURCE_CAP_WARNING_PREFIX)


def test_source_ceiling_at_cap_reference_is_ok(media_file):
    result = verify_download(
        media_file, run_cmd=make_run_cmd(duration=100.0, height=720, mean_volume=-20.0),
        fetch=make_fetch('My Video'),
        expected_duration_sec=100.0, expected_height=720,
        expected_title='My Video', video_id='abc12345678', reference_height=720,
    )
    assert result['status'] == 'ok'


# --- helpers ---

@pytest.mark.parametrize('url,expected', [
    ('https://www.youtube.com/watch?v=dQw4w9WgXcQ', 'dQw4w9WgXcQ'),
    ('https://youtu.be/dQw4w9WgXcQ', 'dQw4w9WgXcQ'),
    ('https://www.youtube.com/shorts/dQw4w9WgXcQ', 'dQw4w9WgXcQ'),
    ('https://www.youtube.com/embed/dQw4w9WgXcQ', 'dQw4w9WgXcQ'),
    ('https://example.com/video/123', None),
])
def test_extract_video_id(url, expected):
    assert extract_video_id(url) == expected


def test_titles_match_normalization():
    assert titles_match('My  VIDEO ', 'my video')
    assert not titles_match('My Video', 'Other Video')


# --- manifest ---

def test_build_manifest_totals():
    entries = [
        {'status': 'ok', 'path': 'a.mp4'},
        {'status': 'ok', 'path': 'b.mp4'},
        {'status': 'already-max', 'path': 'c.mp4'},
        {'status': 'failed', 'path': 'd.mp4'},
    ]
    manifest = build_manifest(entries, tool={'name': 'yt-dlp', 'version': '1'})
    assert manifest['totals'] == {
        'videos': 4, 'ok': 2, 'already_max': 1, 'failed': 1, 'other': 0,
    }
    assert manifest['tool'] == {'name': 'yt-dlp', 'version': '1'}
    assert manifest['generated_at'].endswith('Z')
    assert manifest['videos'] is entries


def test_build_manifest_empty():
    manifest = build_manifest([])
    assert manifest['totals']['videos'] == 0


# --- audio-language and caption fields pass through untouched ---

def test_build_manifest_audio_and_caption_fields():
    entries = [{
        'status': 'ok',
        'path': 'a.mp4',
        'audio_language': 'ko',
        'audio_languages_available': ['ko', 'ja'],
        'subtitles': [
            {'path': 'a.ko.vtt', 'lang': 'ko', 'source': 'manual'},
            {'path': 'a.en-ko.vtt', 'lang': 'en-ko', 'source': 'translated'},
            {'path': None, 'lang': 'de', 'source': 'failed'},
        ],
    }]
    manifest = build_manifest(entries)
    video = manifest['videos'][0]
    assert video['audio_language'] == 'ko'
    assert video['audio_languages_available'] == ['ko', 'ja']
    assert [s['source'] for s in video['subtitles']] == ['manual', 'translated', 'failed']
    assert manifest['totals']['ok'] == 1


def test_build_manifest_entry_without_audio_fields():
    # Legacy-shaped entries (no audio_language / subtitles objects) still tally.
    manifest = build_manifest([{'status': 'ok', 'path': 'a.mp4'}])
    assert manifest['totals']['ok'] == 1
    assert manifest['videos'][0]['path'] == 'a.mp4'
