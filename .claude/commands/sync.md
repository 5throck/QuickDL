# /sync — Full Sync Pipeline

Run the full commit + PR pipeline for QuickDL.

## Usage

```
/sync "feat: description of change"
```

## What it does

1. Runs `scripts/audit.sh` — aborts if CHANGELOG or i18n keys have issues
2. Ensures `memory/YYYY-MM-DD.md` exists (creates if missing)
3. Updates `memory/MEMORY.md` index with today's entry
4. Stages all changes and commits with the provided message
5. On `master`/`main`: creates a `pr/<timestamp>-<slug>` branch, resets master, pushes the PR branch, opens a GitHub PR
6. On feature branches: pushes directly

## Steps

Run:

```bash
bash scripts/dev-sync.sh "$ARGUMENTS"
```

Report the PR URL when done.
