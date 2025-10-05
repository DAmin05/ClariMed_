import { useState } from "react";
import TextInput from "../components/TextInput";
import LanguageSelector from "../components/LanguageSelector";
import { translateText } from "../services/api";

export default function TranslatePage() {
  const [text, setText] = useState("");
  const [lang, setLang] = useState("hi");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const go = async () => {
    if (!text.trim()) return;
    setLoading(true);
    try {
      const data = await translateText(text, lang);
      setResult(data);
    } catch (e) {
      setResult({ ok:false, error: e?.response?.data?.error || e.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container grid">
      <h2>Translate</h2>
      <div className="card grid">
        <TextInput label="Original text" value={text} setValue={setText}/>
        <LanguageSelector value={lang} onChange={setLang} />
        <button onClick={go} disabled={!text.trim() || loading}>
          {loading ? "Translating..." : "Translate"}
        </button>
      </div>
      {result && (
        <div className="card">
          <pre style={{whiteSpace:"pre-wrap"}}>{JSON.stringify(result, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}