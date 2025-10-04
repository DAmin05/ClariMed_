# backend/services/ocr.py
"""
OCR utilities using Google Cloud Vision.
Requires:
- GOOGLE_APPLICATION_CREDENTIALS (service account JSON)
"""

from google.cloud import vision


def run_ocr_gcs(gcs_uri: str) -> str:
    """
    Runs Document Text Detection on a file stored in GCS (gs://...).
    Returns the full extracted text (may be empty string if nothing found).
    """
    client = vision.ImageAnnotatorClient()
    image = vision.Image(source=vision.ImageSource(gcs_image_uri=gcs_uri))
    response = client.document_text_detection(image=image)

    if response.error and response.error.message:
        # Surface Vision error messages clearly
        raise RuntimeError(f"GCV error: {response.error.message}")

    if response.full_text_annotation and response.full_text_annotation.text:
        return response.full_text_annotation.text

    return ""