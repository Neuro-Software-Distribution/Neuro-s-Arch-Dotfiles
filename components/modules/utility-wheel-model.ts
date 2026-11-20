// Pure geometry and selection rules for the Option D utility wheel.  Keeping
// this free of GTK/GI imports gives the interaction a small, deterministic
// surface that can be tested without a compositor.

export type WheelKey = "q" | "w" | "e" | "a" | "s" | "d"
export type Point = [number, number]

export type WheelAction =
    | { type: "request", request: string }
    | { type: "command", command: "terminal" }

export type WheelSlot = {
    key: WheelKey
    label: string
    detail: string
    action: WheelAction
}

export type WheelLayout = {
    center: Point
    ringRadius: number
    slotRadius: number
    centerRadius: number
}

export const SLOT_ORDER: WheelKey[] = ["w", "e", "d", "s", "a", "q"]

// These are beta seed assignments, not a new persistent scratchpad contract.
// Every request targets a shell feature that already has an IPC route.
export const BETA_SLOTS: WheelSlot[] = [
    { key: "q", label: "TERMINAL", detail: "OPEN SHELL", action: { type: "command", command: "terminal" } },
    { key: "w", label: "FORECAST", detail: "LOCAL WEATHER", action: { type: "request", request: "forecast" } },
    { key: "e", label: "APPS", detail: "APPLICATIONS", action: { type: "request", request: "apps-menu" } },
    { key: "a", label: "AUDIO", detail: "VOLUME CONTROL", action: { type: "request", request: "modal vol" } },
    { key: "s", label: "SYSTEM", detail: "SYSTEM STATUS", action: { type: "request", request: "modal sys" } },
    { key: "d", label: "PLAYER", detail: "NOW PLAYING", action: { type: "request", request: "player" } },
]

const slotByKey = new Map<WheelKey, WheelSlot>(BETA_SLOTS.map(slot => [slot.key, slot]))

export const slotForKey = (key: string): WheelSlot | null =>
    slotByKey.get(key.toLowerCase() as WheelKey) || null

export const wheelLayout = (width: number, height: number): WheelLayout => {
    const scale = Math.max(0.72, Math.min(1.25, Math.min(width / 1920, height / 1080)))
    return {
        center: [width / 2, height / 2],
        ringRadius: 176 * scale,
        slotRadius: 62 * scale,
        centerRadius: 52 * scale,
    }
}

// Point-top hexagons let W and S sit on the vertical axis as described in D.
export const regularHex = (center: Point, radius: number): Point[] =>
    Array.from({ length: 6 }, (_, i) => {
        const angle = -Math.PI / 2 + i * Math.PI / 3
        return [center[0] + Math.cos(angle) * radius, center[1] + Math.sin(angle) * radius]
    })

export const slotCenter = (key: WheelKey, layout: WheelLayout): Point => {
    const [cx, cy] = layout.center
    const positions: Record<WheelKey, Point> = {
        q: [-Math.sqrt(3) / 2, -0.5], w: [0, -1], e: [Math.sqrt(3) / 2, -0.5],
        a: [-Math.sqrt(3) / 2, 0.5], s: [0, 1], d: [Math.sqrt(3) / 2, 0.5],
    }
    const [x, y] = positions[key]
    return [cx + x * layout.ringRadius, cy + y * layout.ringRadius]
}

export const slotPolygon = (key: WheelKey, layout: WheelLayout): Point[] =>
    regularHex(slotCenter(key, layout), layout.slotRadius)

export const pointInPolygon = (point: Point, polygon: Point[]): boolean => {
    let inside = false
    for (let i = 0, j = polygon.length - 1; i < polygon.length; j = i++) {
        const [xi, yi] = polygon[i], [xj, yj] = polygon[j]
        const crosses = (yi > point[1]) !== (yj > point[1])
        const atX = (xj - xi) * (point[1] - yi) / (yj - yi || Number.EPSILON) + xi
        if (crosses && point[0] < atX) inside = !inside
    }
    return inside
}

export type WheelHit = WheelKey | "center" | null

export const hitTestWheel = (point: Point, layout: WheelLayout): WheelHit => {
    const [cx, cy] = layout.center
    if (Math.hypot(point[0] - cx, point[1] - cy) <= layout.centerRadius) return "center"
    for (const key of SLOT_ORDER) if (pointInPolygon(point, slotPolygon(key, layout))) return key
    return null
}

export const cycleSlot = (current: WheelKey | null, direction: 1 | -1): WheelKey => {
    const index = current ? SLOT_ORDER.indexOf(current) : 0
    return SLOT_ORDER[(index + direction + SLOT_ORDER.length) % SLOT_ORDER.length]
}
