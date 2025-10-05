// src/services/api.js
import axios from "axios";

export const API_BASE = "http://localhost:5001";

// ---------- uploads & files ----------
export async function uploadFile(file) {
  const fd = new FormData();
  fd.append("file", file);
  const { data } = await axios.post(`${API_BASE}/upload`, fd, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data; // { ok, path, url }
}

export async function analyzePdf(file) {
  const fd = new FormData();
  fd.append("file", file);
  const { data } = await axios.post(`${API_BASE}/analyze-pdf`, fd, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data; // { ok, summary, key_points, extracted_text }
}

export async function getFileUrl(path) {
  const { data } = await axios.get(`${API_BASE}/file-url`, { params: { path } });
  return data; // { ok, url }
}

// ---------- nlp ----------
export async function summarizeText(text) {
  const { data } = await axios.post(`${API_BASE}/process-text`, { text });
  return data; // { ok, summary, key_points }
}

export async function translateText(text, target_language) {
  const { data } = await axios.post(`${API_BASE}/translate`, {
    text,
    target_language,
  });
  return data; // { ok, translation }
}

// ---------- tts ----------
export async function makeTTS(text, voice_id) {
  const { data } = await axios.post(`${API_BASE}/tts`, {
    text,
    voice_id,
  });
  return data; // { ok, audio_url, path }
}