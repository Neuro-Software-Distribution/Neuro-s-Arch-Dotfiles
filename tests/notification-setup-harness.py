#!/usr/bin/env python3
"""Check installer defaults and preference preservation without a live session."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Setup(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.scripts = self.root / 'scripts'; self.scripts.mkdir()
        shutil.copy2(ROOT / 'scripts/install-notifications', self.scripts / 'install-notifications')
        build = self.scripts / 'build-notification-preview'
        build.write_text('''#!/bin/bash
echo build >> "$TEST_LOG"
[ "${TEST_FAIL:-0}" != 1 ] || exit 1
printf '#!/bin/sh\\nexit 0\\n' > "$1"
chmod +x "$1"
''')
        build.chmod(0o755)
        self.state = self.root / 'state/cyberarch'
        self.log = self.root / 'build.log'
        self.env = dict(os.environ, HOME=str(self.root), XDG_STATE_HOME=str(self.root / 'state'),
                        TEST_LOG=str(self.log))

    def setup_notifications(self, **kwargs):
        return subprocess.run(['bash', str(self.scripts / 'install-notifications')],
                              env=dict(self.env, **kwargs), capture_output=True, text=True, timeout=10)

    def test_first_install_selects_native_only_after_a_successful_build(self):
        self.assertNotEqual(self.setup_notifications(TEST_FAIL='1').returncode, 0)
        self.assertFalse((self.state / 'native-notifications-enabled').exists())
        self.assertEqual(self.setup_notifications().returncode, 0)
        self.assertTrue((self.state / 'native-notifications-enabled').exists())

    def test_explicitly_disabled_preference_is_preserved(self):
        self.state.mkdir(parents=True)
        (self.state / 'native-notifications-disabled').touch()
        self.assertEqual(self.setup_notifications().returncode, 0)
        self.assertFalse((self.state / 'native-notifications-enabled').exists())
        self.assertFalse(self.log.exists())

    def test_existing_selection_is_unchanged(self):
        self.state.mkdir(parents=True)
        (self.state / 'native-notifications-enabled').touch()
        self.assertNotEqual(self.setup_notifications(TEST_FAIL='1').returncode, 0)
        self.assertTrue((self.state / 'native-notifications-enabled').exists())
        self.assertEqual(self.setup_notifications().returncode, 0)
        self.assertEqual(self.log.read_text().splitlines(), ['build', 'build'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
