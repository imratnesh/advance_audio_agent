import streamlit as st
import requests

st.title("🎙️ Quick Audio Recorder")

audio_data = st.audio_input("Speak now...")

if audio_data is not None:
    st.audio(audio_data, format='audio/wav')
    if st.button("Send to API"):
        files = {'file': ('recorded.wav', audio_data, 'audio/wav')}
        response = requests.post("http://127.0.0.1:8000/process-audio/", files=files)
        st.write(response.json())
