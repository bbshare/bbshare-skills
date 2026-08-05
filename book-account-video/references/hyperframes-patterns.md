# HyperFrames Patterns

## Environment

```bash
export PATH="$HOME/.local/bin:$PATH"   # Node ≥ 22 for hyperframes
```

## Project Shape

Single `index.html`, `1080x1440`, `data-duration` = **master** audio length  
（`audio/master_with_intro.wav` = 旁白 + **BGM**，见 `audio-bgm.md`）。

Mode A 典型场景序：

1. `scene-opener` — 碎玻璃片头（`opener.md`）
2. `scene-body-a` — 情绪静帧 1 + 短句字幕轮换
3. `scene-body-b`（可选）— 静帧 2，中段切换

固定 UI：顶书名 + 作者；底水印；中下字幕。

```html
<div id="root" data-composition-id="main" data-width="1080" data-height="1440" data-duration="46.416" data-fps="30">
  <audio id="master-audio" src="audio/master_with_intro.wav" data-start="0" data-duration="46.416" data-track-index="0"></audio>
</div>
```

`<audio>` must be a direct child of root. `<video>` backgrounds also as direct children of scene or use class="photo" on video inside scene — per hyperframes-core, video playback is framework-owned.

## Scenes

One full-screen section per beat. Image or video background:

```html
<section id="scene-04" class="clip scene rain" data-start="17.82" data-duration="4.02" data-track-index="4">
  <img class="photo" src="assets/generated/scene-04-rain-window.jpg" alt="" data-layout-ignore>
  <div class="atmosphere cool" data-layout-ignore></div>
  <div class="rain-overlay" data-layout-ignore></div>
  <div class="caption mid" data-layout-allow-occlusion>
    <span class="zh tight" data-reveal="17.82" data-hide="19.63">老妇人只回了一句</span>
    <span class="zh tight gold" data-reveal="19.63">我不拔，就会饿死</span>
  </div>
</section>
```

Video background variant:

```html
<video class="photo" src="assets/library/rain-01.mp4" muted loop playsinline data-layout-ignore></video>
```

## Captions — hard cut only

```css
.caption span { opacity: 0; transform: translateY(0); filter: none; }
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

Use `data-hide` when one scene has multiple semantic beats.

## Motion

See `references/motion.md`. Register one paused GSAP timeline at `window.__timelines["main"]`.

## package.json scripts

```json
{
  "scripts": {
    "dev": "npx hyperframes play --port 3004 --no-open",
    "check": "npx hyperframes lint && npx hyperframes validate && npx hyperframes inspect",
    "render": "npx hyperframes render --quality high --output renders/final.mp4"
  }
}
```

## Validation pipeline

```bash
npm run check
npx hyperframes snapshot --at 1.0,6.5,12.0,19.0,24.5,31.0,38.0,43.5 --output snapshots/check-v1 --describe false
npx hyperframes play --port 3004 --no-open
```

Render **only after user approves** preview:

```bash
npx hyperframes render --quality high --output renders/final.mp4
ffprobe -v error -show_entries format=duration,size -of json renders/final.mp4
```

## Caption / brightness audit

- Compare captions to `audio/voiceover_with_intro.txt`
- Preserve core words in thesis lines
- Contact sheet must show visible midtones, not text-only on black