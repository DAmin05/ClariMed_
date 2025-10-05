import { useState } from "react";
import LanguageSelector from "../components/LanguageSelector";
import AudioPlayer from "../components/AudioPlayer";
import { analyzeReport } from "../services/api";

export default function ReportAssist() {
  const [file, setFile] = useState(null);
  const [lang, setLang] = useState("en");
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState("");
  const [audioUrl, setAudioUrl] = useState("");
  const [error, setError] = useState("");

  const pick = (e) => {
    setFile(e.target.files?.[0] ?? null);
    setSummary("");
    setAudioUrl("");
    setError("");
  };

  const go = async () => {
    if (!file) {
      setError("Please choose a report (PDF or image).");
      return;
    }
    setLoading(true);
    setError("");
    try {
      const data = await analyzeReport(file, lang);
      if (!data.ok) {
        setError(data.error || "Something went wrong.");
      } else {
        setSummary(data.summary || "");
        setAudioUrl(data.audio_url || "");
      }
    } catch (e) {
      setError(e?.message || "Network error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      <section className="hero">
        <img src="/ClarimedLogo.png" className="logo" alt="ClariMed" />
        <h1>ClariMed</h1>
        <p className="tagline">Understand your medical reports with clarity and care.</p>
      </section>

      <section className="card">
        <div className="row">
          <label className="btn">
            <input type="file" accept=".pdf,image/*" hidden onChange={pick} />
            Choose report
          </label>
          {file && <div className="muted">Selected: {file.name}</div>}
        </div>

        <div className="row">
          <LanguageSelector value={lang} onChange={setLang} />
        </div>

        <div className="row">
          <button className="btn primary" onClick={go} disabled={loading}>
            {loading ? "Analyzing…" : "Analyze & Summarize"}
          </button>
        </div>
      </section>

      {error && (
        <section className="card error">
          <strong>Error</strong>
          <pre>{error}</pre>
        </section>
      )}

      {summary && (
        <section className="card">
          <h3>Patient-friendly summary</h3>
          <p style={{ whiteSpace: "pre-wrap" }}>{summary}</p>

          {audioUrl ? (
            <>
              <h4 className="mt">Listen ({lang.toUpperCase()})</h4>
              <AudioPlayer src={audioUrl} />
            </>
          ) : (
            <div className="muted">Audio may be unavailable for this language/voice.</div>
          )}
        </section>
      )}
    </div>
  );
}