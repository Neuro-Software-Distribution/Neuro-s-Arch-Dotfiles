import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { stripTypeScriptTypes } from 'node:module'
import vm from 'node:vm'

const source = readFileSync('components/modules/utility-wheel-model.ts', 'utf8')
const context = vm.createContext({ Map, Math, Array, Number })
vm.runInContext(stripTypeScriptTypes(source.replace(/^export /gm, '')) +
    '\nglobalThis.api = { BETA_SLOTS, SLOT_ORDER, wheelLayout, slotCenter, slotPolygon, hitTestWheel, slotForKey, cycleSlot }', context)
const api = context.api

test('Option D maps QWE / ASD to a regular six-around-one wheel', () => {
    assert.deepEqual(Array.from(api.BETA_SLOTS, slot => slot.key).sort(), ['a', 'd', 'e', 'q', 's', 'w'])
    const layout = api.wheelLayout(1920, 1080)
    const [cx, cy] = layout.center
    const w = api.slotCenter('w', layout), s = api.slotCenter('s', layout)
    const q = api.slotCenter('q', layout), e = api.slotCenter('e', layout)
    const a = api.slotCenter('a', layout), d = api.slotCenter('d', layout)
    assert.deepEqual(Array.from(w), [cx, cy - layout.ringRadius])
    assert.deepEqual(Array.from(s), [cx, cy + layout.ringRadius])
    assert.ok(q[0] < cx && q[1] < cy && e[0] > cx && e[1] < cy)
    assert.ok(a[0] < cx && a[1] > cy && d[0] > cx && d[1] > cy)
    assert.equal(api.slotPolygon('w', layout).length, 6)
})

test('hit testing reserves the neutral centre and rejects the gaps', () => {
    const layout = api.wheelLayout(1920, 1080)
    assert.equal(api.hitTestWheel(layout.center, layout), 'center')
    for (const key of api.SLOT_ORDER) assert.equal(api.hitTestWheel(api.slotCenter(key, layout), layout), key)
    assert.equal(api.hitTestWheel([0, 0], layout), null)
})

test('keyboard selection is case-insensitive and Tab order wraps', () => {
    assert.equal(api.slotForKey('W').label, 'FORECAST')
    assert.equal(api.slotForKey('x'), null)
    assert.equal(api.cycleSlot('q', 1), 'w')
    assert.equal(api.cycleSlot('w', -1), 'q')
})

test('the beta route and configurable keybind stay registered together', () => {
    const core = readFileSync('core.ts', 'utf8')
    const binds = readFileSync('config/keybinds.lua', 'utf8')
    const registry = readFileSync('components/modules/userbinds.ts', 'utf8')
    assert.match(core, /request === "utility-wheel"/)
    assert.match(core, /UtilityWheelWindow\(\)/)
    assert.match(binds, /id="hud\.utilitywheel"[\s\S]*sock\("utility-wheel"\)/)
    assert.match(registry, /id: "hud\.utilitywheel"[\s\S]*mod: "SUPER \+ CTRL"[\s\S]*key: "space"/)
})
