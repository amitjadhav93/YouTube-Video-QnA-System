import { useEffect, useRef, useState } from "react";
import ChatMessage from "./ChatMessage.jsx";
import "./ChatWindow.css";


export default function ChatWindow({ exchanges, onAsk, isAsking }) {
  const [question, setQuestion] = useState("");
  const messagesEndRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [exchanges]);

  function handleSubmit(event) {
    event.preventDefault();
    const trimmed = question.trim();
    if (!trimmed || isAsking) return;
    onAsk(trimmed);
    setQuestion("");
  }

  return (
    <div className="chat-window">
      <div className="chat-messages">
        {exchanges.length === 0 && (
          <p className="chat-empty-state">
            Ask anything about this video — try "What's the main topic?" to get started.
          </p>
        )}

        {exchanges.map((exchange, index) => (
          <ChatMessage key={index} exchange={exchange} />
        ))}

        <div ref={messagesEndRef} />
      </div>

      <form className="chat-input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          className="chat-input-field"
          placeholder="Ask a question about this video..."
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
          disabled={isAsking}
          aria-label="Ask a question about this video"
        />
        <button
          type="submit"
          className="chat-input-button"
          disabled={isAsking || !question.trim()}
        >
          {isAsking ? "Asking..." : "Ask"}
        </button>
      </form>
    </div>
  );
}
