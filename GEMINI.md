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
