import axios from "axios";

// Read the backend base URL from Vite env, defaulting to localhost:8000.
const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const httpClient = axios.create({
  baseURL: BASE_URL,
  timeout: 60000, // video processing can legitimately take 10-30+ seconds
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Normalizes any axios error into a plain, user-facing message.
 * - Backend errors follow { status: "error", message: "..." } — use that message.
 * - Network errors (backend unreachable, timeout) get a friendly fallback.
 * - Anything else falls back to a generic message.
 */
function toFriendlyError(error) {
  if (error.response && error.response.data && error.response.data.message) {
    return new Error(error.response.data.message);
  }
  if (error.code === "ECONNABORTED") {
    return new Error("The request took too long to respond. Please try again.");
  }
  if (error.request) {
    return new Error("Can't reach the server. Is the backend running?");
  }
  return new Error("Something went wrong. Please try again.");
}

/** GET /api/health */
export async function checkHealth() {
  try {
    const { data } = await httpClient.get("/api/health");
    return data;
  } catch (error) {
    throw toFriendlyError(error);
  }
}

/**
 * POST /api/process-video
 * @param {string} videoUrl
 * @returns {Promise<{session_id: string, video_id: string, status: string, message: string}>}
 */
export async function processVideo(videoUrl) {
  try {
    const { data } = await httpClient.post("/api/process-video", {
      video_url: videoUrl,
    });
    return data;
  } catch (error) {
    throw toFriendlyError(error);
  }
}

/**
 * POST /api/ask
 * @param {string} sessionId
 * @param {string} question
 * @returns {Promise<{answer: string, session_id: string}>}
 */
export async function askQuestion(sessionId, question) {
  try {
    const { data } = await httpClient.post("/api/ask", {
      session_id: sessionId,
      question,
    });
    return data;
  } catch (error) {
    throw toFriendlyError(error);
  }
}

/**
 * DELETE /api/session/{session_id}
 * Best-effort cleanup — callers should not block the UI on this.
 */
export async function deleteSession(sessionId) {
  try {
    const { data } = await httpClient.delete(`/api/session/${sessionId}`);
    return data;
  } catch (error) {
    throw toFriendlyError(error);
  }
}

export default httpClient;
