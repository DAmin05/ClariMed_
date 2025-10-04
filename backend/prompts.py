# backend/prompts.py
"""
Prompt templates for ClariMed (Flask backend).

Use with services/gemini.py:
- generate_json(build_main_prompt(...))
- generate_json(build_translate_prompt(...))

Design goals:
- Force STRICT JSON output (no prose)
- Keep language at grade 6–8 readability
- Avoid diagnosis; educational tone only
- Encourage model to say "I don't know" if uncertain
"""

from __future__ import annotations
from textwrap import dedent


# ---- Constants ----

SYSTEM_PROMPT = dedent("""
You are a patient-education assistant. Your job is to convert medical documents into accurate,
culturally sensitive explanations at a 6th–8th grade reading level.

Rules:
- Do NOT diagnose or prescribe. This is educational information only.
- Explain what the document says in plain language.
- Define medical terms clearly and briefly.
- Provide a short checklist of general next steps a typical patient might consider.
- List urgent warning signs ("red flags") to seek care.
- If information is missing or uncertain, say so explicitly and avoid guessing.
- Keep sentences short. Prefer everyday words over jargon.
- Output ONLY valid JSON that matches the required schema (no markdown or commentary).
""").strip()


# The exact JSON keys your UI expects:
JSON_SCHEMA_KEYS = {
    "plain_summary": "string",
    "key_terms": [{"term": "string", "definition": "string"}],
    "action_items": ["string"],
    "red_flags": ["string"],
    "disclaimers": ["string"]
}


# ---- Prompt Builders ----

def build_main_prompt(
    ocr_text: str,
    rag_snippets: str = "",
    target_language: str = "en"
) -> str:
    """
    Build the main prompt for Gemini:
    - Takes OCR text and any Snowflake-provided RAG snippets
    - Requests STRICT JSON with the required keys
    - Asks for output in `target_language` (default English)
    """
    prompt = f"""
{SYSTEM_PROMPT}

Target output language: {target_language}

Required JSON schema (keys and value types):
{JSON_SCHEMA_KEYS}

Source document text (verbatim OCR):
<<<
{ocr_text}
>>>

Contextual facts/snippets (from Snowflake; may be empty):
<<<
{rag_snippets}
>>>

Instructions for the JSON content:
- "plain_summary": 2–5 short paragraphs explaining the document in {target_language}, grade 6–8 reading level.
- "key_terms": 3–10 key medical terms with one-sentence, plain-language definitions.
- "action_items": 3–8 general steps a typical patient might consider (no personalized medical advice).
- "red_flags": 3–8 symptoms/signs that usually require urgent attention (simple and clear).
- "disclaimers": Always include at least:
  - "This is educational information, not medical advice."
  - "Contact your clinician for personalized guidance."

Important:
- Use only information supported by the source text and snippets. If uncertain, state uncertainty.
- DO NOT include markdown, backticks, or any text outside the JSON.
- Return ONLY valid JSON (no trailing commas, no comments).
"""
    return dedent(prompt).strip()


def build_translate_prompt(
    json_payload: dict,
    target_language: str
) -> str:
    """
    Ask Gemini to translate ONLY the JSON VALUES to the target language,
    preserving the original keys and structure exactly.
    """
    import json as _json
    payload_str = _json.dumps(json_payload, ensure_ascii=False)

    prompt = f"""
Translate the JSON VALUES (not keys) to "{target_language}" and return ONLY valid JSON.
- Preserve the exact keys and structure.
- Keep arrays and objects as-is.
- Do NOT add commentary, code fences, or markdown.

JSON to translate:
{payload_str}
"""
    return dedent(prompt).strip()


# ---- (Optional) Few-shot examples (kept small for token economy) ----
# You can add tiny, inline exemplars if you see Gemini drifting.
# For hackathons, the schema + rules above are usually sufficient.