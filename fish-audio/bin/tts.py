#!/usr/bin/env python3
"""Fish Audio TTS helper.

Synthesizes text to speech via the Fish Audio API and writes audio bytes
to a file. Authentication goes through the authd surrogate exchange:
this script only ever handles ``hsurr:*`` surrogate values, which
Sentinel/authd replace with the real credential on egress. The real key
is never readable here, never printed, logged, or persisted.

Usage:
    python3 tts.py --text "你好" --reference-id <voice_id> --output narration.mp3
    python3 tts.py --text-file script.txt --reference-id <id> --output out.mp3 --speed 1.1

On success the response is raw audio bytes (no JSON wrapper).
On error the API returns JSON {status, message} (401/402/404) or a 422
validation list -- both are printed and the exit code is non-zero.
"""
import argparse
import json
import os
import sys
import urllib.request
import urllib.error

sys.path.insert(0, "/opt/hatch/skills/skill-creator/bin")
import dynamic_credentials as dc

API_URL = "https://api.fish.audio/v1/tts"
ALLOWED_HOSTS = ["api.fish.audio"]
CREDENTIAL_NAME = "custom.fish-audio"
FREE_MODEL = "s2.1-pro-free"


def main() -> int:
    ap = argparse.ArgumentParser(description="Fish Audio TTS")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--text", help="Text to synthesize")
    src.add_argument("--text-file", help="Path to a UTF-8 text file to synthesize")
    ap.add_argument("--reference-id", required=True, help="Voice model ID (reference_id)")
    ap.add_argument("--output", required=True, help="Output audio file path")
    ap.add_argument("--model", default=FREE_MODEL,
                    help=f"Model header (default: {FREE_MODEL}, free until 2026-11-30)")
    ap.add_argument("--format", default="mp3", choices=["mp3", "wav", "pcm", "opus"],
                    help="Audio format (default: mp3)")
    ap.add_argument("--speed", type=float, default=1.0,
                    help="Prosody speed 0.5-2.0 (default: 1.0)")
    ap.add_argument("--bitrate", type=int, default=128, help="MP3 bitrate kbps (default: 128)")
    args = ap.parse_args()

    text = args.text
    if args.text_file:
        with open(args.text_file, "r", encoding="utf-8") as f:
            text = f.read()
    if not text or not text.strip():
        print("ERROR: empty text", file=sys.stderr)
        return 2

    payload = {
        "text": text,
        "reference_id": args.reference_id,
        "format": args.format,
        "normalize": True,
        "latency": "normal",
        "prosody": {"speed": args.speed, "volume": 0},
    }
    if args.format == "mp3":
        payload["mp3_bitrate"] = args.bitrate
    elif args.format in ("wav", "pcm"):
        payload["sample_rate"] = 44100

    req = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "model": args.model,
        },
        method="POST",
    )
    try:
        dc.add_surrogate_to_request(
            req, CREDENTIAL_NAME, entry_name="access_token",
            allowed_hosts=ALLOWED_HOSTS,
        )
    except dc.DynamicCredentialError as e:
        print(f"ERROR: credential: {e}", file=sys.stderr)
        return 2

    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            body = dc.read_response_body(resp)
            ctype = resp.headers.get("Content-Type", "")
            if ctype.startswith("application/json") or body[:1] == b"{":
                print(f"ERROR: API returned JSON instead of audio: {body[:500]!r}",
                      file=sys.stderr)
                return 1
            with open(args.output, "wb") as f:
                f.write(body)
    except urllib.error.HTTPError as e:
        detail = e.read()[:500]
        print(f"ERROR: HTTP {e.code}: {detail!r}", file=sys.stderr)
        if e.code in (401, 403):
            print("HINT: a request that did carry the credential was rejected; "
                  "the stored key may be wrong or revoked -- reconnect "
                  "custom.fish-audio.", file=sys.stderr)
        return 1
    except Exception as e:  # network, timeout, etc.
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    size = os.path.getsize(args.output)
    print(f"OK: {args.output} ({size} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
