---
name: post-write
description: Run the Post-Write quality gate chain (audit → pytest → test_app) manually. Use after any Write or Edit when hooks are unavailable (Desktop App, Gemini CLI).
argument-hint: "[changed file]"
allowed-tools: ["Bash"]
---

Load and apply the Post-Write Quality Check skill from `skills/post-write-check/SKILL.md`.

Read the file at `skills/post-write-check/SKILL.md` now and follow all instructions within it.

The changed file (if provided) is: $ARGUMENTS
