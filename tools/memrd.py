"""Read a runtime memory dump (run/memdump_*.bin) falling back to the ELF image."""
import glob, os, struct, sys
sys.path.insert(0, os.path.dirname(__file__))
import rd
dumps = []
for f in glob.glob("run/memdump_*.bin"):
    lo = int(os.path.basename(f)[8:16], 16)
    dumps.append((lo, open(f, "rb").read()))
def r32(a):
    for lo, b in dumps:
        if lo <= a < lo + len(b) - 3: return struct.unpack_from(">I", b, a - lo)[0]
    return rd.r32(a)
def cstr(a):
    for lo, b in dumps:
        if lo <= a < lo + len(b): return b[a - lo: b.index(b"\0", a - lo)].decode(errors="replace")
    return rd.cstr(a)
