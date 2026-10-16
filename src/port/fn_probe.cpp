#include "ppu_recomp.h"
#include <stdio.h>
#include <stdlib.h>
extern "C" void fn_probe_dump_check(unsigned a);
extern "C" void fn_probe_hit(ppu_context* c, unsigned a)
{
    fn_probe_dump_check(a);
    fprintf(stderr, "[probe] %08X tid=%llu lr=%08X r3=%08llX r4=%08llX r5=%08llX r6=%08llX\n", a,
            (unsigned long long)c->thread_id, (unsigned)c->lr,
            (unsigned long long)c->gpr[3], (unsigned long long)c->gpr[4],
            (unsigned long long)c->gpr[5], (unsigned long long)c->gpr[6]);
    static int regs = getenv("FN_PROBE_REGS") != nullptr;
    if (regs) {
        for (int i = 0; i < 32; i++)
            fprintf(stderr, "%sr%d=%08llX", i % 8 ? " " : "\n    ", i, (unsigned long long)c->gpr[i]);
        fprintf(stderr, "\n");
    }
}
extern "C" void fn_probe_ret(ppu_context* c, unsigned a)
{
    fprintf(stderr, "[probe] %08X tid=%llu returns r3=%08llX\n", a,
            (unsigned long long)c->thread_id, (unsigned long long)c->gpr[3]);
}

/* FN_DUMP_AT=<fn>: when that guest function is first entered, write guest
 * memory ranges (FN_DUMP_RANGES=lo-hi,lo-hi; default .data/.bss + the first
 * 128 MB of user heap) to memdump_<lo>.bin for offline inspection. */
#include <stdlib.h>
#include <string.h>
extern "C" uint8_t* vm_base;
static unsigned s_dump_at = []{ const char* e = getenv("FN_DUMP_AT"); return e ? (unsigned)strtoul(e, 0, 16) : 0u; }();
static void fn_dump_ranges(void)
{
    const char* r = getenv("FN_DUMP_RANGES");
    if (!r) r = "950000-B20000,40000000-48000000";
    while (*r) {
        unsigned lo = (unsigned)strtoul(r, (char**)&r, 16); if (*r == '-') r++;
        unsigned hi = (unsigned)strtoul(r, (char**)&r, 16); if (*r == ',') r++;
        char name[64]; snprintf(name, sizeof name, "memdump_%08X.bin", lo);
        FILE* f = fopen(name, "wb");
        /* page by page: guard pages around thread stacks are unreadable */
        static const char zero[4096] = {0};
        if (f) { for (unsigned p = lo; p < hi; p += 4096)
                     if (fwrite(vm_base + p, 1, 4096, f) != 4096) { clearerr(f); fseek(f, (long)(p - lo), SEEK_SET); fwrite(zero, 1, 4096, f); }
                 fclose(f); }
        fprintf(stderr, "[probe] dumped %08X-%08X -> %s\n", lo, hi, name);
    }
}

extern "C" void fn_probe_dump_check(unsigned a)
{
    /* FN_DUMP_AT=<fn>[:<n>] dumps on the n-th entry (default first). */
    static int seen, nth = []{ const char* e = getenv("FN_DUMP_AT"); const char* c = e ? strchr(e, ':') : 0; return c ? atoi(c + 1) : 1; }();
    if (a != s_dump_at || ++seen != nth) return;
    fn_dump_ranges();
}

/* FN_DUMP_SEC=<s>: dump the same ranges once, <s> seconds after start. */
#include <thread>
#include <chrono>
static int s_dump_timer = []{
    const char* e = getenv("FN_DUMP_SEC");
    if (e) std::thread([](int sec){ std::this_thread::sleep_for(std::chrono::seconds(sec)); fn_dump_ranges(); }, atoi(e)).detach();
    return 0;
}();