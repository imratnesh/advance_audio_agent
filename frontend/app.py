import requests
import streamlit as st

# --- Configuration ---
API_URL = "http://127.0.0.1:8000/process-audio/"

# --- Streamlit Page Configuration ---
st.set_page_config(
    page_title="Advanced Audio Agent",
    page_icon="🎙️",
    layout="centered"
)

st.title("🎙️ Advanced Audio Agent")
st.markdown("Upload a `.wav` audio file to get a transcription and a response from our AI agent.")

# --- File Uploader ---
uploaded_file = st.file_uploader("Choose a .wav file", type=["wav"])

if uploaded_file is not None:
    st.audio(uploaded_file, format='audio/wav')

    # --- Process Button ---
    if st.button("Process Audio", use_container_width=True):
        with st.spinner("Processing... This may take a moment."):
            try:
                # Prepare the file for the API request
                files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                # Send the request to the FastAPI backend with the headers
                response = requests.post(API_URL, files=files, timeout=120)

                if response.status_code == 200:
                    result = response.json()
                    st.divider()
                    st.subheader("Transcription")
                    st.info(result.get("transcribed_text", "No transcription available."))

                    st.subheader("Agent Response")
                    st.success(result.get("agent_response", "No response from agent."))
                else:
                    st.error(f"Error from API: {response.status_code} - {response.text}")

            except requests.exceptions.RequestException as e:
                st.error(f"Could not connect to the API. Please ensure the backend is running. Error: {e}")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
