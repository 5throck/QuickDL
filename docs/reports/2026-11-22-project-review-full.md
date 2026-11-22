# Project Review — QuickDL — 2026-11-22

**Date**: 2026-11-22
**Scope**: full (T-01 user request) — 4 paired domain slots, parallel Explore agents
**Method**: 4 parallel agents (Architecture+Scaffolding / Standards+Lifecycle / Automation / Docs+Security) + machine battery
**Project**: QuickDL — co-utility variant (L3), HEAD bd22a17 (post-rebase, post-merge of PR #48)

> Fixes for the Critical set and quick-win High items were applied in-session (see Verification); the remaining High/Moderate items are deferred with wiring recorded below.

## Machine Baseline (Step 0)

| Validator | Result |
|-----------|--------|
| `bun scripts/audit.ts` | ✅ All checks passed (2 skipped) |
| `pytest tests/ -q` | ✅ 111 passed |
| `gitleaks detect --no-git --redact` | ✅ no leaks (33.7 MB scanned) |
| `trail check` | ✅ no conflicts |
| `bun run test:unit` | ⚠️ vacuously green — see High H-8 |

Baseline shows <3 ERRORs → no T-03 pre-triage required; agent dispatch proceeded for non-machine-detectable classes.

## Findings — cross-domain dedup (4 raw reports merged)

Discoverers credited per finding; duplicates merged to the most specific file:line and highest severity.

### 🔴 Critical (fix immediately)

| # | Issue | Agent | File:Line | Class | Fix |
|---|-------|-------|-----------|-------|-----|
| C-1 | `.claude/settings.local.json` git-tracked (broad personal grants incl. `git push *`, `gh repo *`; stale Windows paths) — ignore rule ineffective for tracked files | Docs+Sec | `.claude/settings.local.json` | script-gap | ✅ fixed: `git rm --cached`; validator-hardening note recorded (audit lacks tracked-vs-ignored contradiction check) |
| C-2 | CI i18n audit reads nonexistent root `locales/en.json` → `test` job red on every run since the src/ move | Automation + Docs+Sec | `.github/workflows/ci.yml:194` | script-gap | ✅ fixed → `src/locales/en.json`; validator-hardening note recorded |
| C-3 | `variant.json` identity drift: description still names the co-develop 7-agent roster; `agents[]` omitted `pm` while every other roster surface includes it | Arch + Std | `variant.json:2,17-38` | one-time | ✅ fixed: utility description; `pm` added (6 entries) |
| C-4 | `agents/i18n-specialist.md` frontmatter: `variant: co-develop`, `phases: [5]` contradicting AGENTS.md Phase 3 / phase-definitions / body; dead "constitution §4.x" citations to the archived file | Std | `agents/i18n-specialist.md:7,11-12,44,101,151,154` | one-time | ✅ fixed: variant co-utility, phases [3,4], citations → doctrine pointers |
| C-5 | i18n baseline key count "56" in the customization layer vs 78 actual (parity is load-bearing for locale work) | Std + Arch | `docs/co-utility.context.md:87,249` | one-time | ✅ fixed: hardcoded count dropped; parity SSOT pointed at `tests/test_i18n.py` |
| C-6 | Live command surfaces invoke archived scripts: `/sync` command (`.claude`/`.gemini`/`.codex`) ran `dev-sync.sh`; `agents/qa.md` + PR template ran `audit.sh` | Automation + Docs+Sec | `.claude/commands/sync.md:32`, `.gemini/commands/sync.md:20,32`, `.codex/prompts/sync.md:32`, `agents/qa.md:56`, `.github/pull_request_template.md:16` | systemic | ✅ fixed → `bun scripts/dev-sync.ts` / `bun scripts/audit.ts --skip-memory` |

### 🟡 High (deferred — wiring below)

| # | Issue | Agent | File:Line | Class | Wiring |
|---|-------|-------|-----------|-------|--------|
| H-1 | `ytdl.bat` failure path: cmd parse-time `%MSG%` expansion shows empty message; missing th/ru/it/ar locales vs `ytdl.sh`; no `setlocal`/`exit /b 1`; no `chcp 65001` (launcher-pairing doctrine violation) | Arch + Auto | `ytdl.bat:8-23` vs `ytdl.sh:22-41` | systemic | Deferred: launcher rewrite (needs a deliberate Windows-encoding decision). Recorded below |
| H-2 | `procedures/` 6 schemas dispatch archived agents (`stack-setup`, `security-monitor` owner keys) | Std | `procedures/*/schema.yaml` | systemic | Deferred: co-utility procedure regeneration pass |
| H-3 | `docs/skill-graph.json` carries co-develop skill/procedure placeholder nodes as catalog entries; verifier passes | Std | `docs/skill-graph.json:162-217` | script-gap | Deferred: generator tombstone-marker support |
| H-4 | Skill lifecycle records: 10 tombstoned skills still `Status: active` with false acceptance criteria; `post-write-check` (the only variant-exclusive skill) has no record; 7 records cite unresolvable `templates/common` paths | Std | `docs/lifecycle/skills/` | systemic | Deferred: lifecycle-record regeneration pass |
| H-5 | Stale agent references in platform docs + dead AGENTS.md §-anchors (`#1-agent-ecosystem-overview`, `#36-3-tier-strategy`; `automation-engineer`/`code-writer` as common agents; HERMES specialist list; GEMINI `test-runner` example) | Std + Docs+Sec | `CLAUDE.md:250-266`, `HERMES.md:11,43-47`, `GEMINI.md:84-97`, `agents/frontend.md` | systemic | Partial ✅: `frontend.md`/`pm.md` routes fixed this session; platform-docs anchor sweep deferred |
| H-6 | Agent lifecycle records stale: pre-rebase PM record, no co-utility re-base entries, generic i18n-specialist stub | Std | `docs/lifecycle/agents/*.md` | systemic | Deferred: lifecycle-record refresh pass |
| H-7 | CI `test` job uses floating action tags (`checkout@v4`, `setup-python@v5`) vs SHA-pinned template jobs; Python 3.8 leg is EOL | Auto + Docs+Sec | `.github/workflows/ci.yml:174,177,180` | systemic | Deferred: CI supply-chain alignment |
| H-8 | `test:unit` package script runs 0 tests (no `tests/unit/`) → vacuously green CI job | Auto | `package.json:8`, `scripts/test-runner.ts:229` | script-gap | Deferred: decide remove-vs-populate |
| H-9 | Typecheck gate structurally inactive (`CONSTITUTION.md` guard false; no baseline file) while the sync skill cites it as a merge predicate | Auto | `scripts/dev-sync.ts:1697`, `scripts/typecheck.ts:40-52` | script-gap | Deferred: gate decision (ship baseline vs amend skill text) |
| H-10 | Flask binds `0.0.0.0:5000` while docs promise a localhost app; CORS/SSRF posture assume localhost | Arch + Docs+Sec | `src/app.py:184` | one-time | Deferred: behavior change — needs owner decision on LAN access (`QUICKDL_HOST` override proposed) |
| H-11 | `nocheckcertificate: True` disables TLS verification for every download (MITM swaps attest by `--verify`) | Docs+Sec | `src/download_service.py:411` | one-time | Deferred: opt-in flag design (behavior change) |
| H-12 | `.env.sample` tracked again (re-added post-untrack) + `!.env.sample` in managed gitignore block + gitleaks allowlists its path — three surfaces disagree | Docs+Sec | `.gitignore:2-3,69`, `.gitleaks.toml:~36` | systemic | Deferred: settle policy once (untrack + drop allowlist recommended) |
| H-13 | qa write-phase inconsistent across AGENTS.md dispatch table (Phase 3) vs workflow block (Phase 4) vs phase-definitions (Phase 1+4) | Std | `AGENTS.md:52-59,84-85`, `docs/phase-definitions.md:15-18` | systemic | Deferred: dispatch-model alignment pass (with H-6) |

### 🟢 Moderate (deferred)

| # | Issue | Agent | Class |
|---|-------|-------|-------|
| M-1 | Doctrine says output roots "never `__file__`-relative" but code is `src/`-anchor-based — wording now aligned ✅ (M-2 merged) | Arch | one-time ✅ |
| M-2 | Root `__pycache__/` bytecode residue of the flat layout | Arch | one-time ✅ (removed) |
| M-3 | Hardcoded Korean connector word meaning "or" leaks into every locale's installer completion output (`src/install.py:116,119`) | Arch | one-time — deferred |
| M-4 | Duplicate `WORKSPACE-MANAGED: tier-model-mapping` block ID in AGENTS.md | Arch | script-gap — deferred |
| M-5 | `locale.getdefaultlocale()` deprecation (live Python 3.15 user; silent always-`en` on removal) | Arch | one-time — deferred |
| M-6 | `GEMINI.md:22` example path `@locales/en.json` → `src/locales/en.json`; `variant.json` description override (fixed this session ✅) | Arch | one-time ✅ |
| M-7 | `memory/MEMORY.md` double index headings; 11-19 row summary misleading; missing 05-25 tombstone row | Std | one-time — deferred |
| M-8 | `docs/project.md` identity seed TODO | Std | one-time ✅ (filled) |
| M-9 | CHANGELOG has no entry for the src/ layout move / co-utility rebase | Std | one-time ✅ (added) |
| M-10 | VERSION_MANIFEST "all four mirrors: 0/37" parity line reads false (generator-consistent but misleading) | Std | script-gap — deferred |
| M-11 | i18n-specialist routes to phantom k-* skills and co-deck font doctrine without variant qualification | Std | systemic — deferred |
| M-12 | SSRF filter bypassable via DNS names / non-canonical IP forms (`src/app.py:33-46`) | Docs+Sec | one-time — deferred (resolve-hostname hardening) |
| M-13 | SECURITY.md Supported Versions table vacuous (`Latest —`) | Docs+Sec | one-time — deferred |
| M-14 | Korean vocabulary examples in English-only core docs (CLAUDE/GEMINI/CODEX/context) outside the sanctioned zone | Docs+Sec | systemic — deferred (needs policy carve-out decision) |
| M-15 | `.gitignore` internally duplicated (manual vs WORKSPACE-MANAGED blocks) with contradictions | Docs+Sec | systemic — deferred (ties to H-12) |
| M-16 | pre-commit `.env` regex `[^s]` hole (`.env.secrets` class) | Auto | script-gap — deferred |
| M-17 | pre-push comments reference nonexistent CI jobs | Auto | one-time — deferred |
| M-18 | Python test suite never runs in local gates (CI-only) | Auto | script-gap — deferred (deliberate-choice) |
| M-19 | `.codex/hooks.json` lacks hooksPath enforcement (fresh Codex-only clone bypasses hooks) | Auto | systemic — deferred |
| M-20 | `.claude/settings.json` matcher drift (`MultiEdit` in PreToolUse only) + unverified `asyncRewake` field | Auto | one-time — deferred |
| M-21 | qa.md contradictory test counts (23 vs 111; static `def test_` = 102) | Auto | systemic ✅ partial (audit.sh line fixed; counts deferred) |
| M-22 | Stale `.claude/settings.local.json` allowlist entries (archived scripts, dead Windows paths) | Auto | one-time (file now untracked — local cleanup) |

### ℹ️ Low / Improvements

- `scripts/_legacy/GEMINI.md:161` mojibake `쨌` in inert tombstone (Docs+Sec) — leave as history.

### ✅ Strengths (verified)

- All post-restructure path assumptions hold (Flask discovery, install ROOT, CLI output, i18n locales — programmatically verified).
- Skills SSOT parity byte-perfect across 5 platform mirrors (37/37); command mirrors 7/7/7.
- Agent mirrors correctly generated (tier→model alias transform by design, 6/6 tracked).
- Test-count claims true everywhere ("111" verified via `pytest --collect-only`).
- Locale matrix integrity: 16 locales × 78 keys, parity verified programmatically for every file.
- Runtime-output isolation holds in git (downloads/, .venv/ clean).
- hooksPath enforcement wired (Claude/Gemini SessionStart + WorktreeCreate); hook wrappers thin, fail-loud, gitleaks config pass on pre-rebase.
- CI least privilege (`contents: read`, digest-pinned template jobs, `persist-credentials: false`), secret scanning fail-closed with memory/ deliberately scannable.
- `/api/file/<id>` path traversal well-contained (uuid4 job ids + basename + send_from_directory + one-time pop); CORS regex anchored localhost-only.
- Trail wiring verified end-to-end; settings.json deny list blocks force-push/no-verify/rm -rf.

## Domain summary

| Slot | Critical | High | Moderate | Strengths |
|------|----------|------|----------|-----------|
| A: Architecture + Scaffolding | 0 | 2 | 9 | 8 |
| B: Standards + Lifecycle | 3 | 8 | 6 | 7 |
| C: Automation | 2 | 3 | 8 | 6 |
| D: Documentation + Security | 1 | 8 | 10 | 10 |
| **After dedup** | **6** | **13** | **22** | shared |

Root cause pattern: the 2026-11-19 rebase (co-develop → co-utility + src/ move) updated the primary surfaces but left a residue tail in secondary surfaces (commands, procedures, lifecycle records, platform-doc prose, CI paths). Classification: most residue is `systemic` (multi-surface replication needing a sweep pass), several are `script-gap` (machine-detectable classes with no standing check), the rest `one-time`.

## Action wiring (Step 5)

In-project (ticket.ts is L0-only; deferred items recorded here + memory log per variant-project rule):

- **Fixed this session (Step 6 verified)**: C-1…C-6, M-2, M-6, M-8, M-9, M-1(wording), partial H-5 (frontend/pm routes), partial M-21 (audit.sh line).
- **Deferred batch "rebase-residue sweep"** (one coordinated pass): H-2, H-3, H-4, H-6, H-13, H-5 remainder, M-4, M-7, M-10, M-11, M-21 counts.
- **Deferred batch "launcher/CI hardening"**: H-1, H-7, H-8, H-9, M-16, M-17, M-18, M-19, M-20.
- **Deferred batch "security posture"** (needs owner decisions): H-10 (bind host), H-11 (nocheckcertificate), H-12 (.env.sample policy), M-12 (SSRF), M-13 (SECURITY.md), M-14 (language carve-out), M-15 (gitignore dedupe).
- **Validator-hardening notes** (ratchet — for the workspace upstream backlog, complementing U-20261119-002): tracked-vs-ignored contradiction check (C-1), CI-referenced-path existence check (C-2), tombstone markers in skill-graph generator (H-3), managed-block duplicate-ID check (M-4), .env regex `[^s]` hole (M-16), VERSION_MANIFEST parity-line semantics (M-10), pytest-in-local-gate option (M-18).

## Verification (Step 6)

Applied in-session fixes; re-ran every touched domain's gate:

| Gate | Result |
|------|--------|
| `bun scripts/audit.ts --skip-memory` | ✅ All checks passed |
| `pytest tests/ -q` | ✅ 111 passed |
| Regenerated: VERSION_MANIFEST (6 agents/37 skills), agent mirrors (qa.md), skill-graph | ✅ |
