import uuid, json
from typing import Any, Dict, List
from flask import Flask, request, jsonify, abort
from flask_cors import CORS

# Services
from services.gemini_service import generate_json, translate_values
from services.firebase_service import verify_id_token_optional, save_session_result_optional
from services.gcs_service import signed_upload_url, signed_read_url, upload_bytes
from services.ocr_service import run_ocr_gcs
from services.elevenlabs_service import tts_paragraphs

app = Flask(__name__)
CORS(app)

SESSIONS: Dict[str, Dict[str, Any]] = {}

# ---------- Helpers ----------
def build_prompt(ocr_text: str, target_language: str = "en") -> str:
    SYSTEM = (
        "You are a patient-education assistant. Explain medical documents in plain language (6th–8th grade). "
        "No diagnosis/prescriptions. Define key terms briefly. Provide general next steps and red flags. "
        "If unsure, say so. Return ONLY valid JSON with keys: "
        '{"plain_summary": "...", "key_terms":[{"term":"...","definition":"..."}], '
        '"action_items":["..."], "red_flags":["..."], "disclaimers":["..."]}'
    )
    return f"""
{SYSTEM}

Target output language: {target_language}

Source text:
<<<
{ocr_text}
>>>

Instructions:
- "plain_summary": 2–5 short paragraphs in {target_language}.
- "key_terms": 3–10 concise definitions.
- "action_items": 3–8 general steps (not medical advice).
- "red_flags": 3–8 urgent warning signs.
- "disclaimers": include at least:
  - "This is educational information, not medical advice."
  - "Contact your clinician for personalized guidance."
Return ONLY valid JSON.
""".strip()

def coerce_result(raw: Dict[str, Any]) -> Dict[str, Any]:
    raw = dict(raw or {})
    raw.setdefault("plain_summary", "")
    raw.setdefault("key_terms", [])
    raw.setdefault("action_items", [])
    raw.setdefault("red_flags", [])
    raw.setdefault("disclaimers", ["This is not medical advice. Contact your clinician if you have concerns."])
    terms = []
    for t in raw.get("key_terms", []):
        if isinstance(t, dict) and "term" in t and "definition" in t:
            terms.append({"term": str(t["term"]), "definition": str(t["definition"])})
        elif isinstance(t, list) and len(t) >= 2:
            terms.append({"term": str(t[0]), "definition": str(t[1])})
        elif isinstance(t, str):
            terms.append({"term": t, "definition": ""})
    raw["key_terms"] = terms
    for k in ("action_items", "red_flags", "disclaimers"):
        raw[k] = [str(x) for x in (raw.get(k) or [])]
    return raw

# ---------- Basic routes ----------
@app.get("/")
def index():
    return "ClariMed API running. Try GET /upload-url or POST /process", 200

@app.get("/healthz")
def health():
    return {"status": "ok"}, 200

# ---------- Storage: get signed URL for browser upload ----------
@app.get("/upload-url")
def get_upload_url():
    session_id = str(uuid.uuid4())
    object_name = f"uploads/{session_id}.pdf"
    try:
        url = signed_upload_url(object_name, content_type="application/pdf", expires_minutes=15)
    except Exception as e:
        return abort(500, f"GCS signed URL error: {e}")
    gcs_uri = f"gs://{signed_read_url.__self__._bucket().name}/{object_name}"  # hack to get bucket name
    SESSIONS[session_id] = {"gcs_uri": gcs_uri}
    return jsonify({"upload_url": url, "gcs_uri": gcs_uri, "session_id": session_id})

# ---------- Process a GCS file (PDF/Image) ----------
@app.post("/process")
def process_doc():
    body = request.get_json(force=True) or {}
    gcs_uri = body.get("gcs_uri")
    lang = body.get("language", "en")
    if not gcs_uri:
        return abort(400, "Missing 'gcs_uri'")

    try:
        # 1) OCR
        ocr_text = run_ocr_gcs(gcs_uri)

        # 2) Prompt Gemini
        prompt = build_prompt(ocr_text=ocr_text, target_language=lang)
        raw = generate_json(prompt)
        result = coerce_result(raw)

        # 3) Cache & optional persist
        session_id = None
        for sid, data in SESSIONS.items():
            if data.get("gcs_uri") == gcs_uri:
                session_id = sid
                break
        if not session_id:
            session_id = str(uuid.uuid4())
            SESSIONS[session_id] = {}
        SESSIONS[session_id].update({"gcs_uri": gcs_uri, "language": lang, "result": result})

        uid = verify_id_token_optional(request)
        if uid:
            save_session_result_optional(uid, session_id, {
                "sourceType": "upload",
                "gcsUri": gcs_uri,
                "language": lang,
                "result": result,
                "status": "done",
            })

        return jsonify({"session_id": session_id, "result": result})

    except Exception as e:
        return abort(500, f"Processing error: {e}")

# ---------- Process pasted raw text (no OCR) ----------
@app.post("/process-text")
def process_text():
    body = request.get_json(force=True) or {}
    text = (body.get("text") or "").strip()
    lang = body.get("language", "en")
    if not text:
        return abort(400, "Missing 'text'")
    prompt = build_prompt(ocr_text=text, target_language=lang)
    raw = generate_json(prompt)
    result = coerce_result(raw)
    session_id = body.get("session_id") or str(uuid.uuid4())
    SESSIONS[session_id] = {"language": lang, "result": result}
    uid = verify_id_token_optional(request)
    if uid:
        save_session_result_optional(uid, session_id, {
            "sourceType": "text",
            "inputPreview": text[:280],
            "language": lang,
            "result": result,
            "status": "done",
        })
    return jsonify({"session_id": session_id, "result": result})

# ---------- Translate stored result ----------
@app.post("/translate")
def translate():
    body = request.get_json(force=True) or {}
    session_id = body.get("session_id")
    target = body.get("target_language")
    if not session_id or not target:
        return abort(400, "Missing 'session_id' or 'target_language'")
    sess = SESSIONS.get(session_id)
    if not sess:
        return abort(404, "Session not found")
    translated = coerce_result(translate_values(sess["result"], target))
    sess.setdefault("translations", {})[target] = translated
    return jsonify(translated)

# ---------- TTS: generate audio for summary paragraphs ----------
@app.post("/tts")
def tts():
    """
    Body: { "session_id": "<id>" }
    Creates MP3s with ElevenLabs, uploads to GCS, and returns signed GET URLs.
    """
    body = request.get_json(force=True) or {}
    session_id = body.get("session_id")
    if not session_id:
        return abort(400, "Missing 'session_id'")
    sess = SESSIONS.get(session_id)
    if not (sess and sess.get("result")):
        return abort(404, "Session not found or empty")

    # Split summary into paragraphs (simple split on double newline or periods)
    summary = sess["result"].get("plain_summary", "")
    if not summary.strip():
        return abort(400, "No summary available for TTS")
    paragraphs = [p.strip() for p in summary.split("\n\n") if p.strip()]
    if not paragraphs:
        paragraphs = [summary]

    # 1) Generate MP3 bytes
    mp3s = tts_paragraphs(paragraphs)

    # 2) Upload each to GCS and return signed read URLs
    urls: List[str] = []
    for i, data in enumerate(mp3s):
        obj = f"audio/{session_id}/part_{i+1}.mp3"
        upload_bytes(obj, data, content_type="audio/mpeg")
        url = signed_read_url(obj, expires_minutes=60, response_content_type="audio/mpeg")
        urls.append(url)

    # Cache for convenience
    sess["audio"] = urls
    return jsonify({"audio_urls": urls})

# ---------- Sessions helper ----------
@app.get("/sessions/<session_id>")
def get_session(session_id: str):
    return jsonify(SESSIONS.get(session_id, {}))

# ---------- Entrypoint ----------
if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", "5001"))
    print(f"🚀 Running Flask server on http://127.0.0.1:{port}")
    app.run(host="127.0.0.1", port=port, debug=True, use_reloader=False)