# AGENTS.md — QuickDL (Codex)

> **Shared context:** Read `docs/agent-config/shared.md` first.
> **Agent roles:** See `docs/agent-config/agents.md`.

---

## Codex — Project-Specific Behavior

### Sandbox Constraints

Codex runs without outbound internet access. This means:
- `download_service.download_video()` cannot actually download files — use mocks/stubs in tests
- `download_service.get_video_info()` cannot call YouTube — return fixture data in tests
- Do NOT attempt to `pip install` additional packages; use what is in `requirements.txt`

### Never Modify

- `.venv/` — virtual environment contents are off-limits
- `downloads/` — output directory; do not create test files here

### After Every Change

Run both test scripts and confirm they pass:
```bash
python test_api.py
python test_env.py
```

If a test script does not exist yet for the feature being added, write one.

### Editing Rules

- Prefer editing existing files over creating new ones
- When creating a new file, verify the parent directory exists first
- All user-visible strings must use `t('key')` — never hardcode English text

### Response Language

Respond in **English**.

### Git

Follow conventions in `docs/agent-config/shared.md`.
Append to AI commits: `Co-Authored-By: Codex <noreply@openai.com>`
