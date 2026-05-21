# CLAUDE.md — QuickDL (Project-Level)

> **Shared context:** Read `docs/agent-config/shared.md` first.
> **Agent roles:** See `docs/agent-config/agents.md`.

---

## Claude Code — Project-Specific Behavior

### Superpowers Workflow

Always follow the Superpowers skill hierarchy:
1. **brainstorming** → design spec (`docs/superpowers/specs/`)
2. **writing-plans** → implementation plan (`docs/superpowers/plans/`)
3. **subagent-driven-development** → execute plan task-by-task

Do NOT skip brainstorming for non-trivial changes. Even "simple" tasks need a design.

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

Each implementation task:
1. Fresh subagent executes the task
2. Spec-compliance review subagent checks the result
3. Code-quality review subagent checks for issues
4. Fix and re-review if issues found (max 3 iterations)

### Response Language

Respond in **Korean** unless the user writes in English.

### Session Start

At the start of every coding session, load:
1. [`skills/post-write-check/SKILL.md`](skills/post-write-check/SKILL.md) — mandatory QA chain after any Write/Edit
2. [`skills/i18n-audit/SKILL.md`](skills/i18n-audit/SKILL.md) — locale audit protocol

Then read [`docs/context.md`](docs/context.md) for shared project context.

### Agents

Agent roles live in [`agents/*.md`](agents/). Registry and orchestration contract: [`AGENTS.md`](AGENTS.md).

### Git Hooks

Install project hooks once per clone:
```bash
git config core.hooksPath .githooks
```

Hooks:
- `.githooks/pre-commit` — blocks commit if `CHANGELOG.md` not staged
- `.githooks/pre-push` — runs `audit.sh` before push

### Git

Follow conventions in `docs/context.md`.
Append to AI commits: `Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>`
