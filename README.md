# LittleBigRecomp

A static recompilation of **LittleBigPlanet** (PS3, BCES00141, disc v02.00) to a
native macOS arm64 executable. The game's PowerPC code is lifted to C++ ahead of
time, and so is every SPU program it runs (FMOD, Bink, the WWS physics/job
manager policy module and its 43 job modules, a voice-codec job). Everything is
linked against the [ps3recomp](https://github.com/sp00nznet/ps3recomp) runtime,
a git submodule in `ps3recomp/` tracking the `lbp` branch of
[benjidotsh/ps3recomp](https://github.com/benjidotsh/ps3recomp) (upstream
`0fe7dbf`, MIT, plus the fixes this port needed). Clone with
`git clone --recursive`, or run `git submodule update --init`. Rendering goes through Metal.

No game code, assets, keys or game-derived output are in this repository.

## Status

Boots on an Apple-silicon Mac through the first-boot save creation, the
"Important Information" notice, the logos and intro movie (Bink, decoded by the
recompiled SPU code), and loads **the first level, the Introduction**, where the
game is live: it renders the level and answers the pad (START opens the
in-level pause menu).

Known limits: the Introduction shows magenta placeholder textures for its
first ~20 s while textures stream in, an occasional frame flashes a bright
wedge, and depth/stencil clears ignore the scissor. In-level the game holds
its 30 fps target. FMOD's runtime-relocated DSP plugins run through the SPU
interpreter.

## Building

Needs Xcode clang, CMake, Ninja, Python 3.10+ with `pip install -r ps3recomp/requirements.txt`,
and SDL2 (`brew install sdl2`).

1. Extract the disc ISO and put the decrypted EBOOT in place:

   ```sh
   python3 tools/extract_iso.py "/path/to/LittleBigPlanet.iso" disc
   mkdir -p game && cp /path/to/decrypted/EBOOT.elf game/EBOOT.elf
   ```

   Use a fresh extraction: a pre-extracted copy this port was first tried on
   had 73 corrupt files (among them `output/blurayguids.map`, which breaks
   resource loading).

2. Lift and build:

   ```sh
   PYTHON=/path/to/python3 tools/relift.sh      # PPU + SPU lift, NID table
   cmake -S . -B build -G Ninja && cmake --build build
   ```

3. Run:

   ```sh
   ./run.sh
   ```

   Guest writes (HDD install data, cache, saves) go to `hdd/`; the disc copy
   stays read-only. `PAD_FILE=<file>` drives the pad from a file (write a
   button mask such as `0x4000` for CROSS, `0x0008` for START);
   `tools/autorun.sh <seconds> <log>` runs headless-style and skips the
   intro movie.

## Debugging aids added by this port

- `FN_PROBE=<addr,...>` logs entry/return of guest functions;
  `FN_PROBE_REGS=1` adds all GPRs. `FN_TRACE_AT=<s>` / `FN_TRACE_EXIT=1` write
  each thread's last 64K function entries. `FN_DUMP_AT=<fn>[:n]` /
  `FN_DUMP_SEC=<s>` dump guest memory for `tools/memrd.py`.
- `SPURS_KTRACE=1`, `SPU_TAGSTUCK=1`, `SPU_SNTRACE=1`, `RSX_TEX_LOG/RSX_TEX_DUMP`,
  `RSX_ZSAMPLE_LOG`, `PS3RECOMP_METAL_FRAME_DUMP=dir/f%05u.ppm`.
- `tools/ppcdis.py`, `tools/fnstrings.py`, `tools/peek.sh` (tile frame dumps).
