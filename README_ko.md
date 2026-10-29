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
- **CLI** — `python cli.py <URL>`로 빠른 터미널 다운로드, 배치(여러 URL) 지원.
- **최고 화질** — 최고 영상 + 오디오를 자동 병합하여 MP4로 저장 (ffmpeg 필요).
- **최대 품질 모드** — `--quality best`: 영상별로 프로브하여 인위적 해상도 제한 없이 최대 해상도를 다운로드하고, 동일 화질에서는 브라우저/기기 호환을 위해 h264/aac를 우선합니다.
- **자막 사이드카** — `--write-subs`: 수동 자막(없으면 자동 생성)을 WebVTT(.vtt)로 영상 옆에 저장합니다.
- **자막 폴백 체인** — `--captions-langs "ko,en"`: 요청한 두 언어를 영상별로 모두 수집합니다. 언어별 정직한 폴백 체인(수동 → 자동 생성 → YouTube 자동 번역)을 적용하고, 매니페스트의 각 사이드카에 `manual | auto | translated | failed`로 표시합니다. YouTube 번역 엔드포인트는 요청 한도(429)가 있으므로, 견고한 파이프라인은 매니페스트를 근거로 `failed` 언어를 외부 번역 단계로 처리해야 합니다.
- **자막 정제 파이프라인** — 다운로드된 모든 사이드카는 최종 저장 전에 자동으로 정제됩니다: 인라인 `<c>`/타임스탬프 태그 제거, 롤링 중복 큐 병합, 겹치는 큐 구간 클리핑(원본 YouTube ASR grab이 깨끗한 큐 파일로 변환됨). 매니페스트에는 사이드카별로 `cleaned: true`와 최종 큐 수가 기록됩니다.
- **자막 커버리지 게이트** — 각 사이드카를 영상 길이와 비교해 측정합니다(매니페스트에 `coverage` 0–1, 알 수 없으면 null). 커버리지가 0.95 미만이면 기본적으로 매니페스트에 경고를 기록하고, `--require-caption-coverage`(`--verify`와 함께)는 다운로드를 실패 처리합니다 — 전체 길이를 덮는 자막이 아니면 이 영상을 사용하지 마세요. 영상 중간에 끊기는 소스 트랙 같은 보이지 않는 결함을 잡아냅니다.
- **교체/은퇴 감사 추적** — `--swap OLD_ID:NEW_URL`(반복 가능)은 이전 배치의 영상을 매니페스트 최상위 `retired[]` 목록으로 날짜·사유와 함께 옮기고, 대체 항목에는 `swapped_from` + `swap {date, reason}`을 기록합니다 — 배치 재실행을 위한 완전한 감사 추적입니다.
- **원어 오디오 강제** — `--audio-lang auto`(기본값)는 영상의 원어 음성 트랙을 감지하여 YouTube 자동 더빙 오디오를 배제합니다(실제 장애 사례: 영어 세미나가 일본어 더빙으로 저장됨). `--audio-lang en|ko|…`로 특정 트랙을 강제할 수 있고, 언어 태그가 병합된 MP4에 기록됩니다.
- **검증 게이트** — `--verify`: 다운로드 후 파일 크기, 길이, 오디오 음량, oEmbed 제목 일치, 해상도를 검증합니다.
- **다운로드 매니페스트** — `--manifest out.json`: 배치별 감사 가능한 JSON 보고서를 기록합니다 (영상별 상태 + 합계).
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

# 최대 품질 모드 (높이 제한 없음, 동일 화질에서 h264/aac 우선)
python cli.py <URL> --quality best

# 해상도를 720p로 제한
python cli.py <URL> --quality cap:720

# 자막 사이드카 (.vtt) — 수동 자막 우선, 언어 우선순위 설정 가능
python cli.py <URL> --write-subs --sub-langs "ko.*,en.*"

# 두 언어 모두에 대한 자막 폴백 체인 (수동 → 자동 → 자동 번역,
# 매니페스트에 manual|auto|translated|failed 로 기록)
python cli.py <URL> --write-subs --captions-langs "ko,en"

# 엄격한 자막 커버리지 게이트 (--verify와 함께): 사이드카가 영상 길이의
# 0.95 미만만 덮으면 경고 대신 다운로드를 실패 처리
python cli.py <URL> --write-subs --verify --require-caption-coverage

# 후반 요구사항(예: 부분 자막)을 통과하지 못한 영상 교체: 기존 항목은
# 매니페스트의 retired[] 목록으로 날짜+사유와 함께 이동하고, 대체 항목에는
# swapped_from이 기록됨
python cli.py <URL_OLD> <URL_NEW> --manifest batch.json \
    --swap dQw4w9WgXcQ:https://youtu.be/<new_id> \
    --swap-reason "소스 자막이 영상의 62%만 커버"

# YouTube 자동 더빙 방지: 'auto'는 원어 트랙 선택 (다중 언어 영상),
# 또는 특정 트랙을 명시적으로 강제
python cli.py <URL> --audio-lang auto
python cli.py <URL> --audio-lang en

# 프로덕션 배치: 각 다운로드를 검증하고 JSON 매니페스트 기록
python cli.py <URL1> <URL2> --quality best --write-subs --verify \
    --manifest batch.json --id-names

# 언어 강제 지정
QUICKDL_LANG=en python cli.py <URL>   # macOS/Linux
set QUICKDL_LANG=en && python cli.py <URL>  # Windows
```

CLI 종료 코드: `0` 성공 · `1` 다운로드 실패 · `2` 검증 실패 (`--verify` 사용 시).
배치에서 한 URL이 실패해도 나머지는 계속 처리됩니다.

---

## 프로젝트 구조

```
QuickDL/
├── app.py                  # Flask 서버 — 라우트, 작업 큐, 파일 서빙
├── download_service.py     # yt-dlp 래퍼 (get_video_info, download_video)
├── verification.py         # 다운로드 후 검증 게이트 + 배치 매니페스트 생성
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
│   ├── test_app.py               # Flask API 테스트 (9개 — unittest)
│   ├── test_i18n.py              # i18n 테스트 (14개 — pytest)
│   ├── test_download_service.py  # 서비스 레이어 테스트 (pytest, yt-dlp 목)
│   ├── test_verification.py      # 검증 게이트 테스트 (pytest, 목)
│   └── test_env.py               # 의존성 확인
├── scripts/
│   ├── audit.sh / audit.ps1        # 품질 게이트
│   └── dev-sync.sh / dev-sync.ps1  # PR 파이프라인
└── docs/context.md         # AI 도구용 프로젝트 컨텍스트
```

---

## 테스트 실행

```bash
pytest tests/ -v        # 전체 111개 테스트
bash scripts/audit.sh   # 품질 게이트 (CHANGELOG, i18n 키 동기화, 링크 검사)
```

---

## 라이선스

이 프로젝트는 [GNU Affero General Public License v3.0](LICENSE) 라이선스를 따릅니다.
