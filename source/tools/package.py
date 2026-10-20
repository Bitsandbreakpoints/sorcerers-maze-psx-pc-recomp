#!/usr/bin/env python3
"""Packs the PC port for players: build/package/sorcerers-maze-pc.zip.

    python tools/package.py [--scan-only]

The zip holds sorcerers_maze.exe, the player's README (README.txt) and the
licences of the third-party code built into the exe.  It never holds
anything from the game's disc: before packing, the exe is searched for
every 64-byte block (that is not mostly one repeated value) of the disc's
files - the executable in build/disc/ and, if they are there, all
files in orig/files/ - at every offset.  Any hit stops the packing.
(The exe contains the executable's code translated to x86, but none of
its bytes: data and tables are read from the disc when the game runs.)
Settings and logs from test runs never go in (only the files listed here
are packed).
"""
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = os.path.join(HERE, 'build', 'sorcerers_maze.exe')
OUT_DIR = os.path.join(HERE, 'build', 'package')
ZIP_NAME = 'sorcerers-maze-pc.zip'
FOLDER = 'Sorcerers Maze PC'

BLOCK = 64
MIN_DISTINCT_BYTES = 12        # skip blocks that are mostly one value (zeros, padding)
DISC_DIRS = ['build/disc', 'orig/files']

# licence files: (name in the zip, source, None or the text a licence
# block at the end of a single-file library starts with)
LICENSES = [
    ('imgui.txt', 'third_party/imgui/LICENSE.txt', None),
    ('libchdr.txt', 'third_party/libchdr/LICENSE.txt', None),
    ('zstd.txt', 'third_party/libchdr/deps/zstd-1.5.7/LICENSE', None),
    ('lzma.txt', 'third_party/libchdr/deps/lzma-26.02/LICENSE', None),
    ('miniz.txt', 'third_party/libchdr/deps/miniz-3.1.2/miniz.c', 'Copyright 2013-2014 RAD'),
    ('dr_flac.txt', 'third_party/libchdr/include/dr_libs/dr_flac.h', 'This software is available as a choice'),
    ('stb_image.txt', 'third_party/stb/stb_image.h', 'This software is available under 2 licenses'),
]

README = """Sorcerer's Maze - PC port
==========================

A native Windows version of the PlayStation game Sorcerer's Maze (2002,
XS Games), made by recompiling the game's own code.
It contains no graphics, sound, text or other files from the game: you
need your own copy of the disc (Sorcerer's Maze (USA), SLUS-01495) as a disc
image.

How to play
-----------
1. Make an image of your own disc, e.g. "Sorcerer's Maze (USA).bin" + ".cue",
   or a .chd or .iso.
2. Start sorcerers_maze.exe and choose CHOOSE DISC (or drop the image on the
   window). The image is checked against the release the port was made
   from.
3. Choose PLAY.

In the game: Esc goes back to the launcher, F1 (or Select+Start on the
controller) pauses and shows the settings with Resume, Back to launcher and
Quit game, and holding Tab fast-forwards.

Controls (keyboard and XInput controllers, two players), graphics
(internal resolution up to 4x, precise vertices, picture filters such as
CRT, full screen) and sound are set under SETTINGS. The settings are kept
in settings.ini next to the program. No BIOS is needed.

Requires Windows 10 or later.

The licences of the third-party code are in the "licenses" folder.
Sorcerer's Maze is a trademark of its owner; this project is not affiliated
with XS Games, Dcruise, Siesta, Four Winds or Sony.
"""


def read(path):
    with open(path, 'rb') as f:
        return f.read()


def scan(exe):
    """[(file, offset, exe offset)] of blocks of disc files found in the exe."""
    files = []
    for d in DISC_DIRS:
        for dirpath, _, names in os.walk(os.path.join(HERE, d)):
            files += [os.path.join(dirpath, n) for n in names if n != 'ZZZ.ZZZ']
    blocks = {}
    for path in files:
        data = read(path)
        for offset in range(0, len(data) - BLOCK + 1, BLOCK):
            block = data[offset:offset + BLOCK]
            if len(set(block)) >= MIN_DISTINCT_BYTES:
                blocks.setdefault(block[:8], {}).setdefault(block, (path, offset))
    print(f'scan: {sum(len(v) for v in blocks.values())} blocks of {len(files)} disc files')
    hits = []
    for i in range(len(exe) - BLOCK + 1):
        candidates = blocks.get(exe[i:i + 8])
        if candidates:
            found = candidates.get(exe[i:i + BLOCK])
            if found:
                hits.append((found[0], found[1], i))
    return hits


def license_text(source, start):
    text = read(os.path.join(HERE, source)).decode('utf-8', 'replace')
    if start:
        text = text[text.index(start):]
    return text


def main():
    exe = read(EXE)
    hits = scan(exe)
    for path, offset, at in hits[:20]:
        print(f'  {os.path.relpath(path, HERE)} +{offset:#x} found at exe offset {at:#x}')
    if hits:
        sys.exit(f'{len(hits)} blocks of disc files are in the exe: not packed')
    print('scan: nothing from the disc in the exe')
    if '--scan-only' in sys.argv:
        return
    os.makedirs(OUT_DIR, exist_ok=True)
    out = os.path.join(OUT_DIR, ZIP_NAME)
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr(f'{FOLDER}/sorcerers_maze.exe', exe)
        z.writestr(f'{FOLDER}/README.txt', README.replace('\n', '\r\n'))
        z.writestr(f'{FOLDER}/licenses/THIRD_PARTY.md', read(os.path.join(HERE, 'THIRD_PARTY.md')))
        for name, source, start in LICENSES:
            z.writestr(f'{FOLDER}/licenses/{name}', license_text(source, start))
    print(f'{out} ({os.path.getsize(out) // 1024} KB)')


if __name__ == '__main__':
    main()
