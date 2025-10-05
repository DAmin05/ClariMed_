# app.py
import json
import uuid
from pathlib import Path
from datetime import timedelta
from typing import Any, Dict

from flask import Flask, request, jsonify
from flask_cors import CORS

# Firebase
import firebase_admin
from firebase_admin import credentials, firestore, storage

# Gemini
import google.generativeai as genai

# ElevenLabs (HTTP; works with only API key + voice id)
import requests

# PDF text extraction
from pypdf import PdfReader


# ---------- Setup & helpers ----------

HERE = Path(__file__).resolve().parent
SECRETS_PATH = HERE / "services" / "secrets.json"

def load_secrets() -> Dict[str, Any]:
    if not SECRETS_PATH.exists():
        raise FileNotFoundError(f"Missing secrets.json at {SECRETS_PATH}")
    with SECRETS_PATH.open() as f:
        return json.load(f)

secrets = load_secrets()

# Firebase init
cred_path = (HERE / secrets["FIREBASE_ADMIN_PATH"]).resolve()
if not cred_path.exists():
    raise FileNotFoundError(
        f"Service account JSON not found at {cred_path}. "
        f"Update 'FIREBASE_ADMIN_PATH' in secrets.json."
    )

if not firebase_admin._apps:
    cred = credentials.Certificate(str(cred_path))
    firebase_admin.initialize_app(
        cred,
        {
            "projectId": secrets["FIREBASE_PROJECT_ID"],
            "storageBucket": secrets["FIREBASE_STORAGE_BUCKET"],
        },
    )

db = firestore.client()
bucket = storage.bucket()  # default bucket from config

# Gemini init
genai.configure(api_key=secrets["GEMINI_API_KEY"])
GEMINI_MODEL_ID = secrets.get("GEMINI_MODEL", "gemini-2.5-flash")
gemini_model = genai.GenerativeModel(GEMINI_MODEL_ID)

# ElevenLabs
ELEVEN_API_KEY = secrets["ELEVENLABS_API_KEY"]
DEFAULT_VOICE_ID = secrets.get("ELEVENLABS_DEFAULT_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")


def upload_bytes_to_storage(bytes_data: bytes, path: str, content_type: str) -> str:
    """Upload bytes to Firebase Storage and return a signed URL (1h)."""
    blob = bucket.blob(path)
    blob.upload_from_string(bytes_data, content_type=content_type)
    url = blob.generate_signed_url(
        expiration=timedelta(hours=1),
        version="v4",
    )
    return url


def error(message: str, code: int = 400):
    return jsonify({"ok": False, "error": message}), code


# ---------- Flask app ----------

app = Flask(__name__)
CORS(app)


@app.get("/health")
def health():
    return jsonify({
        "ok": True,
        "project": secrets["FIREBASE_PROJECT_ID"],
        "bucket": secrets["FIREBASE_STORAGE_BUCKET"],
        "gemini_model": GEMINI_MODEL_ID
    })


# --------- Gemini endpoints ---------

@app.post("/process-text")
def process_text():
    """
    Body (JSON): { "text": "..." }
    Returns: { ok, summary, key_points }
    """
    data = request.get_json(silent=True) or {}
    text = data.get("text")
    if not text:
        return error("Missing 'text'")

    prompt = (
        "You are a careful, friendly medical assistant.\n"
        "Read the following medical information and explain it clearly and calmly in plain language suitable for a 6th–8th grade reader.\n"
        "Avoid phrases like 'Here is a summary' or 'This report says' — instead, write as if you are directly explaining the situation to the patient.\n"
        "\n"
        "OUTPUT FORMAT (very important):\n"
        "1) Write a concise paragraph (4–6 sentences) that clearly explains the situation and main points in everyday language, as if speaking to a patient or their family.\n"
        "2) Provide 5–8 bullet points that start with '- ' (dash + space). Bullets should include:\n"
        "   - The 3–5 most important takeaways in simple terms\n"
        "   - Practical steps the patient or family can take at home\n"
        "   - When they should contact a doctor or seek urgent care (clear 'red flags')\n"
        "   - Any key terms, tests, or diagnoses explained simply\n"
        "   - Helpful recommendations or lifestyle tips to support care and health\n"
        "\n"
        "Rules:\n"
        "- Do not guess diagnoses. If something is uncertain, say it may require a clinician’s review.\n"
        "- Avoid medical jargon. Prefer short, simple sentences and familiar words.\n"
        "- Do not include numbered lists — use only '- ' bullets after the paragraph.\n"
        "- Do not include section headers. Start with the paragraph, then list the bullet points.\n"
        "- Write in a warm, helpful, and professional tone.\n"
        "\n"
        "TEXT TO SIMPLIFY:\n"
        f"{text}"
    )
    try:
        resp = gemini_model.generate_content(prompt)
        result = resp.text or ""
        # very simple split heuristic
        parts = result.split("\n- ")
        summary = parts[0].strip()
        key_points = [p.strip("- ").strip() for p in parts[1:]] if len(parts) > 1 else []
        return jsonify({"ok": True, "summary": summary, "key_points": key_points})
    except Exception as e:
        return error(f"Gemini error: {e}", 500)


@app.post("/translate")
def translate():
    """
    Body (JSON): { "text": "...", "target_language": "Spanish" }
    Returns: { ok, translation }
    """
    data = request.get_json(silent=True) or {}
    text = data.get("text")
    target = data.get("target_language")
    if not text or not target:
        return error("Missing 'text' or 'target_language'")

    prompt = (
        f"Translate the following text to {target}. "
        f"Return only the translated text.\n\n{text}"
    )
    try:
        resp = gemini_model.generate_content(prompt)
        return jsonify({"ok": True, "translation": (resp.text or "").strip()})
    except Exception as e:
        return error(f"Gemini error: {e}", 500)


# --------- ElevenLabs TTS ---------

@app.post("/tts")
def tts():
    """
    Body (JSON): { "text": "...", "voice_id": "optional" }
    Returns: { ok, audio_url, path }
    """
    data = request.get_json(silent=True) or {}
    text = data.get("text")
    voice_id = data.get("voice_id", DEFAULT_VOICE_ID)

    if not text:
        return error("Missing 'text'")

    try:
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        headers = {
            "xi-api-key": ELEVEN_API_KEY,
            "accept": "audio/mpeg",
            "content-type": "application/json",
        }
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",  # ensure multilingual reliability
            "voice_settings": {"stability": 0.3, "similarity_boost": 0.7},
        }
        r = requests.post(url, headers=headers, json=payload, timeout=60)
        if r.status_code >= 400:
            # log the real reason to console
            print("ElevenLabs error:", r.status_code, r.text)
            return error(f"ElevenLabs error {r.status_code}: {r.text}", 502)

        mp3_bytes = r.content
        storage_path = f"tts/{uuid.uuid4().hex}.mp3"
        signed_url = upload_bytes_to_storage(mp3_bytes, storage_path, "audio/mpeg")
        return jsonify({"ok": True, "audio_url": signed_url, "path": storage_path})
    except Exception as e:
        return error(f"TTS error: {e}", 500)


# --------- Storage helpers ---------

@app.post("/upload")
def upload_file():
    """
    Multipart form:
      key: file  (select a file in Postman or the frontend)
    Returns: { ok, path, url }
    """
    if "file" not in request.files:
        return error("Missing file in multipart form with key 'file'")

    file = request.files["file"]
    if not file.filename:
        return error("Empty filename")

    ext = Path(file.filename).suffix or ""
    path = f"uploads/{uuid.uuid4().hex}{ext}"
    try:
        content = file.read()
        # guess content type basic:
        content_type = file.mimetype or "application/octet-stream"
        url = upload_bytes_to_storage(content, path, content_type)
        return jsonify({"ok": True, "path": path, "url": url})
    except Exception as e:
        return error(f"Upload error: {e}", 500)


@app.get("/file-url")
def file_url():
    """
    Query: /file-url?path=uploads/abc.mp3
    Returns: { ok, url }
    """
    path = request.args.get("path")
    if not path:
        return error("Missing 'path' query param")

    try:
        blob = bucket.blob(path)
        if not blob.exists():
            return error("File not found", 404)
        url = blob.generate_signed_url(expiration=timedelta(hours=1), version="v4")
        return jsonify({"ok": True, "url": url})
    except Exception as e:
        return error(f"Signed URL error: {e}", 500)


# --------- Example Firestore route (optional) ---------

@app.post("/save-note")
def save_note():
    """
    Body (JSON): { "collection": "notes", "data": { ... } }
    Returns: { ok, id }
    """
    data = request.get_json(silent=True) or {}
    collection = data.get("collection", "notes")
    doc_data = data.get("data", {})
    if not isinstance(doc_data, dict):
        return error("'data' must be an object")

    try:
        doc_ref = db.collection(collection).document()
        doc_ref.set(doc_data)
        return jsonify({"ok": True, "id": doc_ref.id})
    except Exception as e:
        return error(f"Firestore error: {e}", 500)


# --------- NEW: Analyze PDF (extract text + summarize) ---------

@app.post("/analyze-pdf")
def analyze_pdf():
    """
    Multipart form:
      key: file  (PDF only for now)
    Returns: { ok, summary, key_points, extracted_text }
    """
    if "file" not in request.files:
        return error("Missing file in multipart form with key 'file'")

    file = request.files["file"]
    if not file.filename.lower().endswith(".pdf"):
        return error("Please upload a PDF file for now.", 415)

    try:
        reader = PdfReader(file.stream)
        extracted = []
        for page in reader.pages:
            try:
                txt = page.extract_text() or ""
            except Exception:
                txt = ""
            if txt.strip():
                extracted.append(txt.strip())

        full_text = "\n\n".join(extracted).strip()
        if not full_text:
            return error("Could not extract text from this PDF.", 422)

        # Reuse the same summarization logic
        prompt = (
            "You are a helpful medical assistant. "
            "Summarize the following text in 3–5 sentences and return 3 bullet key points.\n\n"
            f"TEXT:\n{full_text}"
        )
        resp = gemini_model.generate_content(prompt)
        result = resp.text or ""
        parts = result.split("\n- ")
        summary = parts[0].strip()
        key_points = [p.strip("- ").strip() for p in parts[1:]] if len(parts) > 1 else []

        return jsonify({
            "ok": True,
            "summary": summary,
            "key_points": key_points,
            "extracted_text": full_text
        })
    except Exception as e:
        return error(f"Analyze PDF error: {e}", 500)


# ---------- Run ----------

if __name__ == "__main__":
    import os
    port = int(os.getenv("PORT", "5001"))
    app.run(host="0.0.0.0", port=port, debug=True)