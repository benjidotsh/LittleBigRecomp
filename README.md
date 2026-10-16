# LittleBigRecomp

A static recompilation of **LittleBigPlanet** (PS3, BCES00141, disc v02.00) to a
native macOS arm64 executable. The game's PowerPC code is lifted to C++ ahead of
time and linked against the [ps3recomp](https://github.com/sp00nznet/ps3recomp)
runtime (vendored in `ps3recomp/`, upstream commit `0fe7dbf`), which supplies
the LV2 kernel, HLE system libraries, SPU runtime and the Metal RSX backend.

No game code, assets or keys are in this repository.

## Building

Needs Xcode clang, CMake, Ninja, Python 3.10+ (`pip install -r ps3recomp/requirements.txt`)
and SDL2 (`brew install sdl2`).

1. Point `vfs` at the extracted disc (the directory holding `PS3_GAME/`) and
   put the decrypted EBOOT at `game/EBOOT.elf`:

   ```sh
   ln -s "/path/to/LittleBigPlanet disc" vfs
   mkdir -p game && cp vfs/PS3_GAME/USRDIR/EBOOT.elf game/EBOOT.elf
   ```

2. Lift and build:

   ```sh
   PYTHON=/path/to/python3 tools/relift.sh
   cmake -S . -B build -G Ninja && cmake --build build
   ```

3. Run:

   ```sh
   ./build/LittleBigRecomp vfs/PS3_GAME/USRDIR/EBOOT.elf
   ```
