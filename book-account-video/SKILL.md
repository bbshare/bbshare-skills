---
name: book-account-video
description: Create Douyin/TikTok-style Chinese book account short videos from a book title, book notes, or a theme. Use when the user wants to make, iterate, render, package, or publish a read-book/book-review video with human-reviewed narration, fixed opener, Doubao TTS, BGM, captions, cover image, and posting copy. Preserve natural approved narration length, use the saved viral reference methodology, and do not re-analyze reference videos unless the user explicitly asks for a new teardown.
---

# Book Account Video

## Core Rule

Use the saved production method in `references/method.md` as the default. Do not ask to download or re-teardown viral videos for ordinary new book-account videos. Only redo reference analysis when the user explicitly supplies new reference videos and says the style should change.

## Production Invariants

- Preserve the approved narration at its natural length. Do not squeeze a long, human-sounding script into an arbitrary 30-60s target; let the final TTS duration drive the timeline.
- Default to a **voice-free visual opener**: 0-3.56s uses the glass/shard/book-card animation plus SFX and BGM; the approved narration starts at 3.56s. Only add spoken opener words when the user explicitly requests them.
- When the opener is voice-free, delay the TTS by the opener duration and shift every scene start, caption reveal, and caption hide by the same offset. Never fix audio without moving the visual cue table.
- Use a clean reusable opener SFX when available. If it contains reference speech, run Demucs `--two-stems=vocals` and use only `no_vocals`; never import the reference voice into the master.
- Mix with explicit levels and `amix=normalize=0`; default amix normalization can make a short opener sound silent. Verify the first opener segment has audible peaks before preview.
- The public preview URL should stay simple: `http://localhost:<port>/simple-preview.html`. Cache-busting belongs inside the audio `src`, not in the user-facing URL. If a port is occupied, choose an available port without killing another project.
- Copy the reference video's method, never its footage. Every new book episode needs a fresh visual set chosen from the narration; do not clone the previous episode's image folder just because the composition structure is reusable.
- Normalize source images to the portrait canvas before judging the composition. For a `1080x1440` video, crop or generate each still to a `3:4` portrait asset first; do not rely on `object-fit: cover` to rescue a wide image and accidentally crop away the subject.
- Titles must describe the book's actual thesis, not a generic human-nature clickbait formula. Check the final title against the book's argument before packaging.

For video implementation, use the installed HyperFrames skills first:

1. Read `hyperframes`.
2. Read `hyperframes-core` before editing composition HTML.
3. Read `hyperframes-cli` before preview/render.
4. Read `hyperframes-media` when generating TTS, BGM, SFX, transcription, or subtitles.

## Workflow

1. **Collect the minimum input**
   - Required: book title or theme.
   - Useful: target account positioning, author/source line, desired tone, any must-use quotes.
   - Default account format: 3:4 vertical, `1080x1440`, usually 35-60s, with 60-90s allowed when shortening would damage the approved narration.

2. **Write the one-pass narration**
   - Default to the saved hook-first five-part script pattern in `references/method.md`.
   - Before drafting, list 3 core viewpoints of the book and select the single most counterintuitive / offensive one. The whole script must only serve that one point.
   - Spoken narration must not start with `今天分享的是...` unless the user explicitly asks for the old fixed opener. Put the book title in sentence 2 or 3.
   - The first sentence must be book-specific. If it could fit many other books, rewrite it.
   - Use one concrete book-grounded example. The example must come from the book's real argument or original examples; if unsure, verify or ask before writing.
   - Include an emotional reversal around the middle, then keep the post-reversal explanation to 4 sentences or fewer.
   - Use only 1-2 memorable lines. Too many "gold lines" makes the script feel written, not spoken.
   - Use natural spoken rhythm: short impact lines mixed with longer setup lines. Do not chop every sentence into 5-8 character fragments.
   - Use `renwei-writing` before presenting the narration when available: read its `SKILL.md` and post-edit checklist, then check that the script sounds like a person with a point of view, not a polished AI summary.
   - Save the full narration text, e.g. `audio/voiceover_with_intro.txt`.

3. **Self-review, then get narration approval before audio**
   - First draft the narration, run the `renwei-writing` check, revise it, and confirm it has a real hook within the first `3-5s`.
   - Only show the user the best candidate you would personally stand behind, not a raw draft.
   - Stop after this self-reviewed narration and ask the user to review it.
   - Do not generate TTS, build the full composition, or download extra visual material until the user approves or requests revisions.
   - Present a compact audit with the narration:
     `hook timing`, `self-review changes`, `why it is not AI-flavored`, `key sentences preserved for captions`.

4. **Generate voice in one pass**
   - Generate the approved narration as one TTS file. Do not generate a separate intro voice or splice reference speech into it.
   - Use Doubao TTS API Key flow if configured; see `references/doubao-tts.md`.
   - Keep the voice calm and slow. A good starting speed is `0.88`.
   - If using the default SFX-only opener, mix the delayed TTS into the master after the opener; do not put the delay into the TTS file itself.

5. **Choose content-matched visual material**
   - Copy the reference method, not the reference materials.
   - Search/select visuals according to the script and the book's subject.
   - Build a new episode-specific asset set. Reusing an old composition is fine; reusing the old episode's footage is not.
   - Use this fallback order: literal content match, theme-adjacent imagery, then emotionally matched scenery.
   - If literal images are weak, forced, or visually inconsistent, prefer evocative landscapes such as misty mountains, rivers, forests, solitary trees, paths, rain, or boats. The captions carry the argument; the scenery carries the emotion.
   - Keep fallback scenery within one coherent visual world instead of mixing unrelated stock-photo styles.
   - Give still scenery restrained, varied motion: alternate slow push, horizontal pan, vertical lift, slight drift, or a subtle mist/parallax layer. Do not apply the same zoom to every scene.
   - Do not default to a dark look. Choose bright, neutral, warm, documentary, or dark treatment according to the book and hook.
   - Keep captions over clean contrast zones. The whole image should not be crushed into black; important shapes should remain visible.
   - Convert wide source images into intentional `3:4` portrait crops before putting them into scenes. Choose the crop per subject: keep the chocolate, hand, face, phone, or other narrative anchor in frame.
   - Track asset sources in `docs/asset_sources.md` or similar.

6. **Build the HyperFrames composition**
   - Use `1080x1440`, `data-duration` equal to final mixed audio.
   - Use fixed top book title, small author/source line, bottom watermark.
   - The visual opener may show the book title from frame 0, but the spoken audio should follow the approved narration. Do not add a separate spoken `今天分享的是...` opener unless it is in the approved script.
   - Use slow Ken Burns motion only: scale/pan, no complex editing.
   - Use large white Chinese text with thick black shadow/outline.
   - Keep captions at most two lines where possible.
   - Keep opener spacing generous: top title, author line, opener subtitle, and book visual must not crowd each other.
   - Default opener timing: `0-3.56s` visual/SFX only; formal voice and the first caption cue begin at `3.56s`. Use the same offset in `data-start`, `data-reveal`, `data-hide`, the root duration, and the audio mix.

7. **Synchronize captions conservatively**
   - Source-of-truth order is: approved narration text, final TTS audio, word/token timestamps, then ASR text. Never copy Chinese ASR output directly into visible captions because recognition may change characters or names.
   - Run local word-timestamp transcription on the clean voice-only TTS file, not on the mixed master with BGM and SFX. Prefer `whisper-fast` when it is actually installed; otherwise use an installed compatible local backend such as the `faster-whisper` Python package, then fall back to whisper.cpp if needed.
   - When using `faster-whisper`, enable `word_timestamps`, use `language=zh`, and pass the approved script as an `initial_prompt` when practical. Save the result, for example, as `audio/transcript_faster.json`.
   - Map the timestamps back onto the approved script. Preserve every spoken word and punctuation choice in the script; use ASR only to locate starts, ends, and pauses.
   - Put scene boundaries between sentences or semantic beats. Never cut a sentence in half just to preserve an old scene duration table.
   - If sync feels off, remove caption animation before debugging.
   - Prefer hard-cut caption visibility at exact cue times over fancy fade/blur/stagger.
   - Add explicit `data-hide` times for old caption lines when a scene contains more than one semantic beat.
   - Run a caption-text audit: compare each screen caption to the narration and preserve core words in important logic sentences.
   - Run an exact normalized-text audit before preview: concatenate visible caption text in reading order, remove only whitespace and punctuation, and compare it with the same normalization of `audio/voiceover_with_intro.txt`. The result must match exactly.
   - Use Whisper token timestamps only as an aid; inspect them because Chinese recognition may have wrong characters.
   - If whisper.cpp crashes on Mac GPU/Metal, rerun with `--no-gpu --no-flash-attn` at the whisper-cli level.

8. **Add BGM and transition carefully**
   - Add quiet background music under narration.
   - Keep BGM low enough that text and voice dominate.
   - Put the opener SFX in the master from time 0. If using a reference-derived bed, remove vocals with Demucs first; do not use high-pass filtering as a substitute for separation.
   - Use one `audio/master_with_intro.wav` as the HyperFrames audio source. Keep the MP3 only for lightweight browser preview when needed.

9. **Preview before render**
   - Start with `npx hyperframes play --port <available> --no-open` or the project wrapper. Prefer a lightweight `simple-preview.html` for user review when the Studio player is overkill.
   - Give the user the direct `simple-preview.html` URL. Do not expose cache-busting query strings or a stale project's port.
   - Have the user review the browser preview.
   - Iterate until the user explicitly approves.
   - Render MP4 only after approval.

10. **Package the deliverables**
   - Render final MP4.
   - Generate a matching `1080x1440` cover image.
   - Keep the cover bright enough to show the subject; do not inherit a dark reference grade automatically.
   - Write `docs/posting-copy.md` with one recommended title, a concise posting body, hashtags, and optional backup titles. The recommended title must be specific to the book's thesis.
   - Verify the MP4 with `ffprobe`: plausible duration, `1080x1440`, H.264 video, and AAC audio.
   - Extract a final contact sheet from several meaningful timestamps, including the hook, experiment/example, reversal, warning, and closing question. Inspect the rendered frames, not only the browser preview.

## Reusable References

- `references/method.md`: distilled viral-method results from the completed sample project.
- `references/doubao-tts.md`: Doubao API Key TTS setup and one-pass voice workflow.
- `references/hyperframes-patterns.md`: composition, caption, render, and sync rules.
- `references/caption-sync.md`: local ASR timing, canonical-script captioning, exact-text auditing, and final-frame verification.
- `references/packaging.md`: cover image and posting copy pattern.

## Bundled Assets

- `assets/script-template.md`: narration and storyboard template.
- `assets/cover-template.html`: HTML/CSS cover template to screenshot into a cover image.

## Scripts

- `scripts/doubao_tts_v3_api_key.py`: deterministic Doubao Speech HTTP V3 TTS helper using API Key auth.

After using any script copied into a project, run it in that project and verify output duration with `ffprobe`.
