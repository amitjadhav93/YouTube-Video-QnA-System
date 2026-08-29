/**
 * Two visual variants, both driven by the same "scanning a transcript" idea:
 *
 * - "scan": a full-width track with a sliding highlight, used while the
 *   backend fetches the transcript + builds the FAISS index. Includes a
 *   text label since this step can take 10-30+ seconds and a bare spinner
 *   would leave the user guessing.
 *
 * - "dots": a compact three-dot "thinking" pulse, used inline in the chat
 *   while waiting for an answer.
 */
export default function LoadingIndicator({ variant = "scan", label }) {
  if (variant === "dots") {
    return (
      <div className="flex items-center gap-1.5 px-1" role="status" aria-label="Assistant is thinking">
        <span className="h-1.5 w-1.5 rounded-full bg-mist-300 animate-blink1" />
        <span className="h-1.5 w-1.5 rounded-full bg-mist-300 animate-blink2" />
        <span className="h-1.5 w-1.5 rounded-full bg-mist-300 animate-blink3" />
      </div>
    );
  }

  return (
    <div className="w-full" role="status" aria-live="polite">
      <div className="relative h-1 w-full overflow-hidden rounded-full bg-ink-700">
        <div className="absolute inset-y-0 left-0 w-1/4 rounded-full bg-cue animate-scan" />
      </div>
      {label && <p className="mt-2 font-mono text-xs text-mist-300">{label}</p>}
    </div>
  );
}
