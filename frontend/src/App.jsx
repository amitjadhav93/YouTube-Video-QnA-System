import { useState } from "react";
import { processVideo, askQuestion } from "./api/client.js";
import VideoInput from "./components/VideoInput.jsx";
import VideoPlayer from "./components/VideoPlayer.jsx";
import ChatWindow from "./components/ChatWindow.jsx";
import ErrorBanner from "./components/ErrorBanner.jsx";
import "./App.css";

export default function App() {
  const [videoId, setVideoId] = useState(null);
  const [chunkCount, setChunkCount] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [processError, setProcessError] = useState("");

  const [exchanges, setExchanges] = useState([]);
  const [isAsking, setIsAsking] = useState(false);
  const [askError, setAskError] = useState("");

  const isProcessed = Boolean(videoId);

  async function handleProcessVideo(youtubeUrl) {
    setIsProcessing(true);
    setProcessError("");

    try {
      const result = await processVideo(youtubeUrl);
      setVideoId(result.video_id);
      setChunkCount(result.chunk_count);
    } catch (error) {
      setProcessError(error.message);
    } finally {
      setIsProcessing(false);
    }
  }

  async function handleAskQuestion(question) {
    setAskError("");
    setIsAsking(true);

    const pendingIndex = exchanges.length;
    setExchanges((prev) => [...prev, { question, isLoading: true }]);

    try {
      const result = await askQuestion(videoId, question);
      setExchanges((prev) => {
        const next = [...prev];
        next[pendingIndex] = {
          question,
          answer: result.answer,
          sources: result.sources,
          isLoading: false,
        };
        return next;
      });
    } catch (error) {
      setExchanges((prev) => {
        const next = [...prev];
        next[pendingIndex] = {
          question,
          isLoading: false,
          error: error.message,
        };
        return next;
      });
      setAskError(error.message);
    } finally {
      setIsAsking(false);
    }
  }

  function handleReset() {
    setVideoId(null);
    setChunkCount(null);
    setProcessError("");
    setExchanges([]);
    setAskError("");
  }

  return (
    <div className="app-shell">
      <div className="app-container">
        {!isProcessed && (
          <>
            <VideoInput onSubmit={handleProcessVideo} isProcessing={isProcessing} />
            <div className="app-error-slot">
              <ErrorBanner
                message={processError}
                onDismiss={() => setProcessError("")}
              />
            </div>
          </>
        )}

        {isProcessed && (
          <div className="qa-view">
            <div className="qa-header">
              <div>
                <h2 className="qa-header-title">Video processed</h2>
                <p className="qa-header-subtitle">
                  {chunkCount != null
                    ? `${chunkCount} transcript chunk${chunkCount === 1 ? "" : "s"} indexed. Ask away.`
                    : "Ask away."}
                </p>
              </div>
              <button type="button" className="qa-new-video-button" onClick={handleReset}>
                New Video
              </button>
            </div>

            <ErrorBanner message={askError} onDismiss={() => setAskError("")} />

            <div className="qa-layout">
              <VideoPlayer videoId={videoId} />
              <ChatWindow
                exchanges={exchanges}
                onAsk={handleAskQuestion}
                isAsking={isAsking}
              />
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
