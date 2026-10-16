#!/usr/bin/env python3
"""ppm2png.py <in.ppm> [out.png] [scale]: P6 -> PNG (optionally downscaled by an int factor)."""
import struct, sys, zlib
src = sys.argv[1]; dst = sys.argv[2] if len(sys.argv) > 2 else src[:-4] + ".png"
k = int(sys.argv[3]) if len(sys.argv) > 3 else 1
d = open(src, "rb").read()
parts = d.split(maxsplit=4); w, h = int(parts[1]), int(parts[2]); px = parts[4]
rows = []
for y in range(0, h, k):
    r = px[y * w * 3:(y + 1) * w * 3]
    rows.append(b"\0" + (r if k == 1 else b"".join(r[x * 3:x * 3 + 3] for x in range(0, w, k))))
W, H = (w + k - 1) // k, (h + k - 1) // k
def chunk(t, b): return struct.pack(">I", len(b)) + t + b + struct.pack(">I", zlib.crc32(t + b))
open(dst, "wb").write(b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
                      + chunk(b"IDAT", zlib.compress(b"".join(rows))) + chunk(b"IEND", b""))
