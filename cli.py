#!/usr/bin/env python3
import argparse
import io
import os
import sys
from pathlib import Path

# Ensure UTF-8 output on Windows terminals that default to cp949
if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if sys.stderr.encoding and sys.stderr.encoding.lower() not in ("utf-8", "utf8"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).parent))
import download_service


def main():
    parser = argparse.ArgumentParser(description="QuickDL — YouTube 영상 다운로더")
    parser.add_argument("url", help="YouTube URL")
    parser.add_argument(
        "--output",
        default=str(Path(__file__).parent / "downloads"),
        help="저장 폴더 (기본: ./downloads)",
    )
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    print("📥 영상 정보 조회 중...")
    try:
        info = download_service.get_video_info(args.url)
    except Exception as e:
        print(f"❌ 오류: {e}")
        sys.exit(1)

    duration = info.get("duration", "")
    print(f"🎬 제목: {info.get('title', '알 수 없음')} ({duration})")
    print(f"   채널: {info.get('channel', '알 수 없음')}")
    print("⬇️  다운로드 중...")

    try:
        saved_path = download_service.download_video(args.url, args.output)
    except Exception as e:
        print(f"❌ 다운로드 실패: {e}")
        sys.exit(1)

    if saved_path and os.path.exists(saved_path):
        print(f"✅ 저장됨: {saved_path}")
    else:
        print(f"✅ 다운로드 완료. 저장 위치: {args.output}")


if __name__ == "__main__":
    main()
