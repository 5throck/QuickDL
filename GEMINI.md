# GEMINI.md — QuickDL (Gemini CLI)

> **Doc intent:** This file contains Gemini CLI-specific overrides only.
> Shared project context lives in [`docs/context.md`](docs/context.md).
> Agent roles live in [`agents/*.md`](agents/) and [`AGENTS.md`](AGENTS.md).

## Context Loading

Load project files at session start using the `@` syntax:

```
@../CONSTITUTION.md      # workspace design standard
@docs/context.md         # project knowledge (includes Session Start Skills)
@AGENTS.md               # canonical agent roster
@memory/MEMORY.md        # recent changes (skip if file does not exist)
```

For i18n work, also load:
```
@locales/en.json         # baseline locale (56 keys)
```

---

## Gemini CLI — Project-Specific Behavior

### Tool Name Mapping

Gemini CLI uses different tool names from Claude Code:

| Claude Code | Gemini CLI |
|-------------|-----------|
| `Read` | `read_file` |
| `Edit` | `edit` |
| `Write` | `write_file` |
| `Bash` | `shell` |
| `Grep` | `grep` |
| `Glob` | `find_files` |

### i18n Workflow

When working on translations:
1. Load `@locales/en.json` as the baseline
2. Run the key audit to find missing keys (see `agents/i18n.md`)
3. Add missing keys to the target locale file — do not remove or rename existing keys
4. Never machine-translate without review

### Editing Files

- Use `edit` for modifying existing files (preferred)
- Use `write_file` for creating new files
- Always `read_file` before editing to get current content

### Response Language

Respond in **Korean** unless the user writes in English.

### Git

Follow conventions in `docs/context.md § Git Conventions`.
Append to AI commits: `Co-Authored-By: Gemini <noreply@google.com>`

---

## Gemini-Specific Workflows

### 1. Planning Mode & Architecture Changes

For complex tasks or architectural modifications:
1. Create a detailed technical design and obtain explicit user approval before modifying code.
2. Document changes in `memory/YYYY-MM-DD.md` and update `CHANGELOG.md`.

### 2. Executing Custom Commands

Unlike Claude Code, Gemini does not natively register slash commands from `.claude/commands/`. Instead:
- Workflows like `/sync` or `/memlog` are executed directly via project scripts:
  - `./scripts/dev-sync.sh` (macOS/Linux)
  - `.\scripts\dev-sync.ps1` (Windows)

### 3. Coexistence with `.claude/`

This project contains a `.claude/` directory used by Claude Code:
- **Absolute Precedence**: `.gemini/` always takes precedence over `.claude/` if it exists.
- **Fallback**: If no `.gemini/` directory exists, Gemini may read `.claude/settings.json` and `.claude/commands/` as fallback.
- **Command Emulation**: Slash commands in `.claude/commands/*.md` can be emulated by reading the markdown file and executing the described script directly via terminal tools.
- **Agent Roles**: Gemini can instantiate roles defined in `agents/*.md` using `define_subagent` and `invoke_subagent` tools.


### Optimal Interaction Guidelines
- **Context Management**: Leverage your massive context window by cross-referencing multiple files simultaneously (e.g., when debugging, review log files along with related code).
- **Tool Usage**: Actively use tools like `search_web` for real-time package version verification or resolving external dependencies.
