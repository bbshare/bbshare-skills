# Format selection policy

Used by `scripts/download.py`. Mirrors the manual workflow:

```bash
./yt-dlp_macos -F --cookies-from-browser chrome <url>
./yt-dlp_macos -f <id> --cookies-from-browser chrome <url>
# or when split streams:
./yt-dlp_macos -f <video_id>+<audio_id> --cookies-from-browser chrome <url>
```

## Resolution

- Measure **short side** `min(width, height)` so portrait (1080×1920) and landscape (1920×1080) both count as 1080p.
- Preference order:
  1. short-side ≥ **1080**
  2. short-side ≥ **720**
  3. otherwise the **highest** short-side available

## Audio

- Prefer formats that already include audio (`vcodec` + `acodec` both present).
- If the best video is video-only, pick best audio-only and use `-f video+audio` (requires `ffmpeg`).

## Quality tie-breakers (same resolution bucket)

1. Prefer **non-watermarked** (skip / deprioritize `download_addr*` and notes containing `watermark`)
2. Prefer non-API CDN mirrors when noted `(API)` or weak `-0`/`-1` suffixes
3. Higher `tbr`, then larger `filesize`

## Douyin notes

- Short links (`v.douyin.com/...`) redirect to `www.douyin.com/video/<id>`.
- Chrome cookies (`--cookies-from-browser chrome`) are usually required.
- Typical good pick looks like `bytevc1_720p_688122-2` (Playback, high bitrate, muxed mp4).
- Watermarked API dumps (`download_addr-*`) can be huge but lower visual quality — avoid unless nothing else exists.
