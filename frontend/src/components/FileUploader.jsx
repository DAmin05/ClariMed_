import { useState } from "react";

export default function FileUploader({ onFile }) {
  const [fileName, setFileName] = useState("");

  const handle = (e) => {
    const f = e.target.files?.[0];
    if (f) {
      setFileName(f.name);
      onFile?.(f);
    }
  };

  return (
    <div className="grid">
      <label>Upload document / image (PDF, PNG, JPG)</label>
      <input type="file" accept=".pdf,.png,.jpg,.jpeg" onChange={handle}/>
      {fileName && <span className="badge">Selected: {fileName}</span>}
    </div>
  );
}