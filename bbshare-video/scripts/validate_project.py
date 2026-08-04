#!/usr/bin/env python3
"""Validate narration/deck consistency and optional final media timing."""

from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
from html.parser import HTMLParser
from pathlib import Path


class SlideParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.slides = []

    def handle_starttag(self, tag, attrs):
        if tag != "section":
            return
        data = dict(attrs)
        classes = set((data.get("class") or "").split())
        if "slide" in classes:
            self.slides.append({
                "id": data.get("data-id", ""),
                "narration": html.unescape(data.get("data-narration", "")),
            })


def norm(text: str) -> str:
    return re.sub(r"\s+", "", text or "")


def probe(path: Path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration:stream=index,codec_type,width,height,start_time,duration",
         "-of", "json", str(path)],
        capture_output=True, text=True, check=True,
    )
    return json.loads(out.stdout)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--audio", type=Path)
    ap.add_argument("--video", type=Path)
    ap.add_argument("--vertical", action="store_true", help="require 1080x1920 video")
    args = ap.parse_args()

    project = args.project
    errors = []
    warnings = []
    narr_json = project / "narration.json"
    narr_txt = project / "narration.txt"
    index = project / "index.html"

    slides_json = json.loads(narr_json.read_text(encoding="utf-8"))["slides"] if narr_json.exists() else []
    paras = [p.strip() for p in re.split(r"\n\s*\n", narr_txt.read_text(encoding="utf-8").strip()) if p.strip()] if narr_txt.exists() else []
    parser = SlideParser()
    if index.exists():
        parser.feed(index.read_text(encoding="utf-8"))

    if not narr_json.exists():
        errors.append("missing narration.json")
    if not narr_txt.exists():
        errors.append("missing narration.txt")
    if not index.exists():
        errors.append("missing index.html")
    counts = {"narration.json": len(slides_json), "narration.txt": len(paras), "index.html": len(parser.slides)}
    if len(set(counts.values())) > 1:
        errors.append(f"slide/paragraph count mismatch: {counts}")

    for i, slide in enumerate(slides_json):
        expected = slide.get("narration", "")
        if i < len(paras) and norm(expected) != norm(paras[i]):
            errors.append(f"narration.json vs narration.txt mismatch at slide {i + 1}")
        if i < len(parser.slides) and norm(expected) != norm(parser.slides[i]["narration"]):
            errors.append(f"narration.json vs index.html mismatch at slide {i + 1}")

    if args.audio:
        if not args.audio.exists():
            errors.append(f"audio not found: {args.audio}")
        else:
            audio_info = probe(args.audio)
            audio_dur = float(audio_info["format"]["duration"])
            print(f"audio: {audio_dur:.3f}s")

    if args.video:
        if not args.video.exists():
            errors.append(f"video not found: {args.video}")
        else:
            info = probe(args.video)
            streams = info.get("streams", [])
            video = next((s for s in streams if s.get("codec_type") == "video"), None)
            audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
            if not video or not audio:
                errors.append("video must contain both video and audio streams")
            else:
                video_dur = float(video["duration"])
                audio_dur = float(audio["duration"])
                print(f"video: {video.get('width')}x{video.get('height')} {video_dur:.3f}s; audio {audio_dur:.3f}s")
                if float(video.get("start_time", 0)) != 0 or float(audio.get("start_time", 0)) != 0:
                    errors.append("video/audio must both start at 0")
                if abs(video_dur - audio_dur) > 0.1:
                    errors.append(f"video/audio duration difference is {abs(video_dur - audio_dur):.3f}s")
                if args.vertical and (video.get("width"), video.get("height")) != (1080, 1920):
                    errors.append("expected 1080x1920 vertical video")

    if errors:
        print("FAIL")
        for item in errors:
            print(f"- {item}")
        raise SystemExit(1)
    for item in warnings:
        print(f"WARNING: {item}")
    print(f"PASS: {counts}")


if __name__ == "__main__":
    main()
