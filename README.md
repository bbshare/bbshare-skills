# bbshare-skills：开源 AI Agent Skills

一组面向 **Claude Code、Codex 和其他 AI Agent** 的可复用开源 Skills，专注于
视频创作、短视频生产、视频下载、小红书内容和 AI 内容工作流。

This repository is a collection of reusable **AI agent skills** for Claude Code,
Codex, and compatible coding agents. It focuses on video creation, short-form
video production, video downloading, Xiaohongshu content, and practical AI
content workflows.

> 项目持续更新中。每个技能都以独立目录维护，包含 `SKILL.md`，并可根据需要
> 单独安装、修改和复用。

## 技能列表

| Skill | 用途 | 适合场景 |
| --- | --- | --- |
| [`bbshare-video`](./bbshare-video/) | 讲解视频生产流水线 | 从一个主题生成 HTML 幻灯片、旁白、TTS、人声字幕、背景音乐和最终视频 |
| [`book-account-video`](./book-account-video/) | 读书账号短视频 | 制作抖音 / TikTok 风格的读书、书评和知识类短视频 |
| [`video-download`](./video-download/) | 视频下载工具 | 下载抖音及其他 `yt-dlp` 支持平台的视频，并自动选择清晰度和合并音频 |
| [`xhs-food-card`](./xhs-food-card/) | 小红书美食卡片 | 生成夏日甜品 / 零食海报、食材步骤、热量估算和小红书发帖文案 |

## 示例效果 / Examples

下面是目前几个 Skill 的实际输出。视频使用封面图展示，点击封面即可打开完整
MP4；图片样例直接展示最终海报效果。

### bbshare-video：AI 讲解视频

[![bbshare-video AI narrated explainer video demo with HTML slides, voiceover, subtitles, and background music](./bbshare-video/examples/cover.png)](./bbshare-video/examples/skill-01-stop-reteaching-ai.mp4)

[观看完整讲解视频](./bbshare-video/examples/skill-01-stop-reteaching-ai.mp4)

### book-account-video：读书账号短视频

[![book-account-video Chinese book review short video demo with narration, captions, cover, and background music](./book-account-video/examples/cover.png)](./book-account-video/examples/huozhe.mp4)

[观看完整读书短视频](./book-account-video/examples/huozhe.mp4)

### xhs-food-card：小红书美食卡片

![小红书夏日美食卡片示例：柠檬蜂蜜冻配方海报](./xhs-food-card/examples/08-ningmeng-fengmi-dong.png)

![小红书水果酸奶碗示例：火龙果酸奶碗食谱信息图](./xhs-food-card/examples/09-huolongguo-suannai-wan.png)

## 快速开始

> 样例视频和图片使用 [Git LFS](https://git-lfs.com/) 管理。需要拉取完整媒体
> 文件时，请先安装 Git LFS 并运行 `git lfs install`；只使用 Skill 文档时不需要
> 下载这些媒体文件。

### 安装单个 Skill

先克隆仓库：

```bash
git clone https://github.com/bbshare/bbshare-skills.git
cd bbshare-skills
```

然后将需要的技能目录复制到你的 AI Agent skills 目录。以 Codex 为例：

```bash
mkdir -p ~/.codex/skills
cp -R bbshare-video ~/.codex/skills/
```

以 Claude Code 为例，可以复制到：

```bash
mkdir -p ~/.claude/skills
cp -R bbshare-video ~/.claude/skills/
```

将命令中的 `bbshare-video` 替换为其他技能目录名即可。不同 AI Agent 的安装
目录可能不同，请以对应客户端的 Skills 文档为准。

### 直接使用

安装后，用自然语言描述任务即可。例如：

```text
帮我把这个主题做成一条带旁白的讲解视频：为什么人会拖延？
```

```text
帮我做一本书的抖音读书账号短视频，书名是《人类简史》。
```

```text
下载这个抖音视频，并尽量保存 1080p 和音频。
```

```text
帮我做一张杨枝甘露的小红书夏日美食卡片，包含做法、热量和发帖文案。
```

部分技能也支持斜杠命令，例如 `/video-download` 和 `/xhs-food-card`。

## 技能详情

### bbshare-video：讲解视频生产流水线

把一个概念、主题或文章转换成一条完整的讲解视频（narrated explainer video）：

```text
主题 → 讲解框架 → HTML 幻灯片 → 旁白稿 → TTS 人声 → 字幕 → 背景音乐 → 录屏 → MP4
```

它以 HTML 幻灯片作为画面源文件，使用 Playwright 录制，使用 ffmpeg 合成，
并根据真实音频时长同步画面、字幕和最终视频。适合知识科普、产品介绍、课程
讲解、文章视频化和 talking-deck 视频。

当前版本：`0.3.0`

详细说明和命令请见 [`bbshare-video/README.md`](./bbshare-video/README.md)。

### book-account-video：读书账号短视频

用于制作中文读书账号、书评账号和知识类账号的短视频，覆盖：

- hook-first 口播稿和人工审核流程
- Doubao TTS、人声、背景音乐和字幕
- 读书视频封面与发布文案
- 抖音 / TikTok 风格的短视频结构
- 可复用的脚本模板、字幕同步规则和包装规范

这个 Skill 强调保留自然的口播长度，并让最终音频驱动视频时间轴，适合稳定地
批量制作读书短视频，而不是只生成一段泛泛的书籍摘要。

### video-download：视频下载

使用 `yt-dlp` 下载抖音及其他受支持平台的视频，自动按照清晰度和音频策略选择
格式：优先 1080p，其次 720p，必要时回退到最高可用清晰度；如果音视频分离，
则自动合并为可播放文件。

```text
/video-download
```

下载前请确认你有权保存和使用相关内容，并遵守来源平台的服务条款、版权和隐私
要求。不要分享或提交浏览器 Cookie、登录态或其他敏感凭据。

### xhs-food-card：小红书夏日美食卡片

输入一个甜品、饮品或夏日小零食名称，即可规划并生成适合小红书发布的 3:4
竖版内容卡片，包括：

- 主视觉美食图和信息图版式
- 食材、克数、制作步骤和食用建议
- 热量估算及估算口径说明
- 小红书标题、正文、标签和小情绪文案

```text
/xhs-food-card 芒果椰奶西米露
```

## 仓库结构

```text
bbshare-skills/
├── .gitignore
├── README.md
├── bbshare-video/       # 讲解视频生产流水线
│   └── examples/         # 讲解视频样例
├── book-account-video/  # 读书账号短视频
│   └── examples/         # 读书短视频样例
├── video-download/      # 视频下载
└── xhs-food-card/       # 小红书美食卡片
    └── examples/         # 美食卡片样例
```

每个 Skill 的目录可以独立使用，通常包含：

- `SKILL.md`：触发条件、工作流、规则和质量标准
- `README.md`：面向使用者的快速说明（如该技能提供）
- `references/`：方法论、模板和参考资料
- `assets/`：可复用的模板和素材
- `scripts/`：自动化脚本

## 设计原则

- **可复用**：一个 Skill 解决一类稳定、重复出现的任务。
- **可检查**：将工作流、输入、输出和质量标准写进文档。
- **可迭代**：技能目录中的文本、脚本和模板都可以独立修改和版本管理。
- **人机协作**：需要创意判断和内容确认的步骤保留人工审核节点。
- **本地优先**：在可能的情况下优先使用本地脚本、缓存模型和现有工具。

## 贡献与反馈

欢迎提交 Issue 或 Pull Request：

- 报告 Skill 的错误、安装问题或文档问题
- 提出新的 AI Agent 工作流和使用场景
- 改进提示词、脚本、模板或质量检查
- 分享真实案例和可复现的改进建议

提交新 Skill 时，建议至少包含：

1. 清晰的 `SKILL.md` front matter，包括 `name` 和 `description`
2. 适用场景、不适用场景和最小输入说明
3. 可执行的工作流、示例和输出规范
4. 依赖、平台限制、版权或隐私注意事项
5. 一个可以让别人快速理解价值的 README 或示例

## License

License information will be added as the project is prepared for public release.

## Keywords

AI agent skills · Claude Code skills · Codex skills · open-source AI workflows ·
video generation · explainer video · short-form video · book review video ·
Douyin video · TikTok video · Xiaohongshu content · recipe card · yt-dlp video
download · TTS · subtitles · ffmpeg
