"""
ElevenLabs TTS (returns list of MP3 bytes, one per paragraph).
"""
from __future__ import annotations
import os, json
from typing import List
import requests

def _secrets():
    p = os.path.join(os.path.dirname(__file__), "secrets.json")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def tts_paragraphs(paragraphs: List[str], voice_id: str | None = None) -> List[bytes]:
    s = _secrets()
    api_key = s.get("ELEVENLABS_API_KEY")
    if not api_key:
        return []
    voice = voice_id or s.get("ELEVENLABS_DEFAULT_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"

    headers = {
        "xi-api-key": api_key,
        "accept": "audio/mpeg",
        "content-type": "application/json",
    }

    results: List[bytes] = []
    for p in paragraphs or []:
        r = requests.post(url, headers=headers, json={"text": p}, timeout=60)
        r.raise_for_status()
        results.append(r.content)
    return results