import GLib from "gi://GLib"
import Gdk from "gi://Gdk?version=3.0"
import { execAsync } from "astal"
import { Anchor, DrawingArea, EventBox, Exclusivity, Keymode, Layer, Window, activeMonitor } from "./widget.ts"
import { NEON, onColorChange } from "./colors.ts"
import { TITLE, MONO } from "./fonts.ts"
import { CYBER_DIR } from "../../env.ts"
import { createAttention, drawAttentionEdge } from "./attention.ts"
import { BETA_SLOTS, SLOT_ORDER, WheelKey, WheelSlot, cycleSlot, hitTestWheel, regularHex, slotForKey, slotPolygon, wheelLayout } from "./utility-wheel-model.ts"

let wheelWin: any = null
let wheelArea: any = null
let wheelOpen = false
let hovered: WheelKey | null = null
let focused: WheelKey | null = "w"
const attention = new Map<WheelKey, ReturnType<typeof createAttention>>()

const rgb = (name: string) => (NEON[name] || NEON.dock).map(value => value / 255)
const path = (ctx: any, points: number[][]) => {
    ctx.newPath()
    points.forEach(([x, y], index) => index ? ctx.lineTo(x, y) : ctx.moveTo(x, y))
    ctx.closePath()
}
const text = (ctx: any, value: string, x: number, y: number) => {
    const extents = ctx.textExtents(value)
    ctx.moveTo(x - extents.width / 2, y)
    ctx.showText(value)
}
const coords = (event: any): [number, number] => {
    try {
        const point = event.get_coords?.()
        if (point && point.length >= 3) return [point[1], point[2]]
    } catch {}
    return [event.x || 0, event.y || 0]
}
const quote = (value: string) => `'${value.replace(/'/g, "'\\''")}'`

const sendRequest = (request: string) => {
    const socket = `${GLib.get_user_runtime_dir()}/astal/cyberpunk.sock`
    // Requests are fixed beta routes, but quote both values so a nonstandard
    // runtime path remains safe and does not change the shell command shape.
    execAsync(["sh", "-c", `printf '%s\\n' ${quote(request)} | socat - UNIX-CONNECT:${quote(socket)}`])
        .catch((error) => print("[utility-wheel] request:", error))
}

const runSlot = (slot: WheelSlot) => {
    closeUtilityWheel()
    if (slot.action.type === "command") {
        execAsync([`${CYBER_DIR}/scripts/${slot.action.command}`])
            .catch((error) => print("[utility-wheel] command:", error))
    } else sendRequest(slot.action.request)
}

const syncAttention = () => {
    for (const key of SLOT_ORDER) attention.get(key)?.set({ hovered: key === hovered, focused: key === focused, selected: false })
    wheelArea?.queue_draw()
}
const setFocus = (key: WheelKey | null) => { focused = key; syncAttention() }

const drawSlot = (ctx: any, slot: WheelSlot, layout: ReturnType<typeof wheelLayout>) => {
    const key = slot.key, points = slotPolygon(key, layout), [x, y] = points.reduce(([sx, sy], p) => [sx + p[0] / points.length, sy + p[1] / points.length], [0, 0])
    const state = attention.get(key)
    const level = state?.value || 0
    const [r, g, b] = rgb("wheelbg"), accent = rgb("wheelfg")
    path(ctx, points)
    ctx.setSourceRGBA(r * (0.75 + level * 0.12), g * (0.75 + level * 0.12), b * (0.75 + level * 0.12), 0.84 + level * 0.08)
    ctx.fill()
    if (level > 0) {
        path(ctx, points)
        ctx.setSourceRGBA(...accent, 0.08 + level * 0.16)
        ctx.fill()
    }
    drawAttentionEdge(ctx, points, level, state?.focused, 1, Math.max(0.75, layout.slotRadius / 62))

    ctx.selectFontFace(TITLE, 0, 1); ctx.setFontSize(Math.max(12, layout.slotRadius * 0.28))
    ctx.setSourceRGBA(...accent, 0.96)
    text(ctx, slot.label, x, y - 4)
    ctx.selectFontFace(MONO, 0, 0); ctx.setFontSize(Math.max(7, layout.slotRadius * 0.14))
    ctx.setSourceRGBA(...accent, 0.62)
    text(ctx, `[${slot.key.toUpperCase()}] ${slot.detail}`, x, y + Math.max(14, layout.slotRadius * 0.26))
}

const draw = (ctx: any) => {
    if (!wheelArea) return
    const width = wheelArea.get_allocated_width?.() || 1920
    const height = wheelArea.get_allocated_height?.() || 1080
    const layout = wheelLayout(width, height)
    const [cx, cy] = layout.center, accent = rgb("wheelfg"), secondary = rgb("press")
    ctx.save()
    ctx.setSourceRGBA(0, 0, 0, 0.32); ctx.rectangle(0, 0, width, height); ctx.fill()
    for (const key of SLOT_ORDER) {
        const point = slotPolygon(key, layout)[0]
        ctx.newPath(); ctx.moveTo(cx, cy); ctx.lineTo(point[0], point[1])
        ctx.setSourceRGBA(...accent, 0.16); ctx.setLineWidth(1); ctx.stroke()
    }
    for (const slot of BETA_SLOTS) drawSlot(ctx, slot, layout)
    const center = regularHex(layout.center, layout.centerRadius)
    path(ctx, center); ctx.setSourceRGBA(0.015, 0.05, 0.07, 0.96); ctx.fill()
    path(ctx, center); ctx.setSourceRGBA(...secondary, 0.88); ctx.setLineWidth(1.3); ctx.stroke()
    ctx.selectFontFace(TITLE, 0, 1); ctx.setFontSize(Math.max(11, layout.centerRadius * 0.29)); ctx.setSourceRGBA(...accent, 0.95)
    text(ctx, "UTILITY", cx, cy - 2)
    ctx.selectFontFace(MONO, 0, 0); ctx.setFontSize(Math.max(7, layout.centerRadius * 0.14)); ctx.setSourceRGBA(...accent, 0.62)
    text(ctx, "ESC / CANCEL", cx, cy + Math.max(13, layout.centerRadius * 0.25))
    ctx.restore()
}

export const closeUtilityWheel = () => {
    if (!wheelOpen) return
    wheelOpen = false; hovered = null
    if (wheelWin) wheelWin.visible = false
    syncAttention()
}

export const toggleUtilityWheel = () => {
    if (!wheelWin) return
    if (wheelOpen) { closeUtilityWheel(); return }
    try { wheelWin.gdkmonitor = activeMonitor() } catch {}
    wheelOpen = true; hovered = null; focused = "w"
    wheelWin.visible = true
    try { wheelWin.grab_focus() } catch {}
    syncAttention()
}

export const UtilityWheelWindow = () => {
    if (wheelWin) return wheelWin
    wheelArea = DrawingArea({})
    wheelArea.connect("draw", (_widget, ctx) => (draw(ctx), false))
    for (const slot of BETA_SLOTS) attention.set(slot.key, createAttention(wheelArea))
    const offColors = onColorChange(() => wheelArea?.queue_draw())
    const events = EventBox({ child: wheelArea })
    try { events.add_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.POINTER_MOTION_MASK) } catch {}
    events.connect("motion-notify-event", (_widget, event) => {
        if (!wheelOpen) return true
        const hit = hitTestWheel(coords(event), wheelLayout(wheelArea.get_allocated_width(), wheelArea.get_allocated_height()))
        hovered = typeof hit === "string" && hit !== "center" ? hit : null
        if (hovered) focused = hovered
        syncAttention(); return true
    })
    events.connect("button-press-event", (_widget, event) => {
        if (!wheelOpen) return true
        let button = 1; try { button = event.get_button?.()[1] ?? event.button } catch {}
        if (button !== 1) { closeUtilityWheel(); return true }
        const hit = hitTestWheel(coords(event), wheelLayout(wheelArea.get_allocated_width(), wheelArea.get_allocated_height()))
        if (hit && hit !== "center") runSlot(slotForKey(hit)!)
        else closeUtilityWheel()
        return true
    })
    wheelWin = Window({
        name: "utility-wheel", namespace: "utility-wheel", className: "aug utility-wheel",
        anchor: Anchor.TOP | Anchor.BOTTOM | Anchor.LEFT | Anchor.RIGHT,
        layer: Layer.OVERLAY, exclusivity: Exclusivity.IGNORE, keymode: Keymode.EXCLUSIVE,
        visible: false, child: events,
    })
    wheelWin.connect("key-press-event", (_widget, event) => {
        let keyval = 0; try { const found = event.get_keyval?.(); keyval = found ? found[1] : event.keyval } catch { keyval = event.keyval }
        if (keyval === Gdk.KEY_Escape) { closeUtilityWheel(); return true }
        if (keyval === Gdk.KEY_Tab) {
            let reverse = false; try { reverse = !!(event.get_state?.()[1] & Gdk.ModifierType.SHIFT_MASK) } catch {}
            setFocus(cycleSlot(focused, reverse ? -1 : 1)); return true
        }
        if (keyval === Gdk.KEY_Return || keyval === Gdk.KEY_KP_Enter || keyval === Gdk.KEY_space) {
            const slot = focused && slotForKey(focused); if (slot) runSlot(slot); else closeUtilityWheel(); return true
        }
        const unicode = Gdk.keyval_to_unicode(keyval)
        const slot = unicode ? slotForKey(String.fromCharCode(unicode)) : null
        if (slot) { runSlot(slot); return true }
        // The overlay is modal: unrelated keys must not leak to the client below it.
        return true
    })
    wheelWin.connect("destroy", () => { offColors(); attention.forEach(item => item.dispose()); attention.clear(); wheelWin = null; wheelArea = null })
    return wheelWin
}
