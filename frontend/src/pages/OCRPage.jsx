import { useState } from "react";
import FileUploader from "../components/FileUploader";
import { uploadFile, getFileUrl } from "../services/api";

export default function OCRPage() {
  const [file, setFile] = useState(null);
  const [res, setRes] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleUpload = async () => {
    if (!file) return;
    setLoading(true);
    try {
      const up = await uploadFile(file); // { ok, path, url? }
      setRes(up);

      // optional: fetch a read URL if backend returns only path
      if (!up.url && up.path) {
        const link = await getFileUrl(up.path);
        setRes({ ...up, url: link?.url });
      }
    } catch (e) {
      setRes({ ok:false, error: e?.response?.data?.error || e.message });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container grid">
      <h2>OCR</h2>
      <div className="card grid">
        <FileUploader onFile={setFile} />
        <div className="row">
          <button onClick={handleUpload} disabled={!file || loading}>
            {loading ? "Uploading..." : "Upload & Extract"}
          </button>
          <button className="ghost" onClick={()=>{setFile(null); setRes(null);}}>Reset</button>
        </div>
      </div>

      {res && (
        <div className="card">
          <div className="badge">{res.ok ? "Success" : "Error"}</div>
          <pre style={{whiteSpace:"pre-wrap"}}>{JSON.stringify(res, null, 2)}</pre>
          {res.url && <a href={res.url} target="_blank">Open uploaded file</a>}
        </div>
      )}
    </div>
  );
}