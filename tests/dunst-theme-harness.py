#!/usr/bin/env python3
"""Exercise Dunst theme installation without changing the desktop session."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'scripts/dunst-theme'


class DunstTheme(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.config = self.root / 'config'
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        self.log = self.root / 'reload'
        self.stub('busctl', 'printf "Comm=%s\\n" "${TEST_OWNER:-other}"')
        self.stub('dunstctl', 'printf "%s\\n" "$*" >> "$TEST_RELOAD"')
        self.env = dict(os.environ, HOME=str(self.root), XDG_CONFIG_HOME=str(self.config),
                        PATH=str(self.bin) + ':' + os.environ['PATH'], TEST_RELOAD=str(self.log))

    def stub(self, name, body):
        path = self.bin / name
        path.write_text('#!/bin/sh\n' + body + '\n')
        path.chmod(0o755)

    def apply(self, *colors, **env):
        return subprocess.run(['bash', str(SCRIPT), *(colors or ('#c170ff', '#00eb74', '#e1e8fa', '#070912'))],
                              env=dict(self.env, **env), capture_output=True, text=True)

    def test_existing_base_preserved_and_palette_replaced(self):
        dunst = self.config / 'dunst'
        dunst.mkdir(parents=True)
        base = dunst / 'dunstrc'
        base.write_text('[global]\nmouse_left_click = do_action\n')
        self.assertEqual(self.apply().returncode, 0)
        self.assertEqual(base.read_text(), '[global]\nmouse_left_click = do_action\n')
        dropin = dunst / 'dunstrc.d/80-neuros.conf'
        self.assertIn('frame_color = "#c170ff"', dropin.read_text())
        self.assertIn('◢', dropin.read_text())
        self.assertIn('╱╱', dropin.read_text())
        self.assertEqual(self.apply('#ff2a3a', '#5ef4f8', '#e7f1f6', '#07090d').returncode, 0)
        self.assertIn('frame_color = "#ff2a3a"', dropin.read_text())
        self.assertFalse(self.log.exists(), 'another server must not trigger dunstctl')

    def test_reload_only_when_dunst_owns_notifications(self):
        self.assertEqual(self.apply(TEST_OWNER='dunst').returncode, 0)
        self.assertEqual(self.log.read_text(),
                         f'reload {self.config}/dunst/dunstrc {self.config}/dunst/dunstrc.d/80-neuros.conf\n')

    def test_unmanaged_dropin_is_preserved(self):
        dropin = self.config / 'dunst/dunstrc.d/80-neuros.conf'
        dropin.parent.mkdir(parents=True)
        dropin.write_text('personal settings\n')
        self.assertNotEqual(self.apply().returncode, 0)
        self.assertEqual(dropin.read_text(), 'personal settings\n')

    def test_invalid_palette_does_not_write_configuration(self):
        self.assertNotEqual(self.apply('bad', '#00eb74', '#e1e8fa', '#070912').returncode, 0)
        self.assertFalse(self.config.exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
