import { useState } from "react";
import TextInput from "../components/TextInput";
import { processText } from "../services/api";

export default function TextProcessingPage() {
  const [input, setInput] = useState("");
  const [out, setOut] = useState(null);
  const [loading, setLoading] = useState(false);

  const run = async () => {
    if (!input.trim()) return;
    setLoading(true);
    try {
      const data = await processText(input);
      setOut(data);
    } catch (e) {
      setOut({ ok:false, error: e?.response?.data?.error || e.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container grid">
      <h2>Summarize / Explain</h2>
      <div className="card grid">
        <TextInput label="Input text" value={input} setValue={setInput} />
        <div className="row">
          <button onClick={run} disabled={!input.trim() || loading}>
            {loading ? "Processing..." : "Run"}
          </button>
          <button className="ghost" onClick={()=>{setInput(""); setOut(null);}}>Clear</button>
        </div>
      </div>
      {out && (
        <div className="card">
          <pre style={{whiteSpace:"pre-wrap"}}>{JSON.stringify(out, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}