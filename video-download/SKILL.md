---
name: video-download
description: >
  Download Douyin (抖音) or other yt-dlp-supported videos at best quality with
  audio: prefer 1080p, else ≥720p, else highest available; auto-pick muxed or
  video+audio merge. Saves files into the current project/working directory.
  Uses local yt-dlp_macos with auto-cached Chrome cookies (fast --cookies jar;
  browser export only when cache missing/stale/failed). Use when the user pastes
  v.douyin.com / douyin.com (or similar) URLs and wants to download, batch-
  download, save 视频, or runs /video-download.
metadata:
  short-description: "Download videos ≥720p with audio into cwd"
---

# /video-download — 视频智能下载

用本机 `yt-dlp_macos` 按分辨率策略下载**带音频**视频。用户给 1 个或多个 URL 即执行。

## Tooling

| Item | Path / value |
|------|----------------|
| Binary | `/Users/alan.xiong/Documents/tools/yt-dlp/yt-dlp_macos` |
| Override | env `YTDLP_BIN` or script flag `--ytdlp` |
| Cookie jar（快） | `~/.cache/video-download/cookies.txt` → `--cookies` |
| Cookie 刷新（慢，自动） | 从 Chrome 导出一次写入 jar |
| Merge | 系统 `ffmpeg` / `ffprobe`（分离音视频时需要） |
| Helper | `scripts/download.py`（本 skill 目录下） |

```bash
SKILL_DIR="$HOME/.grok/skills/video-download"
```

## When to run

- `/video-download`
- 「下载这个抖音 / 视频」「批量下视频」「保存视频」
- 用户粘贴 `https://v.douyin.com/...`、`https://www.douyin.com/video/...` 等并要求下载

**不要**用浏览器爬页面替代；**不要**手写猜 format id；**不要**让用户手动粘贴 cookie 字符串。

## Cookies（必须遵守 — 性能关键）

详见 [references/cookies.md](references/cookies.md)。

**默认路径（快）：**

1. 使用缓存 jar：`--cookies ~/.cache/video-download/cookies.txt`
2. jar 缺失、超过 24h、或下载失败 → 脚本**自动**从 Chrome 导出并写入 jar（慢一次）
3. 同一批 URL **只准备一次** cookie，不要每个视频都 `--cookies-from-browser`

**禁止**默认每次都加 `--cookies-from-browser chrome`（会反复解密 Chrome cookie 库，极慢）。

**拿不到有效 cookie 时（exit code 2 / 输出含 `NEED_USER_ACTION:BROWSER_LOGIN`）：**

1. 明确提示用户：在 **Chrome** 打开该视频链接并确保已登录、能播放
2. 等用户确认后，用 `--refresh-cookies` **重试**（不要让用户导出/粘贴 cookie）
3. 重试命令示例：
   ```bash
   python3 "$SKILL_DIR/scripts/download.py" --refresh-cookies <URL>
   ```

## Output directory（必须遵守）

- **始终下载到当前执行目录（cwd / 当前项目目录）**
- **不要**默认写到 `~/Downloads`、skill 安装目录
- **不要**主动传 `-o`，除非用户明确指定
- 文件名：`%(title).80B [%(id)s].%(ext)s`

## Resolution policy（必须遵守）

1. **有 1080p（短边 ≥1080）→ 优先 1080p**
2. **否则有 720p（短边 ≥720）→ 选最高码率的 ≥720p**
3. **最高都不到 720p → 选最高分辨率**
4. **必须尽量带音频**：优先封装好的 mp4；音视频分离则 `-f 视频ID+音频ID`
5. 同档：无水印 > 有水印；更高 `tbr`/体积优先

短边 = `min(width, height)`。细节见 [references/format-policy.md](references/format-policy.md)。

## Workflow（Agent）

### 1. 收集 URL

- 提取全部视频 URL；shell cwd = 当前项目/工作区

### 2. 一键下载（推荐）

```bash
python3 "$SKILL_DIR/scripts/download.py" <URL> [URL...]
```

仅看清晰度 / dry-run / 强制刷新 cookie：

```bash
python3 "$SKILL_DIR/scripts/download.py" --list-only <URL>
python3 "$SKILL_DIR/scripts/download.py" --dry-run <URL>
python3 "$SKILL_DIR/scripts/download.py" --refresh-cookies <URL>
```

### 3. 用户需打开浏览器时

若脚本退出码为 **2** 或 stderr 含 `NEED_USER_ACTION:BROWSER_LOGIN`：

1. 把脚本打印的 URL 转给用户，请其在 Chrome 打开并登录播放
2. 用户回复「好了 / 已打开 / 重试」后，执行带 `--refresh-cookies` 的下载
3. **不要**要求用户提供 cookie 文件内容

### 4. 汇报

对每个 URL 报告：format id、分辨率档位、保存绝对路径与大小、是否走了 cookie 刷新、是否需用户打开浏览器。

## Batch

- 多 URL **顺序**下载；cookie 在进程内只初始化/刷新一次
- 单个失败继续后续 URL；若最终仍是登录类失败，汇总提示用户打开对应链接

## Gotchas

- 首次（或 jar 过期）从 Chrome 导出仍会慢几十秒——属正常；之后应明显变快
- Chrome 未登录抖音 / 未打开过站点 → 导出的 jar 可能无效 → 走 BROWSER_LOGIN 流程
- 水印源 `download_addr-*` 默认不要选
- 缺 `ffmpeg` 时分离流 merge 会失败
- 输出目录 = **进程 cwd**，不是 skill 安装目录
- **不要**把 `~/.cache/video-download/cookies.txt` 提交进 git 或贴到对话里

## Do not

- 不上传、不公开分享 cookies / 登录态
- 不下载用户未提供的链接
- 不默认每次 `--cookies-from-browser`
- 不让用户手动粘贴 cookie
- 不擅自改下载到 `~/Downloads`
