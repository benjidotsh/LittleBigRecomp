#!/usr/bin/env python3
"""Extract a (decrypted) PS3 disc ISO with original file-name case (Joliet).
extract_iso.py <iso> <outdir>"""
import os, struct, sys
S = 2048
def joliet_root(f):
    for s in range(17, 32):
        f.seek(s * S); v = f.read(S)
        if v[0] == 255: break
        if v[0] == 2 and v[88:91] in (b"%/@", b"%/C", b"%/E"):
            r = v[156:190]
            return struct.unpack_from("<I", r, 2)[0], struct.unpack_from("<I", r, 10)[0]
    raise SystemExit("no Joliet descriptor")
def walk(f, lba, size, out):
    f.seek(lba * S); d = f.read(size); o = 0
    pending = {}
    while o < len(d):
        l = d[o]
        if l == 0: o = (o // S + 1) * S; continue
        ext = struct.unpack_from("<I", d, o + 2)[0]; ln = struct.unpack_from("<I", d, o + 10)[0]
        flags = d[o + 25]; nl = d[o + 32]; raw = d[o + 33:o + 33 + nl]; o += l
        if raw in (b"\0", b"\1"): continue
        name = raw.decode("utf-16-be").split(";")[0]
        path = os.path.join(out, name)
        if flags & 2:
            os.makedirs(path, exist_ok=True); walk(f, ext, ln, path); continue
        # multi-extent files: flag 0x80 means more extents follow under the same name
        pending.setdefault(path, []).append((ext, ln))
        if flags & 0x80: continue
        with open(path, "wb") as w:
            for e, n in pending.pop(path):
                f.seek(e * S)
                while n:
                    c = f.read(min(n, 1 << 24)); w.write(c); n -= len(c)
f = open(sys.argv[1], "rb"); os.makedirs(sys.argv[2], exist_ok=True)
walk(f, *joliet_root(f), sys.argv[2])
