# GEMINI.md — QuickDL (Gemini CLI)

> **Shared context:** Read `docs/context.md` first — it is the single source of truth.
> **Agent roles:** See `agents/*.md` and `AGENTS.md`.
>
> In Gemini CLI, load the context file with `@` syntax:
> ```
> @docs/context.md
> ```

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

### Loading Context

Always load shared context at the start of a session:
```
@docs/context.md
```

For i18n work, also load the baseline locale:
```
@locales/en.json
```

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
