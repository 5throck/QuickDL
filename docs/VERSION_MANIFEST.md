# VERSION_MANIFEST.md

**Generated**: 2026-11-18T16:45:18.116Z
**Manifest Version**: 1.0
**Location**: docs/VERSION_MANIFEST.md

---

## Summary

- **Agents**: 8
- **Skills**: 38
- **Scripts**: 0 *(top-level CLI scripts; library/helper modules under `scripts/lib/`, `scripts/helpers/`, `scripts/hooks/`, and `scripts/validators/` plus experiment files under `scripts/experiments/` are excluded here — `scripts/SCRIPTS.md` is the full registry)*
- **Commands**: 7

---

## Agents

| Name | File | Tier | Model | Last Modified |
|------|------|------|-------|---------------|
| backend | agents/backend.md | N/A | inherit | 2026-05-22 |
| designer | agents/designer.md | medium | claude-sonnet-5-5 | 2026-05-21 |
| frontend | agents/frontend.md | N/A | inherit | 2026-05-21 |
| i18n | agents/i18n.md | N/A | inherit | 2026-05-22 |
| pm | agents/pm.md | N/A | inherit | 2026-05-23 |
| qa | agents/qa.md | N/A | inherit | 2026-05-22 |
| security | agents/security.md | N/A | inherit | 2026-05-21 |
| security-monitor | agents/security-monitor.md | medium | claude-sonnet-5-5 | 2026-05-23 |

---

<!-- validate-md-language:allowlist-begin reason="Triggers column embeds verbatim Korean search keywords copied from k-* SKILL.md frontmatter (proper-noun data values, not prose). Generated region — a whole-file lang: ko exception would be dishonest and would un-validate the rest of the manifest, so scripts/validate-md-language.ts exempts only this marked section (T-20260912-015)." -->
## Skills

| Name | Version | Status | Location | Platform | Triggers | Owner |
|------|---------|--------|----------|----------|----------|-------|
| accessibility-audit | 1.1.0 | active | .claude/skills/accessibility-audit/SKILL.md | all | accessibility-audit, /accessibility-audit, axe-core audit, wcag accessibility check, wcag 2.1 aa | pm |
| agent-lifecycle-manager | 1.4.0 | active | .claude/skills/agent-lifecycle-manager/SKILL.md | all | create agent, new agent, validate agents, agent lifecycle, manage agents, hire agent, fire agent, deprecate agent | pm |
| api-documentation | 1.0.2 | active | .claude/skills/api-documentation/SKILL.md | all | api documentation, document api, api reference, developer documentation, rest api docs, graphql docs, sdk documentation | pm |
| ci-triage | 0.2.0 | active | .claude/skills/ci-triage/SKILL.md | all | ci failure, triage failure, audit gate failed, scaffold failed, fix the pipeline | pm |
| code-review | 1.1.0 | active | .claude/skills/code-review/SKILL.md | all | code review, review pr, evaluate code, check code quality, pull request review, code inspection | pm |
| decision-record | 1.1.0 | active | .claude/skills/decision-record/SKILL.md | all | decision record, gate ruling, go/no-go decision, escalation decision, record a decision | pm |
| delegate-to-hub | 1.0.1 | active | .claude/skills/delegate-to-hub/SKILL.md | all | delegate to hub, delegation ticket, hub delegation, escalate to hub, file delegation | pm |
| design-foundation | 1.1.1 | active | .claude/skills/design-foundation/SKILL.md | all | design foundation, design principles, design guide, design tokens setup, design decision record | design-system-lead |
| documentation-writing | 1.0.3 | active | .claude/skills/documentation-writing/SKILL.md | all | write documentation, create guide, draft communication, write manual, create tutorial, documentation, technical writing | pm |
| evidence-ledger | 1.1.0 | active | .claude/skills/evidence-ledger/SKILL.md | all | evidence ledger, citation ledger, claim verification, source verification, evidence tracking | pm |
| explain-me | 1.0.1 | experimental | .claude/skills/explain-me/SKILL.md | all | /explain-me, /reportme, make a report, create report, explain this topic | pm |
| gateguard | 1.0.2 | active | .claude/skills/gateguard/SKILL.md | all | gateguard, /gateguard, investigate file, check before edit, pre-edit check | pm |
| handbook | 0.6.0 | active | .claude/skills/handbook/SKILL.md | all | make handbook, create handbook, build course site, companion handbook, update handbook, handbook sync, handbook maintenance | pm |
| handbook-sync-audit | 1.0.5 | active | .claude/skills/handbook-sync-audit/SKILL.md | all | audit handbook, handbook parity check, handbook sync audit, textbook drift check | pm |
| i18n-audit | 1.0.1 | active | skills/i18n-audit/SKILL.md | workspace | i18n audit, locale parity, translation parity, glossary audit, L10N parity | i18n-specialist |
| i18n-formatting | 1.0.1 | active | .claude/skills/i18n-formatting/SKILL.md | all | date format, number format, currency format, unit conversion, paper size, korean numerals | i18n-specialist |
| i18n-layout | 1.1.1 | active | .claude/skills/i18n-layout/SKILL.md | all | character encoding, RTL, bidi, font selection, CRLF, BOM | i18n-specialist |
| i18n-locale-config | 1.0.1 | active | .claude/skills/i18n-locale-config/SKILL.md | all | locale config, locale code, BCP 47, collation, collation order, timezone | i18n-specialist |
| meeting-facilitation | 1.5.0 | active | .claude/skills/meeting-facilitation/SKILL.md | all | meeting, agent discussion, collaborative decision, multi-agent coordination, facilitate meeting | pm |
| post-write-check | 1.0.0 | active | skills/post-write-check/SKILL.md | workspace | N/A | N/A |
| project-review | 1.3.2 | active | .claude/skills/project-review/SKILL.md | all | project review, review project, audit project, quality review | pm |
| refactoring | 1.2.0 | active | .claude/skills/refactoring/SKILL.md | all | refactor, clean up code, improve code, reduce duplication, pay down tech debt, code smell, improve design | pm |
| research-analysis | 1.0.2 | active | .claude/skills/research-analysis/SKILL.md | all | research, analyze, investigate, synthesize, evidence gathering, data analysis, literature review | pm |
| script-lifecycle-manager | 1.2.2 | active | .claude/skills/script-lifecycle-manager/SKILL.md | all | create script, update script, deprecate script, script lifecycle, manage scripts | pm |
| security-scan | 1.3.0 | active | .claude/skills/security-scan/SKILL.md | all | security scan, scan for vulnerabilities, security check, run security | pm |
| service-design | 1.1.0 | active | .claude/skills/service-design/SKILL.md | all | service design, customer journey, service blueprint, touchpoint design, customer experience, service innovation, operational alignment | pm |
| skill-lifecycle-manager | 1.5.0 | active | .claude/skills/skill-lifecycle-manager/SKILL.md | all | create skill, new skill, validate skills, skill lifecycle, manage skills, skill request, deprecate skill, remove skill | pm |
| source-command-commit-push-pr | 1.0.3 | active | .claude/skills/source-command-commit-push-pr/SKILL.md | all | commit-push-pr, commit and push, create PR | pm |
| standup-synthesizer | 1.1.0 | active | .claude/skills/standup-synthesizer/SKILL.md | all | standup digest, daily standup, synthesize standup, work summary | pm |
| swe-solve | 1.1.1 | active | .claude/skills/swe-solve/SKILL.md | all | swe-solve, solve issue, autonomous issue resolution, issue to pr | pm |
| sync | 1.10.0 | active | .claude/skills/sync/SKILL.md | all | sync, /sync, commit and push, create PR | automation-engineer |
| team-builder | 1.2.0 | active | .claude/skills/team-builder/SKILL.md | all | build new agent team, create agent team, agent team setup, team builder | pm |
| test-driven-development | 1.2.0 | active | .claude/skills/test-driven-development/SKILL.md | all | tdd, test driven development, test first, write tests first, red green refactor, test coverage | pm |
| token-usage-lint | 1.1.0 | active | .claude/skills/token-usage-lint/SKILL.md | all | token lint, hardcoded color, design token compliance, raw hex values, hardcoded spacing | pm |
| translate | 1.0.3 | active | .claude/skills/translate/SKILL.md | all | translate, translation, Korean translation | pm |
| ui-ux-design-intelligence | 1.0.1 | active | .claude/skills/ui-ux-design-intelligence/SKILL.md | all | design system, ui design, ux design, component design, visual design, design tokens, interface design | pm |
| update-bun-packages | 1.3.1 | active | .claude/skills/update-bun-packages/SKILL.md | all | update bun packages, upgrade bun packages, bun update, update dependencies, upgrade dependencies | pm |
| zod-contract-gate | 1.0.3 | active | .claude/skills/zod-contract-gate/SKILL.md | all | zod-contract-gate, /zod-contract-gate, zod contract validation, schema contract gate, runtime schema validation | contract-gate-engineer |

<!-- validate-md-language:allowlist-end -->

---

## Scripts

| Name | Version | Location | Dependencies |
|------|---------|----------|--------------|

---

## Commands

| Name | File | Platform | Skill Integration |
|------|------|----------|-------------------|
| changelog | .claude/commands/changelog.md | all | N/A |
| i18n-audit | .claude/commands/i18n-audit.md | all | N/A |
| memlog | .claude/commands/memlog.md | all | N/A |
| new-task | .claude/commands/new-task.md | all | N/A |
| post-write | .claude/commands/post-write.md | all | N/A |
| security-check | .claude/commands/security-check.md | claude | N/A |
| sync | .claude/commands/sync.md | all | N/A |

---

## Platform Parity Status

**Checked**: Claude (.claude/), Gemini (.gemini/), Antigravity (.agents/), Codex (.codex/ prompts mapping)

- **Commands with parity (gemini mirror)**: 6 / 7
- **Commands with codex prompts mapping**: 6 / 7
- **Skills in all four mirrors**: 36 / 38
- **Skills in claude+gemini only (both)**: 0 / 38 (common-template skills are parity-exempt)

---

## Drift Detection

⚠️ **Drift detected**:

- [WARNING] Agent backend missing tier metadata
- [WARNING] Agent frontend missing tier metadata
- [WARNING] Agent i18n missing tier metadata
- [WARNING] Agent pm missing tier metadata
- [WARNING] Agent qa missing tier metadata
- [WARNING] Agent security missing tier metadata
- [WARNING] Skill post-write-check has no triggers defined
- [WARNING] Command post-write has no matching skill of the same name
- [WARNING] Command security-check has no matching skill of the same name
