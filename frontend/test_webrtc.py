import streamlit as st
import requests
import queue
import sys
import io
import wave
import numpy as np  # Import numpy for numerical operations
from loguru import logger
from streamlit_webrtc import webrtc_streamer, WebRtcMode, AudioProcessorBase

# --- Configuration ---
API_URL = "http://127.0.0.1:8000/process-audio/"

# --- Logging Configuration ---
logger.remove()
# Set the level to TRACE if you want to see the frame logs, otherwise INFO is fine.
logger.add("logs/frontend.log", rotation="10 MB", retention="10 days", level="INFO")
logger.add(sys.stderr, level="INFO")

logger.info("Frontend application starting...")

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="Advanced Audio Agent",
    page_icon="🎙️",
    layout="wide"
)

st.title("🎙️ Advanced Audio Agent")

# --- Session State Initialization ---
if "webrtc_messages" not in st.session_state:
    st.session_state.webrtc_messages = []
if "audio_frames_queue" not in st.session_state:
    st.session_state.audio_frames_queue = queue.Queue()
# Add a flag to track the recording state to handle queue clearing
if "is_recording" not in st.session_state:
    st.session_state.is_recording = False
if "recorded_audio_frames" not in st.session_state:
    st.session_state.recorded_audio_frames = []
if "ready_to_send" not in st.session_state:
    st.session_state.ready_to_send = False
if "playing_initialized" not in st.session_state:
    st.session_state.playing_initialized = False


st.header("Real-time Conversation")
st.markdown("Click **Record**, then **Send** when done.")


class AudioProcessor(AudioProcessorBase):
    def __init__(self, audio_queue: queue.Queue):
        self.audio_queue = audio_queue
        logger.info("AudioProcessor initialized.")

    def recv_queued(self, frames):
        import datetime
        logger.info(f"🕒 Frame timestamp: {datetime.datetime.now()} | frames received: {len(frames)}")
        logger.info(f"🎧 recv_queued received {len(frames)} frames. Total queued: {audio_queue.qsize()}")
        for frame in frames:
            self.audio_queue.put(frame.to_ndarray())
        return frames[-1]

audio_queue = st.session_state.audio_frames_queue

ctx = webrtc_streamer(
    key="realtime-agent",
    mode=WebRtcMode.SENDRECV,
    audio_processor_factory=lambda: AudioProcessor(audio_queue=audio_queue),
    media_stream_constraints={"video": False, "audio": True},
)

if ctx.state.playing and not st.session_state.is_recording and not st.session_state.playing_initialized:
    logger.info("🎙️ Recording started. Clearing audio queue.")
    with audio_queue.mutex:
        audio_queue.queue.clear()
    st.session_state.is_recording = True
    st.session_state.ready_to_send = False
    st.session_state.playing_initialized = True


elif not ctx.state.playing and st.session_state.is_recording:
    logger.info("🛑 Recording stopped. Saving audio frames.")
    st.session_state.playing_initialized = False
    st.session_state.is_recording = False
    st.session_state.recorded_audio_frames = []

    while not audio_queue.empty():
        st.session_state.recorded_audio_frames.append(audio_queue.get())
    frame_count = len(st.session_state.recorded_audio_frames)
    if frame_count < 50:
        logger.warning(f"⚠️ Too short: Only {frame_count} audio frames. Ignoring.")
        st.session_state.ready_to_send = False
        st.warning("⚠️ Recording too short. Please record for at least 3 seconds.")
    else:
        st.session_state.ready_to_send = True
        logger.info(f"✅ Buffered {frame_count} audio frames for sending.")
    logger.info(f"✅ Buffered {len(st.session_state.recorded_audio_frames)} audio frames for sending.")

if ctx.state.playing:
    st.info("Recording... Click **Stop** above when you're done.")
    st.markdown(f"🔄 **Frames captured**: `{audio_queue.qsize()}`")
else:
    st.warning("Click **Record** above to start.")

if st.session_state.ready_to_send and st.session_state.recorded_audio_frames:
    logger.info("📤 Ready to show Send button.")
    if st.button("Send", type="primary", use_container_width=True):
        logger.info("📨 Send button clicked.")
        with st.spinner("Processing your message..."):
            audio_frames = st.session_state.recorded_audio_frames
            logger.info(f"Processing {len(audio_frames)} recorded audio frames.")

            concatenated_audio = np.concatenate(audio_frames, axis=0)
            logger.info(f"Concatenated audio shape: {concatenated_audio.shape}, dtype: {concatenated_audio.dtype}")

            processed_audio = concatenated_audio.flatten()
            if np.issubdtype(processed_audio.dtype, np.floating):
                logger.info("Audio is float type. Scaling and converting to int16.")
                audio_int16 = (processed_audio * np.iinfo(np.int16).max).astype(np.int16)
            elif processed_audio.dtype == np.int16:
                logger.info("Audio is already int16. No conversion needed.")
                audio_int16 = processed_audio
            else:
                logger.warning(f"Unexpected audio dtype: {processed_audio.dtype}. Casting to int16.")
                audio_int16 = processed_audio.astype(np.int16)

            logger.info(f"Audio max amplitude: {np.max(np.abs(audio_int16))}")
            logger.info(f"Final audio array for WAV. Shape: {audio_int16.shape}, dtype: {audio_int16.dtype}")

            import matplotlib.pyplot as plt
            fig, ax = plt.subplots()
            ax.plot(audio_int16[:16000])
            ax.set_title("Recorded Audio Waveform")
            st.pyplot(fig)

            audio_bytes = audio_int16.tobytes()

            in_memory_wav = io.BytesIO()
            with wave.open(in_memory_wav, 'wb') as wf:
                wf.setnchannels(1)
                wf.setsampwidth(2)
                wf.setframerate(16000)
                wf.writeframes(audio_bytes)
            in_memory_wav.seek(0)
            logger.success(f"Created in-memory WAV file of size {in_memory_wav.getbuffer().nbytes} bytes.")

            try:
                files = {'file': ('recorded_audio.wav', in_memory_wav, 'audio/wav')}
                with open("debug_recorded.wav", "wb") as f:
                    f.write(in_memory_wav.getbuffer())
                logger.info("Sending audio data to backend API...")
                response = requests.post(API_URL, files=files, timeout=120)

                if response.status_code == 200:
                    result = response.json()
                    logger.success(f"✅ Response received from API: {result}")
                    st.info(f"**You said:** {result.get('transcribed_text')}")
                    st.success(f"**Agent said:** {result.get('agent_response')}")
                else:
                    logger.error(f"❌ API Error {response.status_code}: {response.text}")
                    st.error(f"Error from API: {response.status_code} - {response.text}")
            except Exception as e:
                logger.error(f"🚨 Exception during API call: {e}")
                st.error(f"An error occurred: {e}")

            # Reset send flag after completion
            st.session_state.ready_to_send = False

