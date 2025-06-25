import os
import shutil
import sys
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger

from backend.services.agent_service import agent_instance
from backend.services.transcription import transcribe_audio

# --- FastAPI App Initialization ---
app = FastAPI(
    title="Advanced Audio Agent API",
    description="An API for transcribing audio and getting a response from a conversational agent.",
    version="1.0.0"
)

# --- Logging Configuration ---
logger.remove()
logger.add("logs/api.log", rotation="10 MB", retention="10 days", level="INFO")
logger.add(sys.stderr, level="INFO")

# --- Temporary File Directory ---
TEMP_DIR = "temp_audio"
os.makedirs(TEMP_DIR, exist_ok=True)


@app.post("/process-audio/")
async def process_audio_endpoint(file: UploadFile = File(...)):
    """
    Accepts a .wav audio file, transcribes it, and gets a single conversational response.
    """
    logger.info("Received request for /process-audio/ endpoint.")
    if not file.filename.endswith('.wav'):
        logger.warning(f"Invalid file format uploaded: {file.filename}")
        raise HTTPException(status_code=400, detail="Invalid file format. Please upload a .wav file.")

    temp_file_path = os.path.join(TEMP_DIR, file.filename)

    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logger.info(f"Temporarily saved uploaded file to {temp_file_path}")

        transcribed_text = transcribe_audio(temp_file_path)
        if "Error:" in transcribed_text:
            logger.error(f"Transcription failed: {transcribed_text}")
            raise HTTPException(status_code=500, detail=transcribed_text)
        logger.info(f"Transcription successful for '{file.filename}'.")

        # Simplified agent call
        agent_response = agent_instance.invoke_llm(transcribed_text)
        logger.success("Successfully processed audio and generated agent response.")

        return JSONResponse(
            content={
                "transcribed_text": transcribed_text,
                "agent_response": agent_response
            }
        )
    except Exception as e:
        logger.error(f"An unexpected error occurred in /process-audio/: {e}")
        raise HTTPException(status_code=500, detail="An internal server error occurred.")
    finally:
        # Clean up the temporary file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
            logger.info(f"Cleaned up temporary file: {temp_file_path}")


@app.get("/")
def read_root():
    return {"message": "Welcome to the Advanced Audio Agent API. Use the /docs endpoint to see the API documentation."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)