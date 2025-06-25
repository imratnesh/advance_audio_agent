import wave
import json
from vosk import Model, KaldiRecognizer
from loguru import logger

# --- Configuration ---
# Ensure you have the vosk model downloaded.
# If not, it will be downloaded on the first run.
# For better performance, you can download a larger model from:
# https://alphacephei.com/vosk/models
MODEL_PATH = "vosk-model-small-en-us-0.15"

try:
    model = Model(model_name=MODEL_PATH)
    logger.success(f"Successfully loaded Vosk model: {MODEL_PATH}")
except Exception as e:
    logger.error(f"Failed to load Vosk model. Please ensure it's downloaded. Error: {e}")
    model = None


def transcribe_audio(wav_file_path: str) -> str:
    """
    Transcribes a .wav audio file to text using the Vosk library.

    Args:
        wav_file_path (str): The path to the .wav file.

    Returns:
        str: The transcribed text.
    """
    if not model:
        return "Transcription service is not available."

    try:
        with wave.open(wav_file_path, "rb") as wf:
            if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
                logger.error("Audio file must be WAV format mono 16-bit.")
                return "Error: Audio file must be WAV format mono 16-bit."

            rec = KaldiRecognizer(model, wf.getframerate())
            rec.SetWords(True)

            logger.info(f"Transcribing audio file: {wav_file_path}")

            full_text = ""
            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    result = json.loads(rec.Result())
                    full_text += result.get('text', '') + " "

            final_result = json.loads(rec.FinalResult())
            full_text += final_result.get('text', '')

            logger.success("Transcription completed.")
            return full_text.strip()

    except FileNotFoundError:
        logger.error(f"Audio file not found at path: {wav_file_path}")
        return "Error: Audio file not found."
    except Exception as e:
        logger.error(f"An error occurred during transcription: {e}")
        return "Error: An unexpected error occurred during transcription."

# --- New Class for Streaming Transcription ---
class StreamingTranscriber:
    """Handles streaming audio transcription for a single session."""
    def __init__(self, sample_rate: int):
        if not model:
            raise ConnectionError("Vosk model not loaded")
        logger.info(f"Initializing streaming transcriber with sample rate: {sample_rate}")
        self.recognizer = KaldiRecognizer(model, sample_rate)
        self.recognizer.SetWords(True)

    def process_chunk(self, chunk: bytes) -> str | None:
        """
        Processes an audio chunk. Returns transcribed text if a sentence is complete.
        """
        logger.info(f"process_chunk")
        if self.recognizer.AcceptWaveform(chunk):
            result = json.loads(self.recognizer.Result())
            text = result.get('text')
            if text:
                logger.info(f"Partial transcript: '{text}'")
                return text
        return None

    def get_final_result(self) -> str:
        """Gets the final transcription result at the end of the stream."""
        logger.info(f"get_final_result")
        final_result = json.loads(self.recognizer.FinalResult())
        return final_result.get('text', '')