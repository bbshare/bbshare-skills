# HyperFrames Patterns

## Project Shape

Use a single `index.html` composition unless the project becomes unusually large.

Root:

```html
<div id="root" data-composition-id="main" data-width="1080" data-height="1440" data-duration="38.952" data-fps="30">
  <audio id="master-audio" src="audio/master_with_intro.wav" data-start="0" data-duration="38.952" data-track-index="0"></audio>
</div>
```

Keep `<audio>` as a direct child of the root.

## Scenes

Use one full-screen section per beat:

```html
<section id="scene-04" class="clip scene" data-start="15.04" data-duration="5.00" data-track-index="4">
  <img class="photo" src="assets/pixabay/tea-cup.jpg" alt="" data-layout-ignore>
  <div class="caption low" data-layout-allow-occlusion>
    <span class="zh" data-reveal="15.04">有些关系</span>
    <span class="zh gold" data-reveal="16.00">看起来是情分，其实是交换</span>
  </div>
</section>
```

## Captions

For final sync reliability:

```css
.caption span {
  opacity: 0;
  transform: translateY(0);
  filter: none;
}
```

```js
captionLines.forEach((line) => {
  const revealAt = Number.parseFloat(line.dataset.reveal);
  const hideAt = Number.parseFloat(line.dataset.hide || "NaN");
  tl.set(line, { opacity: 1, y: 0, filter: "none" }, revealAt);
  if (Number.isFinite(hideAt)) {
    tl.set(line, { opacity: 0, y: 0, filter: "none" }, hideAt);
  }
});
```

Do not use fade/blur/stagger while debugging voice-caption sync.

Use `data-hide` whenever one scene contains multiple semantic beats:

```html
<span class="zh" data-reveal="30.60" data-hide="34.99">当你站在人群里</span>
<span class="zh" data-reveal="32.47" data-hide="34.99">最危险的不是被别人骗</span>
<span class="zh" data-reveal="34.99">是把别人的声音</span>
<span class="zh" data-reveal="36.45">误以为是自己的想法</span>
```

Caption audit before preview:

- Compare every important caption to `audio/voiceover_with_intro.txt`.
- Keep core words in thesis lines. Do not reduce `而是一个人一旦进入群体，判断力会怎样被情绪接管` to `是进入群体之后`.
- Check that only the current point is visually dominant; stale text should hide.
- Use the approved narration as the exact caption source. ASR timestamps locate the cue, but ASR characters do not get copied into the final subtitle.
- Audit the normalized concatenation of all caption spans against the narration file. Remove only whitespace and punctuation; the remaining character sequences must match exactly.
- Move scene boundaries to sentence or semantic-beat boundaries. A sentence must not be cut by a scene transition just because the old storyboard used a fixed duration.
- Capture snapshots at cue boundaries, especially around `not/but`, warning, and closing beats.

Brightness audit before preview:

- Contact sheets should show visible subjects and midtones, not only white text over near-black images.
- Darken the caption area with overlays if needed; do not darken the entire image by default.
- For dark sources, raise `brightness()` first and rely on text outline/shadow for readability.

## Validation

Run before preview/render:

```bash
npm run check
```

Use snapshots for visual checks:

```bash
npx hyperframes snapshot --at 4.1,8.2,15.2,20.2,35.2 --output snapshots/check-v1 --describe false
```

Preview:

```bash
npx hyperframes play --port 3003 --no-open
```

Render only after user approval:

```bash
npx hyperframes render --quality high --output renders/final.mp4
```

Verify render:

```bash
ffprobe -v error -show_entries format=duration,size -show_entries stream=codec_type,codec_name,width,height,r_frame_rate -of json renders/final.mp4
```
