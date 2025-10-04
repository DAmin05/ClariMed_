# backend/services/gemini.py
"""
Gemini helpers (REST). Uses Google Generative Language API.
Env:
- GEMINI_API_KEY
"""

from __future__ import annotations
import os
import json
import requests

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyAVkdXL2bhNBBou0VGbrNyGCZcplnGUmVY")
GEMINI_URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"
)

if not GEMINI_API_KEY:
    # Don’t raise on import; raise when called so dev server can boot without keys.
    pass


def _post_to_gemini(prompt_text: str) -> dict:
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not configured.")
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
    r = requests.post(GEMINI_URL, headers=headers, params=params, json=payload, timeout=90)
    r.raise_for_status()
    return r.json()


def generate_json(prompt_text: str) -> dict:
    """
    Send a prompt that returns STRICT JSON (as text) and parse it.
    Strips markdown code fences if present.
    """
    data = _post_to_gemini(prompt_text)
    try:
        text = data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        raise RuntimeError(f"Gemini response parse failure: {e}\nRaw: {json.dumps(data)[:600]}")

    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].strip()

    return json.loads(cleaned)


def translate_json(json_payload: dict, target_language: str) -> dict:
    """
    Ask Gemini to translate JSON VALUES to target_language, preserving keys.
    """
    prompt = (
        f"Translate the JSON VALUES (not keys) to {target_language}. "
        f"Preserve keys and return ONLY valid JSON.\n\n"
        f"{json.dumps(json_payload, ensure_ascii=False)}"
    )
    return generate_json(prompt)