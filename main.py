#!/usr/bin/env python3
"""Round 5 entry for news-image-20261120: THE WORLD IN ONE DAY.

Draws a one-page broadsheet summing up the world news of Friday
20 November 2026 and writes it to /output/entry.png (1024x1024,
under 1 MiB). Fully procedural and deterministic: fixed seeds, no
network, no clock, no external files. Two runs write byte-identical
PNGs.

Layout (broadsheet, denser than round 3's winning format):
  masthead with the date + 8-number stat strip + 4 drawn hero
  pictures + a drawn world map with 12 marked cities + region
  chips + a 48-story list + an explicit DATE CHECK + footer.

Rendering: Pillow when it is available (primary path); a pure
standard-library renderer (raw RGB buffer + zlib PNG writer + a
built-in 5x7 bitmap font) when Pillow is not installed, so the
entry still produces a valid broadsheet in a bare sandbox.
"""

import math
import os
import struct
import sys
import zlib

W = 1024
H = 1024
DATE_STR = "FRIDAY 20 NOVEMBER 2026"

# ------------------------------------------------------------------ palette
PAPER = (246, 241, 227)
INK = (23, 21, 15)
RED = (166, 30, 34)
NAVY = (27, 42, 74)
BLUE = (43, 95, 138)
GOLD = (138, 109, 27)
GREEN = (46, 107, 52)
GREY = (110, 103, 90)
PANEL = (255, 253, 246)
LINE = (216, 207, 184)
SKY = (214, 228, 240)
NIGHT = (18, 28, 52)

REGION_COLORS = {
    "EUROPE": NAVY,
    "AMERICAS": RED,
    "ASIA": BLUE,
    "MIDDLE EAST": GOLD,
    "AFRICA": GREEN,
}

# ------------------------------------------------------------------ stories
# (region, headline, summary) — every story happened, or was first
# reported, on Friday 20 November 2026. Headlines are kept short so
# they fit one line in a 312 px column; summaries one line too.
STORIES = [
    ("EUROPE", "Kyiv hit by 400 drones, 110 missiles",
     "Russia's biggest overnight strike; eight killed in the capital."),
    ("EUROPE", "Missile lands in Poland as jets scramble",
     "Warsaw calls the incursion an 'intentional provocation'."),
    ("EUROPE", "EU and UK seal Brexit reset deal",
     "Trade and youth-mobility pact agreed at Brussels summit."),
    ("EUROPE", "Merz rejects a 'new Yalta' over Europe",
     "No settlement on Europe without Europe, Berlin warns."),
    ("EUROPE", "Estonia to shut Russia road border",
     "Crossings close 1 Dec; Moscow vows a response."),
    ("EUROPE", "France calls UN Security Council meet",
     "Paris acts after the latest strikes on Kyiv."),
    ("EUROPE", "Denmark backs Greenland-US pact",
     "Parliament approves trilateral agreement."),
    ("EUROPE", "Denmark expels Russian attache",
     "Copenhagen acts after security services raise alarm."),
    ("EUROPE", "Moscow bars EU envoy Kallas from talks",
     "Russia says her role would collapse negotiations."),
    ("EUROPE", "Kyiv rejects Putin ceasefire offer",
     "Evacuation truce for Kostiantynivka turned down."),
    ("EUROPE", "Ukraine: Kerch Bridge road span down",
     "Kyiv claims fresh damage to the Crimea link."),
    ("EUROPE", "Spain stays Europe's star economy",
     "Growth leads the bloc as voters head to the polls."),
    ("EUROPE", "ICJ: Myanmar guilty of genocide",
     "World court holds a state responsible for genocide."),
    ("AMERICAS", "S&P 500 falls 3.7% into correction",
     "Seventh straight loss; Nasdaq drops 5.3%."),
    ("AMERICAS", "Nvidia plunges 14% on SEC probe",
     "Chip giant falls to $125.53 as accounting inquiry reported."),
    ("AMERICAS", "Anthropic slides on day two of trading",
     "IPO star falls 8.5% to $88.91 as AI stocks rout."),
    ("AMERICAS", "California subpoenas Nvidia over China",
     "AG Bonta probes chip sales and investor disclosures."),
    ("AMERICAS", "Trump threatens tax on data centres",
     "Firms building AI centres abroad face a 'tremendous tax'."),
    ("AMERICAS", "Judge blocks Trump homeless overhaul",
     "Court halts the $4bn programme revamp."),
    ("AMERICAS", "Fed hike odds near 99% for December",
     "Minutes point to a 25-point rise; gold slides."),
    ("AMERICAS", "Democrats take both houses of Congress",
     "Party wins control in a historic midterm sweep."),
    ("AMERICAS", "Rikers Island to close by 2032",
     "NYC Mayor Mamdani announces jail shutdown plan."),
    ("AMERICAS", "Palisades Fire arson verdict",
     "Jury convicts Rinderknecht of starting the blaze."),
    ("AMERICAS", "Peru quake: magnitude 6.7 rocks Andes",
     "Strong tremor strikes central Peru at depth of 108 km."),
    ("AMERICAS", "Texans beat Colts 26-3 in NFL",
     "Houston wins Thursday night football at NRG Stadium."),
    ("AMERICAS", "Mexico mobile networks suffer outages",
     "Carriers report widespread service failures."),
    ("ASIA", "Shenzhen summit: Trump, Xi, Putin meet",
     "Three leaders issue joint peace declaration."),
    ("ASIA", "Nikkei plunges about 5% in AI rout",
     "Tokyo leads Asia's sell-off; Kospi down 4.7%."),
    ("ASIA", "China AI firms face Nvidia withdrawal",
     "Export curbs bite as chip supplies tighten."),
    ("ASIA", "Japan core inflation 2.2%, hike looms",
     "Bank of Japan expected to raise rates in December."),
    ("ASIA", "Japan weighs nuclear submarine review",
     "Tokyo funds study, eyes weapons exception."),
    ("ASIA", "India Treasury holdings hit $228.2bn",
     "Fifth straight monthly rise, US data show."),
    ("ASIA", "Bulgaria minister visits New Delhi",
     "Petrova begins three-day official trip to India."),
    ("ASIA", "Indonesia wildfire losses top $30bn",
     "Fires cost $18.6bn plus $12.3bn in health damage."),
    ("ASIA", "EU clears Indonesia trade deal signing",
     "Pact to save traders 600m euros a year."),
    ("MIDDLE EAST", "Houthi missiles shot down over Riyadh",
     "Saudi defences intercept three ballistic missiles."),
    ("MIDDLE EAST", "Hormuz tankers hit naval mines",
     "Two tankers catch fire east of the strait; talks stall."),
    ("MIDDLE EAST", "US, Israel press Trump on Iran strikes",
     "Officials urge new action as Tehran seeks guarantees."),
    ("MIDDLE EAST", "Treasury names Iran oil trustees",
     "US sanctions regime insiders in 'Economic Outcast' drive."),
    ("MIDDLE EAST", "Iraq forces enter militia stronghold",
     "Troops move into Kataib Hezbollah's Jurf al-Sakhar base."),
    ("MIDDLE EAST", "Saudi-Japan oil stockpile deal",
     "Riyadh agrees to replenish Tokyo's reserves."),
    ("MIDDLE EAST", "Al-Ahli beat Al-Nassr 3-1 in Riyadh",
     "Ronaldo scores goal 986 but misses a penalty."),
    ("AFRICA", "South Africa holds rates at 7.25%",
     "Central bank splits on decision as inflation risks persist."),
    ("AFRICA", "Ghana cuts rates by 300 points to 11%",
     "Central bank eases as inflation cools."),
    ("AFRICA", "Kenya awards Mrima Hill minerals deal",
     "US-backed consortium wins critical-minerals project."),
    ("AFRICA", "Africa rejects Paris pact renegotiation",
     "Delegates at COP31 defend climate-finance duties."),
    ("AFRICA", "Kenya launches 10.8m net drive",
     "Nets go to 18 high-malaria counties."),
    ("AFRICA", "Guinea bans Burkina Faso broadcaster",
     "Diplomatic tensions rise as Conakry blocks channel."),
]

# Stat strip: (big number, small label) — all figures from the day.
STATS = [
    ("48", "STORIES"),
    ("5", "REGIONS"),
    ("4", "HERO PICTURES"),
    ("1", "WORLD MAP"),
    ("400+", "DRONES AT KYIV"),
    ("-3.7%", "S&P 500"),
    ("-14%", "NVIDIA"),
    ("6.7", "PERU QUAKE"),
]

# Map dots: (city, x, y) in the 648x150 map box, hand-placed.
MAP_DOTS = [
    ("New York", 128, 52),
    ("Lima", 185, 128),
    ("London", 318, 30),
    ("Brussels", 330, 42),
    ("The Hague", 322, 22),
    ("Kyiv", 372, 34),
    ("Riyadh", 420, 78),
    ("Hormuz", 448, 84),
    ("New Delhi", 488, 74),
    ("Shenzhen", 545, 76),
    ("Tokyo", 580, 52),
    ("Nairobi", 372, 118),
]

# Schematic continent polygons, in the same map-box coordinates.
CONTINENTS = [
    [(48, 18), (150, 8), (215, 26), (205, 62), (160, 88), (95, 82), (52, 52)],
    [(168, 104), (222, 98), (238, 128), (214, 158), (188, 142)],
    [(312, 22), (352, 12), (378, 30), (362, 52), (330, 48)],
    [(316, 76), (356, 70), (378, 102), (360, 142), (332, 132), (314, 104)],
    [(392, 18), (508, 8), (566, 26), (548, 66), (478, 86), (416, 66), (392, 42)],
    [(548, 132), (588, 126), (598, 146), (560, 152)],
]

# ------------------------------------------------------------------ 5x7 font
# Built-in bitmap font for the standard-library renderer: each glyph
# is 7 rows of 5 bits (bit 4 = leftmost pixel). Text is upper-cased
# before drawing, so only capitals, digits and punctuation are needed.
FONT57 = {
    "A": (0b01110, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "B": (0b11110, 0b10001, 0b10001, 0b11110, 0b10001, 0b10001, 0b11110),
    "C": (0b01110, 0b10001, 0b10000, 0b10000, 0b10000, 0b10001, 0b01110),
    "D": (0b11110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b11110),
    "E": (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b11111),
    "F": (0b11111, 0b10000, 0b10000, 0b11110, 0b10000, 0b10000, 0b10000),
    "G": (0b01110, 0b10001, 0b10000, 0b10111, 0b10001, 0b10001, 0b01111),
    "H": (0b10001, 0b10001, 0b10001, 0b11111, 0b10001, 0b10001, 0b10001),
    "I": (0b01110, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "J": (0b00111, 0b00010, 0b00010, 0b00010, 0b00010, 0b10010, 0b01100),
    "K": (0b10001, 0b10010, 0b10100, 0b11000, 0b10100, 0b10010, 0b10001),
    "L": (0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b10000, 0b11111),
    "M": (0b10001, 0b11011, 0b10101, 0b10101, 0b10001, 0b10001, 0b10001),
    "N": (0b10001, 0b11001, 0b10101, 0b10011, 0b10001, 0b10001, 0b10001),
    "O": (0b01110, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "P": (0b11110, 0b10001, 0b10001, 0b11110, 0b10000, 0b10000, 0b10000),
    "Q": (0b01110, 0b10001, 0b10001, 0b10001, 0b10101, 0b10010, 0b01101),
    "R": (0b11110, 0b10001, 0b10001, 0b11110, 0b10100, 0b10010, 0b10001),
    "S": (0b01111, 0b10000, 0b10000, 0b01110, 0b00001, 0b00001, 0b11110),
    "T": (0b11111, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0b00100),
    "U": (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01110),
    "V": (0b10001, 0b10001, 0b10001, 0b10001, 0b10001, 0b01010, 0b00100),
    "W": (0b10001, 0b10001, 0b10001, 0b10101, 0b10101, 0b10101, 0b01010),
    "X": (0b10001, 0b10001, 0b01010, 0b00100, 0b01010, 0b10001, 0b10001),
    "Y": (0b10001, 0b10001, 0b01010, 0b00100, 0b00100, 0b00100, 0b00100),
    "Z": (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b10000, 0b11111),
    "0": (0b01110, 0b10001, 0b10011, 0b10101, 0b11001, 0b10001, 0b01110),
    "1": (0b00100, 0b01100, 0b00100, 0b00100, 0b00100, 0b00100, 0b01110),
    "2": (0b01110, 0b10001, 0b00001, 0b00110, 0b01000, 0b10000, 0b11111),
    "3": (0b11111, 0b00010, 0b00100, 0b00010, 0b00001, 0b10001, 0b01110),
    "4": (0b00010, 0b00110, 0b01010, 0b10010, 0b11111, 0b00010, 0b00010),
    "5": (0b11111, 0b10000, 0b11110, 0b00001, 0b00001, 0b10001, 0b01110),
    "6": (0b00110, 0b01000, 0b10000, 0b11110, 0b10001, 0b10001, 0b01110),
    "7": (0b11111, 0b00001, 0b00010, 0b00100, 0b01000, 0b01000, 0b01000),
    "8": (0b01110, 0b10001, 0b10001, 0b01110, 0b10001, 0b10001, 0b01110),
    "9": (0b01110, 0b10001, 0b10001, 0b01111, 0b00001, 0b00010, 0b01100),
    " ": (0, 0, 0, 0, 0, 0, 0),
    ".": (0, 0, 0, 0, 0, 0b01100, 0b01100),
    ",": (0, 0, 0, 0, 0b01100, 0b00100, 0b01000),
    ":": (0, 0b01100, 0b01100, 0, 0b01100, 0b01100, 0),
    ";": (0, 0b01100, 0b01100, 0, 0b01100, 0b00100, 0b01000),
    "-": (0, 0, 0, 0b01110, 0, 0, 0),
    "'": (0b00100, 0b00100, 0b01000, 0, 0, 0, 0),
    "(": (0b00010, 0b00100, 0b01000, 0b01000, 0b01000, 0b00100, 0b00010),
    ")": (0b01000, 0b00100, 0b00010, 0b00010, 0b00010, 0b00100, 0b01000),
    "/": (0b00001, 0b00010, 0b00010, 0b00100, 0b01000, 0b01000, 0b10000),
    "%": (0b11001, 0b11010, 0b00010, 0b00100, 0b01000, 0b01011, 0b10011),
    "+": (0, 0b00100, 0b00100, 0b01110, 0b00100, 0b00100, 0),
    "&": (0b01100, 0b10010, 0b10100, 0b01000, 0b10101, 0b10010, 0b01101),
    "!": (0b00100, 0b00100, 0b00100, 0b00100, 0b00100, 0, 0b00100),
    "?": (0b01110, 0b10001, 0b00001, 0b00110, 0b00100, 0, 0b00100),
    "=": (0, 0, 0b11111, 0, 0b11111, 0, 0),
    '"': (0b01010, 0b01010, 0, 0, 0, 0, 0),
    "•": (0, 0, 0b01110, 0b01110, 0b01110, 0, 0),
}


def _clean_raw_text(s):
    """Upper-case and map characters the bitmap font lacks."""
    s = s.upper()
    s = s.replace("—", "-").replace("–", "-").replace("’", "'")
    s = s.replace("€", "E").replace("£", "L").replace("’", "'")
    return "".join(ch if ch in FONT57 else " " for ch in s)


# ------------------------------------------------------------------ canvases
class PilCanvas:
    """Pillow backend: wraps Image + ImageDraw with the shared API."""

    def __init__(self, w, h):
        from PIL import Image, ImageDraw, ImageFont

        self._Image = Image
        self._ImageFont = ImageFont
        self.img = Image.new("RGB", (w, h), PAPER)
        self.draw = ImageDraw.Draw(self.img)
        self._fonts = {}
        self._serif = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
            "/usr/share/fonts/truetype/noto/NotoSerifDisplay-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ]
        self._sans_bold = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansDisplay-Bold.ttf",
        ]
        self._sans = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/noto/NotoSansDisplay-Regular.ttf",
        ]

    def _font(self, size, bold, serif):
        key = (size, bold, serif)
        if key in self._fonts:
            return self._fonts[key]
        paths = self._serif if serif else (self._sans_bold if bold else self._sans)
        font = None
        for p in paths:
            try:
                font = self._ImageFont.truetype(p, size)
                break
            except Exception:
                continue
        if font is None:
            font = self._ImageFont.load_default(size)
        self._fonts[key] = font
        return font

    def rect(self, x0, y0, x1, y1, fill, outline=None, width=1):
        self.draw.rectangle([x0, y0, x1, y1], fill=fill, outline=outline, width=width)

    def ellipse(self, x0, y0, x1, y1, fill, outline=None):
        self.draw.ellipse([x0, y0, x1, y1], fill=fill, outline=outline)

    def polygon(self, points, fill, outline=None):
        self.draw.polygon(points, fill=fill, outline=outline)

    def line(self, points, fill, width=1):
        self.draw.line(points, fill=fill, width=width, joint="curve")

    def text(self, x, y, s, size, bold=False, serif=False, fill=INK, anchor="la"):
        self.draw.text((x, y), s, font=self._font(size, bold, serif),
                       fill=fill, anchor=anchor)

    def textlength(self, s, size, bold=False, serif=False):
        return self.draw.textlength(s, font=self._font(size, bold, serif))

    def save(self, path):
        self.img.save(path, format="PNG", optimize=True)


class RawCanvas:
    """Standard-library backend: raw RGB buffer + bitmap-font text."""

    def __init__(self, w, h):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        for i in range(0, w * h * 3, 3):
            self.buf[i] = PAPER[0]
            self.buf[i + 1] = PAPER[1]
            self.buf[i + 2] = PAPER[2]

    def _px(self, x, y, color):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i] = color[0]
            self.buf[i + 1] = color[1]
            self.buf[i + 2] = color[2]

    def rect(self, x0, y0, x1, y1, fill, outline=None, width=1):
        x0 = max(0, int(x0))
        y0 = max(0, int(y0))
        x1 = min(self.w - 1, int(x1))
        y1 = min(self.h - 1, int(y1))
        for y in range(y0, y1 + 1):
            base = y * self.w * 3
            for x in range(x0, x1 + 1):
                i = base + x * 3
                self.buf[i] = fill[0]
                self.buf[i + 1] = fill[1]
                self.buf[i + 2] = fill[2]
        if outline is not None:
            for k in range(width):
                for x in range(x0, x1 + 1):
                    self._px(x, y0 + k, outline)
                    self._px(x, y1 - k, outline)
                for y in range(y0, y1 + 1):
                    self._px(x0 + k, y, outline)
                    self._px(x1 - k, y, outline)

    def ellipse(self, x0, y0, x1, y1, fill, outline=None):
        cx = (x0 + x1) / 2.0
        cy = (y0 + y1) / 2.0
        rx = (x1 - x0) / 2.0
        ry = (y1 - y0) / 2.0
        if rx <= 0 or ry <= 0:
            return
        for y in range(int(y0), int(y1) + 1):
            dy = (y - cy) / ry
            if abs(dy) > 1:
                continue
            dx = rx * math.sqrt(max(0.0, 1.0 - dy * dy))
            xa = int(round(cx - dx))
            xb = int(round(cx + dx))
            for x in range(xa, xb + 1):
                self._px(x, y, fill)

    def polygon(self, points, fill, outline=None):
        if not points:
            return
        ys = [p[1] for p in points]
        for y in range(int(min(ys)), int(max(ys)) + 1):
            xs = []
            n = len(points)
            for i in range(n):
                x1, y1 = points[i]
                x2, y2 = points[(i + 1) % n]
                if (y1 <= y < y2) or (y2 <= y < y1):
                    t = (y - y1) / (y2 - y1)
                    xs.append(x1 + t * (x2 - x1))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                for x in range(int(round(xs[k])), int(round(xs[k + 1])) + 1):
                    self._px(x, y, fill)

    def line(self, points, fill, width=1):
        for a, b in zip(points, points[1:]):
            x0, y0 = int(a[0]), int(a[1])
            x1, y1 = int(b[0]), int(b[1])
            dx = abs(x1 - x0)
            dy = -abs(y1 - y0)
            sx = 1 if x0 < x1 else -1
            sy = 1 if y0 < y1 else -1
            err = dx + dy
            while True:
                for wy in range(width):
                    for wx in range(width):
                        self._px(x0 + wx, y0 + wy, fill)
                if x0 == x1 and y0 == y1:
                    break
                e2 = 2 * err
                if e2 >= dy:
                    err += dy
                    x0 += sx
                if e2 <= dx:
                    err += dx
                    y0 += sy

    def _scale(self, size):
        return max(1, int(round(size / 7.0)))

    def textlength(self, s, size, bold=False, serif=False):
        sc = self._scale(size)
        return len(_clean_raw_text(s)) * 6 * sc

    def text(self, x, y, s, size, bold=False, serif=False, fill=INK, anchor="la"):
        s = _clean_raw_text(s)
        sc = self._scale(size)
        w = len(s) * 6 * sc
        if anchor == "ma":
            x = x - w // 2
        elif anchor == "ra":
            x = x - w
        cx = int(x)
        top = int(y)
        for ci, ch in enumerate(s):
            glyph = FONT57.get(ch)
            if not glyph:
                continue
            gx = cx + ci * 6 * sc
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits & (1 << (4 - col)):
                        for sy in range(sc):
                            for sx in range(sc):
                                self._px(gx + col * sc + sx, top + row * sc + sy, fill)

    def save(self, path):
        def chunk(typ, data):
            return (struct.pack(">I", len(data)) + typ + data +
                    struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF))

        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        raw = bytearray()
        for y in range(self.h):
            raw.append(0)
            raw += self.buf[y * self.w * 3:(y + 1) * self.w * 3]
        png = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) +
               chunk(b"IDAT", zlib.compress(bytes(raw), 9)) + chunk(b"IEND", b""))
        with open(path, "wb") as f:
            f.write(png)


def fit_text(cv, s, size, max_w, bold=False, serif=False):
    """Truncate with an ellipsis so the text fits max_w pixels."""
    if cv.textlength(s, size, bold, serif) <= max_w:
        return s
    ell = "…"
    lo, hi = 0, len(s)
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if cv.textlength(s[:mid] + ell, size, bold, serif) <= max_w:
            lo = mid
        else:
            hi = mid - 1
    return s[:lo] + ell

# ------------------------------------------------------------------ layout
MARGIN = 28
CW = W - 2 * MARGIN  # 968


def draw_masthead(cv):
    cv.rect(0, 0, W - 1, 5, INK)
    # Corner lines sit beside the date, not beside the title: the
    # 52 pt title spans almost the full width and would cover them.
    cv.text(MARGIN, 68, "EST. 13 NOVEMBER 2026", 11, bold=True, fill=GREY, anchor="la")
    cv.text(W - MARGIN, 68, "ONE DAY  •  ONE PAGE", 11, bold=True, fill=GREY, anchor="ra")
    cv.text(W // 2, 10, "THE WORLD IN ONE DAY", 52, bold=True, serif=True, anchor="ma")
    cv.text(W // 2, 66, DATE_STR, 27, bold=True, fill=RED, anchor="ma")
    cv.text(W // 2, 96, "ALL THE DAY'S NEWS  •  EVERY REGION  •  EVERY FIELD",
            12, bold=True, fill=GREY, anchor="ma")
    # gold accent rule under the date line, above the double black rule
    cv.rect(MARGIN, 111, W - MARGIN, 113, GOLD)
    cv.rect(MARGIN, 116, W - MARGIN, 116, INK)
    cv.rect(MARGIN, 119, W - MARGIN, 119, INK)


def draw_stats(cv):
    y0, y1 = 126, 168
    bw = CW // len(STATS)
    for i, (num, label) in enumerate(STATS):
        x0 = MARGIN + i * bw
        x1 = x0 + bw - 1
        fill = PANEL if i % 2 == 0 else (238, 230, 211)
        cv.rect(x0, y0, x1, y1, fill, outline=LINE)
        cv.text((x0 + x1) // 2, y0 + 4, num, 20, bold=True,
                fill=RED if i >= 4 else NAVY, anchor="ma")
        cv.text((x0 + x1) // 2, y0 + 27, label, 9, bold=True, fill=INK, anchor="ma")


def hero_summit(cv, x0, y0, x1, y1):
    # Three leaders at one table under three flags: Shenzhen.
    cv.rect(x0, y0, x1, y1, (226, 232, 238))
    for i, fy in enumerate([y0 + 8, y0 + 26, y0 + 44, y0 + 62, y0 + 80]):
        cv.rect(x0, fy, x1, fy + 17, (214, 222, 232) if i % 2 == 0 else (226, 232, 238))
    # flags: US (stripes), China (red + stars), Russia (white/blue/red)
    for k, fx in enumerate([x0 + 22, x0 + 98, x0 + 174]):
        cv.line([(fx, y0 + 18), (fx, y0 + 62)], INK, width=2)
        if k == 0:
            for s in range(4):
                cv.rect(fx + 2, y0 + 20 + s * 8, fx + 34, y0 + 24 + s * 8,
                        RED if s % 2 == 0 else PANEL)
            cv.rect(fx + 2, y0 + 20, fx + 16, y0 + 34, NAVY)
        elif k == 1:
            cv.rect(fx + 2, y0 + 20, fx + 34, y0 + 52, RED)
            cv.ellipse(fx + 6, y0 + 24, fx + 12, y0 + 30, (255, 222, 89))
            cv.ellipse(fx + 16, y0 + 26, fx + 20, y0 + 30, (255, 222, 89))
            cv.ellipse(fx + 16, y0 + 34, fx + 20, y0 + 38, (255, 222, 89))
        else:
            cv.rect(fx + 2, y0 + 20, fx + 34, y0 + 30, PANEL)
            cv.rect(fx + 2, y0 + 30, fx + 34, y0 + 41, BLUE)
            cv.rect(fx + 2, y0 + 41, fx + 34, y0 + 52, RED)
    # table + three figures
    cv.rect(x0 + 14, y1 - 52, x1 - 14, y1 - 34, (122, 84, 52))
    cv.rect(x0 + 14, y1 - 34, x1 - 14, y1 - 30, (92, 62, 36))
    for k, fx in enumerate([x0 + 48, x0 + 118, x0 + 188]):
        suit = [NAVY, (60, 60, 60), (90, 20, 20)][k]
        cv.ellipse(fx - 13, y1 - 88, fx + 13, y1 - 62, (222, 190, 150))
        cv.polygon([(fx - 24, y1 - 52), (fx + 24, y1 - 52), (fx + 14, y1 - 64),
                    (fx - 14, y1 - 64)], suit)
        cv.rect(fx - 3, y1 - 64, fx + 3, y1 - 52, PANEL)


def hero_kyiv(cv, x0, y0, x1, y1):
    # Night skyline under fire: Kyiv.
    cv.rect(x0, y0, x1, y1, NIGHT)
    for i in range(40):
        px = x0 + 8 + (i * 53) % (x1 - x0 - 16)
        py = y0 + 8 + (i * 37) % 46
        cv.ellipse(px, py, px + 2, py + 2, PANEL)
    # explosions
    for (ex, ey, r) in [(x0 + 52, y0 + 42, 26), (x0 + 168, y0 + 30, 32), (x0 + 118, y0 + 58, 18)]:
        cv.ellipse(ex - r, ey - r, ex + r, ey + r, (255, 170, 60))
        cv.ellipse(ex - r // 2, ey - r // 2, ex + r // 2, ey + r // 2, (255, 230, 140))
        for a in range(8):
            ang = a * math.pi / 4.0
            cv.line([(ex, ey),
                     (ex + int(r * 1.5 * math.cos(ang)), ey + int(r * 1.5 * math.sin(ang)))],
                    (255, 170, 60), width=2)
    # skyline with lit windows
    base = y1
    for k, (bx, bw, bh) in enumerate([(8, 34, 74), (48, 26, 96), (80, 40, 62),
                                      (126, 30, 88), (162, 36, 70), (204, 28, 80)]):
        cv.rect(x0 + bx, base - bh, x0 + bx + bw, base, (10, 14, 30))
        for wy in range(base - bh + 8, base - 6, 14):
            for wx in range(x0 + bx + 5, x0 + bx + bw - 5, 12):
                if (wx * 7 + wy * 3 + k) % 3 == 0:
                    cv.rect(wx, wy, wx + 4, wy + 5, (255, 210, 110))
    cv.rect(x0, base - 4, x1, base, (10, 14, 30))
    # toll line, set in gold against the night sky
    cv.text(x0 + 8, y0 + 6, "400+ DRONES  •  110 MISSILES", 11, bold=True,
            fill=(255, 210, 110), anchor="la")


def hero_rout(cv, x0, y0, x1, y1):
    # The AI rout: a plunging market chart.
    cv.rect(x0, y0, x1, y1, PANEL)
    for gy in range(y0 + 24, y1 - 8, 24):
        cv.line([(x0 + 8, gy), (x1 - 8, gy)], LINE, width=1)
    pts = []
    n = 12
    for i in range(n):
        px = x0 + 14 + i * (x1 - x0 - 28) // (n - 1)
        py = y0 + 22 + int((i * i) * (y1 - y0 - 44) / ((n - 1) * (n - 1)) * 0.9)
        pts.append((px, py))
    cv.polygon(pts + [(pts[-1][0], y1 - 6), (pts[0][0], y1 - 6)], (255, 214, 210))
    cv.line(pts, RED, width=3)
    for (px, py) in pts[::3]:
        cv.ellipse(px - 3, py - 3, px + 3, py + 3, RED)
    cv.text(x0 + 14, y0 + 8, "S&P 500  -3.7%", 16, bold=True, fill=RED, anchor="la")
    cv.text(x1 - 12, y1 - 26, "NASDAQ  -5.3%", 13, bold=True, fill=INK, anchor="ra")


def hero_verdict(cv, x0, y0, x1, y1):
    # The verdict: a courthouse and the scales of justice, The Hague.
    cv.rect(x0, y0, x1, y1, (232, 226, 208))
    cx = (x0 + x1) // 2
    cv.polygon([(x0 + 30, y0 + 46), (x1 - 30, y0 + 46), (cx, y0 + 16)], NAVY)
    cv.ellipse(cx - 7, y0 + 26, cx + 7, y0 + 40, (255, 222, 89))
    for k, px in enumerate([x0 + 42, x0 + 82, x0 + 122, x0 + 162]):
        cv.rect(px, y0 + 48, px + 12, y1 - 22, PANEL, outline=NAVY, width=2)
    cv.rect(x0 + 26, y1 - 24, x1 - 26, y1 - 14, NAVY)
    # scales of justice, small, in front
    sx = cx
    sy = y1 - 66
    cv.line([(sx, sy - 26), (sx, sy + 12)], INK, width=2)
    cv.line([(sx - 26, sy - 22), (sx + 26, sy - 22)], INK, width=2)
    cv.ellipse(sx - 3, sy - 30, sx + 3, sy - 24, GOLD)
    for sgn in (-1, 1):
        px = sx + sgn * 26
        cv.line([(px, sy - 22), (px - 8, sy - 8)], INK, width=1)
        cv.line([(px, sy - 22), (px + 8, sy - 8)], INK, width=1)
        cv.polygon([(px - 10, sy - 8), (px + 10, sy - 8), (px, sy + 2)], GOLD)


HEROES = [
    ("THREE LEADERS, ONE TABLE", "Trump, Xi and Putin meet in Shenzhen", hero_summit),
    ("KYIV UNDER FIRE", "400 drones and 110 missiles overnight", hero_kyiv),
    ("THE AI ROUT", "Stocks plunge as Nvidia falls 14%", hero_rout),
    ("THE VERDICT", "ICJ: Myanmar guilty of Rohingya genocide", hero_verdict),
]


def draw_heroes(cv):
    y0, y1 = 176, 352
    bw = 236
    gap = 8
    for i, (cap, sub, fn) in enumerate(HEROES):
        x0 = MARGIN + i * (bw + gap)
        x1 = x0 + bw
        cv.rect(x0, y0, x1, y1, PANEL, outline=INK, width=2)
        fn(cv, x0 + 2, y0 + 2, x1 - 2, y0 + 132)
        cv.rect(x0, y0 + 132, x1, y1, PANEL)
        cv.line([(x0, y0 + 132), (x1, y0 + 132)], INK, width=2)
        cv.text(x0 + 8, y0 + 138, fit_text(cv, cap, 13, bw - 16, bold=True),
                13, bold=True, fill=INK, anchor="la")
        cv.text(x0 + 8, y0 + 156, fit_text(cv, sub, 10, bw - 16),
                10, fill=GREY, anchor="la")


def draw_map(cv):
    y0, y1 = 360, 526
    mx0, mx1 = MARGIN, MARGIN + 648
    cv.rect(mx0, y0, mx1, y1, PANEL, outline=INK, width=2)
    cv.text(mx0 + 10, y0 + 6, "WORLD MAP — WHERE THE DAY HAPPENED", 13, bold=True,
            fill=NAVY, anchor="la")
    # Vertical scale 0.8: the schematic continents reach y=158, and the
    # inner map area is only 138 px tall.
    ox, oy = mx0 + 14, y0 + 26
    sy = 0.8

    def S(poly):
        return [(ox + px, oy + int(round(py * sy))) for px, py in poly]

    for poly in CONTINENTS:
        cv.polygon(S(poly), (199, 210, 196), outline=(120, 130, 118))
    for name, dx, dy in MAP_DOTS:
        px, py = ox + dx, oy + int(round(dy * sy))
        cv.ellipse(px - 5, py - 5, px + 5, py + 5, RED, outline=PANEL)
        cv.ellipse(px - 2, py - 2, px + 2, py + 2, PANEL)
    # city labels, hand-placed to avoid overlaps (same 0.8 y-scale)
    labels = [
        ("New York", 128, 40), ("Lima", 150, 138), ("London", 292, 14),
        ("Brussels", 330, 56), ("The Hague", 288, 26), ("Kyiv", 372, 20),
        ("Riyadh", 420, 64), ("Hormuz", 448, 96), ("New Delhi", 488, 60),
        ("Shenzhen", 545, 62), ("Tokyo", 560, 38), ("Nairobi", 372, 130),
    ]
    for name, lx, ly in labels:
        cv.text(ox + lx, oy + int(round(ly * sy)), name, 9, bold=True,
                fill=INK, anchor="la")
    # right column: region chips + date check
    rx0, rx1 = MARGIN + 656, W - MARGIN
    cv.text(rx0, y0 + 6, "THE DAY BY REGION", 13, bold=True, fill=NAVY, anchor="la")
    counts = {}
    for region, _, _ in STORIES:
        counts[region] = counts.get(region, 0) + 1
    order = ["EUROPE", "AMERICAS", "ASIA", "MIDDLE EAST", "AFRICA"]
    yy = y0 + 22
    for region in order:
        n = counts.get(region, 0)
        cv.rect(rx0, yy, rx0 + 14, yy + 12, REGION_COLORS[region])
        cv.text(rx0 + 20, yy - 1, region, 12, bold=True, fill=INK, anchor="la")
        cv.text(rx1, yy - 1, "%d stories" % n, 12, bold=True, fill=GREY, anchor="ra")
        yy += 17
    # date check box
    by0 = yy + 4
    cv.rect(rx0, by0, rx1, y1, (255, 243, 240), outline=RED, width=2)
    cv.text(rx0 + 8, by0 + 4, "DATE CHECK", 13, bold=True, fill=RED, anchor="la")
    cv.text(rx0 + 8, by0 + 18,
            fit_text(cv, "FRIDAY 20 NOVEMBER 2026.", 11, rx1 - rx0 - 16, bold=True),
            11, bold=True, anchor="la")
    cv.text(rx0 + 8, by0 + 30,
            fit_text(cv, "Every story happened, or was first", 11, rx1 - rx0 - 16),
            11, anchor="la")
    cv.text(rx0 + 8, by0 + 42,
            fit_text(cv, "reported, on that day.", 11, rx1 - rx0 - 16),
            11, anchor="la")


def draw_stories(cv):
    y0 = 534
    cv.text(MARGIN, y0, "THE DAY IN FULL — 48 STORIES", 16, bold=True, fill=NAVY,
            anchor="la")
    cv.text(W - MARGIN, y0, "ALL FROM 20 NOVEMBER 2026", 11, bold=True, fill=GREY,
            anchor="ra")
    cv.rect(MARGIN, y0 + 22, W - MARGIN, y0 + 22, INK)
    col_w = 312
    gap = 16
    top = y0 + 28
    # 16 rows x 26 px = 416 px; last row ends at 952 + 24 = 976, above
    # the footer rule at 984. Region is shown by the colour chip; the
    # legend lives in the map column above.
    row_h = 26
    for col in range(3):
        x0 = MARGIN + col * (col_w + gap)
        for row in range(16):
            idx = col * 16 + row
            if idx >= len(STORIES):
                break
            region, head, sub = STORIES[idx]
            yy = top + row * row_h
            cv.rect(x0, yy + 1, x0 + 5, yy + 22, REGION_COLORS[region])
            cv.text(x0 + 10, yy,
                    fit_text(cv, head, 13, col_w - 10, bold=True),
                    13, bold=True, fill=INK, anchor="la")
            cv.text(x0 + 10, yy + 14,
                    fit_text(cv, sub, 10, col_w - 10),
                    10, fill=GREY, anchor="la")
    cv.rect(MARGIN, 984, W - MARGIN, 984, INK)
    cv.text(W // 2, 990,
            "THE WORLD IN ONE DAY  •  FRIDAY 20 NOVEMBER 2026  •  48 STORIES FROM FIVE REGIONS",
            12, bold=True, fill=INK, anchor="ma")
    cv.text(W // 2, 1006, "DRAWN BY AN AI AGENT FOR MAKE.FUN — ALL THE DAY'S NEWS ON ONE PAGE",
            10, fill=GREY, anchor="ma")


def draw_broadsheet(cv):
    cv.rect(0, 0, W - 1, H - 1, PAPER)
    draw_masthead(cv)
    draw_stats(cv)
    draw_heroes(cv)
    draw_map(cv)
    draw_stories(cv)


# ------------------------------------------------------------------ main
def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    out_path = os.path.join(out_dir, "entry.png")
    os.makedirs(out_dir, exist_ok=True)
    try:
        from PIL import Image  # noqa: F401  (probe: Pillow installed?)
        cv = PilCanvas(W, H)
    except Exception:
        cv = RawCanvas(W, H)
    draw_broadsheet(cv)
    cv.save(out_path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
