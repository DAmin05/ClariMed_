"""
Firebase helpers (auth + Firestore), using services/secrets.json + firebase-adminsdk.json.
Degrades gracefully if not configured.
"""
from __future__ import annotations
import os, json
from functools import lru_cache
from typing import Any, Dict, Optional

try:
    import firebase_admin
    from firebase_admin import credentials, auth, firestore
except Exception:
    firebase_admin = None
    credentials = None
    auth = None
    firestore = None

@lru_cache(maxsize=1)
def _secrets() -> Dict[str, Any]:
    p = os.path.join(os.path.dirname(__file__), "secrets.json")
    if not os.path.exists(p):
        return {}
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

_app = None
_db = None

def _maybe_init():
    global _app, _db
    if _app or not firebase_admin:
        return
    s = _secrets()
    pid = s.get("FIREBASE_PROJECT_ID")
    sa_path = s.get("FIREBASE_ADMIN_PATH")
    if not (pid and sa_path and os.path.exists(sa_path)):
        return
    cred = credentials.Certificate(sa_path)
    _app = firebase_admin.initialize_app(cred, {"projectId": pid})
    _db = firestore.client()

def verify_id_token_optional(req) -> Optional[str]:
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
    _maybe_init()
    if not (_db and uid):
        return
    payload = dict(payload or {})
    payload.setdefault("createdAt", firestore.SERVER_TIMESTAMP)
    payload["updatedAt"] = firestore.SERVER_TIMESTAMP
    _db.collection("users").document(uid).collection("sessions").document(session_id).set(payload, merge=True)