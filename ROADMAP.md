# NeurOS interface roadmap

Reviewed against version 2.46 on 2026-11-28. The menu directions below are
design proposals, not approved implementation decisions. The current
desktop composition and interaction requirements are recorded in `NOTES.md`;
the concept art in `concept_art/` and `DESIGN_SHIT.md` supply visual direction.
Use Akira, Ghost in the Shell and Neuromancer as influences while developing an
original NeurOS interface: dark working surfaces, deliberate cuts, technical
typography and controllable neon, without reproducing a game HUD.

## Current stage and next decisions

- **Built in source:** three optional trays, independent utility shortcuts,
  secondary-color attention on selected surfaces, a design-study overlay, the
  upper-right messages panel, and the six-action utility wheel beta. Weather and
  financial markets remain available; NNET is a future replacement.
- **Wheel:** `Super + Space` opens the fixed-action beta. Decide whether
  its geometry and trigger work in use before adding configurable assignments or
  actual scratchpad management; validate keyboard focus and monitor behavior.
- **Visual language:** agree on surface hierarchy, geometry, typography, semantic
  colors and motion/glow behavior using representative real content. Then apply
  the decisions incrementally to trays, expanded utilities and the Den.
- **Qualification:** live Hyprland input, scaling and hotplug, clean install and
  upgrade, and wider hardware/session testing remain open. See
  `RELIABILITY_AUDIT.md`; source and isolated tests are not release certification.

## Super + Tab: application launcher

The current app menu (`components/modules/appsmenu.ts`) supports search,
keyboard and pointer navigation, and application launch. `scripts/launcher`
sends the `apps-menu` request. The legacy desktop launcher in `launcher.ts` also
calls the menu but is not created by the current `core.ts` desktop composition.
Preserve working access, multi-monitor placement, configurable sound and
reduced-motion behavior in any redesign.

### A. Operator index

A wide, cut-corner console panel with a prominent search line, a clear vertical
result list and a narrow context rail for the selected application's icon and
name. Small registration marks and restrained violet-to-mint edge takeover give
it the equipment-panel language from the concept art. Favor fast scanning and
strong keyboard focus over decorative motion.

### B. Transit directory

An asymmetric split panel inspired by a metropolitan information terminal:
search and a dense directory on the left, a larger selected-entry card on the
right, and a fine route-like line connecting the active row to its details.
Use the line only as an attention cue; selection must remain clear without glow
or animation. Keep the surface calm when idle.

### C. Signal stack

A compact central search bar above a stack of chamfered result cards. The
selected card extends a small side panel, while adjacent results remain visible
for context. Allow a user to disable the extension animation and keep the same
information available at smaller screen sizes.

## Super + Shift + C: system monitor / Netrunner Den

The current system monitor lives in `components/modules/cmodal.ts` and exposes
processes, system information, startup entries and logs. Preserve those views,
their actions and data, the direct shortcut, and access from the CPU/RAM tray.
Actual measurements must remain distinguishable from decorative marks.

### A. Operations desk

A stable top navigation rail for Processes, System, Startup and Logs, with a
large central work area and a slim, optional telemetry rail. Use dark, mostly
opaque sections with cut corners, precise dividers and compact labels. Emphasize
the selected tab with both a shape marker and secondary accent; reserve warning
colors for real warnings and destructive actions.

### B. Diagnostic folio

Treat each view as a technical dossier: a persistent identity and status header,
a left index for the four sections, and a broad page for tables, graphs or logs.
Fine linework, small stamped identifiers and selective hatching echo the concept
art without obscuring information. Prioritize readable process rows and logs at
ordinary laptop sizes.

### C. Circuit observatory

A compact central workspace framed by live CPU and memory plots, with the four
views selected through a horizontal strip. Fine circuit-like paths connect only
real status summaries to their associated controls. Keep graphs optional and
avoid implying fictional system activity when data is unavailable.

## Evaluation and implementation gates

- [ ] Choose or combine a direction for each menu before treating either as final.
- [ ] Prototype the selected layouts with real labels, long application names,
  empty/error/loading states and representative process/log data.
- [ ] Preserve application search and launch, process and system tools, startup
  and log views, existing shortcuts and monitor placement. Review destructive
  process actions separately and make their consequences clear.
- [ ] Use existing palette, attention, glow and motion settings. Verify legible
  focus and selection with glow and motion disabled and across all six palettes.
- [ ] Test keyboard and pointer interaction, different resolutions and DPI,
  long text, and live Hyprland behavior. Record visual evidence and known gaps.
- [ ] Reconcile `NOTES.md` and `DESIGN_SHIT.md` when a direction is accepted.

NNET remains the separately planned replacement for the current financial
market widget: a feed of recent technical research, including arXiv articles on
kernels, computational mathematics and related topics. It is not a dependency
of either menu proposal.
