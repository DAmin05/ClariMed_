export default function AudioPlayer({ src }) {
  if (!src) return null;
  return (
    <audio controls preload="metadata" className="audio">
      <source src={src} type="audio/mpeg" />
      Your browser does not support the audio element.
    </audio>
  );
}