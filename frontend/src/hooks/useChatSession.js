import { useCallback, useState } from "react";
import { askQuestion, deleteSession, processVideo } from "../api/client";

/**
 * Encapsulates all state and API interaction for a single video Q&A session:
 * - which video/session is active
 * - the running chat transcript
 * - loading flags for the two async actions (process video, ask question)
 * - the current user-facing error, if any
 */
export function useChatSession() {
  const [sessionId, setSessionId] = useState(null);
  const [videoId, setVideoId] = useState(null);
  const [messages, setMessages] = useState([]); // { role: "user" | "assistant", content: string }
  const [isProcessingVideo, setIsProcessingVideo] = useState(false);
  const [isAskingQuestion, setIsAskingQuestion] = useState(false);
  const [error, setError] = useState(null);

  const isVideoLoaded = Boolean(sessionId);

  const loadVideo = useCallback(async (videoUrl) => {
    const trimmed = videoUrl.trim();
    if (!trimmed) {
      setError("Paste a YouTube URL first.");
      return;
    }

    setIsProcessingVideo(true);
    setError(null);

    try {
      const result = await processVideo(trimmed);
      // Fresh video — discard whatever session/messages existed before.
      setSessionId(result.session_id);
      setVideoId(result.video_id);
      setMessages([]);
    } catch (err) {
      setError(err.message);
      setSessionId(null);
      setVideoId(null);
    } finally {
      setIsProcessingVideo(false);
    }
  }, []);

  const sendQuestion = useCallback(
    async (question) => {
      const trimmed = question.trim();
      if (!trimmed || !sessionId) return;

      const userMessage = { role: "user", content: trimmed };
      setMessages((prev) => [...prev, userMessage]);
      setIsAskingQuestion(true);
      setError(null);

      try {
        const result = await askQuestion(sessionId, trimmed);
        setMessages((prev) => [...prev, { role: "assistant", content: result.answer }]);
      } catch (err) {
        setError(err.message);
      } finally {
        setIsAskingQuestion(false);
      }
    },
    [sessionId]
  );

  const reset = useCallback(() => {
    // Best-effort session cleanup on the backend; never block the UI reset on it.
    if (sessionId) {
      deleteSession(sessionId).catch(() => {});
    }
    setSessionId(null);
    setVideoId(null);
    setMessages([]);
    setError(null);
    setIsProcessingVideo(false);
    setIsAskingQuestion(false);
  }, [sessionId]);

  const clearError = useCallback(() => setError(null), []);

  return {
    sessionId,
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
  };
}
