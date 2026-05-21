import os
import re
import threading
import time
import uuid
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
from download_service import get_video_info, download_video
from i18n import init as i18n_init, t, get_all, get_lang

_URL_PATTERN = re.compile(r'^https?://', re.IGNORECASE)


def _cleanup_downloads(directory: str, keep_hours: int = 24) -> None:
    """Delete files in directory older than keep_hours. keep_hours=0 disables cleanup."""
    if keep_hours == 0:
        return
    p_dir = Path(directory)
    if not p_dir.exists():
        return  # directory not yet created — safe skip
    cutoff = time.time() - keep_hours * 3600
    for p in p_dir.iterdir():
        if p.is_file() and p.stat().st_mtime < cutoff:
            try:
                p.unlink()
            except OSError:
                pass  # file in use (Windows) or already gone — skip silently


def _validate_url(url: str) -> bool:
    return bool(url and _URL_PATTERN.match(url))


app = Flask(__name__)
CORS(app, origins=re.compile(r"http://(localhost|127\.0\.0\.1)(:\d+)?$"))

i18n_init()

DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

_jobs: dict = {}
_completed: dict = {}  # job_id → filename; persists after _jobs entry is removed
_cancel_events: dict = {}  # job_id → threading.Event


@app.route('/')
def index():
    return render_template('index.html', i18n=get_all(), lang=get_lang())


@app.route('/api/info', methods=['POST'])
def get_info():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({'error': t('app.error_url_required')}), 400
    if not _validate_url(url):
        return jsonify({'error': t('app.error_invalid_url')}), 400
    try:
        info = get_video_info(url)
        return jsonify(info)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def make_progress_hook(job_id):
    def hook(d):
        if d['status'] == 'downloading' and job_id in _jobs:
            # _percent_str is deprecated in yt-dlp ≥2024; use byte counts
            downloaded = d.get('downloaded_bytes', 0)
            total = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            if total:
                _jobs[job_id]['progress'] = int(downloaded * 100 / total)
            _jobs[job_id]['speed'] = d.get('_speed_str')
            _jobs[job_id]['eta'] = d.get('eta')
    return hook


@app.route('/api/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({'error': t('app.error_url_required')}), 400
    if not _validate_url(url):
        return jsonify({'error': t('app.error_invalid_url')}), 400

    job_id = str(uuid.uuid4())
    _jobs[job_id] = {
        "status": "pending",
        "filename": None,
        "error": None,
        "progress": 0,
        "speed": None,
        "eta": None,
    }

    cancel_event = threading.Event()
    _cancel_events[job_id] = cancel_event

    def run():
        _jobs[job_id]["status"] = "running"
        try:
            filepath = download_video(
                url, DOWNLOAD_DIR,
                progress_hook=make_progress_hook(job_id),
                cancel_event=cancel_event,
            )
            filename = os.path.basename(filepath)
            _completed[job_id] = filename           # (1) write _completed FIRST
            _jobs[job_id].update({"status": "done", "filename": filename})  # (2) then done
        except Exception as e:
            if cancel_event.is_set():
                _jobs[job_id].update({"status": "cancelled", "error": "Download cancelled by user"})
            else:
                _jobs[job_id].update({"status": "error", "error": str(e)})
        finally:
            _cancel_events.pop(job_id, None)  # always clean up cancel event

    threading.Thread(target=run, daemon=True).start()
    return jsonify({"job_id": job_id, "status": "pending"})


@app.route('/api/status/<job_id>', methods=['GET'])
def job_status(job_id):
    job = _jobs.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    if job["status"] in ("done", "error", "cancelled"):
        _jobs.pop(job_id, None)
    return jsonify(job)


@app.route('/api/file/<job_id>', methods=['GET'])
def serve_file(job_id):
    filename = _completed.get(job_id)
    if not filename:
        return jsonify({'error': 'File not found or already downloaded'}), 404
    _completed.pop(job_id, None)  # one-time link: consumed on first successful serve
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)


@app.route('/api/status/<job_id>', methods=['DELETE'])
def cancel_job(job_id):
    event = _cancel_events.get(job_id)  # peek — do NOT pop, thread still uses _jobs
    if not event:
        return jsonify({'error': 'Job not found or already finished'}), 404
    event.set()  # signals cancel hook; thread catches exception and sets 'cancelled' status
    return jsonify({'cancelled': True})


if __name__ == '__main__':
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    _keep_hours = int(os.environ.get('QUICKDL_KEEP_HOURS', '24'))
    _cleanup_downloads(DOWNLOAD_DIR, _keep_hours)
    debug = os.environ.get('FLASK_DEBUG', '0') == '1'
    app.run(debug=debug, threaded=True, host='0.0.0.0', port=5000)
