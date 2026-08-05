# 视觉线 B · 样例线（毛笔两字 + 山水侧脸 + 中英）

> 终态参考：`huozhe-sample-video`（2026-08 · 《活着》· 撑着）  
> 拆解源：`ref-teardown/sample-book-account/TEARDOWN.md` · `~/Documents/tools/yt-dlp/sample.mp4`  
> **与听页线（玻璃+浮层书卡）并列**；用户点名「按 sample / 中英 / 毛笔片头」时走本线。

---

## 何时用

| 信号 | 视觉线 |
| --- | --- |
| 默认、系列玻璃账号、无特别指定 | **A · 听页线**（`opener.md`） |
| 用户给 sample.mp4、要毛笔两字、中英字幕、山水人物 | **B · 样例线**（本文） |
| 只借文案/闸门、片头仍玻璃 | 文案用 method；片头仍 A |

**禁止**两套片头混剪同一集。

---

## 规格

| 项 | 值 |
| --- | --- |
| 画幅 | **1080×1440** · 30fps |
| 时长 | 旁白自然长；样例甜蜜 **~42–60s**（口播锁时码后全片） |
| 字幕 | **中文主行 + 英文装饰行**（每屏一对） |
| 顶栏 | 白字书名 + 白/浅灰作者（**非**听页橙作者强制） |
| 水印 | 默认 `@读书笔记 · 书评分享` |
| 音频 | VO 可从 **~0s 起**（钩子与两字同步）；BGM 全程；可选短 SFX |

与听页线差异：样例线 **不要求 3.56s 静默片头**；钩子先于或同步报书名。

---

## 内容包（Gate 1 · 先于 TTS）

`docs/content-pack.md` 或并入 `narration-review.md`：

1. **核验书名/作者**  
2. **两字主情绪**（从书内核提炼，不是随便形容词）  
3. **~60s 内**逐字稿（可 A-密收紧）  
4. **中英字幕表**（口播中文定稿 + 英文意译）  
5. **分镜意图**（5 镜左右：远行 / 分叉 / 坐 / 走 / 收束）  

### 两字规则

| 要求 | 说明 |
| --- | --- |
| 2 个汉字 | 书法可写、信息流可认 |
| 贴书 | 《活着》→ **撑着**；样例《钢铁…》→ **自救** |
| 删书名仍想转 | 两字本身是情绪许可证标签 |
| 备选 2–3 个 | 写进 content-pack，选定标 ⭐ |

开场钩子中英各两行，服务两字（例：日子把你掏空以后 / 还能撑着往下过）。

**→ STOP 等用户确认内容包（或用户已说「直接做」则选定后执行）。**

---

## 时间轴终态（B 线）

| 时间 | 内容 |
| ---: | --- |
| **0–0.45** | **首帧封面烧录**（`first-frame.jpg` = 封面构图） |
| 0.28–0.55 | 封面 dissolve → 毛笔片头 |
| 0–2.7 | 两字毛笔 + 天空裂口动效 + 开场钩子中英 |
| 2.55–6.3 | **书封 3D 轮播** ×3（系列感；可与本期书不同） |
| 6.1+ | 正片 5 镜山水人物 + 顶栏 + 中英字幕 + 水印 |

音频：master ≈ VO 时长；旁白与画面从 0 对齐（封面层只盖视觉）。

---

## 片头硬规格

### 1. 首帧封面（硬门 · 2026-08）

| 禁止 | 正确 |
| --- | --- |
| t=0 整屏黑（黑幕 scaleY=1 未开） | **0 帧可见封面图** |
| 只靠平台上传封面、成片第 0 帧仍黑 | 封面 **烧进 MP4 时间轴** |

实现：

```text
assets/opener/first-frame.jpg  ← covers/cover.png 导出
#op-poster  z-index 最高
  0–0.28s  opacity 1
  0.28–0.55s dissolve
#op-brush  在下方同步开跑，交叉淡入时已有动效
```

CSS 建议：`#op-poster { opacity: 1 }` 初始写死，避免 GSAP 首帧前黑闪。  
验收：`ffmpeg -i output.mp4 -vf "select=eq(n\,0)"` 第 0 帧 **不是黑屏**。

### 2. 两字毛笔

```text
Chrome headless 预渲染 brush-render.html
  → assets/opener/brush-chars.png
字内天空填充（background-clip 或 solid 天蓝兜底）
禁止依赖 HyperFrames 内 runtime background-clip  alone（易不可见）
```

动效（对标 sample，缺一少「冲」）：

| 层 | 动效 |
| --- | --- |
| 天空底 | Ken Burns 慢推 |
| 毛笔字 | mix-blend **screen**（黑底透出天空）+ 微缩放 |
| 上下黑幕 | **从中缝 scaleY 拉开**（sample 式裂口） |
| 光带 | 中缝高光展开再淡出 |
| 粒子 | 淡墨尘/光点漂移 |
| 钩子字 | 上下两句中英错落入场 |

### 3. 书封轮播

- 3 本封面图，**三种 3D 入场**（左旋 / 右旋 / 上浮），交错  
- `transformPerspective: 1400`，`overwrite: "auto"`  
- 模糊大底 + 居中书卡  
- 与本期书名可不同（系列感）

### 4. 嵌套 video 禁令

`<video data-start>` **禁止**塞在已有 `data-start` 的 section 内（会冻帧）。  
天空动感用 **静帧 + GSAP**，或 video 作为 stage **直接子级**独立 clip。

---

## 正片硬规格（山水 + 同角）

### 构图

| 规则 | 说明 |
| --- | --- |
| **人物 ≤ 约半屏高** | 远景/中远景；天空与环境占上半 |
| 同角一致 | 先 `char-ref` 再 `image_edit` 换场景 |
| 少正脸大头 | 侧脸 / 背影 / 侧身为主 |
| 5 镜左右 | 忌 1 张硬撑；忌每镜同一姿势 |

### 动作差异（必做）

每镜 **动作类型不同**，例如：

| 镜 | 动作例 |
| --- | --- |
| 1 | 远景背影独行 |
| 2 | 分叉路口侧立 |
| 3 | **坐凳**低头 |
| 4 | **迈步上坡**（发丝风动） |
| 5 | 海边闭眼仰脸（收束） |

出图 prompt 必须写清：`person only 25–45% of frame height` / `extreme wide` / 具体姿势。  
生成后 **读图验收**人物占比；仍占满半身特写 → 重出。

### 动效

每镜 **不同 Ken Burns**（推远 / 左移 / 上抬 / 跟步），禁止五镜同一 `scale 1.05→1.14`。

---

## 字幕（中英）

```html
<div class="cap" data-reveal="…" data-hide="…">
  <span class="zh">中文一句</span>
  <span class="en">English line</span>
</div>
```

- 中文：大白字厚黑描边，中下  
- 英文：小一号、斜体、半透明  
- Whisper 只对齐 **中文口播**；英文跟中文同 reveal/hide  
- 金句中文可 `.gold`

---

## 音频（B 线）

```text
master.wav = VO（一次 TTS）+ 弱 BGM + 可选片头 SFX
amix normalize=0 · loudnorm ≈ -14 LUFS
```

- 口播从 0 起即可（封面层不挡声）  
- 不强制 3.56s adelay；若加片头静音则 **字幕+场景整表偏移**

---

## 工作流（对齐作者五步 + 本 skill 闸门）

| 步 | 内容 | 闸门 |
| --- | --- | --- |
| 1 | 内容包：书 + 两字 + 稿 + 中英表 | **旁白/内容包门** |
| 2 | TTS 锁时码 + BGM/SFX master | — |
| 3 | 毛笔 PNG、书封、char-ref、5 镜半屏 | — |
| 4 | 合成 + Whisper + 首帧封面 | **画面门** |
| 5 | render + covers + posting-copy | **导出包门** |
| 可选 | 剪映草稿 | 用户明确要求再做 |

---

## 项目结构（B 线增量）

```text
assets/
  opener/
    first-frame.jpg      # 烧录首帧 = 封面
    brush-chars.png      # 两字毛笔预渲染
    brush-render.html
    sky-fill.jpg
  books/
    book-01.jpg … 03.jpg
  generated/
    char-ref.jpg
    scene-a-*.jpg … scene-e-*.jpg
docs/
  content-pack.md        # 两字 + 中英表 + 分镜
  narration-review.md    # 可与 content-pack 合并
  cues.json / whisper_*
```

---

## 验收清单（B 线）

- [ ] MP4 第 0 帧是封面，**非黑屏**  
- [ ] 片头有裂口/光带/粒子/书卡三动效，不是静贴图  
- [ ] 正片人物约半屏、姿势 ≥3 种不同  
- [ ] 中英字幕齐全；Whisper 对中文  
- [ ] 1080×1440 · 有 BGM · 仅本期人声  
- [ ] covers + posting-copy 同回合落盘  

---

## 反模式

| 错 | 对 |
| --- | --- |
| 首帧黑幕 | first-frame 烧录 |
| 毛笔 runtime clip 字不可见 | Chrome 预渲染 PNG |
| 人物半身特写占满 | 极端广角 + 读图返工 |
| 五镜同一站姿 | 坐/走/背影/仰脸拆开 |
| video 嵌套 timed section | 静帧 Ken Burns 或独立 clip |
| 与玻璃片头混用 | 一集只选 A 或 B |
