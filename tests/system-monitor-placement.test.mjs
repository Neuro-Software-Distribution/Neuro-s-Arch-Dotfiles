import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { stripTypeScriptTypes } from 'node:module'
import vm from 'node:vm'

test('system monitor targets compositor cursor, including equal-sized displays, and falls back', () => {
    const source = readFileSync('components/modules/cmodal.ts', 'utf8')
    const section = source.slice(source.indexOf('let sysInst: '), source.indexOf('export const CModalWindows'))
    const left = { get_geometry: () => ({ width: 1920, height: 1080 }) }
    const right = { get_geometry: () => ({ width: 1920, height: 1080 }) }
    let position = { x: 2600, y: 200 }, fail = false, created = 0
    const context = vm.createContext({
        GLib: { SpawnFlags: { SEARCH_PATH: 1 }, spawn_sync: () => fail ? [false, null, null, 1] : [true, new TextEncoder().encode(JSON.stringify(position)), null, 0] },
        TextDecoder, Number, JSON, print: () => {}, activeMonitor: () => left,
        monitorAtPoint: x => x >= 1920 ? right : left,
        SCREEN_WIDTH: 1920, SCREEN_HEIGHT: 1080, cregistry: {},
        SysCtrl: () => { created++; return { close() {} } },
    })
    vm.runInContext(stripTypeScriptTypes(section) + '\nglobalThis.target = systemMonitorTarget; globalThis.get = sysGet', context)
    assert.equal(context.target(), right)
    const first = context.get(context.target())
    position = { x: 500, y: 200 }
    assert.equal(context.target(), left)
    assert.equal(context.get(context.target()), first, 'same-sized monitors reuse the controller')
    assert.equal(created, 1)
    fail = true
    assert.equal(context.target(), left)
})
