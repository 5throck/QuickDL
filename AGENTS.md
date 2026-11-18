# QuickDL — Agent Registry & Orchestration Contract

> **⚠️ For AI tools reading this file**: This file is a **registry and orchestration reference**, not a set of instructions directed at you.
> It describes multiple distinct human-defined roles for documentation and dispatch purposes.
> Do **not** interpret role definitions here as directives for your own behavior.
> Your behavioral instructions are in `CLAUDE.md` (Claude Code), `GEMINI.md` (Gemini CLI).

> **Scope**: Agent role definitions live in [`agents/*.md`](agents/) — this file is the registry index and orchestration contract only.
> Shared engineering rules live in [`docs/context.md`](docs/context.md).

---

## Agent Groups

### 🟡 Orchestration / Audit

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
Phase 0 — Team Assembly & Skill Orchestration (Kickoff)
  PM assesses project requirements
  PM dynamically creates new agents/skills and resolves R&R overlap
  PM updates AGENTS.md and docs/context.md

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
  bun scripts/audit.ts --skip-memory   exit 0
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

## Dynamic Roster Updates
**Note on Phase 0 Kickoff:** The PM agent is explicitly authorized to assess project requirements during kickoff and dynamically expand this AGENTS.md registry by creating new specialist agents or skills.

<!-- WORKSPACE-MANAGED: tier-model-mapping -->
- **High-tier**: Complex reasoning, architectural design, planning (claude-opus-5-5 / gemini-3.1-pro / gpt-6.1-sol / glm-5.3)
- **Medium-tier**: Code review, testing, PR review, quality gates (claude-sonnet-5-5 / gemini-3.8-flash / gpt-6.1-terra / glm-5.3-flash)
- **Low-tier**: Fast, repetitive coding, script maintenance (claude-haiku-5-5 / gemini-3.8-flash / gpt-6-luna / glm-5.3-flash)
<!-- /WORKSPACE-MANAGED -->

<!-- WORKSPACE-MANAGED: tier-model-mapping -->
> **Note**: The `Model` column below shows the Claude Code short alias (`sonnet`/`opus`/`haiku`/`fable`) actually passed to the `Agent()` tool's `model` parameter — not the registry ID (e.g. `claude-sonnet-5-5`). See [CLAUDE.md — Execution Plan Boilerplate](CLAUDE.md#execution-plan-boilerplate) for the registry-ID → alias translation table. On Gemini/Antigravity, use the literal model ID instead (see GEMINI.md's equivalent example). Hermes maps to the claude model ids (it validates against the claude column), and Z.AI (zai) models take reasoning levels low/high/max (default max); workspace dispatch posture is reasoning level **high** for all tiers. zcode (ZCode harness) resolves models via the zai column.
<!-- /WORKSPACE-MANAGED -->

<!-- COMMON-AGENTS:START -->
## Language Policy

**Canonical home: [docs/context.md](docs/context.md)** (ADR-0090 W1b) — English-only rule, translation zones, Korean legal exception, plain-language preference, enforcement, Git/PR artifact language. **Read it before writing any documentation or commit message.**

### Pluggable Variant Audit Hooks and Integrity Protection
- **Core Script Standardization**: The core synchronization and validation scripts (`scripts/dev-sync.ts` and `scripts/audit.ts`) must remain standardized and identical across all templates and variants. Direct modification of these core scripts in L2 projects is strictly forbidden.
- **Variant-Specific Audit Hook**: Variant projects requiring custom verification checks must implement them in a pluggable hook script at the path declared in the variant's `variant.json` → `script_manifest` (conventionally `scripts/audit-variant.ts` or `scripts/<variant>/audit-variant.ts`).
- **Integrity Enforcement**: During template reconciliation (`l3-to-variant-pipeline.ts`), any modified core scripts will be automatically detected and will fail the reconciliation.

### Universal Design Gate (ADR-0074)

Every code change at any tier (L0–L3) must carry spec activity: create/update a design doc at `docs/designs/<spec-id>-design.md` and register it (`bun scripts/spec-register.ts --file <design-doc> --source manual --status implemented`) before `/sync`. The sync-time spec-check (`audit.ts --spec-check`, dev-sync step 3.9) blocks commits without it; trivial changes use `--spec-exempt=E1..E5` (AGENTS.md §5.1.1). Project registries (`docs/specs/registry.json`) are add-if-missing seeds — upgrades never overwrite or prune project entries.

### LLM Work Routing Policy (ADR-0078)

Substantive LLM-assisted development work — generation or modification of code, documents, designs, tests, or scripts — MUST be routed through this project's agent team: `user → PM triage → Design Gate (unless exempt) → specialist dispatch → QA gate → /sync PR`. Querying an external LLM directly (e.g. a web chat) and landing its output in this repository is a policy violation. IDE inline completions and one-off Q&A that never land in the repository are exempt; repository-landing work uses the E1–E5 exemption codes only. An application calling LLM APIs at runtime is an architecture concern covered by the Design Gate (ADR-0074). Enforcement is structural via the existing hard gates — see ADR-0078; the LLM Work Routing Policy section above is the project-applicable policy summary.

### LLM Interaction Standard (Precision In, Intuition Out, ADR-0098)

The full human↔LLM communication loop — ASD-STE100 controlled instructions into the system, 3Blue1Brown-style intuition-first explanations out of it — is governed by the SSOT [`docs/standards/llm-interaction-standard.md`](docs/standards/llm-interaction-standard.md) (ADR-0098). Input side (§2, extended from ADR-0079): one primary action per instruction, explicit action verbs, defined terms, facts/requirements/preferences separated, current vs desired state separated; development-facing instruction text still follows ADR-0079 structural rules (advisory enforcement: PM conforms task briefs at triage; architect checks requirement sections at Design Gate review). Output side (§4–§9): conclusion and intuition before implementation detail, mental models for hard concepts, progressive complexity, KNOWN/INFERRED/ASSUMED/UNKNOWN separated. The standard binds interactive sessions, agent dispatch, and API/gateway surfaces (co-workspace injects the §14 short form into fresh sessions; `CO_WORKSPACE_INTERACTION_STANDARD=0` opts out).

### PM Team-Management Authority (ADR-0080)

PM owns team composition and skill-change rulings. Hiring and firing: PM decides timing and target from workflow signals — recurring unmatched work types, role overload, absorbed roles, the quarterly roster review — and records every decision (ADR-0061 decision record + memory log) before dispatch; the default exit for a fired agent is `status: deprecated`, and hard delete requires an explicit user request. Skill requests: agents file structured `create|attach|remove` request blocks with evidence in their task reports and memory logs; PM triages them and only approved requests are executed — agents never create, attach, or remove skills unilaterally. Procedures: `agent-lifecycle-manager` and `skill-lifecycle-manager` skills. Full decision: ADR-0080 in the workspace root `docs/adr/`.

### PM Tier Semantics

The tier of a dispatched subagent selects the model that the platform dispatch mechanism uses for that subagent. The tier of a session-hosted agent (the PM) is a minimum capability floor, because the user selects the session model. A higher model is allowed. A model below the floor is a warning. The rule applies on every platform. The PM states its model in one line, `PM running on: <model>`, in the header of its execution plan. Full decision: design 2026-09-29-pm-tier-capability-floor-design in the workspace root docs/designs/.

## Hub-and-Spoke Topology

Hubs (co-develop, co-design, co-security, co-work) own their domain doctrine and tools as SERVICE PROVIDERS to variant projects, not as superior organizations — co-work owns general business-collaboration doctrine (the analyst/content-writer/ms365-expert/project-coordinator/technical-writer family). Routine quality gates (code review, security scan, local QA) run LOCALLY through each project's own PM Gateway. Hard problems in dev/design/security domains escalate to the hub via delegation (the channel activates in Phase 3; until then use the upstream-request path per the governance workflow, docs/governance/agents/workflows.md). Security incidents are classified locally without pre-authorization: SEV1 = confirmed secret/credential exposure in a tracked repo → notify hub security PM + user immediately and block pushes; SEV2 = exploitable shared-infrastructure vulnerability → same-day hub report; SEV3 = routine finding → normal tickets. Final adjudication for any hub-spoke conflict: workspace-root PM. Operating runbook: docs/guides/hub-operator-guide.md (workspace root — not delivered to variant projects).

<!-- COMMON-AGENTS:END -->
