# Spec — Caption Coverage Gate, Cleaning Pipeline & Swap/Retire Provenance (co-deck rounds 7–8)

- **Date**: 2026-10-30
- **Status**: implemented
- **Origin**: Third validated round from the **co-deck workspace** deck-video pipeline — ADR-0002 amendments, rounds 7–8 (`docs/adr/0002-deck-video-asset-verification-and-injector-binding.md`). Round 7: a chosen video's source captions covered only 0:00–5:22 of an 8:50 video — an invisible defect until a client watched past 5:22 — so the batch measured cue coverage, swapped in a replacement, and recorded the retirement; raw YouTube ASR grabs were turned into clean cue files with a tag-strip + rolling-dedup + overlap-clip pipeline (e.g. a raw grab became a clean 424-cue file). Round 8: the swap/retire records and cleaned sidecar metadata were finalized in the production video-manifest.
- **Scope**: `verification.py`, `download_service.py`, `cli.py`, tests, locales, docs. Web UI intentionally untouched (additive keyword arguments / flags only; defaults preserve legacy behavior).

---

## 1. Goals

1. **Caption duration-coverage gate** — measure each caption sidecar against the video duration and surface partial captions (`coverage` 0–1 in the manifest, warn below 0.95 by default, strict opt-in failure).
2. **Caption cleaning pipeline** — every downloaded sidecar is automatically cleaned (tag-strip → rolling-dedup → overlap-clip) before being finalized; the manifest records the cleaning metadata.
3. **Swap/retire provenance** — a batch that replaces a video records the full audit trail: the old entry moves to a top-level `retired[]` list (date + reason) and the replacement is tagged `swapped_from`.

## 2. Non-goals

- No web UI changes.
- No change to existing default behavior when the new flags are omitted: plain batches keep the exact previous manifest schema (no `retired` key, no coverage warnings without sidecars, byte-identical downloads).
- No re-download / automatic replacement logic: the swap directive is owner-supplied (`--swap`); QuickDL records provenance, it does not choose replacements.

## 3. Design

### 3.1 `verification.py` (additive)

- `CAPTION_COVERAGE_THRESHOLD = 0.95`, `DEFAULT_SWAP_REASON = 'replaced via --swap'`.
- `parse_vtt_last_cue_end(vtt_path)` — scans every WebVTT `-->` timing line (`HH:MM:SS.mmm` or `MM:SS.mmm`) and keeps the MAXIMUM end timestamp, so shuffled/overlapping blocks still yield the true last coverage point; None when unreadable or cue-less.
- `caption_coverage(vtt_path, duration_sec)` — `min(last_cue_end / duration, 1.0)`, rounded; None when duration or cues are unknown ('unknown' is reported, never guessed).
- `annotate_caption_coverage(subtitles, duration_sec, threshold)` — mutates manifest `subtitles[]` entries in place (`coverage` field on path-bearing entries) and returns one warning string per entry measurably below the threshold.
- `verify_download(..., subtitles=None, require_caption_coverage=False, caption_coverage_threshold=0.95)` — Gate 6: when `subtitles` is given, coverage is annotated (duration preference: ffprobe-measured, falling back to the probed expectation) and below-threshold coverage is recorded in `warnings`; `checks.caption_coverage_ok` reflects the aggregate (False also for `source: 'failed'` records — no captions is certainly below coverage). With `require_caption_coverage`, below-threshold sidecars and `failed` records become hard failures (exit code 2 via the existing verify-failure path). When no duration is available at all the gate reports "could not be evaluated" as a warning and does NOT fail — honest, not guessed.
- `apply_swaps(entries, swaps, reason, today)` — for each `(old_id, new_url)`: the entry whose `id` matches the old video is removed from `entries` and appended to the returned `retired` list (`video_id`, `title`, `url`, `path`, `size_mb`, `duration_min`, `status`, `retired` date, `reason`); the replacement entry (matched by URL) gains `swapped_from: <old_id>` and `swap: {date, reason}`. Directives whose old id is not in the batch are ignored.
- `build_manifest(entries, tool, retired=None)` — the top-level `retired` key is present ONLY when the parameter is not None.

### 3.2 `download_service.py` (additive)

- `parse_vtt_cues(raw)` — WebVTT → cues `{start, end, text}` (ms): tag-strips text (`html.unescape` + markup regex), drops empty/markup-only cues, skips `NOTE`/`STYLE`/`REGION` blocks and cue-identifier lines (a standalone line directly followed by a timing line).
- `dedup_rolling_cues(cues)` — drops consecutive duplicate cue texts (YouTube rolling-window ASR), merging windows by extending the previous cue's end so no caption time is lost.
- `clip_cue_overlaps(cues, floor_ms=500)` — clips each cue's end at the next cue's start with a 500 ms minimum window, so players never stack two cues.
- `format_vtt(cues)` / `clean_vtt(raw)` — render / full pipeline.
- `clean_sidecar(vtt_path)` — cleans a downloaded sidecar IN PLACE (the raw grab is transient) and returns the final cue count; None when unreadable (file left untouched, manifest entry simply gets no cleaned/cues fields).
- Note: the VTT cue-line regex is intentionally duplicated in `verification.py` (coverage parse) and `download_service.py` (cleaning parse) — both modules stay dependency-free of each other (verification keeps its injectable-deps standalone contract).

### 3.3 `cli.py`

- New flags: `--require-caption-coverage` (store_true), `--swap OLD_ID:NEW_URL` (repeatable; argparse `type` validates the `OLD_ID:NEW_URL` shape — URLs contain colons, so only the FIRST colon splits), `--swap-reason TEXT`.
- Subtitle flow: each discovered sidecar is cleaned (`clean_sidecar`) BEFORE its manifest entry is built; entries gain `cleaned: true` + `cues: <count>` when cleaning succeeded.
- Coverage wiring: with `--verify`, the entries are passed into `verify_download` (measured duration; strict gate with `--require-caption-coverage`); without `--verify`, `annotate_caption_coverage` runs against the probe duration and appends warnings to the entry.
- Batch flow: when `--swap` directives are given, `apply_swaps` runs over the finished entries and the manifest gains `retired[]`; `tool` info records `require_caption_coverage`, `caption_coverage_threshold`, and (with swaps) `swaps` (the exact directives) + `swap_reason`.

### 3.4 Manifest schema (additive)

```
videos[].subtitles[].coverage      # 0–1 | null — last cue end ÷ video duration
videos[].subtitles[].cleaned       # true — sidecar cleaned in place
videos[].subtitles[].cues          # final cue count after cleaning
videos[].swapped_from              # <old_id> — set on the replacement entry
videos[].swap                      # {date, reason}
retired[]                          # top-level, only when --swap was used
tool.require_caption_coverage, tool.caption_coverage_threshold
tool.swaps, tool.swap_reason       # only when --swap was used
```

## 4. Backward compatibility

| Flow | Before | After |
|---|---|---|
| `python cli.py <URL>` (no new flags) | manifest `{generated_at, tool, videos, totals}` | identical (no coverage annotation without sidecars + duration; no `retired` key) |
| `--write-subs` (no new flags) | raw sidecar VTT written; `subtitles[]` `{path, lang, source}` | sidecar now CLEANED in place (the improvement is the point — raw YouTube ASR grabs are display-broken); entries additionally gain `cleaned`/`cues`/`coverage` |
| `--write-subs --verify` | gates 1–5 | gates 1–5 + coverage warning (never a failure unless `--require-caption-coverage`) |
| Web UI `/api/download` | `download_video` call | identical (cleaning lives in the CLI's manifest flow; service-layer functions are opt-in) |

## 5. i18n

3 new `cli.*` keys (`cli.help_require_caption_coverage`, `cli.help_swap`, `cli.help_swap_reason`) mirrored in all 16 locales (parity enforced by `tests/test_i18n.py`). Baseline grows 75 → 78 keys. Help strings avoid bare `%` (argparse `%`-interpolation), so the threshold is written as `0.95` (matching the manifest `coverage` field semantics).

## 6. Tests (mocked — no network, no real yt-dlp/ffmpeg calls)

`tests/test_verification.py` (+16): last-cue-end parsing (max-of-ends, `MM:SS` support, missing file), coverage ratio/clamp/None semantics, verify-gate annotation + warning (status stays 'ok'), full-coverage no-warning, strict failure, `failed`-source strict failure + warn-only variant, unevaluable-coverage (no duration) warns but never fails, `caption_coverage_ok` None without subtitles, non-verify `annotate_caption_coverage` (custom threshold included), `apply_swaps` (retire + tag, default reason/date, unknown old id ignored), `build_manifest` retired[] inclusion/omission.

`tests/test_download_service.py` (+10): cue parsing (tag strip, NOTE/STYLE blocks, cue ids, markup-only drop, `MM:SS`), rolling dedup with window merge, overlap clipping with 500 ms floor, full `clean_vtt` pipeline output, empty-input header-only VTT, `clean_sidecar` in-place rewrite + missing-file None.

## 7. Acceptance criteria

- Full suite green (85 pre-existing + 26 new = 111 passing; the 1 warning is the pre-existing `test_app.py` background-thread teardown race).
- `bash scripts/audit.sh` unchanged except the pre-existing environmental `CONSTITUTION.md` finding.
- `--help` renders the localized new flags (en + ko smoke-checked).
