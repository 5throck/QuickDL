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
from i18n import init as i18n_init, t


def main():
    i18n_init()
    parser = argparse.ArgumentParser(description=t("cli.description"))
    parser.add_argument("url", help="YouTube URL")
    parser.add_argument(
        "--output",
        default=str(Path(__file__).parent / "downloads"),
        help=t("cli.help_output"),
    )
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)

    print(t("cli.fetching"))
    try:
        info = download_service.get_video_info(args.url)
    except Exception as e:
        print(t("cli.error", e=e))
        sys.exit(1)

    duration = info.get("duration", "")
    print(t("cli.title_line", title=info.get('title', t("cli.unknown")), duration=duration))
    print(t("cli.channel_line", channel=info.get('channel', t("cli.unknown"))))
    print(t("cli.downloading"))

    try:
        saved_path = download_service.download_video(args.url, args.output)
    except Exception as e:
        print(t("cli.download_failed", e=e))
        sys.exit(1)

    if saved_path and os.path.exists(saved_path):
        print(t("cli.saved", saved_path=saved_path))
    else:
        print(t("cli.done", output=args.output))


if __name__ == "__main__":
    main()
