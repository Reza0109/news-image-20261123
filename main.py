"""news-image-20261123: Sum up 23 November 2026 in one image.

Pure Python 3.13, standard library only. Renders a 1024x1024 PNG
with 33 verified news stories from 23 November 2026 and writes it
to /output/entry.png. Deterministic: no time, no randomness, no
network. Uses a hand-defined 5x7 bitmap font (with a dotted zero
so "0" never reads as the letter O) and a hand-written PNG encoder.
"""

import os
import struct
import zlib

W, H = 1024, 1024

# ---------------------------------------------------------------- font --
# 5x7 bitmap glyphs, "1" = pixel on. The zero glyph carries a centre
# dot (row 3 is "10101") so it is unmistakably a zero, not an O.
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10001", "10101", "10001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "*": ("00000", "00100", "10101", "01110", "10101", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    "@": ("01110", "10001", "10111", "10101", "10110", "10000", "01110"),
    "#": ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    "_": ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
}

# -------------------------------------------------------------- colours --
BG = (7, 11, 24)        # deep navy
PANEL = (16, 24, 46)    # hero panel
PANEL2 = (22, 32, 58)   # grid panels
RED = (230, 35, 45)     # accent strip
WHITE = (245, 245, 240)
MUTED = (160, 170, 190)
GOLD = (255, 180, 40)
RULE = (50, 60, 85)     # divider line

# -------------------------------------------------------------- canvas --
buf = bytearray(W * H * 3)


def rect(x, y, w, h, c):
    """Fill an axis-aligned rectangle (clipped to the canvas)."""
    if w <= 0 or h <= 0:
        return
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    if x1 <= x0 or y1 <= y0:
        return
    row = bytes(c) * (x1 - x0)
    for yy in range(y0, y1):
        s = (yy * W + x0) * 3
        buf[s:s + len(row)] = row


def draw_char(x, y, ch, s, c):
    g = FONT.get(ch)
    if g is None:
        return
    for r in range(7):
        row = g[r]
        for col in range(5):
            if row[col] == "1":
                rect(x + col * s, y + r * s, s, s, c)


def text_w(t, s):
    """Pixel width of text at scale s (no trailing space)."""
    return len(t) * 6 * s - s if t else 0


def draw_text(x, y, t, s, c):
    """Draw text left-aligned at (x, y); returns the x after the text."""
    t = t.upper()
    cx = x
    for ch in t:
        if ch != " ":
            draw_char(cx, y, ch, s, c)
        cx += 6 * s
    return cx


def draw_centered(cx, y, t, s, c):
    draw_text(cx - text_w(t.upper(), s) // 2, y, t, s, c)


def grid_panel(x, y, w, h, tag, heads, details):
    """One of the four large secondary-story panels."""
    rect(x, y, w, h, PANEL2)
    draw_text(x + 16, y + 12, tag, 2, GOLD)
    hy = y + 34
    for ln in heads:
        draw_text(x + 16, hy, ln, 3, WHITE)
        hy += 26
    dy = hy + 4
    for ln in details:
        draw_text(x + 16, dy, ln, 2, MUTED)
        dy += 17


# -------------------------------------------------------------- content --
# 33 stories, verified 23 Nov 2026. Hero + 4 grid + 28 supporting.

SUPPORTING = [
    (5, "Russian frigate Merkury sunk off Benghazi, suspected Ukrainian sea drone"),
    (6, "Claimed proof of Riemann Hypothesis - Anthropic mathematician + Claude"),
    (7, "FBI fugitive 'El Chapo Isidro' arrested in Sinaloa, Mexico"),
    (8, "Bolsonaro in ICU with bowel obstruction"),
    (9, "South Korea annual exports pass $1 trillion for the first time"),
    (10, "Taiwan stocks swing 1,578 points intraday; TSMC +2%"),
    (11, "Drone strike kills 5 children in Khartoum and Omdurman, Sudan"),
    (12, "Paramilitary attack kills 24+ civilians in South Sudan"),
    (13, "Thousands protest in Istanbul against media takeover"),
    (14, "Five EU states accept deportation centres in Rwanda"),
    (15, "US Army to detonate unstable explosives in Iowa despite court order"),
    (16, "Gaza war leaves widespread contamination"),
    (17, "Fighting near Ebola area in Congo disrupts outbreak response"),
    (18, "FDA drug may cure hormonal hypertension"),
    (19, "Two leading French candidates question Ukraine aid"),
    (20, "Suspected Chinese hackers use AI 'Cairn' on East Asian universities"),
    (21, "Belgium airports shut as anti-austerity strike grounds flights"),
    (22, "Tata Steel buys $1.67B stake in top Indian steel pipe maker"),
    (23, "US energy exports hit record"),
    (24, "Trump holds third crypto gala amid conflict-of-interest scrutiny"),
    (25, "Mets sign Tarik Skubal for 9 years, $450M - record"),
    (26, "Verstappen wins Las Vegas GP"),
    (27, "Alcaraz wins first ATP Finals title, beats Zverev"),
    (28, "FIFA confirms England to host 2035 Women's World Cup"),
    (29, "Thitikul wins third straight LPGA title"),
    (30, "Red Wings trade captain Dylan Larkin to Canadiens"),
    (31, "Anthropic shares fall after record IPO"),
    (32, "Manchester Co-op Live Arena evacuated, suspected tear gas"),
]


def draw():
    # background + red accent strip
    rect(0, 0, W, H, BG)
    rect(0, 0, W, 10, RED)

    # header: the day, named loud
    draw_centered(W // 2, 22, "23 NOVEMBER 2026", 5, WHITE)
    draw_centered(W // 2, 66, "THE WORLD IN ONE IMAGE - 33 STORIES", 2, MUTED)
    rect(24, 90, 976, 2, RULE)

    # ---- hero: COP31 collapses ----
    # Hero subtext is three short lines, not one long line, so it stays readable at 300 px.
    rect(24, 100, 976, 152, PANEL)
    draw_centered(W // 2, 112, "CLIMATE - ANTALYA, TURKEY", 2, GOLD)
    draw_centered(W // 2, 134, "COP31 COLLAPSES", 7, WHITE)
    draw_centered(W // 2, 192,
                  "UN CLIMATE SUMMIT ENDS WITH NO DEAL - LONGEST COP EVER, FIRST SINCE 2009",
                  2, MUTED)
    draw_centered(W // 2, 212,
                  "EU + 130 NATIONS REJECT 'ANTALYA PACT' AS FOSSIL FUELS STRIPPED FROM TEXT",
                  2, MUTED)
    draw_centered(W // 2, 232,
                  "US ABSENT; 90+ NATIONS SIGN ELECTRIFICATION PLEDGE: 22% TO 35% BY 2035",
                  2, MUTED)

    # ---- 2x2 grid of large secondary stories ----
    grid_panel(24, 264, 472, 132, "MARKETS",
               ["AI SELL-OFF"],
               ["S&P -3.7%, NIKKEI -5.06%, KOSPI -5%",
                "GOLD +2.72%; US FUTURES REBOUND",
                "NASDAQ +3%, DOW +700 PTS"])
    grid_panel(528, 264, 472, 132, "DIPLOMACY",
               ["TRUMP-PUTIN-XI", "MEET IN SHENZHEN"],
               ["HISTORIC TRILATERAL IN SHENZHEN",
                "'DECLARATION TOWARD PEACE' ISSUED"])
    grid_panel(24, 408, 472, 132, "UKRAINE WAR",
               ["RUSSIA HITS", "KYIV REGION"],
               ["STRIKE ON DYMER VILLAGE: 10+ KILLED",
                "7-YEAR-OLD PULLED ALIVE FROM RUBBLE"])
    grid_panel(528, 408, 472, 132, "GULF",
               ["US SINKS 3", "IRAN TANKERS"],
               ["CAPTAIN LEON, TORKEL, ARINA HIT",
                "MISSILES FIRED AT 2 US WARSHIPS"])

    # ---- dense supporting list: stories 5-32 ----
    draw_text(24, 552, "MORE FROM 23 NOVEMBER 2026", 2, GOLD)
    y = 578
    for num, label in SUPPORTING:
        draw_text(24, y, "%02d." % num, 2, GOLD)
        draw_text(68, y, label, 2, WHITE)
        y += 15

    # footer
    draw_centered(W // 2, 1006, "ALL 33 STORIES FROM 23 NOVEMBER 2026", 1, MUTED)


# --------------------------------------------------------- png encoder --
def _chunk(typ, data):
    c = struct.pack(">I", len(data)) + typ + data
    c += struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)
    return c


def write_png(path, w, h, rgb):
    raw = bytearray()
    stride = w * 3
    for yy in range(h):
        raw.append(0)  # filter: none
        raw += rgb[yy * stride:(yy + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    png = b"\x89PNG\r\n\x1a\n"
    png += _chunk(b"IHDR", ihdr)
    png += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(png)
    return len(png)


def main():
    draw()
    os.makedirs("/output", exist_ok=True)
    n = write_png("/output/entry.png", W, H, buf)
    print("wrote /output/entry.png (%d bytes)" % n)


if __name__ == "__main__":
    main()
