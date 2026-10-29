"""Service-layer tests for the production-hardening download features.

All yt-dlp interaction is mocked via the `ydl_class` injection seam (the same
pattern download_service itself supports) — no network, no real downloads.
"""
import os

import pytest

import download_service as ds


class FakeYDL:
    """Minimal YoutubeDL stand-in that records the options it was built with."""

    captured = []  # class-level list, reset by the fixture

    def __init__(self, opts):
        self.opts = opts
        FakeYDL.captured.append(opts)

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def extract_info(self, url, download=False):
        return {'id': 'abc123', 'title': 'My Video', 'ext': 'mp4'}

    def prepare_filename(self, info):
        tmpl = os.path.basename(self.opts['outtmpl'])
        name = (
            tmpl.replace('%(title).100s', info['title'])
            .replace('%(id)s', info['id'])
            .replace('%(ext)s', info['ext'])
        )
        return os.path.join(os.path.dirname(self.opts['outtmpl']), name)


class FakeInfoYDL:
    """YoutubeDL stand-in for the probe path (skip_download=True)."""

    def __init__(self, opts):
        self.opts = opts

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def extract_info(self, url, download=False):
        return {
            'id': 'abc123',
            'title': 'T',
            'duration': 125,
            'duration_string': '2:05',
            'language': 'ko',
            'formats': [
                {'height': 720},
                {'height': 1080},
                {'height': None},
                {'language': 'ko', 'acodec': 'mp4a', 'audio_is_original': True},
                {'language': 'ja', 'acodec': 'mp4a', 'language_preference': -1},
            ],
            'subtitles': {'ko': ['x'], 'en': ['x']},
            'automatic_captions': {'ja': ['x'], 'en-ko': ['x'], 'ko': ['x']},
        }


@pytest.fixture(autouse=True)
def reset_captured():
    FakeYDL.captured = []
    yield


def _last_opts():
    return FakeYDL.captured[-1]


# --- legacy defaults must be byte-for-byte preserved ---

def test_default_opts_unchanged(tmp_path):
    ds.download_video('http://x', str(tmp_path), ydl_class=FakeYDL)
    opts = _last_opts()
    assert opts['format'] == ds.LEGACY_FORMAT
    assert opts['outtmpl'].endswith('%(title).100s.%(ext)s')
    assert opts['merge_output_format'] == 'mp4'
    assert 'format_sort' not in opts
    assert 'writesubtitles' not in opts


def test_default_returns_merged_mp4(tmp_path):
    target = tmp_path / 'My Video.mp4'
    target.write_bytes(b'x' * 16)
    path = ds.download_video('http://x', str(tmp_path), ydl_class=FakeYDL)
    assert path == str(target)


# --- quality modes ---

def test_quality_best_no_height_cap_with_codec_sort(tmp_path):
    ds.download_video('http://x', str(tmp_path), ydl_class=FakeYDL, quality='best')
    opts = _last_opts()
    assert opts['format'] == 'bestvideo+bestaudio/best'
    assert 'height<=' not in opts['format']
    assert opts['format_sort'] == ['res', 'fps', 'vcodec:avc1', 'acodec:mp4a', 'br']
    assert opts['merge_output_format'] == 'mp4'


def test_quality_cap_constrains_height(tmp_path):
    ds.download_video('http://x', str(tmp_path), ydl_class=FakeYDL, quality='cap:720')
    opts = _last_opts()
    assert opts['format'] == (
        'bestvideo[height<=720]+bestaudio[height<=720]/best[height<=720]/best'
    )
    assert opts['format_sort'] == ds.BEST_FORMAT_SORT


def test_format_for_quality_strings():
    assert ds.format_for_quality(None) == ds.LEGACY_FORMAT
    assert ds.format_for_quality('best') == 'bestvideo+bestaudio/best'
    assert 'height<=480' in ds.format_for_quality('cap:480')


@pytest.mark.parametrize('bad', ['max', 'BEST', 'cap:', 'cap:abc', 'cap:0', 'cap:-5'])
def test_invalid_quality_raises(tmp_path, bad):
    with pytest.raises(ValueError):
        ds.download_video('http://x', str(tmp_path), ydl_class=FakeYDL, quality=bad)
    with pytest.raises(ValueError):
        ds.parse_quality(bad)


def test_progress_hooks_always_passed(tmp_path):
    def hook(d):
        pass

    ds.download_video('http://x', str(tmp_path), ydl_class=FakeYDL, progress_hook=hook)
    assert hook in _last_opts()['progress_hooks']


# --- subtitles ---

def test_write_subs_default_langs(tmp_path):
    ds.download_video('http://x', str(tmp_path), ydl_class=FakeYDL, write_subs=True)
    opts = _last_opts()
    assert opts['writesubtitles'] is True
    assert opts['writeautomaticsub'] is True
    assert opts['subtitleslangs'] == ['ko.*', 'en.*']  # order = priority
    assert opts['subtitlesformat'].startswith('vtt')


def test_write_subs_custom_langs(tmp_path):
    ds.download_video(
        'http://x', str(tmp_path), ydl_class=FakeYDL,
        write_subs=True, sub_langs='en.*,fr.*',
    )
    assert _last_opts()['subtitleslangs'] == ['en.*', 'fr.*']


# --- ID-keyed naming ---

def test_id_keyed_names(tmp_path):
    ds.download_video('http://x', str(tmp_path), ydl_class=FakeYDL, id_keyed_names=True)
    assert _last_opts()['outtmpl'].endswith('%(id)s.%(ext)s')


def test_id_keyed_returns_id_named_file(tmp_path):
    target = tmp_path / 'abc123.mp4'
    target.write_bytes(b'x' * 16)
    path = ds.download_video('http://x', str(tmp_path), ydl_class=FakeYDL, id_keyed_names=True)
    assert path == str(target)


# --- probe enrichment ---

def test_get_video_info_returns_height_id_duration():
    info = ds.get_video_info('http://x', ydl_class=FakeInfoYDL)
    assert info['height'] == 1080  # max across formats
    assert info['id'] == 'abc123'
    assert info['duration_sec'] == 125
    assert info['duration'] == '2:05'
    assert info['title'] == 'T'


# --- audio-language probing and original selection (anti-dubbing) ---

def test_get_video_info_audio_and_caption_fields():
    info = ds.get_video_info('http://x', ydl_class=FakeInfoYDL)
    assert info['audio_languages'] == ['ko', 'ja']
    assert info['original_audio_lang'] == 'ko'  # audio_is_original flag wins
    assert info['manual_caption_langs'] == ['en', 'ko']
    assert sorted(info['auto_caption_langs']) == ['en-ko', 'ja', 'ko']


def test_probe_audio_languages_from_formats_and_tracks():
    info = {
        'audio_tracks': [{'language': 'en'}, {'language': 'de'}, {'language': 'en'}],
        'formats': [{'language': 'fr', 'acodec': 'mp4a'}, {'language': None}],
    }
    assert ds.probe_audio_languages(info) == ['en', 'de', 'fr']
    assert ds.probe_audio_languages({}) == []


def test_select_original_single_language():
    assert ds.select_original_audio_language({'formats': [{'language': 'en'}]}) == 'en'


def test_select_original_by_language_preference():
    info = {'formats': [
        {'language': 'ja', 'acodec': 'mp4a', 'language_preference': -1},
        {'language': 'en', 'acodec': 'mp4a', 'language_preference': 0},
    ]}
    assert ds.select_original_audio_language(info) == 'en'


def test_select_original_falls_back_to_video_language():
    info = {'language': 'ko', 'formats': [{'language': 'ko'}, {'language': 'ja'}]}
    assert ds.select_original_audio_language(info) == 'ko'


def test_select_original_none_when_undetectable():
    assert ds.select_original_audio_language({}) is None


def test_resolve_audio_language():
    info = {'original_audio_lang': 'ko'}
    assert ds.resolve_audio_language('auto', info) == 'ko'
    assert ds.resolve_audio_language(None, info) == 'ko'
    assert ds.resolve_audio_language('en', info) == 'en'
    assert ds.resolve_audio_language('auto', {}) is None


# --- audio-language format selection ---

def test_format_for_quality_audio_lang_injects_first_alternative_only():
    assert ds.format_for_quality(None, 'en') == ds.LEGACY_FORMAT.replace(
        'bestaudio', 'bestaudio[language^=en]', 1)
    assert ds.format_for_quality('best', 'ko') == \
        'bestvideo+bestaudio[language^=ko]/best'
    assert ds.format_for_quality('cap:720', 'en') == (
        'bestvideo[height<=720]+bestaudio[language^=en][height<=720]'
        '/best[height<=720]/best'
    )


def test_format_for_quality_audio_lang_none_unchanged():
    assert ds.format_for_quality(None, None) == ds.LEGACY_FORMAT
    assert ds.format_for_quality('best', None) == 'bestvideo+bestaudio/best'


def test_download_video_audio_lang_opts(tmp_path):
    ds.download_video('http://x', str(tmp_path), ydl_class=FakeYDL, audio_lang='en')
    opts = _last_opts()
    assert 'bestaudio[language^=en]' in opts['format']
    assert opts['postprocessor_args'] == ['-metadata:s:a:0', 'language=en']


def test_download_video_default_has_no_audio_opts(tmp_path):
    ds.download_video('http://x', str(tmp_path), ydl_class=FakeYDL)
    opts = _last_opts()
    assert 'language^=' not in opts['format']
    assert 'postprocessor_args' not in opts


# --- caption fallback-chain plan ---

def test_plan_manual_preferred():
    plan = ds.plan_caption_sources(['ko'], ['ko', 'en'], ['ko'])
    assert plan == [{'lang': 'ko', 'source': 'manual', 'request': 'ko'}]


def test_plan_auto_when_no_manual():
    plan = ds.plan_caption_sources(['ko'], ['en'], ['ko'])
    assert plan == [{'lang': 'ko', 'source': 'auto', 'request': 'ko'}]


def test_plan_translated_from_translation_pairs():
    plan = ds.plan_caption_sources(['ko'], [], ['en-ko', 'ja'])
    assert plan == [{'lang': 'ko', 'source': 'translated', 'request': 'en-ko'}]


def test_plan_failed_when_nothing_offered():
    plan = ds.plan_caption_sources(['de'], ['ko'], ['ko', 'en-ko'])
    assert plan == [{'lang': 'de', 'source': 'failed', 'request': None}]


def test_plan_unknown_when_probe_has_no_caption_data():
    plan = ds.plan_caption_sources(['ko', 'en'], None, None)
    assert plan == [
        {'lang': 'ko', 'source': 'unknown', 'request': 'ko'},
        {'lang': 'en', 'source': 'unknown', 'request': 'en'},
    ]


def test_plan_auto_unknown_availability_when_auto_list_missing():
    plan = ds.plan_caption_sources(['ko'], ['en'], None)
    assert plan == [{'lang': 'ko', 'source': 'auto', 'request': 'ko'}]


def test_plan_explicit_translation_request_passthrough():
    plan = ds.plan_caption_sources(['en-ko'], ['en'], ['en'])
    assert plan == [{'lang': 'en-ko', 'source': 'translated', 'request': 'en-ko'}]


def test_plan_each_requested_language_independently():
    plan = ds.plan_caption_sources(['ko', 'en'], ['ko'], ['ko'])
    assert [p['source'] for p in plan] == ['manual', 'failed']


# --- sidecar tagging ---

def test_subtitle_entry_uses_plan_source():
    plan = [{'lang': 'ko', 'source': 'manual', 'request': 'ko'}]
    entry = ds.subtitle_entry('/d/My Video.ko.vtt', '/d/My Video.mp4', plan)
    assert entry == {'path': '/d/My Video.ko.vtt', 'lang': 'ko', 'source': 'manual'}


def test_subtitle_entry_translated_plan_match():
    plan = [{'lang': 'ko', 'source': 'translated', 'request': 'en-ko'}]
    entry = ds.subtitle_entry('/d/V.en-ko.vtt', '/d/V.mp4', plan)
    assert entry['source'] == 'translated'
    assert entry['lang'] == 'en-ko'


def test_subtitle_entry_shape_classification_without_plan():
    assert ds.subtitle_entry('/d/V.ko-orig.vtt', '/d/V.mp4')['source'] == 'auto'
    assert ds.subtitle_entry('/d/V.en-ko.vtt', '/d/V.mp4')['source'] == 'translated'
    assert ds.subtitle_entry('/d/V.ko.vtt', '/d/V.mp4', [])['source'] == 'unknown'


def test_classify_sidecar_token():
    assert ds.classify_sidecar_token('ko-orig') == 'auto'
    assert ds.classify_sidecar_token('en-ko') == 'translated'
    assert ds.classify_sidecar_token('ko') == 'unknown'
    assert ds.classify_sidecar_token('pt-BR') == 'unknown'  # not a translation pair


# --- caption cleaning pipeline (co-deck rounds 7–8) ---

RAW_ROLLING_VTT = (
    'WEBVTT\n'
    'Kind: captions\n'
    'Language: ko\n'
    '\n'
    'NOTE this is a comment block\n'
    'spanning two lines\n'
    '\n'
    'cue-1\n'
    '00:00:00.000 --> 00:00:02.000\n'
    '<c>Hello</c><00:00:01.000><c> world</c></c>\n'
    '\n'
    '00:00:02.000 --> 00:00:04.000\n'
    'Hello world\n'  # rolling duplicate of cue 1's text
    '\n'
    '00:00:04.000 --> 00:00:06.000\n'
    'Second line\n'
)


def test_parse_vtt_cues_strips_tags_skips_blocks_and_ids():
    cues = ds.parse_vtt_cues(RAW_ROLLING_VTT)
    # cue-1 + rolling dup merge in later stages; parse keeps 3 raw cues
    assert len(cues) == 3
    assert cues[0]['text'] == 'Hello world'  # tags + inline timestamp stripped
    assert cues[0]['start'] == 0 and cues[0]['end'] == 2000
    assert cues[2]['text'] == 'Second line'


def test_parse_vtt_cues_drops_empty_and_supports_mmss():
    raw = (
        'WEBVTT\n\n'
        '00:01.000 --> 00:02.000\n'
        '<c></c>\n'  # markup-only → empty → dropped
        '\n'
        '01:02.500 --> 01:03.500\n'
        'Hi\n'
    )
    cues = ds.parse_vtt_cues(raw)
    assert len(cues) == 1
    assert cues[0]['start'] == 62500 and cues[0]['end'] == 63500
    assert cues[0]['text'] == 'Hi'


def test_dedup_rolling_cues_merges_duplicate_extending_end():
    cues = [
        {'start': 0, 'end': 2000, 'text': 'Hello world'},
        {'start': 2000, 'end': 4000, 'text': 'Hello world'},  # rolling dup
        {'start': 4000, 'end': 6000, 'text': 'Second line'},
    ]
    out = ds.dedup_rolling_cues(cues)
    assert len(out) == 2
    assert out[0]['end'] == 4000  # window merged, no time lost
    assert out[1]['text'] == 'Second line'


def test_clip_cue_overlaps_with_floor():
    cues = [
        {'start': 0, 'end': 5000, 'text': 'A'},
        {'start': 2000, 'end': 9000, 'text': 'B'},  # overlaps A
        {'start': 2050, 'end': 9000, 'text': 'C'},  # nearly zero gap → floor
    ]
    out = ds.clip_cue_overlaps([dict(c) for c in cues])
    assert out[0]['end'] == 2000              # clipped at next start
    assert out[1]['end'] == 2500              # 500 ms floor preserved
    assert out[2]['end'] == 9000              # last cue untouched


def test_clean_vtt_full_pipeline():
    cleaned = ds.clean_vtt(RAW_ROLLING_VTT)
    assert cleaned.startswith('WEBVTT\n\n')
    # rolling duplicate merged, overlap clipped, tags gone
    assert cleaned.count('Hello world') == 1
    assert '<c>' not in cleaned and 'NOTE' not in cleaned and 'cue-1' not in cleaned
    # merged rolling duplicate keeps the first window and the later end
    assert '00:00:00.000 --> 00:00:04.000\nHello world' in cleaned
    assert '00:00:04.000 --> 00:00:06.000\nSecond line' in cleaned


def test_clean_vtt_empty_returns_header_only():
    assert ds.clean_vtt('WEBVTT\n') == 'WEBVTT\n\n'


def test_clean_sidecar_overwrites_and_returns_count(tmp_path):
    f = tmp_path / 'video.ko.vtt'
    f.write_text(RAW_ROLLING_VTT, encoding='utf-8')
    count = ds.clean_sidecar(str(f))
    assert count == 2
    content = f.read_text(encoding='utf-8')
    assert content.startswith('WEBVTT\n\n')
    assert '<c>' not in content


def test_clean_sidecar_missing_file_returns_none(tmp_path):
    assert ds.clean_sidecar(str(tmp_path / 'gone.vtt')) is None
