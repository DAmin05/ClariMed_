# app.py
# ClariMed (Flask backend) — ElevenLabs on hold
# ------------------------------------------------
# Endpoints:
#   GET  /upload-url        -> GCS signed PUT URL for PDF upload
#   POST /process           -> OCR -> (Snowflake RAG) -> Gemini -> JSON result
#   POST /translate         -> Translate existing JSON result to a target language
#   GET  /sessions/<sid>    -> Return cached session payload (demo-helper)
#
# Env (see .env.example):
#   GOOGLE_APPLICATION_CREDENTIALS, GCP_BUCKET_NAME
#   GEMINI_API_KEY
#   SNOWFLAKE_USER, SNOWFLAKE_PASSWORD, SNOWFLAKE_ACCOUNT
#   SNOWFLAKE_DATABASE, SNOWFLAKE_SCHEMA, SNOWFLAKE_WAREHOUSE
# ------------------------------------------------

import os
import uuid
import datetime
import json
from typing import Any, Dict, List

from dotenv import load_dotenv
from flask import Flask, request, jsonify, abort
from flask_cors import CORS
from pydantic import ValidationError

# ---- local modules ----
from models import ProcessRequest, TranslateRequest, UploadURLResponse
from prompts import build_main_prompt, build_translate_prompt

from services.gcs import signed_upload_url as gcs_signed_upload_url
from services.ocr import run_ocr_gcs
from services.snowflake_client import fetch_rag_snippets
from services.gemini import generate_json as gemini_generate_json
from services.gemini import translate_json as gemini_translate_json
from services.validate import coerce_process_result as validate_process_result

# -----------------------
# Load environment
# -----------------------
load_dotenv()

GCP_BUCKET = os.getenv("GCP_BUCKET_NAME", "").strip()

# -----------------------
# Flask setup
# -----------------------
app = Flask(__name__)
CORS(app)

# In-memory session store (simple for hackathon)
SESSIONS: Dict[str, Dict[str, Any]] = {}

# -----------------------
# Helpers
# -----------------------
def _json_abort(status: int, msg: str):
    return abort(status, msg)


# -----------------------
# Routes
# -----------------------
@app.route("/upload-url", methods=["GET"])
def get_upload_url():
    """
    Returns:
      {
        "upload_url": "<signed PUT url>",
        "gcs_uri": "gs://bucket/uploads/<session>.pdf",
        "session_id": "<uuid>"
      }
    """
    if not GCP_BUCKET:
        return _json_abort(500, "GCP_BUCKET_NAME not configured")

    session_id = str(uuid.uuid4())
    object_name = f"uploads/{session_id}.pdf"

    try:
        url = gcs_signed_upload_url(object_name, content_type="application/pdf", expires_minutes=15)
    except Exception as e:
        return _json_abort(500, f"GCS signed URL error: {e}")

    gcs_uri = f"gs://{GCP_BUCKET}/{object_name}"
    SESSIONS[session_id] = {"gcs_uri": gcs_uri, "created_at": datetime.datetime.utcnow().isoformat()}

    # shape matches UploadURLResponse but we just return JSON
    return jsonify({"upload_url": url, "gcs_uri": gcs_uri, "session_id": session_id})


@app.route("/process", methods=["POST"])
def process_doc():
    """
    Body: { "gcs_uri": "gs://.../file.pdf", "language": "en" }
    Returns ProcessResult JSON (plain_summary, key_terms, action_items, red_flags, disclaimers)
    """
    try:
        data = request.get_json(force=True)
        req = ProcessRequest(**data)
    except (TypeError, ValidationError) as e:
        return _json_abort(400, f"Bad request: {e}")

    try:
        # 1) OCR
        ocr_text = run_ocr_gcs(req.gcs_uri)

        # 2) naive candidate term extraction (improve later if time)
        tokens = {w.strip(" ,.:;()[]{}\"'").lower() for w in ocr_text.split() if len(w) > 3}
        candidate_terms = list(tokens)[:30]

        # 3) Snowflake RAG (non-fatal if unavailable)
        try:
            rag_text = fetch_rag_snippets(candidate_terms)
        except Exception as e:
            rag_text = ""
            print("Snowflake RAG error:", e)

        # 4) Gemini -> JSON
        prompt_text = build_main_prompt(ocr_text=ocr_text, rag_snippets=rag_text, target_language=req.language)
        raw_json = gemini_generate_json(prompt_text)

        # 5) Validate/coerce to stable shape the UI expects
        result_obj = validate_process_result(raw_json)  # returns a pydantic model
        result = result_obj.dict()

        # 6) Cache to session
        sid = None
        for k, v in SESSIONS.items():
            if v.get("gcs_uri") == req.gcs_uri:
                sid = k
                break
        if sid:
            SESSIONS[sid]["result"] = result
            SESSIONS[sid]["language"] = req.language

        return jsonify(result)

    except Exception as e:
        return _json_abort(500, f"Processing error: {e}")


@app.route("/translate", methods=["POST"])
def translate():
    """
    Body: { "session_id": "...", "target_language": "es" }
    Returns translated ProcessResult JSON
    """
    try:
        data = request.get_json(force=True)
        req = TranslateRequest(**data)
    except (TypeError, ValidationError) as e:
        return _json_abort(400, f"Bad request: {e}")

    sess = SESSIONS.get(req.session_id)
    if not sess or "result" not in sess:
        return _json_abort(404, "Session not found or empty")

    try:
        # Build a strict translate prompt, then parse
        prompt = build_translate_prompt(json_payload=sess["result"], target_language=req.target_language)
        translated_raw = gemini_generate_json(prompt)  # reusing generate_json for strict JSON
        # Validate shape
        translated_obj = validate_process_result(translated_raw)
        translated = translated_obj.dict()

        # Cache translated
        SESSIONS[req.session_id]["result_translated"] = translated
        SESSIONS[req.session_id]["language"] = req.target_language

        return jsonify(translated)

    except Exception as e:
        return _json_abort(500, f"Translation error: {e}")


@app.route("/sessions/<session_id>", methods=["GET"])
def get_session(session_id: str):
    return jsonify(SESSIONS.get(session_id, {}))


# -----------------------
# Entrypoint
# -----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)