#!/usr/bin/env python3
"""Disassemble guest PPU code: ppcdis.py <addr> [count] [elf]."""
import struct, sys
from capstone import Cs, CS_ARCH_PPC, CS_MODE_64, CS_MODE_BIG_ENDIAN
addr = int(sys.argv[1], 16); n = int(sys.argv[2]) if len(sys.argv) > 2 else 64
d = open(sys.argv[3] if len(sys.argv) > 3 else "game/EBOOT.elf", "rb").read()
ph = struct.unpack_from(">Q", d, 0x20)[0]
for i in range(struct.unpack_from(">H", d, 0x38)[0]):
    t, f, off, va, pa, fs, ms, al = struct.unpack_from(">IIQQQQQQ", d, ph + i * 56)
    if t == 1 and va <= addr < va + fs:
        code = d[off + addr - va: off + addr - va + 4 * n]
        break
else:
    sys.exit("address not in a loaded segment")
md = Cs(CS_ARCH_PPC, CS_MODE_64 | CS_MODE_BIG_ENDIAN)
for off in range(0, len(code) - 3, 4):
    ins = next(md.disasm(code[off:off + 4], addr + off), None)
    if ins: print(f"{addr + off:08X}  {ins.mnemonic:8} {ins.op_str}")
    else:   print(f"{addr + off:08X}  .long    0x{int.from_bytes(code[off:off+4], 'big'):08X}")
