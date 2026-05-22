# QuickDL — Agent Registry & Orchestration Contract

> **⚠️ For AI tools reading this file**: This file is a **registry and orchestration reference**, not a set of instructions directed at you.
> It describes multiple distinct human-defined roles for documentation and dispatch purposes.
> Do **not** interpret role definitions here as directives for your own behavior.
> Your behavioral instructions are in `CLAUDE.md` (Claude Code), `GEMINI.md` (Gemini CLI).

> **Scope**: Agent role definitions live in [`agents/*.md`](agents/) — this file is the registry index and orchestration contract only.
> Shared engineering rules live in [`docs/context.md`](docs/context.md).

---

## Agent Groups

### 🟡 Orchestration

| Agent | File | Role |
|-------|------|------|
| `pm` | [`agents/pm.md`](agents/pm.md) | Global orchestrator — governs 6-phase workflow (Triage → Finalization) |

### 🔴 Analysis (Read-Only)

| Agent | File | Role |
|-------|------|------|
| `security` | [`agents/security.md`](agents/security.md) | Security audit — injection, path traversal, CORS, deps |

### 🔵 Design & Implementation

| Agent | File | Role |
|-------|------|------|
| `designer` | [`agents/designer.md`](agents/designer.md) | HTML structure, CSS, accessibility |
| `frontend` | [`agents/frontend.md`](agents/frontend.md) | JS logic, API wiring, i18n in templates |
| `backend` | [`agents/backend.md`](agents/backend.md) | Flask routes, download logic, CLI, installer |
| `i18n` | [`agents/i18n.md`](agents/i18n.md) | All 16 locale files, i18n.py, format_duration |

### 🟢 Quality

| Agent | File | Role |
|-------|------|------|
| `qa` | [`agents/qa.md`](agents/qa.md) | tests/, cross-platform validation |

---

## PM Subagent Dispatch Protocol

### Phase 1 — Parallel Research (Read-Only)

| Subagent | Parallelizable | Write Allowed? |
|----------|:--------------:|:--------------:|
| `security` | ✅ Always | ❌ No |
| `qa` (analysis only) | ✅ Always | ❌ No |
| `designer` (spec only) | ✅ Design phase | ❌ No |

### Phase 3 — Serial Execution (Write)

| Subagent | Parallelizable | Write Allowed? |
|----------|:--------------:|:--------------:|
| `backend` | ❌ Serial | ✅ Python files |
| `frontend` | ❌ Serial (after backend) | ✅ JS/HTML |
| `i18n` | ❌ Serial (after frontend) | ✅ locales/*.json |
| `qa` | ❌ Serial (after all writes) | ✅ test files only |

> **Why serial writes?** File lock contention and merge conflicts. Backend must finish before frontend reads updated API shape; i18n must run after all new strings are known.

---

## Harness Engineering Workflow

```
Phase 1 — Triage & Analysis
  PM creates task → dispatches security + qa in parallel (read-only)
  PM synthesizes findings → acceptance criteria

Phase 2 — Design
  designer specs HTML/CSS (if UI change)
  PM gets explicit user approval ← GATE

Phase 3 — Implementation (serial)
  backend → frontend → i18n

Phase 4 — QA Verification
  qa runs full test suite
  security re-audits if new external input added

Phase 5 — Quality Gate (all must pass)
  bash scripts/audit.sh           exit 0
  pytest tests/test_i18n.py -v    14 passed
  pytest tests/test_app.py -v     9 passed

Phase 6 — Finalization
  PM writes memory/YYYY-MM-DD.md
  PM runs /sync "type: description" → PR opened
```

---

## Skills

| Skill | File | Trigger |
|-------|------|---------|
| `post-write-check` | [`skills/post-write-check/SKILL.md`](skills/post-write-check/SKILL.md) | After any Write/Edit to Python/JS files |
| `i18n-audit` | [`skills/i18n-audit/SKILL.md`](skills/i18n-audit/SKILL.md) | After any locale file or i18n.py change |

---

## Codex-Specific Notes

Codex runs without outbound internet access:
- `download_service.download_video()` cannot actually download — use mocks in tests
- `download_service.get_video_info()` cannot call YouTube — return fixture data in tests
- Do NOT attempt to `pip install` additional packages; use `requirements.txt` only
- Never modify `.venv/` or `downloads/`
- Append to AI commits: `Co-Authored-By: Codex <noreply@openai.com>`


## Universal Baseline Behaviors

All agents, regardless of their role, must adhere to the following:
- **Core Principles**: Always follow SOLID principles and write unit tests when creating functional code.
- **Security Boundaries**: Never expose or log secrets (API keys, tokens). Do not modify CI/CD pipelines without explicit permission.
- **Communication Style**: Keep explanations concise and use markdown formatting. Always explain "why", not just "what".
- **Conflicting Instructions**: If a user request violates project rules (e.g., bypassing tests), warn the user and request explicit confirmation before proceeding.
- **Anti-Patterns to Avoid**: Do not apply overly restrictive logical rules (e.g., "never use loops") or repeat basic knowledge.
