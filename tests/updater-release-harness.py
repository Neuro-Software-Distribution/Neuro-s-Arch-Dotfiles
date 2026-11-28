#!/usr/bin/env python3
"""Exercise release lookup without network access or modifying a real checkout."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ReleaseLookup(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'repo'
        self.repo.mkdir()
        self.home = self.root / 'home'
        self.home.mkdir()
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        shutil.copy2(ROOT / 'updater.sh', self.repo / 'updater.sh')
        (self.repo / 'VERSION').write_text('2.45\n')
        def git(*args):
            subprocess.run(['git', '-C', str(self.repo), *args], check=True, capture_output=True)
        git('init', '-q')
        git('config', 'user.name', 'Test')
        git('config', 'user.email', 'test@example.invalid')
        git('remote', 'add', 'origin', 'https://github.com/example/project.git')
        git('add', 'updater.sh', 'VERSION')
        git('commit', '-qm', 'test')
        curl = self.bin / 'curl'
        curl.write_text('''#!/usr/bin/env bash
while [ "$#" -gt 0 ]; do
    if [ "$1" = -o ]; then shift; output="$1"; fi
    shift
done
printf '%s' "$TEST_BODY" > "$output"
printf '%s' "$TEST_HTTP"
exit "${TEST_CURL_EXIT:-0}"
''')
        curl.chmod(0o755)

    def run_update(self, status, body, *args, curl_exit='0'):
        env = dict(os.environ, HOME=str(self.home), XDG_CONFIG_HOME=str(self.home / '.config'),
                   PATH=str(self.bin) + ':' + os.environ['PATH'], TEST_HTTP=status,
                   TEST_BODY=body, TEST_CURL_EXIT=curl_exit)
        return subprocess.run(['bash', str(self.repo / 'updater.sh'), *args], env=env,
                              capture_output=True, text=True, timeout=10)

    def test_missing_release_explains_publishing(self):
        result = self.run_update('404', '{"message":"Not Found"}')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('No published stable release found', result.stderr)
        self.assertIn('release assets are not required', result.stderr)

    def test_http_and_network_errors_are_distinct(self):
        self.assertIn('HTTP 403', self.run_update('403', '{}').stderr)
        self.assertIn('curl exit 6', self.run_update('000', '', curl_exit='6').stderr)

    def test_invalid_response_is_rejected(self):
        self.assertIn('invalid release response', self.run_update('200', '{}').stderr)

    def test_published_release_needs_no_asset(self):
        result = self.run_update('200', '{"tag_name":"v2.45","body":"Notes"}')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Already up to date', result.stdout)

    def test_greek_alphabet_maps_to_numeric_major_versions(self):
        names = 'alpha beta gamma delta epsilon zeta eta theta iota kappa lambda mu nu xi omicron pi rho sigma tau upsilon phi chi psi omega'.split()
        letters = 'α β γ δ ε ζ η θ ι κ λ μ ν ξ ο π ρ σ τ υ φ χ ψ ω'.split()
        for number, (name, letter) in enumerate(zip(names, letters), 1):
            for spelling in (name, letter):
                with self.subTest(version=spelling):
                    (self.repo / 'VERSION').write_text(f'{number}.3\n')
                    body = json.dumps({'tag_name': f'{spelling}.3'})
                    self.assertEqual(self.run_update('200', body, 'check').stdout.splitlines()[0], '0')
                    body = json.dumps({'tag_name': f'{spelling}.4'})
                    self.assertEqual(self.run_update('200', body, 'check').stdout.splitlines()[0], '1')

    def test_beta_migrates_from_numeric_and_accepts_unicode_tag(self):
        newer = json.dumps({'tag_name': 'β.46', 'body': 'Greek release'})
        result = self.run_update('200', newer, 'check')
        self.assertEqual(result.stdout.splitlines()[:3], ['1', '2.45', 'β.46'])
        same = json.dumps({'tag_name': 'β.45'})
        result = self.run_update('200', same)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('Already up to date', result.stdout)

    def test_invalid_version_is_rejected(self):
        for tag in ('banana.9', 'β.-1', '2.1.2.3.4'):
            with self.subTest(tag=tag):
                result = self.run_update('200', json.dumps({'tag_name': tag}))
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Invalid release version', result.stdout)

    def test_background_check_preserves_machine_readable_output(self):
        result = self.run_update('404', '{}', 'check')
        self.assertEqual(result.stdout, '0\n2.45\n2.45\n')
        self.assertEqual(result.stderr, '')


if __name__ == '__main__':
    unittest.main(verbosity=2)
