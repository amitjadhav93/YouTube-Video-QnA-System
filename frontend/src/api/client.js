import axios from "axios";

export const API_BASE_URL = "http://localhost:8000";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 60000, 
});

function extractErrorMessage(error, fallback) {
  if (error.response && error.response.data && error.response.data.detail) {
    return error.response.data.detail;
  }
  if (error.code === "ECONNABORTED") {
    return "The request timed out. The server may be taking longer than expected.";
  }
  if (error.message === "Network Error") {
    return "Could not reach the server. Is the backend running at " + API_BASE_URL + "?";
  }
  return fallback;
}

export async function checkHealth() {
  try {
    const response = await apiClient.get("/api/health");
    return response.data;
  } catch (error) {
    throw new Error(extractErrorMessage(error, "Health check failed."));
  }
}


export async function processVideo(youtubeUrl) {
  try {
    const response = await apiClient.post("/api/process-video", {
      youtube_url: youtubeUrl,
    });
    return response.data;
  } catch (error) {
    throw new Error(
      extractErrorMessage(error, "Failed to process the video. Please try again.")
    );
  }
}


export async function askQuestion(videoId, question) {
  try {
    const response = await apiClient.post("/api/ask", {
      video_id: videoId,
      question: question,
    });
    return response.data;
  } catch (error) {
    throw new Error(
      extractErrorMessage(error, "Failed to get an answer. Please try again.")
    );
  }
}

export default apiClient;
