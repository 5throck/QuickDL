# Python minimum version floor 3.8 → 3.10 — design

- **Spec ID**: 2026-11-22-python-floor-310-design
- **Status**: Implemented (2026-11-22)
- **Date**: 2026-11-22
- **Trigger**: User decision (support-policy change); review finding H-7 (EOL 3.8 leg in CI)

## 1. Problem

QuickDL declares Python 3.8+ while 3.8 went EOL 2024-10: the CI 3.8 leg needed a
pinned ubuntu-22.04 runner (setup-python no longer provisions 3.8 on 26.04), modern
yt-dlp releases target newer Pythons, and the coding guideline banned PEP 604 unions.

## 2. Decision

Raise the minimum supported Python to **3.10** (user-approved 2026-11-22):

- `src/install.py` gate: `(3, 8)` → `(3, 10)`.
- 16 locale files: `install.python_bad` values updated 3.8 → 3.10 (atomic i18n change —
  every locale touched in one change; key trees untouched).
- README.md / README_ko.md: badge, prerequisites, installer description.
- docs/co-utility.context.md: stack table, CI matrix line, setup snippet, coding
  guideline (PEP 604 `X | None` is now the house style; `Optional[str]` still legal).
- `agents/backend.md` (+ .claude mirror): constraint reworded to the 3.10 floor.
- CI matrix: `["3.10", "3.12", "3.14"]` — the 3.8 leg, the ubuntu-22.04 runner pin, and
  the include/exclude pair are removed; 3.14 added (verified locally: 111 tests pass on
  3.14.10).

## 3. Non-goals

Bulk code modernization (`Optional[str]` → `str | None` sweep) — incremental, on touch.

## 4. Verification

`bun scripts/audit.ts --skip-memory` exit 0; `pytest tests/ -q` 111 passed (3.14.10);
CI on push runs the new matrix (Actions enabled 2026-11-22).
