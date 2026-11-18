---
name: sync
description: Sync today's development session to Git — run the documentation audit, update the memory index, commit all changes, push, and open a GitHub PR.
argument-hint: "<conventional-commit-message>"
allowed-tools: ["Bash"]
---

# /sync — Full Sync Pipeline

Run the full commit + PR pipeline for QuickDL.

## Usage

```
/sync "feat: description of change"
```

## What it does

1. Runs `scripts/audit.sh` — aborts if CHANGELOG or i18n keys have issues
2. Ensures `memory/YYYY-MM-DD.md` exists (creates if missing)
3. Updates `memory/MEMORY.md` index with today's entry (awk insertion after header)
4. Stages all changes and commits with the provided message
5. On `master`/`main`: creates a `pr/<timestamp>-<slug>` branch, resets master, pushes the PR branch, opens a GitHub PR (skips if PR already exists)
6. On feature branches: pushes directly

## Steps

Run:

```bash
bash scripts/dev-sync.sh "$ARGUMENTS"
```

If `$ARGUMENTS` is empty, the script will prompt for a commit message.

Report the PR URL when done.

## Pre-PR Security Gate (public repos only)

Before pushing/creating PR, check if the repo is public:

```bash
gh repo view --json isPrivate -q '.isPrivate' 2>/dev/null
```

If the result is `false` (public repo): run `/security-check --pr` (read-only advisory check).

- If CRITICAL advisories are found: show the warning and **pause** — let the user decide whether to proceed or stop.
- If no CRITICAL advisories: continue with push and PR.

For private repos: skip this gate entirely.
