import os
import re
import threading
import uuid
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from download_service import get_video_info, download_video
from i18n import init as i18n_init, t, get_all, get_lang

app = Flask(__name__)
CORS(app, origins=re.compile(r"http://(localhost|127\.0\.0\.1)(:\d+)?$"))

i18n_init()

DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

_jobs: dict = {}

_URL_PATTERN = re.compile(r'^https?://', re.IGNORECASE)


def _validate_url(url: str) -> bool:
    return bool(url and _URL_PATTERN.match(url))


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


@app.route('/api/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({'error': t('app.error_url_required')}), 400
    if not _validate_url(url):
        return jsonify({'error': t('app.error_invalid_url')}), 400

    job_id = str(uuid.uuid4())
    _jobs[job_id] = {"status": "pending", "filepath": None, "error": None}

    def run():
        _jobs[job_id]["status"] = "running"
        try:
            filepath = download_video(url, DOWNLOAD_DIR)
            _jobs[job_id].update({"status": "done", "filepath": filepath})
        except Exception as e:
            _jobs[job_id].update({"status": "error", "error": str(e)})

    threading.Thread(target=run, daemon=True).start()
    return jsonify({"job_id": job_id, "status": "pending"})


@app.route('/api/status/<job_id>', methods=['GET'])
def job_status(job_id):
    job = _jobs.get(job_id)
    if not job:
        return jsonify({'error': 'Job not found'}), 404
    if job["status"] in ("done", "error"):
        _jobs.pop(job_id, None)
    return jsonify(job)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
