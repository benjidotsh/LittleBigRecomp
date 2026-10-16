#!/usr/bin/env python3
"""fnstrings.py <lo> <hi> [toc]: strings loaded through the TOC by code in [lo,hi)."""
import re, sys, os
sys.path.insert(0, os.path.dirname(__file__)); import rd
lo, hi = int(sys.argv[1], 16), int(sys.argv[2], 16)
toc = int(sys.argv[3], 16) if len(sys.argv) > 3 else 0x96c1f0
seen = set()
for line in open("run/dis_all.txt"):
    a = int(line[:8], 16)
    if not lo <= a < hi: continue
    m = re.search(r"lwz +r\d+, (-?0x[0-9a-f]+|-?\d+)\(r2\)", line)
    if not m: continue
    off = int(m.group(1), 0)
    try: s = rd.cstr(rd.r32(toc + off))
    except Exception: continue
    if len(s) >= 4 and s.isprintable() and s not in seen:
        seen.add(s); print(f"{a:08X} {s[:100]!r}")
