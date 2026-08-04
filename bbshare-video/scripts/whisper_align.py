#!/usr/bin/env python3
"""Align approved narration text to faster-whisper word timestamps.

Whisper supplies timing only. The final cue text always comes from the
approved narration file, so recognition mistakes never reach the subtitles.

Usage:
  python whisper_align.py \
    --audio audio/voicebox_manual.wav \
    --text-file narration.txt \
    --out-srt audio/voicebox_whisper.srt \
    --whisper-json audio/voicebox_whisper.json \
    --cues-json audio/voicebox_whisper_cues.json
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

from faster_whisper import WhisperModel

SENT_END = "。！？；;!?"
CLAUSE_END = "，,、:：—"


def probe_duration(path: Path) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(out.stdout.strip())


def norm_text(text: str) -> str:
    out = []
    for ch in unicodedata.normalize("NFKC", text).lower():
        if ch.isalnum() or "\u3400" <= ch <= "\u9fff":
            out.append(ch)
    return "".join(out)


def width(text: str) -> float:
    return sum(1.0 if "\u3400" <= ch <= "\u9fff" else 0.5 for ch in text)


def split_units(para: str) -> list[str]:
    sents = [s.strip() for s in re.split(rf"(?<=[{SENT_END}])", para) if s.strip()]
    units = []
    for sent in sents:
        units.extend([p.strip() for p in re.split(rf"(?<=[{CLAUSE_END}])", sent) if p.strip()])
    return units or [para]


def wrap(text: str, max_width: float) -> str:
    if width(text) <= max_width:
        return text
    mid = len(text) // 2
    for j in range(max(1, mid - 6), min(len(text), mid + 7)):
        if text[j - 1] in CLAUSE_END + SENT_END + " ":
            return text[:j].rstrip() + "\n" + text[j:].lstrip()
    return text[:mid] + "\n" + text[mid:]


def ts(sec: float) -> str:
    sec = max(0.0, sec)
    h, rem = divmod(int(sec), 3600)
    m, s = divmod(rem, 60)
    ms = int(round((sec - int(sec)) * 1000))
    if ms == 1000:
        s, ms = s + 1, 0
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def transcribe(args):
    model = WhisperModel(args.model, device=args.device, compute_type=args.compute_type)
    segments, info = model.transcribe(
        str(args.audio),
        language=args.language,
        word_timestamps=True,
        vad_filter=True,
        condition_on_previous_text=False,
    )
    segments = list(segments)
    raw = {"language": info.language, "duration": probe_duration(args.audio), "segments": []}
    chars = []
    for seg in segments:
        words = []
        for word in (seg.words or []):
            item = {"start": float(word.start), "end": float(word.end), "word": word.word}
            words.append(item)
            token = norm_text(word.word)
            for ch in token:
                chars.append((ch, float(word.start), float(word.end)))
        if not words:
            token = norm_text(seg.text)
            span = max(float(seg.end) - float(seg.start), 0.01)
            for i, ch in enumerate(token):
                s = float(seg.start) + span * i / max(len(token), 1)
                e = float(seg.start) + span * (i + 1) / max(len(token), 1)
                chars.append((ch, s, e))
        raw["segments"].append({
            "start": float(seg.start), "end": float(seg.end), "text": seg.text, "words": words,
        })
    return raw, chars


def align_times(target: str, spoken_chars: list[tuple[str, float, float]], duration: float):
    hyp = "".join(x[0] for x in spoken_chars)
    times: list[tuple[float, float] | None] = [None] * len(target)
    if not target or not hyp:
        return [(0.0, duration)] * max(len(target), 1)

    blocks = SequenceMatcher(None, target, hyp, autojunk=False).get_matching_blocks()
    for i, j, n in blocks:
        for k in range(n):
            times[i + k] = (spoken_chars[j + k][1], spoken_chars[j + k][2])

    matched = [i for i, value in enumerate(times) if value is not None]
    if not matched:
        return [(duration * i / len(target), duration * (i + 1) / len(target)) for i in range(len(target))]

    first = matched[0]
    first_time = times[first][0]
    for i in range(first):
        times[i] = (first_time * i / max(first, 1), first_time * (i + 1) / max(first, 1))

    for left, right in zip(matched, matched[1:]):
        if right - left <= 1:
            continue
        left_end = times[left][1]
        right_start = times[right][0]
        span = max(right_start - left_end, 0.01)
        for i in range(left + 1, right):
            a = (i - left) / (right - left)
            times[i] = (left_end + span * a * 0.8, left_end + span * (a + 0.2) * 0.8)

    last = matched[-1]
    tail_start = times[last][1]
    tail = max(duration - tail_start, 0.01)
    for i in range(last + 1, len(target)):
        a = (i - last) / max(len(target) - last, 1)
        times[i] = (tail_start + tail * a * 0.8, tail_start + tail * (a + 0.2) * 0.8)

    return [x or (0.0, duration) for x in times]


def build_cues(text: str, char_times, duration: float, max_width: float):
    paras = [p.strip() for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]
    target = "".join(norm_text(p) for p in paras)
    cursor = 0
    cues = []
    for para_index, para in enumerate(paras):
        for unit in split_units(para):
            unit_norm = norm_text(unit)
            if not unit_norm:
                continue
            pos = target.find(unit_norm, cursor)
            if pos < 0:
                pos = cursor
            end_pos = min(pos + len(unit_norm) - 1, len(char_times) - 1)
            start = char_times[pos][0]
            end = char_times[end_pos][1]
            cues.append({"para": para_index, "start": start, "end": end, "text": unit})
            cursor = end_pos + 1

    if not cues:
        raise SystemExit("no caption cues could be built from narration.txt")
    cues[0]["start"] = 0.0
    cues[-1]["end"] = duration
    for i in range(1, len(cues)):
        cues[i]["start"] = max(cues[i]["start"], cues[i - 1]["end"])
        if cues[i]["end"] <= cues[i]["start"]:
            cues[i]["end"] = min(duration, cues[i]["start"] + 0.8)
    for cue in cues:
        cue["text"] = wrap(cue["text"], max_width)
    return cues


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--audio", type=Path, required=True)
    ap.add_argument("--text-file", type=Path, required=True)
    ap.add_argument("--out-srt", type=Path, required=True)
    ap.add_argument("--whisper-json", type=Path)
    ap.add_argument("--cues-json", type=Path)
    ap.add_argument("--model", default="base")
    ap.add_argument("--language", default="zh")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--compute-type", default="int8")
    ap.add_argument("--max-width", type=float, default=26)
    args = ap.parse_args()

    duration = probe_duration(args.audio)
    raw, spoken_chars = transcribe(args)
    target_text = args.text_file.read_text(encoding="utf-8")
    char_times = align_times(norm_text(target_text), spoken_chars, duration)
    cues = build_cues(target_text, char_times, duration, args.max_width)

    blocks = [f"{i}\n{ts(c['start'])} --> {ts(c['end'])}\n{c['text']}\n" for i, c in enumerate(cues, 1)]
    args.out_srt.parent.mkdir(parents=True, exist_ok=True)
    args.out_srt.write_text("\n".join(blocks), encoding="utf-8")
    if args.whisper_json:
        args.whisper_json.write_text(json.dumps(raw, indent=2, ensure_ascii=False), encoding="utf-8")
    if args.cues_json:
        args.cues_json.write_text(json.dumps(cues, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"{len(cues)} exact-text cues over {duration:.2f}s -> {args.out_srt}")


if __name__ == "__main__":
    main()
