# NeurOS Interface: Design Notes

> **Status:** Design direction, not an implementation specification.  
> **Scope:** NeurOS-Interface (desktop shell, widgets, overlays, appearance, and interactions), not the NeurOS Distribution, its bootloader, or Axon.

## Implementation reconciliation — 2026-11-28

This document combines established principles, experiments and historical
proposals. The current composition in `NOTES.md` supersedes conflicting older
statements below: compact weather and markets are present in an optional tray;
markets remain functional until the planned NNET replacement is designed and
built. The controls and CPU/RAM trays have saved visibility preferences. Expanded
views and inherited controls still need redesign. These are source-level facts,
not certification of live behavior.

The Option D wheel is a beta, not yet a scratchpad: `Super + Space`
toggles six fixed point-top actions. Held-modifier activation, configurable
assignments, scratchpad integration and live focus/input qualification remain
open. The design prototype and secondary-color attention renderer exist; their
final geometry, tokens, effect levels and wider migration remain design work.
See `ROADMAP.md` for proposed next steps and `RELIABILITY_AUDIT.md` for release
limits.

## How to read this document

**North star:** NeurOS should be an original cyberpunk-influenced genuinely usable desktop that its creator would be happy to give to **another human being**. It must not be a Cyberpunk 2077 HUD imitation nor simply Henry's CyberArch-Shell with NSD colors pasted onto it. 

User choice is part of the identity, not an obstacle to it.

---

## **DIRECTION**

The computer feels **personal, operator-controlled, and technically capable**: comfortable in ordinary use, with sophisticated tools accessible when requested. Cyberpunk is expressed through material, geometry, lighting, typography, and interaction, not through a permanent in-game HUD.

**OPEN**

- Who created and distributes NeurOS within the fictional story: an individual, a loose community, or a shared starting image customized by each operator?
- What parts of that story deserve to appear in optional branding, documentation, startup presentation, or easter eggs?

## 2. The core product promise: the machine belongs to the user

**DECIDED**

- **Nothing nonessential is forced to live on the desktop.** Widgets and visual modules should be user-controllable.

- **Expanded utilities remain independently available by hotkey**, even when their compact desktop counterparts are absent or hidden.

- The shell should support an ordinary daily workflow, not demand constant attention.

- A user may prefer a heavily instrumented desktop, a mostly empty desktop, or something between the two.

- Customization must not require understanding project lore.

- Do not compromise usability merely to make NeurOS seem aesthetically consistent or different from its upstream.

**DIRECTION**

- **Daily desktop:** practical, readable, with room for wallpapers and work.

- **On-demand utility views:** fully featured weather, market, and other applications 
invoked directly when needed.

- **Netrunner Den:** a dedicated, hotkey-invoked advanced workspace with denser system and operational information. It is **not** a mandatory destination for every utility.

- **Hotkey access panel / quick controls:** discoverable access to commands and shortcuts without permanent HUD-like corner clutter. The interaction and layout need redesign.

**Existing behavior to preserve while refactoring:** `Super+Alt+H` currently hides the desktop HUD elements as a group. There is already a separate shortcut for opening the Netrunner Den. Preserve working access paths until replacements are usable.

**OPEN**

- Exact quick-panel layout, categories, invocation key, and relationship to Den navigation.
- Visibility controls beyond the three implemented tray preferences.
- Default visible widgets on first boot.

## 3. What to remove, preserve, or redesign

### Remove from the persistent desktop presentation

**DECIDED / confirmed direction**

- **Removed:** the player-stat / health-bar-like upper-left HUD, including its gauge settings and workspace badge. System details remain available on demand.

- The **permanent right-side HUD tower**, especially the minimap-style composition and stacked information plates.

- The **game-loadout / corner-shrine** composition of persistent shortcuts and small HUD elements.

- **Current direction:** compact weather and markets are grouped in an optional right-side tray; expanded views remain independently accessible. NNET is planned to replace the market function.

### Preserve the capabilities, change their appearance

**DECIDED**

- **Full weather view:** keep its hotkey-accessible, unfolded application and its meaningful forecast/detail content.

- **Current full market view:** keep its existing capabilities and shortcut until the planned NNET replacement is ready; financial functionality is not a permanent requirement.

- **Netrunner Den:** keep the concept and existing advanced views, including the process/system/log-oriented tools, while redesigning inherited game-HUD styling.

- **Useful system controls, telemetry, media controls, and shortcuts:** keep the functions where useful; reassess their default visibility, location, and presentation.

- Do **not** delete an application simply because its old compact desktop widget is being removed.

**DIRECTION**

- Preserve useful information hierarchies; change the visual treatment around them.
- Favor meaningful borders, selections, statuses, and controls over decorative "visor" marks that convey nothing.
- Improve contrast and background separation in expanded overlays independently of which wallpaper happens to be visible.

## 4. Visual identity: keep the cyberpunk genes

**DECIDED**

- **Chamfered / cut corners stay.** They are a feature, not a problem to eliminate. The redesign must not flatten everything into generic rectangular UI.

- **Neon and glow stay**, and stronger glow is welcome as an aesthetic option.

- **Glow intensity must be controllable**; strong effects cannot be imposed on everyone.

- Current NSD purple-and-green coloring alone is **not** enough to establish originality. The current indicators and HUD composition still read too strongly as Cyberpunk 2077.

- Visual identity must outlive any particular wallpaper or theme.

**DIRECTION**

- Define a coherent **NeurOS geometry language** using intentional cuts, edge segments, asymmetry, spacing, and panel construction.

- Keep sophisticated, high-tech visual richness. **Do not confuse originality with minimalism.**

- Reduce *borrowed visual metaphors* such as avatar stats, minimap framing, equipment-slot clusters, and constant visor overlays, rather than banning angles, borders, or luminous effects.

- Let hierarchy determine where strong framing belongs. Not every text field, label, and icon needs equal visual intensity.

**OPEN**

- Exact shape families, corner-cut dimensions, typography, icon set, material/translucency rules, and animation timing.

- How much ornamental detail genuinely belongs to the NeurOS style versus the upstream shell.

## 5. The distinctive interaction idea: secondary-color takeover

**DECIDED**

When a window or control is **hovered or focused**, the **secondary theme color progressively overtakes the resting primary color**, accompanied by stronger local edge glow. This is intended to become a defining NeurOS interaction behavior, not merely a static two-color theme.

### Proposed state language

**Prototype implemented — 2026-10-14:** Shared `attention.ts` drives utility tray
tabs, the CPU/RAM panel and standard glass dialog borders. The secondary accent
travels clockwise from the first corner in 180ms and retracts in 160ms. Focus
adds a thicker edge and inset corner; an expanded tray keeps its active accent.
Primary/secondary resolve from the editable `dock`/`press` palette slots.
Theme Settings offers independent takeover motion and Off/Low/Normal/Strong
edge glow. Motion follows the animation master switch, with immediate state
changes when disabled. The effect stops ticking after settling and uses vector
strokes rather than blur surfaces. Timings and direction remain experimental.

Remaining migration: internal canvas buttons/sliders/Den tabs, legacy HUD frames,
and compositor-managed application borders. Semantic warning, recording and
destructive-action colors retain their existing meaning.

| State | Appearance intent |
| --- | --- |
| **Idle** | Primary-accent structure, subdued edge illumination. |
| **Hover** | Secondary accent starts to take over selected corners/edge segments; glow rises locally. |
| **Keyboard focus** | Clearly legible secondary-accent emphasis, not dependent on mouse hover. |
| **Selected / active** | More pronounced takeover where selection or active-window status should be obvious. |
| **Warning / destructive / recording** | Real semantic status remains distinguishable; do not confuse attention effects with safety information. |

**DIRECTION**

- Apply the grammar consistently to window borders, Den tabs, quick-panel controls, buttons, sliders, graph interaction points, and selected modules where appropriate.
- Make the secondary color **move through structural elements** rather than turning every pixel into the same glowing color.
- Use *different intensities for different interaction importance*: tiny control hover should not rival focused-window emphasis.
- The system should remain recognizable when the user switches color themes.
- Potentially animate takeover from a consistent direction or corner, but **this is an experiment, not a settled decision**.

**Accessibility / user control (DECIDED principle; exact controls OPEN)**

- Glow must be adjustable, including a low- or no-glow choice.
- Reduced-motion and low-effects users must still be able to tell which control or window has focus.
- Avoid compulsory flashing, aggressive pulsing, or distracting full-screen transitions.
- Make sure focus/selection can be distinguished by more than color alone, especially when effects are disabled.

## 6. Themes, palettes, and wallpapers

**Existing baseline**

- The current shell provides **6 palettes**: NETWATCH, BLADE, SYNTHWAVE, JOHNNY, GHOST and NSD.
- The setup has a collection of animated/live wallpaper options associated with themes, plus additional wallpaper choices in the user's own rotation.
- The desktop must not depend on a single wallpaper or composition to remain readable.

**DECIDED principles**

- **NeurOS identity must not be enforced by restricting the user's colors or wallpaper.**
- Appearance is user choice. A desktop that is NeurOS in purple should still be NeurOS in other palettes.
- Keep the *interface's layout/interaction grammar* distinct from its theme colors and wallpaper assets.
- Preserve customization where doing so is practical and sustainable. No need to delete existing themes merely to prove originality.

**DIRECTION / recommendation, not a locked shipping promise**

- Give NeurOS a carefully designed **default appearance**, likely based on its NSD palette, while allowing alternatives.
- Retain the remaining upstream palettes as optional/legacy choices **if they can be adapted and maintained**; do not promise perfect support for every palette before it is tested against new components.
- Decouple wallpaper choice from palette choice where practical.
- Offer static wallpapers and user-supplied imagery; do not require live wallpapers or wallpaper cycling.
- Treat large wallpaper collections as optional content if packaging, performance, or storage make that sensible.
- Check permissions for **individual wallpapers, fonts, graphics, and other third-party assets** before redistributing them; permission to modify the shell does not automatically license every bundled asset.

**OPEN**

- Which themes ship preinstalled versus as optional packs.
- Which animations/wallpapers remain in the initial distribution.
- Whether users can create arbitrary palettes through a first-party appearance editor.

## 7. Reliability and implementation boundaries

**DECIDED principle:** Visual ambition should not break ordinary desktop behavior or the upstream reliability improvements already made.

**DIRECTION**

- Separate **data and behavior** (weather retrieval, market data, system monitoring, media controls, Hyprland interaction) from **presentation** (shape, color, effect, placement) as the refactor progresses.

- Prefer shared **semantic visual tokens** (surface, text, primary/secondary accent, focus, warning, success, border) instead of scattering hardcoded NSD colors throughout individual widgets.

- Keep layout/geometry rules separate from color themes unless deliberately supporting distinct layout presets.

- Build and test **one representative redesigned component** before wholesale migration; the market view, weather view, Den tabs, or a focused-window border could serve as prototypes.

- Test themes, varying wallpapers, no-glow/reduced-motion states, and keyboard-only access.

- Retain upstream author credit and applicable licensing. Becoming visually original does not require rewriting functioning infrastructure solely to erase its provenance.

## 8. Working refactor order 

1. **Design experiments:** prototype chamfered shapes and the primary-to-secondary focus takeover, including disabled/reduced glow states.

   **Prototype added — 2026-10-16:** The on-demand `design-prototype` shell request opens three native panel studies derived from options A, B and D, using the shared attention renderer and current palette. Hover advances the secondary edge; keyboard focus adds a thicker edge, inset marker and explicit focus label; selection remains marked with `[x]`. Local Theme/Off/Low/Normal/Strong glow and Theme/Off motion controls allow comparison without saving appearance changes. Theme motion respects the global animation settings. Sample readings are illustrative. Close with `Esc` or the Close button. Implementation is untested at the user's request; geometry and rendering remain experimental.

   Open after loading the updated shell: `astal -i cyberpunk design-prototype`. Repeat the request to close it.

2. **Desktop composition:** remove unwanted persistent HUD metaphors and decide what, if anything, is on screen by default.

3. **Independent visibility:** retain current global hide behavior while giving individual optional elements predictable visibility controls.

4. **Expanded utility restyling:** weather and market keep their features and hotkeys; new geometry, focus states, typography, and information hierarchy.

5. **Hotkey access panel:** replace the inherited game-like shortcut presentation with a recognizable, discoverable NeurOS control system.

6. **Netrunner Den:** preserve the advanced workstation concept; make its visual language consistent with the rest of NeurOS.

_(Dev-sided):_

7. **Themes and assets:** migrate palettes, test contrasts, decouple wallpaper choices, and clarify asset redistribution rights.

8. **Usability pass:** verify that another person can install, navigate, configure, and use the system without lore knowledge or hidden compulsory UI. 

## 9. Explicit non-goals

- **Not** a Cyberpunk 2077 HUD recreation.
- **Not** Henry's CyberArch-Shell with only a purple/green recolor.
- **Not** a generic flat desktop stripped of cuts, lighting, or personality.
- **Not** a system that requires another user to understand NSD's private jokes.
- **Not** a forced always-on dashboard.
- **Not** a promise to rebuild functioning upstream infrastructure for aesthetic purity.
- **Not** a decision that every expanded utility must live inside Netrunner Den.

## 10. Outstanding design questions

- What specific proportions, cut patterns, and edge treatments make a panel recognizably NeurOS?

- Where does secondary-color takeover begin, how fast does it travel, and what distinguishes hover from actual window focus?

- How should reduced-motion, no-glow, and high-contrast themes express those same states?

- What should a fresh install display by default?

- What is the shape and interaction model of the Hotkey Access Panel?

- Does the fictional netrunner begin with a personal build, or a shared NeurOS base tailored to their needs?

- What default palette and type hierarchy best represent NeurOS without depending on purple alone?

- Which upstream themes and wallpaper assets can be confidently supported and redistributed?

---

> **Design mantra:** **Cyberpunk in character. Civilized in behavior.**  
>
> Keep the cut corners. Keep the neon. 
Let the second color take over when the machine has the operator's attention. Let the operator decide what stays visible.  
>
> **The machine belongs to the user.**






## 11. Redesign options from the concept art

**Status:** Options for exploration, reviewed against `concept_art/` on 2026-10-16. The option names below describe the visual directions in the references; no single direction is selected or approved for implementation. They can be combined across components.

The sheets are collections of visual ingredients, not proposed full-desktop layouts. Their density does not change the decision to keep desktop elements optional or to preserve weather, market and Den as independently accessible views.

### Option A: Luminous instrument panels

**Reference:** [Concept art 1](concept_art/concept_art1.jpeg).

- **Visual vocabulary:** Dark surfaces, bright mint/purple outlines, chamfered buttons, hexagonal icon holders, segmented bars, circular meters and corner-bracket readouts. Strong edge glow gives controls a tangible, illuminated quality.
- **Possible application:** QKuick controls and settings use the button/toggle family; Den uses the meters and telemetry frames. Reserve stronger framing for active controls and important readings.
- **Interaction adaptation:** Use the resting primary accent and progressive secondary-color takeover from section 5. The sheet's differently colored buttons are references for appearance, not a complete state specification.
- **Tradeoff:** Heavy bloom and repeated gauges can crowd content and recreate the old HUD feel. Compare thin idle outlines with brighter focused edges; keep real values, units and labels readable without glow.

### Option B: Modular technical panels

**Reference:** [Concept art 2](concept_art/concept_art2.jpeg).

- **Visual vocabulary:** Fine outlines, restrained gray surfaces, clipped panel corners, compact monochrome icons, linear progress controls and separated technical sections. Hexagonal and circular emblems provide stronger identity accents.
- **Possible application:** Expanded weather/market views, settings and the Hotkey Access Panel. This is a candidate for the everyday component foundation, with more luminous styling applied on interaction.
- **Branding options within the sheet:** A hexagonal N monogram, an open double-outline hexagon around NSD, a connected hexagon cluster, or a circular seal. Test a simple mark at small sizes before choosing an emblem family.
- **Tradeoff:** Fine strokes and small labels can become illegible at desktop scale. Prototype real content and comfortable spacing rather than reproducing the sheet's miniature technical annotations.

### Option C: Phosphor diagnostics and industrial surfaces

**Reference:** [Concept art 3](concept_art/concept_art3.jpeg).

- **Visual vocabulary:** Phosphor-like green readings, waveform/area graphs, segmented power bars, circuit/eye/brain icons, bracketed logs, amber warning plates and distressed industrial labels.
- **Possible application:** Netrunner Den's system, process, network and log views. Circuit and node motifs could identify technical categories; graphs should visualize actual available data.
- **Warning treatment:** Explore the amber heading band, explicit icon and readable message as a real warning component. Keep warning/error meaning separate from primary-to-secondary attention effects.
- **Tradeoff:** Scanlines, grain and glitch damage can obscure live data or imply faults. Treat them as optional surface/branding experiments, keeping text, chart traces and actionable controls clear. Radar-like illustrations do not justify restoring the desktop minimap tower.

### Option D: Hexagonal NeurOS identity

**Reference:** [Concept art 4](concept_art/concept_art4.jpeg).

- **Visual vocabulary:** Purple structural edges with mint highlights, a sharp NeurOS wordmark and N emblem, six-around-one hexagonal arrangements, circuit traces, chamfered bars, compact forecast rows and market sparklines.
- **Possible application:** The Scratchpad Utility Wheel is the clearest interaction fit. The forecast and market examples suggest information styling for the expanded applications; the emblems could support an About view or optional shell branding.
- **Geometry options:** Compare continuous hexagon outlines, separated edge segments and nested outlines. Use chamfered rectangular panels for dense content while reserving hexagons for utility selection, icons and identity marks.
- **Tradeoff:** The large, sharp wordmark and decorative decals compete with functional content at small sizes. Keep those treatments at display scale and use a simpler mark where space is limited. Compact data examples do not reverse the decision to remove persistent weather/market widgets.

### Supporting logo and wheel variants

| Asset | Visible direction | Redesign option / open question |
| --- | --- | --- |
| [neurOS.png](concept_art/neurOS.png) | Purple wordmark with green edges and distressed metallic texture. | NSD-colored display branding; explore an optional About or shell welcome treatment. |
| [neuros.png](concept_art/neuros.png) | Gold/yellow wordmark with cyan edges in the same angular family. | An alternate palette reference for checking whether the identity survives a color change. |
| [neuros-splash.gif](concept_art/neuros-splash.gif) | GIF splash asset whose opening frame uses the gold/cyan wordmark. | Optional motion reference; timing and full animation behavior still need review. This does not add bootloader work to the interface scope. |
| [wheel_frame1.png](concept_art/wheel_frame1.png) | Broad purple outline with a flat top and bottom. | Flat-top hexagon candidate; test stroke weight and icon/key-label space at actual wheel size. |
| [wheel_frame2.png](concept_art/wheel_frame2.png) | Mint outline with top and bottom points. | Point-top hexagon candidate; compare orientation and spacing with the surrounding slots. |
| [wheel.svg](concept_art/wheel.svg) | Six purple Q/W/E/A/S/D slots around a glowing green center. | Concrete placement reference for the proposed wheel: W above, S below, Q/E upper sides and A/D lower sides. Geometry and center behavior remain open. |

The two wheel PNGs differ in orientation and size as well as color; they are not yet a matched idle/focus pair. The SVG is a layout sketch with mixed hexagon orientations, not proof of a regular interlocking construction. Prototype consistent geometry and hit areas before treating these assets as final controls.

### Combining the options

**Proposed prototype direction, not a decision:** Use B's readable panel structure for everyday utilities, A's luminous edges for attention states, C's telemetry treatments inside Den, and D's hexagonal vocabulary for the wheel and identity. Compare this combination with a more strongly illuminated A/D treatment using the same content.

- Keep purple/green as an example palette; resolve interface colors through theme tokens and preserve semantic warning/error colors.
- Use readable UI typography for controls and body text; explore technical or condensed lettering for short headings and monospaced numerals for data. The sheets do not establish an exact font choice.
- Treat fictional corporation labels, hazard tape, barcodes, glitch fragments and microtext as optional art direction. Replace placeholder copy with meaningful labels before any functional prototype; the sheets do not settle project lore.
- Compare a button/toggle group, one expanded utility panel, a Den telemetry section and the wheel at actual desktop scale, including keyboard focus, no glow, reduced motion and contrasting wallpapers.

**OPEN:** Which panel family should lead, how much texture belongs in normal use, whether flat-top or point-top hexagons best fit the wheel, which logo variant represents the interface, and where optional branding should appear.

## Scratchpad Utility Wheel (concept and beta)

**Status:** A six-action beta exists; the scratchpad concept and permanent assignments remain open. The interaction below is the original proposal, not a description of the beta.

### Concept

Introduce a keyboard-first **Scratchpad Utility Wheel** inspired by the modular geometry of CyberArch's theme selector, but redesigned around six interlocking, regular hexagonal utility slots surrounding a central hexagon.

The wheel is a temporary tool selector, **not a permanent desktop widget**. Its purpose is to summon frequently used scratchpad utilities without interrupting the current workspace.

### Layout and keyboard mapping

The six outer hexagons correspond spatially to the QWERTY keyboard cluster:

```text
       [Q]  [W]  [E]
            
       [A]  [S]  [D]
```

*Diagram is conceptual; final hexagon positioning and geometry require prototyping.*

**Proposed interaction:**

1. Hold `Super + Ctrl` to reveal the utility wheel.
2. Press `Q`, `W`, `E`, `A`, `S`, or `D` to select a corresponding utility.
3. The wheel closes and the selected utility opens as a scratchpad.
4. `Esc` cancels; mouse selection should also be supported.
5. Modifier-release dismissal without selection is a possible behavior, subject to implementation testing.

**Ergonomic rationale:** Holding the modifiers with the left hand leaves nearby fingers available for QWEASD selection, avoiding the longer reaches associated with number-row shortcuts.

### Visual direction

- **Local references:** [Concept art 4](concept_art/concept_art4.jpeg), [wheel layout sketch](concept_art/wheel.svg), [flat-top frame](concept_art/wheel_frame1.png) and [point-top frame](concept_art/wheel_frame2.png). See section 11 for the geometry options and unresolved differences between these references.
- Six geometrically consistent, interlocking hexagons around a central element.
- Preserve NeurOS's angular geometry, chamfered detailing and neon aesthetic.
- Avoid directly reproducing Cyberpunk 2077's skill-tree design or Henry's theme selector.
- Idle slots use the theme's primary accent and restrained glow.
- Hovered or keyboard-selected slots transition toward the **secondary accent**, which progressively overtakes the primary edge color with stronger glow.
- The selected utility remains clearly distinguishable when glow and animations are disabled.
- Glow intensity, motion and colors follow user appearance/accessibility preferences.

### Intended utility behavior

- Each slot launches or toggles a small, quickly accessible scratchpad utility.
- Potential utilities include terminal, calculator, quick notes, clipboard history, system monitor and media controls.
- **The six default utilities and their key assignments are TBD.**
- The central hexagon's function is also TBD; keep it simple initially.
- The wheel disappears after selection without becoming persistent desktop clutter.

### Relationship to other interfaces

| Component | Responsibility |
|---|---|
| **Utility Wheel** | Fast selection of frequently used scratchpad tools |
| **Scratchpad** | Temporary floating workspace for the selected tool |
| **Hotkey Access Panel** | Broader command and shortcut discovery |
| **Netrunner Den** | Full technical workspace for detailed diagnostics and tools |

These are complementary interfaces, not four competing application launchers.

### Usability and implementation considerations

- Make shortcut assignments configurable for different keyboard layouts and personal preferences.
- Provide mouse interaction and an accessible alternative to holding multiple keys.
- Ensure the compositor intercepts wheel shortcuts correctly without leaking selections into the previously focused application.
- Preserve focus and workspace behavior when opening or hiding scratchpads.
- Keep the wheel functional with animations and glow disabled.
- Prototype and validate modifier-only activation, key handling and focus transitions on Hyprland before committing to the interaction model.

### Initial scope

**V1 goal:** A six-slot wheel that opens, accepts keyboard or mouse selection, launches the assigned scratchpad, dismisses reliably and preserves focus correctly.

Avoid nested wheels, complex context-sensitive behavior, excessive configuration infrastructure and unrelated features until the basic interaction proves useful.

**Design principle:** *The interface stays quiet until the operator needs a tool. Geometry communicates organization; light communicates attention; keyboard placement determines interaction.*

## Option D delivery plan — draft

**Status:** Beta input shell implemented, 2026-11-20. The delivery sequence
below still covers the remaining scratchpad, persistence and live-session work;
it does not select a logo or a permanent desktop layout.

### Scope boundary

Option D should establish the **temporary Utility Wheel** and a restrained
identity vocabulary. It should not turn every panel into a hexagon or replace
the readable rectangular panel
structure proposed in Option B.

- Use a regular six-around-one arrangement for the wheel, with a neutral centre
  that closes/cancels in V1. This resolves the mismatch between the intended
  ring and the two-row Q/W/E/A/S/D sketch; the spatial mapping remains `W` top,
  `S` bottom, `Q/E` upper sides and `A/D` lower sides.
- Compare **flat-top** and **point-top** regular hexagons using the same slot
  size, labels and input paths. Do not promote the existing wheel assets to
  production geometry: they are references with inconsistent orientation.
- Use the N mark or wordmark only at display scale (an About/welcome view or
  optional branding). Dense controls get a simple label/icon and a semantic
  accessible name. Confirm asset provenance before shipping an art-derived mark.
- Resolve purple/mint through the primary/secondary palette tokens. Warning,
  recording and destructive states keep their semantic colors.

### V1 behaviour

The wheel is a short-lived overlay on the monitor under the pointer. It has six
focusable slots, a cancel centre, `Esc` dismissal, pointer hit targets and the
same Q/W/E/A/S/D keyboard map. A selection performs one action, dismisses the
wheel, and must not leak the selecting key into the previously focused client.

The beta uses six deliberately small seed actions that already exist in the
shell: terminal, forecast, applications, audio, system status and player. They
exercise both command and IPC routes without inventing a scratchpad service.
They are beta defaults rather than a permanent utility contract: persistence,
per-slot customization and an `unassigned` state arrive before a release
claims that a terminal, calculator, clipboard manager or notes app is
universally wanted.

### Architecture

1. Add a `utility-wheel.ts` presentation module. It owns only overlay lifetime,
   focus, pointer/key routing, vector geometry and the secondary-accent takeover.
   Reuse the shared `attention.ts` renderer and GTK window primitives; do not
   reuse `appsmenu.ts`, whose searchable application carousel and sound loop are
   a different interaction.
2. Keep a pure wheel model beside the renderer: slot id/key, label, optional
   icon, action descriptor, logical hexagon points and hit-test result. Geometry
   must be calculated in logical coordinates so it can be unit-tested at mixed
   DPI rather than inferred from a screenshot.
3. Introduce a small action broker with two initial descriptor types: a shell
   command and an existing shell IPC request. A future scratchpad controller can
   extend it with an application class/window rule without making the wheel
   responsible for Hyprland window placement.
4. Persist assignments separately from the presentation state in the existing
   user configuration area. Store stable action ids, not executable display
   labels; unknown or removed ids render as unassigned and never execute.
5. Register one `utility-wheel` IPC request in `core.ts` and one named action in
   `config/keybinds.lua`/`userbinds.ts`, so the opening shortcut is visible,
   conflict-checked and configurable like the existing trays.

### Input feasibility spike — first implementation task

The proposed modifier-only hold (`Super + Ctrl`) is not safe to commit until it
is proven in the live compositor. Normal binds cannot reliably distinguish a
modifier press/release sequence from application input or every possible keyboard
layout.

- Start with a configurable, explicit trigger such as `Super + Space`.
  It opens the exclusive overlay; Q/W/E/A/S/D, pointer activation and `Esc` are
  then handled by the overlay rather than global binds.
- Prototype the held-modifier version separately using Hyprland's supported
  input/submap mechanisms. It passes only if release cancels predictably,
  selection keys never reach the client, repeat/IME/layout behaviour is benign,
  and focus restores after cancellation.
- If that spike fails any criterion, retain the explicit trigger. The wheel's
  interaction quality matters more than preserving a clever activation gesture.

### Milestones and acceptance checks

| Milestone | Deliverable | Must prove |
| --- | --- | --- |
| 0. Geometry study | Two non-launching wheel studies: flat-top and point-top. | Regular outlines, non-overlapping hit areas, readable Q/W/E/A/S/D labels at normal and scaled DPI. |
| 1. Input shell | Exclusive overlay with keyboard focus, `Esc`, mouse hover/click and centre cancel. | No key leakage; keyboard-only route works; focus returns to the previous client on cancel. |
| 2. Action broker | Six beta seed descriptors, then configurable/unassigned slots. | Exactly one action fires per selection; errors surface without leaving an orphaned overlay. |
| 3. Scratchpad integration | A deliberately chosen first scratchpad utility. | Toggle/open, focus, workspace and close behaviour survive repeated use and monitor changes. |
| 4. Appearance/persistence | Token-driven attention, palette changes and saved assignments. | No-glow/reduced-motion states remain understandable; all palettes avoid hardcoded NSD colors. |
| 5. Live qualification | Hyprland session checks. | Multi-monitor, mixed DPI, hotplug, global HUD hiding, recording, IME/layout and shortcut-conflict behaviour are acceptable. |

### Test plan

- Unit-test hex path generation, scale-aware hit testing, nearest-slot selection
  and the hidden/open/selected/dismissed state machine.
- Add regression coverage for animation reversal and no-motion/no-glow focus
  cues through the existing attention test approach.
- Exercise the IPC request and keybind registry in isolated tests, then perform
  the input/focus checks in a real Hyprland session. Mocked GTK tests cannot
  certify modifier-release behaviour or compositor key delivery.
- Validate the same wheel over light/dark and static/live wallpapers. It must
  be readable without relying on its backdrop.

### Decisions required before Milestone 3

1. Does the beta point-top geometry work at desktop scale, or should flat-top be explored?
2. Does the held-modifier trigger pass the live spike, or does V1 keep an
   explicit toggle chord?
3. Which six utilities are supported first, and which are actual scratchpads
   rather than simple shell actions?
4. Which mark, if any, has the right provenance and deserves optional branding?
