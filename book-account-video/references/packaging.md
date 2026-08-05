# Packaging: Cover And Posting Copy

## 导出后硬门（与 SKILL 一致）

用户要求导出 MP4 且 render **成功后**，同一回合必须落盘：

| 产物 | 路径 |
| --- | --- |
| 成片 | `output/<slug>.mp4` 或 `renders/final.mp4` |
| 封面 | `covers/cover.png` + `covers/cover.jpg` |
| 标题文案 | `docs/posting-copy.md` |

**禁止**只在聊天里贴标题/文案、不写本地文件。

## Cover

Default: `1080x1440`。

结构：

- 与成片同一情绪色世界（Mode A：主静帧裁切即可）
- 顶栏：《书名》+ 作者（线 A 常用橙字；线 B 白/浅灰亦可）  
- **大钩子金句**（可截图那句）居中  
- 底水印（默认 **`@读书笔记 · 书评分享`**，以用户指定为准）

不要因为参考片偏暗就把封面和正片统一压暗。先保证主体、书名和钩子在手机上清楚，再决定是否保留情绪阴影。

钩子来自成片主线，例如：

- `你越批评一个人` / `他越不可能改`（第二行可金色）  
- 线 B《活着》：`熬过去，不会有奖` / `撑着，就算数`

项目内写 `covers/cover.html`（背景指向 `assets/generated/...`），再 Chrome headless：

```bash
PROJ=/absolute/path/to/project
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless=new --disable-gpu --hide-scrollbars \
  --window-size=1080,1440 \
  --screenshot="$PROJ/covers/cover.png" \
  "file://$PROJ/covers/cover.html"

# JPG
sips -s format jpeg -s formatOptions 92 "$PROJ/covers/cover.png" --out "$PROJ/covers/cover.jpg"
# 或: magick covers/cover.png -quality 92 covers/cover.jpg
```

模板参考：skill 内 `assets/cover-template.html`。

## 首帧封面烧录（硬门 · 线 B 必做；线 A 强烈建议）

信息流缩略图常用 **视频第 0 帧**。片头若以全黑幕开场，上传后封面位是黑块。

| 禁止 | 正确 |
| --- | --- |
| t=0 整屏黑 | 第 0 帧 = 封面构图（书名+钩子+主视觉） |
| 只上传平台封面、成片仍黑首帧 | **烧进 MP4 时间轴** |

**做法（`huozhe-sample-video` 终态）：**

```bash
# 1) 先有 covers/cover.png
sips -s format jpeg -s formatOptions 92 covers/cover.png --out assets/opener/first-frame.jpg

# 2) 合成内 #op-poster：data-start=0 · ~0.4–0.5s
#    CSS 初始 opacity:1；~0.28s 起 dissolve 进片头动画
#    z-index 高于片头层
```

验收：

```bash
ffmpeg -y -i output/<slug>.mp4 -vf "select=eq(n\,0)" -vframes 1 snapshots/mp4-frame0.jpg
# 目视：有书名/钩子/主视觉，不是纯黑
```

封面文案迭代后：**同步刷新** `first-frame.jpg` 再 render。

## Posting Copy

**必须**写入 `docs/posting-copy.md`：

1. 成片/封面路径（可选一行）  
2. **推荐标题** 1 条  
3. **备选标题** 3 条  
4. **正文 · 抖音/视频号短版**  
5. **正文 · 小红书稍长版**  
6. **话题标签**  

## 爆款标题公式（运营向 · 必读）

标题必须围绕书的真实核心论点，不要把心理学、成瘾、财富、认知和历史类书籍都套成泛化的「看透人性」标题。优先使用一个书中特有的矛盾或问题，例如《成瘾》可用：

```text
为什么快乐越来越多，我们却越来越难满足？《成瘾》
```

信息流 0.5s 内完成：**点名你 → 制造不适/好奇 → 暗示有解**。

| 公式 | 结构 | 例 |
| --- | --- | --- |
| 反常识断言 | 常识反着说 | 越批评人，人越改不了 |
| 你+痛点 | 你越… / 你一… | 你一开口，对方只会辩解 |
| 禁忌句 | 永远不要 / 千万别 | 永远不要指责、批评、抱怨 |
| 结果对比 | 做X得Y（坏） | 批评伤的是自尊，不是问题 |
| 身份点名 | 职场/情侣/父母 | 职场最废的一种沟通：批评 |
| 金句｜书名 | 刺句在前，书名在后 | …｜《人性的弱点》 |

**弱 → 强：** 主角从「书」换成「你/关系」。  
**忌：** 书面腔、书单腔、标题与片内钩子对不上。  
抖音优先短狠口语；小红书可「为什么…」提问式。

完整拆解 + 本片 A/B 标题见：  
`renxingderuodian-video/docs/posting-copy.md`

## 正文公式（Mode A）

**抖音短：** 钩子复述 → 你场景半句 → 书名背书 → 金句单行 → 标签  

**小红书：** 场景痛 → 为什么 → 书内结论 → 一句行动 → 二选一提问 → 标签  

1. 重申许可证（对齐封面）  
2. 半句书名背书  
3. 金句单独成行（可截图）  
4. 轻互动（小红书更需要）  
5. Hashtags：`#读书笔记 #书名 #沟通` 等 
