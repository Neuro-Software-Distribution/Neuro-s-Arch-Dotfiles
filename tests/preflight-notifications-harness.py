#!/usr/bin/env python3
"""Check native renderer build gating without invoking a desktop session."""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Preflight(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        scripts = self.root / 'scripts'; scripts.mkdir()
        shutil.copy2(ROOT / 'scripts/preflight', scripts / 'preflight')
        (scripts / 'build-notification-preview').write_text('#!/bin/bash\nexit 42\n')
        self.bin = self.root / 'bin'; self.bin.mkdir()
        self.stub('ags', 'printf shell > "$3"')
        self.stub('sassc', 'printf css > "$2"')
        for cmd in ('gjs', 'astal', 'hyprctl'): self.stub(cmd, 'exit 0')
        self.env = dict(os.environ, HOME=str(self.root), AGS_BIN=str(self.bin / 'ags'),
                        PATH=str(self.bin) + ':' + os.environ['PATH'])

    def stub(self, name, body):
        path = self.bin / name
        path.write_text('#!/bin/bash\nset -eu\n' + body + '\n')
        path.chmod(0o755)

    def run_preflight(self, require):
        return subprocess.run(['bash', str(self.root / 'scripts/preflight'), str(self.root / 'out')],
                              env=dict(self.env, NEUROS_REQUIRE_NOTIFICATION_RENDERER=str(require)),
                              capture_output=True, text=True, timeout=10)

    def test_shell_can_still_build_when_native_renderer_is_optional(self):
        result = self.run_preflight(0)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.root / 'out/shell.js').exists())
        self.assertIn('keeping the existing notification server', result.stderr)

    def test_required_renderer_failure_rejects_candidate(self):
        result = self.run_preflight(1)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Required native notification renderer did not build', result.stderr)
        self.assertFalse((self.root / 'out/notification-renderer').exists())


if __name__ == '__main__':
    unittest.main(verbosity=2)
