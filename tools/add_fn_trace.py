#!/usr/bin/env python3
"""Post-process a lift: record every guest function entry in a per-thread ring
(src/port/fn_trace.c) so a stalled or bailing thread can say how it got there."""
import glob, re, sys
d = sys.argv[1] if len(sys.argv) > 1 else "src/recomp"
pat = re.compile(r"^(void (func_[0-9A-F]{8})\(ppu_context\* ctx\) \{)$", re.M)
for f in sorted(glob.glob(d + "/ppu_recomp_[0-9]*.cpp")):
    s = open(f).read()
    if "PPU_FN_ENTER" in s:
        continue
    s = pat.sub(lambda m: f"{m.group(1)} PPU_FN_ENTER(ctx, 0x{m.group(2)[5:]}u);", s)
    s = s.replace('#include "ppu_recomp.h"\n',
                  '#include "ppu_recomp.h"\n'
                  'extern "C" unsigned g_fn_trace[64][65536];\n'
                  'extern "C" unsigned short g_fn_trace_pos[64];\n'
                  'extern "C" unsigned char g_fn_probe[0x300000];\n'
                  'extern "C" void fn_probe_hit(ppu_context*, unsigned);\n'
                  'extern "C" void fn_probe_ret(ppu_context*, unsigned);\n'
                  'struct FnProbeGuard { ppu_context* c; unsigned a; bool on;\n'
                  '    ~FnProbeGuard() { if (__builtin_expect(on, 0)) fn_probe_ret(c, a); } };\n'
                  '#define PPU_FN_ENTER(c, a) g_fn_trace[(c)->thread_id & 63][g_fn_trace_pos[(c)->thread_id & 63]++] = (a); \\\n'
                  '    FnProbeGuard _probe{(c), (a), g_fn_probe[((a) >> 2) & 0x2FFFFF] != 0}; \\\n'
                  '    if (__builtin_expect(_probe.on, 0)) fn_probe_hit((c), (a))\n', 1)
    open(f, "w").write(s)
