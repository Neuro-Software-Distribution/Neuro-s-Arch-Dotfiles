#!/usr/bin/env python3
"""Exercise the opt-in handoff with disposable services and process stubs."""
import os
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import textwrap
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Manager(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.scripts = self.root / 'scripts'; self.scripts.mkdir()
        shutil.copy2(ROOT / 'scripts/notifications', self.scripts / 'notifications')
        (self.scripts / 'runtime.sh').write_text('CYBER_RUNTIME="$TEST_RUNTIME"; export CYBER_RUNTIME\n')
        self.stub(self.scripts / 'restart', 'exit "${TEST_RESTART_EXIT:-0}"')
        self.runtime = self.root / 'runtime'; self.runtime.mkdir()
        self.build = self.runtime / 'build.test'; self.build.mkdir()
        (self.runtime / 'current').symlink_to(self.build)
        self.binary = self.build / 'notification-renderer'
        source = self.root / 'renderer.c'
        source.write_text('''#include <stdio.h>\n#include <stdlib.h>\n#include <unistd.h>\n#include <signal.h>\n'''
                          '''static const char *ready; static void stop(int sig) { (void)sig; unlink(ready); _exit(0); }\n'''
                          '''int main(void) {\n'''
                          '''if (getenv("TEST_FAIL_RENDERER")) return 1;\n'''
                          '''ready = getenv("TEST_READY"); signal(SIGTERM, stop);\n'''
                          '''FILE *f = fopen(ready, "w"); if (!f) return 1; fclose(f);\n'''
                          '''for (;;) pause();\n}\n''')
        subprocess.run(['cc', str(source), '-o', str(self.binary)], check=True)
        self.bin = self.root / 'bin'; self.bin.mkdir()
        self.owner = self.root / 'owner'; self.owner.write_text('dunst')
        self.ready = self.root / 'ready'
        self.log = self.root / 'calls'
        self.stub(self.bin / 'astal', 'readlink -f "$TEST_RUNTIME/current"')
        self.stub(self.bin / 'gdbus', '''
            case "$*" in
              *io.neuros.NotificationRenderer*) [ -e "$TEST_READY" ] && echo '(true,)' || echo '(false,)' ;;
              *) echo '(true,)' ;;
            esac
        ''')
        self.stub(self.bin / 'busctl', '''
            if [[ "$*" == *' status io.neuros.NotificationRenderer'* ]]; then
                printf 'PID='; cat "$TEST_RUNTIME/notification-renderer.pid"; exit 0
            fi
            if [[ "$*" == *' status '* ]]; then echo PID=123; exit 0; fi
            case "$(cat "$TEST_OWNER")" in
              dunst) echo 'ssss "dunst" "vendor" "1" "1.2"' ;;
              astal) echo 'ssss "notifd" "astal" "1" "1.2"' ;;
              *) echo 'ssss "other" "vendor" "1" "1.2"' ;;
            esac
        ''')
        self.stub(self.bin / 'systemctl', '''
            echo "$*" >> "$TEST_CALLS"
            case "$*" in
              *' is-active '*) exit 0 ;;
              *' show '*) echo 123 ;;
              *' stop '*) echo astal > "$TEST_OWNER" ;;
            esac
        ''')
        self.env = dict(os.environ, HOME=str(self.root), XDG_STATE_HOME=str(self.root / 'state'),
                        PATH=str(self.bin) + ':' + os.environ['PATH'], TEST_RUNTIME=str(self.runtime),
                        TEST_OWNER=str(self.owner), TEST_READY=str(self.ready), TEST_CALLS=str(self.log))

    def tearDown(self):
        pidfile = self.runtime / 'notification-renderer.pid'
        if pidfile.exists():
            try: os.kill(int(pidfile.read_text()), signal.SIGTERM)
            except ProcessLookupError: pass

    @staticmethod
    def stub(path, body):
        path.write_text('#!/bin/bash\nset -eu\n' + textwrap.dedent(body) + '\n')
        path.chmod(0o755)

    def run_manager(self, command, **env):
        return subprocess.run(['bash', str(self.scripts / 'notifications'), command],
                              env=dict(self.env, **env), capture_output=True, text=True, timeout=15)

    def test_enable_and_disable_preserve_a_shell_fallback(self):
        result = self.run_manager('enable')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.root / 'state/cyberarch/native-notifications-enabled').exists())
        self.assertEqual(self.owner.read_text().strip(), 'astal')
        self.assertIn('stop dunst.service', self.log.read_text())
        status = self.run_manager('status')
        self.assertIn('Native notifications: selected', status.stdout)
        self.assertIn('Renderer: ready', status.stdout)
        self.assertIn('Notification server: Astal', status.stdout)
        pid = int((self.runtime / 'notification-renderer.pid').read_text())
        self.assertEqual(self.run_manager('disable').returncode, 0)
        self.assertFalse((self.root / 'state/cyberarch/native-notifications-enabled').exists())
        self.assertTrue((self.root / 'state/cyberarch/native-notifications-disabled').exists())
        status = self.run_manager('status')
        self.assertIn('Native notifications: disabled by preference', status.stdout)
        self.assertIn('Renderer: not ready', status.stdout)
        self.assertFalse((self.runtime / 'notification-renderer.pid').exists())
        for _ in range(100):
            try:
                state = Path(f'/proc/{pid}/stat').read_text().split()[2]
                if state == 'Z': break
            except FileNotFoundError: break
            time.sleep(0.01)
        else: self.fail('renderer was not stopped')

    def test_unknown_server_is_not_stopped(self):
        self.owner.write_text('other')
        result = self.run_manager('enable')
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.log.exists())
        self.assertFalse((self.root / 'state/cyberarch/native-notifications-enabled').exists())

    def test_automatic_resume_respects_another_server_and_explicit_disable(self):
        state = self.root / 'state/cyberarch'; state.mkdir(parents=True)
        (state / 'native-notifications-enabled').touch()
        self.owner.write_text('other')
        result = self.run_manager('resume')
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((state / 'native-notifications-enabled').exists())
        self.assertFalse(self.log.exists())
        (state / 'native-notifications-disabled').touch()
        self.assertEqual(self.run_manager('resume').returncode, 0)
        self.assertFalse(self.log.exists())

    def test_failed_renderer_does_not_enable_native_mode(self):
        result = self.run_manager('enable', TEST_FAIL_RENDERER='1')
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(self.owner.read_text().strip(), 'astal')
        self.assertFalse((self.root / 'state/cyberarch/native-notifications-enabled').exists())
        self.assertFalse((self.runtime / 'notification-renderer.pid').exists())

    def test_resume_replaces_renderer_after_a_new_shell_build(self):
        self.assertEqual(self.run_manager('enable').returncode, 0)
        old_pid = int((self.runtime / 'notification-renderer.pid').read_text())
        newer = self.runtime / 'build.new'; newer.mkdir()
        shutil.copy2(self.binary, newer / 'notification-renderer')
        (self.runtime / 'current').unlink()
        (self.runtime / 'current').symlink_to(newer)
        result = self.run_manager('resume')
        self.assertEqual(result.returncode, 0, result.stderr)
        new_pid = int((self.runtime / 'notification-renderer.pid').read_text())
        self.assertNotEqual(new_pid, old_pid)
        self.assertEqual(Path(f'/proc/{new_pid}/exe').resolve(), newer / 'notification-renderer')

    def test_reenable_clears_explicit_disable(self):
        self.assertEqual(self.run_manager('enable').returncode, 0)
        self.assertEqual(self.run_manager('disable').returncode, 0)
        self.assertEqual(self.run_manager('enable').returncode, 0)
        self.assertFalse((self.root / 'state/cyberarch/native-notifications-disabled').exists())
        self.assertTrue((self.root / 'state/cyberarch/native-notifications-enabled').exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
