#!/usr/bin/env python3
"""strip.py out.png a.png b.png ...: tile equally sized RGB PNGs (from ppm2png) horizontally."""
import struct, sys, zlib
def rd(p):
    d = open(p, "rb").read(); w, h = struct.unpack(">II", d[16:24])
    raw = b""; i = 8
    while i < len(d):
        n = struct.unpack(">I", d[i:i + 4])[0]; t = d[i + 4:i + 8]
        if t == b"IDAT": raw += d[i + 8:i + 8 + n]
        i += 12 + n
    raw = zlib.decompress(raw)
    return w, h, [raw[y * (w * 3 + 1) + 1:(y + 1) * (w * 3 + 1)] for y in range(h)]
ims = [rd(p) for p in sys.argv[2:]]
w, h = ims[0][0], ims[0][1]
rows = [b"\0" + b"".join(im[2][y] for im in ims) for y in range(h)]
def chunk(t, b): return struct.pack(">I", len(b)) + t + b + struct.pack(">I", zlib.crc32(t + b))
open(sys.argv[1], "wb").write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", w * len(ims), h, 8, 2, 0, 0, 0))
                              + chunk(b"IDAT", zlib.compress(b"".join(rows))) + chunk(b"IEND", b""))
