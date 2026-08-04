# Packaging: Cover And Posting Copy

## Cover

Default cover size: `1080x1440`.

Cover structure:

- Same visual world as the video. Match the video's brightness and subject; do not force a dark cover.
- Book cover or book/candle still-life as the visual anchor.
- One large hook line.
- Full book title as secondary text.
- Optional short insight line.
- Bottom watermark/account name.

The cover does not need to show a literal book if the available image is weak. A coherent, emotionally matched landscape is acceptable, but keep the central hook and full book title readable at `1080x1440`.

Recommended hook patterns:

- `别把人性\n想得太干净`
- `有些情分\n其实是交换`
- `成年人要懂\n人性的边界`
- `这本书\n把人性写透了`
- `别把群体的声音\n当成你的想法`
- `别在人群里\n丢掉判断力`
- `你以为是选择\n其实是跟风`

Choose hook patterns from the video's actual thesis. Do not reuse human-nature hooks for wealth, cognition, crowd psychology, or history books when a more specific hook is available.

Use the HTML template in `assets/cover-template.html`, render with Chrome headless:

```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --headless=new --disable-gpu --hide-scrollbars \
  --window-size=1080,1440 \
  --screenshot=covers/cover.png \
  file:///ABSOLUTE/PATH/TO/covers/cover.html
```

Export JPG if needed:

```bash
magick covers/cover.png -quality 92 covers/cover.jpg
```

## Posting Copy

Recommended title direction:

```text
用书中真实的核心矛盾提问，再带出《书名》
```

Do not force a human-nature title onto psychology, addiction, wealth, cognition, or history books. For example, a faithful title for 《成瘾》 is：

```text
为什么快乐越来越多，我们却越来越难满足？《成瘾》
```

Body formula:

1. One sentence reframing the book.
2. Two sentences summarizing the human insight.
3. One practical warning.
4. One closing boundary/self-protection line.
5. Hashtags.

Keep it readable on mobile. Avoid over-explaining the whole video.
Save the final title, body, and hashtags to `docs/posting-copy.md`.
