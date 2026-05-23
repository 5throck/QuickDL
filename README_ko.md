# QuickDL

데스크톱 앱, 시스템 트레이, 웹 UI, CLI를 갖춘 경량 YouTube 영상 다운로더입니다.

![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)
![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)
![CI](https://github.com/5throck/QuickDL/actions/workflows/ci.yml/badge.svg)

[View English Documentation](README.md)

---

## 주요 기능

- **데스크톱 앱** — 더블클릭으로 실행. 터미널 불필요.
- **시스템 트레이** — 트레이 아이콘을 통한 앱 관리 기능.
- **웹 UI** — 실시간 다운로드 큐와 진행률을 제공하는 완전한 브라우저 인터페이스.
- **CLI** — `python cli.py <URL>`로 빠른 터미널 다운로드.
- **최고 화질** — 최고 영상 + 오디오를 자동 병합하여 MP4로 저장 (ffmpeg 필요).
- **다크 / 라이트 모드** — OS 테마를 자동으로 따릅니다.
- **다운로드 큐** — 여러 다운로드를 동시에 시작하고 항목별 진행률을 확인.
- **16개 언어** — OS 로케일 자동 감지 (en, ko, ja, zh-TW, zh-CN, de, es, fr, pt, vi, ms, id, th, ru, it, ar).
- **크로스플랫폼** — Windows, macOS, Linux 지원.

---

## 시스템 요구사항

- Python 3.8 이상
- ffmpeg (고화질 영상/오디오 병합 시 필요)
  - Windows: `winget install ffmpeg` 또는 https://ffmpeg.org/download.html
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`

---

## 설치

```bash
git clone https://github.com/5throck/QuickDL.git
cd QuickDL
python install.py
```

`install.py`가 자동으로 수행하는 작업:
- Python 버전 확인 (3.8+)
- 가상환경(`.venv/`) 생성
- `requirements.txt`의 모든 의존성 설치
- 시스템에 누락된 경우 패키지 매니저(winget, brew, apt)를 통해 `ffmpeg` 자동 설치
- 필요한 환경변수 설정 (`PYTHONIOENCODING=utf-8`)

---

## 사용법

### 데스크톱 앱 (권장)

**Windows:**
```
ytdl.bat 더블클릭
```

**macOS / Linux:**
```bash
chmod +x ytdl.sh
./ytdl.sh
```

또는 직접 실행:
```bash
python desktop.py
```

앱이 창으로 열리고 트레이 아이콘이 추가됩니다.  
창을 닫으면 프로그램이 완전히 종료됩니다. 트레이 아이콘의 '종료' 메뉴를 통해서도 종료할 수 있습니다.

### 웹 UI (브라우저)

```bash
python app.py
# http://localhost:5000 열기
```

YouTube URL을 붙여넣고 **다운로드** 버튼을 클릭하면 실시간 진행률 큐에서 상태를 확인할 수 있습니다.  
완료되면 다운로드 링크가 표시됩니다.

### CLI

```bash
# 기본 다운로드 (./downloads/ 에 저장)
python cli.py <YouTube URL>

# 저장 경로 지정
python cli.py <YouTube URL> --output /저장/경로

# 언어 강제 지정
QUICKDL_LANG=en python cli.py <URL>   # macOS/Linux
set QUICKDL_LANG=en && python cli.py <URL>  # Windows
```

---

## 프로젝트 구조

```
QuickDL/
├── app.py                  # Flask 서버 — 라우트, 작업 큐, 파일 서빙
├── download_service.py     # yt-dlp 래퍼 (get_video_info, download_video)
├── desktop.py              # 데스크톱 진입점 (pywebview + pystray)
├── cli.py                  # CLI 진입점 (argparse)
├── install.py              # 크로스플랫폼 설치 스크립트
├── i18n.py                 # i18n: init(), t(), get_all(), format_duration()
├── requirements.txt        # Python 의존성
├── ytdl.bat                # Windows 실행 스크립트
├── ytdl.sh                 # macOS/Linux 실행 스크립트
├── locales/                # 16개 언어 번역 파일 (en.json 기준)
├── templates/index.html    # 웹 UI (Jinja2)
├── static/
│   ├── css/styles.css      # UI 스타일 (다크 + 라이트, 반응형)
│   └── js/script.js        # 프론트엔드 JS (fetch, 큐, 폴링)
├── tests/
│   ├── test_app.py         # Flask API 테스트 (9개 — unittest)
│   ├── test_i18n.py        # i18n 테스트 (14개 — pytest)
│   └── test_env.py         # 의존성 확인
├── scripts/
│   ├── audit.sh / audit.ps1        # 품질 게이트
│   └── dev-sync.sh / dev-sync.ps1  # PR 파이프라인
└── docs/context.md         # AI 도구용 프로젝트 컨텍스트
```

---

## 테스트 실행

```bash
pytest tests/ -v        # 전체 23개 테스트
bash scripts/audit.sh   # 품질 게이트 (CHANGELOG, i18n 키 동기화, 링크 검사)
```

---

## 라이선스

이 프로젝트는 [GNU Affero General Public License v3.0](LICENSE) 라이선스를 따릅니다.


## 🤖 Multi-Agent Kickoff (Recommended)
Before writing any code or beginning a new major feature, ask the AI to start a PM-led kickoff meeting:
> *"Let's start the PM agent kickoff meeting for this project."*
This will trigger the Phase 0 Dynamic Team Assembly process to align roles and skills.
