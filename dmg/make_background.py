#!/usr/bin/env python3
"""Draws the Stems DMG background as pixel art.

Everything is drawn on a small logical canvas and scaled up with
nearest-neighbour, so the pixels stay crisp at 1x and 2x (Retina).

    python3 dmg/make_background.py [--theme dark|light]

Writes dmg/background.png (2560x1600) and dmg/background@2x.png (5120x3200).
Needs Pillow.
"""
import argparse
import random
from pathlib import Path

from PIL import Image

W, H = 165, 100           # logical design area; x4 = 660x400, the art inside the window
# Finder ignores the requested window size when the viewer's settings (path bar, tab bar) need more room,
# and paints white past the image. So the image is far bigger than any window: the design sits top left
# and the night, ground and garden carry on to the right and below.
CW, CH = 640, 400         # logical canvas; x4 = 2560x1600
OUT = Path(__file__).parent

# Where Finder will place the icons, in logical pixels (keep in sync with
# make-dmg.sh: window-coords / 4).
APP_X, DROP_X, ICON_Y = 41, 124, 47
# Finder draws the icon labels here, in black in Light Mode and white in Dark Mode; a DMG can't change
# that. So each label sits on a mid-grey plate that both colours read on at about 4.5:1.
# (centre x, half width) per label, and the plate's rows.
PLATES = [(APP_X, 9), (DROP_X, 13)]
PLATE_TOP, PLATE_BOTTOM = 65, 70
PLATE = "#77777a"

PALETTES = {
    "dark": dict(
        bg="#1b1b1d", star="#27272a", text="#d8d8dc",
        ground=["#2a2a2d", "#353538", "#232326", "#3a3a3d"],
        green="#4a9e2e", green_hi="#6cc04a", green_dk="#2f6f1c",
    ),
    "light": dict(
        bg="#f1e9d6", star="#e6dcc4", text="#3a3a3f",
        ground=["#d9cfb8", "#cfc4aa", "#e0d6bf", "#c6bba0"],
        green="#3f8f2a", green_hi="#62b043", green_dk="#2a6a1a",
    ),
}
FLOWER = dict(orange="#f0a030", red="#e0506a", blue="#2f6fe0", purple="#9a55d0",
              pink="#f4a6b4", sand="#f6d9a0")

# 5x7 pixel font, only the letters we use.
FONT = {
    "D": ["XXXX.", "X...X", "X...X", "X...X", "X...X", "X...X", "XXXX."],
    "R": ["XXXX.", "X...X", "X...X", "XXXX.", "X.X..", "X..X.", "X...X"],
    "A": [".XXX.", "X...X", "X...X", "XXXXX", "X...X", "X...X", "X...X"],
    "G": [".XXXX", "X....", "X....", "X.XXX", "X...X", "X...X", ".XXX."],
    "T": ["XXXXX", "..X..", "..X..", "..X..", "..X..", "..X..", "..X.."],
    "O": [".XXX.", "X...X", "X...X", "X...X", "X...X", "X...X", ".XXX."],
    "I": ["XXX", ".X.", ".X.", ".X.", ".X.", ".X.", "XXX"],
    "N": ["X...X", "XX..X", "X.X.X", "X.X.X", "X..XX", "X...X", "X...X"],
    "S": [".XXXX", "X....", "X....", ".XXX.", "....X", "....X", "XXXX."],
    "L": ["X....", "X....", "X....", "X....", "X....", "X....", "XXXXX"],
    " ": ["..", "..", "..", "..", "..", "..", ".."],
}

# 3-wide flower heads: '.' empty, letters map to colours given at draw time.
HEADS = {
    "red":    (["." "A" ".", "ABA", "." "A" "."], dict(A="red", B="pink")),
    "orange": (["AAA", "ABA", "AAA"], dict(A="orange", B="sand")),
    "blue":   (["." "A" ".", "AAA", "." "A" ".", "." "A" "."], dict(A="blue")),
    "purple": (["A.A", "AAA", "ABA"], dict(A="purple", B="pink")),
}


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (255,)


def build(theme):
    pal = PALETTES[theme]
    img = Image.new("RGBA", (CW, CH), hex_rgb(pal["bg"]))
    px = img.load()

    def put(x, y, colour):
        if 0 <= x < CW and 0 <= y < CH:
            px[x, y] = hex_rgb(colour)

    def colour_of(name):
        return FLOWER.get(name) or pal[name]

    # --- faint stars, kept clear of the icons, arrow and heading -------------
    rng = random.Random(7)
    keep_out = [(APP_X - 20, 26, APP_X + 20, 80), (DROP_X - 20, 26, DROP_X + 20, 80),
                (60, 38, 106, 56), (30, 4, 135, 20)]
    placed = 0
    while placed < 45:
        x, y = rng.randrange(1, W - 1), rng.randrange(1, H - 12)
        if any(a <= x <= c and b <= y <= d for a, b, c, d in keep_out):
            continue
        put(x, y, pal["star"])
        placed += 1
    # The same density of stars over the rest of the sky.
    while placed < 45 * (CW * (H - 12)) // (W * (H - 12)):
        x, y = rng.randrange(W, CW), rng.randrange(1, H - 12)
        put(x, y, pal["star"])
        placed += 1

    # --- ground: dithered strip like the base under the app icon ------------
    for x in range(CW):
        for y in range(H - 3, H):
            put(x, y, pal["ground"][(x * 3 + y * 5 + (x // 3)) % len(pal["ground"])])
    # Below the window's bottom edge: soil, sparse specks that thin out with depth.
    for y in range(H, CH):
        for x in range(CW):
            if rng.random() < 0.10 * max(0.15, 1 - (y - H) / 40):
                put(x, y, pal["ground"][(x + y) % len(pal["ground"])])

    # --- little garden: stems with the four flower types --------------------
    garden = [(9, "orange", 8), (19, "purple", 5), (30, "red", 7), (143, "blue", 8),
              (153, "orange", 5), (160, "purple", 6), (14, "blue", 4), (148, "red", 4),
              (24, "red", 3), (136, "purple", 3), (90, "orange", 3), (76, "blue", 3),
              (103, "red", 2), (64, "purple", 2)]
    # More of the garden to the right, in loose clumps.
    x = W + rng.randrange(4, 12)
    while x < CW - 2:
        garden.append((x, rng.choice(list(HEADS)), rng.choice([2, 3, 3, 4, 5, 6, 7, 8])))
        x += rng.choice([4, 5, 6, 7, 14, 22, 30])
    for x, kind, height in garden:
        top = H - 4 - height
        for y in range(top, H - 3):
            put(x, y, pal["green"])
        put(x - 1, top + height // 2, pal["green_dk"])     # leaf
        put(x + 1, top + height // 2 + 1, pal["green_dk"])
        rows, keys = HEADS[kind]
        hw = len(rows[0])
        for ry, row in enumerate(rows):
            for rx, ch in enumerate(row):
                if ch != ".":
                    put(x - hw // 2 + rx, top - len(rows) + ry, colour_of(keys[ch]))

    # --- label plates, corners clipped --------------------------------------
    for cx, half in PLATES:
        for y in range(PLATE_TOP, PLATE_BOTTOM + 1):
            inset = 1 if y in (PLATE_TOP, PLATE_BOTTOM) else 0
            for x in range(cx - half + inset, cx + half + 1 - inset):
                put(x, y, PLATE)

    # --- heading ------------------------------------------------------------
    text = "DRAG TO INSTALL"
    total = sum(len(FONT[c][0]) + 1 for c in text) - 1
    cx = (W - total) // 2
    for c in text:
        glyph = FONT[c]
        for gy, row in enumerate(glyph):
            for gx, ch in enumerate(row):
                if ch == "X":
                    put(cx + gx, 9 + gy, pal["text"])
        cx += len(glyph[0]) + 1

    # --- arrow: dashes in the four flower colours, green head ---------------
    cols = ["orange", "red", "blue", "purple"]
    x, i = 64, 0
    while x + 4 <= 93:
        for dx in range(4):
            for dy in (-1, 0, 1):
                put(x + dx, ICON_Y + dy, FLOWER[cols[i % 4]])
        x += 6
        i += 1
    for col in range(7):                                  # head, tip on the right
        half = 6 - col
        for y in range(ICON_Y - half, ICON_Y + half + 1):
            put(95 + col, y, pal["green_hi"] if y == ICON_Y - half else pal["green"])
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--theme", choices=PALETTES, default="dark")
    theme = ap.parse_args().theme
    img = build(theme)
    img.resize((CW * 4, CH * 4), Image.NEAREST).convert("RGB").save(OUT / "background.png", optimize=True)
    img.resize((CW * 8, CH * 8), Image.NEAREST).convert("RGB").save(OUT / "background@2x.png", optimize=True)
    print(f"wrote {OUT/'background.png'} and background@2x.png ({theme})")


if __name__ == "__main__":
    main()
