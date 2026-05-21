# GEMINI.md — QuickDL (Gemini CLI)

> **Shared context:** Read `docs/agent-config/shared.md` first.
> **Agent roles:** See `docs/agent-config/agents.md`.
>
> In Gemini CLI, load context files with `@` syntax:
> ```
> @docs/agent-config/shared.md
> @docs/agent-config/agents.md
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
@docs/agent-config/shared.md
```

For i18n work, also load the baseline locale:
```
@locales/en.json
```

### i18n Workflow

When working on translations:
1. Load `@locales/en.json` as the baseline
2. Run the key audit to find missing keys (see i18n Expert in `agents.md`)
3. Add missing keys to the target locale file — do not remove or rename existing keys
4. Never machine-translate without review

### Editing Files

- Use `edit` for modifying existing files (preferred)
- Use `write_file` for creating new files
- Always `read_file` before editing to get current content

### Response Language

Respond in **English**.

### Git

Follow conventions in `docs/agent-config/shared.md`.
Append to AI commits: `Co-Authored-By: Gemini <noreply@google.com>`

---

## Gemini-Specific Workflows

### 1. Planning Mode & Architecture Changes
For complex tasks or architectural modifications, Gemini must enter **Planning Mode**:
1. Create a detailed technical design using the **Implementation Plan** artifact.
2. Obtain explicit user approval before modifying code.
3. Track tasks using `task.md` and document changes in `walkthrough.md`.
4. Ensure that after changes are verified, the outcomes are summarized in the project's `memory/YYYY-MM-DD.md` log (if present) or `CHANGELOG.md`.

### 2. Executing Custom Commands
Unlike Claude Code, Gemini does not natively register local custom slash commands from `.gemini/commands/` or `.claude/commands/`. Instead:
- Automation workflows like `/sync` or `/memlog` are simulated or executed directly as project scripts (e.g., executing `.\scripts\dev-sync.ps1` or `./scripts/dev-sync.sh` via terminal tools).
- System-provided slash commands (like `/goal`, `/schedule`, `/browser`, `/grill-me`) can be recommended to the user.

### 3. Coexistence, Precedence & Migration of .claude
This project contains a `.claude/` directory. To prevent configuration drift and avoid issues when transitioning away from Claude Code, Gemini follows these rules:
- **Absolute Precedence**: `.gemini/` always takes absolute precedence over `.claude/`. If `.gemini/` exists, `.claude/` is ignored by Gemini to prevent duplicate or conflicting configurations.
- **Fallback (Coexistence Phase)**: If a project lacks a `.gemini/` directory but contains `.claude/`, Gemini will temporarily read and respect `.claude/settings.json`, `.claude/settings.local.json`, and `.claude/commands/` as the fallback source of truth.
- **Graceful Migration**: If the project transitions fully away from Claude Code, or if Gemini needs to write new project-level settings/commands, Gemini should proactively offer to migrate the `.claude/` configuration to `.gemini/` (copying and adapting files) rather than leaving legacy files orphaned.
- **Command Emulation**: Custom slash commands defined as markdown files in `.claude/commands/` must be emulated by Gemini by reading the `.md` file to understand the underlying script execution and running them directly via terminal tools.
- **Gemini Integration Rule**: Gemini can dynamically instantiate roles defined in `docs/agent-config/agents.md` using the `define_subagent` and `invoke_subagent` tools.
