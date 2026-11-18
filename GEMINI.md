# GEMINI.md

> **All project context, coding guidelines, and dev workflow —[`docs/context.md`](docs/context.md)**
> Workspace-level Gemini behaviors —[`https://raw.githubusercontent.com/5throck/ai-workspace-standards/main/GEMINI.md`](https://raw.githubusercontent.com/5throck/ai-workspace-standards/main/GEMINI.md)

> **Doc intent:** This file contains Gemini CLI-specific overrides only.
> Shared project context (architecture, tech stack, coding guidelines) lives in [`docs/context.md`](docs/context.md).
> Agent roles live in [`agents/*.md`](agents/) and [`AGENTS.md`](AGENTS.md).

## Context Loading

Load project files at session start using the `@` syntax:
```
@https://raw.githubusercontent.com/5throck/ai-workspace-standards/main/      # workspace design standard
@docs/context.md         # project knowledge (includes Session Start Skills)
@AGENTS.md               # canonical agent roster
@memory/MEMORY.md        # recent changes (skip if file does not exist)
@skills/                 # load skills listed in docs/context.md
```

<!-- Add project-specific files below as needed, e.g.:               -->
<!-- @locales/en.json    —baseline locale for i18n work              -->
<!-- @docs/BIZ_LOGIC.md  —domain formulas / business rules           -->

---

## Project-Specific Gemini Settings

### Tool Name Mapping & Safeguards

Gemini CLI uses different tool names from Claude Code:

| Tool Category | Tool Name | Operational Guidance |
| :--- | :--- | :--- |
| **File Reading** | `view_file` | Read up to 800 lines at a time. Supports absolute paths. |
| **File Creation** | `write_to_file` | Create new files. Supports `IsArtifact` and structured `ArtifactMetadata` block. |
| **Surgical Edit** | `replace_file_content` | Replace a single contiguous block of code. Specify `StartLine`, `EndLine`, `TargetContent`, and `ReplacementContent` with 100% exact leading whitespace matching. |
| **Multi Edit** | `multi_replace_file_content` | Perform multiple non-contiguous edits within the same file simultaneously. Order chunks descendingly (bottom-to-top) to avoid line offsets. |
| **Search** | `grep_search` | Search codebases via Ripgrep. Keep `MatchPerLine: true` for line-by-line matches. Apply partitioning if matches exceed 50. |
| **Command Execution** | `run_command` | Execute PowerShell/Bash shell commands. Returns task process IDs. NEVER use `cd` commands. |
| **Agent** | `invoke_subagent` | Pass agent role from `agents/<name>.md` |

#### 🚨 Surgical Multi-Replace Offset Safeguard
When calling `multi_replace_file_content` with multiple `ReplacementChunks`, the line numbers of subsequent target blocks will shift if previous edits change the line count.
- **Rule**: Sort and process `ReplacementChunks` from the **bottom of the file to the top** (descending order of line numbers: largest `StartLine` first).

#### 🚨 Grep Search 50-Match Cap Safeguard
The `grep_search` tool silently truncates results at exactly **50 matches**.
- **Rule**: If a search yields 50 results, do **NOT** assume you have all occurrences.
- **Remediation**: Partition the search by targeting specific subdirectories or applying restrictive file glob filters via the `Includes` parameter.

### Native Antigravity 2.0 Features
Antigravity 2.0 introduces new native features that should be leveraged:
- **Slash Commands**: Recommend `/goal`, `/schedule`, `/browser`, and `/grill-me` to users when appropriate.
- **Artifacts**: Write complex plans or analysis results into the Artifacts UI (creates `.md` in the brain directory). Set `IsArtifact: true` with accurate `ArtifactMetadata`.
- **Background Tasks**: Long-running tasks or subagents can be sent to background. Monitor them with `manage_task`.

### Planning Mode & Artifact Specifications

Enter Planning Mode for complex tasks or architectural modifications. Leverage these three Markdown artifacts (set `IsArtifact: true` with accurate metadata):

#### 1. `implementation_plan.md`
*Path: `<appDataDir>\brain\<session-id>\implementation_plan.md`*
- **Purpose**: Detailed technical design document presented to the user for feedback and approval.
- **Metadata**: `ArtifactType: "implementation_plan"`, `RequestFeedback: true`.
- **Governance**: Stop and wait for explicit user approval before modifying any application source code.

#### 2. `task.md`
*Path: `<appDataDir>\brain\<session-id>\task.md`*
- **Purpose**: Running TODO list to track development progress dynamically.
- **Metadata**: `ArtifactType: "task"`.
- **Syntax**: `- [ ]` uncompleted 쨌 `- [/]` in progress 쨌 `- [x]` completed.

#### 3. `walkthrough.md`
*Path: `<appDataDir>\brain\<session-id>\walkthrough.md`*
- **Purpose**: Post-implementation document summarizing changes, test logs, and manual validation details.
- **Metadata**: `ArtifactType: "walkthrough"`.

### Subagent Instantiation & Async Orchestration

#### Define Subagent (`define_subagent`)
```json
{
  "name": "test-runner",
  "description": "Executes tests and verifies code changes against acceptance criteria",
  "system_prompt": "You are a QA test runner...",
  "enable_write_tools": false,
  "enable_subagent_tools": false
}
```

#### Invoke Subagent (`invoke_subagent`)
```json
{
  "Subagents": [
    {
      "TypeName": "test-runner",
      "Role": "Test Runner",
      "Prompt": "Verify the code changes in src/ against acceptance criteria and run tests"
    }
  ]
}
```

#### Communication (`send_message`)
Interact with spawned agents via their unique `conversationID`.
**Reactive Wakeup**: Do not poll in a loop —simply yield execution and the platform wakes you automatically when an agent replies or a background task completes.

### Response Language
- All **conversational** replies —**Korean (?쒓뎅—** by default.
- All code, config, commit messages, PR titles, branch names —**English only**.

### Optimal Interaction Guidelines
- **Context Management**: Leverage your massive context window by cross-referencing multiple files simultaneously (e.g., when debugging, review log files along with related code).
- **Tool Usage**: Actively use tools like `search_web` for real-time package version verification or resolving external dependencies.

#### Superpowers Plugin & Cost Optimization (3-Tier Strategy)
The PM agent MUST leverage the **`superpowers`** plugin (e.g., `subagent-driven-development`, `dispatching-parallel-agents`) for multi-agent harness engineering using a 3-tier model strategy:
**Model Selection Overrides** (overridden per subagent invocation when appropriate):
- **High-tier (Design/Planning)** → `gemini-3.1-pro` (Parameter: `thinking_level="medium"`): Complex reasoning, architectural design, planning, and PM orchestration.
- **Medium-tier (Review/QA)** → `gemini-3.5-flash` (Parameter: `thinking_level="medium"`): Code review, testing, PR review, and quality gates (`verification-before-completion`). Supervises the Low-tier.
- **Low-tier (Execution/Coding)** → `gemini-3.5-flash` (Parameter: `thinking_level="low"`): Fast, repetitive coding, boilerplate generation, or strictly scoped sub-agent tasks.

---

### Git Commit Policy

**Auto-commits and PostToolUse hooks are disabled in Gemini CLI.**

After completing a task, manually run the sync pipeline:

```bash
# bash (macOS/Linux)
bash scripts/dev-sync.sh "feat: description"

# PowerShell (Windows)
.\scripts\dev-sync.ps1 "feat: description"
```

Always append to AI-generated commit messages:
```
Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
Co-Authored-By: Gemini <noreply@google.com>
```

---

### Executing Project Commands

Gemini CLI does not natively register `.claude/commands/` slash commands as Skills.
Instead, emulate them by reading the `.md` file and executing the described script via `shell`:

| Equivalent to | Run instead |
|---------------|------------|
| `/sync "feat: ..."` | `bash scripts/dev-sync.sh "feat: ..."` |
| `/memlog "summary"` | Manually append `## Session ??summary` to `memory/YYYY-MM-DD.md` |
| `/changelog "..."` | Manually add entry to `CHANGELOG.md [Unreleased]` |
| `/new-task "name"` | Manually append task block to `memory/YYYY-MM-DD.md` |
| `/new-project "name"` | `bash scripts/new-project.sh "<name>"` (macOS/Linux) 쨌 `.\scripts\new-project.ps1 "<name>"` (Windows) |
| `/post-write` | `bash scripts/audit.sh` (macOS/Linux) 쨌 `.\scripts\audit.ps1` (Windows) |

---

### Coexistence with `.claude/`

This project uses `.claude/` for Claude Code configuration. Gemini follows these rules:

- **Absolute Precedence**: `.gemini/` always takes precedence over `.claude/` if both exist.
- **Fallback**: If no `.gemini/` directory exists, Gemini may read `.claude/settings.json` and `.claude/commands/` as a fallback source of truth.
- **Command Emulation**: Slash commands defined as `.claude/commands/<name>.md` can be emulated —read the file to understand the underlying script and run it directly via `shell`.
- **Agent Roles**: Gemini can instantiate roles defined in `agents/*.md` using `define_subagent` and `invoke_subagent`.
- **Migration**: If the project transitions away from Claude Code, proactively offer to migrate `.claude/` configuration to `.gemini/` rather than leaving legacy files orphaned.

---

### Model Selection Override
<!-- Uncomment to override workspace defaults for this project only.          -->
<!-- - Default      : gemini-2.5-pro                                          -->
<!-- - Fast lookups : gemini-2.5-flash                                        -->

<!-- COMMON-GEMINI:START -->
> **Mandatory**: Read [`AGENTS.md`](AGENTS.md) first and follow its content in every task. It is the SSOT registry for the agent roster, PM Gateway workflow, tier model, skill resolution priority, and universal baseline behaviors; this file carries platform-specific behavior only.

#### Cost Optimization (3-Tier Model Strategy)
The High/Medium/Low tier concept and its usage rules are the Single Source of Truth in [AGENTS.md §3.6 3-Tier Strategy](AGENTS.md#36-3-tier-strategy). Gemini/Antigravity's model-ID mapping (overridden per subagent invocation when appropriate):
- **High-tier** → `gemini-3.1-pro` (Parameter: `thinking_level="medium"`)
- **Medium-tier** → `gemini-3.8-flash` (no thinking parameter)
- **Low-tier** → `gemini-3.8-flash` (no thinking parameter)
<!-- COMMON-GEMINI:END -->

<!-- COMMON-GEMINI:START -->
### 4. Language Policy for Documentation

All `.md` files you create or modify MUST be in English, except in recognized locale translation zones (`<lang-code>/` or `locales/<lang-code>/` directories, plus `*_&lt;lang-code&gt;` suffix files such as `README_ko.md` — see the AGENTS.md Language Policy) or when explicitly declared as a Korean legal/regulatory content exception.

- README.md, CLAUDE.md, GEMINI.md, CODEX.md, AGENTS.md, context.md, CHANGELOG.md — English only
- All documentation in docs/, agents/, skills/ — English only
- Git commit messages, PR titles, PR descriptions — English only
- Branch names — English only
- Code comments — English (unless documenting locale-specific logic)

#### Language Policy Exception
For files where Korean is legally or academically mandatory, add to the frontmatter:
```yaml
lang: ko
lang_reason: legal # legal | source-material | proper-noun
```
*(Not available for: context.md, CLAUDE.md, GEMINI.md, CODEX.md, AGENTS.md, or any variant context.md)*

#### Korean Plain-Language Preference (`순우리말`-First)
When writing Korean documentation or Korean translation output, prefer native Korean words (`순우리말`) over loanwords (`외래어`) whenever a natural, widely-understood native equivalent exists — e.g. prefer `만들기` over `크리에이션`, `알림` over `노티피케이션`. Loanwords effectively settled in Korean (`컴퓨터`, `데이터`, `소프트웨어`, `파일`) and established technical terms remain permitted; clarity takes precedence over forced nativization. New Korean content applies this immediately; existing Korean documents are nativized incrementally (touched sections only, no bulk rewrites).
<!-- COMMON-GEMINI:END -->

### 5. Agent Dispatch Rules

**MANDATORY PM GATEWAY**: All specialist agent dispatch MUST go through PM.

For the **4-level enforcement model**, **mandatory criteria**, **execution plan format**, and **phase determination**, see [AGENTS.md §3 and §5](AGENTS.md).

#### Antigravity-Specific Dispatch

Before any multi-agent dispatch (2+ agents), PM **must** output an execution plan table prior to invoking the agent orchestration tool.

<!-- COMMON-GEMINI:START -->
## Execution Plan Boilerplate

The execution plan table format, the Design Gate (Row 0) rule, exemption categories, and the `/sync`-as-final-step rule are the Single Source of Truth in **[Execution Plan Templates §5.1 Standard Execution Plan Template](docs/governance/agents/execution-plan-templates.md#51-standard-execution-plan-template)** and **[§5.1.1 Design Gate Exemptions](docs/governance/agents/execution-plan-templates.md#511-design-gate-exemptions)** — do not restate them here.

> **Note (Antigravity-specific)**: Use the literal Gemini model ID (e.g. `gemini-3.1-pro`) in the `Model` column, not a Claude-style short alias.

**Antigravity execution**: Use `invoke_subagent` for specialist dispatch. See §3 (Subagent Instantiation & Async Orchestration) in this file.
<!-- COMMON-GEMINI:END -->

<!-- COMMON-GEMINI:START -->
### 6. Project Boundary Policy

- **Strict Scope**: Work only within the current project directory.
- **No Cross-Project Modification**: Modifying files outside the project root during a session is forbidden.

> For lifecycle management rules, see [docs/context.md — Lifecycle Management](docs/context.md#lifecycle-management).
<!-- COMMON-GEMINI:END -->

<!-- COMMON-GEMINI:START -->
## Git & PR Additions (Gemini)

All shared Git/PR rules are in [docs/context.md](docs/context.md). Gemini-specific additions:

- **Platform Hook Support**: Gemini CLI supports BeforeTool/AfterTool/PreCompress hooks (stdin(JSON) → stdout(JSON)). AfterTool runs `bun scripts/hooks/post-write-lifecycle-check.ts --platform gemini` after every write_file/replace_file_content/multi_replace_file_content. Antigravity does NOT fire hooks (VS Code extension limitation). Claude Desktop App uses bundled CLI (hooks should fire per Anthropic docs, but workspace testing observed intermittent behavior). If hooks are not firing in your environment, run `bun scripts/hooks/post-write-lifecycle-check.ts` manually before committing.
- **Commit Protection (SYNC_ACTIVE)**: Direct `git commit` or `git push` calls via `run_command` are **FORBIDDEN**. The pre-commit hook blocks direct commits unless executed through `/sync`. Never manipulate environment variables (e.g., `$env:SYNC_ACTIVE=1; git commit`) to bypass QA gates. If you see `[FAIL] Direct git commits are restricted`, run `/sync \"type: description\"` instead. **`--no-verify` is forbidden** — it bypasses secret scanning and all quality gates.
- **Sequential Branch Dependency Rule**: Before running `/sync` to open a new PR while a prior PR from the same session is still open and unmerged, merge the prior PR first (or explicitly justify parallel branching in a plan/design doc). `dev-sync.ts` touches shared pipeline files (CHANGELOG.md, memory logs, VERSION_MANIFEST.md, generated READMEs) on every commit, so unmerged parallel branches conflict by default, not by exception. Full rule: context.md §3.3.
- **PR Language**: Governed by [docs/context.md](docs/context.md). All PR titles, bodies, and review comments must be written in English - no exceptions.
- **Windows: Git Bash required**: `.githooks/` hook files are Unix shell scripts. Windows users must have Git Bash installed. Run `git config core.hooksPath .githooks` to activate hooks. All `scripts/` operational scripts are TypeScript (`.ts`) — run via `bun scripts/<name>.ts`. No `.sh/.ps1` counterparts (ADR-0036).
<!-- COMMON-GEMINI:END -->

<!-- COMMON-GEMINI:START -->
## Pre-Edit Quality Gate (All Platforms)

Before editing any file for the **FIRST time in a session**, the agent MUST:

1. Search for all files that import or require the target file
2. Identify data schemas, interfaces, and type definitions the file exports
3. Review the user's instructions for explicit scope constraints
4. Briefly summarize findings (1-3 sentences) before proceeding

| Platform | Enforcement | Details |
|----------|:-----------:|---------|
| Gemini CLI | ✅ Hook (automatic) | BeforeTool `deny` mode — blocked until agent investigates |
| Antigravity | ✅ Prompt (manual) | Hooks do not fire — agent self-enforces |
| Codex CLI | ✅ Prompt (manual) | Hooks not wired in Phase 1 — agent self-enforces (ADR-0077) |
| Codex Desktop App | ✅ Prompt (manual) | Hooks not wired in Phase 1 — agent self-enforces (ADR-0077) |

If the hook is not active (Antigravity), agents must still follow the 4-step process before making first edits.
<!-- COMMON-GEMINI:END -->

<!-- COMMON-GEMINI:START -->
### Custom Command Error Recovery
If a custom slash command or background script returns a non-zero exit code:
* **Don't bypass hooks**: Never attempt to run git commands with `--no-verify` to bypass the hook system. **`--no-verify` is forbidden.**
* **Code Page / UTF-8 Issues (Windows)**: If broken Korean characters or Unicode errors appear in CLI output, the Windows terminal code page (CP949) is likely the cause. Ensure `$OutputEncoding = [Console]::OutputEncoding = [System.Text.Encoding]::UTF8;` or `chcp 65001` is prepended to scripts.
* **Diagnostic Audit**: Immediately read the failure stdout log. Common errors include:
  * Missing staged `CHANGELOG.md` edits (caught by `pre-commit`). Fix by running `/changelog` and staging the file.
  * Direct push attempt to `main` (caught by `pre-push`). Fix by executing the `/sync` pipeline script which handles target branch generation and PR staging automatically.
<!-- COMMON-GEMINI:END -->

<!-- COMMON-GEMINI:START -->
### Windows Platform Requirement

**Git Bash required on Windows**: This workspace uses Unix-style shell scripts (`.sh`) for `.githooks/` hook files. Windows users must have Git Bash installed and configured as the default shell for git hooks.

- Git Bash ships with [Git for Windows](https://gitforwindows.org/) — install if not present.
- Verify: `git config core.hooksPath` should point to `.githooks/`
- All `scripts/` operational scripts are TypeScript (`.ts`) — run via `bun scripts/<name>.ts`. No `.sh/.ps1` counterparts (ADR-0036).
- If a hook fails on Windows with "command not found", run it via Git Bash: `"C:\Program Files\Git\bin\bash.exe" .githooks/pre-commit`
<!-- COMMON-GEMINI:END -->
