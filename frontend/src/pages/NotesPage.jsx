import { useState } from "react";
import { saveNote } from "../services/api";
import TextInput from "../components/TextInput";

export default function NotesPage() {
  const [text, setText] = useState("");
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const save = async () => {
    if (!text.trim()) return;
    setLoading(true);
    try {
      const data = await saveNote(text);
      setStatus(data);
      setText("");
    } catch (e) {
      setStatus({ ok:false, error: e?.response?.data?.error || e.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container grid">
      <h2>Notes</h2>
      <div className="card grid">
        <TextInput label="Note" value={text} setValue={setText} rows={5}/>
        <button onClick={save} disabled={!text.trim() || loading}>
          {loading ? "Saving..." : "Save to Firestore"}
        </button>
      </div>
      {status && (
        <div className="card">
          <pre>{JSON.stringify(status, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}