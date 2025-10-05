// // src/pages/Home.jsx
// import React, { useRef, useState } from "react";
// import {
//   analyzePdf,
//   summarizeText,
//   translateText,
//   makeTTS,
//   uploadFile,
// } from "../services/api";

import RecommendationsPanel from "../components/RecommendationsPanel";
import ChatPopup from "../components/ChatPopup";



// const LANGS = [
//   "English",
//   "Hindi",
//   "Spanish",
//   "French",
//   "German",
//   "Bengali",
//   "Tamil",
//   "Telugu",
//   "Gujarati",
//   "Marathi",
// ];

// export default function Home() {
//   const [file, setFile] = useState(null);
//   const [selectedName, setSelectedName] = useState("");
//   const [lang, setLang] = useState("English");
//   const [text, setText] = useState("");

//   const [busy, setBusy] = useState(false);
//   const [err, setErr] = useState("");
//   const [summary, setSummary] = useState("");
//   const [keyPoints, setKeyPoints] = useState([]);
//   const [audioUrl, setAudioUrl] = useState("");

//   const audioRef = useRef(null);

//   const onChooseFile = (e) => {
//     const f = e.target.files?.[0];
//     setFile(f || null);
//     setSelectedName(f ? f.name : "");
//   };

//   const reset = () => {
//     setFile(null);
//     setSelectedName("");
//     setText("");
//     setSummary("");
//     setKeyPoints([]);
//     setAudioUrl("");
//     setErr("");
//   };

//   async function runFlow() {
//     setBusy(true);
//     setErr("");
//     setSummary("");
//     setKeyPoints([]);
//     setAudioUrl("");

//     try {
//       let baseText = text.trim();

//       // 1) If PDF was chosen, analyze it
//       if (file) {
//         // Optional: store in Firebase for history (not required for analysis)
//         try { await uploadFile(file); } catch { /* don't block flow */ }

//         const res = await analyzePdf(file);
//         if (!res.ok) throw new Error(res.error || "Analyze PDF failed");
//         setSummary(res.summary);
//         setKeyPoints(res.key_points || []);
//         baseText = res.summary;
//       } else {
//         // If no PDF, require pasted text
//         if (!baseText) {
//           setErr("Please paste the report text for now. (OCR endpoint not enabled yet.)");
//           return;
//         }
//         const sres = await summarizeText(baseText);
//         if (!sres.ok) throw new Error(sres.error || "Summarization failed");
//         setSummary(sres.summary);
//         setKeyPoints(sres.key_points || []);
//         baseText = sres.summary;
//       }

//       // 2) If language is not English, translate the summary before TTS
//       let speakText = baseText;
//       if (lang !== "English") {
//         const tres = await translateText(baseText, lang);
//         if (!tres.ok) throw new Error(tres.error || "Translation failed");
//         speakText = tres.translation;
//       }

//       // 3) TTS
//       const tt = await makeTTS(speakText);
//       if (!tt.ok) throw new Error(tt.error || "TTS failed");
//       setAudioUrl(tt.audio_url);

//       // autoplay if possible
//       setTimeout(() => {
//         if (audioRef.current) audioRef.current.play().catch(() => {});
//       }, 200);
//     } catch (e) {
//       setErr(e?.message || String(e));
//     } finally {
//       setBusy(false);
//     }
//   }

//   return (
//     <div className="container">
//       <h1>ClariMed</h1>
//       <div className="subtitle">
//         Understand your medical reports with clarity and care.
//       </div>

//       <div className="card" style={{ marginBottom: 16 }}>
//         <div className="row" style={{ marginBottom: 10 }}>
//           <label>Upload report (PDF/Image)</label>
//           <input type="file" accept=".pdf,image/*" onChange={onChooseFile} />
//           {selectedName && <span>Selected: {selectedName}</span>}
//         </div>

//         <div className="row" style={{ alignItems: "flex-start" }}>
//           <div>
//             <label>Report text (paste here until OCR is enabled)</label>
//             <br />
//             <textarea
//               placeholder="Paste the report text here…"
//               value={text}
//               onChange={(e) => setText(e.target.value)}
//             />
//           </div>

//           <div>
//             <label>Audio language</label>
//             <br />
//             <select value={lang} onChange={(e) => setLang(e.target.value)}>
//               {LANGS.map((l) => (
//                 <option key={l} value={l}>{l}</option>
//               ))}
//             </select>
//             <div style={{ marginTop: 12, display: "flex", gap: 10 }}>
//               <button className="primary" disabled={busy} onClick={runFlow}>
//                 {busy ? "Working…" : "Analyze & Summarize"}
//               </button>
//               <button className="secondary" onClick={reset} disabled={busy}>Reset</button>
//             </div>
//           </div>
//         </div>

//         {err && (
//           <div className="error" style={{ marginTop: 16 }}>
//             {err}
//           </div>
//         )}
//       </div>

//       {summary && (
//         <>
//           <div className="section-title">Summary</div>
//           <div className="card summary">{summary}</div>

//           {keyPoints?.length > 0 && (
//             <>
//               <div className="section-title">Key Points</div>
//               <div className="card">
//                 <ul className="kps">
//                   {keyPoints.map((k, i) => <li key={i}>{k}</li>)}
//                 </ul>
//               </div>
//             </>
//           )}

//           <div className="section-title">Listen</div>
//           <div className="card">
//             {audioUrl ? (
//               <audio ref={audioRef} controls src={audioUrl} />
//             ) : (
//               <span style={{ color: "var(--muted)" }}>TTS will appear here after summarization.</span>
//             )}
//           </div>
//         </>
//       )}
//     </div>
//   );
// }

import React, { useRef, useState, useEffect } from "react";
import {
  analyzePdf,
  summarizeText,
  translateText,
  makeTTS,
  uploadFile,
} from "../services/api";
import { auth, logout } from "../firebase";
import AudioPlayer from "../components/AudioPlayer";


const LANGS = [
  "English",
  "Hindi",
  "Spanish",
  "French",
  "German",
  "Bengali",
  "Tamil",
  "Telugu",
  "Gujarati",
  "Marathi",
];

export default function Home({ user, onLogout }) {
  const [file, setFile] = useState(null);
  const [selectedName, setSelectedName] = useState("");
  const [lang, setLang] = useState("English");
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  const [summary, setSummary] = useState("");
  const [keyPoints, setKeyPoints] = useState([]);
  const [audioUrl, setAudioUrl] = useState("");

  const onChooseFile = (e) => {
    const f = e.target.files?.[0];
    setFile(f || null);
    setSelectedName(f ? f.name : "");
  };

  const reset = () => {
    setFile(null);
    setSelectedName("");
    setText("");
    setSummary("");
    setKeyPoints([]);
    setAudioUrl("");
    setErr("");
  };

  // 🔒 Test secure API call on load
  useEffect(() => {
    const checkSecureAPI = async () => {
      const token = await auth.currentUser.getIdToken();
      const res = await fetch("http://127.0.0.1:5000/secure-endpoint", {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      console.log("Secure API Response:", data);
    };
    checkSecureAPI();
  }, []);

  async function runFlow() {
    setBusy(true);
    setErr("");
    setSummary("");
    setKeyPoints([]);
    setAudioUrl("");

    try {
      const token = await auth.currentUser.getIdToken();

      let baseText = text.trim();

      // 1️⃣ Analyze PDF if provided
      if (file) {
        try {
          await uploadFile(file);
        } catch {
          /* optional: skip upload errors */
        }

        const res = await analyzePdf(file, token);
        if (!res.ok) throw new Error(res.error || "Analyze PDF failed");
        setSummary(res.summary);
        setKeyPoints(res.key_points || []);
        baseText = res.summary;
      } else {
        if (!baseText) {
          setErr("Please paste the report text for now. (OCR not enabled yet.)");
          return;
        }
        const sres = await summarizeText(baseText, token);
        if (!sres.ok) throw new Error(sres.error || "Summarization failed");
        setSummary(sres.summary);
        setKeyPoints(sres.key_points || []);
        baseText = sres.summary;
      }

      // 2️⃣ Translate (if needed)
      let speakText = baseText;
      if (lang !== "English") {
        const tres = await translateText(baseText, lang, token);
        if (!tres.ok) throw new Error(tres.error || "Translation failed");
        speakText = tres.translation;
      }

      // 3️⃣ TTS
      const tt = await makeTTS(speakText, token);
      if (!tt.ok) throw new Error(tt.error || "TTS failed");
      setAudioUrl(tt.audio_url);

      
    } catch (e) {
      setErr(e?.message || String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="container">
      {/* Header */}
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 20,
        }}
      >
        <h1>ClariMed</h1>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span style={{ color: "#C7D0E0" }}>
            👤 {user?.displayName || user?.email}
          </span>
          <button
            onClick={onLogout || logout}
            style={{
              background: "rgba(0,123,255,0.15)",
              border: "1px solid rgba(0,123,255,0.5)",
              color: "white",
              borderRadius: "8px",
              padding: "6px 12px",
              cursor: "pointer",
            }}
          >
            Logout
          </button>
        </div>
      </div>

      <div className="subtitle">
        Understand your medical reports with clarity and care.
      </div>

      {/* Upload + Analyze Section */}
      <div className="card" style={{ marginBottom: 16 }}>
        <div className="row" style={{ marginBottom: 10 }}>
          <label>Upload report (PDF/Image)</label>
          <input type="file" accept=".pdf,image/*" onChange={onChooseFile} />
          {selectedName && <span>Selected: {selectedName}</span>}
        </div>

        <div className="row" style={{ alignItems: "flex-start" }}>
          <div>
            <label>Report text (paste here until OCR is enabled)</label>
            <br />
            <textarea
              placeholder="Paste the report text here…"
              value={text}
              onChange={(e) => setText(e.target.value)}
            />
          </div>

          <div>
            <label>Audio language</label>
            <br />
            <select value={lang} onChange={(e) => setLang(e.target.value)}>
              {LANGS.map((l) => (
                <option key={l} value={l}>
                  {l}
                </option>
              ))}
            </select>
            <div style={{ marginTop: 12, display: "flex", gap: 10 }}>
              <button className="primary" disabled={busy} onClick={runFlow}>
                {busy ? "Working…" : "Analyze & Summarize"}
              </button>
              <button className="secondary" onClick={reset} disabled={busy}>
                Reset
              </button>
            </div>
          </div>
        </div>

        {err && (
          <div className="error" style={{ marginTop: 16 }}>
            {err}
          </div>
        )}
      </div>

      {summary && (
        <>
          <div className="section-title">Summary</div>
          <div className="card summary">{summary} 
            <div>
             {audioUrl && <AudioPlayer src={audioUrl} autoPlay={false} />}
            </div>
          </div>

          {keyPoints?.length > 0 && (
            <>
              <div className="section-title">Key Points</div>
              <div className="card">
                <ul className="kps">
                  {keyPoints.map((k, i) => (
                    <li key={i}>{k}</li>
                  ))}
                </ul>
              </div>
              
            </>
          )}

            {/* ✅ Summary Action Buttons Row */}
{/* ✅ Action Buttons Row */}
<div
  style={{
    display: "flex",
    alignItems: "center",
    gap: "12px",
    marginTop: "16px",
  }}
>
  <RecommendationsPanel summary={summary} lang={lang} />

</div>




          {summary && <ChatPopup summary={summary} />}

        </>
      )}
    </div>
  );
}
