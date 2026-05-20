import sys
try:
    import flask
    import yt_dlp
    import flask_cors
    print("All packages installed.")
except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"Error: {e}")
