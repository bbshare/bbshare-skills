# Caption Sync Protocol

Use this protocol when a preview sounds right but captions drift, omit words, or paraphrase the narration.

## Alignment Order

1. Treat `audio/voiceover_with_intro.txt` as the canonical visible text.
2. Transcribe the clean voice file, usually `audio/voiceover_with_intro.mp3`, not `audio/master_with_intro.wav`.
3. Use ASR timestamps to locate speech, pauses, and sentence boundaries.
4. Replace ASR text with the approved script text before writing HTML captions.

Chinese ASR is useful for timing but can misrecognize names, numbers, punctuation, and homophones. It must not become the final caption source.

## Local Timestamp Pass

Prefer an installed local backend in this order:

- `whisper-fast`, if the executable is present.
- Python `faster-whisper`, with `language="zh"`, `word_timestamps=True`, and `vad_filter=False` for short TTS narration.
- The local whisper.cpp binary as a fallback.

For `faster-whisper`, save a JSON artifact such as `audio/transcript_faster.json` with segment and word `start`/`end` values. If macOS reports an OpenMP duplicate-runtime error, retry the local process with `KMP_DUPLICATE_LIB_OK=TRUE` and a modest `OMP_NUM_THREADS` value; do not alter the audio to hide the problem.

## Cue Table Rules

- Add the voice-free opener offset to every scene start, caption reveal, and caption hide.
- Make one cue per spoken sentence or natural pause, keeping the original script words intact.
- Set each old cue's `data-hide` before the next cue appears.
- Move scene boundaries to sentence or semantic-beat boundaries. A scene can be longer or shorter than the first storyboard estimate.
- Keep the visible caption to one or two lines where possible; split a long sentence at a real spoken pause, but do not omit or paraphrase words.
- Use hard cuts while debugging. Reintroduce motion only after the text timing is stable.

## Exact-Text Audit

Before preview, concatenate all visible caption text in reading order and compare it to the narration file after removing only whitespace and punctuation. This catches the common failure where the subtitle is “on time” but silently summarizes a sentence.

Also check:

- every reveal and hide lies inside its scene interval;
- cue times are monotonically increasing;
- no sentence is split across a scene transition;
- the last caption ends before the final audio tail;
- the opener remains voice-free until its configured end.

## Final Render Check

After rendering, extract a contact sheet at the hook, example, result/reversal, warning, and closing question. Inspect the MP4 frames themselves, then run `ffprobe` for duration, `1080x1440`, H.264 video, and AAC audio. A browser preview alone is not enough to certify the final export.
