# Remaining deferred items + Python modernization + bun upgrade — design

- **Spec ID**: 2026-11-22-remaining-deferred-batches-design
- **Status**: Implemented (2026-11-22)
- **Date**: 2026-11-22
- **Builds on**: 2026-11-22-review-remediation-batches-design (user directive: execute the remaining deferred items and upgrade bun)

## 1. Decisions

1. **Python modernization sweep** (floor 3.10 follow-through): `Optional[X]` → `X | None`
   (PEP 604) and `List`/`Dict` → `list`/`dict` (PEP 585) across src/ + tests/
   (78 sites); typing imports pruned to `Callable`. `Callable[..., T]` retained
   (typing) to limit churn. 111 tests pass post-sweep.
2. **M-16**: pre-commit .env regex `[^s]` hole closed — the trailing class becomes `.+`
   (example/sample lookahead already exempts templates); pre-commit.ts 1.14.0 → 1.14.1.
3. **M-17 + M-18**: pre-push.ts 1.9.0 → 1.10.0 — stale CI-job comments corrected to the
   real ci.yml jobs, and a changed-path pytest arm added (push touching tests/*.py runs
   the project suite via the venv python under the existing gitCleanEnvForShell +
   repo-config snapshot guards; absent venv skips silently — CI remains the
   authoritative full-suite gate).
4. **M-20**: .claude/settings.json PostToolUse matcher aligned to the PreToolUse form
   (`Edit|Write|MultiEdit`); `asyncRewake` retained (vendor field — unverified, watch
   on next Claude Code update).
5. **M-15**: .gitignore legacy head block deduped into the WORKSPACE-MANAGED block +
   a minimal QuickDL project block (downloads/, *.part). All critical patterns verified
   present; `.env.sample` now correctly ignored (settled H-12 policy consequence).
6. **M-14**: inline vocabulary carve-out recorded in docs/co-utility.context.md
   Language Policy (quoted locale-specific terms in governance prose are permitted as
   evidence; prose stays English-only) — resolves the finding without touching the
   pipeline-maintained context.md.
7. **bun**: local binary upgraded 1.4.4 → 1.4.5 (`bun upgrade`). CI project jobs don't
   use bun; the template jobs pin their own setup-bun SHA (unchanged).

## 2. Still deferred (upstream-owned)

H-9 (typecheck gate guard — L0 core script), M-4 (template-shipped duplicate
managed-block id), M-10 (VERSION_MANIFEST parity-line semantics — L0 generator),
U-20261119-002 triage.

## 3. Verification

`verify-scripts --verify` 192/192 · `audit --skip-memory` exit 0 · pytest 111 passed ·
bun 1.4.5.
