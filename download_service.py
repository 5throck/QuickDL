import os
import threading
from typing import Optional, Callable
from i18n import t, format_duration


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
        return {
            'title': info_dict.get('title'),
            'thumbnail': info_dict.get('thumbnail'),
            'duration': duration,
            'channel': info_dict.get('uploader')
        }


def download_video(
    url: str,
    output_dir: str,
    ydl_class=None,
    progress_hook: Optional[Callable] = None,
    cancel_event: Optional[threading.Event] = None,
) -> str:
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

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(output_dir, '%(title).100s.%(ext)s'),
        'merge_output_format': 'mp4',
        'windowsfilenames': True,
        'nocheckcertificate': True,
        'progress_hooks': hooks,
    }
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
