# QuickDL — Agent Role Definitions

> Referenced by `CLAUDE.md`, `AGENTS.md`, and `GEMINI.md`.
> When asked to act as a specific role, apply the scope, responsibilities, and output contract defined here.

---

## Agent Roster

| ID | Role | Primary Files |
|----|------|---------------|
| `pm` | Project Manager | `docs/`, task lists, specs, plans |
| `designer` | Designer | `templates/index.html`, `static/css/` |
| `frontend` | Frontend Developer | `templates/index.html`, `static/js/script.js` |
| `i18n` | i18n Expert | `locales/*.json`, `i18n.py`, `ytdl.bat`, `ytdl.sh` |
| `security` | Security Officer | All files (read-only audit) |
| `backend` | Backend Developer | `app.py`, `download_service.py`, `desktop.py`, `cli.py`, `install.py` |
| `qa` | QA Engineer | `test_api.py`, `test_env.py`, manual test checklists |

---

## Role Definitions

### PM — Project Manager

**Responsibilities:**
- Decompose feature requests into discrete, estimable tasks
- Maintain task list (create, update, resolve tasks)
- Write specs (`docs/superpowers/specs/`) and implementation plans (`docs/superpowers/plans/`)
- Resolve blockers by coordinating between roles
- Sign off on deliverables before merge

**Entry criteria:** New feature request, bug report, or planning session

**Output contract:**
- Spec document (`YYYY-MM-DD-<topic>-design.md`)
- Implementation plan (`YYYY-MM-DD-<feature>.md`) with bite-sized tasks and checkboxes
- Updated task list

**Hands off to:** Designer (UI changes), Backend Developer (logic changes), i18n Expert (translation changes)

---

### Designer

**Responsibilities:**
- Define UI/UX for the web interface (`templates/index.html`) and desktop window layout
- Specify HTML structure, CSS class naming, component hierarchy
- Ensure accessibility (ARIA labels, contrast, keyboard nav)
- Produce annotated mockups or HTML sketches for Frontend Developer to implement

**Scope:** `templates/index.html` (structure only, no JS logic), `static/css/`

**Entry criteria:** New UI component, layout change, or visual bug

**Output contract:**
- Annotated HTML skeleton or diff showing structural changes
- CSS class/variable naming spec
- Accessibility checklist

**Hands off to:** Frontend Developer (implementation), i18n Expert (new visible strings)

---

### Frontend Developer

**Responsibilities:**
- Implement Designer specs in `templates/index.html` and `static/js/script.js`
- Wire up API calls to Flask endpoints (`/api/info`, `/api/download`)
- Use `window.I18N['key']` for all user-visible strings in JS
- Use `{{ i18n['key'] }}` Jinja2 syntax for all static strings in HTML
- Never hardcode user-visible text in English directly

**Scope:** `templates/index.html`, `static/js/script.js`, `static/css/`

**Entry criteria:** Designer hands off spec, or JS bug reported

**Output contract:**
- Working implementation matching Designer spec
- All new strings added to `locales/en.json` with appropriate key
- Notify i18n Expert of new keys

**Hands off to:** i18n Expert (new translation keys), QA Engineer (testing)

---

### i18n Expert

**Responsibilities:**
- Maintain all files in `locales/` — ensure every locale has exactly the same keys as `locales/en.json`
- Update `i18n.py` `SUPPORTED` set when adding a new language
- Add new language strings to `ytdl.bat` and `ytdl.sh`
- Review translation quality (not just machine-translate)
- Audit for missing keys: `locales/en.json` is always the baseline

**Scope:** `locales/*.json`, `i18n.py`, `ytdl.bat`, `ytdl.sh`

**Entry criteria:** New language requested, new translation keys added by Frontend/Backend, i18n bug reported

**Key audit command:**
```bash
python -c "
import json, pathlib
base = json.loads(pathlib.Path('locales/en.json').read_text(encoding='utf-8'))
for p in sorted(pathlib.Path('locales').glob('*.json')):
    other = json.loads(p.read_text(encoding='utf-8'))
    missing = set(base) - set(other)
    extra = set(other) - set(base)
    status = 'OK' if not missing and not extra else f'MISSING={missing} EXTRA={extra}'
    print(f'{p.name}: {status}')
"
```

**Output contract:**
- All locale files have identical key sets to `en.json`
- `SUPPORTED` set in `i18n.py` matches the set of locale files
- Shell scripts updated for new languages

**Hands off to:** QA Engineer (validation)

---

### Security Officer

**Responsibilities:**
- Audit code for injection risks (URL params passed to subprocess, path traversal)
- Review `download_service.py` for unsafe yt-dlp option handling
- Check `app.py` for missing input validation on API endpoints
- Scan `requirements.txt` for known-vulnerable dependency versions
- Flag issues; does NOT implement fixes (hands off to Backend Developer)

**Scope:** All Python files (read-only audit)

**Entry criteria:** New feature touching external input or file system, periodic security review, dependency update

**Output contract:**
- Security audit report with severity (Critical / High / Medium / Low)
- Specific file + line references for each finding
- Recommended fix per finding

**Hands off to:** Backend Developer (fixes), PM (severity triage)

---

### Backend Developer

**Responsibilities:**
- Implement Flask routes in `app.py`
- Maintain download logic in `download_service.py` (yt-dlp integration)
- Manage desktop app lifecycle in `desktop.py` (Flask thread, pywebview, pystray queue)
- Maintain `cli.py` (argparse interface) and `install.py` (cross-platform setup)
- Ensure Python 3.8 compatibility (`Optional[str]`, no walrus operator in hot paths, etc.)

**Scope:** `app.py`, `download_service.py`, `desktop.py`, `cli.py`, `install.py`, `i18n.py`

**Entry criteria:** New API endpoint, download logic change, desktop app bug, installer issue

**Output contract:**
- Passing `python test_api.py` and `python test_env.py`
- No new bare `except:` clauses
- New user-visible strings use `t()` — not hardcoded

**Hands off to:** i18n Expert (new keys), QA Engineer (testing), Security Officer (new external input)

---

### QA Engineer

**Responsibilities:**
- Write and maintain test scripts (`test_api.py`, `test_env.py`)
- Validate cross-platform behavior (document Windows vs macOS/Linux differences)
- Run i18n completeness audit (see i18n Expert audit command)
- Verify installer idempotency (run `install.py` twice, confirm no errors)
- Test CLI with valid and invalid URLs

**Scope:** `test_api.py`, `test_env.py`, manual test checklists

**Entry criteria:** After any Backend or Frontend change, before release

**Test checklist template:**
```
[ ] python test_api.py  — all assertions pass
[ ] python test_env.py  — all assertions pass
[ ] QUICKDL_LANG=en python cli.py --help  — English output
[ ] QUICKDL_LANG=ko python cli.py --help  — Korean output
[ ] python install.py (second run)  — reports "already exists", no errors
[ ] All locale files: same 49 keys as en.json
[ ] ytdl.bat exists and has correct .venv check logic
[ ] ytdl.sh exists and is executable
```

**Output contract:**
- Test run output (pass/fail per test)
- List of any cross-platform issues found

**Hands off to:** Backend Developer or Frontend Developer (bug fixes), PM (release decision)
