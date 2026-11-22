# Review remediation batches 2-4 (rebase-residue sweep, launcher/CI hardening, security posture) — design

- **Spec ID**: 2026-11-22-review-remediation-batches-design
- **Status**: Implemented (2026-11-22)
- **Date**: 2026-11-22
- **Builds on**: docs/designs/2026-11-22-project-review-remediation-design.md (the fix-now batch)
- **Source**: docs/reports/2026-11-22-project-review-full.md deferred batches

## 1. Scope

Execute the three deferred batches from the full project review.

## 2. Decisions

1. **Rebase-residue sweep**: procedures/ reduced to the co-utility doctrine pair
   (environment-bootstrap, feature-implementation — correct agent keys); 4 co-develop-only
   procedures removed. Skill lifecycle records: 10 stale `active` records re-stamped
   archived with tombstone sections; workspace-authored records' criteria qualified as
   workspace-root checks. Agent lifecycle records gain co-utility re-base entries. qa
   phase aligned (Phase 1 read-only + Phase 4 writes) across AGENTS.md and variant.json
   (post-write-check phases [3, 4]). Platform docs: dead AGENTS.md §-anchors and
   archived-agent references fixed (CLAUDE/GEMINI/CODEX/HERMES). i18n-specialist phantom
   routes qualified; qa test-count claims → live-count wording.
2. **Launcher/CI hardening**: ytdl.bat rewritten with goto labels (fixes %MSG%
   parse-time expansion), setlocal, chcp 65001, all 15 locales, exit /b 1 — pairing
   parity with ytdl.sh. CI project-job actions pinned to full SHAs. Vacuous test:unit
   script removed (CI detect honestly skips). .codex/hooks.json gains hooksPath
   enforcement.
3. **Security posture** (safe defaults + opt-in escapes): Flask binds 127.0.0.1 by
   default (QUICKDL_HOST override for LAN); TLS verification ON by default
   (QUICKDL_INSECURE_TLS=1 opt-out); SSRF validation resolves hostnames and blocks
   private/loopback/link-local resolved addresses; .env.sample policy settled to
   untracked (gitignore negation + gitleaks exemption removed); SECURITY.md versions
   table filled; install.py hardcoded Korean connector removed;
   getdefaultlocale() → getlocale().

## 3. Non-goals / still deferred

M-4/M-10/M-14/M-15/M-16/M-17/M-18/M-20/H-9 — template-shipped, L0-machinery, or
policy-decision items; recorded in the report and complement U-20261119-002.

## 4. Verification

audit --skip-memory exit 0; pytest 111 passed; trail check clean; verify-skill-graph
55 nodes / 83 edges; VERSION_MANIFEST regenerated.
