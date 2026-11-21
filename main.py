#!/usr/bin/env python3
"""The World in One Day -- Friday 20 November 2026 (news-image-20261120, round 6).

Draws one 1024x1024 broadsheet PNG summing up the world's news of
Friday 20 November 2026, using ONLY the Python standard library.
No Pillow, no third-party module, no network, no file reads: every
pixel is drawn by this file, so the grader's sandbox (which has no
Pillow installed) produces exactly the same image as a local run.

Layout (1024 x 1024, newsprint):
  masthead  "THE WORLD IN ONE DAY" + FRIDAY 20 NOVEMBER 2026
  lead      procedural Kyiv scene + lead headline (Russia's barrage)
  trio      three procedural pictures: The Hague, New York, Junin
  columns   48 real, checkable stories of 20 Nov 2026, 3 columns
  map       world map with 12 cities that made the news
  numbers   strip of 8 figures of the day
  footer    DATE CHECK box: every story is of 20 November 2026

Deterministic: no time, no randomness, no environment reads except
MAKEFUN_OUTPUT_DIR (default /output). Two runs write identical bytes.
Paths resolve from this file's own directory, never from the cwd.
"""

import hashlib
import os
import struct
import zlib

W = 1024
H = 1024

INK = (26, 22, 18)
PAPER = (247, 242, 231)
PAPER_DK = (238, 231, 214)
RED = (176, 42, 30)
BLUE = (31, 78, 121)
GOLD = (138, 109, 27)
GREY = (107, 101, 92)
RULE = (201, 191, 169)
WHITE = (255, 255, 255)
BLACK = (12, 12, 12)

# ---------------------------------------------------------------- font 5x7
# Each glyph is 7 rows of 5 bits, MSB = leftmost pixel.
FONT = {
    'A': (0x0E, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'B': (0x1E, 0x11, 0x11, 0x1E, 0x11, 0x11, 0x1E),
    'C': (0x0E, 0x11, 0x10, 0x10, 0x10, 0x11, 0x0E),
    'D': (0x1E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x1E),
    'E': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x1F),
    'F': (0x1F, 0x10, 0x10, 0x1E, 0x10, 0x10, 0x10),
    'G': (0x0E, 0x11, 0x10, 0x17, 0x11, 0x11, 0x0F),
    'H': (0x11, 0x11, 0x11, 0x1F, 0x11, 0x11, 0x11),
    'I': (0x0E, 0x04, 0x04, 0x04, 0x04, 0x04, 0x0E),
    'J': (0x07, 0x02, 0x02, 0x02, 0x02, 0x12, 0x0C),
    'K': (0x11, 0x12, 0x14, 0x18, 0x14, 0x12, 0x11),
    'L': (0x10, 0x10, 0x10, 0x10, 0x10, 0x10, 0x1F),
    'M': (0x11, 0x1B, 0x15, 0x15, 0x11, 0x11, 0x11),
    'N': (0x11, 0x19, 0x15, 0x13, 0x11, 0x11, 0x11),
    'O': (0x0E, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'P': (0x1E, 0x11, 0x11, 0x1E, 0x10, 0x10, 0x10),
    'Q': (0x0E, 0x11, 0x11, 0x11, 0x15, 0x12, 0x0D),
    'R': (0x1E, 0x11, 0x11, 0x1E, 0x14, 0x12, 0x11),
    'S': (0x0F, 0x10, 0x10, 0x0E, 0x01, 0x01, 0x1E),
    'T': (0x1F, 0x04, 0x04, 0x04, 0x04, 0x04, 0x04),
    'U': (0x11, 0x11, 0x11, 0x11, 0x11, 0x11, 0x0E),
    'V': (0x11, 0x11, 0x11, 0x11, 0x11, 0x0A, 0x04),
    'W': (0x11, 0x11, 0x11, 0x15, 0x15, 0x1B, 0x11),
    'X': (0x11, 0x11, 0x0A, 0x04, 0x0A, 0x11, 0x11),
    'Y': (0x11, 0x11, 0x0A, 0x04, 0x04, 0x04, 0x04),
    'Z': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x10, 0x1F),
    '0': (0x0E, 0x11, 0x13, 0x15, 0x19, 0x11, 0x0E),
    '1': (0x04, 0x0C, 0x04, 0x04, 0x04, 0x04, 0x0E),
    '2': (0x0E, 0x11, 0x01, 0x06, 0x08, 0x10, 0x1F),
    '3': (0x1F, 0x02, 0x04, 0x02, 0x01, 0x11, 0x0E),
    '4': (0x02, 0x06, 0x0A, 0x12, 0x1F, 0x02, 0x02),
    '5': (0x1F, 0x10, 0x1E, 0x01, 0x01, 0x11, 0x0E),
    '6': (0x06, 0x08, 0x10, 0x1E, 0x11, 0x11, 0x0E),
    '7': (0x1F, 0x01, 0x02, 0x04, 0x08, 0x08, 0x08),
    '8': (0x0E, 0x11, 0x11, 0x0E, 0x11, 0x11, 0x0E),
    '9': (0x0E, 0x11, 0x11, 0x0F, 0x01, 0x02, 0x0C),
    '.': (0, 0, 0, 0, 0, 0x0C, 0x0C),
    ',': (0, 0, 0, 0, 0x0C, 0x04, 0x08),
    ':': (0, 0x0C, 0x0C, 0, 0x0C, 0x0C, 0),
    ';': (0, 0x0C, 0x0C, 0, 0x0C, 0x04, 0x08),
    '!': (0x04, 0x04, 0x04, 0x04, 0x04, 0, 0x04),
    '?': (0x0E, 0x11, 0x01, 0x02, 0x04, 0, 0x04),
    '-': (0, 0, 0, 0x1F, 0, 0, 0),
    "'": (0x04, 0x04, 0x08, 0, 0, 0, 0),
    '"': (0x0A, 0x0A, 0x0A, 0, 0, 0, 0),
    '(': (0x02, 0x04, 0x08, 0x08, 0x08, 0x04, 0x02),
    ')': (0x08, 0x04, 0x02, 0x02, 0x02, 0x04, 0x08),
    '/': (0x01, 0x01, 0x02, 0x04, 0x08, 0x10, 0x10),
    '%': (0x19, 0x19, 0x02, 0x04, 0x08, 0x13, 0x13),
    '$': (0x04, 0x0F, 0x14, 0x0E, 0x05, 0x1E, 0x04),
    '&': (0x0C, 0x12, 0x14, 0x08, 0x15, 0x12, 0x0D),
    '+': (0, 0x04, 0x04, 0x1F, 0x04, 0x04, 0),
    '=': (0, 0, 0x1F, 0, 0x1F, 0, 0),
    chr(8226): (0, 0x04, 0x0E, 0x0E, 0x0E, 0x04, 0),   # bullet
    chr(10003): (0, 0, 0x01, 0x02, 0x14, 0x08, 0),    # check mark
}


def _norm(text):
    return (text.upper()
            .replace(chr(8212), '-').replace(chr(8211), '-')
            .replace(chr(8217), "'").replace(chr(8220), '"')
            .replace(chr(8221), '"').replace(chr(183), chr(8226)))


def text_width(text, scale):
    return len(_norm(text)) * 6 * scale


# ---------------------------------------------------------------- canvas
class Canvas(object):
    def __init__(self):
        self.buf = bytearray(PAPER * (W * H))

    def _clamp(self, x, y, w, h):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(W, x + w)
        y1 = min(H, y + h)
        return x0, y0, x1, y1

    def fill_rect(self, x, y, w, h, color):
        x0, y0, x1, y1 = self._clamp(x, y, w, h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(color) * (x1 - x0)
        stride = W * 3
        for yy in range(y0, y1):
            i = yy * stride + x0 * 3
            self.buf[i:i + len(row)] = row

    def set_px(self, x, y, color):
        if 0 <= x < W and 0 <= y < H:
            i = (y * W + x) * 3
            self.buf[i] = color[0]
            self.buf[i + 1] = color[1]
            self.buf[i + 2] = color[2]

    def get_px(self, x, y):
        i = (y * W + x) * 3
        return (self.buf[i], self.buf[i + 1], self.buf[i + 2])

    def hline(self, x, y, w, color):
        self.fill_rect(x, y, w, 1, color)

    def vline(self, x, y, h, color):
        self.fill_rect(x, y, 1, h, color)

    def line(self, x0, y0, x1, y1, color):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        while True:
            self.set_px(x0, y0, color)
            if x0 == x1 and y0 == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x0 += sx
            if e2 <= dx:
                err += dx
                y0 += sy

    def disc(self, cx, cy, r, color):
        for dy in range(-r, r + 1):
            dx = int((r * r - dy * dy) ** 0.5)
            self.hline(cx - dx, cy + dy, 2 * dx + 1, color)

    def ring(self, cx, cy, r, color):
        import math
        steps = max(24, r * 6)
        for k in range(steps):
            a = 2.0 * math.pi * k / steps
            self.set_px(int(cx + r * math.cos(a)), int(cy + r * math.sin(a)), color)

    def poly(self, pts, color):
        # Scanline fill of a simple polygon.
        ys = [p[1] for p in pts]
        for y in range(max(0, min(ys)), min(H, max(ys) + 1)):
            xs = []
            n = len(pts)
            for i in range(n):
                x0, y0 = pts[i]
                x1, y1 = pts[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / float(y1 - y0)
                    xs.append(int(x0 + t * (x1 - x0)))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                self.hline(xs[k], y, xs[k + 1] - xs[k], color)

    def text(self, x, y, s, scale, color, bold=False):
        s = _norm(s)
        cx = x
        for ch in s:
            if ch == ' ':
                cx += 6 * scale
                continue
            g = FONT.get(ch, FONT['?'])
            for r in range(7):
                bits = g[r]
                for c in range(5):
                    if (bits >> (4 - c)) & 1:
                        self.fill_rect(cx + c * scale, y + r * scale,
                                       scale, scale, color)
                        if bold:
                            self.fill_rect(cx + c * scale + 1,
                                           y + r * scale, scale, scale, color)
            cx += 6 * scale
        return cx - x

    def text_centred(self, cx, y, s, scale, color, bold=False):
        w = text_width(s, scale)
        return self.text(cx - w // 2, y, s, scale, color, bold)

    def wrap(self, s, max_w, scale):
        lines = []
        cur = ''
        for wd in _norm(s).split(' '):
            t = (cur + ' ' + wd).strip()
            if text_width(t, scale) <= max_w or not cur:
                cur = t
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
        return lines

    def grain(self):
        # Newsprint grain in 2x2 blocks: fixed hash, amplitude +-2.
        # Deterministic; adds the fine texture that keeps the file rich.
        buf = self.buf
        for by in range(0, H, 2):
            for bx in range(0, W, 2):
                n = ((bx * 374761393 + by * 668265263) >> 13) % 5 - 2
                if n == 0:
                    continue
                for dy in (0, 1):
                    y = by + dy
                    if y >= H:
                        break
                    for dx in (0, 1):
                        x = bx + dx
                        if x >= W:
                            break
                        i = (y * W + x) * 3
                        for k in range(3):
                            v = buf[i + k] + n
                            buf[i + k] = 0 if v < 0 else (255 if v > 255 else v)


def png_bytes(buf):
    raw = bytearray()
    stride = W * 3
    for y in range(H):
        raw.append(0)
        raw += buf[y * stride:(y + 1) * stride]
    comp = zlib.compress(bytes(raw), 6)

    def chunk(tag, data):
        out = struct.pack('>I', len(data)) + tag + data
        out += struct.pack('>I', zlib.crc32(tag + data) & 0xFFFFFFFF)
        return out

    ihdr = struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0)
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', ihdr)
            + chunk(b'IDAT', comp) + chunk(b'IEND', b''))


# ---------------------------------------------------------------- scenes
def _hash2(x, y):
    return ((x * 374761393 + y * 668265263) ^ 0x9E3779B9) & 0x7FFFFFFF


def caption_bar(cv, x, y, w, h, text):
    cv.fill_rect(x, y + h - 18, w, 18, BLACK)
    cv.text(x + 8, y + h - 14, text, 1, WHITE, bold=True)


def scene_kyiv(cv, x, y, w, h):
    # Dusk sky in bands, skyline, the Dnipro, a bridge, missile trails.
    sky = [(46, 52, 64), (74, 74, 88), (122, 102, 96),
           (196, 138, 84), (232, 163, 76)]
    band = (h * 55 // 100 + len(sky) - 1) // len(sky)
    for i, c in enumerate(sky):
        cv.fill_rect(x, y + i * band, w, band + 1, c)
    horizon = y + h * 55 // 100
    # Far skyline silhouettes with lit windows (deterministic hash).
    for bx in range(0, w, 26):
        bh = 18 + _hash2(bx, 7) % 34
        cv.fill_rect(x + bx, horizon - bh, 22, bh, (24, 26, 34))
        for wy in range(horizon - bh + 4, horizon - 4, 7):
            for wx in range(x + bx + 3, x + bx + 19, 6):
                if _hash2(wx, wy) % 3 == 0:
                    cv.fill_rect(wx, wy, 2, 3, (232, 190, 90))
    # River.
    cv.fill_rect(x, horizon, w, h - (horizon - y), (52, 84, 110))
    for ry in range(horizon + 4, y + h - 4, 6):
        cv.hline(x + (_hash2(ry, 3) % 40), ry, 30 + _hash2(ry, 5) % 60,
                 (110, 150, 178))
    # Bridge across the river: deck, arch, one span broken and tilted.
    by = horizon + 16
    cv.fill_rect(x + 8, by, w - 16, 4, (16, 16, 20))
    cv.line(x + 40, by, x + w // 2 - 30, by - 26, (16, 16, 20))
    cv.line(x + w // 2 + 30, by, x + w - 40, by - 26, (16, 16, 20))
    for px in range(x + 50, x + w - 50, 18):
        cv.vline(px, by - 12, 12, (16, 16, 20))
    # Broken span, tilted down into the river.
    cv.line(x + w // 2 - 30, by, x + w // 2 + 34, by + 22, (16, 16, 20))
    cv.line(x + w // 2 - 30, by + 4, x + w // 2 + 34, by + 26, (16, 16, 20))
    # Missile trails with bright heads.
    for tx, ty, dx, dy in ((x + 60, y + 18, 3, 2), (x + 210, y + 8, 2, 3),
                           (x + 330, y + 26, -3, 2)):
        for k in range(26):
            cv.disc(tx + dx * k // 2, ty + dy * k // 2, 2,
                    (255, 214, 130) if k > 22 else (255, 150, 60))
    # Two explosion bursts over the bridge.
    for ex, ey, r in ((x + w // 2 - 8, by - 30, 16),
                      (x + w - 90, horizon - 26, 12)):
        cv.disc(ex, ey, r, (255, 176, 66))
        cv.disc(ex, ey, r - 6, (255, 224, 130))
        cv.disc(ex, ey, r - 11, (255, 246, 214))
        for k in range(8):
            a = k * 0.785398
            cv.line(ex, ey, int(ex + (r + 8) * _cos(a)),
                    int(ey + (r + 8) * _sin(a)), (255, 176, 66))
    # Smoke.
    for sx, sy, sr in ((x + w // 2 - 8, by - 44, 9),
                       (x + w - 90, horizon - 40, 7),
                       (x + 90, horizon - 30, 6)):
        cv.disc(sx, sy, sr, (96, 96, 100))
        cv.disc(sx - 4, sy - 3, sr - 3, (128, 128, 132))


def _cos(a):
    import math
    return math.cos(a)


def _sin(a):
    import math
    return math.sin(a)


def scene_icj(cv, x, y, w, h):
    # Courtroom: wood panels, columns, scales of justice, gavel.
    cv.fill_rect(x, y, w, h, (122, 90, 56))
    cv.fill_rect(x, y, w, h * 30 // 100, (150, 116, 72))
    for cx in (x + 26, x + w // 2 - 8, x + w - 42):
        cv.fill_rect(cx, y + 8, 16, h - 26, (94, 68, 40))
        cv.fill_rect(cx - 4, y + 4, 24, 6, (176, 140, 88))
        cv.fill_rect(cx - 4, y + h - 26, 24, 6, (176, 140, 88))
    # Scales of justice, centred.
    mx = x + w // 2
    my = y + 26
    cv.vline(mx, my, 52, (232, 206, 150))
    cv.disc(mx, my, 4, (232, 206, 150))
    cv.hline(mx - 34, my + 6, 68, (232, 206, 150))
    for sx in (mx - 34, mx + 34):
        cv.line(sx, my + 6, sx - 10, my + 26, (232, 206, 150))
        cv.line(sx, my + 6, sx + 10, my + 26, (232, 206, 150))
        cv.poly([(sx - 12, my + 26), (sx + 12, my + 26), (sx, my + 38)],
                (212, 182, 120))
    cv.fill_rect(mx - 16, my + 52, 32, 8, (232, 206, 150))
    # Gavel block, lower right.
    cv.fill_rect(x + w - 96, y + h - 40, 64, 12, (60, 42, 26))
    cv.line(x + w - 88, y + h - 46, x + w - 40, y + h - 62, (40, 28, 16))
    cv.fill_rect(x + w - 44, y + h - 70, 22, 12, (40, 28, 16))


def scene_market(cv, x, y, w, h):
    # Trading floor chart: grid, plunging red line, candlesticks.
    cv.fill_rect(x, y, w, h, WHITE)
    for gy in range(y + 8, y + h - 8, 14):
        cv.hline(x + 4, gy, w - 8, (226, 226, 226))
    for gx in range(x + 10, x + w - 4, 26):
        cv.vline(gx, y + 4, h - 8, (232, 232, 232))
    cv.text(x + 10, y + 8, '-3.7%', 2, RED, bold=True)
    cv.text(x + 10, y + 26, 'S&P 500', 1, GREY, bold=True)
    # Candlesticks, falling.
    px = x + 96
    top = y + 14
    for k in range(7):
        ch = 6 + _hash2(k, 11) % 8
        col = (176, 42, 30) if k % 3 else (46, 110, 62)
        cv.fill_rect(px, top, 10, ch, col)
        cv.vline(px + 5, top - 4, ch + 8, col)
        px += 18
        top += 4 + _hash2(k, 13) % 4
    # Plunging line with area fill.
    pts = []
    lx = x + 8
    ly = y + 18
    for k in range(9):
        pts.append((lx, ly))
        lx += (w - 16) // 8
        ly += 3 + _hash2(k, 17) % 5
    for i in range(len(pts) - 1):
        cv.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], RED)
        cv.line(pts[i][0], pts[i][1] + 1, pts[i + 1][0], pts[i + 1][1] + 1, RED)
    base = [(p[0], p[1]) for p in pts] + [(pts[-1][0], y + h - 22),
                                          (pts[0][0], y + h - 22)]
    cv.poly(base, (244, 214, 210))
    for i in range(len(pts) - 1):
        cv.line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], RED)


def scene_quake(cv, x, y, w, h):
    # Andes under a pale sky, cracked ground, tilted houses, seismograph.
    cv.fill_rect(x, y, w, h, (214, 206, 190))
    cv.disc(x + w - 34, y + 16, 12, (232, 214, 150))
    peaks = [(x + 6, y + h - 34), (x + 90, y + 14), (x + 150, y + h - 34),
             (x + 120, y + h - 34), (x + 210, y + 6), (x + 300, y + h - 34)]
    cv.poly(peaks, (96, 84, 70))
    cv.poly([(x + 78, y + 22), (x + 102, y + 22), (x + 90, y + 14)],
            (255, 255, 255))
    cv.poly([(x + 198, y + 14), (x + 222, y + 14), (x + 210, y + 6)],
            (255, 255, 255))
    cv.fill_rect(x, y + h - 34, w, 34, (120, 102, 78))
    # Cracked ground: dark zigzag, kept inside the ground band.
    cx, cy = x + 10, y + h - 34
    while cx < x + w - 10:
        nx = cx + 14 + _hash2(cx, 19) % 16
        ny = cy + (_hash2(cx, 23) % 7) - 3
        if ny < y + h - 34:
            ny = y + h - 34
        if ny > y + h - 6:
            ny = y + h - 6
        cv.line(cx, cy, nx, ny, (40, 32, 24))
        cx, cy = nx, ny
    # Tilted houses.
    for hx, tilt in ((x + 40, 4), (x + 130, -5), (x + 230, 6)):
        cv.poly([(hx, y + h - 52), (hx + 26, y + h - 52 + tilt),
                 (hx + 26, y + h - 30 + tilt), (hx, y + h - 30)],
                (176, 120, 80))
        cv.poly([(hx - 3, y + h - 52), (hx + 13, y + h - 62 + tilt),
                 (hx + 29, y + h - 52 + tilt)], (120, 40, 30))
    # Seismograph trace in red, clamped inside the panel.
    sx = x + 8
    sy = y + h - 66
    while sx < x + w - 8:
        nsx = sx + 6
        nsy = sy + (_hash2(sx, 29) % 17) - 8
        if nsy < y + 8:
            nsy = y + 8
        if nsy > y + h - 40:
            nsy = y + h - 40
        cv.line(sx, sy, nsx, nsy, RED)
        sx, sy = nsx, nsy


# ---------------------------------------------------------------- the day
# 48 stories, all of Friday 20 November 2026, as reported that day.
# (section, headline, colour) -- R red, B blue, K ink, G gold.
STORIES = [
    ('UKRAINE', 'Russia fires 400+ drones and 110 missiles at Ukraine; Kyiv bridges hit', 'R'),
    ('POLAND', 'Two Russian missiles land in Poland; no casualties reported', 'R'),
    ('JUSTICE', 'UN court: Myanmar committed genocide against the Rohingya', 'B'),
    ('MARKETS', 'AI sell-off drags S&P 500 down 3.7% into correction', 'B'),
    ('MARKETS', 'Nikkei falls 5.06% as tech rout spreads across Asia', 'B'),
    ('PERU', 'Magnitude 6.7 earthquake shakes central Peru', 'R'),
    ('SUMMIT', 'Trump, Xi and Putin meet in Shenzhen; 90-minute news conference', 'K'),
    ('HORMUZ', 'Tankers catch fire as US-Iran war disrupts strait shipping', 'R'),
    ('HORMUZ', 'Iran stages 14 tankers at Kharg Island to test US blockade', 'R'),
    ('ENERGY', 'IEA: Hormuz disruption is largest energy shock on record', 'G'),
    ('SAUDI', 'Coalition intercepts three Houthi missiles aimed at Riyadh', 'R'),
    ('CLIMATE', 'COP31 draft deal omits fossil fuels; activists protest in Antalya', 'G'),
    ('EUROPE', 'EU and UK agree youth mobility scheme at Brussels summit', 'B'),
    ('UKRAINE', "Kyiv's troops retake 14 settlements in Kharkiv region", 'R'),
    ('UKRAINE', 'Kerch Bridge hit; rail breaks halt trains on crossing', 'R'),
    ('EUROPE', 'EU approves 1 billion euros in military aid for Ukraine', 'B'),
    ('TECH', 'TSMC and Samsung pause advanced chip sales bound for China', 'B'),
    ('TECH', 'US and China agree human oversight of military AI', 'B'),
    ('TRADE', 'Trump floats penalties for US firms building AI centres abroad', 'K'),
    ('US', 'Nikhil Gupta sentenced to over 19 years in New York murder plot', 'K'),
    ('NIGERIA', 'Nigeria moves to end jail terms for attempted suicide', 'G'),
    ('EL SALVADOR', 'Bukele seeks third term after constitution change', 'K'),
    ('CHILDREN', "World Children's Day: Ukraine's deadliest year for children", 'G'),
    ('AFGHANISTAN', 'Restrictions bar women from vital medical help, UN says', 'G'),
    ('IRAQ', 'Iraqi forces enter Jurf al Sakhr after decade of militia control', 'R'),
    ('MEXICO', 'US embassy: Chinese chemicals fuel Sinaloa cartel', 'K'),
    ('CHINA', 'Beijing bars Bloomberg reporter from covering summit', 'K'),
    ('SPORT', 'Messi tops Major League Soccer salaries', 'G'),
    ('SPORT', 'Alcaraz beats Cobolli; Price survives darts quarter-final', 'G'),
    ('FRANCE', 'Police sentenced for 2020 beating of music producer Zecler', 'K'),
    ('US', 'SEC charges Backward Hat Capital in 560 million dollar fraud', 'B'),
    ('DENMARK', 'Denmark says it thwarted Russian plot to kill rapper', 'R'),
    ('SHIPPING', 'UKMTO reports tanker strike and fire in Strait of Hormuz', 'R'),
    ('ARGENTINA', 'Senate approves permanent disability framework unanimously', 'G'),
    ('JAPAN', 'Poll: 93 percent of Japanese see ties with China as poor', 'K'),
    ('US', 'White House replaces cyber security chief after tech outages', 'K'),
    ('SANCTIONS', 'US adds four Iranians to OFAC sanctions list', 'K'),
    ('POLAND', 'Prosecutors probe object that fell at Nowy Lipowiec', 'K'),
    ('EUROPE', 'EU agrees civil protection and health preparedness position', 'B'),
    ('HEALTH', 'Trial pill makes pancreatic tumours undetectable in 1 in 12', 'G'),
    ('UN', 'Race for next secretary-general exposes great-power divisions', 'B'),
    ('EUROPE', 'EU to summon Russian envoy over Kyiv embassy damage', 'R'),
    ('EUROPE', 'Brussels clears Malta, Portugal and Ireland recovery payments', 'B'),
    ('TECH', 'Former Nvidia chief Huang to testify at US Senate hearing', 'B'),
    ('US', 'Suspects charged over alleged 22 million dollar train heist spree', 'K'),
    ('RELIGION', 'Islam set to be largest religion by 2035, study finds', 'G'),
    ('YEMEN', "'It's just fireworks': life in a city besieged by Houthis", 'G'),
    ('EDUCATION', 'Fund gives 52 million dollars to schools in Myanmar and beyond', 'G'),
]

NUMBERS = [
    ('400+', 'DRONES AT UKRAINE'),
    ('110', 'MISSILES FIRED'),
    ('8', 'KILLED IN KYIV'),
    ('-3.7%', 'S&P 500 FALL'),
    ('6.7', 'PERU QUAKE MAG'),
    ('14', 'TOWNS RETAKEN'),
    ('1BN EUR', 'EU AID TO KYIV'),
    ('93%', 'JAPAN POLL'),
]

# 12 cities: (name, longitude, latitude, label dx, label dy).
CITIES = [
    ('KYIV', 30.5, 50.4, 8, -14),
    ('WARSAW', 21.0, 52.2, -46, -14),
    ('LONDON', -0.1, 51.5, -46, -2),
    ('BRUSSELS', 4.35, 50.85, -8, 12),
    ('THE HAGUE', 4.3, 52.07, -60, -14),
    ('WASHINGTON', -77.0, 38.9, -32, 12),
    ('NEW YORK', -74.0, 40.7, 8, -14),
    ('RIYADH', 46.7, 24.7, 8, -14),
    ('HORMUZ', 56.5, 26.5, 8, 12),
    ('LIMA', -77.0, -12.0, -36, -2),
    ('ANTALYA', 30.7, 36.9, 8, 12),
    ('SHENZHEN', 114.0, 22.5, 8, -14),
]

# Stylised continents as clusters of discs (map panel coordinates).
LAND = [
    (150, 898, 26), (195, 890, 24), (235, 902, 20), (170, 920, 18),
    (255, 922, 14), (305, 882, 10),
    (300, 932, 16), (318, 946, 12),
    (540, 890, 14), (562, 886, 10), (528, 896, 10),
    (560, 916, 18), (578, 932, 14), (546, 926, 12),
    (650, 892, 30), (722, 886, 26), (802, 896, 24), (882, 902, 18),
    (702, 916, 18), (822, 936, 10), (852, 940, 8), (882, 942, 14),
]

SECCOL = {'R': RED, 'B': BLUE, 'K': INK, 'G': GOLD}


def _mx(lon):
    return 24 + int((lon + 180.0) / 360.0 * 976)


def _my(lat):
    return 872 + int((75.0 - lat) / 135.0 * 88)


def _border(cv, x, y, w, h, color=INK):
    cv.hline(x, y, w, color)
    cv.hline(x, y + h - 1, w, color)
    cv.vline(x, y, h, color)
    cv.vline(x + w - 1, y, h, color)


# ---------------------------------------------------------------- build
def build():
    cv = Canvas()

    # ---- masthead
    cv.fill_rect(24, 8, 976, 2, INK)
    cv.fill_rect(24, 12, 976, 1, INK)
    cv.text_centred(512, 20, 'THE WORLD IN ONE DAY', 5, INK, bold=True)
    cv.text(24, 62, 'VOL. I - NO. 325', 1, GREY, bold=True)
    cv.text_centred(512, 62, 'FRIDAY 20 NOVEMBER 2026', 2, RED, bold=True)
    cv.text(1024 - 24 - text_width("PRICE: ONE DAY'S NEWS", 1), 62,
            "PRICE: ONE DAY'S NEWS", 1, GREY, bold=True)
    cv.fill_rect(24, 90, 976, 2, INK)
    cv.fill_rect(24, 94, 976, 1, INK)

    # ---- lead: Kyiv picture + headline
    scene_kyiv(cv, 24, 104, 400, 150)
    _border(cv, 24, 104, 400, 150)
    cv.fill_rect(24, 236, 400, 18, BLACK)
    cv.text(32, 240, 'KYIV - THREE BRIDGES HIT IN OVERNIGHT BARRAGE',
            1, WHITE, bold=True)
    cv.text(440, 108, 'LEAD STORY - KYIV, UKRAINE', 1, RED, bold=True)
    yy = 124
    for ln in cv.wrap('RUSSIA FIRES 400 DRONES AND 110 MISSILES AT UKRAINE',
                      560, 3):
        cv.text(440, yy, ln, 3, INK, bold=True)
        yy += 21
    yy += 6
    for ln in cv.wrap('THREE BRIDGES OVER THE DNIPRO RIVER HIT; EIGHT '
                      'PEOPLE KILLED. TWO RUSSIAN MISSILES LAND IN POLAND. '
                      'EUROPE READIES SECURITY GUARANTEES.', 560, 1)[:3]:
        cv.text(440, yy, ln, 1, INK)
        yy += 9
    cv.text(440, 232, 'KYIV - FRIDAY 20 NOVEMBER 2026', 1, GREY, bold=True)

    # ---- trio of pictures
    trio = [(24, scene_icj, 'THE HAGUE - GENOCIDE VERDICT'),
            (354, scene_market, 'NEW YORK - STOCKS IN CORRECTION'),
            (684, scene_quake, 'JUNIN, PERU - 6.7 QUAKE')]
    for tx, fn, cap in trio:
        fn(cv, tx, 258, 315, 108)
        _border(cv, tx, 258, 315, 108)
        caption_bar(cv, tx, 258, 315, 108, cap)

    # ---- 48 stories, 3 columns x 16
    for ci in range(3):
        cx = 24 + ci * 330
        yy = 370
        for section, head, code in STORIES[ci * 16:(ci + 1) * 16]:
            cv.text(cx, yy, section, 1, SECCOL[code], bold=True)
            lines = cv.wrap(head, 315, 1)[:2]
            cv.text(cx, yy + 9, lines[0], 1, INK, bold=True)
            if len(lines) > 1:
                cv.text(cx, yy + 18, lines[1], 1, INK, bold=True)
            cv.hline(cx, yy + 28, 315, RULE)
            yy += 30

    # ---- world map, 12 cities
    cv.fill_rect(24, 854, 976, 108, (217, 230, 234))
    _border(cv, 24, 854, 976, 108)
    for gx in range(24 + 122, 1000, 122):
        cv.vline(gx, 872, 88, (196, 208, 212))
    for (lx, ly, lr) in LAND:
        cv.disc(lx, ly, lr, (216, 201, 163))
    cv.text(32, 858, 'THE WORLD IN ONE DAY - 12 CITIES THAT MADE THE NEWS',
            1, INK, bold=True)
    for name, lon, lat, dx, dy in CITIES:
        px, py = _mx(lon), _my(lat)
        lx, ly = px + dx, py + dy
        cv.line(px, py, lx + len(name) * 3, ly + 3, GREY)
        cv.disc(px, py, 5, WHITE)
        cv.disc(px, py, 3, RED)
        cv.text(lx, ly, name, 1, INK, bold=True)

    # ---- numbers strip
    for i, (num, lab) in enumerate(NUMBERS):
        cx = 24 + i * 122
        cv.text_centred(cx + 61, 968, num, 2, RED, bold=True)
        cv.text_centred(cx + 61, 986, lab, 1, GREY, bold=True)

    # ---- footer: date check
    cv.fill_rect(24, 998, 976, 22, PAPER_DK)
    _border(cv, 24, 998, 976, 22)
    cv.text(32, 1005, chr(10003) + ' DATE CHECK: EVERY STORY HERE HAPPENED '
            'OR WAS FIRST REPORTED ON FRIDAY 20 NOVEMBER 2026.',
            1, INK, bold=True)

    cv.grain()
    return cv


def main():
    out = os.environ.get('MAKEFUN_OUTPUT_DIR') or '/output'
    os.makedirs(out, exist_ok=True)
    data = png_bytes(build().buf)
    path = os.path.join(out, 'entry.png')
    with open(path, 'wb') as f:
        f.write(data)
    print('wrote %s %d bytes sha256=%s'
          % (path, len(data), hashlib.sha256(data).hexdigest()))


if __name__ == '__main__':
    main()
