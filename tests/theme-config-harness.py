#!/usr/bin/env python3
"""Preference preservation tests against disposable files, including symlinks."""
import configparser
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('theme_config', ROOT / 'scripts/theme-config.py')
theme = importlib.util.module_from_spec(spec)
spec.loader.exec_module(theme)


class Preferences(unittest.TestCase):
    def test_gtk_preserves_accessibility_and_shared_symlink_target(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            shared = root / 'shared.ini'
            original = '[Settings]\ngtk-font-name=Sans 18\ngtk-enable-animations=false\n'
            shared.write_text(original)
            user = root / 'settings.ini'
            user.symlink_to(shared)
            theme.ini(user, 'Settings', ['gtk-theme-name=Adwaita-dark'])
            self.assertEqual(shared.read_text(), original)
            config = theme.configparser.ConfigParser()
            config.read(user)
            self.assertEqual(config['Settings']['gtk-font-name'], 'Sans 18')
            self.assertEqual(config['Settings']['gtk-enable-animations'], 'false')

    def test_shell_theme_writes_notification_palette(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fake = root / 'bin'; fake.mkdir()
            for name in ('hyprctl', 'gsettings', 'busctl'):
                command = fake / name
                command.write_text('#!/bin/sh\nexit 0\n')
                command.chmod(0o755)
            env = dict(os.environ, HOME=tmp, XDG_CONFIG_HOME=str(root / 'config'),
                       CYBER_DIR=str(ROOT), PATH=str(fake) + ':' + os.environ['PATH'])
            result = subprocess.run(['bash', str(ROOT / 'scripts/shell-theme'), 'BLADE'], env=env,
                                    capture_output=True, text=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
            palette = configparser.ConfigParser(interpolation=None)
            palette.read(root / 'config/cyberarch/notification.palette')
            self.assertEqual(palette['palette']['accent'], '#b75107')
            self.assertEqual(palette['palette']['secondary'], '#c37812')
            self.assertEqual(palette['palette']['background'], '#040302')


if __name__ == '__main__':
    unittest.main(verbosity=2)
