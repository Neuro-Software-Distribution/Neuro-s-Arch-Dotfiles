#!/usr/bin/env python3
"""Exercise wallpaper replacement without touching a user's renderer."""
import os
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import textwrap
import unittest


ROOT = Path(__file__).resolve().parents[1]


class WallpaperHandoff(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.work = Path(self.tmp.name)
        self.home = self.work / 'home'
        self.home.mkdir()
        self.runtime = self.work / 'runtime'
        self.runtime.mkdir(mode=0o700)
        self.scripts = self.work / 'scripts'
        self.scripts.mkdir()
        for name in ('runtime.sh', 'set-wallpaper'):
            shutil.copy2(ROOT / 'scripts' / name, self.scripts / name)
        self.video = self.work / 'candidate.mp4'
        self.video.write_bytes(b'not-a-real-video')
        self.bin = self.work / 'bin'
        self.bin.mkdir()
        self.old_mpv = subprocess.Popen(['/bin/sleep', '60'])
        self.old_awww = subprocess.Popen(['/bin/sleep', '60'])
        self.addCleanup(self.stop, self.old_mpv)
        self.addCleanup(self.stop, self.old_awww)
        self.stub('wlr-randr', 'exit 0')
        self.stub('hyprctl', "printf '%s\\n' '[]'")
        self.stub('pgrep', '''
            case "$*" in
                *'mpvpaper'*) printf '%s\\n' "$OLD_MPV_PID" ;;
                *'awww-daemon'*) printf '%s\\n' "$OLD_AWWW_PID" ;;
            esac
        ''')
        self.stub('socat', '''
            if [ "${TEST_READY:-0}" = 1 ]; then
                printf '%s\\n' '{"error":"success","data":{"w":1}}'
            else
                printf '%s\\n' '{"error":"property unavailable"}'
            fi
        ''')
        self.stub('mpvpaper', '''
            socket=""
            for arg in "$@"; do
                case "$arg" in *--input-ipc-server=*) socket="${arg##*--input-ipc-server=}" ;; esac
            done
            [ -n "$socket" ] || exit 2
            if [ "${TEST_READY:-0}" = 1 ]; then delay=1; else delay=0.1; fi
            exec python3 -c 'import socket, sys, time; s = socket.socket(socket.AF_UNIX); s.bind(sys.argv[1]); s.listen(); time.sleep(float(sys.argv[2]))' "$socket" "$delay" >/dev/null 2>&1
        ''')

    def stub(self, name, body):
        path = self.bin / name
        path.write_text('#!/usr/bin/env bash\nset -eu\n' + textwrap.dedent(body))
        path.chmod(0o755)

    @staticmethod
    def stop(process):
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=2)

    def run_wallpaper(self, ready):
        display = self.runtime / 'wayland-1'
        with socket.socket(socket.AF_UNIX) as listener:
            listener.bind(str(display))
            env = dict(os.environ, HOME=str(self.home), XDG_RUNTIME_DIR=str(self.runtime),
                       HYPRLAND_INSTANCE_SIGNATURE='test',
                       WAYLAND_DISPLAY='wayland-1', PATH=str(self.bin) + ':' + os.environ['PATH'],
                       CYBER_SDDM_CURRENT_DIR=str(self.work / 'not-installed'),
                       OLD_MPV_PID=str(self.old_mpv.pid), OLD_AWWW_PID=str(self.old_awww.pid),
                       TEST_READY='1' if ready else '0')
            return subprocess.run(['bash', str(self.scripts / 'set-wallpaper'), str(self.video)],
                                  env=env, capture_output=True, text=True, timeout=20)

    def test_unready_replacement_keeps_existing_renderers(self):
        result = self.run_wallpaper(False)
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIsNone(self.old_mpv.poll())
        self.assertIsNone(self.old_awww.poll())

    def test_ready_replacement_retires_existing_renderers(self):
        result = self.run_wallpaper(True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.old_mpv.wait(timeout=1)
        self.old_awww.wait(timeout=1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
