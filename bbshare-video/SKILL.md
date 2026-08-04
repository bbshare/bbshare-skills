---
name: bbshare-video
description: Build a narrated explainer video from a concept — discussion → structure → HTML slide deck → narration script → TTS voice → subtitles → background music → Playwright screen recording → ffmpeg composite. Use when asked to make a 讲解视频 / explainer / talking-deck video, to turn a topic or article into a narrated video or animated slide deck, or to redo one stage of an existing deck (re-record, re-mix BGM, regenerate captions, swap the voice).
---

# BBShare Video Pipeline

**当前版本：0.3.0**

版本规则：修复或小幅调整递增补丁号；新增可复用能力递增次版本号；发生不兼容变更时递增主版本号。

Turns a concept into a finished narrated video. No digital human, no avatar — an
HTML deck is the source of truth, and everything else is generated from it.

The whole point of doing it this way: an HTML deck is code. It diffs, it takes a
scripted screenshot, it re-renders identically, and one file drives both the
visuals and the narration text. Drag-and-drop slide tools cannot do that.

The measured voice file is the master clock. The approved narration is the
master text. The recording metadata, caption timestamps, cover treatment, and
final QA must all be derived from those two inputs — never from authored time
estimates or a guessed browser wait.

All authored copy in this workflow must pass through an applicable dbskills
skill before finalization: use the content/script/resonance skills for
narration and on-screen wording, and `dbs-xhs-title` plus platform-specific
dbskills for publishing copy. Preserve the user's approved wording after the
narration lock; do not silently rewrite it during production.

## Pipeline

```
concept ──discuss──▶ framework.json ──▶ index.html + narration.{txt,json,md}
                                              │
                    ┌─────────────────────────┴──────────────────────┐
                    ▼                                                ▼
           TTS (voicebox/edge/say)                        Playwright records
              audio/voice.wav                             the animated deck
                    │                                                │
              build_srt.py                                    trim the lead-in
              audio/voice.srt ─────────▶ caption PNGs ────▶ overlay + mux ────▶ final/*.mp4
                    │                                                ▲
              mix_bgm.sh ──────────────────────────────────────────┘
                                     │
                         capture metadata + cover + QA
```

Steps 1–2 are authoring (do them with the user). Steps 3–8 are mechanical and
`scripts/build_video.sh` runs them.

## Step 1 — Agree on the framework before writing anything

Do not open an editor yet. Talk the concept through with the user, then write
`framework.json`:

```json
{
  "concept": "...", "audience": "...", "one_liner": "...",
  "total_pages": 8, "target_duration_sec": 94,
  "structure": [{ "page": 1, "role": "钩子", "point": "..." }]
}
```

Rules that hold up: 8 pages ≈ 90–110 seconds. One point per page. Give every
page a *role* (hook / context / why / overview / method / method / method /
close), not just a title. Show the framework and get a yes before drafting.

## Step 2 — Deck and narration together

Copy `references/deck-template.html` to `presentations/<slug>/index.html` and
rewrite the slides. Write the narration **into** the slides as
`data-narration`, with `data-duration` in seconds — that markup is the single
source, and everything downstream reads it.

Narration voice: spoken, not written. Short sentences. No academic register. One
to two sentences per page. Read it out loud; if you stumble, so will the TTS.

Then emit four sibling files:

| file | what | consumed by |
|---|---|---|
| `index.html` | the deck | recording |
| `narration.json` | per-slide title / narration / duration_sec | timeline |
| `narration.txt` | continuous script, **one blank-line-separated paragraph per slide, same order** | TTS + SRT |
| `narration.md` | human-readable script + page/time table | the user |

`narration.txt`'s paragraph-per-slide structure is load-bearing — `build_srt.py`
uses paragraph boundaries to place the pauses between slides. Pressing `E` in
the deck exports `narration.json` directly from the markup.

Let the user read `narration.md` and approve before spending TTS time.

### Narration lock

Once the user edits or approves the narration, stop treating generated siblings
as independent drafts. Pick the approved text as the source, then synchronize
`narration.txt`, `narration.json`, and every slide's `data-narration` before
generating audio. Check that paragraph/slide count, order, punctuation, and
page titles still match. Do not silently rewrite approved wording for style.

After a narration change, invalidate the SRT, timeline, recording, captions,
and final video; never reuse them just because the files already exist.

## Steps 3–8 — Assemble

```bash
S=~/.codex/skills/bbshare-video/scripts
bash $S/build_video.sh presentations/<slug> --bgm audio/music.mp3
```

`--tts auto` (the default) uses the local Voicebox daemon if it answers, else
`edge-tts` if installed, else macOS `say`. Nothing downstream cares which one
ran, so a first pass on `say` is a legitimate way to see the whole pipeline
work before setting up a real voice:

```bash
bash $S/build_video.sh presentations/<slug> --tts say                       # zero install
bash $S/build_video.sh presentations/<slug> --tts edge --voice zh-CN-YunxiNeural
bash $S/build_video.sh presentations/<slug> --tts voicebox --voice <profile>  # cloned voice
python3 $S/tts.py --engine edge --list                                       # what voices exist
```

Each step skips if its output exists, so iterating is cheap:

```bash
bash $S/build_video.sh presentations/<slug> --only mix,compose --bgm-volume 0.12   # BGM too loud
bash $S/build_video.sh presentations/<slug> --from record                          # deck changed
bash $S/build_video.sh presentations/<slug> --only srt,compose                      # captions off
bash $S/build_video.sh presentations/<slug> --force                                 # rebuild all
```

If the user already generated a voice in Voicebox, use the WAV as the clock
instead of synthesizing a second voice. When captions were aligned separately,
pass them in explicitly:

```bash
bash $S/build_video.sh presentations/<slug> \
  --audio audio/voicebox_manual.wav \
  --srt-file audio/voicebox_whisper.srt \
  --lead 0.57 --bgm none --from srt
```

`--lead auto` is only a fallback estimate. For a publishable render, inspect
the first visual transition in the raw capture and pass the measured lead.
Use `--lead none` only when the capture is known to start at the first audio
sample.

Scripts, if you need one on its own:

- `tts.py` — narration → `audio/voice.wav` on whichever engine is available.
- `tts_voicebox.py` — the Voicebox backend on its own. `--list` shows profiles.
- `build_srt.py` — narration + measured audio duration → `audio/voice.srt`.
- `whisper_align.py` — faster-whisper word timing + approved narration text → exact-text SRT.
- `deck_capture.py timeline|slides|video` — timeline scaled to real audio; static PNGs; animated webm.
- `render_captions.py` — SRT → transparent PNGs + `record/burn_caps.sh`.
- `mix_bgm.sh` — voice + music → `audio/voice_with_bgm.wav`.
- `compose.sh` — align, burn captions, mux → `final/<slug>.mp4`.
- `add_cover.sh` — finite first-frame cover overlay without shifting audio.
- `validate_project.py` — check narration/deck consistency and final media timing.

### Recommended order when the voice is manual

1. Synchronize the approved narration across `narration.md`, `narration.txt`, and the deck.
2. Probe the supplied WAV; do not stretch it to authored durations.
3. Run `whisper_align.py` for word timestamps; keep the approved narration as the final text.
4. Rebuild `timeline.json`, then record with `deck_capture.py video` at the final
   delivery aspect ratio. For Xiaohongshu/WeChat Channels use 1080×1920.
5. Inspect multiple raw visual transitions and fit the capture to the audio clock;
   use `--lead <seconds>` only when there is no measurable speed drift. If the
   raw capture drifts progressively, apply an affine time correction before
   burning captions.
6. Render captions after the video clock is normalized. For vertical delivery,
   pass the frame size explicitly and reserve the platform-safe caption band.
7. Add a cover only after the timed video works. Overlay it for about 0.5–0.7s;
   do not prepend it unless matching audio lead-in is intentional.
8. Verify the first frame, one frame after the cover, page transitions, stream
   start times, and audio/video durations before delivery.
9. Run `validate_project.py` once before TTS and once after the final render.
10. Create `publish-copy.md` with platform-specific Xiaohongshu and WeChat
    Channels titles, body copy, and hashtags after the video passes QA.

Use `.venv/bin/python` if the project has one (Playwright and Pillow live
there); `build_video.sh` finds it automatically.

## Things that will bite you

**Audio duration is the master clock.** Authored `data-duration` values are
estimates. TTS decides the real length. Everything — slide timeline, captions,
recording — gets scaled to the measured `voice.wav` duration, never the other
way round. Never hardcode a duration; always `ffprobe` it.

**Playwright's webm can contain lead, tail, and speed drift.** The recorder
calls `deckAPI.playSequence()` once inside the browser; calling `go()` and
`wait_for_timeout()` from Python for every slide accumulates round-trip drift
and can make the first page disappear when the duration difference is trimmed.
The capture metadata's `capture_duration - target_duration` is only a
duration-difference heuristic, not proof of a lead-in. Measure at least two or
three visible page transitions against their audio boundaries. If raw times
`r` and audio times `t` fit `r ≈ a + b·t` with `b` materially different from 1,
normalize with an affine correction such as
`trim=start=a,setpts=(PTS-STARTPTS)/b` before captioning. In the tested vertical
capture, the raw WebM was about 12.9% slow (`b≈1.1289`) even though its first
frame did not contain a 14-second lead. Probe the actual raw frame rate too;
the requested recording rate and the WebM rate may differ. Normalize the final
delivery to 30fps.

**Vertical captions need an explicit platform-safe area.** `render_captions.py`
defaults to 1920×1080 and a 70px bottom margin, and the stock `compose.sh`
does not expose vertical caption sizing. For a 1080×1920 Xiaohongshu/WeChat
Channels video, invoke the caption renderer with explicit dimensions; the
validated baseline is `--width 1080 --height 1920 --font-size 44 --margin 240`.
Treat 240px from the bottom as the default safe band for this delivery target,
then inspect a real
frame. The deck's `padding-bottom` protects slide content but does not move
burned-in captions, so both areas need separate checks.

**`subtitles=` may not exist.** Homebrew ffmpeg is frequently built without
libass. Check with `ffmpeg -filters | grep subtitles`. `compose.sh` falls back
to Pillow-rendered transparent PNGs overlaid with
`enable='between(t,start,end)'` — which also gives better CJK font control.
Caption PNG chains scale fine to ~50 cues; past a few hundred, split the video.

**`amix` normalizes by default.** It divides each input's gain by the input
count, so the BGM disappears and raising `volume=` does nothing. Always
`normalize=0` and set levels explicitly. Voice at `loudnorm=I=-16`, BGM at
`volume=0.20`, `alimiter=limit=0.97` on the sum. Verify with `volumedetect`
rather than trusting the graph.

**Synthesized sine pads sound like tinnitus.** The "滋滋声" complaint. Use a real
music file. `--bgm synth` is only a no-network fallback.

**Voicebox hangs need clearing.** `/generate/{id}/status` is a blocking SSE
stream — poll `/history/{id}` with `Accept: application/json` instead. A crashed
worker leaves jobs stuck in `generating` forever and blocks new ones;
`tts_voicebox.py --cancel-stuck` clears them. If the daemon itself is
unresponsive, `kill` the orphaned `voicebox-server` and reopen the app.

**Use two caption modes deliberately.** For a normal neural voice,
`build_srt.py` distributes the approved text by character weight. For a manual
Voicebox recording with expressive pauses, run `whisper_align.py` with the local
`faster-whisper` model to obtain word timestamps. Never copy Whisper's
recognized text into the final SRT; align its timings back onto the approved
narration so names, punctuation, and wording stay exact.

**A deck sized for the preview looks empty at 1920×1080.** The "右边太空了"
problem. Two causes, both fixed in the template's `body.record-mode` block:
`max-width` on slide children strands the right third, and `rem`-capped
`clamp()` font sizes tuned for the ~1120px preview stage stay small when the
stage grows to full frame. Record mode drops the ceilings and sizes type in
`vw`, and reserves `padding-bottom: 16vh` so vertically-centred content sits
above the caption band instead of behind it. Always eyeball a real frame
(`ffmpeg -ss <t> -i final.mp4 -frames:v 1 f.png`) before calling it done.

**A cover is a visual overlay, not a new intro by default.** Generate it with
the local image-generation skill, sample the deck background first, and preserve
the approved title exactly. Keep the generation prompt under
`cover-image/prompts/`, verify the final cover is 9:16/1080×1920, and use
`add_cover.sh` to create a finite 30-fps cover clip and overlay it on the first
0.5–0.7 seconds. An infinite image loop in the final encode can produce an
incomplete MP4 without a valid `moov` atom.

**Final QA is part of the pipeline.** `ffprobe` must show video and audio
starting at 0. The video should be 1080×1920/30fps for vertical delivery, and
the duration difference should be no more than one frame plus normal AAC
rounding. Extract frames at 0, just after the cover, around 1s, and at every
timeline boundary; check the first page, subtitle placement relative to the
240px safe band, and the final page. Check that the cover ends cleanly and
that the first real slide is already in a readable animation state.

**Publishing is part of delivery.** A finished explainer is not complete until
it has a `publish-copy.md`. Do not paste the narration as the caption. Use the
`dbs-xhs-title` workflow for Xiaohongshu titles (≤20 characters, with a
traceable formula) and `dbs-content` for platform/form-expression diagnosis,
then write separate copy for Xiaohongshu and WeChat Channels. Include a
recommended title, body, hashtags, and a small set of alternatives. Keep the
copy conversational and make the closing question match the video's actual
ending.

## Output layout

```
presentations/<slug>/
  framework.json  index.html  narration.{json,txt,md}
  audio/   voice.wav  voice.srt  bgm_loop.wav  voice_with_bgm.{wav,mp3}
  record/  timeline.json  capture_meta.json  animated_capture.webm  aligned.mp4
           caps/  caps_meta.json  burn_caps.sh  captioned.mp4
  cover-image/  cover.png  prompts/
  publish-copy.md
  final/   <slug>.mp4
```

## Requirements

Required: `ffmpeg` + `ffprobe`; Python 3.9+ with `playwright` (then
`python -m playwright install chromium`) and `pillow`. For precise timing on
manual recordings, install/use `faster-whisper` and a locally cached model.

```bash
pip install playwright pillow && python -m playwright install chromium
brew install ffmpeg            # macOS; any recent ffmpeg works
```

For the voice, one of: Voicebox on `127.0.0.1:17493` (cloned voice, best),
`pip install edge-tts` (free neural voices, cross-platform), or macOS `say`
(already there). A CJK font is needed for Chinese captions — `render_captions.py`
probes for `Arial Unicode.ttf`, Hiragino Sans GB, or STHeiti.

Developed and run on macOS (Apple Silicon). The Python and ffmpeg steps are
portable; `--tts say` is the only macOS-only piece.

## Reference

- `references/deck-template.html` — working deck with the full `deckAPI` recording
  contract, staggered enter animations, and `[data-step]` progressive highlights.
