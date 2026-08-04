# Distilled Viral Method For This Book Account Format

This is the saved result from the completed reference teardown. Use it directly; do not re-teardown the old references for each new video.

## Format

- Aspect: `3:4`, composition size `1080x1440`.
- Duration: usually `35-60s`; allow `60-90s` when the approved narration is naturally longer. Do not compress a good spoken script just to hit a number.
- Video type: faceless book-review/read-book insight clip.
- Rhythm: fixed opener, then one visual beat per sentence or half-sentence.
- Motion: restrained slow push, pan, vertical lift, slight drift, or subtle mist/parallax. Vary the treatment by scene; avoid fast cuts and busy transitions.
- Tone: human, oral, and opinionated. Avoid polished AI-summary phrasing.

## Default Narration Pattern: Hook-First Five-Part Script

This is now the default script mode for new book-account videos unless the user explicitly asks for the old fixed spoken opener.

Before drafting:

1. List 3 core viewpoints of the book.
2. Select the single most counterintuitive / offensive viewpoint.
3. Write the whole script around only that one viewpoint.

Output for user review must include the 3 viewpoints, the selected viewpoint, then the script.

Five-part structure:

1. **Hook in first 3s**: first sentence is a counterintuitive claim, painful question, or concrete disturbing scene. It must be book-specific. If it can fit another book, rewrite.
2. **Book title in sentence 2 or 3**: do not start spoken audio with `今天分享的是...` by default.
3. **Grounded case**: use a real argument or original example from the book. Do not invent a lifestyle example just to make it "relatable". If uncertain, verify from a reliable source or ask the user to confirm the example first.
4. **Emotional reversal**: include one turn such as `听起来很冷血对吧？但这本书真正想说的，恰恰相反。` Then explain for no more than 4 sentences.
5. **Controversial comment ending**: end with a question viewers can argue about.

Language:

- Oral and conversational, like talking to a friend.
- Use `你` often, but not mechanically.
- Alternate short impact lines with longer setup lines. Do not chop all lines into 5-8 character fragments.
- Keep each sentence under about 25 Chinese characters where practical.
- Avoid `首先/其次/最后`, translation tone, encyclopedia summary, and soft promotional language.
- Keep 1-2 gold lines maximum, placed after the reversal.

Reference pattern for 《自私的基因》:

```text
你有没有想过，你对家人的爱，可能是被"设计"出来的？

有一本书，四十多年来一直在得罪人，它就是道金斯的《自私的基因》。

它说了一个让人不舒服的真相：你不是基因的主人，你只是基因的载体。

母亲为什么愿意为孩子牺牲？这本书会告诉你，因为孩子身上有她一半的基因——保护孩子，就是基因在保护自己的副本。

听起来很冷血对吧？

但这本书真正想说的，恰恰相反。

基因是自私的，可人不必是。

我们是地球上唯一能对基因说"不"的物种。你选择善良、选择克制、选择不占那个便宜——每一次，都是在改写基因给你的剧本。

所以别再用"人性本来如此"给自己找借口了。

基因写了开头，但结局，握在你手里。

你觉得，人到底能不能战胜本能？评论区聊聊。
```

Pattern essence:

- One offensive thesis, not a survey of the book.
- Book-specific hook: love for family as gene design.
- Real book-grounded example: parent-child genetic relatedness / kin selection logic.
- Reversal: the book looks cold but actually opens room for human choice.
- One or two memorable lines only: `基因是自私的，可人不必是。` and `基因写了开头，但结局，握在你手里。`
- Ending asks a fight-worthy question.

## Old Fixed Opener

Use this only when the user explicitly asks for the fixed account opener or when continuing an older project built with that style.

Use a reusable account opener, but generate the voice in one pass with the main narration:

```text
今天分享的是，《本期书名》。
```

Visual opener:

- 0.0-4.0s-ish depending on TTS timing.
- Display `今天分享的是` then full book title.
- The first real hook must be heard or readable within `3-5s`; if the spoken opener takes most of that time, reveal the hook caption immediately after the title phrase.
- Style must match the main captions: large heavy Chinese, white or blue-white fill, thick black outline/shadow.
- Add a small transition into the body if it helps, but keep it understated.
- Keep enough vertical spacing between top title, author line, opener subtitle, and book visual. Do not let small opener text cling to the book/card edge.

## Script Formula

For legacy fixed-opener scripts, use this beat structure as a guide, not a rigid template:

1. Opener: `今天分享的是，《书名》。`
2. Main hook: one sentence that makes the viewer feel "this is about me" within the first few seconds.
3. Reframe the book: one clear contrast or reversal. `不是 X，而是 Y` can work, but do not force it if it sounds templated.
4. Two relationship/human-nature observations.
5. One practical warning or boundary insight.
6. Closing sentence: `这不是冷漠，是成年人保护自己的开始。` or a theme-specific equivalent.

Good sentence traits:

- Short, oral, calm.
- One idea per sentence.
- Uses contrast when it is natural: `不是...而是...`, `看起来...其实...`.
- Avoids plot summary unless the user asks for plot.
- Has a person behind it: a judgment, a little friction, a specific warning, not a smooth encyclopedia summary.
- Avoids clustered AI tells: repeated neat contrasts, generic "真正写的", slogan-like endings, grand abstractions, and perfect parallelism.

## Narration Self-Review Gate

Before TTS, self-review and revise the narration, then stop and show the user the best candidate for approval.

Also show a compact audit:

- Hook: which line prevents swiping in the first `3-5s`.
- Self-review changes: what was changed after the first draft.
- Human flavor: what makes it sound like a person, not an AI summary.
- Caption-preserved lines: logic sentences whose core words must stay in subtitles.
- Risks: any sentence that may feel too formulaic or too long.

If `renwei-writing` is available, read its `SKILL.md` and post-edit checklist before presenting the narration. Apply its principles lightly: do not over-polish; keep oral roughness where it helps.

Do not show a raw first draft unless the user explicitly asks to see rough options. The normal approval artifact is the self-reviewed version the agent believes is ready to produce.

## Visual Rules

Select visuals by content meaning, not by copying the reference video's exact footage.

Recommended motifs, selected by topic:

- Books, candlelight, windows, doors, tea, courtyards, ledgers, coins, rain, shadows.
- For crowd/psychology/cognition books: crowds, public spaces, windows, newspapers, screens, notebooks, solitary figures, books.
- For wealth/business books: desks, ledgers, markets, city light, receipts, tools, office scenes, books.
- For literary/human-nature books: old books, courtyards, tea, doorways, candlelight, rain, shadows.
- Fallback hierarchy: literal content match, theme-adjacent imagery, then emotionally matched scenery.
- If literal images look forced or inconsistent, use one coherent world of evocative scenery: misty mountains, rivers, forests, paths, solitary trees, rain, clouds, or boats.
- In scenic fallback mode, captions carry the argument and landscapes carry the emotion. Do not force every sentence into a literal stock-photo illustration.
- Animate scenic stills with varied, restrained motion. Alternate slow push, horizontal pan, vertical lift, slight drift, and subtle mist/parallax rather than repeating the same zoom.
- Choose the brightness by the subject. Dark is only one option, not the default.
- Use clean contrast areas behind captions, but keep the main image readable with visible midtones.

Avoid:

- Real film/TV faces or recognisable dramatic stills.
- Erotic or sensational imagery.
- Bright stock-like scenes.
- Busy textures behind captions.
- Over-dark grading that hides the subject and makes the video feel muddy.

## Caption Style

- Chinese caption: 68-78px for normal lines; 90-120px for cover image hero text.
- Heavy black outline/shadow; white fill; occasional warm-gold/blue-white accent.
- Main video captions should be 1-2 lines where possible.
- For sync-critical previews, use hard-cut captions: no fade, no blur, no stagger.
- Optional English subtitle can add texture, but do not let it compete with Chinese.
- When a scene has multiple semantic beats, old caption lines must hide via `data-hide` so the current spoken point stays visually dominant.
- Do not over-compress important logic sentences. For lines with `不是...而是...`, `最危险的不是...而是...`, or a book's core thesis, subtitles should preserve the key words from the narration.

## Audio Rules

- Generate the approved narration as one TTS file; do not splice a separate intro voice into it.
- Default opener is voice-free: play visual SFX/BGM for `3.56s`, then start the TTS. Shift all scene and caption cues by the same `3.56s` offset.
- If the reusable opener contains reference speech, separate it with Demucs and use only the `no_vocals` stem. The final master may contain only this episode's TTS, opener SFX, and BGM.
- Mix with `amix=normalize=0` so a short SFX bed is not automatically divided down by the number of input tracks. Confirm the first `3.56s` has audible peaks.
- Keep BGM subtle.
- Use one final master audio file in the composition.
- Treat final audio as the source of truth for `data-duration`.

## Packaging Rules

- The cover should match the video's visual world and brightness; scenic fallback is fine when literal book imagery is weak.
- The title must be faithful to the book's actual argument. Prefer a specific question or tension from the thesis over a generic formula such as "看透人性".
- Save the final title and posting body to `docs/posting-copy.md` as well as returning them in chat.

## Lessons Learned

- Separate intro TTS splicing can make breath, loudness, and emotional pacing feel wrong.
- Caption animation can make correctly timed subtitles feel late; remove it when debugging sync.
- Static silence detection is not enough for Chinese TTS. Use token timestamps when possible, then manually verify.
- Use local word timestamps on the clean voice track. `faster-whisper` is a practical fallback when a `whisper-fast` executable is not installed; use its recognized text for timing only, because Chinese names and homophones can be wrong.
- Keep the approved narration as the subtitle source of truth. Normalize and compare the concatenated caption text against the narration before preview; no omitted words or silent paraphrases.
- Rebuild scene boundaries around sentence and semantic-beat boundaries after timing. Do not preserve a storyboard duration if it cuts through a spoken sentence.
- If Whisper is slow or unreliable, use `ffmpeg silencedetect` as the fallback to place first-pass cue boundaries, then visually check key snapshots.
- A caption can be "on time" but still feel wrong if old lines remain onscreen. Hide stale lines.
- Screen captions that over-summarize the voice feel like missing words. Audit text against the narration before preview.
- Contact sheets should be checked for brightness. If the image reads as black-on-black except for text, raise exposure or reduce overlay.
- Generate a fresh visual asset set for each book. Reuse the motion grammar and opener structure, not the previous episode's footage.
- Pre-crop wide generated or downloaded images to intentional portrait assets before scene assembly; otherwise the vertical `object-fit: cover` crop can remove the narrative subject.
- HyperFrames render should happen only after the user approves the browser preview.
- After rendering, inspect an MP4 contact sheet at the hook, example, reversal, warning, and closing question. A successful browser preview alone does not certify the export.
