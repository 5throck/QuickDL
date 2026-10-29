"""Tests for the post-download verification gates and batch manifest.

ffprobe/ffmpeg subprocesses and the oEmbed HTTP call are replaced with
injectable fakes (`run_cmd` / `fetch`) — no network, no external binaries.
"""
import json
import os
import re
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


# --- caption coverage gate (co-deck rounds 7–8) ---

from verification import (  # noqa: E402  (grouped with the feature under test)
    CAPTION_COVERAGE_THRESHOLD,
    annotate_caption_coverage,
    apply_swaps,
    caption_coverage,
    parse_vtt_last_cue_end,
)


def make_vtt(tmp_path, name='video.ko.vtt', last_end='00:00:50.000'):
    f = tmp_path / name
    f.write_text(
        'WEBVTT\n\n00:00:00.000 --> %s\nHello\n' % last_end, encoding='utf-8'
    )
    return str(f)


def test_parse_vtt_last_cue_end_takes_max_end(tmp_path):
    f = tmp_path / 'v.vtt'
    f.write_text(
        'WEBVTT\n\n'
        '00:00:00.000 --> 00:00:40.000\nA\n\n'
        '00:00:30.000 --> 00:00:35.000\nB\n\n'  # later start, earlier end
        '00:00:41.000 --> 00:00:50.500\nC\n',
        encoding='utf-8',
    )
    assert parse_vtt_last_cue_end(str(f)) == 50.5


def test_parse_vtt_last_cue_end_supports_mmss(tmp_path):
    f = tmp_path / 'v.vtt'
    f.write_text('WEBVTT\n\n02:05.500 --> 03:10.250\nHi\n', encoding='utf-8')
    assert parse_vtt_last_cue_end(str(f)) == 190.25


def test_parse_vtt_last_cue_end_missing_file(tmp_path):
    assert parse_vtt_last_cue_end(str(tmp_path / 'gone.vtt')) is None


def test_caption_coverage_ratio_and_clamp(tmp_path):
    vtt = make_vtt(tmp_path, last_end='00:00:50.000')
    assert caption_coverage(vtt, 100.0) == 0.5
    long_vtt = make_vtt(tmp_path, 'long.vtt', last_end='00:02:00.000')
    assert caption_coverage(long_vtt, 100.0) == 1.0  # clamped, never > 1


def test_caption_coverage_none_without_duration(tmp_path):
    vtt = make_vtt(tmp_path)
    assert caption_coverage(vtt, None) is None
    assert caption_coverage(vtt, 0) is None


def test_verify_annotates_coverage_and_warns_below_threshold(media_file, tmp_path):
    vtt = make_vtt(tmp_path)
    subs = [{'path': vtt, 'lang': 'ko', 'source': 'manual'}]
    result = verify_download(
        media_file, run_cmd=make_run_cmd(duration=100.0, height=1080, mean_volume=-20.0),
        fetch=make_fetch('My Video'), **FULL_GOOD, subtitles=subs,
    )
    assert subs[0]['coverage'] == 0.5
    assert result['status'] == 'ok'  # warn by default, not fail
    assert result['checks']['caption_coverage_ok'] is False
    assert any('below the 95% threshold' in w for w in result['warnings'])


def test_verify_full_coverage_no_warning(media_file, tmp_path):
    vtt = make_vtt(tmp_path, last_end='00:01:40.000')  # 100s of 100s
    subs = [{'path': vtt, 'lang': 'ko', 'source': 'manual'}]
    result = verify_download(
        media_file, run_cmd=make_run_cmd(duration=100.0, height=1080, mean_volume=-20.0),
        fetch=make_fetch('My Video'), **FULL_GOOD, subtitles=subs,
    )
    assert subs[0]['coverage'] == 1.0
    assert result['checks']['caption_coverage_ok'] is True
    assert result['warnings'] == []


def test_verify_require_caption_coverage_fails(media_file, tmp_path):
    vtt = make_vtt(tmp_path)  # 50% coverage
    subs = [{'path': vtt, 'lang': 'ko', 'source': 'manual'}]
    result = verify_download(
        media_file, run_cmd=make_run_cmd(duration=100.0, height=1080, mean_volume=-20.0),
        fetch=make_fetch('My Video'), **FULL_GOOD, subtitles=subs,
        require_caption_coverage=True,
    )
    assert result['status'] == 'failed'
    assert any('caption coverage gate' in r for r in result['reasons'])


def test_verify_require_coverage_failed_source_fails(media_file):
    subs = [{'path': None, 'lang': 'de', 'source': 'failed'}]
    result = verify_download(
        media_file, run_cmd=make_run_cmd(duration=100.0, height=1080, mean_volume=-20.0),
        fetch=make_fetch('My Video'), **FULL_GOOD, subtitles=subs,
        require_caption_coverage=True,
    )
    assert result['status'] == 'failed'
    assert any('no captions at all' in r for r in result['reasons'])


def test_verify_failed_source_warns_without_require(media_file):
    subs = [{'path': None, 'lang': 'de', 'source': 'failed'}]
    result = verify_download(
        media_file, run_cmd=make_run_cmd(duration=100.0, height=1080, mean_volume=-20.0),
        fetch=make_fetch('My Video'), **FULL_GOOD, subtitles=subs,
    )
    assert result['status'] == 'ok'
    assert result['checks']['caption_coverage_ok'] is False
    assert result['reasons'] == []


def test_verify_coverage_unevaluable_without_duration_warns_not_fails(media_file, tmp_path):
    # ffprobe unavailable AND no expected duration: coverage cannot be
    # measured — reported honestly as warnings, never a guessed failure.
    vtt = make_vtt(tmp_path)
    subs = [{'path': vtt, 'lang': 'ko', 'source': 'manual'}]
    result = verify_download(
        media_file, run_cmd=make_run_cmd(fail=True), fetch=make_fetch('My Video'),
        expected_height=1080, expected_title='My Video',
        video_id='abc12345678', reference_height=1080,
        subtitles=subs, require_caption_coverage=True,
    )
    assert subs[0]['coverage'] is None
    assert result['status'] == 'ok'
    assert any('could not be evaluated' in w for w in result['warnings'])


def test_verify_without_subtitles_leaves_coverage_check_none(media_file):
    result = verify_download(
        media_file, run_cmd=make_run_cmd(duration=100.0, height=1080, mean_volume=-20.0),
        fetch=make_fetch('My Video'), **FULL_GOOD,
    )
    assert result['checks']['caption_coverage_ok'] is None


def test_annotate_caption_coverage_non_verify_path(tmp_path):
    vtt = make_vtt(tmp_path)
    subs = [{'path': vtt, 'lang': 'ko', 'source': 'manual'},
            {'path': None, 'lang': 'de', 'source': 'failed'}]
    warnings = annotate_caption_coverage(subs, 100.0)
    assert subs[0]['coverage'] == 0.5
    assert 'coverage' not in subs[1]  # failed records have no sidecar
    assert len(warnings) == 1 and 'ko' in warnings[0]
    # custom threshold: 50% passes a 0.4 gate
    subs2 = [{'path': vtt, 'lang': 'ko', 'source': 'manual'}]
    assert annotate_caption_coverage(subs2, 100.0, threshold=0.4) == []
    assert CAPTION_COVERAGE_THRESHOLD == 0.95


# --- swap/retire provenance (co-deck rounds 7–8) ---

def test_apply_swaps_retires_old_and_tags_replacement():
    entries = [
        {'url': 'https://youtu.be/oldvideo111', 'id': 'oldvideo111', 'title': 'Old',
         'path': 'old.mp4', 'size_mb': 10.0, 'duration_min': 8.83, 'status': 'ok'},
        {'url': 'https://youtu.be/newvideo222', 'id': 'newvideo222', 'title': 'New'},
    ]
    entries, retired = apply_swaps(
        entries, [('oldvideo111', 'https://youtu.be/newvideo222')],
        reason='caption coverage 62%', today='2026-10-30',
    )
    assert [e['id'] for e in entries] == ['newvideo222']
    assert entries[0]['swapped_from'] == 'oldvideo111'
    assert entries[0]['swap'] == {'date': '2026-10-30', 'reason': 'caption coverage 62%'}
    assert len(retired) == 1
    r = retired[0]
    assert r['video_id'] == 'oldvideo111'
    assert r['title'] == 'Old'
    assert r['retired'] == '2026-10-30'
    assert r['reason'] == 'caption coverage 62%'
    assert r['path'] == 'old.mp4'


def test_apply_swaps_default_reason_and_date():
    entries = [{'url': 'u', 'id': 'old'}, {'url': 'https://x/new', 'id': 'new'}]
    entries, retired = apply_swaps(entries, [('old', 'https://x/new')])
    assert retired[0]['reason'] == 'replaced via --swap'
    assert re.fullmatch(r'\d{4}-\d{2}-\d{2}', retired[0]['retired'])  # today


def test_apply_swaps_unknown_old_id_ignored():
    entries = [{'url': 'u', 'id': 'a'}]
    entries, retired = apply_swaps(entries, [('nope', 'https://x/new')])
    assert entries == [{'url': 'u', 'id': 'a'}]
    assert retired == []


def test_build_manifest_includes_retired_when_given():
    manifest = build_manifest([{'status': 'ok', 'path': 'a.mp4'}],
                              retired=[{'video_id': 'old', 'retired': '2026-10-30'}])
    assert manifest['retired'] == [{'video_id': 'old', 'retired': '2026-10-30'}]


def test_build_manifest_omits_retired_key_when_none():
    manifest = build_manifest([{'status': 'ok', 'path': 'a.mp4'}])
    assert 'retired' not in manifest  # plain batches keep the exact schema
