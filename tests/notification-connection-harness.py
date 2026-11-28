#!/usr/bin/env python3
"""Test renderer/Astal interaction inside a disposable D-Bus session.

Run with: dbus-run-session -- env NEUROS_ISOLATED_NOTIFICATION_TEST=1 \
    python3 tests/notification-connection-harness.py
Requires a Wayland compositor supporting layer shell. Never run against the
user's regular session bus.
"""
import os
from pathlib import Path
import subprocess
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(os.environ.get('NEUROS_ISOLATED_NOTIFICATION_TEST') == '1',
                     'requires an explicitly isolated D-Bus and Wayland session')
class Connection(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.env = dict(os.environ, XDG_CONFIG_HOME=str(self.root / 'config'),
                        XDG_CACHE_HOME=str(self.root / 'cache'), XDG_STATE_HOME=str(self.root / 'state'),
                        GSETTINGS_BACKEND='memory')
        self.palette = self.root / 'config/cyberarch/notification.palette'
        self.palette.parent.mkdir(parents=True)
        self.palette.write_text('[palette]\naccent=#c170ff\nsecondary=#00eb74\n'
                                'foreground=#e1e8fa\nbackground=#070912\n')
        self.binary = self.root / 'renderer'
        subprocess.run(['bash', str(ROOT / 'scripts/build-notification-preview'), str(self.binary)], check=True)
        self.log = self.root / 'renderer.log'
        self.output = self.log.open('w')
        self.addCleanup(self.output.close)
        self.renderer = subprocess.Popen([str(self.binary), '--listen'], env=self.env,
                                         stdout=self.output, stderr=subprocess.STDOUT)
        self.addCleanup(self.stop, self.renderer)
        self.wait_for(lambda: self.has_owner(), 'notification service did not start')
        self.wait_for(lambda: self.has_owner('io.neuros.NotificationRenderer'), 'renderer did not become ready')

    @staticmethod
    def stop(process):
        if process.poll() is None:
            process.terminate()
            try: process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill(); process.wait(timeout=3)

    def call(self, *args):
        return subprocess.run(args, env=self.env, capture_output=True, text=True, timeout=5, check=True).stdout

    def has_owner(self, name='org.freedesktop.Notifications'):
        return 'true' in self.call('gdbus', 'call', '--session', '--dest', 'org.freedesktop.DBus',
                                   '--object-path', '/org/freedesktop/DBus',
                                   '--method', 'org.freedesktop.DBus.NameHasOwner',
                                   name)

    def owner(self):
        result = subprocess.run(['gdbus', 'call', '--session', '--dest', 'org.freedesktop.DBus',
                                 '--object-path', '/org/freedesktop/DBus', '--method',
                                 'org.freedesktop.DBus.GetNameOwner', 'org.freedesktop.Notifications'],
                                env=self.env, capture_output=True, text=True, timeout=5)
        return result.stdout.strip() if result.returncode == 0 else ''

    def wait_for(self, check, message, check_renderer=True):
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if check(): return
            if check_renderer and hasattr(self, 'renderer') and self.renderer.poll() is not None:
                self.fail(f'{message}: {self.log.read_text()}')
            time.sleep(0.05)
        self.fail(f'{message}: {self.log.read_text()}')

    def test_replacement_resolution_and_message_center_proxy(self):
        proxy_script = self.root / 'proxy.js'
        proxy_script.write_text('''
import AstalNotifd from "gi://AstalNotifd";
import GLib from "gi://GLib";
const service = AstalNotifd.get_default();
service.connect("notified", (_s, id) => {
    const n = service.get_notification(id);
    print(`proxy notified ${id} image=${n?.get_image() || ""}`);
});
new GLib.MainLoop(null, false).run();
''')
        proxy_log = self.root / 'proxy.log'
        with proxy_log.open('w') as stream:
            proxy = subprocess.Popen(['gjs', '-m', str(proxy_script)], env=self.env,
                                     stdout=stream, stderr=subprocess.STDOUT)
        self.addCleanup(self.stop, proxy)
        # The proxy sets up its subscriptions asynchronously.
        time.sleep(0.5)
        first = self.call('notify-send', '--print-id', '--expire-time=0', '--app-name=Test',
                          'Original', 'First body').strip()
        self.assertTrue(first.isdigit(), first)
        self.wait_for(lambda: f'Notification popup displayed: {first}' in self.log.read_text(),
                      'renderer did not display the notification')
        self.wait_for(lambda: f'proxy notified {first}' in proxy_log.read_text(),
                      'message center proxy did not receive the notification')
        second = self.call('notify-send', '--print-id', '--replace-id', first, '--expire-time=0',
                           '--app-name=Test', 'Replacement', 'Second body').strip()
        self.assertEqual(second, first)
        self.wait_for(lambda: self.log.read_text().count(f'Notification popup displayed: {first}') == 2,
                      'renderer did not replace the popup')
        self.call('gdbus', 'call', '--session', '--dest', 'org.freedesktop.Notifications',
                  '--object-path', '/org/freedesktop/Notifications',
                  '--method', 'org.freedesktop.Notifications.CloseNotification', first)
        self.wait_for(lambda: f'Notification resolved: {first}' in self.log.read_text(),
                      'renderer did not close the resolved notification')
        image = str(ROOT / 'assets/icons/file.png')
        screenshot = self.call('notify-send', '--print-id', '--expire-time=0', '--app-name=Screenshot',
                               '--icon', image, 'Screenshot', 'Saved and copied').strip()
        self.wait_for(lambda: f'Notification popup displayed: {screenshot}' in self.log.read_text(),
                      'renderer did not display the screenshot notification')
        self.wait_for(lambda: f'proxy notified {screenshot} image={image}' in proxy_log.read_text(),
                      'screenshot image path was not delivered to the message center')

    def test_refuses_to_replace_a_non_astal_notification_server(self):
        self.stop(self.renderer)
        self.wait_for(lambda: not self.has_owner(), 'renderer did not release the notification service', False)
        log = (self.root / 'dunst.log').open('w')
        self.addCleanup(log.close)
        dunst = subprocess.Popen(['dunst', '-conf', '/dev/null'], env=self.env, stdout=log, stderr=subprocess.STDOUT)
        self.addCleanup(self.stop, dunst)
        self.wait_for(self.has_owner, 'Dunst did not start', False)
        result = subprocess.run([str(self.binary), '--listen'], env=self.env, capture_output=True, text=True, timeout=5)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Another notification server owns the service', result.stderr)
        self.assertIsNone(dunst.poll())

    def test_shell_proxy_takes_over_if_renderer_exits(self):
        proxy_script = self.root / 'fallback.js'
        proxy_script.write_text('''
import AstalNotifd from "gi://AstalNotifd";
import GLib from "gi://GLib";
const service = AstalNotifd.get_default();
service.connect("notified", (_s, id) => print(`fallback notified ${id}`));
new GLib.MainLoop(null, false).run();
''')
        proxy_log = self.root / 'fallback.log'
        with proxy_log.open('w') as stream:
            proxy = subprocess.Popen(['gjs', '-m', str(proxy_script)], env=self.env,
                                     stdout=stream, stderr=subprocess.STDOUT)
        self.addCleanup(self.stop, proxy)
        time.sleep(0.5)
        first = self.call('notify-send', '--print-id', '--expire-time=0', 'Before failure').strip()
        self.wait_for(lambda: f'fallback notified {first}' in proxy_log.read_text(), 'proxy was not ready')
        original_owner = self.owner()
        self.stop(self.renderer)
        self.wait_for(lambda: bool(self.owner()) and self.owner() != original_owner,
                      'shell proxy did not take ownership', False)
        self.assertFalse(self.has_owner('io.neuros.NotificationRenderer'))
        self.call('notify-send', '--print-id', '--expire-time=0', 'After failure')
        self.wait_for(lambda: proxy_log.read_text().count('fallback notified ') >= 2,
                      'shell proxy did not receive notifications after failover', False)

        # Reconnect the renderer as a proxy, then stop the shell owner. The
        # renderer must verify the new owner before announcing itself again.
        self.renderer = subprocess.Popen([str(self.binary), '--listen'], env=self.env,
                                         stdout=self.output, stderr=subprocess.STDOUT)
        self.addCleanup(self.stop, self.renderer)
        self.wait_for(lambda: self.has_owner('io.neuros.NotificationRenderer'), 'renderer did not reconnect')
        shell_owner = self.owner()
        self.stop(proxy)
        self.wait_for(lambda: bool(self.owner()) and self.owner() != shell_owner,
                      'renderer did not take over from the shell')
        self.wait_for(lambda: self.log.read_text().count('NeurOS notification renderer ready') >= 3,
                      'renderer did not revalidate after ownership changed')
        result = self.call('notify-send', '--print-id', '--expire-time=0', 'After shell exit').strip()
        self.wait_for(lambda: f'Notification popup displayed: {result}' in self.log.read_text(),
                      'renderer did not display notifications after takeover')

    def test_atomic_palette_update_is_observed(self):
        new = self.palette.with_name('new.palette')
        new.write_text('[palette]\naccent=#ff2a3a\nsecondary=#5ef4f8\n'
                       'foreground=#e7f1f6\nbackground=#07090d\n')
        new.replace(self.palette)
        self.wait_for(lambda: 'Notification palette updated' in self.log.read_text(),
                      'renderer did not reload the palette')

    def test_keyboard_read_invokes_the_notification_action(self):
        client = subprocess.Popen(['notify-send', '--action=default=Open', '--expire-time=0', 'Action test'],
                                  env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        self.addCleanup(self.stop, client)
        self.wait_for(lambda: 'Notification popup displayed:' in self.log.read_text(), 'popup did not appear')
        reply = self.call('gdbus', 'call', '--session', '--dest', 'io.neuros.NotificationRenderer',
                          '--object-path', '/io/neuros/NotificationRenderer',
                          '--method', 'io.neuros.NotificationRenderer.Read')
        self.assertIn('true', reply)
        out, err = client.communicate(timeout=5)
        self.assertEqual(client.returncode, 0, err)
        self.assertEqual(out.strip(), 'default')

    def test_keyboard_dismiss_resolves_the_notification(self):
        first = self.call('notify-send', '--print-id', '--expire-time=0', 'Dismiss test').strip()
        self.wait_for(lambda: f'Notification popup displayed: {first}' in self.log.read_text(), 'popup did not appear')
        reply = self.call('gdbus', 'call', '--session', '--dest', 'io.neuros.NotificationRenderer',
                          '--object-path', '/io/neuros/NotificationRenderer',
                          '--method', 'io.neuros.NotificationRenderer.Dismiss')
        self.assertIn('true', reply)
        self.wait_for(lambda: f'Notification resolved: {first}' in self.log.read_text(), 'notification was not dismissed')
        reply = self.call('gdbus', 'call', '--session', '--dest', 'io.neuros.NotificationRenderer',
                          '--object-path', '/io/neuros/NotificationRenderer',
                          '--method', 'io.neuros.NotificationRenderer.Dismiss')
        self.assertIn('false', reply)

    def test_standard_progress_hint_reaches_the_renderer(self):
        first = self.call('notify-send', '--print-id', '--expire-time=0', '--hint=int:value:42',
                          'Progress test').strip()
        self.wait_for(lambda: f'Notification popup displayed: {first} (progress 42)' in self.log.read_text(),
                      'renderer did not process the progress hint')

    def test_critical_notification_without_explicit_timeout_remains_visible(self):
        first = self.call('notify-send', '--print-id', '--urgency=critical', 'Critical test').strip()
        self.wait_for(lambda: f'Notification popup displayed: {first}' in self.log.read_text(), 'popup did not appear')
        time.sleep(8.5)
        reply = self.call('gdbus', 'call', '--session', '--dest', 'io.neuros.NotificationRenderer',
                          '--object-path', '/io/neuros/NotificationRenderer',
                          '--method', 'io.neuros.NotificationRenderer.Dismiss')
        self.assertIn('true', reply)


if __name__ == '__main__':
    unittest.main(verbosity=2)
