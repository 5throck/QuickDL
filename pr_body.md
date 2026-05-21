**Description**
This PR aligns the project's `README.md` and `README_ko.md` documentation with the latest application behavior changes introduced in previous PRs. 

**Changes**
* Updated documentation for `install.py` to highlight that it now automatically installs `ffmpeg` via system package managers if missing.
* Corrected the "System Tray" and Desktop App usage documentation to accurately state that closing the app window now completely terminates the application, replacing the legacy "minimize to tray" behavior.

**Verification**
- [x] Passed `audit.ps1` (READMEs formatting and paths correctly preserved)

:robot: Generated with AI Assistant
