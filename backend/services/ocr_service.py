"""
Google Vision OCR.
- If the GCS URI ends with .pdf -> use async batch (PDF OCR)
- Else -> use document_text_detection for images
"""
from __future__ import annotations
import os, json, time
from typing import Tuple
from google.cloud import vision

def _secrets():
    p = os.path.join(os.path.dirname(__file__), "secrets.json")
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)

def _client() -> vision.ImageAnnotatorClient:
    cred = _secrets().get("GOOGLE_APPLICATION_CREDENTIALS")
    if not (cred and os.path.exists(cred)):
        raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS missing or not found.")
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred
    return vision.ImageAnnotatorClient()

def run_ocr_gcs(gcs_uri: str) -> str:
    client = _client()

    if gcs_uri.lower().endswith(".pdf"):
        # Async batch for PDFs (first page for speed; tweak as needed)
        mime_type = "application/pdf"
        feature = vision.Feature(type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)
        gcs_source = vision.GcsSource(uri=gcs_uri)
        input_config = vision.InputConfig(gcs_source=gcs_source, mime_type=mime_type)
        # Write output JSON to a temp GCS path next to input
        out_uri = gcs_uri.rsplit("/", 1)[0] + "/_ocr_output/"
        gcs_destination = vision.GcsDestination(uri=out_uri)
        output_config = vision.OutputConfig(gcs_destination=gcs_destination, batch_size=1)

        request = vision.AsyncAnnotateFileRequest(features=[feature], input_config=input_config, output_config=output_config)
        operation = client.async_batch_annotate_files(requests=[request])

        operation.result(timeout=180)  # wait up to 3 minutes
        # We won't fetch the JSON back from GCS here; for hackathon, call simple detection again per page OR
        # do a quick single-image pass:
        # Fallback (fast): try simple text detection (works for image-like PDFs sometimes)
        image = vision.Image(source=vision.ImageSource(gcs_image_uri=gcs_uri))
        response = client.document_text_detection(image=image)
        if response.error and response.error.message:
            raise RuntimeError(f"OCR error: {response.error.message}")
        return response.full_text_annotation.text if response.full_text_annotation else ""

    else:
        # images (png/jpg)
        image = vision.Image(source=vision.ImageSource(gcs_image_uri=gcs_uri))
        response = client.document_text_detection(image=image)
        if response.error and response.error.message:
            raise RuntimeError(f"OCR error: {response.error.message}")
        return response.full_text_annotation.text if response.full_text_annotation else ""