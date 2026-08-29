import ChatWindow from "./components/ChatWindow";
import ErrorBanner from "./components/ErrorBanner";
import VideoUrlForm from "./components/VideoUrlForm";
import { useChatSession } from "./hooks/useChatSession";

export default function App() {
  const {
    videoId,
    messages,
    isProcessingVideo,
    isAskingQuestion,
    isVideoLoaded,
    error,
    loadVideo,
    sendQuestion,
    reset,
    clearError,
  } = useChatSession();

  // `error` covers both video-processing and question-asking failures.
  // Route it to the top-level banner before a video is loaded, and inline
  // in the chat once one is (see ChatWindow's `error` prop below).
  const bannerError = !isVideoLoaded ? error : null;

  return (
    <div className="flex h-screen flex-col bg-ink-950">
      <header className="flex items-center justify-between border-b border-ink-700 bg-ink-900 px-4 py-3 sm:px-8">
        <div className="flex items-center gap-2.5">
          <span className="flex h-7 w-7 items-center justify-center rounded-md bg-cue/15 font-mono text-xs font-semibold text-cue">
            ▸
          </span>
          <div>
            <h1 className="font-display text-sm font-semibold leading-none text-mist-100">Transcript</h1>
            <p className="mt-0.5 font-mono text-[11px] leading-none text-mist-400">
              {videoId ? `video · ${videoId}` : "video Q&A, grounded"}
            </p>
          </div>
        </div>

        {isVideoLoaded && (
          <button
            type="button"
            onClick={reset}
            className="rounded-lg border border-ink-700 px-3 py-1.5 text-xs font-medium text-mist-300 transition-colors hover:border-ink-600 hover:text-mist-100"
          >
            New Video
          </button>
        )}
      </header>

      {bannerError && (
        <div className="px-4 pt-4 sm:px-8">
          <ErrorBanner message={bannerError} onDismiss={clearError} />
        </div>
      )}

      {isVideoLoaded ? (
        <ChatWindow
          messages={messages}
          isAskingQuestion={isAskingQuestion}
          onSendQuestion={sendQuestion}
          error={isVideoLoaded ? error : null}
        />
      ) : (
        <div className="flex flex-1 items-center overflow-y-auto">
          <VideoUrlForm onSubmit={loadVideo} isProcessingVideo={isProcessingVideo} />
        </div>
      )}
    </div>
  );
}
