import sys

import requests
import streamlit as st
from loguru import logger

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

# --- UI Layout ---
col1, col2 = st.columns(2)

with col1:
    st.header("File-based Processing")
    st.markdown("Upload a `.wav` audio file to get a transcription and a response.")
    uploaded_file = st.file_uploader("Choose a .wav file", type=["wav"])

    if uploaded_file is not None:
        st.audio(uploaded_file, format='audio/wav')
        if st.button("Process Audio File", use_container_width=True):
            with st.spinner("Processing file..."):
                try:
                    files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    response = requests.post(API_URL, files=files, timeout=120)
                    if response.status_code == 200:
                        result = response.json()
                        st.info(f"**You said:** {result.get('transcribed_text')}")
                        st.success(f"**Agent said:** {result.get('agent_response')}")
                    else:
                        st.error(f"Error from API: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"An error occurred: {e}")

with col2:
    st.header("🎙️ Real-time Conversation (via Audio Input)")
    st.markdown("Record a short message and send it to the agent.")

    audio_data = st.audio_input("Press to Record to ask question")

    if audio_data:
        st.audio(audio_data, format='audio/wav')
        st.success("🎧 Audio recorded! Ready to send.")

        if st.button("Send", type="primary", use_container_width=True):
            st.info("📤 Sending audio to backend...")
            try:
                # Optional: display waveform
                import matplotlib.pyplot as plt
                import wave
                import numpy as np
                import io

                wav_bytes = audio_data.read()
                with wave.open(io.BytesIO(wav_bytes), 'rb') as wf:
                    sample_rate = wf.getframerate()
                    frames = wf.readframes(wf.getnframes())
                    audio_np = np.frombuffer(frames, dtype=np.int16)

                st.markdown(f"🔊 **Sample rate:** {sample_rate} Hz &nbsp;&nbsp; 🔢 **Samples:** {len(audio_np)}")
                fig, ax = plt.subplots()
                ax.plot(audio_np)
                ax.set_title("Recorded Audio Waveform")
                st.pyplot(fig)

                # Send to backend
                files = {'file': ('recorded_audio.wav', wav_bytes, 'audio/wav')}
                response = requests.post(API_URL, files=files, timeout=120)

                if response.status_code == 200:
                    result = response.json()
                    st.info(f"**You said:** {result.get('transcribed_text')}")
                    st.success(f"**Agent said:** {result.get('agent_response')}")
                else:
                    st.error(f"❌ API Error {response.status_code}: {response.text}")
            except Exception as e:
                st.error(f"🚨 Failed to process audio: {e}")
