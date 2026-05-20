import os
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from download_service import get_video_info, download_video

app = Flask(__name__)
CORS(app)

DOWNLOAD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'downloads')
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/info', methods=['POST'])
def get_info():
    data = request.json
    url = data.get('url')
    if not url:
        return jsonify({'error': 'URL이 필요합니다.'}), 400
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
        return jsonify({'error': 'URL이 필요합니다.'}), 400
    try:
        # Blocks until download completes
        filepath = download_video(url, DOWNLOAD_DIR)
        return jsonify({
            'success': True, 
            'message': '다운로드가 완료되었습니다.', 
            'filepath': filepath
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
