export default function TextInput({ label="Text", value, setValue, placeholder, rows=8 }) {
  return (
    <div className="grid">
      <label>{label}</label>
      <textarea
        placeholder={placeholder || "Paste or type here..."}
        value={value}
        rows={rows}
        onChange={(e)=>setValue(e.target.value)}
      />
    </div>
  );
}