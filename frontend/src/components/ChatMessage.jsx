/**
 * A single chat bubble. User messages align right in the signal-blue
 * accent; assistant messages align left as quiet transcript-style panels
 * with a left rule, echoing the "captions" motif from the loading state.
 */
export default function ChatMessage({ role, content }) {
  const isUser = role === "user";

  return (
    <div className={`flex w-full ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={
          isUser
            ? "max-w-[85%] rounded-2xl rounded-br-sm bg-signal px-4 py-2.5 text-sm leading-relaxed text-ink-950 sm:max-w-[70%]"
            : "max-w-[85%] rounded-r-2xl rounded-l-sm border-l-2 border-cue bg-ink-800 px-4 py-2.5 text-sm leading-relaxed text-mist-100 sm:max-w-[70%]"
        }
      >
        <p className="whitespace-pre-wrap break-words">{content}</p>
      </div>
    </div>
  );
}
