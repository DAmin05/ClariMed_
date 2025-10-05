import React, { useState, useRef, useEffect } from "react";
import { makeTTS } from "../services/api";
import { API_BASE } from "../services/api";

export default function ChatPopup({ summary }) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      text: "👋 Hi, I’m ClariMed Assistant. You can ask me any medical question related to your report!",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, open]);

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg = { role: "user", text: input.trim() };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setLoading(true);

    try {
      // 🧠 Determine if question is medical
      const isMedicalPrompt = `
        Determine if the user's message is about a medical topic such as reports, symptoms, conditions, treatments, or healthcare.
        If yes, respond with "yes". If it's unrelated (like general, math, or random), respond with "no".
        Message: "${userMsg.text}"
      `;

      const checkRes = await fetch(`${API_BASE}/process-text`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: isMedicalPrompt }),
      });

      const checkData = await checkRes.json();
      const decision = checkData.summary?.toLowerCase() || "";

      if (decision.includes("no")) {
        setMessages((m) => [
          ...m,
          {
            role: "assistant",
            text: "🙏 I’m a medical assistant and can only answer health-related questions. Sorry for the inconvenience!",
          },
        ]);
        setLoading(false);
        return;
      }

      // 🧠 Context prompt for Gemini
      const fullContext = `
You are ClariMed AI — a friendly, factual medical assistant.
Your task is to help the user understand their report summary and related medical concerns.
Use clear, 6th–8th grade-level explanations. Do not give prescriptions.
Be empathetic and brief (4–6 sentences max).

Report Summary:
${summary}

Conversation so far:
${messages
  .map((m) => `${m.role === "user" ? "User" : "Assistant"}: ${m.text}`)
  .join("\n")}

User’s new question:
${userMsg.text}
`;

      const res = await fetch(`${API_BASE}/process-text`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: fullContext }),
      });

      const data = await res.json();
      const aiText =
        data.summary ||
        "I'm sorry, I couldn’t understand that. Please rephrase your question.";

      setMessages((m) => [...m, { role: "assistant", text: aiText }]);
    } catch (err) {
      console.error(err);
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          text: "⚠️ There was an issue connecting to the assistant. Please try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Floating Chat Toggle Button */}
      <button
        onClick={() => setOpen(!open)}
        className="primary"
        style={{
          position: "fixed",
          bottom: "24px",
          right: "24px",
          borderRadius: "50px",
          padding: "12px 16px",
          fontWeight: "bold",
          zIndex: 999,
        }}
      >
        {open ? "Close Chat" : "💬 Ask AI"}
      </button>

      {open && (
        <div
          className="card summary"
          style={{
            position: "fixed",
            bottom: "90px",
            right: "24px",
            width: "340px",
            maxHeight: "450px",
            overflowY: "auto",
            padding: "16px",
            boxShadow: "0 4px 12px rgba(0,0,0,0.25)",
            zIndex: 1000,
          }}
        >
          <div
            style={{
              fontWeight: "bold",
              marginBottom: "10px",
              fontSize: "1.05rem",
              color: "var(--text)",
            }}
          >
            🩺 ClariMed Assistant
          </div>

          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: "8px",
              marginBottom: "10px",
            }}
          >
            {messages.map((msg, i) => (
              <div
                key={i}
                style={{
                  alignSelf:
                    msg.role === "user" ? "flex-end" : "flex-start",
                  backgroundColor:
                    msg.role === "user"
                      ? "rgba(0,123,255,0.1)"
                      : "rgba(255,255,255,0.08)",
                  color: "var(--text)",
                  borderRadius:
                    msg.role === "user"
                      ? "12px 12px 0 12px"
                      : "12px 12px 12px 0",
                  padding: "8px 10px",
                  maxWidth: "85%",
                  wordWrap: "break-word",
                  whiteSpace: "pre-wrap",
                }}
              >
                {msg.text}
              </div>
            ))}
            <div ref={chatEndRef} />
          </div>

          <div style={{ display: "flex", gap: "6px", marginTop: "8px" }}>
            <input
              type="text"
              placeholder="Ask about your report..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
              style={{
                flex: 1,
                borderRadius: "8px",
                padding: "8px",
                border: "1px solid rgba(255,255,255,0.2)",
                background: "rgba(0,0,0,0.1)",
                color: "white",
              }}
            />
            <button
              onClick={handleSend}
              disabled={loading}
              className="primary"
              style={{ borderRadius: "8px", padding: "8px 12px" }}
            >
              {loading ? "..." : "Send"}
            </button>
          </div>
        </div>
      )}
    </>
  );
}
