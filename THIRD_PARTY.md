# Third-party code and pictures

The release (`sorcerers_maze.exe`) is built with the following open-source code.
The full licence texts are in the `licenses` folder of the release.

| Component | Licence | Used for |
|---|---|---|
| [Dear ImGui](https://github.com/ocornut/imgui) 1.92.9b | MIT | launcher, settings, pause menu |
| [libchdr](https://github.com/rtissera/libchdr) (commit 47d7941) | BSD-3-Clause | reading `.chd` disc images |
| – zstd 1.5.7 | BSD-3-Clause (chosen from GPLv2/BSD) | CHD decoding |
| – LZMA SDK 26.02 (LzmaDec only) | public domain | CHD decoding |
| – miniz 3.1.2 | MIT | CHD decoding (zlib) |
| – dr_flac | public domain / MIT-0 | CHD decoding (FLAC) |
| [stb_image](https://github.com/nothings/stb) 2.30 | public domain / MIT | the launcher's background (PNG) |

It is compiled with [llvm-mingw](https://github.com/mstorsjo/llvm-mingw)
(clang and mingw-w64) and built with [ninja](https://ninja-build.org/);
neither is part of the program. No font is shipped.

## Pictures

| Picture | Author | Licence | Source |
|---|---|---|---|
| `images/banner.webp` | Bits and Breakpoints (the banner of our projects) | © Bits and Breakpoints | – |
| `images/launcher.png`, `images/settings.png` | the port's launcher (its background is drawn by `source/tools/make_background.py`) | – | – |
| `images/pause-menu.png` | the port's pause menu over the game | the game's pictures are © their respective owners; shown for identification | – |
| `images/title.png`, `images/story.png`, `images/map.png`, `images/puzzle.png` | pictures of the game running in this port | the game's pictures are © their respective owners; shown for identification | – |
| `images/cover.jpg` | front cover of *Sorcerer's Maze (USA)*, SLUS-01495 | © its respective owners; shown for identification | [PSX Data Center](https://psxdatacenter.com/games/U/S/SLUS-01495.html) |

The game's own files (code, graphics, sound, text, data) are not included;
they are read from the player's own disc.
