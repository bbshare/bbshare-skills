---
name: xhs-food-card
description: >
  Generate Xiaohongshu-style summer snack / dessert recipe poster cards with
  matching post copy: hero food photo + right-side ingredient/steps/calories
  infographic, plus detailed recipe, kcal estimate, and emotional 小情绪文案.
  Use when the user gives a food name and wants a poster, 小红书美食图, 夏日小零食
  卡片, 做法+热量+文案, recipe card like 杨枝甘露/西瓜椰奶西米 sample, or runs
  /xhs-food-card. Also trigger for "按那个模板出图", "再做一杯××", "发小红书的甜品图".
---

# 小红书夏日小零食海报 Skill

输入一个**食品名**（可附口味/人群备注），输出：

1. 一张与风格样例一致的竖版美食信息图  
2. 可直接发帖的标题 + 小情绪正文 + 标签  
3. 详细做法、食材克数、热量估算  

默认语言：**中文**。默认比例：**3:4**。

---

## When to use

- 用户只丢一个菜名/饮品名，要「出图 + 文案」
- 用户说「按上次杨枝甘露/西米露那个模板」
- `/xhs-food-card` 或「小红书甜品卡 / 夏日小零食海报」

不适用：纯菜谱文字、非食品、需要多页知识卡片长文（改走 `baoyu-xhs-images`）。

---

## Style anchor（必须）

风格样例路径（优先）：

1. 技能内：`{this-skill}/references/style-sample.png`
2. 工作区：`sample.png` 或用户 @ 的参考图
3. 若都没有：用下文「版式规格」纯文案还原，并告知用户可补参考图

**生成时**：用 `image_edit`，把 style-sample 作为第一张参考图，锁定版式/字体/信息栏气质；只替换菜品与文案内容。

详细版式见 `references/poster-spec.md`。  
文案模板见 `references/copy-templates.md`。

---

## Workflow

### Step 0 — 解析输入

从用户消息提取：

| 字段 | 必填 | 说明 |
|------|------|------|
| `food_name` | ✅ | 如「蜜桃乌龙冻」「芋圆仙草奶」 |
| `variant` | 可选 | 低卡/厚乳/懒人/一人份 等 |
| `kcal_target` | 可选 | 用户指定热量口径 |
| `output_dir` | 可选 | 默认 `summer-snack/` 或当前工作区下 `{slug}/` |
| `skip_image` | 可选 | 只要文案时跳过出图 |
| `batch` | 可选 | 多个菜名则逐个完整跑完再下一个 |

`slug`：食品名转拼音或英文 kebab-case，如 `mitao-wulong-dong`。

若名称含糊（只说「再来一个」「随便夏天的」）：从 `references/summer-menu-30.md` 推荐 3 个让用户选，或直接选一个最搭系列的。

---

### Step 1 — 内容策划（先写后画）

为该食品在脑中完成一张「内容卡」，再出图（避免图文不一致）：

1. **定位一句话**：解暑 / 低卡 / 茶饮复刻 / 古早冰 / 懒人 …
2. **副标**（竖排用）：`夏日××の××`（8 字以内气质）  
   例：`夏日解暑の清甜小确幸`、`夏日茶饮の治愈系甜品`
3. **红章**：默认 `夏日限定`；可换 `懒人友好` `低卡优选` `茶饮同款`
4. **食材 4–5 项**：名称 + 感官短句 + 约克数/毫升  
   每项必须能拍成小圆盘特写（颜色区分开）
5. **制作 4 步**：图标流：准备 → 核心加工 → 组装 → 完成享用
6. **风味特点**：1–2 句，口语、有画面
7. **饮用/食用建议**：3 条（冷藏 / 尽快吃 / 可调比例 等）
8. **热量**：一人份估算整数 + 口径说明（清爽版优先）

热量估算原则：

- 写「约 N kcal/份（估算）」
- 优先标**清爽可发版本**（少糖、椰浆可减半时注明）
- 脚注：`*以上热量为估算值，具体以实际食材为准`
- 正文里可附「满配版」对照，避免误导

---

### Step 2 — 出图

**工具**：优先 `image_edit`（参考 style-sample）；无参考时用 `image_gen`。

**比例**：`3:4`

**Prompt 结构**（必须包含）：

```
Using the reference image as the EXACT layout/typography/infographic system template,
create a new Xiaohongshu food recipe poster for: {中文全名}.

CRITICAL TEXT — perfect Simplified Chinese, no garbled/duplicated characters:
- Left vertical title ONLY the dish name characters, single column, no leftover old dish names
- Vertical subtitle: {副标}
- Red stamp: {红章}

Hero (lower left): tall clear glass/bowl of {具体分层与配料视觉描述}, condensation if iced,
ceramic plate, wooden spoon, small side dish of key ingredient, soft window light,
bamboo or green leaves, linen cloth — same premium food photography as reference.

Right cream panel:
① 食材搭配 — {N} items with circle photos MATCHING each name + short sensory line + amount
② 制作概要 — 4 circular step icons + short Chinese labels
③ 风味特点 — {句子}
④ 饮用建议/食用建议 — 3 tips with small icons
⑤ Bottom badge: 约{N} kcal/杯或份（估算）+ 清爽低负担 夏日小确幸
Footer: *以上热量为估算值，具体以实际食材为准

Same beige cream panel, dotted leader lines, soft botanical editorial aesthetic.
Clean uncluttered type, no overlapping text. 3:4 vertical poster.
```

出图后：

1. **读图检查**标题是否正确、有无串菜名/乱码、食材小图是否与名称匹配  
2. 若标题乱码或串了旧菜名：**再 `image_edit` 修正一轮**（强调 only one vertical title = 当前菜名）  
3. 禁止用代码/PS 涂字修图；文字问题一律重生成  
4. 将终稿复制到：  
   `{output_dir}/{NN}-{slug}.jpg`  
   同目录写 `{NN}-{slug}.md`（文案+做法）

`NN`：该目录下已有序号 +1，默认 `01`。

---

### Step 3 — 文案包

每个食品输出以下模块（中文，可直接粘贴小红书）：

#### A. 标题备选 ×3–4
公式轮换：

- `38℃的夏天，靠这杯/碗{名}续命`
- `懒人 × 分钟｜比奶茶更××的{名}`
- `低卡夏日小确幸｜约{N}kcal {名}`
- `茶饮店同款复刻｜{名}`

#### B. 正文小情绪（120–220 字）
结构：

1. 开场钩子（天气/情绪/场景）  
2. 做法有多简单（降低门槛）  
3. 口感分层描写（2–3 口）  
4. 情绪落点（不必大道理，一句就够）  
5. 热量/负担一句 + emoji 收尾  

#### C. 标签
`#夏日小零食 #{菜名} #低卡甜品 #夏日解暑 #懒人甜品 #小红书美食` + 1–2 个品类标签

#### D. 详细做法表
- 食材表（用量 + 备注）  
- 分步（可复现）  
- 小技巧 2–4 条  
- 热量拆分表 + 低卡替换  

完整 Markdown 模板：`references/output-template.md`

---

### Step 4 — 交付格式

回复用户时用这个结构：

```markdown
## {食品名} · 海报已生成

**图片**：`path/to/xx.jpg`

### 小红书文案
**标题备选**
1. …
**正文**
> …
**标签**
…

### 详细做法
…

### 热量
…
```

若用户只要图或只要文案：按需裁剪，不啰嗦。

---

## Batch mode

用户一次给多个菜名 / 「按清单做前 5 个」：

1. 列任务表（名 | slug | 状态）  
2. **串行**每个完整跑完（策划 → 出图 → 校验 → md）再下一个  
3. 同一系列保持：奶油信息栏、夏日限定章、热量徽章、副标句式一致  
4. 汇总路径列表 + 哪几张建议优先发  

---

## Quality bar

- [ ] 标题字正确，无乱码、无上一道菜残留  
- [ ] 右侧食材圆图与名称一致  
- [ ] 主视觉能一眼看出是什么食物  
- [ ] 热量有「估算」口径，不装精确实验室数据  
- [ ] 文案有小情绪，不是说明书体  
- [ ] 文件已落到工作区，路径可点  

---

## Defaults

| 项 | 默认 |
|----|------|
| 份量 | 1 人份 / 1 杯 |
| 红章 | 夏日限定 |
| 右栏底 tagline | 清爽低负担 夏日小确幸 |
| 输出目录 | `summer-snack/` |
| 比例 | 3:4 |
| 语言 | 简体中文 |

用户说「厚乳版 / 放纵版」时：主视觉更浓郁，热量上调，文案情绪改「允许自己甜一下」。  
用户说「低卡 / 减脂」时：椰浆→轻椰奶、少糖，主视觉仍好看，文案强调「无负担」。
---
