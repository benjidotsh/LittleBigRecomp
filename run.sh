#!/bin/sh
# Run the port. The disc stays read-only: guest writes (/dev_hdd0 install data,
# /dev_hdd1 cache, saves) land in hdd/, which sees the disc through a symlink.
cd "$(dirname "$0")"
mkdir -p hdd
[ -e hdd/PS3_GAME ] || ln -s "$(cd disc && pwd)/PS3_GAME" hdd/PS3_GAME
export PS3_VFS_ROOT="${PS3_VFS_ROOT:-$PWD/hdd}"
export PS3_DEV_FLASH="${PS3_DEV_FLASH:-$HOME/Library/Application Support/rpcs3/dev_flash}"
# FMOD relocates its codec/DSP plugins into local store at run time; no static
# lift can exist for those addresses, so they run through the SPU interpreter.
export SPU_INTERP_UNLIFTED="${SPU_INTERP_UNLIFTED:-1}"
# LBP runs even single-player as a local network session over loopback
# sockets; the offline libnet model leaves those calls unanswered.
export PS3_NET_SOCKETS="${PS3_NET_SOCKETS:-1}"
exec ./build/LittleBigRecomp game/EBOOT.elf "$@"
