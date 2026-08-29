import { useState } from "react";
import LoadingIndicator from "./LoadingIndicator";

/**
 * The entry screen: paste a YouTube URL, kick off processing.
 * Disabled + showing LoadingIndicator (scan variant) while isProcessingVideo.
 */
export default function VideoUrlForm({ onSubmit, isProcessingVideo }) {
  const [url, setUrl] = useState("");
  const [touched, setTouched] = useState(false);

  const isBlank = url.trim().length === 0;

  function handleSubmit(event) {
    event.preventDefault();
    setTouched(true);
    if (isBlank || isProcessingVideo) return;
    onSubmit(url);
  }

  return (
    <div className="mx-auto flex w-full max-w-xl flex-col gap-6 px-6 py-16">
      <div className="space-y-2 text-center">
        <p className="font-mono text-xs uppercase tracking-[0.2em] text-cue">00:00 → transcript</p>
        <h1 className="font-display text-3xl font-semibold text-mist-100">
          Ask questions about any YouTube video
        </h1>
        <p className="text-sm text-mist-300">
          Paste a link. We'll pull the transcript and ground every answer in what's actually said.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-3">
        <div className="flex flex-col gap-3 sm:flex-row">
          <input
            type="url"
            inputMode="url"
            placeholder="https://www.youtube.com/watch?v=..."
            value={url}
            onChange={(event) => setUrl(event.target.value)}
            onBlur={() => setTouched(true)}
            disabled={isProcessingVideo}
            aria-label="YouTube video URL"
            aria-invalid={touched && isBlank}
            className="flex-1 rounded-lg border border-ink-700 bg-ink-800 px-4 py-3 text-sm text-mist-100 placeholder:text-mist-400 focus-visible:outline-none disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isProcessingVideo || isBlank}
            className="shrink-0 rounded-lg bg-signal px-5 py-3 text-sm font-medium text-ink-950 transition-colors hover:bg-signal/90 disabled:cursor-not-allowed disabled:bg-ink-700 disabled:text-mist-400"
          >
            {isProcessingVideo ? "Processing…" : "Process Video"}
          </button>
        </div>
        {touched && isBlank && (
          <p className="text-xs text-danger">Paste a video URL before processing.</p>
        )}
      </form>

      {isProcessingVideo && (
        <LoadingIndicator variant="scan" label="Fetching transcript and building the index — this can take up to 30s…" />
      )}
    </div>
  );
}
