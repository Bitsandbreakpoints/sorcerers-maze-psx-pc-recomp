# Sorcerer's Maze: PC port (source)

A native Windows version of the PlayStation game *Sorcerer's Maze*
(SLUS-01495, XS Games, 2002). No emulator and no BIOS: the game's own MIPS
code is translated to C (static recompilation) and compiled for x86, and
Sony's libraries for graphics, CD-ROM, controllers, the memory card and
interrupts are replaced by PC code.

The game plays: the logos, title, the story, the world map, the puzzle
stages, the 2 player mode, HI SCORE and OPTIONS, with music and sound
effects, keyboard or XInput controllers (two players) and graphics at up to
4× the internal resolution, bilinear, CRT or soft-TV filters. F1 (or
Select+Start) pauses and opens a menu with the settings and Resume, Back to
launcher and Quit game; Tab fast-forwards and Esc goes back to the launcher.

## You need your own disc
Neither the source nor the program contains graphics, sound, text or other
data from the game. Everything is read from your own disc of *Sorcerer's
Maze (USA)* (`.chd`, `.bin`/`.cue` or `.iso`) while the game runs. Choose it
in the launcher with CHOOSE DISC or drop the file on the window; the
launcher checks that it is the release the port was made from.

The build needs the disc too: the code is translated from the disc's
program (`SLUS_014.95`), and the translated code only ever lands in
`build/`, never in the source.

## Building
Needs Windows 10/11 and Python 3.
```bat
build.bat --disc "D:\Games\Sorcerer's Maze (USA).chd"
```
The first time, the compiler (llvm-mingw) and ninja are downloaded to
`tools/` (SHA256-checked). The disc's path is remembered, so `build.bat` is
enough after that. The result is `build/sorcerers_maze.exe`. `run.bat`
builds and starts it; `build.bat --debug` makes a debug build. A disc image
named `Sorcerer*Maze*.chd` (or `.cue`, `.iso`) in this folder is found
without `--disc`.

A package for players: `python tools/package.py` makes
`build/package/sorcerers-maze-pc.zip` (exe, README.txt, licences), after
checking that the exe contains nothing from the disc.

## How it works
| Part | Where | What |
|---|---|---|
| Recompiler | `recomp/` | Python: MIPS R3000A + GTE → C, one C function per function of the game, jump tables as `switch` |
| Configuration | `recomp/config/main.cfg` | the program's SHA1, which of Sony's functions are replaced (`hle`), jump tables |
| Run-time | `src/runtime/` | CPU registers, memory, interrupts/VSync, the BIOS functions, the GPU/CD/controller/memory card replacements, the hardware registers of the sound |
| PS1 hardware in software | `src/psx/` | GPU (with a high-resolution copy), GTE, SPU |
| PC | `src/platform/`, `src/launcher/`, `src/disc/` | window, Direct3D 11, XInput, XAudio2, launcher, disc reader (bin/cue/chd/iso) |

The recompiler follows the code from the entry point: every `jal` target,
function pointers built with `lui`/`addiu` or stored in the data, and the
config's `func` lines. Delay slots run before the jump (the condition is
computed first), backward jumps check for interrupts, and jumps through a
register become a `switch` when their table is found (its entries are read
from PS1 memory at run time), otherwise a call by address.

The game's RAM lies at its own address (0x80000000) in a 32-bit process, so
a PS1 address is a plain pointer. Interrupts are taken where the code checks
for them (loops) and in VSync(); the game's callbacks run with the registers
saved around them. LIBGS, the sound libraries (LIBSND/LIBSPU) and the
game's own code run as recompiled code against a software GPU and an
emulated SPU. The controllers are read the way the BIOS does it
(InitPAD/StartPAD). The game starts the memory card library but never
saves, so the port has no memory card.

## Tests
None of the tests use the global keyboard, so the PC can be used while they
run.

- `python tests/play.py <name> <frames> "<buttons>" <frames…>`: a scripted
  run with a montage of pictures in `build/test/<name>/`.
- `python tests/compare_duckstation.py`: the same screens (title, world
  map) in the port and in the original game in DuckStation (put a portable
  DuckStation in `tools/emulator/duckstation` with a BIOS in its `bios`
  folder), with difference pictures.
- `python tests/window_shot.py build/test/launcher.png`: the launcher's
  window.

Debugging with environment variables: `SM_AUTOSTART=1`, `SM_QUIT=1`,
`SM_INPUT=<frame>[-<last>]:<button>,…`, `SM_LEAVE=<frame>`,
`SM_VRAM_DUMP=<frame>,…`, `SM_WAV_DUMP=<file>`, `SM_MUTE=1`, `SM_NATIVE=1`,
`SM_FAST=1`, `SM_SPU_TRACE=1` (see `src/main_pc.cpp`).

See `THIRD_PARTY.md` for the licences.
