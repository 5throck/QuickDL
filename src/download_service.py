import html
import os
import re
import threading
from typing import Optional, Callable
from i18n import t, format_duration

# Default subtitle language patterns — order is priority (spoken language first).
# When both writesubtitles and writeautomaticsub are enabled, yt-dlp prefers
# manual subtitles over auto-generated ones for a requested language.
DEFAULT_SUB_LANGS = "ko.*,en.*"

# Format sort fields for best-available mode. Resolution sorts first (never
# trade resolution for codec); at equal resolution/fps, h264 (avc1) video and
# AAC (mp4a) audio are preferred for browser and device compatibility.
# format_sort is a preference, not a hard filter.
BEST_FORMAT_SORT = ['res', 'fps', 'vcodec:avc1', 'acodec:mp4a', 'br']

# Legacy default format selector — used whenever `quality` is not requested,
# keeping the historical default behavior byte-for-byte unchanged.
LEGACY_FORMAT = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'


def parse_quality(quality: Optional[str]) -> Optional[int]:
    """Validate a quality mode string.

    Returns the height cap for 'cap:N', or None for None/'best'.
    Raises ValueError for anything else.
    """
    if quality is None or quality == 'best':
        return None
    if quality.startswith('cap:'):
        try:
            cap = int(quality[len('cap:'):])
        except ValueError:
            raise ValueError(
                "Invalid quality '%s': expected 'best' or 'cap:N' with integer N" % quality
            )
        if cap <= 0:
            raise ValueError("Invalid quality '%s': cap must be a positive integer" % quality)
        return cap
    raise ValueError("Invalid quality '%s': expected 'best' or 'cap:N'" % quality)


def format_for_quality(quality: Optional[str], audio_lang: Optional[str] = None) -> str:
    """Return the yt-dlp format selector string for a quality mode.

    When `audio_lang` is given, the FIRST alternative gets a language filter
    on its audio stream (`bestaudio[language^=<lang>]`) so YouTube auto-dubbed
    audio (e.g. an English video delivered with Japanese dub audio) is not
    picked silently.  The remaining alternatives are unchanged graceful
    fallbacks for videos that offer no track in the requested language.
    With `audio_lang=None` every returned string is byte-for-byte identical
    to the pre-audio-language behavior.
    """
    cap = parse_quality(quality) if quality is not None else None
    if quality is None:
        base = LEGACY_FORMAT
    elif cap is not None:
        base = (
            'bestvideo[height<=%d]+bestaudio[height<=%d]/best[height<=%d]/best'
            % (cap, cap, cap)
        )
    else:
        base = 'bestvideo+bestaudio/best'
    if not audio_lang:
        return base
    return base.replace('bestaudio', 'bestaudio[language^=%s]' % audio_lang, 1)


def probe_audio_languages(info_dict: dict) -> list:
    """Collect the distinct audio-track language codes of a probed video.

    Reads both the `audio_tracks` list and per-format `language` fields that
    yt-dlp exposes (YouTube auto-dubbing adds one format per dub language).
    Order of first appearance is preserved; empty list when undetectable.
    """
    langs: list = []
    seen = set()
    for track in (info_dict.get('audio_tracks') or []):
        lang = track.get('language') if isinstance(track, dict) else None
        if lang and lang not in seen:
            seen.add(lang)
            langs.append(lang)
    for f in (info_dict.get('formats') or []):
        lang = f.get('language')
        if lang and lang not in seen and f.get('acodec') != 'none':
            seen.add(lang)
            langs.append(lang)
    return langs


def select_original_audio_language(info_dict: dict, audio_languages: Optional[list] = None) -> Optional[str]:
    """Pick the video's ORIGINAL spoken-language audio code (anti-dubbing).

    Priority: a track explicitly flagged `audio_is_original`, then the track
    with the highest `language_preference` (yt-dlp marks original above dubs),
    then the video-level `language`, then a single available track.  Returns
    None when the original language cannot be determined.
    """
    langs = audio_languages if audio_languages is not None else probe_audio_languages(info_dict)
    if not langs:
        return info_dict.get('language') or None
    if len(langs) == 1:
        return langs[0]
    for f in (info_dict.get('formats') or []):
        if f.get('audio_is_original') and f.get('language') in langs:
            return f['language']
    best, best_pref = None, None
    for f in (info_dict.get('formats') or []):
        pref = f.get('language_preference')
        if f.get('language') in langs and pref is not None and (best is None or pref > best_pref):
            best, best_pref = f['language'], pref
    if best:
        return best
    return info_dict.get('language') or langs[0]


def resolve_audio_language(mode: Optional[str], info: dict) -> Optional[str]:
    """Resolve a CLI `--audio-lang` value into a concrete language code.

    'auto' (or None) picks the probed original spoken language; any other
    value is used verbatim as the requested code.
    """
    if not mode or mode == 'auto':
        return info.get('original_audio_lang')
    return mode


# Caption acquisition sources recorded in the manifest.  'unknown' means the
# probe did not expose caption availability (non-YouTube extractors) and the
# request was passed through unchanged; 'failed' means no source offered the
# requested language at all (nothing was fetched for it).
CAPTION_SOURCES = ('manual', 'auto', 'translated', 'failed', 'unknown')


def plan_caption_sources(
    requested_langs: list,
    manual_langs: Optional[list],
    auto_langs: Optional[list],
) -> list:
    """Resolve the best caption acquisition source per requested language.

    Honest fallback chain per language: native manual → native auto-generated
    → YouTube auto-TRANSLATED captions (translation keys like 'en-ko' listed
    under `automatic_captions`) → 'failed' (nothing offered).  When the probe
    did not expose caption data at all (both lists None) the request is passed
    through with source 'unknown' — legacy behavior.  Each plan item:
    `{'lang': requested, 'source': <CAPTION_SOURCES member>, 'request': <yt-dlp
    language pattern or None>}`.
    """
    plan = []
    for lang in requested_langs:
        if manual_langs is None and auto_langs is None:
            plan.append({'lang': lang, 'source': 'unknown', 'request': lang})
            continue
        if '-' in lang:
            # Explicit translation-shaped request (e.g. 'en-ko' given in
            # --sub-langs): pass through, tagged as a translated source.
            plan.append({'lang': lang, 'source': 'translated', 'request': lang})
            continue
        if lang in (manual_langs or []):
            plan.append({'lang': lang, 'source': 'manual', 'request': lang})
            continue
        if lang in (auto_langs or []):
            plan.append({'lang': lang, 'source': 'auto', 'request': lang})
            continue
        if auto_langs is None:
            # auto availability unknown — let yt-dlp try the native request
            plan.append({'lang': lang, 'source': 'auto', 'request': lang})
            continue
        translations = sorted(t for t in auto_langs if t.endswith('-' + lang))
        if translations:
            plan.append({'lang': lang, 'source': 'translated', 'request': translations[0]})
            continue
        plan.append({'lang': lang, 'source': 'failed', 'request': None})
    return plan


def classify_sidecar_token(token: str) -> str:
    """Best-effort caption source classification from a sidecar's language token.

    yt-dlp names sidecars `<base>.<token>.vtt` where the token is a language
    code, an auto-original marker ('ko-orig'), or a translation pair
    ('en-ko').  Used only when no caption plan matched the token.
    """
    if token.endswith('-orig'):
        return 'auto'
    parts = token.split('-')
    if len(parts) == 2 and re.fullmatch(r'[a-z]{2,3}', parts[0]) \
            and re.fullmatch(r'[a-z]{2,3}', parts[1]):
        return 'translated'
    return 'unknown'


def subtitle_entry(vtt_path: str, saved_path: str, plan: Optional[list] = None) -> dict:
    """Build one manifest `subtitles[]` record for a downloaded sidecar.

    Source resolution: the plan entry whose request exactly matches the file's
    language token wins (the plan was computed from a fresh probe moments
    before the download); otherwise the token shape classifies it; otherwise
    'unknown'.  Note yt-dlp filenames cannot distinguish a fetched manual from
    an auto track for the same requested code — the plan-time source is
    recorded, which is the honest best available at request time.
    """
    base_name = os.path.basename(os.path.splitext(saved_path)[0])
    token = os.path.basename(vtt_path)[len(base_name) + 1:-4]
    source = None
    for item in (plan or []):
        if item.get('request') and token == item['request']:
            source = item['source']
            break
    if source is None:
        source = classify_sidecar_token(token)
    return {'path': vtt_path, 'lang': token, 'source': source}


# --- caption cleaning pipeline -------------------------------------------
# Raw YouTube VTT sidecars carry inline timestamp/<c> tags, rolling caption
# windows (each cue repeats the previous cue's lines plus one new line) and
# overlapping cue intervals. Proven in the co-deck production rounds: the
# tag-strip + rolling-dedup + overlap-clip pipeline turns raw grabs into
# clean cue files (e.g. a raw 424-cue ASR track) without changing content.

VTT_CUE_LINE_RE = re.compile(
    r'^(?:(\d+):)?(\d{1,2}):(\d{2})[.,](\d{3})\s*-->\s*'
    r'(?:(\d+):)?(\d{1,2}):(\d{2})[.,](\d{3})'
)
OVERLAP_FLOOR_MS = 500  # minimum display window after clipping an overlap


def _vtt_ts_ms(groups) -> int:
    """Convert one VTT timestamp regex match group tuple to milliseconds."""
    h, m, s, ms = groups
    return (int(h) if h else 0) * 3600000 + int(m) * 60000 + int(s) * 1000 + int(ms)


def _strip_vtt_markup(text: str) -> str:
    """Entity-decode and remove inline markup (`<c>`, `<00:00:01.000>`, ...)."""
    text = html.unescape(text)
    return re.sub(r'<[^>]+>', '', text).strip()


def parse_vtt_cues(raw: str) -> list:
    """Parse a WebVTT string into cues `{'start', 'end', 'text'}` (ms/text).

    Tag-strips cue text, drops empty cues, and skips NOTE/STYLE/REGION
    blocks and cue identifier lines (a standalone line directly followed by
    a timing line).
    """
    lines = raw.splitlines()
    cues = []
    cur = None
    i = 0
    n = len(lines)
    while i < n:
        stripped = lines[i].strip()
        m = VTT_CUE_LINE_RE.match(stripped)
        if m:
            start = _vtt_ts_ms(m.groups()[:4])
            end = _vtt_ts_ms(m.groups()[4:])
            cur = {'start': start, 'end': max(end, start), 'text': ''}
            cues.append(cur)
            i += 1
            continue
        if not stripped:
            i += 1
            continue
        if stripped.startswith(('NOTE', 'STYLE', 'REGION')):
            # header/metadata block — runs until the next blank line
            i += 1
            while i < n and lines[i].strip():
                i += 1
            cur = None
            continue
        # A non-empty non-timing line is cue text — unless it is a cue
        # identifier, i.e. it is directly followed by a timing line.
        if cur is None or (i + 1 < n and VTT_CUE_LINE_RE.match(lines[i + 1].strip())):
            i += 1
            continue
        text = _strip_vtt_markup(stripped)
        if text and text != cur['text']:
            cur['text'] = (cur['text'] + '\n' + text).strip()
        i += 1
    return [c for c in cues if c['text']]


def dedup_rolling_cues(cues: list) -> list:
    """Drop consecutive duplicate cue texts (YouTube rolling-window ASR).

    When a cue repeats the previous cue's text the window is merged by
    extending the previous cue's end, so no caption time is lost.
    """
    out = []
    for c in cues:
        if out and c['text'] == out[-1]['text']:
            out[-1]['end'] = max(out[-1]['end'], c['end'])
            continue
        out.append(dict(c))
    return out


def clip_cue_overlaps(cues: list, floor_ms: int = OVERLAP_FLOOR_MS) -> list:
    """Clip each cue's end at the next cue's start (with a minimum window).

    ASR word-timed tracks produce rolling overlapping windows; without
    clipping, players stack two cues on screen at once.
    """
    for i, c in enumerate(cues):
        if i + 1 < len(cues):
            nxt = cues[i + 1]['start']
            if nxt > c['start']:
                c['end'] = min(c['end'], max(nxt, c['start'] + floor_ms))
    return cues


def format_vtt(cues: list) -> str:
    """Render cleaned cues as a WebVTT string."""
    blocks = []
    for c in cues:
        blocks.append('%s --> %s\n%s' % (
            _ms_to_vtt_ts(c['start']), _ms_to_vtt_ts(c['end']), c['text'],
        ))
    return 'WEBVTT\n\n' + '\n\n'.join(blocks) + ('\n' if blocks else '')


def _ms_to_vtt_ts(ms: int) -> str:
    h, rem = divmod(int(ms), 3600000)
    m, rem = divmod(rem, 60000)
    s, milli = divmod(rem, 1000)
    return '%02d:%02d:%02d.%03d' % (h, m, s, milli)


def clean_vtt(raw: str) -> str:
    """Full cleaning pipeline: parse → tag-strip → rolling dedup → overlap clip."""
    cues = parse_vtt_cues(raw)
    cues = dedup_rolling_cues(cues)
    cues = clip_cue_overlaps(cues)
    return format_vtt(cues)


def clean_sidecar(vtt_path: str) -> Optional[int]:
    """Clean a downloaded sidecar VTT in place; return the final cue count.

    The raw file is overwritten with the cleaned pipeline output (the raw
    grab is transient — the manifest records `cleaned: true` + cue count).
    Returns None when the file cannot be read (left untouched; the manifest
    entry simply gets no cleaned/cues fields — nothing is guessed).
    """
    try:
        with open(vtt_path, encoding='utf-8') as f:
            raw = f.read()
    except OSError:
        return None
    cleaned = clean_vtt(raw)
    with open(vtt_path, 'w', encoding='utf-8') as f:
        f.write(cleaned)
    return len(parse_vtt_cues(cleaned))


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
        formats = info_dict.get('formats') or []
        heights = [f.get('height') for f in formats if f.get('height')]
        max_height = max(heights) if heights else info_dict.get('height')
        audio_langs = probe_audio_languages(info_dict)
        manual_subs = info_dict.get('subtitles')
        auto_subs = info_dict.get('automatic_captions')
        return {
            'id': info_dict.get('id'),
            'title': info_dict.get('title'),
            'thumbnail': info_dict.get('thumbnail'),
            'duration': duration,
            'duration_sec': raw_dur,
            'channel': info_dict.get('uploader'),
            'height': max_height,
            # Audio-language fields (anti auto-dubbing)
            'audio_languages': audio_langs,
            'original_audio_lang': select_original_audio_language(info_dict, audio_langs),
            # Caption availability (None = probe did not expose the data)
            'manual_caption_langs': sorted(manual_subs.keys()) if isinstance(manual_subs, dict) else None,
            'auto_caption_langs': sorted(auto_subs.keys()) if isinstance(auto_subs, dict) else None,
        }


def _build_ydl_opts(
    output_dir: str,
    quality: Optional[str],
    id_keyed_names: bool,
    write_subs: bool,
    sub_langs: Optional[str],
    audio_lang: Optional[str] = None,
) -> dict:
    ydl_opts = {
        'format': format_for_quality(quality, audio_lang),
        'outtmpl': os.path.join(output_dir, '%(title).100s.%(ext)s'),
        'merge_output_format': 'mp4',
        'windowsfilenames': True,
        'nocheckcertificate': True,
    }
    if id_keyed_names:
        # ID-keyed naming: unambiguous file identity for scripted batches
        # (fixes the "newest mp4 in the folder" identity weakness).
        ydl_opts['outtmpl'] = os.path.join(output_dir, '%(id)s.%(ext)s')
    if quality is not None:
        ydl_opts['format_sort'] = list(BEST_FORMAT_SORT)
    if audio_lang:
        # Best-effort: stamp the requested language onto the first audio
        # stream during the ffmpeg merge/remux so the mp4 keeps a language
        # tag even when the selected stream lost it.  A plain list applies
        # to all ffmpeg postprocessor invocations (yt-dlp backward-compat).
        ydl_opts['postprocessor_args'] = [
            '-metadata:s:a:0', 'language=%s' % audio_lang,
        ]
    if write_subs:
        patterns = [s.strip() for s in (sub_langs or DEFAULT_SUB_LANGS).split(',') if s.strip()]
        ydl_opts.update({
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': patterns,
            'subtitlesformat': 'vtt/best',
        })
    return ydl_opts


def download_video(
    url: str,
    output_dir: str,
    ydl_class=None,
    progress_hook: Optional[Callable] = None,
    cancel_event: Optional[threading.Event] = None,
    quality: Optional[str] = None,
    write_subs: bool = False,
    sub_langs: Optional[str] = None,
    id_keyed_names: bool = False,
    audio_lang: Optional[str] = None,
) -> str:
    """Download a video and return the merged .mp4 path.

    All new parameters are opt-in: calling with only (url, output_dir) keeps
    the exact legacy behavior (legacy format selector, title-based filename,
    no subtitles).

    `audio_lang` forces the original-language audio track: the format
    selector gains `bestaudio[language^=<lang>]` on its first alternative
    (with graceful fallback to any audio) and the merged file gets the
    language stamped via `-metadata:s:a:0 language=<lang>`.
    """
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

    ydl_opts = _build_ydl_opts(
        output_dir, quality, id_keyed_names, write_subs, sub_langs, audio_lang,
    )
    ydl_opts['progress_hooks'] = hooks

    with ydl_class(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        base, _ = os.path.splitext(filename)
        # prepare_filename() returns the pre-merge stream filename; the actual
        # merged output may have a different name on disk.  Prefer a real .mp4
        # file that matches the base path, then fall back to the expected name.
        import glob as _glob
        candidates = _glob.glob(base + '.*')
        mp4_files = [f for f in candidates if f.lower().endswith('.mp4')]
        return mp4_files[0] if mp4_files else base + '.mp4'
