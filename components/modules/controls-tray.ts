import { Box } from "./widget.ts"
import { Toggles, HorizDock } from "./dock.ts"
import { createUtilTray } from "./util-tray.ts"

const controls = createUtilTray({
    visibilityKey: "trayControls",
    label: "CONTROLS",
    code: "01",
    caption: "LOCAL / I/O",
    content: mon => Box({ vertical: true, children: [Toggles(mon), HorizDock(mon)] }),
})
export const ControlsTray = controls.create
export const toggleControlsTray = controls.toggle
