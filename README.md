# 📑 YouTube Video QnA System: RAG-Powered Video Understanding

**YouTube Video QnA System** is an intelligent tool engineered to make any YouTube video instantly searchable through natural conversation. By deploying a **Retrieval-Augmented Generation (RAG) pipeline** powered by **Google's Gemini LLM**, it fetches a video's transcript, breaks it into meaningful chunks, embeds them locally, and lets you ask natural-language questions about the video's content — answered with the exact transcript snippets (and timestamps) the answer came from.

The final experience is delivered through a clean **React chat interface**, so you can paste a link, wait a moment, and start asking questions like you would to a person who just watched the video.

---

## 🚨 Why YouTube Video QnA System?

Getting information out of a long video is a significant bottleneck for learners and researchers alike.
It's slow, easy to lose your place in, and impossible to scale across many videos.

### Core Challenges:
- **Time-Consuming Viewing**: Scrubbing through a long video to find one answer drains productivity.
- **No Easy Way to Search Spoken Content**: Video platforms don't let you search *inside* what was said.
- **Context Without a Source**: General-purpose chat tools can answer questions but can't point back to the exact moment in the video.

---

## ✅ How YouTube Video QnA System Solves This

- 🤖 **Automated Transcript Retrieval**: Fetches and normalizes the transcript directly from any YouTube URL.
- 🧩 **Smart Chunking**: Splits the transcript into overlapping chunks while preserving each chunk's original timestamp.
- 🧠 **Local Embeddings + Gemini Reasoning**: Embeds chunks locally with HuggingFace sentence-transformers, retrieves the most relevant ones via FAISS, and lets Gemini (via LangChain) generate the answer.
- 📊 **Grounded, Structured Output**: Every answer comes back with the transcript sources (and timestamps) it was built from.

---

## 🛠️ Tech Stack

### 🌐 Frontend
- **React 18** – UI components (functional components + hooks only)
- **Vite** – Lightning-fast dev/build tool
- **axios** – HTTP client, centralized in a single API module
- **Plain CSS** – Component-scoped `.css` files, no UI kit

### 🔗 Backend
- **FastAPI** – Python web framework (APIs)
- **LangChain** – RAG pipeline orchestration
- **Google Gemini** – LLM for answer generation (`langchain-google-genai`)
- **sentence-transformers** – Local HuggingFace embeddings (`all-MiniLM-L6-v2`)
- **FAISS** – Vector similarity search, one index per video
- **youtube-transcript-api** – Transcript fetching
- **Pydantic** – Request/response schema validation

---

## 🏗️ RAG Pipeline Architecture

YouTube Video QnA System's strength = a **focused, single-pass RAG pipeline**.

```
YouTube URL → transcript fetch → chunking → HuggingFace embeddings
  → FAISS index (per video) → similarity search → LangChain prompt
  → Gemini → answer
```

- **Transcript Service** → Fetches and normalizes the transcript for a given video ID.
- **Chunking Service** → Splits the transcript with `RecursiveCharacterTextSplitter`, keeping `start_time` metadata per chunk.
- **Embedding Service** → Generates cached HuggingFace sentence-transformer embeddings, run locally on CPU.
- **Vectorstore Service** → Creates/loads/saves a FAISS index per `video_id`, backed by a small processed-video registry.
- **QnA Service** → Runs similarity search, builds the LangChain prompt, and calls Gemini for the final answer.

---

## 📡 API Reference

### ▶️ Health Check
**GET** `/api/health`
```json
{ "status": "ok" }
```

### ▶️ Process Video
**POST** `/api/process-video`
Fetches and indexes a video's transcript.

#### Request Body:
```json
{ "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ" }
```

#### Response (200):
```json
{
  "video_id": "dQw4w9WgXcQ",
  "status": "processed",
  "chunk_count": 42,
  "transcript_available": true
}
```
Re-calling with the same video returns `"status": "already_processed"` without re-fetching or re-embedding. Errors return `{ "detail": "..." }` with 400 (bad URL), 404 (no transcript available), or 500 (indexing failure).

### ▶️ Ask a Question
**POST** `/api/ask`
Answers a question about an already-processed video.

#### Request Body:
```json
{ "video_id": "dQw4w9WgXcQ", "question": "What is this video about?" }
```

#### Response (200):
```json
{
  "video_id": "dQw4w9WgXcQ",
  "question": "What is this video about?",
  "answer": "...",
  "sources": [
    { "text": "...transcript snippet...", "start_time": 12.5 }
  ]
}
```
If the video hasn't been processed yet, returns `404`:
```json
{ "detail": "Video has not been processed yet. Call /api/process-video first." }
```

---

## 🧪 Getting Started

### 📦 Prerequisites
- Python **3.11+**
- Node.js **v18+** (with npm)
- A Google Gemini API key (get one at https://aistudio.google.com/app/apikey)

---

### 🚀 Installation

**Clone the Repo**
```bash
git clone <https://github.com/amitjadhav93/YouTube-Video-QnA-System>
cd <YouTube-Video-QnA-System>
```

**Backend Setup**
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**Frontend Setup**
```bash
cd ../frontend
npm install
```

---

### 🔐 Environment Variables

Create **`backend/.env`**):
```env
# Google Gemini API Key
GOOGLE_API_KEY="YOUR_GEMINI_API_KEY"

# Optional: override the default Gemini model
GEMINI_MODEL="gemini-2.0-flash"
```

No API key is needed for embeddings — `sentence-transformers` runs locally on CPU. The first run will download the `all-MiniLM-L6-v2` model (~90 MB) from HuggingFace.

The frontend's backend URL is defined directly in `src/api/client.js`:
```js
export const API_BASE_URL = "http://localhost:8000";
```

---

### 🧑‍💻 Running the Application

**Start Backend (FastAPI)**
```bash
cd backend
uvicorn main:app --reload --port 8000
```
Interactive docs (Swagger UI) are auto-generated at `http://localhost:8000/docs`.

**Start Frontend (Vite)**
```bash
cd frontend
npm run dev
```

App will be available at → [http://localhost:5173](http://localhost:5173)

CORS is enabled for `http://localhost:5173` and `http://localhost:3000` so the React frontend can call this API directly during local development.

---

## 🌱 Future Scope
- 📊 **Dashboard & History** – Browse previously processed videos and past Q&A sessions
- 🌍 **Residential-Proxy Support** – Work around YouTube rate-limiting/blocking of `youtube-transcript-api` on cloud/datacenter IPs
- 🗄️ **Real Database Backing** – Replace the JSON-file video registry with a proper database for concurrent, multi-process use
- ⚡ **Multi-Worker Embedding Cache** – Share a single embedding-model/Gemini-client instance across Uvicorn workers instead of per-process copies
- 🌐 **Multi-Language Support** – Answer questions about videos in multiple languages

---
