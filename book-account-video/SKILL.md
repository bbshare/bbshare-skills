---
name: book-account-video
description: "Create Douyin/TikTok-style Chinese book-account short videos (读书笔记/书评短视频) from a book title or theme. Use when the user wants to make, iterate, preview, render, or publish a faceless book-review clip with hook-first monologue, captions, mandatory BGM, cover, and posting copy. Two visual lines: (A) 听页 glass+book cards; (B) sample-style brush two-char opener + landscape side-profile + bilingual ZH/EN captions + burned-in first-frame cover. Natural narration length wins over arbitrary duration caps. Hard gate: stop for narration/content-pack approval before TTS when required. Default Mode A = emotional-license monologue. Uses HyperFrames + Doubao TTS."
---

# Book Account Video（读书笔记 / 书评短视频）

对标账号形态：`@听页/书评分享` 类爆款结构 + **样例线**（毛笔两字 / 山水人物 / 中英字幕）。  
**借鉴结构与气质，自建画面与 UI，禁止贴爆款原片当片头。**  
默认交付 **情绪许可证 monologue**，不是百科书评、不是情节解说。

## 双视觉线（先选线再开工）

| 线 | 名称 | 何时用 | 规格摘要 |
| --- | --- | --- | --- |
| **A（默认）** | **听页线** | 未指定；系列玻璃账号 | 碎玻璃 + 浮层书卡；默认 3.56s 无口播片头；中文大字；2–3 情绪场 |
| **B** | **样例线** | 用户给 sample、要毛笔两字 / 中英 / 山水侧脸 | 首帧封面烧录 + 两字毛笔裂口 + 书封 3D 轮播 + 5 镜半屏人物；VO 可从 0 起 |

- **一集只选一线**，禁止玻璃片头 + 毛笔片头混剪。  
- **B 线必读**：`references/visual-line-sample.md`  
- **A 线必读**：`references/opener.md`

参考成片：

| 项目 | 线 | 要点 |
| --- | --- | --- |
| `renxingderuodian-video` | A | 片头/系列资产 |
| `luoshengmen-video` | A | Whisper 对轴 + 正片多层动效 |
| `huozhe-video` | A | 文案四轮：说破 + A-密 |
| **`huozhe-sample-video`** | **B** | **样例线终态**：撑着 / 中英 / 首帧封面 / 半屏人物 |

## Hard Gates（不可跳过）

1. **旁白 / 内容包门**：写完旁白（B 线含 **两字主情绪 + 中英表**）并自检后，**必须停下**交给用户。**明确通过前**禁止 TTS / 大体积出图 / `index.html` 成片预览 / render。用户明确「直接做 / 按样例做」可边做边以 content-pack 为据，仍须落盘文稿。  
2. **画面审核门**：预览 / snapshot 给用户后，**批准前禁止 render**（用户已说导出且画面已批除外）。  
3. **导出包（硬门）**：render 成功后同一回合必须落盘：  
   - `covers/cover.png` + `cover.jpg`  
   - `docs/posting-copy.md`  
   - **B 线另验**：成片 **第 0 帧非黑屏**（首帧封面烧录）  
4. **BGM 硬门**：禁止无 BGM 成片。  
5. **人声硬门**：仅本期 TTS 一种音色。  
6. **片头硬门（按线）**：  
   - **A**：0–3.56s 默认可无口播，仅 SFX+BGM；旁白从 3.56s 起则场景/字幕整表偏移。  
   - **B**：0 帧必须是封面；毛笔裂口 + 书封三动效；VO 可与画面同起。  
7. **对轴硬门**：延迟旁白则场景与字幕同步偏移；Whisper 对中文。  
8. **标题硬门**：落在本书真实核心，禁止泛化「看透人性」。  
9. **B 线人物硬门**：正片人物约占 **≤半屏高**；每镜 **动作姿势不同**。

## Tooling

Read before implementation:

1. `references/viral-formula.md` — 为何这样拍  
2. `references/method.md` — 旁白 / 说破 vs 疗愈 / A-短·A-密  
3. **线 A** → `references/opener.md`  
4. **线 B** → `references/visual-line-sample.md`  
5. `references/audio-bgm.md` · `references/doubao-tts.md`  
6. `references/lessons-learned.md`  
7. `references/packaging.md` — 封面 + **首帧烧录** + 文案  
8. `hyperframes` → `hyperframes-core` → `hyperframes-cli`  
9. `imagine` / `media-use` 按需  

```bash
export PATH="$HOME/.local/bin:$PATH"
# Node ≥ 22（推荐 24+）
```

## 双模式（文案 · 与视觉线正交）

| 模式 | 名称 | 何时用 | 目标时长 |
| --- | --- | --- | ---: |
| **A（默认）** | **情绪许可证 monologue** | 用户未指定 | **31–36s** 短；或 **A-密 45–90s** |
| **B（可选）** | **单观点书评** | 用户明确要情节/论证 | **35–45s** 体感 |

### Mode A 本质

> 用一本书当权威背书，讲一句观众已经隐隐觉得、但需要别人替自己说出口的话。

- 书名 = 可信度标签  
- 文案 = 情绪许可证（默认 **说破/站队**，不是疗愈摸头）  
- **线 A 画面** = 2–3 情绪场 + 雨雾粒子  
- **线 B 画面** = 两字情绪 + 5 镜山水同角 + 中英字幕  
- 密度 = 默认 A-短；嫌像诗 → A-密  

选题过滤器：

> **删掉书名，这句话还能否让人想转发？**  
> **想转的人是在站队，还是只被摸头安慰？**

## Workflow

### 1. 收集输入 + 选视觉线

- **必填**：书名或主题  
- **选填**：视觉线 A/B、水印、作者行、工作目录  
- **默认规格**：`1080×1440` · 30fps  
- 用户贴 sample / 说中英、毛笔 → **线 B**；否则 **线 A**

### 2. 写旁白 / 内容包 → **STOP**

读 `method.md`。  

| 线 | 交付 |
| --- | --- |
| A | `docs/narration-review.md`（候选许可证 + 正文 + 审核摘要） |
| B | 同上，或 `docs/content-pack.md`：**两字 ⭐** + 正文 + **中英字幕表** + 分镜意图 |

用户打回文案：见 method（dbs-resonate / spread / hook；禁止只建议不落定稿）。

### 3. 批准后：配音 + BGM（+ SFX）

读 `audio-bgm.md`、`doubao-tts.md`。

1. 一次 TTS（批准正文）  
2. 线 A：`opener_sfx_glass` + 可选 3.56s 垫静音  
3. 线 B：VO 可从 0 起；弱 BGM + 可选短 SFX  
4. `amix=normalize=0` · loudnorm ≈ -14 LUFS  
5. `data-duration` = master 时长  

### 4. 视觉资产

| 线 | 读 | 资产 |
| --- | --- | --- |
| A | `opener.md` · `visual-sourcing.md` | `assets/opener/op-glass*` · brand 书卡 · scene-a/b/c |
| B | **`visual-line-sample.md`** | `first-frame.jpg` · `brush-chars.png` · `books/*` · `char-ref` · scene-a…e **半屏人物** |

登记 `docs/asset_sources.md`。

### 5. 搭建 HyperFrames

**线 A 时间轴**（无口播片头默认）：

| 时间 | 内容 |
| ---: | --- |
| 0–0.85 | 碎玻璃 |
| 1.05–2.6 | 三书卡交错 |
| 2.6–3.56 | hold → dissolve |
| 3.56+ | 旁白 + 字幕 + 正片 |

**线 B 时间轴**：

| 时间 | 内容 |
| ---: | --- |
| 0–0.45 | **首帧封面烧录** |
| 0–2.7 | 两字毛笔 + 天空裂口 + 钩子中英 |
| 2.55–6.3 | 书封 3D 轮播 |
| 6.1+ | 正片 5 镜 + 顶栏 + 中英字幕 |

**UI（按线）**

| 元素 | 线 A | 线 B |
| --- | --- | --- |
| 顶栏书名 | 白/冰蓝 + glow | 白字厚描边即可 |
| 作者 | **橙色** | 白/浅灰 |
| 字幕 | 中文 `.zh.tight` | **中文 + 英文小行** |
| 水印 | `@读书笔记 · 书评分享` | 同 |

### 6. Whisper 对轴

```bash
export KMP_DUPLICATE_LIB_OK=TRUE
export OMP_NUM_THREADS=1
# faster-whisper 词级时间 → docs/whisper_cues.md / cues.json
```

- 映射 **中文口播**；线 B 英文跟中文同 reveal/hide  
- 近音归一（发讲→发奖、鱼花→余华…）  
- 禁止为躲书卡拖后字幕  

### 7. 预览与自检

```bash
npx hyperframes lint
npx hyperframes snapshot --at 0,0.5,1.5,3.5,6,12,20,30 --output snapshots/check-v1 --describe false
npx hyperframes play --port <available> --no-open
```

**必查第 0 帧**（`--at 0`）：线 B / 任意线均 **禁止首帧纯黑**。

清单：

- [ ] 线正确（A 或 B，未混）  
- [ ] 线 A：玻璃在动、书卡三交错；或 线 B：裂口+光带+书卡 3D  
- [ ] Whisper 对轴  
- [ ] 正片动效不重复；线 B 人物半屏、姿势多样  
- [ ] 仅本期人声 + BGM  

**→ 用户批准画面。**

### 8. 导出 → 封面 → 文案（同一回合）

```bash
npx hyperframes render -o output/<slug>.mp4 -q high
# covers/cover.html → Chrome headless → cover.png + cover.jpg
# 线 B：同步 sips/复制 cover → assets/opener/first-frame.jpg（下次合成用）
# docs/posting-copy.md
```

**验收：**

- [ ] `output/*.mp4` 可播 · 1080×1440 H.264 + AAC  
- [ ] `covers/cover.png`  
- [ ] `docs/posting-copy.md`  
- [ ] **`ffmpeg` 抽第 0 帧非黑屏**（线 B 硬门；线 A 也建议）  

## 换书最小改动

| 线 A | 线 B |
| --- | --- |
| 旁白+TTS+master | 旁白+两字+中英表+TTS+master |
| Whisper 全表 | Whisper 全表 |
| 顶栏书名作者 | 顶栏 + 毛笔两字重渲 + first-frame |
| 2–3 主视觉 | char-ref + 5 镜半屏重出 |
| 封面+文案 | 封面+文案+first-frame 同步 |

## 项目结构

```
<project>/
  index.html
  audio/          master*.wav · voiceover* · bgm · sfx
  assets/
    opener/       # A: glass/brand  |  B: first-frame · brush-chars · sky
    books/        # B: 书封轮播
    generated/    # 正片；B 含 char-ref
    fonts/
  docs/
    narration-review.md | content-pack.md
    asset_sources.md
    whisper_cues.md · cues.json
    posting-copy.md
  covers/
  snapshots/
  output/
```

## References

| 文件 | 用途 |
| --- | --- |
| `references/visual-line-sample.md` | **线 B 样例线终态（必读）** |
| `references/opener.md` | 线 A 玻璃/书卡 |
| `references/method.md` | 旁白；说破/疗愈；A-短/A-密 |
| `references/lessons-learned.md` | 复盘（含活着文案 + 样例线） |
| `references/packaging.md` | 封面、首帧烧录、发布文案 |
| `references/audio-bgm.md` | 混音 |
| `references/doubao-tts.md` | TTS |
| `references/visual-sourcing.md` | 出图 |
| `references/viral-formula.md` | 爆款公式 |
| `references/motion.md` | 动效 |
| `references/hyperframes-patterns.md` | 合成校验 |

## Scripts

- `scripts/doubao_tts_v3_api_key.py` — Doubao Speech HTTP V3 TTS
