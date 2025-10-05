import React from "react";

export default function AudioPlayer({ src, blob, autoPlay = false }) {
  if (!src && !blob) return null;

  const audioSrc = blob ? URL.createObjectURL(blob) : src;

  return (
    <div style={{ marginTop: 10 }}>
      <audio
        controls
        preload="auto"
        src={audioSrc}
        style={{
          width: "100%",
          borderRadius: "8px",
          outline: "none",
        }}
        autoPlay={autoPlay}
      />
    </div>
  );
}
