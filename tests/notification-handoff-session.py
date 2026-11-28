#!/usr/bin/env python3
"""Exercise Dunst-to-Astal-to-C handoff on a disposable D-Bus session."""
import os
from contextlib import ExitStack
from pathlib import Path
import shutil
import subprocess
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(os.environ.get('NEUROS_ISOLATED_NOTIFICATION_TEST') == '1', 'requires an isolated D-Bus session')
class Handoff(unittest.TestCase):
    def test_dunst_handoff_and_shell_fallback(self):
        with tempfile.TemporaryDirectory() as temp, ExitStack() as cleanup:
            root = Path(temp)
            scripts = root / 'scripts'; scripts.mkdir()
            shutil.copy2(ROOT / 'scripts/notifications', scripts / 'notifications')
            (scripts / 'runtime.sh').write_text('CYBER_RUNTIME="$TEST_RUNTIME"; export CYBER_RUNTIME\n')
            restart = scripts / 'restart'; restart.write_text('#!/bin/sh\nexit 0\n'); restart.chmod(0o755)
            runtime = root / 'runtime'; runtime.mkdir()
            build = runtime / 'build.test'; build.mkdir()
            (runtime / 'current').symlink_to(build)
            binary = build / 'notification-renderer'
            subprocess.run(['bash', str(ROOT / 'scripts/build-notification-preview'), str(binary)], check=True)
            fake = root / 'bin'; fake.mkdir()
            astal = fake / 'astal'; astal.write_text('#!/bin/sh\nreadlink -f "$TEST_RUNTIME/current"\n'); astal.chmod(0o755)
            systemctl = fake / 'systemctl'
            systemctl.write_text('''#!/bin/bash
case "$*" in
  *' is-active '*) kill -0 "$TEST_DUNST_PID" ;;
  *' show '*) echo "$TEST_DUNST_PID" ;;
  *' stop '*) kill "$TEST_DUNST_PID" ;;
  *) exit 1 ;;
esac
''')
            systemctl.chmod(0o755)
            env = dict(os.environ, HOME=str(root), XDG_CONFIG_HOME=str(root / 'config'),
                       XDG_CACHE_HOME=str(root / 'cache'), XDG_STATE_HOME=str(root / 'state'),
                       GSETTINGS_BACKEND='memory', TEST_RUNTIME=str(runtime),
                       PATH=str(fake) + ':' + os.environ['PATH'])
            processes = []
            def stop_all():
                pidfile = runtime / 'notification-renderer.pid'
                if pidfile.exists():
                    try: os.kill(int(pidfile.read_text()), 15)
                    except ProcessLookupError: pass
                for process in processes:
                    if process.poll() is None: process.terminate()
                for process in processes:
                    try: process.wait(timeout=3)
                    except subprocess.TimeoutExpired: process.kill(); process.wait(timeout=3)
            cleanup.callback(stop_all)
            def owner(name):
                result = subprocess.run(['gdbus', 'call', '--session', '--dest', 'org.freedesktop.DBus',
                                         '--object-path', '/org/freedesktop/DBus', '--method',
                                         'org.freedesktop.DBus.NameHasOwner', name],
                                        env=env, capture_output=True, text=True, timeout=3)
                return result.returncode == 0 and 'true' in result.stdout
            def wait(check, what):
                end = time.monotonic() + 8
                while time.monotonic() < end:
                    if check(): return
                    time.sleep(0.05)
                self.fail(what)
            dunst = subprocess.Popen(['dunst', '-conf', '/dev/null'], env=env,
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            processes.append(dunst); env['TEST_DUNST_PID'] = str(dunst.pid)
            wait(lambda: owner('org.freedesktop.Notifications'), 'Dunst did not acquire the name')
            proxy_source = root / 'proxy.js'
            proxy_source.write_text('''
import AstalNotifd from "gi://AstalNotifd";
import GLib from "gi://GLib";
const n = AstalNotifd.get_default();
n.connect("notified", (_s, id) => print(`notified ${id}`));
print("proxy ready");
new GLib.MainLoop(null, false).run();
''')
            proxy_log = root / 'proxy.log'
            with proxy_log.open('w') as stream:
                proxy = subprocess.Popen(['gjs', '-m', str(proxy_source)], env=env, stdout=stream, stderr=subprocess.STDOUT)
            processes.append(proxy)
            wait(lambda: proxy_log.exists() and 'proxy ready' in proxy_log.read_text(), 'shell proxy did not start')
            result = subprocess.run(['bash', str(scripts / 'notifications'), 'enable'], env=env,
                                    capture_output=True, text=True, timeout=25)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(owner('io.neuros.NotificationRenderer'))
            first = subprocess.run(['notify-send', '--print-id', '--expire-time=0', 'Handoff test'],
                                   env=env, check=True, capture_output=True, text=True).stdout.strip()
            renderer_log = root / 'state/cyberarch/notification-renderer.log'
            wait(lambda: f'Notification popup displayed: {first}' in renderer_log.read_text(),
                 'C renderer did not display the notification')
            wait(lambda: f'notified {first}' in proxy_log.read_text(), 'shell proxy did not see the notification')
            result = subprocess.run(['bash', str(scripts / 'notifications'), 'disable'], env=env,
                                    capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            wait(lambda: not owner('io.neuros.NotificationRenderer'), 'renderer did not release its name')
            second = subprocess.run(['notify-send', '--print-id', '--expire-time=0', 'Fallback test'],
                                    env=env, check=True, capture_output=True, text=True).stdout.strip()
            wait(lambda: f'notified {second}' in proxy_log.read_text(), 'shell fallback did not receive notifications')


if __name__ == '__main__':
    unittest.main(verbosity=2)
