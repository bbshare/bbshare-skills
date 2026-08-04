# bbshare-video

**当前版本：0.3.0**

后续更新按语义版本号递增。

把一个概念做成一条**带旁白的讲解视频**：讨论 → 讲解框架 → HTML 幻灯 → 口播稿 →
TTS 人声 → 字幕 → 背景音乐 → Playwright 录屏 → ffmpeg 合成。

没有数字人、没有 avatar。**一份 HTML 就是全片的源文件**，画面和旁白都从它派生。

## 为什么是 HTML 而不是 PPT / 剪映

|  | 拖拽工具 | 这条流水线 |
|---|---|---|
| 改一个字 | 打开软件手动改，重新导出 | 改文本文件，重跑脚本 |
| 做第二条 | 再拖一遍 | 换内容文件，模板不动 |
| 能否 diff / 回滚 | 不能 | 能，就是一堆文本文件 |

代价是第一次要自己写 CSS，比拖 PPT 慢——但这是一次性成本。

## 用法

装好之后（见仓库根目录 README），直接跟 Claude Code 说：

> 帮我做一条讲解视频，主题是 XXX

它会先跟你把**讲解框架**聊定（8 页左右、每页一个 `role`），确认之后再产出
HTML 和口播稿，最后一条命令跑完剩下的装配步骤。

也可以只重跑其中一段：

```bash
S=~/.codex/skills/bbshare-video/scripts

bash $S/build_video.sh presentations/<slug>                       # 全流程
bash $S/build_video.sh presentations/<slug> --tts say             # 零安装先跑通
bash $S/build_video.sh presentations/<slug> --only mix,compose --bgm-volume 0.12   # 只重混音
bash $S/build_video.sh presentations/<slug> --from record         # 改了画面，从录屏往后
```

如果声音已经在 Voicebox 里手动生成，可以直接把 WAV 当成主时钟，不必再跑
TTS。需要精确字幕时，用本地 faster-whisper 只提取时间戳，字幕文字仍取自
已经确认的 `narration.txt`：

```bash
python $S/whisper_align.py \
  --audio presentations/<slug>/audio/voicebox_manual.wav \
  --text-file presentations/<slug>/narration.txt \
  --out-srt presentations/<slug>/audio/voicebox_whisper.srt

bash $S/build_video.sh presentations/<slug> \
  --audio presentations/<slug>/audio/voicebox_manual.wav \
  --srt-file presentations/<slug>/audio/voicebox_whisper.srt \
  --lead 0.57 --bgm none --from srt
```

`--lead auto` 只是根据录屏元数据或视频、音频时长差做估算。发布前要抽帧确认
第一处翻页，再把实测值传给 `--lead`。如果要解决白色首帧，先把视频跑通，
再用 `add_cover.sh` 叠加一个 0.5–0.7 秒的有限帧封面；不要直接把无限循环的
静态图作为最终 MP4 的输入。

渲染前后都可以运行一致性检查：

```bash
python $S/validate_project.py \
  --project presentations/<slug> \
  --audio presentations/<slug>/audio/voicebox_manual.wav \
  --video presentations/<slug>/final/<slug>.mp4 --vertical
```

## 人声：三种引擎，或直接使用已有 WAV

整条管线里**人声是最容易替换的一环**——下游只认最终 wav 的**实测时长**，
不认是谁念的。所以先用能跑的，回头再升级：

| 引擎 | 装什么 | 效果 |
|---|---|---|
| `--tts say` | 不用装（macOS 自带） | 机器音，用来验证流程通不通 |
| `--tts edge` | `pip install edge-tts` | 免费神经网络音色，够用 |
| `--tts voicebox` | 本地跑 Voicebox app | 声音复刻，最像本人 |
| `--audio existing.wav` | 已有本地录音 | 不重新合成，直接以实测时长为主时钟 |

默认 `--tts auto`：Voicebox 能连就用它，否则 edge-tts，再否则 `say`。

## 依赖

```bash
pip install playwright pillow faster-whisper && python -m playwright install chromium
brew install ffmpeg
```

在 macOS（Apple Silicon）上开发和跑通。Python / ffmpeg 部分是跨平台的，
只有 `--tts say` 是 macOS 专属。

## 已知短板（V0）

诚实说明，这是第一版：

1. **HTML 效果随机**——同样的模板，这次排版顺眼下次有点松垮；动画是通用的淡入位移，没有设计感。
2. **口播偏平**——TTS 缺语气起伏；声音复刻的音色如果只用中文样本训练，遇到
   HTML / TTS / Whisper 这类英文词会露馅。
3. **没有数字人、没有对口型**——画面就是幻灯片翻页加画外音。

三个都是工程问题，不是路线问题。第 3 条需要的输入（干净人声轨 +
逐句时间轴）这条管线已经产出了，数字人是**接在后面的新环节**，不是推翻重来。

## 设计要点

- **音频时长是主时钟。** 稿子里写的 `data-duration` 只是估算，TTS 念出来多长才算数。
  翻页时间轴、字幕、录屏长度全部按实测的 `voice.wav` 缩放，绝不反过来。
- **字幕时间戳从最终音频倒推，不从稿子正推。** 普通 TTS 用按字数分配；手动
  Voicebox 或停顿明显的录音，优先用 `whisper_align.py` 的词级时间戳，但不
  采用 Whisper 识别出来的文字。

更多坑记在 `SKILL.md` 的 “Things that will bite you”。
