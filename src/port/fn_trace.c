/* Per-thread ring of the last 64K guest function entries (filled by the
 * PPU_FN_ENTER hook tools/add_fn_trace.py puts in every lifted function).
 * Racy by design: a diagnostic, not a record. */
#include <stdio.h>

unsigned       g_fn_trace[64][65536];
unsigned short g_fn_trace_pos[64];

/* n entries, oldest first; n > 64 goes to fntrace_<tid>.txt instead of stderr. */
void fn_trace_dump(unsigned tid, int n)
{
    unsigned t = tid & 63;
    unsigned short p = g_fn_trace_pos[t];
    FILE* f = stderr;
    char name[64];
    if (n > 64) { snprintf(name, sizeof name, "fntrace_%u.txt", tid); f = fopen(name, "w"); if (!f) return; }
    fprintf(f, "[fntrace] thread %u, last %d function entries (oldest first):\n", tid, n);
    for (int i = n; i > 0; i--) {
        unsigned a = g_fn_trace[t][(unsigned short)(p - i)];
        if (a) fprintf(f, n > 64 ? "%08X\n" : " %08X", a);
    }
    fprintf(f, "\n");
    if (f != stderr) fclose(f);
}

/* FN_PROBE=addr,addr,...: print the thread, LR and r3..r6 whenever one of
 * these guest functions is entered. */
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
unsigned char g_fn_probe[0x300000];

__attribute__((constructor)) static void fn_probe_init(void)
{
    const char* e = getenv("FN_PROBE");
    while (e && *e) {
        unsigned a = (unsigned)strtoul(e, (char**)&e, 16);
        g_fn_probe[(a >> 2) & 0x2FFFFF] = 1;
        if (*e == ',') e++; else break;
    }
}

/* FN_TRACE_AT=<sec>: after that many seconds, write every thread's last 64K
 * function entries to fntrace_<tid>.txt (and a 48-entry tail to stderr). */
#include <pthread.h>
#include <unistd.h>
static void* fn_trace_timer(void* arg)
{
    sleep((unsigned)(uintptr_t)arg);
    for (unsigned t = 1; t < 64; t++) {
        if (!g_fn_trace_pos[t] && !g_fn_trace[t][65535]) continue;
        fn_trace_dump(t, 48);
        fn_trace_dump(t, 65536);
    }
    return 0;
}
__attribute__((constructor)) static void fn_trace_timer_init(void)
{
    const char* e = getenv("FN_TRACE_AT");
    if (!e) return;
    pthread_t th;
    pthread_create(&th, 0, fn_trace_timer, (void*)(uintptr_t)atoi(e));
}
