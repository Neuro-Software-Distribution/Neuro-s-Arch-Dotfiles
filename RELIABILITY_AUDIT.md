# Desktop reliability audit — remediation status

Reviewed against the checkout on 2026-11-28. Source fixes and isolated regression
checks do not certify a complete installation or a live graphical session.
The 2026-11-28 documentation reconciliation inspected the current source and CI
configuration; it did not rerun the earlier audit or verify remote workflow runs.

- **IMPLEMENTED, QUALIFICATION OPEN — native notifications:** the optional C/GTK
  renderer connects to Astal, supports actions and palette changes, and falls
  back to the shell popup if it exits. The component README records successful
  live test notifications and isolated handoff coverage. Clean installation,
  multi-monitor behavior, accessibility and long-running stability remain open.
- **IMPLEMENTED, QUALIFICATION OPEN — beta utility wheel and trays:** isolated
  model/input and tray tests exist, but focus restoration, key delivery, monitor
  placement, scaling and hotplug require real Hyprland session checks. The wheel
  currently invokes fixed actions, not a persistent scratchpad service.


- **FIXED IN SOURCE — wallpaper and greeter recovery:** greeter media is staged
  and replaced only after the desktop renderer succeeds; a failed copy leaves the
  prior greeter media in place. Renderer retirement is restricted to processes
  owned by the current user and associated with the current Wayland display.
  Processes whose environment cannot be inspected are left running. Isolated
  handoff checks cover copy failure, renderer failure and another display.

- **FIXED IN SOURCE — release cache and updater launch:** release metadata is
  written to a temporary file and atomically replaced, retaining the last valid
  cache if generation fails. The terminal launcher passes the updater path as
  an argument, including when a checkout path contains shell metacharacters.

- **FIXED IN SOURCE — generated bundle accumulation:** successful, verified
  shell restarts remove older generated bundles while keeping the current and
  previous rollback bundles. Failed restarts do not prune. Interrupted builds
  also clean up their staging directory. Cleanup applies within the active
  session; old runtime directories from other sessions are not touched.

- **CHECKED LOCALLY — build and regression suites:** native preflight and the
  isolated JavaScript, Python, shell and Lua checks passed. Socket-based tests
  needed permission to run outside the execution sandbox. CI now also runs the
  existing Lua tray-keybind regression. No live shell restart, real wallpaper
  handoff, clean installation or upgrade was performed during this audit.

- **FIXED — installer final summary:** removed the undefined legacy `GTKEY`
  expansion that aborted the installer under `set -u` after printing success.
  The summary now lists Kitty on `SUPER + T` and `SUPER + SHIFT + T`, matching
  `config/keybinds.lua` and `scripts/terminal`. The installer safety harness
  executes the real summary through a declined logout, with and without a
  required restart and an active greeter. It checks completion without session
  changes. The regression reproduced the original failure in all four cases.

- **FIXED IN SOURCE — pacman hook ownership:** `install.sh` installs a root-owned
  helper at `/usr/lib/cyberarch/pkg-notify`; the hook template invokes that path
  rather than a user-writable checkout. Existing installations need the updated
  hook installed; deployed ownership was not inspected in this review.

- **FIXED — installation repository:** README installation commands clone
  `neurmancer/Neuro-s-Arch-Dotfiles`, retaining upstream credit separately.

- **OBSOLETE — failed Rio rebuild deletes the terminal:** the Rio build/removal
  path is gone. Kitty is a package dependency, and `scripts/terminal` launches it.
  This does not certify package-manager failure recovery.

- **IMPLEMENTED — regression CI and recovery infrastructure:**
  `.github/workflows/reliability.yml` runs the isolated harnesses. The updater
  stages builds and checks activation with rollback; the launcher bounds retries,
  and restart retains a healthy bundle. These supersede the historical claims
  of absent CI, supervision, and update activation checks in `NOTES.md`.

- **IMPLEMENTED IN CI CONFIG — native production build gate:** the workflow now
  has an Arch container job that installs the AGS/Astal/GJS/Sass stack, creates
  the same runtime module links as the installer, and runs `scripts/preflight`.
  The isolated harnesses remain the faster behavioural layer. This needs a
  successful GitHub run before it can be called release-certified; the checkout
  review cannot inspect remote Actions state.

- **FIXED IN SOURCE — guarded live-wallpaper handoff:** `scripts/set-wallpaper`
  now requires the replacement `mpvpaper` instance to report video parameters
  over IPC before it terminates an existing `mpvpaper` or `awww-daemon`. A
  failure kills only the unready candidate and returns an error, preserving the
  working renderer. The isolated handoff harness covers both paths. This does
  not replace live GPU/output testing.

- **OPEN — distro packaging and supported dependency set:** no package recipe,
  pinned/tested Hyprland/Quickshell/AGS/Astal/Qt combination or package build gate
  is defined. `package.json` still uses wildcard system-module dependencies and
  the installer still uses moving packages. Do not invent version pins from a
  successful local bundle. A distro release needs a maintained package repository
  and a clean-VM install/upgrade/rollback matrix before this can be marked fixed.

- **OPEN — graphical release certification:** lock/PAM recovery, suspend/resume,
  hotplug, multiple real users/sessions, GPU variants, accessibility/input methods,
  storage exhaustion/power loss and a long memory/CPU soak remain unexercised.
  Retain a known-good session in the greeter until these pass.
