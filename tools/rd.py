"""Tiny static reader for the EBOOT image: import and call r32(addr)."""
import struct
d = open("game/EBOOT.elf", "rb").read()
ph = struct.unpack_from(">Q", d, 0x20)[0]
segs = []
for i in range(struct.unpack_from(">H", d, 0x38)[0]):
    t, f, off, va, pa, fs, ms, al = struct.unpack_from(">IIQQQQQQ", d, ph + i * 56)
    if t == 1: segs.append((va, off, fs, ms))
def r32(a):
    for va, off, fs, ms in segs:
        if va <= a < va + fs: return struct.unpack_from(">I", d, off + a - va)[0]
        if va <= a < va + ms: return 0
    raise KeyError(hex(a))
def cstr(a):
    s = b""
    while True:
        for va, off, fs, ms in segs:
            if va <= a < va + fs: c = d[off + a - va]; break
        else: return s.decode(errors="replace")
        if c == 0: return s.decode(errors="replace")
        s += bytes([c]); a += 1
