#!/bin/sh
# Regenerate everything git-ignored from the decrypted EBOOT: the import list,
# the function list, the lifted PPU tree and the HLE NID table.
# Run from the repo root with game/EBOOT.elf in place (see README).
set -e
PY="${PYTHON:-python3}"
T=ps3recomp/tools

# .text ends where the .lib.stub import trampolines end (0x83D1C4 + 307*0x20);
# everything above in the R-X segment is .rodata.
CODE_END=0x83F824

mkdir -p analysis
"$PY" "$T/ppu_loader.py" game/EBOOT.elf -o analysis/
"$PY" "$T/gen_imports.py" game/EBOOT.elf -o analysis/imports.json
"$PY" "$T/find_functions.py" game/EBOOT.elf \
    --seed-json analysis/EBOOT.functions.json --output analysis/functions.json

rm -rf src/recomp src/gen && mkdir -p src/recomp src/gen
"$PY" "$T/ppu_lifter.py" game/EBOOT.elf \
    --functions analysis/functions.json \
    --hle-stubs analysis/imports.json \
    --code-end "$CODE_END" --chunks 48 \
    -o src/recomp
"$PY" "$T/gen_hle_nids.py" --all --out src/gen/ppu_hle_nids.cpp
