#!/usr/bin/env python3
"""Build and verify the independent renderer without a graphical session."""
import os
from pathlib import Path
import shutil
import struct
import subprocess
import tempfile
import unittest
import zlib

ROOT = Path(__file__).resolve().parents[1]


def pixels(path):
    data = path.read_bytes()
    assert data[:8] == b'\x89PNG\r\n\x1a\n'
    pos, chunks = 8, bytearray()
    while pos < len(data):
        size = struct.unpack_from('>I', data, pos)[0]
        kind, payload = data[pos + 4:pos + 8], data[pos + 8:pos + 8 + size]
        if kind == b'IHDR':
            width, height, depth, color, _, _, interlace = struct.unpack('>IIBBBBB', payload)
            assert (depth, color, interlace) == (8, 6, 0)
        if kind == b'IDAT': chunks.extend(payload)
        pos += size + 12
    raw, stride, rows = zlib.decompress(chunks), width * 4, []
    offset, previous = 0, bytearray(stride)
    for _ in range(height):
        mode = raw[offset]; offset += 1
        row = bytearray(raw[offset:offset + stride]); offset += stride
        for i in range(stride):
            left = row[i - 4] if i >= 4 else 0
            up = previous[i]
            upper_left = previous[i - 4] if i >= 4 else 0
            if mode == 1: value = left
            elif mode == 2: value = up
            elif mode == 3: value = (left + up) // 2
            elif mode == 4:
                p = left + up - upper_left
                value = min((left, up, upper_left), key=lambda c: abs(p - c))
            else: value = 0
            row[i] = (row[i] + value) & 255
        rows.append(row); previous = row
    return width, height, rows


@unittest.skipUnless(shutil.which('cc') and shutil.which('pkg-config') and
                     subprocess.run(['pkg-config', '--exists', 'gtk+-3.0', 'gtk-layer-shell-0', 'astal-notifd-0.1']).returncode == 0,
                     'GTK 3, gtk-layer-shell and AstalNotifd development files are required')
class Preview(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        cls.binary = cls.root / 'preview'
        subprocess.run(['bash', str(ROOT / 'scripts/build-notification-preview'), str(cls.binary)], check=True)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def render(self, *args):
        target = self.root / 'card.png'
        result = subprocess.run([str(self.binary), '--render', str(target), *args],
                                env=dict(os.environ, DISPLAY='', WAYLAND_DISPLAY=''),
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return pixels(target)

    def test_actual_corners_are_transparent_and_center_is_opaque(self):
        width, height, rows = self.render()
        self.assertEqual(width, 420)
        self.assertGreaterEqual(height, 104)
        self.assertEqual(rows[0][(width - 1) * 4 + 3], 0)
        self.assertEqual(rows[-1][3], 0)
        self.assertGreater(rows[height // 2][width // 2 * 4 + 3], 200)

    def test_long_text_is_bounded_and_bad_image_falls_back(self):
        width, height, _ = self.render('--title', 'Long title ' * 200, '--body', 'Long body ' * 500,
                                       '--image', str(self.root / 'missing.png'))
        self.assertEqual(width, 420)
        self.assertLess(height, 300)

    def test_invalid_colors_are_rejected(self):
        result = subprocess.run([str(self.binary), '--render', str(self.root / 'bad.png'), '--accent', 'not-a-color'],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Invalid palette color', result.stderr)

    def test_palette_file_changes_the_rendered_background(self):
        palette = self.root / 'colors.ini'
        palette.write_text('[palette]\naccent=#ff2040\nsecondary=#40ff80\n'
                           'foreground=#ffffff\nbackground=#204060\n')
        width, height, rows = self.render('--palette-file', str(palette))
        pixel = rows[height // 2][(width - 12) * 4:(width - 12) * 4 + 4]
        self.assertTrue(all(abs(a - b) <= 2 for a, b in zip(pixel[:3], (32, 64, 96))), list(pixel))
        palette.write_text('[palette]\naccent=invalid\n')
        result = subprocess.run([str(self.binary), '--render', str(self.root / 'bad.png'),
                                 '--palette-file', str(palette)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)

    def test_progress_adds_a_partially_filled_indicator(self):
        _, base_height, _ = self.render()
        width, height, rows = self.render('--progress', '40')
        self.assertGreater(height, base_height)
        row = rows[height - 14]
        filled = row[30 * 4:30 * 4 + 3]
        empty = row[(width - 30) * 4:(width - 30) * 4 + 3]
        self.assertGreater(filled[1], filled[0])
        self.assertNotEqual(filled, empty)
        result = subprocess.run([str(self.binary), '--render', str(self.root / 'bad.png'), '--progress', '101'],
                                capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
