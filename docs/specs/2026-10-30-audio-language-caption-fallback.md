# Spec — Original-Audio Forcing & Caption Fallback Chain (co-deck rounds 4–6)

- **Date**: 2026-10-30
- **Status**: implemented
- **Origin**: Second validated round from the **co-deck workspace** deck-video pipeline — ADR-0002 amendments, rounds 4–6 (`docs/adr/0002-deck-video-asset-verification-and-injector-binding.md`). Round 4: caption language selection config + YouTube auto-translated sidecars with a `manual | auto | translated` source vocabulary. Round 5: original-audio forcing after YouTube auto-dubbing delivered real production failures (an English seminar downloaded with Japanese audio; a Korean news clip with Korean-dubbed audio). Round 6: an external LLM translation fallback for languages the translation endpoint 429s.
- **Scope**: `download_service.py`, `cli.py`, tests, locales, docs. Web UI intentionally untouched (`app.py` keeps working via additive keyword arguments with backward-compatible defaults).

---

## 1. Goals

1. **Original-audio forcing (anti-dubbing)** — never let YouTube auto-dubbing silently replace a video's spoken audio: probe each video's audio-track languages, default to the ORIGINAL track when multiple dub tracks exist, allow forcing a code, and stamp the language tag into the merged MP4.
2. **Caption language configuration** — request BOTH configured languages per video (gap-fill, not first-found) and record each sidecar with its own language and acquisition source.
3. **Translated-caption acquisition with honest fallback chain** — manual → auto-generated → YouTube auto-TRANSLATED captions → `failed`; no silent omissions, no fake sources.
4. **External-translation readiness** — document (not implement) that a robust pipeline should drive an external translation step off the manifest's `failed` records, because YouTube's translation endpoint rate-limits (429).

## 2. Non-goals

- No actual translation implementation (round 6's LLM cue-for-cue translation stays in the consumer pipeline; QuickDL provides acquisition + honest tagging).
- No web UI changes.
- No change to existing default behavior when the new flags are omitted (legacy format string, legacy subtitle pattern string, no postprocessor args).

## 3. Design

### 3.1 `download_service.py` (additive, defaults preserve legacy behavior)

- `format_for_quality(quality, audio_lang=None)` — when `audio_lang` is set, the FIRST alternative of the quality selector gains `bestaudio[language^=<code>]` (filters are ANDed by yt-dlp regardless of position); the remaining alternatives stay unchanged as graceful fallback for videos offering no matching track. With `audio_lang=None` all returned strings are byte-for-byte identical to before.
- `probe_audio_languages(info_dict)` — distinct audio-track language codes from `audio_tracks` entries and audio-bearing formats (`acodec != 'none'`), first-appearance order.
- `select_original_audio_language(info_dict, audio_languages)` — original spoken language: a track flagged `audio_is_original` → highest `language_preference` → video-level `language` → single available track → None.
- `resolve_audio_language(mode, info)` — `'auto'`/None → probed original; any other value passes through verbatim.
- `plan_caption_sources(requested_langs, manual_langs, auto_langs)` — the fallback chain, one plan item per requested language: `manual` (native manual subs) → `auto` (native auto captions) → `translated` (YouTube translation key `<src>-<dst>` targeting the language; explicit translation-shaped requests pass through) → `failed` (nothing offered; not requested at all). When the probe exposes no caption data at all (both lists None) items are `unknown` with the original request so legacy behavior holds; when only `automatic_captions` is missing, auto availability is treated as unknown and the native request is attempted.
- `classify_sidecar_token(token)` / `subtitle_entry(vtt_path, saved_path, plan)` — manifest `subtitles[]` records `{path, lang, source}`; the plan entry whose request exactly matches the file's language token wins (the plan is computed from a fresh probe moments before the download), otherwise shape classification (`-orig` → auto, lowercase `xx-yy` pair → translated, else `unknown`). yt-dlp filenames cannot distinguish a fetched manual from an auto track for the same code — the plan-time source is recorded (honest best available at request time).
- `get_video_info()` additionally returns `audio_languages`, `original_audio_lang`, `manual_caption_langs`, `auto_caption_langs` (None when the extractor did not expose caption data) — existing keys unchanged.
- `download_video(..., audio_lang=None)` — with `audio_lang` set, adds `postprocessor_args = ['-metadata:s:a:0', 'language=<code>']` (a plain list applies to all ffmpeg postprocessor invocations; the merge/remux writes the stream language tag into the MP4).

### 3.2 `cli.py`

- New flags: `--audio-lang` (default `auto`), `--captions-langs "ko,en"` (implies `--write-subs`).
- Per video: resolve `--audio-lang` → concrete code; manifest entry gains `audio_language`, plus `audio_languages_available` when the video offers multiple audio languages; a multi-language video whose original cannot be determined, or a forced code the video does not offer, records a manifest warning (printed warnings unchanged).
- Caption plan: requested codes come from `--captions-langs` (plain codes) or the `--sub-langs` patterns reduced to codes (`ko.*` → `ko`); when the probe exposed caption data the resolved request list (including `<src>-<dst>` translations) replaces the pattern string, `failed` languages are not requested, and `subtitles[]` records each discovered sidecar plus a `failed` record (`path: null`) for every unfetchable language. With no probe data the legacy pattern string passes through byte-for-byte.
- `--manifest` tool info gains `audio_lang` and `captions_langs`.

### 3.3 Manifest schema (additive)

```
videos[].audio_language            # "ko" | null — resolved original/forced audio code
videos[].audio_languages_available # ["ko","ja"] — only when the video offers multiple
videos[].subtitles[]               # {path, lang, source}; source ∈ manual|auto|translated|failed|unknown
tool.audio_lang, tool.captions_langs
```

## 4. Backward compatibility

| Flow | Before | After |
|---|---|---|
| `python cli.py <URL>` | legacy format string, title name | format selector identical UNLESS the probe detects an audio language: `--audio-lang auto` (default) then adds `bestaudio[language^=<original>]` to the first alternative (matches the video's only/original track; graceful fallback kept) and stamps the language tag. This is the intended anti-dubbing default. The service layer keeps byte-identical behavior when `audio_lang=None`. |
| `--write-subs --sub-langs` | pattern string passed to yt-dlp | identical when probe data is absent; when present, resolved per-language requests (superset of the same languages, plus honest failed records) |
| Web UI `/api/download` | `download_video` call | identical (new kwargs default to legacy behavior) |

## 5. i18n

3 new `cli.*` keys (`cli.help_audio_lang`, `cli.help_captions_langs`, `cli.audio_lang`) mirrored in all 16 locales (parity enforced by `tests/test_i18n.py`). Baseline grows 72 → 75 keys.

## 6. Tests (mocked — no network, no real yt-dlp/ffmpeg calls)

`tests/test_download_service.py`: language-filter injection into all three quality selectors (and byte-identity without it); `audio_is_original` / `language_preference` / video-language original selection; `resolve_audio_language`; `postprocessor_args` presence/absence; caption plan for manual / auto / translated / failed / unknown / auto-unknown / explicit-translation-request / per-language independence; sidecar tagging by plan match and token shape.

`tests/test_verification.py`: manifest passthrough of `audio_language`, `audio_languages_available`, and object-shaped `subtitles[]` (including `failed` records), plus legacy-shaped entries still tallying.

## 7. Acceptance criteria

- Full suite green (60 pre-existing + new tests; 85 passing after this round).
- `bash scripts/audit.sh` unchanged except the pre-existing environmental `CONSTITUTION.md` finding.
- `--help` renders the localized new flags (en + ko smoke-checked).
