import { useState } from "react";
import TextInput from "../components/TextInput";
import AudioPlayer from "../components/AudioPlayer";
import { tts } from "../services/api";

export default function TextToSpeechPage() {
  const [text, setText] = useState("");
  const [audio, setAudio] = useState(null);
  const [loading, setLoading] = useState(false);
  const [voice, setVoice] = useState("EXAVITQu4vr4xnSDxMaL");
  const [model, setModel] = useState("eleven_multilingual_v2");

  const speak = async () => {
    if (!text.trim()) return;
    setLoading(true);
    try {
      const blob = await tts(text, voice, model);
      setAudio(blob);
    } catch (e) {
      alert(e?.response?.data?.error || e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container grid">
      <h2>Text-to-Speech</h2>
      <div className="card grid">
        <TextInput label="Text" value={text} setValue={setText}/>
        <div className="grid grid-2">
          <div className="grid">
            <label>Voice ID</label>
            <input value={voice} onChange={(e)=>setVoice(e.target.value)} />
          </div>
          <div className="grid">
            <label>Model</label>
            <input value={model} onChange={(e)=>setModel(e.target.value)} />
          </div>
        </div>
        <button onClick={speak} disabled={!text.trim() || loading}>
          {loading ? "Generating..." : "Generate Audio"}
        </button>
        <AudioPlayer blob={audio}/>
      </div>
    </div>
  );
}