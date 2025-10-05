import React, { useState } from "react";
import { chatWithDoctor } from "../services/api";

export default function ChatPopup({ summary }) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([]); // [{from:'user'|'bot', text:''}]
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const sendMessage = async () => {
    const question = input.trim();
    if (!question) return;
    setInput("");
    const newMessages = [...messages, { from: "user", text: question }];
    setMessages(newMessages);
    setLoading(true);

    try {
      const history = newMessages.map((m) => ({
        role: m.from === "user" ? "user" : "assistant",
        text: m.text,
      }));

      const res = await chatWithDoctor(summary, history, question);
      if (res.ok) {
        const botMsg = { from: "bot", text: res.answer };
        setMessages((prev) => [...prev, botMsg]);
      } else {
        setMessages((prev) => [
          ...prev,
          { from: "bot", text: "Sorry, I couldn’t process your question right now." },
        ]);
      }
    } catch (err) {
      console.error(err);
      setMessages((prev) => [
        ...prev,
        { from: "bot", text: "An error occurred while connecting to the AI." },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      {/* Floating Chat Button */}
      <div
        style={{
          position: "fixed",
          bottom: 20,
          right: 20,
          zIndex: 1000,
        }}
      >
        {!open && (
          <button
            className="primary"
            onClick={() => setOpen(true)}
            style={{
              borderRadius: "50%",
              width: 60,
              height: 60,
              fontSize: 26,
              cursor: "pointer",
            }}
          >
            💬
          </button>
        )}
      </div>

      {/* Chat Window */}
      {open && (
        <div
          style={{
            position: "fixed",
            bottom: 90,
            right: 20,
            width: 340,
            height: 440,
            backgroundColor: "#fff",
            border: "1px solid #ccc",
            borderRadius: 12,
            boxShadow: "0 4px 16px rgba(0,0,0,0.2)",
            display: "flex",
            flexDirection: "column",
            zIndex: 2000,
          }}
        >
          <div
            style={{
              backgroundColor: "#007bff",
              color: "#fff",
              padding: "10px 12px",
              borderTopLeftRadius: 12,
              borderTopRightRadius: 12,
              display: "flex",
              justifyContent: "space-between",
              alignItems: "center",
            }}
          >
            <span>🩺 AI Doctor Chat</span>
            <button
              style={{
                background: "transparent",
                border: "none",
                color: "white",
                fontSize: 18,
                cursor: "pointer",
              }}
              onClick={() => setOpen(false)}
            >
              ✕
            </button>
          </div>

          <div
            style={{
              flex: 1,
              overflowY: "auto",
              padding: "10px",
              fontSize: 14,
              scrollBehavior: "smooth",
            }}
          >
            {messages.length === 0 && (
              <p style={{ color: "#555" }}>
                Ask me anything about your medical report — I can explain terms, next steps, or where to seek help.
              </p>
            )}
            {messages.map((msg, i) => (
              <div
                key={i}
                style={{
                  margin: "8px 0",
                  textAlign: msg.from === "user" ? "right" : "left",
                }}
              >
                <div
                  style={{
                    display: "inline-block",
                    backgroundColor:
                      msg.from === "user" ? "#d1e7ff" : "#f3f3f3",
                    padding: "8px 12px",
                    borderRadius: 10,
                    maxWidth: "85%",
                    whiteSpace: "pre-wrap",
                  }}
                >
                  {msg.text}
                </div>
              </div>
            ))}
            {loading && <p style={{ color: "#888" }}>Thinking...</p>}
          </div>

          <div
            style={{
              display: "flex",
              borderTop: "1px solid #ccc",
              padding: "8px",
              gap: "6px",
            }}
          >
            <input
              type="text"
              placeholder="Ask your medical question..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              style={{
                flex: 1,
                border: "1px solid #ccc",
                borderRadius: 8,
                padding: "6px 8px",
              }}
            />
            <button
              className="primary"
              onClick={sendMessage}
              disabled={loading}
              style={{ borderRadius: 8 }}
            >
              ➤
            </button>
          </div>
        </div>
      )}
    </>
  );
}
