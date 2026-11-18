---
name: memlog
description: Write or update today's development log entry in memory/YYYY-MM-DD.md and update the MEMORY.md index.
argument-hint: "[session summary]"
allowed-tools: ["Read", "Write", "Edit", "Bash"]
---

# /memlog — Write Development Log

Write or update today's development log entry in `memory/YYYY-MM-DD.md`.

## Usage

```
/memlog
```

## What it does

1. Determines today's date (YYYY-MM-DD)
2. Opens (or creates) `memory/YYYY-MM-DD.md`
3. Fills in the log based on this session's work
4. Updates `memory/MEMORY.md` index if the date isn't already listed

## Log format

```markdown
## <Feature / Module Name>
- **Files**: path/to/file1.py, path/to/file2.js
- **Purpose**: one-line summary of what was built/changed
- **Decisions**: key technical choices and why
- **Issues**: symptom → root cause → resolution
```

## Steps

1. Check today's date: `date +%Y-%m-%d`
2. Read `memory/YYYY-MM-DD.md` if it exists
3. Write the log entry in the format above using this session's context
4. Ensure `memory/MEMORY.md` has a row for today:
   `| [YYYY-MM-DD](YYYY-MM-DD.md) | <summary> |`

Always write log files in **English**.
