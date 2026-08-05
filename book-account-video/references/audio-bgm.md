# Audio: TTS + Glass SFX + Mandatory BGM

## 硬规则

| 门 | 内容 |
| --- | --- |
| BGM | **禁止无 BGM 成片**；master 必须混氛围底 |
| 人声 | **仅本期 TTS** 一种音色；禁止贴爆款口播床 |
| 片头 SFX | 建议有碎玻璃/whoosh；用 Demucs 从参考片拆 **no_vocals**，或干净素材库 |
| 黑场 | 停顿靠旁白气口，不靠长静音黑屏 |
| 单轨 | `index.html` 只挂 `master_with_intro.wav` |

```text
master_with_intro.wav =
  本期 TTS 全段
  + opener_sfx_glass（0–~2.5s，Demucs 去人声）
  + 全程弱 BGM（0.08–0.12）
  → loudnorm ≈ -14 LUFS / -1 dBTP
```

当前默认变体是**无口播片头**：片头 SFX/BGM 播放 `3.56s`，本期 TTS 从 `3.56s` 开始。旁白延迟后，场景和字幕 cue 表也必须整体加 `3.56s`。

## 1. TTS 干声

见 `doubao-tts.md`。

- **一次合成**含「今天分享的是，《书名》」+ 正文（禁止片头旁白拼接）
- 语速约 `0.88–0.92`
- 输出：`audio/voiceover_with_intro.mp3`

## 2. 片头 SFX（推荐）

### 正确：Demucs 去人声

```bash
# 从参考片截 0–2.55s 音轨
ffmpeg -y -i ref.mp4 -t 2.55 -vn -ac 2 -ar 48000 audio/opener_bed.wav

# 分离（需 demucs + numpy）
python3 -m demucs --two-stems=vocals -n htdemucs audio/opener_bed.wav -o audio/demucs_out
# → audio/demucs_out/htdemucs/opener_bed/no_vocals.wav

ffmpeg -y -i audio/demucs_out/htdemucs/opener_bed/no_vocals.wav -af "
  highpass=f=120,volume=1.3,afade=t=out:st=2.28:d=0.25
" -ar 48000 audio/opener_sfx_glass.wav
```

### 禁止

| 错 | 为什么 |
| --- | --- |
| 整段 `opener_bed` 进 master | 带别人男/女声 |
| 仅 highpass「抢救」当主 SFX | 易残留人声且难听 |
| 合成噪点冒充玻璃当唯一方案 | 可用但质感弱于 Demucs 实采 |

## 3. BGM

优先级：

1. `media-use` resolve `--type bgm`
2. 项目/全局缓存
3. 既往冷静钢琴兜底

Mode A intent 示例：`melancholy soft piano rain ambient bed low` / `calm ambient piano soft emotional no lyrics`

禁止有歌词人声、禁止大鼓点盖口播。

## 4. 混音示例

```bash
VO=audio/voiceover_with_intro.mp3
SFX=audio/opener_sfx_glass.wav
BGM=audio/bgm.mp3
OUT=audio/master_with_intro.wav

DUR=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$VO")
FADE_ST=$(python3 -c "print(max(0, float('$DUR')-0.8))")

ffmpeg -y \
  -i "$VO" \
  -i "$SFX" \
  -stream_loop -1 -i "$BGM" \
  -filter_complex "
    [0:a]aformat=sample_fmts=fltp:channel_layouts=stereo,volume=1.0[vo];
    [1:a]aformat=sample_fmts=fltp:channel_layouts=stereo,volume=0.85,apad=whole_dur=${DUR}[sfx];
    [2:a]aformat=sample_fmts=fltp:channel_layouts=stereo,volume=0.09,afade=t=out:st=${FADE_ST}:d=0.8,atrim=0:${DUR}[bg];
    [vo][sfx][bg]amix=inputs=3:duration=first:dropout_transition=0:normalize=0,
    loudnorm=I=-14:TP=-1.0:LRA=11
  " -t "$DUR" -ar 48000 -ac 2 "$OUT"
```

验收：

- [ ] 片头有碎玻璃/氛围，**无串戏人声**
- [ ] 旁白清晰，BGM 有空气
- [ ] 无整段死寂；结尾 fade 不硬切

## SFX-only opener mix

当用户选择无口播片头时：

```bash
INTRO=3.56
DUR=FINAL_MASTER_DURATION

# 参考片头先分离人声；只使用 no_vocals stem
python3 -m demucs --two-stems=vocals -n htdemucs opener_bed.wav -o audio/demucs_out

# 旁白延迟到片头结束；视觉 scene/caption 时间也加 INTRO
[0:a]adelay=3560|3560,atrim=duration=${DUR}[vo]
```

混音时显式写 `amix=normalize=0`。否则三轨输入会把短片头音效自动摊薄，出现“片头没有声音”的错觉。完成后分别检查 `0–3.56s` 与 `3.56s` 后的响度和波形，确认片头有峰值、正式旁白没有被截掉。

## 5. 写入合成

```html
<audio id="master-audio"
  src="audio/master_with_intro.wav"
  data-start="0"
  data-duration="D.DDD"
  data-track-index="0"
  data-volume="1"></audio>
```

`data-duration` = master 精确时长。

## 登记

`docs/asset_sources.md`：TTS 音色、BGM 来源、SFX 是否 Demucs / 素材库。
