# backend/services/elevenlabs.py
"""
ElevenLabs TTS helper.
Env:
- ELEVENLABS_API_KEY
"""

from __future__ import annotations
import os
import requests

API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
DEFAULT_VOICE_ID = "EXAVITQu4vr4xnSDxMaL"  # replace if you want
BASE_URL = "https://api.elevenlabs.io/v1/text-to-speech"


def tts_paragraphs(paragraphs: list[str], voice_id: str | None = None) -> list[bytes]:
    """
    Generate MP3 bytes for each paragraph. Returns a list of bytes objects.
    If API key is missing, returns [] (non-fatal for demo).
    """
    if not API_KEY:
        return []

    vid = voice_id or DEFAULT_VOICE_ID
    url = f"{BASE_URL}/{vid}"
    headers = {
        "xi-api-key": API_KEY,
        "accept": "audio/mpeg",
        "content-type": "application/json",
    }

    results: list[bytes] = []
    for p in paragraphs or []:
        resp = requests.post(url, headers=headers, json={"text": p}, timeout=60)
        resp.raise_for_status()
        results.append(resp.content)
    return results