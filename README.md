# Advanced Audio Agent

This project provides a complete solution for processing audio files through a conversational AI agent. It features a FastAPI backend for processing, a Streamlit frontend for user interaction, and uses a locally-run Ollama model to ensure privacy and avoid paid APIs.

![Screenshot](tests/img.png)

[YouTube](https://www.youtube.com/@IndiaAnalytica) | [LinkedIn](https://www.linkedin.com/in/ratneshkushwaha/)

## Features

- **FastAPI Backend**: Robust API to handle audio file uploads and process them.
- **Streamlit Frontend**: User-friendly interface for file upload and real-time audio.
- **Local AI Model**: Uses Ollama with `deepseek-r1:1.5b` for conversational responses.
- **Offline Transcription**: Employs the `vosk` library for fast, local, and low-latency speech-to-text.
- **Observability**: Structured logging with `loguru` for monitoring and debugging.
- **Asynchronous**: Built with `asyncio` and `FastAPI` for efficient handling of requests.
- **Comprehensive Testing**: Includes unit and integration tests.

---

## Prerequisites

1. **Python 3.9+** (recommended: 3.12)
2. **Ollama**: Install and run Ollama from [https://ollama.ai/](https://ollama.ai/)
3. **Ollama Model**: Pull the required model:
   ```sh
   ollama pull deepseek-r1:1.5b
   ```
4. **Vosk Model**: Download the English model from [https://alphacephei.com/vosk/models](https://alphacephei.com/vosk/models) and extract it as `vosk-model-small-en-us-0.15` in the project root.

---

## Installation

### 1. Clone the repository

```sh
git clone https://github.com/yourusername/advanced_audio_agent.git
cd advanced_audio_agent
```

### 2. Install dependencies

```sh
pip install -r requirements.txt
```

---

## Running the Backend

### Option 1: Using Docker

Build and run the FastAPI backend with Docker:

```sh
docker build -t audio-agent-backend .
docker run -p 8000:8000 audio-agent-backend
```

### Option 2: Run Locally

```sh
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000
```

The API will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000). See interactive docs at `/docs`.

---

## Running the Frontend

In a new terminal:

```sh
cd frontend
streamlit run app.py
```

- The frontend will connect to the backend at `http://127.0.0.1:8000/process-audio/`.
- You can upload `.wav` files or use real-time audio input.

---

## Testing

Run tests with:

```sh
pytest
```

---

## Usage

- **File Upload**: Upload a `.wav` file in the frontend to get transcription and agent response.
- **Real-time Audio**: Use the real-time audio input for live conversation.
- **API**: You can POST a `.wav` file to `/process-audio/` endpoint.

---

## Directory Structure

- `backend/` - FastAPI backend code
- `frontend/` - Streamlit frontend code
- `requirements.txt` - Python dependencies
- `Dockerfile` - For backend containerization
- `tests/` - Test cases and sample audio

---

## Notes

- Ensure Ollama and the required model are running before starting the backend.
- The Vosk model directory must be present as `vosk-model-small-en-us-0.15` in the project root.
- Logs are written to the `logs/` directory.

---

## Voice AI Agent

This project features a Voice AI Agent that processes audio input, transcribes speech to text, and can interact with users through natural language. The backend leverages FastAPI and Vosk for speech recognition, while the frontend provides an interactive interface using Streamlit. The agent can:

- Accept `.wav` audio files and transcribe spoken content.
- Respond to user queries using advanced language models (ensure Ollama and the required model are running).
- Log interactions and results for review and debugging.

---
