#!/usr/bin/env python3
"""Generate voiceover audio with Doubao Speech HTTP V3 and API Key auth.

This is for the newer Doubao Speech API Key path:
POST https://openspeech.bytedance.com/api/v3/tts/unidirectional

Credentials are read from environment variables only:
- DOUBAO_SPEECH_API_KEY
- DOUBAO_TTS_ENDPOINT, optional endpoint override
- DOUBAO_RESOURCE_ID, for example seed-tts-2.0
- DOUBAO_SPEAKER_ID, for example a voice/speaker id from the speech console
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import urllib.error
import urllib.request
import uuid
from pathlib import Path


DEFAULT_ENDPOINT = "https://openspeech.bytedance.com/api/v3/tts/unidirectional"


def env_required(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"Missing required environment variable: {name}")
    return value


def parse_concatenated_json(raw: str) -> list[dict]:
    decoder = json.JSONDecoder()
    index = 0
    objects: list[dict] = []
    while index < len(raw):
        while index < len(raw) and raw[index] in " \n\r\t":
            index += 1
        if index >= len(raw):
            break
        obj, index = decoder.raw_decode(raw, index)
        if isinstance(obj, dict):
            objects.append(obj)
    return objects


def post_tts(endpoint: str, api_key: str, resource_id: str, payload: dict) -> tuple[bytes, list[dict], dict[str, str]]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {
        "Content-Type": "application/json",
        "X-Api-Key": api_key,
        "X-Api-Resource-Id": resource_id,
        "X-Api-Request-Id": str(uuid.uuid4()),
    }
    request = urllib.request.Request(endpoint, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(request, timeout=90) as response:
            response_headers = {key: value for key, value in response.headers.items()}
            raw = response.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        logid = exc.headers.get("X-Tt-Logid") if exc.headers else None
        logid_text = f" X-Tt-Logid={logid}" if logid else ""
        raise SystemExit(f"Doubao TTS HTTP {exc.code}:{logid_text} {body}") from exc

    events = parse_concatenated_json(raw)
    chunks: list[bytes] = []
    for event in events:
        code = event.get("code")
        if code not in (None, 0, 20000000):
            raise SystemExit(f"Doubao TTS error event: {json.dumps(event, ensure_ascii=False)}")
        audio_data = event.get("data")
        if isinstance(audio_data, str) and audio_data:
            chunks.append(base64.b64decode(audio_data))
    if not chunks:
        raise SystemExit(f"Doubao TTS returned no audio chunks. Events: {json.dumps(events[-5:], ensure_ascii=False)}")
    return b"".join(chunks), events, response_headers


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--text-file", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument("--format", default="mp3", choices=["mp3", "pcm", "ogg_opus"])
    parser.add_argument("--sample-rate", type=int, default=24000)
    parser.add_argument("--speed", type=float, default=0.88, help="Natural speed ratio. 0.88 maps to -12 speech_rate.")
    parser.add_argument("--loudness", type=int, default=0, help="Doubao loudness_rate, usually -50..100.")
    parser.add_argument(
        "--endpoint",
        default=os.environ.get("DOUBAO_TTS_ENDPOINT", DEFAULT_ENDPOINT),
        help="Doubao TTS endpoint. Ark Agent/Coding Plan keys can override this with the /plan/ endpoint.",
    )
    parser.add_argument(
        "--tts-model",
        default=os.environ.get("DOUBAO_TTS_MODEL", "seed-tts-2.0-expressive"),
        help="TTS 2.0 model variant, e.g. seed-tts-2.0-expressive or seed-tts-2.0-standard.",
    )
    args = parser.parse_args()

    api_key = env_required("DOUBAO_SPEECH_API_KEY")
    resource_id = env_required("DOUBAO_RESOURCE_ID")
    speaker_id = env_required("DOUBAO_SPEAKER_ID")
    if resource_id.startswith("apikey-"):
        raise SystemExit(
            "DOUBAO_RESOURCE_ID should be the TTS service resource, e.g. seed-tts-2.0, "
            "not the API Key table resource id that starts with apikey-."
        )

    text = Path(args.text_file).read_text(encoding="utf-8").strip()
    if not text:
        raise SystemExit("Text file is empty.")

    speech_rate = round((args.speed - 1.0) * 100)
    payload = {
        "user": {"uid": "codex-video-maker"},
        "req_params": {
            "text": text,
            "model": args.tts_model,
            "speaker": speaker_id,
            "audio_params": {
                "format": args.format,
                "sample_rate": args.sample_rate,
                "speech_rate": speech_rate,
                "loudness_rate": args.loudness,
            },
        },
    }

    audio_bytes, events, response_headers = post_tts(args.endpoint, api_key, resource_id, payload)
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(audio_bytes)

    meta = {
        "provider": "doubao_tts_v3_api_key",
        "endpoint": args.endpoint,
        "resource_id": resource_id,
        "speaker_id": speaker_id,
        "tts_model": args.tts_model,
        "format": args.format,
        "sample_rate": args.sample_rate,
        "speed_ratio": args.speed,
        "speech_rate": speech_rate,
        "loudness_rate": args.loudness,
        "event_count": len(events),
        "audio_bytes": len(audio_bytes),
        "x_tt_logid": response_headers.get("X-Tt-Logid"),
        "output": str(out_path),
    }
    meta_path = out_path.with_suffix(out_path.suffix + ".meta.json")
    meta_path.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    print(str(out_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
