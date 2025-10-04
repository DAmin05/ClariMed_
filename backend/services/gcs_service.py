"""
Google Cloud Storage helpers (signed URLs + upload bytes).
Reads bucket & creds from services/secrets.json.
"""
from __future__ import annotations
import os, json, datetime
from typing import Optional
from google.cloud import storage

def _secrets():
    p = os.path.join(os.path.dirname(__file__), "secrets.json")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def _client() -> storage.Client:
    s = _secrets()
    cred_path = s.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not (cred_path and os.path.exists(cred_path)):
        raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS missing or not found.")
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path
    return storage.Client()

def _bucket():
    s = _secrets()
    name = s.get("GCP_BUCKET_NAME", "").strip()
    if not name:
        raise RuntimeError("GCP_BUCKET_NAME missing in secrets.json")
    return _client().bucket(name)

def signed_upload_url(object_name: str, content_type: str = "application/pdf", expires_minutes: int = 15) -> str:
    blob = _bucket().blob(object_name)
    return blob.generate_signed_url(
        version="v4",
        expiration=datetime.timedelta(minutes=expires_minutes),
        method="PUT",
        content_type=content_type,
    )

def signed_read_url(object_name: str, expires_minutes: int = 60, response_content_type: Optional[str] = None) -> str:
    blob = _bucket().blob(object_name)
    params = {"response_type": response_content_type} if response_content_type else None
    return blob.generate_signed_url(
        version="v4",
        expiration=datetime.timedelta(minutes=expires_minutes),
        method="GET",
        query_parameters=params,
    )

def upload_bytes(object_name: str, data: bytes, content_type: str) -> str:
    blob = _bucket().blob(object_name)
    blob.upload_from_string(data, content_type=content_type)
    return f"gs://{_secrets()['GCP_BUCKET_NAME']}/{object_name}"