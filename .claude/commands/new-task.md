---
name: new-task
description: Create a new structured task for the current session using TaskCreate.
argument-hint: "<task title>"
allowed-tools: ["TaskCreate"]
---

# /new-task — Create a New Task

Create a structured task entry for the current session.

## Usage

```
/new-task "Task title"
```

## What it does

1. Calls `TaskCreate` with the provided subject and a prompted description
2. Sets the task to `pending` (default)
3. Reports the task ID for future reference

## Guidelines

- Write task subjects in imperative form: "Add Thai locale", not "Adding Thai locale"
- Keep subjects concise (under 60 characters)
- Description should clarify scope, files affected, and acceptance criteria
- Use `TaskUpdate` to set `in_progress` before starting work
- Use `TaskUpdate` to set `completed` immediately after finishing

## Steps

Use the TaskCreate tool with:
- `subject`: `"$ARGUMENTS"` or prompt the user if empty
- `description`: describe scope, files affected, acceptance criteria

Confirm the created task ID to the user.
