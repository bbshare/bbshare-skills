# Cookie strategy (fast path)

## Why not always `--cookies-from-browser`?

Reading Chrome’s cookie DB decrypts the whole jar via Keychain on every call.
That often takes **20–40s** and used to run **twice** per video (metadata `-J` + download).

## What we do instead

1. **Cache jar** (Netscape format): `~/.cache/video-download/cookies.txt`
2. **Fast path**: `--cookies <jar>` for both metadata and download (milliseconds).
3. **Slow path (auto)**: when the jar is missing / older than 24h / download fails, run once:
   ```bash
   yt-dlp --cookies-from-browser chrome --cookies ~/.cache/video-download/cookies.txt \
     --skip-download --ignore-no-formats-error https://www.douyin.com/
   ```
   yt-dlp loads browser cookies and **dumps** them into the jar.
4. **User never pastes cookies.** Agent/script refreshes automatically.
5. If browser export fails or retry still cannot get formats → exit `2` with  
   `NEED_USER_ACTION:BROWSER_LOGIN` and ask the user to open the video URL in Chrome (logged in), then re-run. Re-run forces a fresh export.

## Knobs

| Flag / env | Meaning |
|------------|---------|
| `--cookie-cache PATH` | Jar location |
| `--cookie-max-age-hours N` | Stale after N hours (default 24) |
| `--refresh-cookies` | Force browser export before download |
| `--cookies-from-browser NAME` | Browser for export only (default chrome) |
| `VIDEO_DOWNLOAD_COOKIE_MAX_AGE_HOURS` | Default max age |

## Security

- Jar is local user data (login session). Do not commit, upload, or paste it into chat.
- Prefer keeping it under `~/.cache/` (not the project repo).
