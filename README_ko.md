# QuickDL

데스크톱 앱, 시스템 트레이, CLI를 갖춘 경량 YouTube 영상 다운로더입니다.

![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)
![Python 3.8+](https://img.shields.io/badge/Python-3.8%2B-blue)

## 주요 기능

- **데스크톱 앱** — 더블클릭으로 실행. 터미널 불필요.
- **시스템 트레이** — 트레이로 최소화 후 언제든 재오픈.
- **CLI** — `python cli.py <URL>`로 빠른 터미널 다운로드.
- **최고 화질** — 자동으로 최고 화질 MP4 다운로드.
- **크로스플랫폼** — Windows, macOS, Linux 지원.

## 시스템 요구사항

- Python 3.8 이상
- ffmpeg (선택, 고화질 영상/오디오 병합 시 필요)

## 설치

```bash
git clone https://github.com/5throck/QuickDL.git
cd QuickDL
python install.py
```

`install.py`가 자동으로 수행하는 작업:
- Python 버전 확인
- 가상환경(`.venv/`) 생성
- 의존성 패키지 설치
- 필요한 환경변수 설정

## 사용법

### 데스크톱 앱

**Windows:**
```
ytdl.bat 더블클릭
```

**macOS / Linux:**
```bash
./ytdl.sh
```

또는 직접 실행:
```bash
python desktop.py
```

### CLI

```bash
python cli.py <YouTube URL>
python cli.py <YouTube URL> --output /저장/경로
```

### 웹 UI (브라우저)

```bash
python app.py
# http://localhost:5000 열기
```

## 프로젝트 구조

```
QuickDL/
├── app.py              # Flask 웹 서버
├── download_service.py # 다운로드 로직 (yt-dlp)
├── desktop.py          # 데스크톱 앱 진입점
├── cli.py              # CLI 진입점
├── install.py          # 크로스플랫폼 설치 스크립트
├── ytdl.bat            # Windows 실행 스크립트
├── ytdl.sh             # macOS/Linux 실행 스크립트
├── requirements.txt
├── templates/
└── static/
```

## 라이선스

이 프로젝트는 [GNU Affero General Public License v3.0](LICENSE) 라이선스를 따릅니다.
