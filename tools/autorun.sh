#!/bin/bash
# autorun.sh <seconds> <log> [extra env...]: run the port headless-ish for
# <seconds>, skipping the intro movie (CROSS a few times once lbpintro.bik is
# open). Extra arguments are VAR=value pairs passed to the port.
secs=$1; log=$2; shift 2
cd "$(dirname "$0")/.."
: > run/pad.txt
env PAD_FILE="$PWD/run/pad.txt" "$@" gtimeout -s KILL "$secs" ./run.sh > "$log" 2>&1 &
pid=$!
( until grep -q "lbpintro.bik" "$log" 2>/dev/null; do sleep 2; done
  for i in 1 2 3 4 5 6; do sleep 4; echo 0x4000 > run/pad.txt; done ) &
wait $pid
