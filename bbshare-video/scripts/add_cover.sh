#!/usr/bin/env bash
# Overlay a finite cover clip on the first frames without shifting audio.
# A finite intro is intentional: feeding an infinite -loop image directly to
# the final MP4 can leave an unclosed moov atom when an encode is interrupted.
set -euo pipefail

VIDEO=""; COVER=""; OUT=""; DURATION="0.6"; FPS="30"; PYTHON="${PYTHON:-python3}"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --video)    VIDEO="$2";    shift 2 ;;
    --cover)    COVER="$2";    shift 2 ;;
    --out)      OUT="$2";      shift 2 ;;
    --duration) DURATION="$2"; shift 2 ;;
    --fps)      FPS="$2";      shift 2 ;;
    --python)   PYTHON="$2";   shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done
[[ -f "$VIDEO" && -f "$COVER" && -n "$OUT" ]] || {
  echo "usage: add_cover.sh --video input.mp4 --cover cover.png --out output.mp4 [--duration 0.6]" >&2
  exit 2
}

SIZE=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=p=0:s=x "$VIDEO")
W="${SIZE%x*}"; H="${SIZE#*x}"
VID_DUR=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$VIDEO")
FRAMES=$("$PYTHON" -c 'import math,sys; print(max(1, round(float(sys.argv[1])*float(sys.argv[2]))))' "$DURATION" "$FPS")
TMP_DIR=$(mktemp -d "${TMPDIR:-/tmp}/bbshare-video-cover.XXXXXX")
trap 'rm -rf "$TMP_DIR"' EXIT
INTRO="$TMP_DIR/cover_intro.mp4"
mkdir -p "$(dirname "$OUT")"

ffmpeg -y -hide_banner -loglevel error \
  -loop 1 -framerate "$FPS" -i "$COVER" \
  -vf "scale=${W}:${H}:flags=lanczos" -frames:v "$FRAMES" -an \
  -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p -movflags +faststart "$INTRO"

FILTER="[1:v]scale=${W}:${H}:flags=lanczos[cover];[0:v][cover]overlay=0:0:enable='lt(t,${DURATION})':eof_action=pass:repeatlast=0[v]"
ffmpeg -y -hide_banner -loglevel error \
  -i "$VIDEO" -i "$INTRO" -filter_complex "$FILTER" \
  -map "[v]" -map 0:a? -c:v libx264 -preset medium -crf 18 -pix_fmt yuv420p \
  -c:a copy -movflags +faststart -t "$VID_DUR" "$OUT"

echo "cover: ${DURATION}s -> $OUT"
ffprobe -v error -show_entries format=duration:stream=codec_type,width,height \
  -of default=nw=1 "$OUT"
