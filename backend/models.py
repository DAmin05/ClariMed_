# backend/models.py
"""
Pydantic models for ClariMed (Flask backend).

These schemas keep request/response payloads well-typed and consistent
between the frontend and backend.
"""

from __future__ import annotations

from typing import List
from pydantic import BaseModel, Field


# ---------- Requests ----------

class ProcessRequest(BaseModel):
    """Request body for /process"""
    gcs_uri: str = Field(..., description="gs:// URI of the uploaded document")
    language: str = Field("en", description="Preferred language code for initial output (e.g., 'en', 'es')")


class TranslateRequest(BaseModel):
    """Request body for /translate"""
    session_id: str = Field(..., description="Session ID returned from /upload-url")
    target_language: str = Field(..., description="Target language code (e.g., 'es', 'fr', 'en')")


# If/when you re-enable ElevenLabs TTS, uncomment this:
# class TTSRequest(BaseModel):
#     """Request body for /tts (optional feature)"""
#     session_id: str = Field(..., description="Session ID for which to generate audio")
#     paragraphs: List[str] = Field(..., description="List of text paragraphs to convert to audio")


# ---------- Responses ----------

class KeyTerm(BaseModel):
    term: str
    definition: str


class ProcessResult(BaseModel):
    """Response body from /process (and also used by /translate)."""
    plain_summary: str
    key_terms: List[KeyTerm]
    action_items: List[str]
    red_flags: List[str]
    disclaimers: List[str]


class UploadURLResponse(BaseModel):
    """Response body from /upload-url"""
    upload_url: str  # signed PUT URL for the browser to upload the PDF
    gcs_uri: str     # gs:// path where the file will live
    session_id: str  # ID you can use to fetch/update this session later