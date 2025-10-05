"""
Firebase helpers (auth + Firestore + Storage), via services/secrets.json and firebase-adminsdk.json.
Degrades gracefully if not configured (functions return None/No-ops).
"""
from __future__ import annotations
import os, json, uuid
from functools import lru_cache
from typing import Any, Dict, Optional

try:
    import firebase_admin
    from firebase_admin import credentials, auth, firestore, storage
except Exception:
    firebase_admin = None
    credentials = None
    auth = None
    firestore = None
    storage = None

@lru_cache(maxsize=1)
def _secrets() -> Dict[str, Any]:
    path = os.path.join(os.path.dirname(__file__), "secrets.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

_app = None
_db = None
_bucket = None

def _maybe_init():
    """Initialize Firebase Admin app + Firestore + Storage if secrets provided."""
    global _app, _db, _bucket
    if _app or not firebase_admin:
        return
    s = _secrets()
    pid = s.get("FIREBASE_PROJECT_ID")
    sa_path = s.get("FIREBASE_ADMIN_PATH")
    bucket_name = s.get("FIREBASE_STORAGE_BUCKET")

    if not (pid and sa_path and os.path.exists(sa_path)):
        return  # not configured

    cred = credentials.Certificate(sa_path)
    _app = firebase_admin.initialize_app(cred, {
        "projectId": pid,
        "storageBucket": bucket_name
    })
    _db = firestore.client()
    _bucket = storage.bucket() if storage else None

def verify_id_token_optional(req) -> Optional[str]:
    """Returns uid from Authorization: Bearer <idToken>, or None if not configured/invalid."""
    _maybe_init()
    if not (_app and auth):
        return None
    authz = req.headers.get("Authorization", "")
    if not authz.startswith("Bearer "):
        return None
    token = authz.split(" ", 1)[1].strip()
    try:
        decoded = auth.verify_id_token(token)
        return decoded.get("uid")
    except Exception:
        return None

def save_session_result_optional(uid: str, session_id: str, payload: Dict[str, Any]):
    """Saves session JSON under /users/{uid}/sessions/{session_id} if Firestore available."""
    _maybe_init()
    if not (_db and uid):
        return
    payload = dict(payload or {})
    payload.setdefault("createdAt", firestore.SERVER_TIMESTAMP)
    payload["updatedAt"] = firestore.SERVER_TIMESTAMP
    _db.collection("users").document(uid).collection("sessions").document(session_id).set(payload, merge=True)

def upload_bytes_to_storage(object_name: str, data: bytes, content_type: str = "application/octet-stream") -> Optional[str]:
    """
    Uploads bytes to Firebase Storage and returns a **download URL** using a token.
    No-op returns None if storage not configured.
    """
    _maybe_init()
    if not _bucket:
        return None

    blob = _bucket.blob(object_name)

    # Add a download token to metadata so we can construct a URL
    download_token = str(uuid.uuid4())
    blob.metadata = {"firebaseStorageDownloadTokens": download_token}

    blob.upload_from_string(data, content_type=content_type)

    # Construct Firebase download URL (token required)
    bucket_name = _bucket.name
    # object_name must be URL-encoded for the path segment; simplest: replace "/" with "%2F"
    encoded_path = object_name.replace("/", "%2F")
    return f"https://firebasestorage.googleapis.com/v0/b/{bucket_name}/o/{encoded_path}?alt=media&token={download_token}"