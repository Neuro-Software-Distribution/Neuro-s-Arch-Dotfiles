# NeurOS redesign — remaining work

Reviewed against version 2.46 on 2026-11-28. This section records the current agreed direction and takes
precedence over the older widget guide below and conflicting earlier design
notes. Implementation status describes the checkout, not a confirmed live session.

## Current implementation snapshot — 2026-11-28

- The first retro-futurist design pass is implemented in the system monitor:
  cut-corner dark console, palette-driven animated tab attention and keyboard
  navigation (1–4 or left/right for views, up/down for processes and startup,
  Enter toggles a startup entry, Escape closes). It retains pointer actions.
  Native preflight and focused isolated tests passed; live visual, keyboard and
  small-display qualification remain open. Other surfaces are not yet migrated.

- The three independently configurable trays, shared attention effects, upper-right
  messages panel and prototype design studies are in source. The redesign remains
  incomplete: inherited controls and expanded views still need a coherent treatment.
- The beta utility wheel is implemented at `Super + Space` (IPC
  `utility-wheel`). Six point-top slots launch terminal, forecast, apps, audio,
  system and player through fixed seed actions. Q/W/E/A/S/D, pointer, Tab,
  Enter and Escape are supported. It is not yet a configurable scratchpad system.
- A C/GTK notification renderer can be enabled and falls back to the existing
  shell popup on failure; notification history and application tray remain in
  the shell. See `components/notifications/README.md` for activation and limits.
- `scripts/preflight` builds the AGS shell, stylesheet and, when available, the
  native notification renderer. CI defines isolated regressions and an Arch
  native preflight; remote CI and live compositor behavior were not checked in
  this documentation review. See `RELIABILITY_AUDIT.md` for qualification gaps.
- The following long configuration guide is historical, not a verified reference
  for every current widget or setting. Check source and README before changing
  configuration; removed map/gauges and older dock/notification details may persist.

## Agreed direction

- Group related desktop utilities into independently toggleable **util-trays**.
  Each tray gets its own configurable hotkey. Existing individual utility
  shortcuts remain independent and usable while the containing tray is closed
  (for example, `Super + Shift + W` opens the full weather view).
- Aim for a William Gibson-inspired personal working console, fused with the
  angular geometry and selective neon of CP2077. Detailed visual treatment is
  still to be explored; functionality comes first.
- Bottom-left: one controls tray, excluding messages.
- Right side: a second tray containing weather and **NNET**, retaining compact
  access and expanded views. The current market widget is the existing baseline;
  NNET will replace its financial-market purpose with technical research tracking.
- Upper-left: bring back CPU/RAM monitoring as a separate optional system tray.
- Upper-right: relocate messages into the space vacated by the map and redesign
  that interface completely. Keep the existing hover behavior.
- Remove the map completely and remove the dedicated network-status/speed widget.
  Keep Wi-Fi management in the controls tray.

## Completed baseline

- [x] Removed the Kitty, Arctic and Bloodmoon desktop themes, their bundled
  wallpapers, selector artwork, terminal color presets and theme-specific code.
  Kitty terminal support remains. Six palettes remain: NETWATCH, BLADE,
  SYNTHWAVE, JOHNNY, GHOST and NSD. Unavailable saved presets fall back to
  NSD while retaining explicit user color overrides. Previously installed
  wallpaper copies outside the repository were not deleted.
- [x] Fixed the installer's undefined `GTKEY` summary expansion and corrected its
  terminal shortcut labels. The installer safety harness covers all four
  restart/greeter combinations through declined logout. Audit findings were
  reconciled in `RELIABILITY_AUDIT.md`.
- [x] Implemented `components/modules/controls-tray.ts`, replacing the two
  separate bottom-left dock windows with one tray in `core.ts`.
- [x] Grouped volume/microphone access, brightness, music, recording, Wi-Fi,
  Bluetooth and power. Excluded messages without removing their existing hotkey.
- [x] Added `Super + Alt + C` (`hud.controls`, IPC request `controls-tray`),
  configurable through the existing keybind settings. It targets the monitor
  under the pointer; tray state is independent per monitor and resets on restart.
- [x] Added the angled upper-right corner, screen-edge anchoring and removed the
  tooltip. Current interaction is **peek → hover reveals tab → click opens
  widgets**. Hover alone never opens widgets. A clicked-open tray stays open
  after pointer exit; clicking again or using its hotkey closes it. A closed tab
  retracts to the small edge strip after the pointer leaves.
- [x] Kept individual utility shortcuts working independently. Tray motion
  follows the existing modal animation setting; hidden controls pause polling,
  and monitor removal cleans up subscriptions and timers. Global widget hiding
  and recording visibility rules also apply to the tray and its tab.

## Weather / markets tray implementation — 2026-10-13

- [x] Added the lower-right **WEATHER / MARKETS** tray with the same idle peek,
  hover-to-reveal-tab, click-to-open interaction. `Super + Alt + W` toggles it on
  the pointer's monitor (`hud.information`, IPC `information-tray`). Controls and
  information trays have separate state, using shared `util-tray.ts` behavior.
- [x] Replaced the old right-side windows with compact weather above markets.
  Weather click and market double-click open their existing expanded views;
  `Super + Shift + W` and `Super + Shift + G` remain independent of tray state.
- [x] Removed map rendering/generation, the bundled map image, network-status
  drawing and its speed/status polling from the former sidepanel. Weather now
  lives in `weather.ts`; saved city files remain compatible. Clock/date stays
  with weather; right-click the clock for time settings, or weather for city selection.
- [x] Decoupled saved location/watchlist initialization from compact widget
  construction. Periodic data requests run only while a compact widget or its
  expanded view is visible. Removed the obsolete network color controls and
  relabeled shared image tint/forecast settings.
- [ ] Validate both trays in the live compositor, including pointer regions,
  mixed DPI, right-edge placement, opening full utilities from closed trays,
  hotplug and recording/global-hide behavior. The upper-right area is available
  for the planned messages redesign; the initial relocation is recorded below.

## Next: finish the controls tray prototype

- [x] Moved weather/markets to the vertical center of the right screen edge.
  Its vertical tab now peeks horizontally and the bundle opens leftward; the
  handle remains centered with the widgets open. Controls remain bottom-left.
- [x] Restyled both handles as restrained console panels: clipped corners,
  numbered utility labels, palette-colored edge accents, etched divider lines,
  and an open/closed latch. Styling uses static vector paint and retains the
  fixed-size hover canvas. A GTK preview checked the actual weather/market
  layout, tab lettering and centered handle; live compositor verification remains.

- [x] Reworked shared tray motion after the reported lag/jitter: fixed-size tab
  canvas, elapsed-time GTK frame-clock animation (120 ms maximum), no delayed
  pointer-exit timer, and stable hover geometry during motion. The content panel
  keeps GTK's native slide; widget construction remains lazy and reused.
- [x] Replaced HUD screenshot/alpha-mask input calculation with cached geometric
  outlines for tabs and dock controls, plus clipped widget allocations. Hidden
  content, angled corners and dock gaps remain click-through on both HUD layers;
  app-window overlaps are subtracted on the bottom layer. Input is updated with
  allocation rather than waiting for idle after each resize.
- [x] Regression tests cover fixed hover allocation, delayed frames, reversals,
  reduced motion, independent tray hotkeys, scaled outlines and input clipping.
  An isolated GTK check confirmed no hover reallocations, stable input during
  motion, panel expansion/collapse and hide/show cleanup. Live Wayland frame
  pacing and pointer behavior still need checking below.

- [ ] Check the current peek/hover/click behavior in the real Hyprland session:
  screen-edge access, fast pointer crossings, tab-to-widget movement, clicked-open
  persistence, closing while hovered, and opening utilities from a closed tray.
- [ ] Check the Wayland input region during extension/retraction: the angled cut
  and hidden content must not intercept clicks; controls must remain clickable.
- [ ] Verify mixed-DPI/multiple monitors, hotplug, global hide/show, HUD layers,
  recording transitions and reduced-motion behavior. Headless GTK and mocked
  tests do not certify these compositor interactions.
- [ ] Refine the tray's internal arrangement and visuals with user feedback.
  Current controls reuse the inherited dock artwork; the small tab change does
  not complete the Gibson-influenced redesign.
- [ ] Decide which parts of this interaction become shared tray infrastructure
  as further trays are added. The first two now share `util-tray.ts`. Retain the controls behavior;
  do not make hover open widgets again.

## Then: remaining desktop composition

The upper-left CPU/RAM tray is now implemented. It opens downward from a top-edge
peek/tab, uses two segmented meters, and has its own configurable shortcut:
`Super + Alt + S` (`hud.system`, IPC `system-tray`). Clicking the panel opens the
existing system/process monitor; `Super + Shift + C` remains independent. It
starts collapsed, follows global widget/recording visibility, and maintains state
per monitor. One shared `/proc` sampler runs only while a panel is mapped, at one
sample per second; CPU starts with an unavailable value until two counter samples
exist. RAM uses `MemTotal - MemAvailable` and reports used/total GiB.

Top-edge allocation, click/hover state, scaled input shapes, sampler cleanup,
live CPU/RAM rendering and Lua shortcut registration have been checked. The panel
uses existing dock/green palette colors; obsolete CPU/RAM color keys caused the
initial blank-panel rendering bug and are no longer referenced. All tray actions
now live in the final Lua registry and appear in keybind settings, correcting the
earlier overwritten tray-action list. Live multi-monitor/hotplug checks remain.

Weather/market grouping, independent initialization, and map/network-indicator
removal are implemented above. Retain their compact-to-expanded interactions
while refining visuals. Remaining composition work:

1. **Redesign and relocate messages to the upper right.** The existing window
   is now anchored at the upper-right and opens on the messages tab; its apps
   tab and menus remain available. A flat cut-corner console surface replaces
   the projected phone artwork, and the obsolete dock notification tile is removed.
   The input region follows the panel outline and monitor scale. This redesign is
   untested; retain its existing hover behavior and complete live compositor checks. Preserve notification
   actions/history and existing message shortcuts. The current messages view
   also contains the application system tray: decide how those app icons/menus
   fit as the design evolves.
2. **Refine the upper-left CPU/RAM tray** after live use. Its functional baseline
   is implemented above; visibility preferences are described below.
3. **Replace the market widget with NNET.** Redesign its compact tray and
   expanded application around keeping track of technical advances. Remove the
   financial-market functionality and use recent arXiv articles about kernels,
   computational mathematics and related concepts as the research feed. Design
   the discovery, refresh, article details and reading interactions as part of
   this work; keep the existing market implementation until its replacement is
   ready. Existing market references below describe the current implementation,
   not a requirement to retain market data or the financial watchlist.

## Shared design and later work

The aesthetic direction uses the supplied concept art with Akira, Ghost in the
Shell and Neuromancer as influences: dark console surfaces, intentional cut
corners, technical registration marks, readable typography and theme-driven
neon. The current shared tray, compact weather and messages now include a small
common registration motif; this is an initial pass, not a completed redesign.
The same motif now appears on shared glass dialogs. The system-monitor tabs use
the theme's active accent for hover and include a shape marker for selection;
weather and system-monitor pulse effects respect the modal animation setting.
The shell bundle, stylesheet and local regression tests pass. These changes
still need visual and interaction checks in a live Hyprland session.

- [ ] Establish reusable surface, text, accent, focus, border and status styles.
  Keep cut corners, configurable glow, clear keyboard focus and reduced-motion
  behavior. Validate every retained palette over varied wallpapers.
- [ ] Apply the agreed visual language to expanded weather/NNET, then quick
  controls and the Netrunner Den, preserving their existing capabilities.
- [x] Added independent saved visibility preferences for the controls, weather /
  markets and CPU / RAM trays in Theme Settings → Configuration. All three default
  to visible; the global hide shortcut still applies. A disabled tray stays hidden
  across recording and monitor transitions and ignores its tray toggle until
  re-enabled. Individual utility shortcuts remain independent. Live validation is
  pending.
- [x] Implemented the separate beta utility wheel with fixed seed actions.
- [ ] Validate live input and focus, decide assignments and scratchpad behavior,
  and implement persistence/customization if the beta interaction is accepted.
- [ ] Reconcile README, `DESIGN_SHIT.md` and the historical guide below as the
  redesign lands. The older guide still contains removed gauge/Rio references;
  treat those as historical, not current implementation instructions.

## Verification and release limits

The controls interaction regression, AGS/SCSS build and isolated GTK sizing checks
have been exercised. Live Wayland appearance, input behavior and hardware/session
qualification remain pending. No full installation or logout was performed.
Packaging, a tested dependency set, clean-VM installation/upgrade/rollback,
lock/PAM recovery, suspend/resume and broader hardware/accessibility/soak testing
remain open as recorded in `RELIABILITY_AUDIT.md`.

All four planning documents are currently ignored by the repository’s Markdown
ignore rule; updates remain local unless their tracking policy is changed.

---

## Current color scheme — NETWATCH HUD

Main red, yellow and blue/cyan accents from `components/modules/colors.ts`
(`PALETTES.NETWATCH`):

| Color | Hex | Palette role |
| --- | --- | --- |
| Red | `#FF2A3A` | `red` |
| Yellow | `#FFDE69` | `netinfo` |
| Blue / cyan | `#5EF4F8` | `cyan` |

## Audit reconciliation — 2026-10-13

Current remediation status is maintained in [RELIABILITY_AUDIT.md](RELIABILITY_AUDIT.md).
The following findings from the original review are no longer open source defects:

- **Pacman hook:** the installer deploys a root-owned helper to
  `/usr/lib/cyberarch/pkg-notify`, and the hook invokes that installed copy.
  Existing deployed hooks were not inspected; they need the updated installation.
- **Installation instructions:** the README clones `neurmancer/Neuro-s-Arch-Dotfiles`.
  Upstream attribution remains separate.
- **Rio rebuild:** the old build/removal branch is gone; Kitty is the packaged terminal.
- **Installer summary:** the undefined `GTKEY` expansion is removed. The safety
  harness covers both restart states and both greeter states through declined logout.

## Update and pipeline context

`updater.sh` derives GitHub release requests from the checkout's `origin`.
It stages a build, requires a clean fast-forward update, and rolls back a failed
activation. `.github/workflows/reliability.yml` runs isolated regression checks.
Remote GitHub settings and workflow runs were not inspected. Existing CyberArch
configuration paths, instance names and system integration names are shared with
upstream, so changing a remote alone does not isolate installations.

#### NSD Colors

  blue  #5A96FF
  purple  #b570ff
  green  #00EB74



## Historical Cyberpunk HUD and widget configuration guide

**Historical reference:** reviewed in October; portions describe removed or
replaced UI and have not been comprehensively revalidated. Prefer the current
snapshot above, `README.md`, and the implementation when details conflict.

Source reference: this checkout, reviewed 2026-10-09. Paths below are relative
to the repository unless they start with `~`. The Cyberpunk “bar” is an AGS /
Astal GTK 3 application composed of separate windows, not a Waybar configuration.
Most visible widgets use Cairo drawing code, so their borders, fonts, shapes and
internal spacing are controlled by TypeScript rather than CSS.

### Start here: settings, files and reloads

Open **Theme Settings** with the default `Super + Shift + Backspace` binding.
The modifier and bindings can be customized, so check `config/keybinds.lua` and
`~/.config/hypr/user.lua` if that shortcut differs on your installation.
Settings tabs are **CONFIGURATION**, **COLORS**, **KEYBINDS**, **WINDOW MANAGEMENT**
and **WALLPAPER**. Configuration covers gauge assignments, animations and sound.
Colors contains presets and individual widget color controls.

You can also open settings from a terminal in the running desktop session:

```bash
printf '%s\n' 'modal themesettings' | socat - UNIX-CONNECT:"$XDG_RUNTIME_DIR/astal/cyberpunk.sock"
```

| What to change | File / location |
| --- | --- |
| Widget creation, screen anchors, shared outer margins | `core.ts`: `createMonitorHud()`, `surface()`, `WRAP_MARGINS` |
| Global size / monitor scaling | `env.ts`: `CYBER_SCALE`, `scaleOf()`, `winScale()` |
| Individual widget geometry and drawing | Corresponding file in `components/modules/` below |
| GTK wrapper spacing and applicable GTK styles | `components/style/cyber.scss` |
| Palette defaults, derived colors and transparency | `components/modules/colors.ts` |
| Persistent animation, audio and gauge preferences | `USER_DIR/user_config.lua`, handled by `config.ts` |
| Persistent palette and color overrides | `USER_DIR/user_colors.lua`, handled by `colors.ts` |
| Application-window borders, opacity, corners and shadows | `USER_DIR/wm_config.lua`, handled by `wmconfig.ts` |
| Shared drawing fonts | `components/modules/fonts.ts` |
| Desktop window gaps | `theme.lua`: `general.gaps_in` / `general.gaps_out` |

`USER_DIR` means `${XDG_CONFIG_HOME:-$HOME/.config}/cyberarch`, normally
`~/.config/cyberarch`. `CYBER_DIR` is the running checkout's build-time `SRC`.
The canonical theme path is `~/.config/hypr/themes/cyberpunk`; verify where it
points before editing if you have multiple checkouts:

```bash
readlink -f ~/.config/hypr/themes/cyberpunk
```

UI changes to colors/configuration generally apply immediately and save their
preferences. For TypeScript, SCSS or manually edited preference files, restart
from the checkout you edited:

```bash
sh scripts/restart
```

This stops only the named `cyberpunk` AGS instance and launches this checkout.
`scripts/preflight` bundles the shell and compiles `cyber.scss` into a staging
directory. The launcher supplies the generated CSS to `core.ts`; direct startup
can compile it into the session runtime directory. Edit the SCSS source. There
is no source/style watcher. Launcher output goes to
`${XDG_STATE_HOME:-$HOME/.local/state}/cyberarch/shell.log`, with the preceding
attempt in `shell.previous.log`.
Back up saved preferences before manual changes, and avoid editing them while
the settings UI is saving the same file.

### Colors, transparency and fonts

Choose a preset first, then customize individual colors. Presets are `NETWATCH`,
`BLADE`, `SYNTHWAVE`, `JOHNNY`, `GHOST` and `NSD`.
Choosing a preset clears individual override flags; the Colors reset button
applies NSD. New installations default to NSD; existing saved presets remain selected. Palette selection also invokes shell/terminal theming and,
through the settings UI, theme wallpaper selection.

`colors.ts` stores `NEON` colors as RGB values from 0–255 and exposes `USER`
colors normalized to 0–1 for Cairo. `PALETTES` defines preset values; `DERIVE`
links child colors to master colors unless a preset pins them or a user overrides
them. For example, `dockv` / `dockh` derive from `dock`, their hover colors from
`press`, and `xpbar` from `badge`. Saved colors can supersede source defaults.

| Widget / role | Color keys in Colors / `colors.ts` |
| --- | --- |
| Shared accent / modal background / text / hover | `cyan`, `modalbg`, `glassacc`, `modalhov` |
| Application wheel | `wheelbg`, `wheelfg` |
| Gauge badge / XP / health / RAM / stamina | `badge`, `xpbar`, `cpu`, `ram`, `stamina` |
| Vertical dock / hover | `dockv`, `dockvh` |
| Horizontal dock / hover | `dockh`, `dockhh` |
| Launcher image / label | `launchico`, `launchlbl` |
| Clock / city / weather / map accent / tile tint | `mapclock`, `mapcity`, `mapwx`, `mapaccent`, `maptile` |
| Network labels / chip / download / upload | `netinfo`, `netchip`, `netdown`, `netup` |
| Markets accent / hover | `mktacc`, `mkthov` |
| Update banner background / foreground / icon | `aurbg`, `aurfg`, `auricon` |
| Update banner labels / title / outline | `aurlbl`, `aurtitle`, `aurline` |
| Notification badge / phone / mail / heads-up | `notifbadge`, `notifphone`, `notifmail`, `notifheads` |
| Notification title / foreground / background / labels | `notiftitle`, `notiffg`, `notifbg`, `notiflbl` |
| Player title / header background / accent | `radiotitle`, `radiohdrbg`, `radioacc` |
| Player volume / track text / track background / controls | `radiovol`, `radiotrkfg`, `radiotrkbg`, `radioctl` |
| System/settings veil / alert and region frame / alert text | `sysveil`, `overlay`, `f25` |
| Master HUD / press accents | `dock`, `press` |
| General text, highlights and legacy/shared roles | Remaining `NEON` keys, including `red`, `green`, `blue`, `magenta`, `amber`, `white`, `dim`, `grid`, `hudcyan`, `appsred`, `glyphcol`, `msggrey`, `notifgrey`, `goldf`, `goldd`, `dimred`, `darkred`, `aurgreen`, `aurbrt`, `aurblack`, `aurwht`, `notifred`, `notifyel`, `notifcyn`, `pure` |

Only `modalbg`, `wheelbg`, `maptile`, `aurbg`, `notifbg`, `radiohdrbg` and
`radiotrkbg` have saved alpha controls (`USER_A`, range 0–1). The final drawing
may multiply alpha by its own opacity. Map alpha controls tint strength, not a
universal window-opacity setting. Preset-specific behavior also lives in
`GLASS_ALPHA`, `GLASS_MODE`, `MENU_BG`, `MAP_ACCENT`, `HUD_SOFT` and tint tables.

For your NSD colors, the RGB equivalents are blue `[90, 150, 255]`, purple
`[193, 112, 255]`, green `[0, 235, 116]`. Enter their hex values in the Colors UI.
For a manual override, edit the existing matching lines in `user_colors.lua`
and include its override flag, for example:

```lua
users["dockv"] = { 90, 150, 255 }
over["dockv"] = true
users["dockh"] = { 193, 112, 255 }
over["dockh"] = true
users["stamina"] = { 0, 235, 116 }
over["stamina"] = true
```

Keep the rest of the saved file, including its palette declaration. The loader
parses a restricted line format, so preserve double-quoted keys, integer RGB
channels, and the generated file structure. Merely changing a derived color
without its override flag can let palette derivation replace it.

`fonts.ts` exports families such as `TITLE = "Quantico"`, `MONO = "Tektur"` and
`ICONF = "Symbols Nerd Font"`, plus specialist display fonts. Change the family
there for consumers of that constant. Font sizes live in each widget's
`tiltText()`, `txt()`, `pango()` or `setFontSize()` calls. Some widgets use their
own font constants. The SCSS global font family affects GTK text, not all Cairo
text. After increasing font size, check clipping and clickable-region alignment.

### Size, placement, margins, padding and borders

Automatic scale is `min(monitor width / 1920, monitor height / 1080)` in logical
monitor coordinates. To test a fixed scale for the next launch:

```bash
CYBER_SCALE=0.9 sh scripts/restart
```

Only a positive value overrides auto-scaling. Persist the environment value in
your session/startup configuration if wanted. This scales widgets that use the
shared scale helpers; fixed CSS pixel margins are not automatically multiplied.

The main HUD is created per monitor. `WRAP_MARGINS` values are
`[top, right, bottom, left]`, multiplied by that monitor's scale:

| Surface | Anchor / current outer placement |
| --- | --- |
| `monitors` | Top-left; `[20, 0, 0, 20]` |
| `sidepanel` | Top-right; `[26, 28, 0, 0]` |
| `markets` | Top-right; window `margin_top: Math.round(560 * S)` |
| `toggles` (vertical dock) | Bottom-left; `[0, 0, 0, -5]` |
| `hordock` (horizontal dock) | Bottom-left; SCSS `.hordock-wrap { margin: 0 0 8px 66px; }` |
| `launcher` | Bottom-right; `launcher.ts` wrapper right margin `3 * S` |

For example, change `monitors: [20, 0, 0, 20]` to
`monitors: [32, 0, 0, 36]` to move the gauges down 12 and right 16 design units.
Change `sidepanel`'s second value to move it inward from the right edge. To lift
the vertical dock, give its bottom entry a positive value. GTK may constrain
negative margins; prefer positive offsets when repositioning it.

For the horizontal dock, an SCSS adjustment could be:

```scss
.hordock-wrap { margin: 0 0 20px 82px; }
```

This lifts it 12 CSS pixels and moves it right 16 relative to the existing rule.
Use one outer-spacing mechanism deliberately: GTK widget margins, window
margins, CSS margins and Cairo offsets can combine. Some SCSS comments still
say bottom-right for the horizontal dock; the actual anchor in `core.ts` is
bottom-left.

For internal size and spacing, edit the owning module's `W`, `H`, layout arrays,
row heights and drawing coordinates. `makePlane({ w, h, yaw, pitch, roll, focal,
dist, pad })` in `proj.ts` controls the projected canvas: yaw/pitch/roll set tilt,
focal/dist affect perspective, and pad adds room around the projection. Plane
padding is not a screen-edge margin. Enlarging the allocation alone does not
redistribute hardcoded content coordinates.

For a **Cairo border**, change the relevant `ctx.setLineWidth(...)` or width
argument to `strokePath(ctx, plane, points, color, alpha, width, close)` in the
widget. For example, increasing an outline width from `1` to `2` thickens that
stroke. Frame polygon coordinates / chamfer constants control cut corners;
`setSourceRGBA()` and gradient alpha stops control fills and glow. Adjust glow
strokes separately from the main outline. Update drawing bounds and hit regions
together when moving or resizing controls.

For an actual **GTK border**, edit the matching SCSS selector's `border`,
`border-radius`, `padding`, `margin` or `box-shadow`. Many `.dock-tile`,
`.modal-*`, `.city-*`, `.quest-wrap` and `.topclock-wrap` rules are not the
rendering path of the current Cairo widgets. Confirm a class is instantiated
before expecting its CSS to work:

```bash
rg -n 'dock-tile|className|setLineWidth|strokePath|makePlane' components/modules/dock.ts
```

For **application-window borders**, use Window Management. Those settings do
not change the drawn HUD frames. `wmBorders`, `wmBorderSize`, `wmBorderColor`,
`wmCorners`, `wmRounding`, `wmGlow*`, `wmShadow*` and `wmOpacity*` are handled by
`wmconfig.ts`. Corner choices are `round`, `bevel`, `sharp`; opacity application
modes are `off` (global only), `only`, `except`. Preserve generated `t["key"]`
touched flags when manually editing `wm_config.lua`. Desktop gaps are separate:
`theme.lua` currently uses `gaps_in = 12`, `gaps_out = 24`.

### Every HUD widget and its controls

#### System gauges — `components/modules/monitors.ts`

The top-left cluster contains the workspace badge, XP/storage strip, health/CPU
bar, RAM bar and stamina/battery bar. In Configuration, assign a metric to each:

| Setting | Default | Allowed values |
| --- | --- | --- |
| `gaugeBadge` | `workspace` | `workspace`, `cputemp`, `cpu`, `ram`, `ramfree`, `swap`, `disk`, `battery`, `gpu`, `load` |
| `gaugeXp` | `disk` | `cpu`, `cputemp`, `ram`, `ramfree`, `swap`, `disk`, `battery`, `gpu`, `vram`, `load`, `net` |
| `gaugeHealth` | `cpu` | Same bar metrics as `gaugeXp` |
| `gaugeRam` | `ram` | Same bar metrics as `gaugeXp` |
| `gaugeStamina` | `battery` | Same bar metrics as `gaugeXp` |

For example, edit these existing entries in `user_config.lua` to show temperature
in the badge and GPU load in the stamina slot:

```lua
cfg["gaugeBadge"] = "cputemp"
cfg["gaugeStamina"] = "gpu"
```

The base canvas is `W = 500`, `H = 96`. `X0`, `MAIN`, `RAMX`, `BATX` and the
local drawing coordinates set the individual bar positions; `plane` sets tilt.
Use the gauge color keys above. Stamina also uses threshold colors from
`goodLowColor()` / `goodHighColor()` and override logic, so inspect those when
changing warning colors. `animGauge` controls its animation. Disk usage reads
`/`; change `readDisk()` to target another filesystem. Battery, temperature and
GPU readers use `/sys`, while memory/network/load readers use `/proc`; inspect
those readers if a metric is unavailable. `NET_CAP` controls network gauge
normalization. Shared CPU/RAM sampling lives in `sys.ts`.

#### Clock, minimap, weather and network — `components/modules/sidepanel.ts`

These are subwidgets of one top-right surface. Base size is `320 × 530`.
`MAP_DX`, `CONN_DX` / `CONN_DY`, `ICON_DX` / `ICON_DY`, `MX0` / `MY0` / `MX1` /
`MY1` and the `minimap`, `plane`, `connPlane`, `iconPlane` projections determine
internal placement. Move the complete group using `WRAP_MARGINS.sidepanel`.
Colors are the map and network groups listed above.

Open city selection with the `weather` request, detailed forecast with
`forecast`, and clock settings with `clock`. The location is saved to
`USER_DIR/city.json`, with fallback to `config/city.json`. Fields are `name`,
`full`, numeric `lat` / `lon` for weather, numeric `mapLat` / `mapLon` for the map,
and `mapCache`. The checked-in fallback is Edogawa, Tokyo. Preserve the shape
when editing; the city picker is the simplest way to update related fields.
Map tiles cache under `${XDG_CACHE_HOME:-$HOME/.cache}/cyberpunk-maps`.

Weather refreshes every 30 minutes, connection name every 15 seconds, and traffic
rates every second. Change the intervals beside `SidePanel()` to adjust these.
Network traffic follows the default route (`netIface()`), not a saved interface
setting. Clock formatting lives in this module; timezone, NTP and manual time
controls live in `timeset.ts` and operate on the system clock through
`timedatectl`. The weather location does not itself set the system timezone.
City/forecast dialog geometry is in their `createModal()` specifications and
associated drawing code; clock dialog geometry is in `timeset.ts`.

#### Markets and news — `components/modules/markets.ts`

Open with `markets`. Saved pins are `USER_DIR/markets.json`:

```json
{"stocks":["NVDA","INTC"],"crypto":["bitcoin","ethereum"]}
```

Stocks use symbols and crypto uses provider IDs. `MAXPIN = 5` limits each list;
use the modal's pin controls or edit the file and restart. `MARKET_PLANE` is
`320 × 196`; the window's top offset is in `core.ts`. Row/chart geometry and
click targets live in `MarketsPanel()` / `drawMarketModal()`. `mktacc` and
`mkthov` control accents, while `UP`, `DOWN`, `UP_RGB`, `DOWN_RGB` explicitly set
gain/loss colors. Quotes refresh every 60 seconds. `GLOBAL_FEEDS`,
`EXTRA_NEWS_FEEDS` and `NEWS_BATCH_QUERIES` define news sources; local news reads
the saved city. `BROWSE_CHUNK` and `NEWS_CHUNK` set paging sizes.

#### Vertical and horizontal docks — `components/modules/dock.ts`

Vertical tiles: volume (`vol`), brightness (`brt`), notifications
(`notification`), music (`music`). Horizontal tiles: recording (`rec`), Wi-Fi
(`wifi`), Bluetooth (`bt`), power (`pwr`). Edit `VERT_TILES` / `HORIZ_TILES` for
icons, displayed shortcut labels and state checks; inspect each dock's input
handlers for click/scroll actions. Changing a displayed `sc` label does not
change the actual keybinding.

Vertical slot size is `VSW = 44`, `VSH = 42`, gap `VG = 6`. Horizontal size is
`HSW = 50`, `HSH = 48`, gap `HG = 8`. `BADGE = 19`, `BGAP = 5` control shortcut
badges. `VLAYOUT` / `HLAYOUT` define tile coordinates and `vsp` / `hsp` define
tilt. The plane dimension formulas currently assume four slots: update those,
layout arrays and event handling together when adding/removing tiles.
`vertSlotFrame()` / `horizSlotFrame()` define beveled outlines. Use `dockv`,
`dockh`, `dockvh`, `dockhh`, `notifbadge`, `notifphone` colors; `animMusic`
affects music animation. Outer dock margins are documented above.

#### Launcher and application wheel

`launcher.ts` draws the bottom-right launcher: `W = 180`, `H = 180`, `plane`
for its image and `prompt` for its label. Change its image-loading path for a
replacement asset, and `launchico` / `launchlbl` for tint. Right margin is set
on the wrapper (`3 * S`).

`appsmenu.ts` implements the searchable application wheel opened by `apps-menu`
and reused by other pickers. Apps come from desktop application entries.
`VISIBLE = 9`, `ROW_H = 50`, `ROW_W = 400`, `LIST_X = 150`, `CURVE = 46`
control rows and the curved layout. Frame shape is in `itemPath()`; wheel colors
are `wheelbg` / `wheelfg`, with backdrop behavior in `colors.ts`'s `MENU_BG`.
Use `animWheel` and `sndWheel*` for animation and sounds. The separate `launcher`
request in `core.ts` launches Rofi; use `apps-menu` to open the built-in wheel.

#### Volume and brightness OSD — `components/modules/osd.ts`

Appears on audio/backlight changes, anchored bottom-center. Base size is
`300 × 64`; tilt/padding are in `plane`. `.osd-wrap` in SCSS controls the bottom
margin (130px) and padding (6px 10px). Volume uses `cyan`, brightness uses
`amber`. `hideTimer` hides it after 1500ms. Audio follows AstalWp's default
speaker; `findBacklight()` lists the supported backlight paths. Update that
function if your device uses another sysfs name.

#### Notification popups and notification center

`notifpopup.ts`: transient top-left messages. `LIFETIME = 15000` milliseconds,
`MAXFR = 8`, drawing canvas `TOTALW = 700`, `TOTALH = 650`.
`MARGIN_L = 16`, `MARGIN_T = 199`, `CX`, `FW = 400`, `FH = 43` and `STEP = 55`
control placement and message geometry inside the drawing. Change these with
its projection and drawing bounds. Requests `notif-read` and `notif-dismiss`
operate on notifications through the handlers in `core.ts`.

`notifmessages.ts`: notification center/detail views, opened by `notif-hud` or
the dock tile. `W = 400`, `ICONW = 64`, `HEADER = 48`, `ROWH = 50`,
`ROW_GAP = 6`, `MAXROWS = 7`, `FOOTER_H = 24` control the list. Wrapper margins
are set to top `156 * S`, left `18 * S` both during creation and monitor changes;
update both sites. Internal `MARGIN_L` / `MARGIN_T` are separate drawing offsets.
Footer/tab polygons and input regions must follow layout changes.

Both modules use the notification color group, `animNotif`, `sndNotif` and
`sndNotifFile`. They connect to AstalNotifd. Do not assume every `LIFETIME`
constant means permanent notification history retention; inspect the particular
view's removal logic before changing it. `dismiss-notifs` dismisses daemon
notifications; `notif-dismiss` has view-dependent behavior in `core.ts`.

#### System tray — `components/modules/tray.ts`

Open the notification center and select its **Apps** tab. Tray applications
register through StatusNotifier / D-Bus; this is not a separate dock window.
`tray.ts` handles discovery, icon loading, activation and context-menu data.
`notifmessages.ts` draws the rows and menus: adjust its row dimensions, tray
icon drawing, `MENU_ITEM_H = 24` and `MENU_SEP_H = 8` for their appearance.
Left-click activates an item; right-click opens its menu. Adjust icon loading
sizes in `tray.ts` along with display sizes if changing icon resolution.

#### Update / package banner — `components/modules/aurbar.ts`

Displays package updates, theme updates and installation notices at the left
edge, vertically centered. Window left margin is `14 * scale`; change both its
initial value and rescaling path. The flat console card uses `CARD_W = 396`,
`CARD_H = 146`, `INSET = 8` and 12px cut corners. It displays a package count,
release versions or installation details, with the configured review/dismiss
shortcuts. Text is measured and truncated to fit. It remains click-through.
Use the `aur*` colors above; titles default to `aurfg` unless `aurtitle` is
explicitly overridden. A frame-clock fade/6px slide takes 180ms to enter and
140ms to leave, respects reduced motion, and stops ticking when settled.
There are no projected image assets or multi-stage animations in this card.
Package rechecks run every 30 minutes, theme
rechecks every six hours; the installed-notice auto-hide timer is 120000ms.
`modal aur` opens system updates; `modal update` opens theme updates.
`aur-dismiss` hides the update notice. The `pkg-installed NAME|DETAIL` request
creates an installation notice. Updater behavior is in `updater.sh`, separate
from the banner's appearance.

#### Media player and now-playing banner

`player.ts`: RADIOPORT, opened by `player` or the music dock tile. Dimensions
are `PW = 560`, `PH = 648`, artwork size `CSZ = 186`; the panel is centered
inside a full-screen overlay. Change drawing coordinates and `toLocal()` / hit
regions consistently when moving it. It discovers and controls MPRIS players
through `playerctl`; there is no static radio-station list. The displayed
frequency labels are generated by `freqOf()`. Use `radio*` colors and
`animMusic`. Player state polls every 1500ms while open.

`nowplaying.ts`: automatic track announcement. `IW = 300`, `IH = 54` and
`plane` define geometry. It is top-right anchored with top margin `30 * S` and
right margin `414 * S`. `TOTAL_MS = 7500`, `SCAN_MS = 2000`, `INTRO_MS = 620`,
`OUTRO_MS = 500`, `SETTLE_MS = 140` control lifetime/transitions. Its own drawing
code selects colors; changing RADIOPORT colors does not guarantee every banner
element changes with it.

#### Toasts, screenshots, workspace transitions and recording overlays

`toast.ts`: full-screen transparent surface with a drawn toast. Change its
computed drawing coordinates to move the toast rather than adding a full-screen
window margin. `GAP`, `ACW` control spacing; timing constants are `A_BLINK = 350`,
`EDGE_HOLD = 1000`, `OPEN = 300`, `HOLD = 1700`, `CLOSE = 230`, `ENDF = 200` (ms).
Preview via the `toast YOUR MESSAGE` request.

`region.ts`: screenshot / recording region selector. `INTRO_MS`, `DISSOLVE_MS`
control transitions; `CARD_DELAY`, `CARD_DUR`, `ICO`, `FRW`, `FRH`, `CARD_W`
control the action card. Border strokes and selection geometry live in its
Cairo drawing functions. Main colors include `dock` and `overlay`. Requests
are `region-shot` and `record-region`; capture plumbing is in `scripts/`.

`anim.ts`: workspace effect (`WsAnimWindow` / `triggerWsSwitch`), screenshot
banner (`BannerWindow` / `triggerShutter`), recording HUD (`RecWindow`), recording
transition (`RecGlitchWindow`) and region frame (`RecFrameWindow`). Each has its
own window/draw function. Recorder geometry uses `LEFT_W/H`, `RIGHT_W/H`,
`BOT_W/H`, `REC_TOP_W/H`; anchors are beside each `Window()` constructor.
Change the relevant draw function's offsets, stroke widths and colors for that
overlay. `animWorkspace`, `animGlitch`, `animModal` and the master `anim` affect
supported effects; check `animOn()` call sites for a particular animation.
The recording system can hide registered HUD windows. `toggle-hud` switches
HUD visibility during recording and top/bottom layering otherwise.

### All control dialogs

Most dialogs are in `components/modules/cmodal.ts`. Find the matching
`createModal({ name, W, H, ... })` to adjust that dialog's dimensions. Shared
`createModal()` accepts `yaw`, `pitch`, `roll`, `focal`, `dist`, `pad`, `col`,
`accent`, `hud`, `noGlass` and other behavior options used at its call sites.
`drawHudFrame()` draws HUD frames; `glass.ts`'s `drawGlass()` draws glass panels.
`drawBtn()`, `drawSlider()`, `drawToggle()` set common control shapes and borders.
Changes to these shared helpers affect multiple dialogs. Inner rows/buttons
still have their own coordinates and hit regions.

Send `modal NAME` through the session socket to open any registered dialog:

| Name / function | Current base size | What it controls / where to customize |
| --- | --- | --- |
| `vol` / `VolCtrl` | 480 × 720 | Audio devices, volume and application audio; `mic` aliases `vol` |
| `brt` / `BrtCtrl` | 312 × 176 | Display brightness; refresh every 2500ms |
| `wifi` / `WifiCtrl` | 320 × 380 | Network controls; right-anchored, yaw 15; inspect its network actions and row drawing |
| `bt` / `BtCtrl` | 320 × 380 | Bluetooth controls; right-anchored, yaw 15 |
| `pwr` / `PwrCtrl` | 312 × 252 | Session/power action buttons; commands live in this controller |
| `bat` / `BatCtrl` | 352 × 470 | Battery / power-cell details |
| `sys` / `SysCtrl` | Active monitor dimensions | System-monitor panels; readers in `sys.ts`, chart and layout code in `cmodal.ts` |
| `keys` / `KeysCtrl` | 470 × 660 | Keybinding reference display |
| `aur` / `AurCtrl` | 470 × 512 | Package update list and upgrade action |
| `update` / `UpdCtrl` | 470 × 512 | Theme update list and action |
| `themesettings` | Screen-sized | `themesettings_ctrl.ts` frame/tab layout; `themesettings.ts` settings controls |
| `termtheme` | 434 × 492 | `terminal_theme.ts`; terminal palette browser |

Other dialogs are created by their feature modules: city/forecast in
`sidepanel.ts`, clock in `timeset.ts`, markets in `markets.ts`, and keybinding
conflicts in `kbconflicts.ts` (`560 × 460`). Open the first four with `weather`,
`forecast`, `clock`, `markets` requests rather than assuming they are standard
`modal NAME` entries. The conflict dialog is opened by keybinding conflict logic.

### Animation, sound and other saved configuration

`config.ts` defines every supported `cfg` key. Arbitrary new keys in the Lua
file do nothing until supported in code. Preserve the generated
`local cfg = {}` / `return cfg` structure and use the exact assignment syntax.

| Keys | Default / purpose |
| --- | --- |
| `anim` | `true`; master animation toggle, also applies Hyprland animation state |
| `animWorkspace` | `false`; workspace animation option |
| `animGlitch`, `animModal`, `animGauge`, `animNotif`, `animMusic`, `animWheel` | `true`; individual supported effects, gated by master `anim` |
| `snd` | `true`; master sound toggle |
| `sndNotif`, `sndWheel`, `sndOverlay` | `true`; notification, wheel and overlay sound groups |
| `sndNotifFile` | Empty string uses notification fallback sound |
| `sndWheelStart`, `sndWheelActive`, `sndWheelEnd` | Empty strings use wheel fallback sounds |
| `sndOverlayFile` | Empty string uses the overlay fallback sound |
| `gaugeBadge`, `gaugeXp`, `gaugeHealth`, `gaugeRam`, `gaugeStamina` | Metric assignments documented above |

Sound selection through the UI copies adopted files to `USER_DIR/sounds`.
Manual sound paths must name existing files; empty or missing paths use the
fallback passed by the caller. Default assets are in `assets/audio`.

Theme Settings also manages wallpaper and keybindings. `env.ts` points wallpaper
storage at `~/Pictures/Wallpapers` and preferences at `USER_DIR/wallpaper.lua`.
Keybinding edits use `userbinds.ts`, `cyberdeck.ts`, `config/keybinds.lua` and
`~/.config/hypr/user.lua`; use the UI's conflict handling when rebinding dock
shortcuts. Terminal themes use `terminal_theme.ts`, `USER_DIR/rio_theme.json`,
`USER_DIR/rio_themes` and bundled Rio theme/style files under `assets/rio/`.

### Supporting files and other UI in this directory

| File / group | Role and customization scope |
| --- | --- |
| `widget.ts` | Astal GTK widget wrappers and monitor helpers; not a standalone visible widget |
| `proj.ts` | Shared perspective, polygon, image and text drawing; global changes affect all consumers |
| `glass.ts` | Shared modal glass, text, reveal and frame rendering |
| `fonts.ts` | Shared font families |
| `colors.ts`, `config.ts`, `wmconfig.ts` | Color/configuration/window-management state and persistence described above |
| `sys.ts` | System-stat readers and polling; adjust data source or interval here rather than in a purely visual widget |
| `themesettings.ts`, `themesettings_ctrl.ts` | Settings UI, control rows, tab layout and interaction |
| `userbinds.ts`, `cyberdeck.ts`, `kbconflicts.ts` | Binding editing, parsing and conflict UI |
| `terminal_theme.ts` | Terminal theme selection dialog |
| `tray.ts` | StatusNotifier / D-Bus tray backend used by the notification center’s Apps tab; icon loading and application/menu actions live here, while visible rows live in `notifmessages.ts` |
| `themesettings.ts.backup` | Backup copy, not the active imported settings implementation |
| `components/glitch.frag` | Separate shader asset; find its consumer before editing, since HUD animations also have their own drawing code |
| `components/login/lock_shell.qml` | Quickshell lock/login host; `QS_THEME` / `QS_THEME_PATH` select the theme |
| `components/login/themes/netwatch/` | QML lock/login design: `Main.qml`, `Background.qml`, `CutPanel.qml`, `Bracket.qml`; adjust QML dimensions, anchors, margins, color properties and strokes here |
| `components/login/sddm-theme/` | Separate SDDM theme; `theme.conf` defines background/type/font/color/fontSize, with QML files for detailed layout |
| `components/apps/CyberSpace/cyberspace.c` | Separate native CyberSpace application source; the adjacent `cyberspace` file is its executable, not an AGS widget configuration |

Shell color saving also writes `USER_DIR/login_colors.json` (`accent`, `bg`,
`fg`, `hover`). Login/lock UI uses a separate QML rendering system: GTK SCSS and
HUD `WRAP_MARGINS` do not position those components. Edit the theme actually
selected by the running login/lock host.

### Applying and checking a customization

1. Confirm the active checkout and identify the widget's owning module above.
2. Use Colors / Configuration for saved preferences; use source edits for
   geometry, stroke widths, fonts and behavior without a saved control.
3. Restart with `sh scripts/restart` after source or manual configuration edits.
4. Inspect the changed widget on each monitor, including hover, clicks, long
   labels and its open dialog. Check for clipped strokes and displaced hitboxes.
5. If an edit seems ignored, check saved color overrides, derived colors, the
   active module/class, the running checkout and the startup log in that order.

The guide describes the checked-in implementation. Live desktop behavior and
these example customizations were not exercised while writing this documentation.

### Live focused-window opacity hotkeys

- **Super + Alt + Page Up**: increase the focused window's opacity by 5 percentage points.
- **Super + Alt + Page Down**: decrease it by 5 percentage points.

These run immediately in Hyprland; no session restart or HUD restart is needed.
Values are clamped to 10–100% and applied to the window's active, inactive and
fullscreen opacity, with override enabled so global opacity does not multiply
it again. Application-rendered transparency can still affect the result.

Implementation: `config/window-opacity.lua`; theme actions `win.opacityup` and
`win.opacitydown` in `config/keybinds.lua`. Adjust the `0.05` arguments to change
the step. Each window starts from the global `decoration.active_opacity` on its
first adjustment (currently about 88%), then remembers its own chosen value in
Lua memory. A pre-existing per-application opacity rule is replaced on first
use; it is not read as the starting value. Window opacity choices are not saved
to disk across session restarts. The helper preserves its table across reloads,
but other rule/theme changes can affect the rendered result until the next step.

On this machine the running theme still points to `/home/neuro/CyberArch-Dotfiles`.
The shortcuts were therefore also saved in `~/.config/hypr/user.lua` and
registered live, with a timestamped `user.lua.opacity-backup-*` backup. Those
user bindings load the helper from this workspace's absolute path. Update that
path if moving the checkout. They take precedence over the matching theme
bindings through the existing user-binding conflict scan.

Dispatcher reference: [Hyprland window set_prop](https://wiki.hypr.land/configuring/core/dispatchers/#set_prop).
Validated against the running Hyprland 0.56.2 API: Lua syntax, mocked stepping /
bounds / per-window state / no-focus behavior, and live registration of both
bindings. Visual opacity changes were not exercised automatically.

### Live theme palette hotkeys

- **Super + Alt + P**: next palette.
- **Super + Alt + Shift + P**: previous palette.

Order: NETWATCH → BLADE → SYNTHWAVE → JOHNNY → GHOST → NSD → NETWATCH; reverse cycling wraps too. A toast displays the chosen name.
The shortcuts send `palette-next` / `palette-prev` to the running HUD. Its
`palette-current` request reports the current preset, including when individual
colors have been customized. Cycling uses the tracked preset rather than trying
to match modified RGB values.

The handler in `core.ts` uses the same `applyColors()` path as the Colors tab:
it applies and saves the palette, updates shell/terminal colors and selects its
wallpaper. Choosing a preset clears individual color overrides. Each switch is
live; neither Hyprland nor the HUD needs restarting after the handler is loaded.
Theme binding IDs are `hud.palettenext` and `hud.paletteprev`.

This machine also has these bindings in `~/.config/hypr/user.lua` (backed up as
`user.lua.palette-backup-*`). The HUD was reloaded once from this workspace to
load the handler. The canonical theme symlink still points to the other checkout:
if a later login starts that older HUD, these new requests will be unavailable.
Run `sh scripts/restart` from this workspace to activate the updated HUD again,
or use the installer's documented checkout migration for permanent startup.

Validation: AGS GTK 3 bundle, Lua syntax and whitespace checks passed. Live
registration and `palette-current` were checked without cycling away from the
user's current colors.

### Adding a new color palette

A new palette starts in `components/modules/colors.ts`. The Colors settings
buttons and palette hotkeys both read `Object.keys(PALETTES)`, so adding an entry
makes it available in both places automatically. You do not need a new hotkey,
widget, SCSS file or request handler for each palette.

#### 1. Choose a name and extend the palette type

Use uppercase letters only, for example `NSD`. The saved-palette loader currently
matches `[A-Z]+`; names with spaces, digits, underscores or hyphens will not
reload correctly unless you also update that parser.

Add `"NSD"` to the `PaletteName` union near the top of `colors.ts`:

```ts
export type PaletteName = "NETWATCH" | "BLADE" | "SYNTHWAVE" | "JOHNNY" | "GHOST" | "NSD"
```

#### 2. Define the palette's colors

Start with a complete existing preset and customize it. For example, insert the
following **after the closing brace of the `PALETTES` declaration and before
`export const USER`**, not inside the object initializer:

```ts
PALETTES.NSD = {
    ...PALETTES.NETWATCH,
    // NSD blue #5A96FF, purple #C170FF, green #00EB74.
    red:     [193, 112, 255],
    cyan:    [0, 235, 116],
    blue:    [90, 150, 255],
    magenta: [193, 112, 255],
    green:   [0, 235, 116],
    dock:    [193, 112, 255],
    press:   [0, 235, 116],
    badge:   [193, 112, 255],
    cpu:     [193, 112, 255],
    ram:     [90, 150, 255],
    stamina: [0, 235, 116],
    netinfo: [0, 235, 116],
    hudcyan: [0, 235, 116],
    overlay: [193, 112, 255],
    sysveil: [193, 112, 255],
    glassacc: [196, 220, 255],
}
```

This is a starting point: unspecified colors retain NETWATCH's values, including
some notification and update-banner accents. Customize those using the widget
color-key table earlier in this guide. Semantic names such as `red` are roles;
their assigned RGB value can be purple or any other color.

Use integer RGB channels from 0–255 in `PALETTES`, not hex strings or normalized
0–1 values. Alpha is separate from RGB and is not a fourth palette-array element.
Use only keys already declared in `NEON` unless you also implement the new role's
consumer and settings UI.

You can instead add `NSD: { ... }` directly inside `PALETTES`, copying an existing
preset's full body. Do not reference `PALETTES.NETWATCH` from inside the initial
`PALETTES` object: that variable has not finished initialization yet.

Avoid defining only two or three colors without a base. `applyPalette()` updates
keys supplied by the selected preset; it does not reset every `NEON` key first.
An omitted base color can therefore retain a value from the previous preset.
Copying NETWATCH gives the example the same base-role coverage as that preset.

The `DERIVE` table fills linked roles unless your preset explicitly includes
them. In the example, `dockv` / `dockh` follow `dock`, their hover roles follow
`press`, and `xpbar` follows `badge`. To make one different, add a direct entry,
for example `dockh: [193, 112, 255]`. A direct palette entry pins that role.

#### 3. Customize special effects if needed

These tables in `colors.ts` control behavior beyond ordinary widget RGB values:

| Table | Purpose / default for a new name |
| --- | --- |
| `IMG_TINT` | Image/map tint and strength; no preset tint when absent |
| `MAP_ACCENT` | Clock, city and weather defaults; uses `MAP_ACCENT_DEF` when absent |
| `MENU_BG` | Application-menu background and fog; uses `MENU_BG_DEF` when absent |
| `GLASS_ALPHA` | Glass intensity multiplier; defaults to `1` |
| `GLASS_MODE` | Alternate glass appearance; defaults to `false` |
| `HUD_SOFT` | Special modal text/accent colors; otherwise derives from `glassacc` |
| `CIRCLE_TINT`, `LAUNCHER_TINT`, `LAUNCHER_LABEL_TINT` | Special image/label tint paths |
| `RADIO_BG`, `NOTIF_BUBBLE` | Special player-header and notification-image colors |

For example, to give NSD a purple-tinted map with green weather text, add these
entries **inside the existing corresponding table declarations**:
A
```ts
// Inside IMG_TINT:
NSD: [[193, 112, 255], 0.65],

// Inside MAP_ACCENT:
NSD: {
    clock: [193, 112, 255],
    city: [0, 235, 116],
    forecast: [0, 235, 116],
},
```

Map accents and several special tint helpers run after the main palette is
applied. For these roles, use the appropriate helper table as well as inspecting
`applyDerived()`; a direct `PALETTES.NSD.mapclock` entry alone is not sufficient
to prevent `updateMapAccent()` from setting its default. A saved user override
is different: helpers generally check its `OVR` flag before replacing it.
`HUD_SOFT` uses normalized 0–1 channels; most other RGB tables above use 0–255.
Follow each table's declared type and neighboring entries.

#### 4. Match desktop application colors

The HUD palette does not automatically define GTK, Qt/Kvantum or compositor
colors. Add an `NSD)` branch to the **first** `case "$NAME" in` block in
`scripts/shell-theme`, before its `*)` fallback:

```bash
NSD) ACC="193 112 255"; SEC="0 235 116"; TXT="225 232 242"; DIM="100 110 140"; BAS="7 9 13"; WRN="0 235 116" ;;
```

`ACC` is the primary accent, `SEC` secondary accent, `TXT` foreground, `DIM`
muted text, `BAS` background base, and `WRN` warning accent. Without a matching
branch the script changes its local name to NETWATCH and uses that scheme for
its generated desktop configuration.

The script's second `case` block controls rounding, rounding power, border size
and glow. Add an NSD branch there if desired; otherwise the default geometry is
used. Saved Window Management overrides can still take precedence.

#### 5. Match the terminal and wallpaper (optional)

For Rio, copy a bundled full style such as `assets/rio/styles/cybercore.toml` to
`assets/rio/styles/nsd.toml`, then edit its color settings. Add `NSD: "nsd"` to
`KITTY_STYLES` in `colors.ts`. Without this mapping, palette selection uses
`cybercore`. The style is a complete terminal configuration, so preserve settings
you want to retain. Merely adding a file under `assets/rio/themes` does not wire
it into palette switching.

`scripts/rio-style` finds bundled styles through `CYBER_DIR` or the canonical
theme path, then falls back to user Rio theme/style directories. If running a
different checkout than the canonical one, ensure the new style is available at
the path the script actually resolves. It also skips reapplying a style whose
name already matches `.rio-style`; switch to another style and back when testing
changes to the currently selected style file.

For wallpaper selection, put images/videos in `~/Pictures/Wallpapers/nsd/`.
`scripts/theme-wallpaper` normally lowercases the preset name to find its folder
(BLADE is the existing special case). A missing or empty directory leaves the
wallpaper unchanged. No additional script branch is needed for NSD. In a
multi-checkout installation, its `set-wallpaper` helper also resolves through
`CYBER_DIR` or the canonical theme directory.

#### 6. Load, select and verify

From this checkout:

```bash
ags bundle core.ts /tmp/cyber-palette-check.js --gtk 3
bash -n scripts/shell-theme
sh scripts/restart
```

The HUD needs this one restart to load new TypeScript definitions; Hyprland does
not need restarting. Then select NSD in **Theme Settings → Colors**, or cycle
with **Super + Alt + P** / **Super + Alt + Shift + P**. An entry appended after
the existing declaration appears after GHOST in the current cycle order.
Subsequent switches apply live.

Check the current trays, notifications, player and dialogs, then switch from
a very different preset to NSD to catch leftover colors. Check shell colors,
terminal and wallpaper separately. Restart the HUD once more to confirm the
selected name and colors survive saving/loading.

Source edits to an already saved preset do not necessarily replace the RGB
snapshot in `USER_DIR/user_colors.lua` on restart. Reselect the preset in Colors
to apply its new source values and save them. Preset selection clears personal
color override flags. Also make your preset meaningfully different from others:
`getPaletteName()` matches RGB values and can identify an identical copy as the
first matching preset, while hotkey cycling uses `getActivePalette()`.

NSD is now implemented in `colors.ts`, `scripts/shell-theme` and the Rio NSD
style/theme files. The example above remains a simplified recipe; do not add a
second `PALETTES.NSD` assignment over the implemented preset.

#### New palette checklist: required and optional edits

| Step | Edit | Required? |
| --- | --- | --- |
| Register the name | Add an uppercase, letters-only name to `PaletteName` in `components/modules/colors.ts` | Keep the declared type in sync |
| Define the HUD colors | Add a `PALETTES` entry using the complete base-preset example above; customize RGB roles | Yes |
| Add it to settings and hotkeys | No separate edit: both enumerate `Object.keys(PALETTES)` | Automatic |
| Match GTK, Qt and window accents | Add a branch before the first fallback in `scripts/shell-theme` | Required for a matching desktop scheme; otherwise NSD is used |
| Set map/text/image special colors | Extend the relevant `MAP_ACCENT`, `IMG_TINT` or other helper table in `colors.ts` | Optional; helper defaults can replace some direct palette entries |
| Match Rio | Add `assets/rio/styles/<name>.toml` and its `RIO_STYLES` mapping | Optional; otherwise `cybercore` is selected |
| Match wallpaper | Populate `~/Pictures/Wallpapers/<lowercase-name>/` | Optional; missing/empty folders keep the current wallpaper |
| Load the definition | Bundle-check, restart the HUD once, then select the new preset | Yes; subsequent palette switches are live |

To change **only an existing preset**, edit its entry and any corresponding
helper/script values, restart the HUD, and reselect it in Colors. To create a
**separately selectable preset**, give it a new `PALETTES` key. Editing
`user_colors.lua` alone customizes saved colors but does not create another
preset button or another entry in the hotkey cycle.


### Implemented NSD theme

NSD uses purple `#C170FF` as the primary color and green `#00EB74` for accents,
hover/interaction states and status highlights. Blue `#5A96FF` is a supporting
color (for example, the RAM gauge and terminal ANSI blue), with dark navy
backgrounds and pale foreground text. It explicitly defines every current HUD
color role to avoid inheriting leftovers from the previously selected preset.
Map, launcher, menu fog and player-header helper tables also include NSD.

Select **NSD** in Theme Settings → Colors, or cycle to it using the palette
hotkeys. It follows GHOST in the cycle. `scripts/shell-theme` provides matching
GTK/Qt/window accents; `assets/rio/styles/nsd.toml` contains a complete Rio
configuration with embedded colors, and `assets/rio/themes/nsd.toml` provides
the standalone color theme. Rio style switching now receives this checkout's
`CYBER_DIR` explicitly, so its new style is found even with an older canonical
theme symlink. Optional wallpaper files go in `~/Pictures/Wallpapers/nsd/`;
without that folder, the existing wallpaper remains.

## Distro reliability audit — original review 2026-10-09, reconciled 2026-10-13

See [RELIABILITY_AUDIT.md](RELIABILITY_AUDIT.md) for current remediation status.
The original findings describe the checkout at the time of that review, not the
current implementation. Root-owned hook deployment, staged update activation
and rollback, private session runtime paths, bounded HUD supervision, and
healthy-bundle restart recovery now exist. The Rio build/removal path is gone.
Isolated harnesses cover installer rollback, location migration, startup/restart
recovery, preference preservation, and palette write ordering.

Packaging and a tested dependency set remain open, as do clean-VM installation,
upgrade/rollback qualification and real graphical/hardware testing. Local mocks
and build checks do not establish distro readiness or describe the running HUD.
