# test_app.py
import json
import threading
import unittest
from unittest.mock import patch


class TestAppAPI(unittest.TestCase):
    # Prerequisites: Groups A (S-1, S-3/S-4) and B (U-1, U-2) must be implemented.
    # Specifically: _completed, _cancel_events, _validate_url must exist in app.py.

    def setUp(self):
        import app as app_module
        app_module.app.config['TESTING'] = True
        self.client = app_module.app.test_client()
        self.app_module = app_module
        # Reset shared state between tests to prevent inter-test pollution
        app_module._jobs.clear()
        app_module._completed.clear()
        app_module._cancel_events.clear()

    def tearDown(self):
        self.app_module._jobs.clear()
        self.app_module._completed.clear()
        self.app_module._cancel_events.clear()

    # --- /api/info ---

    def test_info_missing_url(self):
        r = self.client.post('/api/info', json={}, content_type='application/json')
        self.assertEqual(r.status_code, 400)

    def test_info_invalid_scheme(self):
        # Requires Group A S-1 URL validation
        r = self.client.post('/api/info',
            json={'url': 'file:///etc/passwd'},
            content_type='application/json')
        self.assertEqual(r.status_code, 400)
        data = json.loads(r.data)
        self.assertIn('error', data)

    def test_info_success(self):
        mock_info = {'title': 'Test', 'thumbnail': 'http://t', 'duration': '3:00', 'channel': 'Ch'}
        with patch('app.get_video_info', return_value=mock_info):
            r = self.client.post('/api/info',
                json={'url': 'https://youtube.com/watch?v=test'},
                content_type='application/json')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(json.loads(r.data)['title'], 'Test')

    # --- /api/download ---

    def test_download_missing_url(self):
        r = self.client.post('/api/download', json={}, content_type='application/json')
        self.assertEqual(r.status_code, 400)

    def test_download_invalid_scheme(self):
        # Requires Group A S-1 URL validation
        r = self.client.post('/api/download',
            json={'url': 'ftp://bad.com'},
            content_type='application/json')
        self.assertEqual(r.status_code, 400)

    def test_download_returns_job_id(self):
        # Block the background thread to avoid race on status assertion
        block = threading.Event()
        def slow_download(*args, **kwargs):
            block.wait()
            return '/downloads/test.mp4'
        with patch('app.download_video', side_effect=slow_download):
            r = self.client.post('/api/download',
                json={'url': 'https://youtube.com/watch?v=test'},
                content_type='application/json')
        self.assertEqual(r.status_code, 200)
        data = json.loads(r.data)
        self.assertIn('job_id', data)
        self.assertEqual(data['status'], 'pending')
        block.set()  # let background thread complete cleanly

    # --- /api/status ---

    def test_status_not_found(self):
        r = self.client.get('/api/status/nonexistent-job-id')
        self.assertEqual(r.status_code, 404)

    def test_status_returns_progress(self):
        import uuid
        job_id = str(uuid.uuid4())
        # Schema matches the full _jobs structure after Groups A + B
        self.app_module._jobs[job_id] = {
            'status': 'running',
            'progress': 50,
            'speed': None,
            'eta': None,
            'filename': None,
            'error': None,
        }
        r = self.client.get(f'/api/status/{job_id}')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(json.loads(r.data)['progress'], 50)

    # --- /api/file ---

    def test_file_not_found(self):
        r = self.client.get('/api/file/nonexistent-job-id')
        self.assertEqual(r.status_code, 404)


if __name__ == '__main__':
    unittest.main()
