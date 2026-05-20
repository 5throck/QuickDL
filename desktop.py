import queue
import socket
import sys
import threading
import time
from pathlib import Path

import webview
from PIL import Image, ImageDraw
import pystray

sys.path.insert(0, str(Path(__file__).parent))
from app import app as flask_app
from i18n import init as i18n_init, t

APP_NAME = "QuickDL"


def find_free_port(preferred=5000):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("127.0.0.1", preferred))
            return preferred
    except OSError:
        pass
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def wait_for_server(port, timeout=5.0):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.1)
    return False


def make_tray_icon():
    img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    draw.ellipse([4, 4, 124, 124], fill="#FF0000")
    draw.polygon([(48, 36), (48, 92), (96, 64)], fill="white")
    return img


def run_flask(port):
    flask_app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False, threaded=True)


def main():
    i18n_init()
    port = find_free_port()
    url = f"http://127.0.0.1:{port}"

    flask_thread = threading.Thread(target=run_flask, args=(port,), daemon=True)
    flask_thread.start()

    if not wait_for_server(port):
        try:
            import tkinter.messagebox as mb
            mb.showerror(APP_NAME, t("desktop.server_error_msg"))
        except Exception:
            print(t("desktop.server_error_print"))
        sys.exit(1)

    event_queue = queue.Queue()

    def create_window():
        win = webview.create_window(
            APP_NAME, url, width=900, height=700, min_size=(600, 500)
        )
        # 창이 닫혀도 앱을 종료하지 않음 — 트레이에서 계속 접근 가능.
        # pywebview 백엔드에 따라 창만 사라지고 프로세스는 유지됨.
        # 완전 종료는 트레이 "종료" 메뉴를 통해서만 수행.
        win.events.closed += lambda: event_queue.put("closed")
        return win

    def tray_open(_icon, _item):
        event_queue.put("show")

    def tray_quit(_icon, _item):
        event_queue.put("quit")

    tray_icon = pystray.Icon(
        APP_NAME,
        make_tray_icon(),
        APP_NAME,
        menu=pystray.Menu(
            pystray.MenuItem(APP_NAME, None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(t("desktop.tray_open"), tray_open),
            pystray.MenuItem(t("desktop.tray_quit"), tray_quit),
        ),
    )
    threading.Thread(target=tray_icon.run, daemon=True).start()

    def poll_queue():
        while True:
            time.sleep(0.1)
            try:
                event = event_queue.get_nowait()
            except queue.Empty:
                continue
            if event == "show":
                # pywebview가 poll_queue를 GUI 스레드에서 실행하므로 여기서 create_window() 호출 가능.
                # 백엔드에 따라 threading 오류 발생 시: webview.windows[0].show() 를 시도할 것.
                create_window()
            elif event == "quit":
                tray_icon.stop()
                for w in webview.windows:
                    w.destroy()
                return  # webview.start()의 func이 반환되면 이벤트 루프가 정상 종료됨

    create_window()
    webview.start(poll_queue)
    sys.exit(0)  # webview.start() 정상 반환 후 종료


if __name__ == "__main__":
    main()
