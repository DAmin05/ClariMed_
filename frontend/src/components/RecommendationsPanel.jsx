import React, { useState } from "react";
import { getRecommendations, makeTTS, translateText } from "../services/api";
import AudioPlayer from "./AudioPlayer";

export default function RecommendationsPanel({ summary, lang }) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [recs, setRecs] = useState([]);
  const [audioUrl, setAudioUrl] = useState("");

  const handleClick = async () => {
    if (!summary) return;
    if (!open && recs.length === 0) {
      setLoading(true);
      try {
        const res = await getRecommendations(summary);
        if (res.ok) setRecs(res.recommendations || []);
      } catch (err) {
        console.error(err);
        alert("Could not load recommendations.");
      } finally {
        setLoading(false);
      }
    }
    setOpen(!open);
  };

  const handlePlayAudio = async () => {
    if (recs.length === 0) return alert("No recommendations to read.");

    try {
      let textToSpeak = recs.join(". ");

      // 🌍 Use the same language as summary
      if (lang && lang !== "English") {
        const tRes = await translateText(textToSpeak, lang);
        if (tRes.ok && tRes.translation) textToSpeak = tRes.translation;
      }

      const res = await makeTTS(textToSpeak);
      if (res.ok) {
        setAudioUrl(res.audio_url);
      } else {
        alert("Could not generate audio.");
      }
    } catch (err) {
      console.error(err);
      alert("Audio generation failed.");
    }
  };

  return (
    <div style={{ marginTop: 20 }}>
      <button
        onClick={handleClick}
        disabled={loading}
        className="primary"
        style={{ marginBottom: 10 }}
      >
        {loading
          ? "Loading..."
          : open
          ? "Hide Recommendations"
          : "View Recommendations"}
      </button>

      {open && (
        <>
          <div className="section-title">Recommendations</div>
          <div className="card summary">
            {recs.length === 0 ? (
              <p style={{ color: "var(--muted)" }}>No recommendations yet.</p>
            ) : (
              <ul className="kps">
                {recs.map((r, i) => (
                  <li key={i}>{r}</li>
                ))}
              </ul>
            )}

            {/* 🎧 Audio for recommendations */}
            {audioUrl ? (
              <AudioPlayer src={audioUrl} autoPlay={false} />
            ) : (
              <button
                className="primary"
                onClick={handlePlayAudio}
                style={{ marginTop: 12 }}
              >
                ▶️ Play Recommendations
              </button>
            )}
          </div>
        </>
      )}
    </div>
  );
}
