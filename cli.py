#!/usr/bin/env python3
import argparse
import glob as _glob
import io
import json
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
from verification import (
    CAPTION_COVERAGE_THRESHOLD,
    DEFAULT_REFERENCE_HEIGHT,
    SOURCE_CAP_WARNING_PREFIX,
    annotate_caption_coverage,
    apply_swaps,
    build_manifest,
    extract_video_id,
    verify_download,
)
from i18n import init as i18n_init, t


def _swap_spec(value: str):
    """Parse a `--swap OLD_ID:NEW_URL` argument (URLs contain colons)."""
    old, sep, new = value.partition(':')
    if not sep or not old.strip() or not new.strip():
        raise argparse.ArgumentTypeError(
            "expected OLD_ID:NEW_URL (e.g. dQw4w9WgXcQ:https://youtu.be/<new_id>)"
        )
    return (old.strip(), new.strip())


def _parse_args():
    parser = argparse.ArgumentParser(description=t("cli.description"))
    parser.add_argument("url", nargs="+", help="YouTube URL(s); multiple URLs form a batch")
    parser.add_argument(
        "--output",
        default=str(Path(__file__).parent / "downloads"),
        help=t("cli.help_output"),
    )
    parser.add_argument(
        "--quality",
        default=None,
        help=t("cli.help_quality"),
    )
    parser.add_argument(
        "--write-subs",
        action="store_true",
        help=t("cli.help_subs"),
    )
    parser.add_argument(
        "--sub-langs",
        default=None,
        help=t("cli.help_sub_langs"),
    )
    parser.add_argument(
        "--captions-langs",
        default=None,
        help=t("cli.help_captions_langs"),
    )
    parser.add_argument(
        "--audio-lang",
        default="auto",
        help=t("cli.help_audio_lang"),
    )
    parser.add_argument(
        "--require-caption-coverage",
        action="store_true",
        help=t("cli.help_require_caption_coverage"),
    )
    parser.add_argument(
        "--swap",
        action="append",
        default=[],
        type=_swap_spec,
        metavar="OLD_ID:NEW_URL",
        help=t("cli.help_swap"),
    )
    parser.add_argument(
        "--swap-reason",
        default=None,
        help=t("cli.help_swap_reason"),
    )
    parser.add_argument(
        "--manifest",
        default=None,
        metavar="PATH",
        help=t("cli.help_manifest"),
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help=t("cli.help_verify"),
    )
    parser.add_argument(
        "--id-names",
        action="store_true",
        help=t("cli.help_id_names"),
    )
    return parser.parse_args()


def _new_entry(url: str) -> dict:
    return {
        "url": url,
        "id": None,
        "title": None,
        "path": None,
        "resolution_height": None,
        "size_mb": None,
        "duration_min": None,
        "audio_mean_db": None,
        "audio_language": None,
        "subtitles": [],
        "status": "failed",
        "warnings": [],
    }


def _reference_height(quality) -> int:
    """Reporting reference height for verification (never a download cap)."""
    if quality == "best":
        return DEFAULT_REFERENCE_HEIGHT
    cap = download_service.parse_quality(quality)
    return cap if cap else DEFAULT_REFERENCE_HEIGHT


def _discover_subtitles(saved_path: str) -> list:
    base, _ = os.path.splitext(saved_path)
    return sorted(_glob.glob(base + ".*.vtt"))


def _write_subs(args) -> bool:
    # --captions-langs implies --write-subs
    return args.write_subs or bool(args.captions_langs)


def _requested_caption_langs(args) -> list:
    """Plain language codes to plan caption acquisition for.

    `--captions-langs "ko,en"` gives the codes directly; otherwise the
    `--sub-langs` patterns are reduced to codes ('ko.*' → 'ko') so the same
    fallback-chain plan applies to the plain --write-subs flow.
    """
    if not _write_subs(args):
        return []
    raw = args.captions_langs or args.sub_langs or download_service.DEFAULT_SUB_LANGS
    codes = []
    for part in raw.split(","):
        code = part.strip()
        if code.endswith(".*"):
            code = code[:-2]
        if code and code not in codes:
            codes.append(code)
    return codes


def _caption_plan(args, info) -> list:
    """Resolve per-language caption sources: manual → auto → translated.

    With no caption data exposed by the probe every entry is 'unknown' and
    `_sub_langs_for_download` passes the legacy pattern string through
    byte-for-byte; when data exists, failed languages are not requested at
    all but recorded as 'failed' in the manifest.
    """
    requested = _requested_caption_langs(args)
    if not requested:
        return []
    return download_service.plan_caption_sources(
        requested,
        info.get("manual_caption_langs"),
        info.get("auto_caption_langs"),
    )


def _sub_langs_for_download(args, plan: list) -> str:
    if not plan:
        return args.sub_langs
    if any(p["source"] == "unknown" for p in plan):
        return args.sub_langs or download_service.DEFAULT_SUB_LANGS
    return ",".join(p["request"] for p in plan if p["request"])


def _tool_info(args) -> dict:
    try:
        import yt_dlp
        version = yt_dlp.version.__version__
    except Exception:
        version = "unknown"
    sub_langs = None
    if _write_subs(args):
        sub_langs = args.sub_langs or download_service.DEFAULT_SUB_LANGS
    tool = {
        "name": "yt-dlp",
        "version": version,
        "quality": args.quality or "legacy",
        "format": download_service.format_for_quality(args.quality),
        "merge_output_format": "mp4",
        "subtitles": bool(args.write_subs or args.captions_langs),
        "sub_langs": sub_langs,
        "captions_langs": args.captions_langs,
        "audio_lang": args.audio_lang,
        "id_keyed_names": bool(args.id_names),
        "verify": bool(args.verify),
        "require_caption_coverage": bool(args.require_caption_coverage),
        "caption_coverage_threshold": CAPTION_COVERAGE_THRESHOLD,
    }
    if args.swap:
        # Audit trail: the exact swap directives applied to this batch
        # (per-entry swapped_from/swap and retired[] carry the outcome).
        tool["swaps"] = [{"retires": old, "replaced_by_url": new} for old, new in args.swap]
        if args.swap_reason:
            tool["swap_reason"] = args.swap_reason
    return tool


def _print_verification(result: dict, expected_height) -> None:
    if result["status"] == "failed":
        print(t("cli.verify_failed", reason="; ".join(result["reasons"])))
        return
    already_max = result["status"] == "already-max"
    if already_max and expected_height:
        print(t("cli.already_max", height=expected_height))
    else:
        print(t("cli.verify_ok"))
    for warning in result["warnings"]:
        if already_max and warning.startswith(SOURCE_CAP_WARNING_PREFIX):
            continue  # already reported via cli.already_max
        print(t("cli.verify_warning", reason=warning))


def _download_one(url: str, args) -> dict:
    """Download (and optionally verify) one URL, returning its manifest entry.

    Legacy message flow (fetching → title → channel → downloading → saved)
    is preserved exactly for single-URL runs without new flags.
    """
    entry = _new_entry(url)

    print(t("cli.fetching"))
    try:
        info = download_service.get_video_info(url)
    except Exception as e:
        print(t("cli.error", e=e))
        return entry

    duration = info.get("duration", "")
    entry["id"] = info.get("id")
    entry["title"] = info.get("title")
    print(t("cli.title_line", title=info.get("title", t("cli.unknown")), duration=duration))
    print(t("cli.channel_line", channel=info.get("channel", t("cli.unknown"))))

    # Original-audio forcing (anti auto-dubbing): resolve --audio-lang to a
    # concrete code; 'auto' picks the probed original spoken language.
    audio_lang = download_service.resolve_audio_language(args.audio_lang, info)
    entry["audio_language"] = audio_lang
    available = info.get("audio_languages") or []
    if len(available) > 1:
        entry["audio_languages_available"] = available
        if audio_lang:
            print(t("cli.audio_lang", lang=audio_lang))
        else:
            entry["warnings"].append(
                "multiple audio languages available (%s) but the original "
                "could not be determined" % ", ".join(available)
            )
    elif audio_lang and available and args.audio_lang != "auto" and audio_lang not in available:
        entry["warnings"].append(
            "requested audio language '%s' not offered (available: %s) — "
            "falling back to the default audio track" % (audio_lang, ", ".join(available))
        )

    # Caption fallback chain: per requested language pick manual → auto →
    # YouTube auto-translated; failed languages get an honest manifest record.
    write_subs = _write_subs(args)
    plan = _caption_plan(args, info)

    print(t("cli.downloading"))

    try:
        saved_path = download_service.download_video(
            url,
            args.output,
            quality=args.quality,
            write_subs=write_subs,
            sub_langs=_sub_langs_for_download(args, plan),
            id_keyed_names=args.id_names,
            audio_lang=audio_lang,
        )
    except Exception as e:
        print(t("cli.download_failed", e=e))
        return entry

    entry["path"] = saved_path

    if saved_path and os.path.exists(saved_path):
        print(t("cli.saved", saved_path=saved_path))
    else:
        print(t("cli.done", output=args.output))

    if write_subs:
        paths = _discover_subtitles(saved_path)
        subs = []
        for p in paths:
            # Cleaning pipeline: strip inline tags, drop rolling duplicates,
            # clip overlapping windows — in place, before the manifest entry
            # is built (the raw grab is transient).
            cue_count = download_service.clean_sidecar(p)
            sub = download_service.subtitle_entry(p, saved_path, plan)
            if cue_count is not None:
                sub["cleaned"] = True
                sub["cues"] = cue_count
            subs.append(sub)
        for p in plan:
            if p["source"] == "failed":
                subs.append({"path": None, "lang": p["lang"], "source": "failed"})
        entry["subtitles"] = subs
        if paths:
            names = ", ".join(os.path.basename(p) for p in paths)
            print(t("cli.subs_saved", files=names))
        # Caption coverage: manifest warnings by default. With --verify the
        # gate runs inside verify_download (measured duration, optional
        # strict failure via --require-caption-coverage); without it the
        # probe duration annotates the entries directly.
        if not args.verify:
            entry["warnings"].extend(
                annotate_caption_coverage(subs, info.get("duration_sec"))
            )

    if args.verify:
        print(t("cli.verifying"))
        result = verify_download(
            saved_path,
            expected_duration_sec=info.get("duration_sec"),
            expected_height=info.get("height"),
            expected_title=info.get("title"),
            video_id=info.get("id") or extract_video_id(url),
            reference_height=_reference_height(args.quality),
            subtitles=entry.get("subtitles") or None,
            require_caption_coverage=args.require_caption_coverage,
        )
        _print_verification(result, info.get("height"))
        entry["resolution_height"] = result["measured"].get("height")
        entry["size_mb"] = result["size_mb"]
        measured_duration = result["measured"].get("duration_sec")
        if measured_duration:
            entry["duration_min"] = round(measured_duration / 60.0, 2)
        entry["audio_mean_db"] = result["measured"].get("mean_volume_db")
        entry["status"] = result["status"]
        entry["warnings"] = result["warnings"]
    elif saved_path and os.path.exists(saved_path):
        entry["size_mb"] = round(os.path.getsize(saved_path) / (1024 * 1024), 2)
        entry["status"] = "ok"
    # Non-verify missing file keeps legacy exit behavior (no failure exit);
    # the manifest still records status 'failed'.
    return entry


def main():
    i18n_init()
    args = _parse_args()

    os.makedirs(args.output, exist_ok=True)

    entries = []
    download_failures = 0
    verify_failures = 0
    for url in args.url:
        entry = _download_one(url, args)
        entries.append(entry)
        if entry["path"] is None:
            download_failures += 1
        elif args.verify and entry["status"] == "failed":
            verify_failures += 1

    # Swap/retire provenance: retired entries move to a top-level manifest
    # `retired[]` list; replacements are tagged swapped_from + swap{date,reason}.
    retired = None
    if args.swap:
        entries, retired = apply_swaps(entries, args.swap, reason=args.swap_reason)

    if args.manifest:
        manifest = build_manifest(entries, tool=_tool_info(args), retired=retired)
        manifest_dir = os.path.dirname(os.path.abspath(args.manifest))
        os.makedirs(manifest_dir, exist_ok=True)
        with open(args.manifest, "w", encoding="utf-8") as f:
            json.dump(manifest, f, ensure_ascii=False, indent=2)
        print(t("cli.manifest_written", path=args.manifest))

    # Exit codes: 0 success, 1 download failure, 2 verification failure.
    if download_failures:
        sys.exit(1)
    if verify_failures:
        sys.exit(2)


if __name__ == "__main__":
    main()
