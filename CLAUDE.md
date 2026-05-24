# CLAUDE.md —QuickDL

**Claude Code (CLI & Desktop App)** configuration for the QuickDL project.

> **Doc intent:** This file is Claude Code-specific behavioral configuration.
> Shared project context (architecture, tech stack, i18n system, git conventions) lives in [`docs/context.md`](docs/context.md).
> Agent roles live in [`agents/*.md`](agents/) and [`AGENTS.md`](AGENTS.md).

---

## Session Start

At the start of every Claude Code session, run this checklist:

```
0. git config core.hooksPath .githooks   # activate hooks (run once per clone)
1. Read https://raw.githubusercontent.com/5throck/ai-workspace-standards/main/CONSTITUTION.md               # workspace design standard
2. Read docs/context.md                  # project knowledge ??architecture, i18n, workflow
3. Read AGENTS.md                        # canonical agent roster
4. Read memory/MEMORY.md                 # recent session history (skip if absent)
5. Load skills/post-write-check/SKILL.md # mandatory QA chain after any Write/Edit
6. Load skills/i18n-audit/SKILL.md       # locale key parity audit protocol
```

---

## Claude Code: CLI vs Desktop App

Both the CLI and the Desktop App share the same `.claude/settings.json` and slash commands.

> **Hook limitation**: `PostToolUse` hooks defined in `.claude/settings.json` do **not** fire in the Desktop App. After any Write/Edit, run `bash scripts/audit.sh` manually before committing.

> **Recommended split**: Use CLI for automated workflows (hook-driven audit, multi-step tasks). Use Desktop App for PR monitoring and visual review.

---

## Claude Code Settings

- `.claude/settings.json` —shared team config: PostToolUse audit hook (committed to repo)
- `.claude/settings.local.json` —personal git/gh write permissions (gitignored)
- `.claude/commands/` —slash commands: `/sync`, `/memlog`, `/new-task`

Both files are loaded automatically by Claude Code.

---

## Hooks

A `PostToolUse` hook fires after every `Write` or `Edit` call and runs `scripts/sync-md.sh`, which delegates to `scripts/audit.sh`.

| Environment | Hook fires? | Action if not |
|-------------|:-----------:|---------------|
| Claude Code CLI | —| Automatic |
| Claude Code Desktop App | —| Run `bash scripts/audit.sh` manually |
| Gemini CLI | —| Run `bash scripts/audit.sh` manually |

`audit.sh` checks: CHANGELOG.md existence 쨌 locale key parity 쨌 absolute path detection 쨌 broken markdown links 쨌 `.sh`/`.ps1` script pairing.

---

## Behavioral Rules

### Response Language

Respond in **Korean** unless the user writes in English.

### Plan Mode

Enter plan mode (`EnterPlanMode`) when:
- User requests a new feature or significant refactor
- The change touches more than 2 files
- The correct approach is unclear

### Task Tracking

- Call `TaskCreate` before starting any multi-step work
- Set status `in_progress` before beginning a task
- Set status `completed` immediately after finishing
- Never leave tasks `in_progress` at end of session

### Subagent Pattern

Follow the 6-phase PM Subagent Dispatch Protocol defined in `AGENTS.md`:
1. Phase 1: Triage (Parallel read-only)
2. Phase 2: Design
3. Phase 3: Implementation (Serial writes: backend —frontend —i18n)
4. Phase 4: QA Verification
5. Phase 5: Quality Gate
6. Phase 6: Finalization

---

## Git Hooks

Install project hooks once per clone:
```bash
git config core.hooksPath .githooks
```

| Hook | Trigger | Action |
|------|---------|--------|
| `.githooks/pre-commit` | Every commit | Blocks if `CHANGELOG.md` not staged |
| `.githooks/pre-push` | Every push | Runs `audit.sh`; aborts on failure |

---

## Git

Follow conventions in [`docs/context.md 짠 Git Conventions`](docs/context.md#git-conventions).
Append to AI commits: `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`

---

*Last Updated: 2026-05-24*


### Optimal Interaction Guidelines
- **XML Tagging**: Utilize XML tags like `<thought>`, `<plan>`, and `<execution>` to structure complex reasoning and plans before generating final responses.
- **Tone**: Maintain an objective, highly analytical tone. Focus on systematic execution.

