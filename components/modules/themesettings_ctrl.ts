import { SCREEN_WIDTH, SCREEN_HEIGHT } from "../../env.ts"
import { TITLE, MONO, txt } from "./glass.ts"
import { createModal } from "./cmodal.ts"
import { USER } from "./colors.ts"
import Gdk from "gi://Gdk?version=3.0"
import {
    readTune, TABS, setThemeSettingsController,
    drawColors, drawKeybinds, drawConfig, drawWm, drawWallRing, drawWallBrowse, drawWallPicker,
    wallOpen, scrollWall, wallPickerOpen, wallPickerScroll, setWallPickerScroll, wallPickerKey,
    kbScroll, kbMaxScroll, setKbScroll,
    hexEditing, colorsKeyRaw, colorsHexCancel
} from "./themesettings.ts"
import { stopModalStats } from "./sys.ts"

const SW = SCREEN_WIDTH, SH = SCREEN_HEIGHT
const tabBase = (): [number, number, number] => USER.sysveil as any
const tabAcc = (): [number, number, number] => USER.cyan as any

export const ThemeSettingsCtrl = () => {
    const st: any = { tab: TABS[0][1] }
    let ctrl: any

    ctrl = createModal({
        name: "themesettings",
        tabTitle: "THEME SETTINGS",
        W: SW,
        H: SH,
        noGlass: true,
        pad: 0,
        idleFrameMs: 70,
        col: USER.sysveil as any,
        accent: USER.sysveil as any,
        onOpen: () => {
            st.tab = TABS[0][1]
            setKbScroll(0)
            readTune()
        },
        onClose: () => {
            stopModalStats()
        },
        onScroll: (d) => {
            if (st.tab === "wall" && wallPickerOpen) {
                setWallPickerScroll(wallPickerScroll + d * 36)
                ctrl.requestDraw()
                return
            }
            if (st.tab === "wall" && wallOpen) {
                scrollWall(d * 36)
                ctrl.requestDraw()
                return
            }
            if (st.tab === "keybinds" || st.tab === "wm" || st.tab === "anim" || st.tab === "colors") {
                const newScroll = kbScroll + d * 36
                if (newScroll >= 0 && newScroll <= kbMaxScroll) {
                    setKbScroll(newScroll)
                    ctrl.requestDraw()
                }
            }
        },
        onKeyRaw: (k, m, pressed) => { colorsKeyRaw(k, m, pressed) },
        onKey: (k) => {
            if (hexEditing()) {
                if (k === Gdk.KEY_Escape) { colorsHexCancel(); return true }
                return true
            }
            if (st.tab === "wall" && wallPickerOpen) {
                if (wallPickerKey(k)) return true
            }
            if (k === Gdk.KEY_Left || k === Gdk.KEY_Right) {
                const idx = TABS.findIndex(([, id]) => id === st.tab)
                if (idx < 0) return
                const next = k === Gdk.KEY_Left ? idx - 1 : idx + 1
                if (next >= 0 && next < TABS.length) {
                    st.tab = TABS[next][1]
                    setKbScroll(0)
                    ctrl.requestDraw()
                }
                return true
            }
        },
        draw: (ctx, g) => {
            const X = g.X, Y = g.Y, W = g.w, H = g.h
            const base = tabBase(), acc = tabAcc()
            const panelX = X + Math.max(22, (W - 1280) / 2)
            const panelW = W - (panelX - X) * 2
            const panelY = Y + 28, panelH = H - 56
            const cut = 20
            const line = (color, alpha, width, x1, y1, x2, y2) => {
                ctx.setSourceRGBA(color[0], color[1], color[2], alpha)
                ctx.setLineWidth(width); ctx.newPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke()
            }

            ctx.setSourceRGBA(0.008, 0.01, 0.018, 0.78)
            ctx.rectangle(0, 0, SW, SH); ctx.fill()
            ctx.newPath()
            ctx.moveTo(panelX + cut, panelY); ctx.lineTo(panelX + panelW, panelY)
            ctx.lineTo(panelX + panelW, panelY + panelH - cut)
            ctx.lineTo(panelX + panelW - cut, panelY + panelH)
            ctx.lineTo(panelX, panelY + panelH); ctx.lineTo(panelX, panelY + cut)
            ctx.closePath()
            ctx.setSourceRGBA(0.025, 0.03, 0.045, 0.97); ctx.fillPreserve()
            ctx.setSourceRGBA(base[0], base[1], base[2], 0.72); ctx.setLineWidth(1); ctx.stroke()
            line(acc, 0.9, 2, panelX + cut, panelY, panelX + 160, panelY)

            const left = panelX + 32, right = panelX + panelW - 32
            txt(ctx, left, panelY + 33, "NEUROS  /  SETTINGS", TITLE, 17, acc, 1)
            txt(ctx, left, panelY + 54, "DESKTOP CONFIGURATION", MONO, 10, base, 0.8)
            const hint = "←  →  SECTIONS     ESC  CLOSE"
            ctx.selectFontFace(MONO, 0, 0); ctx.setFontSize(10)
            txt(ctx, right - ctx.textExtents(hint).width, panelY + 39, hint, MONO, 10, base, 0.8)
            line(base, 0.32, 1, left, panelY + 70, right, panelY + 70)

            const navY = panelY + 82
            const navW = (panelW - 64) / TABS.length
            TABS.forEach(([label, id], i) => {
                const nx = left + i * navW
                const active = st.tab === id
                const hover = g.push.hoverKey === `tab:${id}`
                if (active || hover) {
                    ctx.setSourceRGBA(acc[0], acc[1], acc[2], active ? 0.14 : 0.07)
                    ctx.rectangle(nx, navY, navW - 6, 42); ctx.fill()
                    line(acc, active ? 1 : 0.5, active ? 2 : 1, nx, navY + 41, nx + navW - 6, navY + 41)
                }
                txt(ctx, nx + 9, navY + 16, `0${i + 1}`, MONO, 9, active ? acc : base, 0.7)
                txt(ctx, nx + 9, navY + 33, label, TITLE, 11, active || hover ? acc : base, active ? 1 : 0.75)
                g.push({ kind: "tab", key: `tab:${id}`, hoverable: true,
                    bx0: nx, by0: navY, bx1: nx + navW - 6, by1: navY + 42,
                    on: () => { st.tab = id; setKbScroll(0); ctrl.requestDraw() } })
            })

            // Existing content renderers derive their scroll viewport from g's bounds.
            const mx = left + 18, mw = panelW - 100, cy = navY + 62
            const content = { ...g, Y: panelY, h: panelH - 14 }
            if (st.tab === "colors") drawColors(ctx, content, mx, cy, mw)
            else if (st.tab === "keybinds") drawKeybinds(ctx, content, mx, cy, mw)
            else if (st.tab === "anim") drawConfig(ctx, content, mx, cy, mw)
            else if (st.tab === "wm") drawWm(ctx, content, mx, cy, mw)
            else if (st.tab === "wall") {
                if (wallPickerOpen) drawWallPicker(ctx, content, mx, cy, mw)
                else if (wallOpen) drawWallBrowse(ctx, content, mx, cy, mw)
                else drawWallRing(ctx, content, mx, cy, mw)
            }
        },
    })

    setThemeSettingsController(ctrl)
    return ctrl
}
