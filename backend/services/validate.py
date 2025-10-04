# backend/services/validate.py
"""
Validation & coercion utilities for Gemini output.
Ensures the JSON has the shape that the frontend expects.
"""

from __future__ import annotations
from typing import Any, Dict, List
from pydantic import BaseModel


class KeyTerm(BaseModel):
    term: str
    definition: str


class ProcessResult(BaseModel):
    plain_summary: str
    key_terms: List[KeyTerm]
    action_items: List[str]
    red_flags: List[str]
    disclaimers: List[str]


def coerce_process_result(raw: Dict[str, Any]) -> ProcessResult:
    """
    Make best-effort to coerce model output to ProcessResult.
    Fills missing keys and coerces key_terms if needed.
    """
    raw = dict(raw or {})
    raw.setdefault("plain_summary", "")
    raw.setdefault("key_terms", [])
    raw.setdefault("action_items", [])
    raw.setdefault("red_flags", [])
    raw.setdefault("disclaimers", ["This is not medical advice. Contact your clinician if you have concerns."])

    # Normalize key_terms
    normalized_terms: List[Dict[str, str]] = []
    for t in raw.get("key_terms", []):
        if isinstance(t, dict) and "term" in t and "definition" in t:
            normalized_terms.append({"term": str(t["term"]), "definition": str(t["definition"])})
        elif isinstance(t, list) and len(t) >= 2:
            normalized_terms.append({"term": str(t[0]), "definition": str(t[1])})
        elif isinstance(t, str):
            normalized_terms.append({"term": t, "definition": ""})
    raw["key_terms"] = normalized_terms

    # Coerce lists to strings
    for k in ("action_items", "red_flags", "disclaimers"):
        raw[k] = [str(x) for x in (raw.get(k) or [])]

    return ProcessResult(**raw)