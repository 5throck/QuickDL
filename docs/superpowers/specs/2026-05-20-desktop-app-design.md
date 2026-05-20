# QuickDL — 데스크톱 앱 전환 설계

## Context

현재 프로젝트는 Flask 웹 앱으로, 사용하려면 터미널에서 `python app.py`를 실행하고 브라우저를 열어야 한다. 이 두 단계를 없애고 더블클릭 하나로 실행되는 데스크톱 앱 경험을 제공하는 것이 목표다. 동시에 터미널에서도 빠르게 사용할 수 있는 CLI도 추가한다.

## 목표

- 더블클릭으로 앱 실행 (데스크톱 창)
- 창을 닫아도 트레이에서 계속 접근 가능
- 터미널에서 `python cli.py <URL>` 한 줄로 다운로드

## 디렉토리 이름 변경

`C:\git\youtube` → `C:\git\QuickDL` 로 이름 변경. 구현 시작 전 `mv` 또는 Windows 탐색기에서 rename.

## 아키텍처

기존 코드(`app.py`, `download_service.py`, `templates/`, `static/`)의 **로직은 변경하지 않는다.** 단, `app.py`의 `app.run()` 호출은 `desktop.py`에서 직접 수행하므로 `debug=False, use_reloader=False`로 오버라이드한다.

### 추가 파일

| 파일 | 역할 |
|------|------|
| `desktop.py` | 데스크톱 앱 진입점 (Flask + pywebview + pystray 통합) |
| `cli.py` | CLI 진입점 (Flask 없이 download_service 직접 호출) |
| `assets/icon.png` | 트레이 아이콘 이미지 (PIL로 런타임 생성) |
| `ytdl.bat` | Windows 원클릭 실행 배치 파일 |

### 추가 패키지 (requirements.txt에도 추가)

```
pywebview   # Flask UI를 네이티브 창으로 표시
pystray     # 시스템 트레이 아이콘
pillow      # pystray 아이콘 렌더링 및 생성
```

## 컴포넌트 설계

### desktop.py

1. 사용 가능한 포트를 자동 탐색 (`socket`으로 빈 포트 확보, 기본 5000 시도 후 실패 시 랜덤 포트)
2. Flask 앱을 백그라운드 스레드로 시작 (`debug=False, use_reloader=False, threaded=True`)
3. 서버 준비 완료까지 polling 대기 (최대 5초, 실패 시 에러 다이얼로그 표시 후 종료)
4. PIL로 트레이 아이콘 이미지를 메모리에서 생성 (128×128, YouTube 레드 원형)
5. pystray 트레이 아이콘 등록 — 별도 스레드로 실행
   - 메뉴: `QuickDL` (비활성 타이틀) / `창 열기` / `종료`
   - `창 열기`: 큐(queue.Queue)에 `"show"` 이벤트를 넣어 메인 스레드에 전달
   - `종료`: 큐에 `"quit"` 이벤트를 넣어 메인 스레드에 전달
6. pywebview 창 생성 (`webview.create_window("QuickDL", url, width=900, height=700, min_size=(600, 500))`)
7. `on_closed` 핸들러: 창을 숨기는 대신 destroy하고 `window_visible = False` 플래그 설정
8. `webview.start(func=poll_queue)`로 메인 스레드에서 이벤트 루프 시작 — `poll_queue`는 0.1초 간격으로 큐를 확인하는 함수
   - `"show"` 이벤트: `webview.create_window(...)` 호출로 창 재생성 (이미 실행 중인 이벤트 루프 안에서 호출, `webview.start()` 재호출 금지)
   - `"quit"` 이벤트: `tray.stop()` 후 `sys.exit(0)` 종료
9. `webview.start()`는 메인 스레드에서 실행 (pywebview 요구사항), polling interval은 0.1초

### cli.py

- `argparse` 사용
- 사용법: `python cli.py <URL> [--output <폴더>]`
- `--output` 기본값: `cli.py` 위치 기준 `downloads/` 폴더
- `download_service.get_video_info(url)` → 제목/채널/길이 출력
- `download_service.download_video(url, output_dir)` → 다운로드 실행
- 반환된 경로에 `os.path.exists()` 확인 후 출력 (불일치 시 fallback 메시지)
- Flask 서버 불필요 — 독립 실행

**출력 예시:**
```
📥 영상 정보 조회 중...
🎬 제목: How to Cook Perfect Pasta (5:32)
⬇️  다운로드 중...
✅ 저장됨: C:\git\QuickDL\downloads\How_to_Cook.mp4
```

### ytdl.bat

```bat
@echo off
cd /d "%~dp0"
if exist ".venv\Scripts\pythonw.exe" (
    ".venv\Scripts\pythonw.exe" desktop.py
) else if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" desktop.py
) else (
    echo [경고] .venv를 찾을 수 없습니다. 시스템 Python으로 실행합니다.
    pythonw desktop.py 2>nul || python desktop.py
)
```

`cd /d "%~dp0"` 로 배치 파일 위치를 기준 디렉토리로 설정 — 공백 포함 경로에서 더블클릭 시에도 정상 동작.

### 트레이 메뉴

```
QuickDL   ← 비활성 타이틀
─────────────────
창 열기
종료
```

## 데이터 흐름

```
[ytdl.bat]
    └─→ desktop.py (메인 스레드)
            ├─→ 포트 탐색 (socket)
            ├─→ Thread: Flask app → localhost:<port>  [debug=False]
            ├─→ Thread: pystray 트레이 아이콘
            │       └─→ 이벤트 큐로 메인 스레드에 신호
            └─→ webview.start() [메인 스레드 점유]
                    └─→ 큐 polling → 창 재생성 or 종료

[python cli.py <URL>]
    └─→ download_service.get_video_info(url)
    └─→ download_service.download_video(url, output_dir)
    └─→ os.path.exists() 확인
    └─→ 터미널 출력
```

## 검증 방법

1. `requirements.txt`에 `pywebview`, `pystray`, `pillow` 추가 후 `pip install -r requirements.txt`
2. `python desktop.py` 실행 → 창이 열리고 기존 UI 표시 확인
3. 포트 5000을 다른 프로세스로 점유 후 실행 → 대체 포트로 정상 동작 확인
4. 트레이 아이콘 우클릭 → 메뉴(`창 열기`, `종료`) 확인
5. 창 닫기 → 트레이에 남아있는지, `창 열기`로 재오픈 가능한지 확인
6. 트레이 `종료` → 완전 종료 확인
7. `python cli.py <YouTube URL>` → 다운로드 완료 및 경로 출력 확인
8. `python cli.py <URL> --output C:\Videos` → 지정 폴더에 저장 확인
9. `ytdl.bat` 더블클릭 → 콘솔 없이 앱 실행 확인
