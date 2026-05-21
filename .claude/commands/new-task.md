# /new-task — Create a New Task

Create a structured task entry for the current session.

## Usage

```
/new-task "Task title" "Task description"
```

Or without arguments — Claude will prompt for details.

## What it does

1. Calls `TaskCreate` with the provided subject and description
2. Sets the task to `pending` (default)
3. Reports the task ID so it can be referenced later

## Guidelines

- Write task subjects in imperative form: "Add Thai locale", not "Adding Thai locale"
- Keep subjects concise (under 60 characters)
- Description should clarify scope and acceptance criteria
- Use `TaskUpdate` to set `in_progress` before starting work
- Use `TaskUpdate` to set `completed` immediately after finishing

## Steps

Use the TaskCreate tool with:
- `subject`: "$ARGUMENTS" (first part) or prompt the user
- `description`: describe scope, files affected, acceptance criteria

Then confirm the task ID to the user.
