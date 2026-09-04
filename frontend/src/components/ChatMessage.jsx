import { useState } from "react";
import LoadingSpinner from "./LoadingSpinner.jsx";
import "./ChatMessage.css";

function formatTimestamp(seconds) {
  if (typeof seconds !== "number" || Number.isNaN(seconds)) return null;
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60)
    .toString()
    .padStart(2, "0");
  return `${mins}:${secs}`;
}


export default function ChatMessage({ exchange }) {
  const [sourcesOpen, setSourcesOpen] = useState(false);
  const { question, answer, sources, isLoading, error } = exchange;

  return (
    <div className="chat-exchange">
      <div className="chat-bubble chat-bubble-user">
        <p>{question}</p>
      </div>

      <div className="chat-bubble chat-bubble-ai">
        {isLoading && <LoadingSpinner label="Thinking..." size="small" />}

        {!isLoading && error && <p className="chat-bubble-error">{error}</p>}

        {!isLoading && !error && (
          <>
            <p>{answer}</p>

            {sources && sources.length > 0 && (
              <div className="chat-sources">
                <button
                  type="button"
                  className="chat-sources-toggle"
                  onClick={() => setSourcesOpen((open) => !open)}
                >
                  {sourcesOpen ? "Hide sources" : `Show sources (${sources.length})`}
                </button>

                {sourcesOpen && (
                  <ul className="chat-sources-list">
                    {sources.map((source, index) => {
                      const timestamp = formatTimestamp(source.start_time);
                      return (
                        <li key={index} className="chat-source-item">
                          {timestamp && (
                            <span className="chat-source-timestamp">{timestamp}</span>
                          )}
                          <span className="chat-source-text">{source.text}</span>
                        </li>
                      );
                    })}
                  </ul>
                )}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
