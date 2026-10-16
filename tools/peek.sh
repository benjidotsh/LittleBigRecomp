#!/bin/bash
# peek.sh <frames-dir> <prefix> [count=4] [scale=4]: tile the last <count>
# (evenly spaced) captures with that prefix into <dir>/strip.png.
d=$1; p=$2; n=${3:-4}; k=${4:-4}; t=$(dirname "$0")
files=($(ls "$d"/$p*.ppm | sort))
total=${#files[@]}; step=$(( total / n )); [ $step -lt 1 ] && step=1
pngs=()
for ((i = total - 1 - (n - 1) * step; i < total; i += step)); do
  [ $i -lt 0 ] && continue
  f=${files[$i]}; python3 "$t/ppm2png.py" "$f" "${f%.ppm}.png" "$k"; pngs+=("${f%.ppm}.png")
done
python3 "$t/strip.py" "$d/strip.png" "${pngs[@]}"
echo "${pngs[@]##*/}"
