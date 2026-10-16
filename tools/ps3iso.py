#!/usr/bin/env python3
"""Minimal PS3 disc ISO reader: region map + ISO9660 file lookup.
ps3iso.py <iso> regions | ls <dir> | find <path>"""
import struct, sys
S = 2048
def regions(f):
    f.seek(0); h = f.read(S)
    n = struct.unpack_from(">I", h, 0)[0]
    pts = [struct.unpack_from(">I", h, 8 + 4 * i)[0] for i in range(n * 2)]
    return n, pts
def dirents(f, lba, size):
    f.seek(lba * S); d = f.read(size); o = 0; out = []
    while o < len(d):
        l = d[o]
        if l == 0: o = (o // S + 1) * S; continue
        ext, ln = struct.unpack_from("<I", d, o + 2)[0], struct.unpack_from("<I", d, o + 10)[0]
        nl = d[o + 32]; name = d[o + 33:o + 33 + nl].decode(errors="replace")
        out.append((name, ext, ln, d[o + 25] & 2)); o += l
    return out
def root(f):
    f.seek(16 * S); p = f.read(S); r = p[156:156 + 34]
    return struct.unpack_from("<I", r, 2)[0], struct.unpack_from("<I", r, 10)[0]
def find(f, path):
    lba, size = root(f)
    for part in [p for p in path.upper().split("/") if p]:
        for name, ext, ln, isdir in dirents(f, lba, size):
            if name.split(";")[0] == part: lba, size = ext, ln; break
        else: raise FileNotFoundError(path)
    return lba, size
if __name__ == "__main__":
    f = open(sys.argv[1], "rb"); cmd = sys.argv[2]
    if cmd == "regions":
        n, pts = regions(f); print(n, "regions:", [(hex(pts[i]), hex(pts[i+1])) for i in range(0, len(pts), 2)])
    elif cmd == "ls":
        lba, size = find(f, sys.argv[3])
        for e in dirents(f, lba, size): print(e)
    elif cmd == "find":
        print(find(f, sys.argv[3]))
