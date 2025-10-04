"""
Gemini service wrapper (reads keys from services/secrets.json).
"""
from __future__ import annotations
import json, os
from functools import lru_cache
from typing import Any, Dict
import requests

@lru_cache(maxsize=1)
def _secrets() -> Dict[str, Any]:
    p = os.path.join(os.path.dirname(__file__), "secrets.json")
    if not os.path.exists(p):
        raise FileNotFoundError(f"Missing secrets file: {p}")
    with open(p, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not data.get("GEMINI_API_KEY"):
        raise RuntimeError("GEMINI_API_KEY missing in services/secrets.json")
    return data

def _endpoint() -> str:
    model = _secrets().get("GEMINI_MODEL", "gemini-1.5-flash")
    return f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

def _api_key() -> str:
    return _secrets()["GEMINI_API_KEY"]

def _post(prompt_text: str, timeout: int = 90) -> Dict[str, Any]:
    url = _endpoint()
    headers = {"Content-Type": "application/json"}
    params = {"key": _api_key()}
    payload = {"contents": [{"parts": [{"text": prompt_text}]}]}
    r = requests.post(url, headers=headers, params=params, json=payload, timeout=timeout)
    try:
        r.raise_for_status()
    except requests.HTTPError as e:
        raise RuntimeError(f"Gemini HTTP error: {e}\n{r.text[:600]}") from e
    return r.json()

def _extract_text(api_json: Dict[str, Any]) -> str:
    try:
        return api_json["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        raise RuntimeError(f"Unexpected Gemini response.\nRaw: {json.dumps(api_json)[:800]}") from e

def _strip_fences(txt: str) -> str:
    t = txt.strip()
    if t.startswith("```"):
        t = t.strip("`").lstrip()
        if t.lower().startswith("json"):
            t = t[4:].lstrip()
    return t

def generate_json(prompt_text: str) -> Dict[str, Any]:
    data = _post(prompt_text)
    cleaned = _strip_fences(_extract_text(data))
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Gemini did not return valid JSON: {e}\nPreview:\n{cleaned[:800]}") from e

def translate_values(json_payload: Dict[str, Any], target_language: str) -> Dict[str, Any]:
    prompt = (
        "Translate the JSON VALUES (not keys) to '{lang}'. "
        "Preserve keys and structure. Return ONLY valid JSON.\n\n{payload}"
    ).format(lang=target_language, payload=json.dumps(json_payload, ensure_ascii=False))
    return generate_json(prompt)