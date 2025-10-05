export default function LanguageSelector({ value, onChange }) {
  const options = [
    { code: "en", label: "English" },
    { code: "hi", label: "Hindi" },
    { code: "es", label: "Spanish" },
    { code: "ar", label: "Arabic" },
    { code: "bn", label: "Bengali" },
    { code: "zh", label: "Chinese" },
  ];

  return (
    <label className="inline">
      <span className="lbl">Audio language</span>
      <select
        className="select"
        value={value}
        onChange={(e) => onChange(e.target.value)}
      >
        {options.map((o) => (
          <option key={o.code} value={o.code}>
            {o.label}
          </option>
        ))}
      </select>
    </label>
  );
}