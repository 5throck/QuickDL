import yt_dlp
import os
from i18n import t, format_duration

def get_video_info(url):
    ydl_opts = {
        'skip_download': True,
        'extract_flat': False,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
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

def download_video(url, output_dir):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'outtmpl': os.path.join(output_dir, '%(title).100s.%(ext)s'),
        'merge_output_format': 'mp4',
        'windowsfilenames': True,
        'nocheckcertificate': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        base, _ = os.path.splitext(filename)
        # yt-dlp may merge and change the extension to mp4
        return base + '.mp4'
