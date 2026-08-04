# Doubao TTS API Key Workflow

Use the API Key path, not the older AppID/Token flow.

## Environment Variables

Require:

```bash
export DOUBAO_SPEECH_API_KEY="..."
export DOUBAO_RESOURCE_ID="seed-tts-2.0"
export DOUBAO_SPEAKER_ID="zh_male_ruyayichen_uranus_bigtts"
```

Optional:

```bash
export DOUBAO_TTS_MODEL="seed-tts-2.0-expressive"
export DOUBAO_TTS_ENDPOINT="https://openspeech.bytedance.com/api/v3/tts/unidirectional"
```

Important:

- `DOUBAO_RESOURCE_ID` is the TTS service resource such as `seed-tts-2.0`.
- It is not the API Key table resource id that starts with `apikey-`.
- Do not print secrets.

Useful speaker IDs discovered during setup:

- `zh_female_cancan_uranus_bigtts`
- `zh_female_liuchangnv_uranus_bigtts`
- `zh_female_kefunvsheng_uranus_bigtts`
- `zh_male_ruyayichen_uranus_bigtts`

## Generate One-Pass Voice

Copy or use `scripts/doubao_tts_v3_api_key.py` inside the project:

```bash
source ~/.zshrc >/dev/null 2>&1
python3 scripts/doubao_tts_v3_api_key.py \
  --text-file audio/voiceover_with_intro.txt \
  --out audio/voiceover_with_intro.mp3 \
  --speed 0.88 \
  --loudness 0
```

Check duration:

```bash
ffprobe -v error -show_entries format=duration -of default=nk=1:nw=1 audio/voiceover_with_intro.mp3
```

## Mix Audio

Use the TTS voice, low BGM, and optional transition SFX to make one master file:

```bash
ffmpeg -y \
  -i audio/voiceover_with_intro.mp3 \
  -stream_loop -1 -i audio/bgm.mp3 \
  -filter_complex "[1:a]volume=0.10,atrim=0:DURATION[bgm];[0:a]volume=1.0[voice];[voice][bgm]amix=inputs=2:duration=first:dropout_transition=0[a]" \
  -map "[a]" -ar 48000 -ac 2 audio/master_with_intro.wav
```

Replace `DURATION` with the voice duration or use a script.

## Caption Sync

After generating TTS, do not assume old storyboard times are still valid. Recompute cue times from the final TTS audio.

If using whisper.cpp directly on a Mac and it crashes with Metal/GPU errors, add:

```bash
--no-gpu --no-flash-attn
```

Chinese Whisper text can be wrong even when token times are useful. Use timing as evidence, not as final copy.
