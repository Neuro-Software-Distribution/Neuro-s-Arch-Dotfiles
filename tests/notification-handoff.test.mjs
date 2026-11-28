import test from 'node:test'
import assert from 'node:assert/strict'
import { readFileSync } from 'node:fs'
import { stripTypeScriptTypes } from 'node:module'
import vm from 'node:vm'

test('replacements update one message-center row', () => {
    const source = readFileSync('components/modules/notifmessages.ts', 'utf8')
    const add = source.slice(source.indexOf('const add = (n: any)'), source.indexOf('export const isNotifHudOpen'))
    const ctx = vm.createContext({ msgs: [], _readFilter: null, MAXROWS: 7, view: 'main',
        selectedApp: null, hudVisible: false, kick() {}, applyInput() {} })
    vm.runInContext(stripTypeScriptTypes(add) + '\nglobalThis.add = add', ctx)
    ctx.add({ id: 17, summary: 'Original', body: 'first' })
    ctx.add({ id: 17, summary: 'Updated', body: 'second' })
    assert.equal(ctx.msgs.length, 1)
    assert.equal(ctx.msgs[0].title, 'UPDATED')
    assert.equal(ctx.msgs[0].body, 'second')
})

test('legacy popup resumes when the native renderer disappears', () => {
    const source = readFileSync('components/modules/notifpopup.ts', 'utf8')
    const add = source.slice(source.indexOf('const add = (n: any)'), source.indexOf('export const NotifPopupWindow'))
    const ctx = vm.createContext({ nativeRendererActive: true, msgs: [], MAXFR: 8,
        intro: 0, closing: false, holdUntil: 0, win: { visible: true },
        LIFETIME: 15000, play() {}, kick() {}, timeout() {} })
    vm.runInContext(stripTypeScriptTypes(add) + '\nglobalThis.add = add', ctx)
    ctx.add({ id: 1, summary: 'Native owns popups' })
    assert.equal(ctx.msgs.length, 0)
    ctx.nativeRendererActive = false
    ctx.add({ id: 2, summary: 'Fallback' })
    assert.equal(ctx.msgs.length, 1)
    assert.equal(ctx.msgs[0].id, 2)
})

test('notification shortcuts use the native renderer and fall back on failure', () => {
    const source = readFileSync('core.ts', 'utf8')
    const helper = source.slice(source.indexOf('const notificationAction ='), source.indexOf('const compileCss ='))
    let reply = true, fails = false, calls = 0, fallbacks = 0
    const ctx = vm.createContext({
        Gio: { DBusCallFlags: { NO_AUTO_START: 1 }, DBus: { session: { call(...args) {
            calls++
            args.at(-1)({ call_finish() { if (fails) throw Error('renderer unavailable'); return { deep_unpack: () => [reply] } } }, {})
        } } } }, GLib: { VariantType: class {} },
    })
    vm.runInContext(stripTypeScriptTypes(helper) + '\nglobalThis.run = notificationAction', ctx)
    ctx.run('Read', () => fallbacks++)
    assert.equal(fallbacks, 0)
    reply = false; ctx.run('Dismiss', () => fallbacks++)
    fails = true; ctx.run('Read', () => fallbacks++)
    assert.equal(calls, 3)
    assert.equal(fallbacks, 2)
})
