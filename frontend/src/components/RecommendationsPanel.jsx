import React, { useState } from "react";
import { getRecommendations } from "../services/api";

export default function RecommendationsPanel({ summary }) {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [recs, setRecs] = useState([]);

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

  return (
    <div style={{ marginTop: 20 }}>
      <button
        onClick={handleClick}
        disabled={loading}
        className="primary"
        style={{ marginBottom: 10 }}
      >
        {loading ? "Loading..." : open ? "Hide Recommendations" : "View Recommendations"}
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
          </div>
        </>
      )}
    </div>
  );
}
