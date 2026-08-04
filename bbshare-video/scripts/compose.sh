#!/usr/bin/env bash
# Align the recorded deck to the audio, burn captions, mux the final MP4.
#
# The raw Playwright recording may contain a lead-in before the first slide and
# a short tail after the last one. Trim only the measured lead, then pad/trim
# the video to the audio clock before burning captions. Use --lead for a
# verified value; --lead auto keeps the duration-difference fallback.
#
# Usage:
#   compose.sh --project presentations/foo \
#     --video record/animated_capture.webm \
#     --audio audio/voice_with_bgm.wav \
#     --srt   audio/voice.srt \
#     --lead  0.57 \
#     --out   final/foo.mp4
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT="" ; VIDEO="" ; AUDIO="" ; SRT="" ; OUT="" ; LEAD_MODE="auto" ; PYTHON="${PYTHON:-python3}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --project) PROJECT="$2"; shift 2 ;;
    --video)   VIDEO="$2";   shift 2 ;;
    --audio)   AUDIO="$2";   shift 2 ;;
    --srt)     SRT="$2";     shift 2 ;;
    --lead)    LEAD_MODE="$2"; shift 2 ;;
    --out)     OUT="$2";     shift 2 ;;
    --python)  PYTHON="$2";  shift 2 ;;
    *) echo "unknown arg: $1" >&2; exit 2 ;;
  esac
done
[[ -n "$PROJECT" && -n "$VIDEO" && -n "$AUDIO" && -n "$OUT" ]] \
  || { echo "need --project --video --audio --out" >&2; exit 2; }

cd "$PROJECT"
dur() { ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$1"; }

AUDIO_DUR=$(dur "$AUDIO")
VID_DUR=$(dur "$VIDEO")
if [[ "$LEAD_MODE" == "auto" ]]; then
  if [[ -f record/capture_meta.json ]]; then
    LEAD=$("$PYTHON" -c 'import json,sys; d=json.load(open(sys.argv[1])); print(max(0.0, round(float(d.get("recommended_lead_sec", 0)), 3)))' record/capture_meta.json)
    echo "lead=auto (record/capture_meta.json)"
  else
    LEAD=$("$PYTHON" -c 'import sys; print(max(0.0, round(float(sys.argv[1])-float(sys.argv[2]), 3)))' "$VID_DUR" "$AUDIO_DUR")
    echo "WARNING: no capture_meta.json; using video-audio duration difference (${LEAD}s) as lead estimate" >&2
  fi
elif [[ "$LEAD_MODE" == "none" ]]; then
  LEAD="0.0"
else
  LEAD=$("$PYTHON" -c 'import sys; print(max(0.0, round(float(sys.argv[1]), 3)))' "$LEAD_MODE")
fi
echo "audio=${AUDIO_DUR}s video=${VID_DUR}s -> trimming ${LEAD}s of measured lead-in"

mkdir -p record final
TRIMMED="record/aligned.mp4"
ffmpeg -y -hide_banner -loglevel error \
  -ss "$LEAD" -i "$VIDEO" -t "$AUDIO_DUR" \
  -vf "fps=30,format=yuv420p,tpad=stop_mode=clone:stop_duration=1" \
  -c:v libx264 -preset veryfast -crf 18 -an \
  "$TRIMMED"

VIDEO_TRACK="$TRIMMED"
if [[ -n "$SRT" && -f "$SRT" ]]; then
  if ffmpeg -hide_banner -filters 2>/dev/null | grep -q ' subtitles '; then
    echo "burning captions with libass"
    VIDEO_TRACK="record/captioned.mp4"
    ffmpeg -y -hide_banner -loglevel error -i "$TRIMMED" \
      -vf "subtitles=${SRT}:force_style='FontSize=28,PrimaryColour=&H00FFFFFF&,OutlineColour=&H80000000&,BorderStyle=3,Outline=1,MarginV=60'" \
      -c:v libx264 -preset medium -crf 17 -pix_fmt yuv420p -an "$VIDEO_TRACK"
  else
    echo "no libass in this ffmpeg — rendering caption PNGs and overlaying"
    VIDEO_TRACK="record/captioned.mp4"
    $PYTHON "$HERE/render_captions.py" \
      --srt "$SRT" --project . --input "$TRIMMED" --output "$VIDEO_TRACK"
    bash record/burn_caps.sh
  fi
fi

ffmpeg -y -hide_banner -loglevel error \
  -i "$VIDEO_TRACK" -i "$AUDIO" \
  -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 192k \
  -t "$AUDIO_DUR" -shortest \
  "$OUT"

echo "final: $OUT"
ffprobe -v error -show_entries format=duration:stream=codec_type,codec_name,width,height \
  -of default=nw=1 "$OUT"
