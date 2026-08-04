#!/usr/bin/env python3
"""Smart video downloader via local yt-dlp_macos (skill: video-download).

Resolution policy:
  1. Prefer 1080p+ (min(width,height) >= 1080) with audio
  2. Else prefer 720p+ with audio
  3. Else highest available resolution with audio
  4. Prefer muxed (video+audio) formats; else merge best video + best audio
  5. Prefer non-watermarked over watermarked
  6. Among ties: higher bitrate / filesize, prefer non-API CDN id (-2/-3)

Cookies (fast path):
  Prefer a Netscape cookie jar at ~/.cache/video-download/cookies.txt via
  --cookies FILE. Auto-refresh that jar from Chrome only when missing, stale,
  or a download fails for auth reasons (slow path once). User never pastes
  cookies manually.

Output:
  Default: current working directory (project cwd). Do not pass -o unless
  the user explicitly wants another folder.

Usage:
  download.py URL [URL ...]
  download.py --list-only URL
  download.py --dry-run URL
  download.py --refresh-cookies URL
  download.py -o DIR URL   # only when user asks for a custom dir
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_YTDLP = Path.home() / "Documents/tools/yt-dlp/yt-dlp_macos"
DEFAULT_BROWSER = "chrome"
DEFAULT_COOKIE_CACHE = Path.home() / ".cache" / "video-download" / "cookies.txt"
# How long a cached jar is considered fresh (hours). Override with env.
DEFAULT_COOKIE_MAX_AGE_HOURS = float(
    os.environ.get("VIDEO_DOWNLOAD_COOKIE_MAX_AGE_HOURS", "24")
)
# Seed URL used only when exporting cookies from the browser into the jar.
COOKIE_SEED_URL = "https://www.douyin.com/"

# short-side thresholds (portrait & landscape both work)
P1080 = 1080
P720 = 720

# Exit when agent/user must open the link in a logged-in browser, then retry.
EXIT_NEED_BROWSER = 2


def die(msg: str, code: int = 1) -> None:
    print(f"error: {msg}", file=sys.stderr)
    raise SystemExit(code)


def need_browser_action(urls: list[str], detail: str = "") -> None:
    """Tell the agent/user to open the URL in Chrome and re-run."""
    print("NEED_USER_ACTION:BROWSER_LOGIN", file=sys.stderr)
    if detail:
        print(detail, file=sys.stderr)
    print(
        "无法获取有效的抖音登录 Cookie。请在 Chrome 中打开并登录下面的链接"
        "（确认能正常播放），然后告诉我重试：",
        file=sys.stderr,
    )
    for u in urls:
        print(f"  {u}", file=sys.stderr)
    print(
        "提示：登录成功后无需手动导出 cookie；重新运行本命令会自动从 Chrome 刷新缓存。",
        file=sys.stderr,
    )
    raise SystemExit(EXIT_NEED_BROWSER)


def which_ytdlp(explicit: str | None) -> Path:
    if explicit:
        p = Path(explicit).expanduser()
        if not p.is_file():
            die(f"yt-dlp not found: {p}")
        return p
    env = os.environ.get("YTDLP_BIN")
    if env:
        p = Path(env).expanduser()
        if p.is_file():
            return p
    if DEFAULT_YTDLP.is_file():
        return DEFAULT_YTDLP
    found = shutil.which("yt-dlp") or shutil.which("yt-dlp_macos")
    if found:
        return Path(found)
    die(
        f"yt-dlp not found. Expected {DEFAULT_YTDLP} "
        "or set YTDLP_BIN / pass --ytdlp"
    )


def has_video(fmt: dict[str, Any]) -> bool:
    vc = (fmt.get("vcodec") or "none").lower()
    return vc not in ("none", "null", "")


def has_audio(fmt: dict[str, Any]) -> bool:
    ac = (fmt.get("acodec") or "none").lower()
    return ac not in ("none", "null", "")


def short_side(fmt: dict[str, Any]) -> int:
    w = fmt.get("width") or 0
    h = fmt.get("height") or 0
    try:
        w, h = int(w), int(h)
    except (TypeError, ValueError):
        return 0
    if w > 0 and h > 0:
        return min(w, h)
    return w or h or 0


def long_side(fmt: dict[str, Any]) -> int:
    w = fmt.get("width") or 0
    h = fmt.get("height") or 0
    try:
        w, h = int(w), int(h)
    except (TypeError, ValueError):
        return 0
    if w > 0 and h > 0:
        return max(w, h)
    return w or h or 0


def is_watermarked(fmt: dict[str, Any]) -> bool:
    note = (fmt.get("format_note") or "") + " " + (fmt.get("format") or "")
    fid = fmt.get("format_id") or ""
    blob = f"{note} {fid}".lower()
    return "watermark" in blob or fid.startswith("download_addr")


def is_api_variant(fmt: dict[str, Any]) -> bool:
    note = (fmt.get("format_note") or "").lower()
    fid = fmt.get("format_id") or ""
    if "(api)" in note:
        return True
    # Douyin often suffixes -0/-1 as API CDN mirrors
    m = re.search(r"-(\d+)$", fid)
    if m and int(m.group(1)) <= 1 and not fid.startswith("download_addr"):
        # weak signal; only use as tie-break later
        return True
    return False


def bitrate(fmt: dict[str, Any]) -> float:
    for key in ("tbr", "vbr", "abr"):
        v = fmt.get(key)
        if v is not None:
            try:
                return float(v)
            except (TypeError, ValueError):
                pass
    fs = fmt.get("filesize") or fmt.get("filesize_approx")
    if fs:
        try:
            # rough proxy when duration unknown
            return float(fs) / 1_000_000.0
        except (TypeError, ValueError):
            pass
    return 0.0


def filesize(fmt: dict[str, Any]) -> int:
    for key in ("filesize", "filesize_approx"):
        v = fmt.get(key)
        if v is not None:
            try:
                return int(v)
            except (TypeError, ValueError):
                pass
    return 0


def res_bucket(ss: int) -> int:
    """Higher is better: 2 = 1080p+, 1 = 720p+, 0 = below 720p."""
    if ss >= P1080:
        return 2
    if ss >= P720:
        return 1
    return 0


@dataclass
class Pick:
    format_spec: str  # e.g. "bytevc1_720p_688122-2" or "vid+aud"
    label: str
    height_like: int
    muxed: bool


def rank_muxed(fmt: dict[str, Any]) -> tuple:
    ss = short_side(fmt)
    return (
        res_bucket(ss),  # prefer 1080 then 720 then lower
        ss,
        long_side(fmt),
        0 if is_watermarked(fmt) else 1,
        0 if is_api_variant(fmt) else 1,
        bitrate(fmt),
        filesize(fmt),
    )


def rank_video_only(fmt: dict[str, Any]) -> tuple:
    ss = short_side(fmt)
    return (
        res_bucket(ss),
        ss,
        long_side(fmt),
        0 if is_watermarked(fmt) else 1,
        0 if is_api_variant(fmt) else 1,
        bitrate(fmt),
        filesize(fmt),
    )


def rank_audio_only(fmt: dict[str, Any]) -> tuple:
    return (
        bitrate(fmt),
        filesize(fmt),
        0 if is_api_variant(fmt) else 1,
    )


def pick_format(formats: list[dict[str, Any]]) -> Pick:
    muxed = [f for f in formats if has_video(f) and has_audio(f)]
    video_only = [f for f in formats if has_video(f) and not has_audio(f)]
    audio_only = [f for f in formats if has_audio(f) and not has_video(f)]

    best_muxed = max(muxed, key=rank_muxed) if muxed else None
    best_v = max(video_only, key=rank_video_only) if video_only else None
    best_a = max(audio_only, key=rank_audio_only) if audio_only else None

    # If we can merge and video-only short side beats muxed (or no muxed), merge
    if best_v and best_a:
        merge_ss = short_side(best_v)
        merge_bucket = res_bucket(merge_ss)
        if best_muxed is None:
            return Pick(
                format_spec=f"{best_v['format_id']}+{best_a['format_id']}",
                label=(
                    f"merge {best_v['format_id']}+{best_a['format_id']} "
                    f"{best_v.get('width')}x{best_v.get('height')}"
                ),
                height_like=merge_ss,
                muxed=False,
            )
        mux_ss = short_side(best_muxed)
        mux_bucket = res_bucket(mux_ss)
        # Prefer higher resolution bucket; within same bucket prefer muxed
        # unless video-only is clearly higher short-side
        if merge_bucket > mux_bucket or (
            merge_bucket == mux_bucket and merge_ss > mux_ss
        ):
            return Pick(
                format_spec=f"{best_v['format_id']}+{best_a['format_id']}",
                label=(
                    f"merge {best_v['format_id']}+{best_a['format_id']} "
                    f"{best_v.get('width')}x{best_v.get('height')}"
                ),
                height_like=merge_ss,
                muxed=False,
            )

    if best_muxed:
        ss = short_side(best_muxed)
        return Pick(
            format_spec=str(best_muxed["format_id"]),
            label=(
                f"muxed {best_muxed['format_id']} "
                f"{best_muxed.get('width')}x{best_muxed.get('height')} "
                f"tbr={best_muxed.get('tbr')} "
                f"note={best_muxed.get('format_note')}"
            ),
            height_like=ss,
            muxed=True,
        )

    if best_v and best_a:
        return Pick(
            format_spec=f"{best_v['format_id']}+{best_a['format_id']}",
            label=(
                f"merge {best_v['format_id']}+{best_a['format_id']} "
                f"{best_v.get('width')}x{best_v.get('height')}"
            ),
            height_like=short_side(best_v),
            muxed=False,
        )

    if best_v:
        # last resort: video without audio
        return Pick(
            format_spec=str(best_v["format_id"]),
            label=f"video-only {best_v['format_id']} (NO AUDIO)",
            height_like=short_side(best_v),
            muxed=False,
        )

    die("no downloadable video formats found")


def run_ytdlp(
    ytdlp: Path, args: list[str], capture: bool = False
) -> subprocess.CompletedProcess:
    cmd = [str(ytdlp), *args]
    # Avoid dumping huge cookie-path noise; still show the command.
    print("+", " ".join(cmd), file=sys.stderr)
    if capture:
        return subprocess.run(cmd, check=False, capture_output=True, text=True)
    return subprocess.run(cmd, check=False)


def looks_like_auth_error(text: str) -> bool:
    t = (text or "").lower()
    needles = (
        "cookies",
        "cookie",
        "login",
        "sign in",
        "not available",
        "unable to extract",
        "fresh cookies",
        "403",
        "401",
        "status code 403",
        "status code 401",
        "private video",
        "login required",
        "only images are available",
        "no video formats",
        "requested format is not available",
    )
    return any(n in t for n in needles)


def cookie_cache_usable(path: Path, max_age_hours: float) -> bool:
    if not path.is_file():
        return False
    try:
        if path.stat().st_size < 32:
            return False
        # Require at least one non-comment cookie line
        text = path.read_text(encoding="utf-8", errors="ignore")
        has_row = any(
            line.strip() and not line.startswith("#") for line in text.splitlines()
        )
        if not has_row:
            return False
        age_h = (time.time() - path.stat().st_mtime) / 3600.0
        if age_h > max_age_hours:
            print(
                f"cookie cache stale ({age_h:.1f}h > {max_age_hours}h): {path}",
                file=sys.stderr,
            )
            return False
        return True
    except OSError:
        return False


def refresh_cookies_from_browser(
    ytdlp: Path,
    browser: str,
    cache_path: Path,
    seed_url: str = COOKIE_SEED_URL,
) -> bool:
    """Export Chrome cookies into Netscape jar via yt-dlp (slow, once)."""
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    # Touch empty jar so yt-dlp can dump into it even if missing
    if not cache_path.exists():
        cache_path.write_text("# Netscape HTTP Cookie File\n", encoding="utf-8")

    print(
        f"refreshing cookie cache from browser={browser} → {cache_path}",
        file=sys.stderr,
    )
    args = [
        "--cookies-from-browser",
        browser,
        "--cookies",
        str(cache_path),
        "--skip-download",
        "--no-playlist",
        # Douyin may return no formats on homepage; ignore that.
        "--ignore-no-formats-error",
        seed_url,
    ]
    cp = run_ytdlp(ytdlp, args, capture=True)
    # Even with non-zero (e.g. no formats on homepage), jar may still be written.
    if cookie_cache_usable(cache_path, max_age_hours=10**9):
        # Bump mtime so max-age clock starts now
        try:
            os.utime(cache_path, None)
        except OSError:
            pass
        size = cache_path.stat().st_size
        print(f"cookie cache ready ({size} bytes): {cache_path}", file=sys.stderr)
        return True

    err = (cp.stderr or cp.stdout or "").strip()
    print(
        f"cookie refresh failed (exit {cp.returncode})\n{err[-1500:]}",
        file=sys.stderr,
    )
    return False


def ensure_cookie_args(
    ytdlp: Path,
    browser: str,
    cache_path: Path,
    max_age_hours: float,
    force_refresh: bool = False,
) -> list[str]:
    """Return yt-dlp cookie args. Prefer fast --cookies FILE."""
    if force_refresh or not cookie_cache_usable(cache_path, max_age_hours):
        ok = refresh_cookies_from_browser(ytdlp, browser, cache_path)
        if not ok:
            # Last resort: direct browser (slow every call) — still try once
            print(
                "falling back to --cookies-from-browser (no usable cache)",
                file=sys.stderr,
            )
            return ["--cookies-from-browser", browser]
    else:
        age_h = (time.time() - cache_path.stat().st_mtime) / 3600.0
        print(
            f"using cookie cache ({age_h:.1f}h old): {cache_path}",
            file=sys.stderr,
        )
    return ["--cookies", str(cache_path)]


def fetch_info(
    ytdlp: Path, url: str, cookie_args: list[str]
) -> tuple[dict[str, Any] | None, str]:
    """Return (info, error_text). info is None on failure."""
    args = ["-J", "--no-playlist", *cookie_args, url]
    cp = run_ytdlp(ytdlp, args, capture=True)
    err = (cp.stderr or "").strip()
    out = (cp.stdout or "").strip()
    if cp.returncode != 0 or not out:
        return None, err or out or f"exit {cp.returncode}"
    try:
        info = json.loads(out)
    except json.JSONDecodeError as e:
        return None, f"invalid JSON: {e}\n{out[:500]}"
    formats = info.get("formats") or []
    if not any(has_video(f) or has_audio(f) for f in formats):
        return None, err or "no video/audio formats in metadata"
    return info, err


def list_formats(info: dict[str, Any]) -> None:
    title = info.get("title") or ""
    vid = info.get("id") or ""
    print(f"\n# {vid}  {title}")
    print(
        f"{'ID':<28} {'RES':>11} {'FPS':>4} {'TBR':>7} "
        f"{'V':>6} {'A':>6} NOTE"
    )
    for f in info.get("formats") or []:
        if not has_video(f) and not has_audio(f):
            continue
        w, h = f.get("width") or "?", f.get("height") or "?"
        res = f"{w}x{h}" if has_video(f) else "audio"
        fps = f.get("fps") or ""
        tbr = f.get("tbr") or ""
        vc = (f.get("vcodec") or "none")[:6]
        ac = (f.get("acodec") or "none")[:6]
        note = f.get("format_note") or ""
        print(
            f"{f.get('format_id', ''):<28} {res:>11} {str(fps):>4} "
            f"{str(tbr):>7} {vc:>6} {ac:>6} {note}"
        )


def resolve_saved_path(outdir: Path, vid: str) -> Path | None:
    matches: list[Path] = []
    if not vid:
        return None
    try:
        for p in outdir.iterdir():
            if p.is_file() and f"[{vid}]" in p.name:
                matches.append(p)
    except OSError:
        return None
    if not matches:
        return None
    matches.sort(key=lambda p: p.stat().st_mtime)
    return matches[-1]


def download_one(
    ytdlp: Path,
    url: str,
    outdir: Path,
    cookie_args: list[str],
    dry_run: bool,
    list_only: bool,
) -> Path | None:
    info, err = fetch_info(ytdlp, url, cookie_args)
    if info is None:
        raise RuntimeError(f"metadata failed: {err[-2000:]}")

    if list_only:
        list_formats(info)
        pick = pick_format(info.get("formats") or [])
        print(f"\n→ would pick: {pick.label}  (-f {pick.format_spec})")
        return None

    formats = info.get("formats") or []
    pick = pick_format(formats)
    title = (info.get("title") or info.get("id") or "video")[:60]
    print(f"\n=== {title}", file=sys.stderr)
    print(f"pick: {pick.label}", file=sys.stderr)
    print(f"-f {pick.format_spec}  (short-side≈{pick.height_like}p)", file=sys.stderr)

    if pick.height_like and pick.height_like < P720:
        print(
            f"note: max available short-side is {pick.height_like}p (<720); "
            "downloading best available",
            file=sys.stderr,
        )
    elif pick.height_like >= P1080:
        print("note: 1080p+ selected", file=sys.stderr)
    else:
        print("note: 720p+ selected", file=sys.stderr)

    outdir.mkdir(parents=True, exist_ok=True)
    outtmpl = str(outdir / "%(title).80B [%(id)s].%(ext)s")

    args = [
        "-f",
        pick.format_spec,
        *cookie_args,
        "--no-playlist",
        "-o",
        outtmpl,
        "--merge-output-format",
        "mp4",
        "--newline",
        url,
    ]

    if dry_run:
        print("dry-run: skip download", file=sys.stderr)
        print(" ".join([str(ytdlp), *args]))
        return None

    cp = run_ytdlp(ytdlp, args, capture=False)
    if cp.returncode != 0:
        raise RuntimeError(f"download failed (exit {cp.returncode})")

    path = resolve_saved_path(outdir, info.get("id") or "")
    if path:
        print(f"saved: {path}", file=sys.stderr)
        return path
    print("download finished (output path not resolved)", file=sys.stderr)
    return None


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description=(
            "Download Douyin/compatible videos at best ≥720p (prefer 1080p) "
            "with audio. Cookies: auto-cache from Chrome, reuse via --cookies."
        )
    )
    p.add_argument("urls", nargs="+", help="video URL(s), e.g. https://v.douyin.com/...")
    p.add_argument(
        "-o",
        "--outdir",
        default=None,
        help="output directory (default: current working directory / project cwd)",
    )
    p.add_argument(
        "--ytdlp",
        default=None,
        help=f"path to yt-dlp binary (default: {DEFAULT_YTDLP})",
    )
    p.add_argument(
        "--cookies-from-browser",
        default=DEFAULT_BROWSER,
        help=f"browser used only when refreshing cookie cache (default: {DEFAULT_BROWSER})",
    )
    p.add_argument(
        "--cookie-cache",
        default=str(DEFAULT_COOKIE_CACHE),
        help=f"Netscape cookie jar path (default: {DEFAULT_COOKIE_CACHE})",
    )
    p.add_argument(
        "--cookie-max-age-hours",
        type=float,
        default=DEFAULT_COOKIE_MAX_AGE_HOURS,
        help=f"refresh cache when older than this (default: {DEFAULT_COOKIE_MAX_AGE_HOURS})",
    )
    p.add_argument(
        "--refresh-cookies",
        action="store_true",
        help="force re-export cookies from the browser before downloading",
    )
    p.add_argument(
        "--list-only",
        action="store_true",
        help="list formats and show pick, do not download",
    )
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="print selected format and command only",
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> None:
    args = parse_args(argv)
    ytdlp = which_ytdlp(args.ytdlp)
    outdir = (
        Path(args.outdir).expanduser().resolve()
        if args.outdir
        else Path.cwd().resolve()
    )
    print(f"output dir: {outdir}", file=sys.stderr)
    cache_path = Path(args.cookie_cache).expanduser().resolve()
    browser = args.cookies_from_browser
    max_age = float(args.cookie_max_age_hours)

    if not shutil.which("ffmpeg"):
        print(
            "warning: ffmpeg not on PATH; separate video+audio merge may fail",
            file=sys.stderr,
        )

    urls = [u.strip() for u in args.urls if u.strip()]
    if not urls:
        die("no URLs given")

    # Prepare cookie jar once for the whole batch (not per URL).
    cookie_args = ensure_cookie_args(
        ytdlp=ytdlp,
        browser=browser,
        cache_path=cache_path,
        max_age_hours=max_age,
        force_refresh=args.refresh_cookies,
    )

    results: list[Path] = []
    failures: list[str] = []
    auth_blocked: list[str] = []

    for url in urls:
        try:
            path = download_one(
                ytdlp=ytdlp,
                url=url,
                outdir=outdir,
                cookie_args=cookie_args,
                dry_run=args.dry_run,
                list_only=args.list_only,
            )
            if path:
                results.append(path)
            continue
        except SystemExit:
            raise
        except Exception as first_err:
            err_text = str(first_err)
            print(f"warn: {url}: {err_text[:500]}", file=sys.stderr)
            # One forced browser re-export + retry. Douyin errors are often
            # opaque; a stale jar is the most common fixable cause.
            print(
                "retrying after forced cookie refresh from browser…",
                file=sys.stderr,
            )
            ok = refresh_cookies_from_browser(ytdlp, browser, cache_path)
            if not ok:
                auth_blocked.append(url)
                continue
            cookie_args = ["--cookies", str(cache_path)]
            try:
                path = download_one(
                    ytdlp=ytdlp,
                    url=url,
                    outdir=outdir,
                    cookie_args=cookie_args,
                    dry_run=args.dry_run,
                    list_only=args.list_only,
                )
                if path:
                    results.append(path)
                continue
            except SystemExit:
                raise
            except Exception as second_err:
                err2 = str(second_err)
                print(f"error: {url}: {err2[:800]}", file=sys.stderr)
                if looks_like_auth_error(err2) or looks_like_auth_error(err_text):
                    auth_blocked.append(url)
                else:
                    failures.append(url)
                continue

    if results:
        print("\n# downloaded")
        for r in results:
            print(r)

    if auth_blocked and not results:
        need_browser_action(auth_blocked)
    if auth_blocked:
        # Partial success: still surface remaining need-login URLs
        need_browser_action(auth_blocked, detail="部分链接下载成功，以下仍失败：")
    if failures:
        die(f"{len(failures)} URL(s) failed: {failures}")


if __name__ == "__main__":
    main()
