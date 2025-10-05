// src/services/api.js
import axios from "axios";

// 🧠 Prevent Google/Firebase auth tokens from breaking external API routes
axios.interceptors.request.use((config) => {
  const sensitivePaths = ["/tts", "/recommendations", "/translate"];
  const shouldSkipAuth = sensitivePaths.some((p) => config.url.includes(p));

  if (shouldSkipAuth) {
    // remove any Authorization header that Firebase might add
    delete config.headers.Authorization;
  }

  return config;
});

export const API_BASE = "http://localhost:5001";


const cleanAxios = axios.create({
  baseURL: API_BASE,
  headers: { "Content-Type": "application/json" },
});

// ---------- uploads & files ----------
export async function uploadFile(file) {
  const fd = new FormData();
  fd.append("file", file);
  const { data } = await cleanAxios.post(`${API_BASE}/upload`, fd, {
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
  const { data } = await cleanAxios.post(`${API_BASE}/translate`, {
    text,
    target_language,
  });
  return data; // { ok, translation }
}

// ---------- tts ----------
export async function makeTTS(text, voice_id) {
  const { data } = await cleanAxios.post(`${API_BASE}/tts`, {
    text
  });
  return data; // { ok, audio_url, path }
}

// ---------- recommendations ----------
export async function getRecommendations(summary) {
  const { data } = await cleanAxios.post(`${API_BASE}/recommendations`, { summary });
  return data;
}


// ---------- doctor chat ----------
export async function chatWithDoctor(summary, history, question) {
  const { data } = await axios.post(`${API_BASE}/chat`, {
    summary,
    history,
    question,
  });
  return data; // { ok, answer }
}

