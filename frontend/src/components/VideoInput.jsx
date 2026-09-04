import { useState } from "react";
import LoadingSpinner from "./LoadingSpinner.jsx";
import "./VideoInput.css";

const YOUTUBE_URL_PATTERN =
  /^(https?:\/\/)?(www\.)?(youtube\.com\/(watch\?v=|shorts\/|live\/)|youtu\.be\/)[\w-]+/i;

function isLikelyYoutubeUrl(url) {
  return YOUTUBE_URL_PATTERN.test(url.trim());
}


export default function VideoInput({ onSubmit, isProcessing }) {
  const [url, setUrl] = useState("");
  const [validationError, setValidationError] = useState("");

  function handleSubmit(event) {
    event.preventDefault();

    const trimmedUrl = url.trim();

    if (!trimmedUrl) {
      setValidationError("Please paste a YouTube video URL.");
      return;
    }

    if (!isLikelyYoutubeUrl(trimmedUrl)) {
      setValidationError(
        "That doesn't look like a YouTube URL. Try something like https://www.youtube.com/watch?v=..."
      );
      return;
    }

    setValidationError("");
    onSubmit(trimmedUrl);
  }

  return (
    <div className="video-input-card">
      <h1 className="video-input-title">YouTube Video Q&amp;A</h1>
      <p className="video-input-subtitle">
        Paste a YouTube link, and ask questions about the video once it's processed.
      </p>

      <form className="video-input-form" onSubmit={handleSubmit}>
        <input
          type="text"
          className="video-input-field"
          placeholder="https://www.youtube.com/watch?v=..."
          value={url}
          onChange={(event) => {
            setUrl(event.target.value);
            if (validationError) setValidationError("");
          }}
          disabled={isProcessing}
          aria-label="YouTube video URL"
        />
        <button
          type="submit"
          className="video-input-button"
          disabled={isProcessing}
        >
          {isProcessing ? (
            <LoadingSpinner label="Processing transcript..." size="small" />
          ) : (
            "Process Video"
          )}
        </button>
      </form>

      {validationError && (
        <p className="video-input-validation-error">{validationError}</p>
      )}
    </div>
  );
}
