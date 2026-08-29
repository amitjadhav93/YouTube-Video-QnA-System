/**
 * Non-blocking, dismissible error banner. Used for video-processing errors
 * below the URL form; question-asking errors are rendered inline in the
 * chat instead (see ChatWindow), so this stays generic and reusable.
 */
export default function ErrorBanner({ message, onDismiss }) {
  if (!message) return null;

  return (
    <div
      role="alert"
      className="flex items-start justify-between gap-3 rounded-lg border border-danger/30 bg-danger-dim/40 px-4 py-3"
    >
      <p className="text-sm leading-relaxed text-red-200">{message}</p>
      {onDismiss && (
        <button
          type="button"
          onClick={onDismiss}
          aria-label="Dismiss error"
          className="shrink-0 rounded text-red-300/70 hover:text-red-100 focus-visible:outline-none"
        >
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path
              d="M12 4L4 12M4 4l8 8"
              stroke="currentColor"
              strokeWidth="1.5"
              strokeLinecap="round"
            />
          </svg>
        </button>
      )}
    </div>
  );
}
