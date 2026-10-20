#!/usr/bin/env python3
"""Draws the launcher's background (assets/launcher/background.png): a
glowing circular maze, like a sorcerer's sigil, with magic orbs and a
crystal star in the middle, in the port's own style.  Our own picture,
made by this script (no photo, nothing from the game).

    python tools/make_background.py
"""
import math
import os
import random
import struct
import zlib

W, H = 1600, 960
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets', 'launcher',
                   'background.png')

# the maze: centre, rings
CX, CY = 1100, 480
RINGS = 7
R0, STEP = 70, 54
WALL = 3.2
GOLD = (255, 196, 92)
GLOW = (255, 150, 60)


def smooth(edge0, edge1, x):
    t = max(0.0, min(1.0, (x - edge0) / (edge1 - edge0)))
    return t * t * (3 - 2 * t)


def mix(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def make_maze():
    """A random circular maze: for each ring, the angles of its gaps; for
    each band between rings, the angles of its radial walls."""
    rnd = random.Random(1495)
    gaps, spokes = [], []
    for k in range(RINGS):
        n = 1 if k in (0, RINGS - 1) else rnd.randint(2, 3)
        gaps.append([rnd.uniform(0, 2 * math.pi) for _ in range(n)])
    for k in range(RINGS - 1):
        n = 3 + k
        base = rnd.uniform(0, 2 * math.pi)
        spokes.append([base + 2 * math.pi * (i + rnd.uniform(-0.25, 0.25)) / n for i in range(n)])
    return gaps, spokes


GAPS, SPOKES = make_maze()
GAP_LEN = 30.0          # pixels of arc


def angle_diff(a, b):
    d = (a - b) % (2 * math.pi)
    return min(d, 2 * math.pi - d)


def maze_distance(px, py):
    """distance to the nearest wall of the maze"""
    r = math.hypot(px, py)
    a = math.atan2(py, px)
    best = 1e9
    for k in range(RINGS):
        rk = R0 + STEP * k
        d = abs(r - rk)
        if d < best:
            in_gap = any(angle_diff(a, g) * rk < GAP_LEN / 2 for g in GAPS[k])
            if in_gap:
                # the gap's end caps
                for g in GAPS[k]:
                    for s in (-1, 1):
                        ea = g + s * GAP_LEN / 2 / rk
                        d = min(d if not in_gap else 1e9,
                                math.hypot(px - rk * math.cos(ea), py - rk * math.sin(ea)))
                        best = min(best, d)
            else:
                best = min(best, d)
    for k in range(RINGS - 1):
        r1, r2 = R0 + STEP * k, R0 + STEP * (k + 1)
        for s in SPOKES[k]:
            ux, uy = math.cos(s), math.sin(s)
            t = max(r1, min(r2, px * ux + py * uy))
            best = min(best, math.hypot(px - t * ux, py - t * uy))
    return best


# glowing orbs in the corridors: (ring band, angle, colour)
ORBS = [(1, 0.6, (90, 170, 255)), (3, 2.4, (120, 235, 140)), (4, -0.9, (255, 110, 200)),
        (5, 1.7, (90, 170, 255)), (2, -2.2, (255, 220, 110)), (5, -2.6, (120, 235, 140))]


def star_field(x, y):
    """small twinkling stars of the night sky"""
    cell = 23
    gx, gy = int(x // cell), int(y // cell)
    h = (gx * 73856093 ^ gy * 19349663) & 0xFFFFFF
    if h % 7:
        return 0.0
    sx = gx * cell + (h % cell)
    sy = gy * cell + ((h >> 8) % cell)
    d = math.hypot(x - sx, y - sy)
    return (0.4 + 0.6 * ((h >> 16) % 100) / 100) * math.exp(-d * d / 1.6)


def pixel(x, y):
    px, py = x - CX, y - CY
    r = math.hypot(px, py)
    # the night: deep violet, lighter around the maze
    c = mix((58, 26, 96), (7, 4, 20), smooth(0.0, 1.0, math.hypot(px / 950, py / 700)))
    c = mix(c, (230, 220, 255), 0.8 * star_field(x, y) * smooth(300, 520, r))
    outer = R0 + STEP * (RINGS - 1)
    # a soft disc of light under the maze
    c = mix(c, (90, 40, 130), 0.45 * (1 - smooth(outer - 40, outer + 90, r)))
    # the walls: gold with a warm glow
    if r < outer + 60:
        d = maze_distance(px, py)
        c = mix(c, GLOW, 0.45 * math.exp(-max(0.0, d - WALL) / 9))
        wall = mix(GOLD, (255, 245, 210), 0.5 * (1 - smooth(0, WALL, d)))
        c = mix(c, wall, 1 - smooth(WALL - 1.0, WALL + 1.0, d))
    # the orbs
    for band, ang, col in ORBS:
        rr = R0 + STEP * (band + 0.5)
        ox, oy = rr * math.cos(ang), rr * math.sin(ang)
        d = math.hypot(px - ox, py - oy)
        rad = 15
        c = mix(c, col, 0.55 * math.exp(-max(0.0, d - rad) / 12))
        body = mix(col, (255, 255, 255), 0.75 * (1 - smooth(0, rad, math.hypot(px - ox + 5, py - oy + 5))))
        c = mix(c, body, 1 - smooth(rad - 1.2, rad + 1.2, d))
    # the crystal star in the middle: eight points, icy blue-white
    a = math.atan2(py, px)
    spike = 0.25 + 0.75 * abs(math.cos(4 * a)) ** 6
    star_r = 46 * spike
    c = mix(c, (120, 220, 255), 0.6 * math.exp(-max(0.0, r - star_r) / 20))
    core = mix((150, 230, 255), (255, 255, 255), 1 - smooth(0, star_r, r))
    c = mix(c, core, 1 - smooth(star_r - 1.5, star_r + 1.5, r))
    # long sparkle rays
    for k in range(4):
        ra = k * math.pi / 2 + math.pi / 4
        along = px * math.cos(ra) + py * math.sin(ra)
        across = -px * math.sin(ra) + py * math.cos(ra)
        c = mix(c, (200, 240, 255), 0.5 * math.exp(-abs(across) / 1.6) * math.exp(-abs(along) / 160))
    # left side darker for the menu
    c = mix(c, (5, 3, 14), 0.68 * (1 - smooth(0, 720, x)))
    return c


def main():
    rows = []
    for y in range(H):
        row = bytearray([0])
        for x in range(W):
            r, g, b = pixel(x + 0.5, y + 0.5)
            row += bytes((int(max(0, min(255, r))), int(max(0, min(255, g))), int(max(0, min(255, b)))))
        rows.append(bytes(row))
    raw = b''.join(rows)

    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))

    png = b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', W, H, 8, 2, 0, 0, 0))
    png += chunk(b'IDAT', zlib.compress(raw, 9)) + chunk(b'IEND', b'')
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, 'wb').write(png)
    print(f'wrote {OUT}')


if __name__ == '__main__':
    main()
