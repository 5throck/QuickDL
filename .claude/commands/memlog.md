# /memlog — Write Development Log

Write or update today's development log entry in `memory/YYYY-MM-DD.md`.

## Usage

```
/memlog
```

## What it does

1. Determines today's date (YYYY-MM-DD)
2. Opens (or creates) `memory/YYYY-MM-DD.md`
3. Asks what was done in this session and fills in the log
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
3. Ask the user to summarize the session's work (or use conversation context)
4. Write the log entry in the format above
5. Ensure `memory/MEMORY.md` has a row for today:
   `| [YYYY-MM-DD](YYYY-MM-DD.md) | <summary> |`

Always write log files in **English**.
