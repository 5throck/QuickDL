# Spec — Production-Hardened Download Features (quality modes, subtitles, verification, manifest)

- **Date**: 2026-10-29
- **Status**: implemented
- **Origin**: Features validated in an external production batch run (18 videos, 0 failures) that used QuickDL's bundled yt-dlp directly. This spec reflects them back as native QuickDL features. The verification policy itself originates from the **co-deck workspace** — `docs/adr/0002-deck-video-asset-verification-and-injector-binding.md` (volumedetect ≥ −60 dB silence gate, oEmbed/ID identity check, clean per-video download folder, never "newest file") — and was proven in that workspace's 2026-10 18-video production deck run.
- **Scope**: CLI + service layer (`cli.py`, `download_service.py`, new `verification.py`). Web UI (`app.py`, templates, `static/js`) intentionally untouched — `app.py` keeps working via additive keyword arguments with backward-compatible defaults.

---

## 1. Goals

1. **Best-available quality mode** — probe per video for the maximum available height; download with no artificial height cap; prefer h264/aac at equal resolution for browser/device compatibility (never trade resolution for codec); record when the source caps lower (`already-max`).
2. **Subtitle sidecar download** — manual subtitles preferred over auto-generated, configurable language patterns (spoken language first), cleaned WebVTT stored next to the video.
3. **Verification gates** — per-download: file exists & > 1 MB; duration within ±5%; audio mean loudness ≥ −60 dB (not silent); oEmbed title identity; resolution equals probed max (else warn).
4. **Download manifest** — one JSON manifest per batch: per-video record + totals + tool/format info. Makes batches auditable.
5. **ID-keyed filenames** — opt-in `%(id)s.%(ext)s` output template, fixing the "newest-mp4 in temp folder" identity weakness for scripted batches.

## 2. Non-goals

- No web UI changes (frontend wiring of these options is future work; the service layer already exposes the needed parameters).
- No change to existing default behavior (see §4).
- No new third-party dependencies (`ffprobe`/`ffmpeg` invoked as external binaries, already required by QuickDL).

## 3. Design

### 3.1 `download_service.py` (additive, defaults preserve legacy behavior)

- `get_video_info()` additionally returns `height` (max height across `formats`), `duration_sec` (raw seconds), and `id`. Existing keys unchanged → `/api/info` response grows additively; frontend ignores unknown keys.
- `download_video(...)` gains keyword-only-style optional parameters:
  - `quality: Optional[str]` — `None` (default) = exact legacy format string `bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best`; `'best'` = `bestvideo+bestaudio/best` with `format_sort: ['res', 'fps', 'vcodec:avc1', 'acodec:mp4a', 'br']` (sort preference, not a hard filter — never trades resolution for codec) + `merge_output_format: 'mp4'`; `'cap:N'` = same sort plus `[height<=N]` constraints. Invalid values raise `ValueError`.
  - `write_subs: bool = False` with `sub_langs: str = "ko.*,en.*"` — maps to `writesubtitles` + `writeautomaticsub` + `subtitleslangs` + `subtitlesformat: 'vtt/best'`. yt-dlp natively prefers manual subs over auto subs for a requested language when both flags are set. Language pattern order = priority (spoken language first).
  - `id_keyed_names: bool = False` — switches `outtmpl` from `%(title).100s.%(ext)s` to `%(id)s.%(ext)s`.
- Return type stays `str` (the merged `.mp4` path) — `app.py` depends on it.

### 3.2 `verification.py` (new module — post-download gates + manifest schema)

Pure functions with injectable I/O (mirrors the `ydl_class` injection pattern) so tests need no network/binaries:

- `verify_download(path, expected_duration_sec, expected_height, expected_title, video_id, reference_height, run_cmd, fetch) -> dict`
  - Gates: exists & size > 1 MB (hard fail); duration within ±5% of expected (hard fail when both measurable); `ffmpeg -af volumedetect` mean ≥ −60 dB (hard fail; missing ffmpeg → warning); oEmbed title identity vs requested title (hard fail on mismatch, warning when network unavailable); measured height == probed max (warning when lower).
  - Status: `ok` (all gates pass, resolution reached reference/cap), `already-max` (gates pass but the **source** ceiling — probed max — is below the reference height, i.e. nothing better exists), `failed` (any hard gate failed).
  - `reference_height`: for `quality='best'` the CLI passes 1080 (the platform's standard "best" reference — a *reporting* reference only, never a download cap); for `cap:N` it passes N.
- `extract_video_id(url)` — YouTube watch/youtu.be/shorts/embed ID extraction (fallback when probe info lacks `id`).
- `build_manifest(entries, tool) -> dict` — attaches `generated_at` and `totals` (videos/ok/already_max/failed) to the per-video records.
- Subprocess via `subprocess.run(argv, capture_output=True, text=True, timeout=30)` — no shell. oEmbed via `urllib.request` with `timeout=10` against a fixed host.

### 3.3 `cli.py`

- `url` becomes `nargs="+"` (one **or more** URLs — a batch); each URL is downloaded and verified independently; one failed video does not abort the batch.
- New flags (all opt-in): `--quality best|cap:N`, `--write-subs`, `--sub-langs "ko.*,en.*"`, `--manifest PATH`, `--verify`, `--id-names`.
- After each download: discover `.vtt` sidecars next to the output, print status; with `--verify`, print gate results (`cli.verify_failed` / `cli.already_max` / warnings).
- `--manifest PATH` writes UTF-8 JSON (`ensure_ascii=False`, indent 2).
- Exit codes: `0` success; `1` hard download failure (existing semantics, now also when *every* video failed); `2` completed but ≥ 1 video failed verification (new, documented in README).

## 4. Backward compatibility

| Default flow | Before | After |
|---|---|---|
| `python cli.py <URL>` | legacy format string, title-based name | identical (no new flag given) |
| Web UI `/api/download` | legacy `download_video` call | identical call, unchanged behavior |
| `/api/info` response | title/thumbnail/duration/channel | same keys + `height`, `duration_sec`, `id` |

## 5. i18n

13 new `cli.*` keys added to `locales/en.json` and mirrored in all 16 locales (parity enforced by `tests/test_i18n.py::test_all_locales_have_same_keys`). Baseline grows 59 → 72 keys.

## 6. Tests (mocked — no network, no real yt-dlp/ffmpeg calls)

`tests/test_download_service.py` (pytest): fake `ydl_class` capturing `ydl_opts` — legacy defaults unchanged; `best` / `cap:N` option shapes; subtitle options; ID-keyed template; invalid quality → `ValueError`; info dict gains height/id/duration_sec.

`tests/test_verification.py` (pytest): injectable `run_cmd`/`fetch` fixtures — missing/too-small file; duration tolerance edges; silent audio; title mismatch; resolution warning; `already-max` status; manifest totals.

## 7. Acceptance criteria

- All pre-existing tests still pass (14 i18n + 9 app).
- New tests pass; `bash scripts/audit.sh` unchanged except the pre-existing environmental CONSTITUTION.md finding (not caused by this work).
- CLI `--help` renders localized new flags; `QUICKDL_LANG=en python cli.py --help` smoke-checked.
