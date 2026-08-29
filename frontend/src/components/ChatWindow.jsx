import { useEffect, useRef, useState } from "react";
import ChatMessage from "./ChatMessage";
import LoadingIndicator from "./LoadingIndicator";

/**
 * Scrollable message history + fixed input bar. Auto-scrolls to the newest
 * message (including while the "thinking" indicator is showing).
 */
export default function ChatWindow({ messages, isAskingQuestion, onSendQuestion, error }) {
  const [draft, setDraft] = useState("");
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, isAskingQuestion]);

  function handleSubmit(event) {
    event.preventDefault();
    const trimmed = draft.trim();
    if (!trimmed || isAskingQuestion) return;
    onSendQuestion(trimmed);
    setDraft("");
  }

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="scroll-thin flex-1 space-y-3 overflow-y-auto px-4 py-6 sm:px-8">
        {messages.length === 0 && (
          <p className="mx-auto max-w-sm pt-12 text-center text-sm text-mist-400">
            Video's loaded. Ask anything about it — a summary, a specific claim, a timestamp-worthy detail.
          </p>
        )}

        {messages.map((message, index) => (
          <ChatMessage key={index} role={message.role} content={message.content} />
        ))}

        {isAskingQuestion && (
          <div className="flex w-full justify-start">
            <div className="rounded-r-2xl rounded-l-sm border-l-2 border-cue bg-ink-800 px-4 py-3">
              <LoadingIndicator variant="dots" />
            </div>
          </div>
        )}

        {error && (
          <div className="flex w-full justify-start">
            <div className="max-w-[85%] rounded-r-2xl rounded-l-sm border-l-2 border-danger bg-danger-dim/40 px-4 py-2.5 text-sm text-red-200 sm:max-w-[70%]">
              {error}
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      <form
        onSubmit={handleSubmit}
        className="flex items-center gap-3 border-t border-ink-700 bg-ink-900 px-4 py-3 sm:px-8"
      >
        <input
          type="text"
          value={draft}
          onChange={(event) => setDraft(event.target.value)}
          disabled={isAskingQuestion}
          placeholder={isAskingQuestion ? "Waiting on an answer…" : "Ask about the video…"}
          aria-label="Your question"
          className="flex-1 rounded-lg border border-ink-700 bg-ink-800 px-4 py-2.5 text-sm text-mist-100 placeholder:text-mist-400 focus-visible:outline-none disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={isAskingQuestion || draft.trim().length === 0}
          className="shrink-0 rounded-lg bg-signal px-4 py-2.5 text-sm font-medium text-ink-950 transition-colors hover:bg-signal/90 disabled:cursor-not-allowed disabled:bg-ink-700 disabled:text-mist-400"
        >
          Send
        </button>
      </form>
    </div>
  );
}
