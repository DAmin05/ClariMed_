import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home";
import OCRPage from "./pages/OCRPage";
import TextProcessingPage from "./pages/TextProcessingPage";
import TranslatePage from "./pages/TranslatePage";
import TextToSpeechPage from "./pages/TextToSpeechPage";
import NotesPage from "./pages/NotesPage";

export default function RouterView() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/ocr" element={<OCRPage />} />
      <Route path="/process" element={<TextProcessingPage />} />
      <Route path="/translate" element={<TranslatePage />} />
      <Route path="/tts" element={<TextToSpeechPage />} />
      <Route path="/notes" element={<NotesPage />} />
    </Routes>
  );
}