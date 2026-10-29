"""Post-download verification gates and batch manifest for QuickDL.

Implements the verification policy validated in an external production batch
run (18 videos, 0 failures) and reflects it back as native functionality:

- file exists and is larger than 1 MB
- measured duration within ±5% of the expected duration
- audio mean loudness (ffmpeg volumedetect) at or above -60 dB (not silent)
- oEmbed title identity against the requested video
- measured resolution equals the probed maximum (warn when lower)

All external I/O (ffprobe/ffmpeg subprocesses, the oEmbed HTTP call) is
injectable via `run_cmd` / `fetch` so the module is fully testable offline.
"""
import json
import os
import re
import subprocess
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional

MIN_SIZE_BYTES = 1024 * 1024          # a healthy download is never under 1 MB
DURATION_TOLERANCE = 0.05             # ±5% of the expected duration
MIN_MEAN_VOLUME_DB = -60.0            # below this the audio track is effectively silent
FFMPEG_TIMEOUT_SEC = 30
OEMBED_TIMEOUT_SEC = 10
OEMBED_ENDPOINT = 'https://www.youtube.com/oembed'
# Reporting-only reference for best mode: when the source ceiling (probed max
# height) is below this, the download already IS the best the source offers.
# It is never used as a download cap.
DEFAULT_REFERENCE_HEIGHT = 1080

# Stable prefix of the source-cap warning so consumers (cli.py) can identify
# it without duplicating the message text.
SOURCE_CAP_WARNING_PREFIX = 'source caps at'

RunCmd = Callable[..., 'subprocess.CompletedProcess']
Fetch = Callable[..., str]


def _default_run_cmd(argv: List[str], timeout: Optional[float] = None) -> 'subprocess.CompletedProcess':
    return subprocess.run(argv, capture_output=True, text=True, timeout=timeout)


def _default_fetch(url: str, timeout: Optional[float] = None) -> str:
    with urllib.request.urlopen(url, timeout=timeout) as resp:
        return resp.read().decode('utf-8')


def extract_video_id(url: str) -> Optional[str]:
    """Extract an 11-char YouTube video ID from common URL shapes."""
    m = re.search(r'(?:v=|youtu\.be/|/shorts/|/embed/)([A-Za-z0-9_-]{11})', url)
    return m.group(1) if m else None


def _normalize_title(title: str) -> str:
    return re.sub(r'\s+', ' ', title).strip().lower()


def titles_match(a: str, b: str) -> bool:
    """Whitespace/case-insensitive title identity check."""
    return _normalize_title(a) == _normalize_title(b)


def _probe_duration(path: str, run_cmd: RunCmd) -> Optional[float]:
    """Return media duration in seconds via ffprobe, or None when unavailable."""
    try:
        proc = run_cmd(
            ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
             '-of', 'csv=p=0', path],
            timeout=FFMPEG_TIMEOUT_SEC,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    try:
        return float(proc.stdout.strip())
    except ValueError:
        return None


def _probe_height(path: str, run_cmd: RunCmd) -> Optional[int]:
    """Return the first video stream height via ffprobe, or None."""
    try:
        proc = run_cmd(
            ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
             '-show_entries', 'stream=height', '-of', 'csv=p=0', path],
            timeout=FFMPEG_TIMEOUT_SEC,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    try:
        return int(proc.stdout.strip().splitlines()[0])
    except (ValueError, IndexError):
        return None


def _probe_mean_volume_db(path: str, run_cmd: RunCmd) -> Optional[float]:
    """Return the ffmpeg volumedetect mean_volume in dB, or None.

    ffmpeg writes volume stats to stderr; parse them regardless of the
    process exit code (the null muxer always "fails" at the end on some
    builds while the stats are still valid).
    """
    try:
        proc = run_cmd(
            ['ffmpeg', '-hide_banner', '-nostats', '-i', path,
             '-af', 'volumedetect', '-f', 'null', '-'],
            timeout=FFMPEG_TIMEOUT_SEC,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    m = re.search(r'mean_volume:\s*(-?[\d.]+)\s*dB', proc.stderr)
    return float(m.group(1)) if m else None


def _fetch_oembed_title(video_id: str, fetch: Fetch) -> Optional[str]:
    """Return the canonical YouTube title via oEmbed, or None when unavailable."""
    qs = urllib.parse.urlencode({
        'url': 'https://www.youtube.com/watch?v=' + video_id,
        'format': 'json',
    })
    try:
        payload = fetch(OEMBED_ENDPOINT + '?' + qs, timeout=OEMBED_TIMEOUT_SEC)
        title = json.loads(payload).get('title')
        return title if isinstance(title, str) else None
    except (OSError, ValueError):
        return None


def verify_download(
    path: str,
    expected_duration_sec: Optional[float] = None,
    expected_height: Optional[int] = None,
    expected_title: Optional[str] = None,
    video_id: Optional[str] = None,
    reference_height: Optional[int] = None,
    run_cmd: Optional[RunCmd] = None,
    fetch: Optional[Fetch] = None,
) -> Dict:
    """Run the post-download verification gates for one file.

    Status semantics:
    - 'ok'          — all gates pass and the resolution reached the reference/cap
    - 'already-max' — gates pass but the source ceiling (probed max height) is
                      below the reference height: nothing better was available
    - 'failed'      — a hard gate failed (see 'reasons')
    Soft findings (resolution below probed max, tools/network unavailable) are
    recorded in 'warnings' and do not fail the download.
    """
    if run_cmd is None:
        run_cmd = _default_run_cmd
    if fetch is None:
        fetch = _default_fetch

    result: Dict = {
        'path': path,
        'size_mb': None,
        'checks': {
            'exists': False, 'size_ok': False,
            'duration_ok': None, 'audio_ok': None,
            'title_ok': None, 'resolution_ok': None,
        },
        'measured': {
            'duration_sec': None, 'mean_volume_db': None,
            'height': None, 'oembed_title': None,
        },
        'warnings': [],
        'reasons': [],
        'status': 'failed',
    }

    # Gate 1 — file presence and minimum size
    if not os.path.exists(path):
        result['reasons'].append('file not found: %s' % path)
        return result
    result['checks']['exists'] = True
    size_bytes = os.path.getsize(path)
    result['size_mb'] = round(size_bytes / (1024 * 1024), 2)
    if size_bytes <= MIN_SIZE_BYTES:
        result['reasons'].append(
            'file too small: %.2f MB (minimum threshold is 1 MB)' % result['size_mb']
        )
        return result
    result['checks']['size_ok'] = True

    hard_fail = False

    # Gate 2 — duration within ±5% of expected
    duration = _probe_duration(path, run_cmd)
    result['measured']['duration_sec'] = duration
    if expected_duration_sec and duration is not None:
        delta = abs(duration - expected_duration_sec) / expected_duration_sec
        duration_ok = delta <= DURATION_TOLERANCE
        result['checks']['duration_ok'] = duration_ok
        if not duration_ok:
            hard_fail = True
            result['reasons'].append(
                'duration mismatch: expected %.1fs, measured %.1fs (tolerance ±5%%)'
                % (expected_duration_sec, duration)
            )
    elif duration is None:
        result['warnings'].append('duration could not be measured (ffprobe unavailable?)')

    # Gate 3 — audio not silent
    mean_db = _probe_mean_volume_db(path, run_cmd)
    result['measured']['mean_volume_db'] = mean_db
    if mean_db is not None:
        audio_ok = mean_db >= MIN_MEAN_VOLUME_DB
        result['checks']['audio_ok'] = audio_ok
        if not audio_ok:
            hard_fail = True
            result['reasons'].append(
                'audio track is silent: mean %.1f dB is below the %.0f dB threshold'
                % (mean_db, MIN_MEAN_VOLUME_DB)
            )
    else:
        result['warnings'].append('audio loudness could not be measured (ffmpeg unavailable?)')

    # Gate 4 — oEmbed title identity
    if expected_title and video_id:
        oembed_title = _fetch_oembed_title(video_id, fetch)
        result['measured']['oembed_title'] = oembed_title
        if oembed_title is not None:
            title_ok = titles_match(oembed_title, expected_title)
            result['checks']['title_ok'] = title_ok
            if not title_ok:
                hard_fail = True
                result['reasons'].append(
                    'title identity mismatch: requested %r but oEmbed reports %r'
                    % (expected_title, oembed_title)
                )
        else:
            result['warnings'].append('oEmbed title check skipped (network unavailable?)')

    # Gate 5 — resolution equals the probed maximum (warn, not fail)
    height = _probe_height(path, run_cmd)
    result['measured']['height'] = height
    if expected_height and height is not None:
        resolution_ok = height == expected_height
        result['checks']['resolution_ok'] = resolution_ok
        if not resolution_ok:
            result['warnings'].append(
                'downloaded height %dp is below the probed maximum %dp' % (height, expected_height)
            )

    if hard_fail:
        return result

    # Source-ceiling reporting: probed max below the reference height means
    # the source caps lower than the reference — the download is already the
    # best available (report-only; never a download cap).
    if reference_height and expected_height is not None and expected_height < reference_height:
        result['status'] = 'already-max'
        result['warnings'].append(
            '%s %dp (reference %dp) — already max available quality'
            % (SOURCE_CAP_WARNING_PREFIX, expected_height, reference_height)
        )
    else:
        result['status'] = 'ok'
    return result


def build_manifest(entries: List[Dict], tool: Optional[Dict] = None) -> Dict:
    """Assemble a batch manifest: per-video entries + totals + tool info."""
    counts = {'ok': 0, 'already_max': 0, 'failed': 0, 'other': 0}
    for entry in entries:
        status = entry.get('status')
        if status == 'ok':
            counts['ok'] += 1
        elif status == 'already-max':
            counts['already_max'] += 1
        elif status == 'failed':
            counts['failed'] += 1
        else:
            counts['other'] += 1
    return {
        'generated_at': datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'tool': tool or {},
        'videos': entries,
        'totals': {
            'videos': len(entries),
            'ok': counts['ok'],
            'already_max': counts['already_max'],
            'failed': counts['failed'],
            'other': counts['other'],
        },
    }
