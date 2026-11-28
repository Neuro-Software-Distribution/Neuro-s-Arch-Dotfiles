import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { stripTypeScriptTypes } from 'node:module'
import vm from 'node:vm'

test('system monitor keyboard switches tabs and refreshes logs', async () => {
    const source = readFileSync('components/modules/cmodal.ts', 'utf8')
    const body = source.slice(source.indexOf('const SysCtrl ='), source.indexOf('const KEYBINDS ='))
    const commands = [], keys = { KEY_1: 49, KEY_4: 52, KEY_Left: 100, KEY_Right: 101, KEY_Up: 102, KEY_Down: 103, KEY_Return: 104, KEY_KP_Enter: 105 }
    let spec, draws = 0
    const context = vm.createContext({
        Gdk: keys, sh: command => { commands.push(command); return Promise.resolve('') },
        createModal: options => { spec = options; return { requestDraw: () => draws++ } },
    })
    vm.runInContext(stripTypeScriptTypes(body) + '\nglobalThis.make = SysCtrl', context)
    context.make(1920, 1080)
    assert.equal(spec.onKey(keys.KEY_4), true)
    assert.match(commands.at(-1), /journalctl/)
    assert.equal(spec.onKey(keys.KEY_Right), true)
    assert.equal(spec.onKey(keys.KEY_Left), true)
    assert.equal(commands.filter(command => command.includes('journalctl')).length, 2)
    assert.equal(spec.onKey(keys.KEY_Up), true)
    assert.equal(spec.onKey(keys.KEY_Return), false)
    assert.equal(spec.onKey(999), false)
    assert.ok(draws >= 3)
    await Promise.resolve()
})
