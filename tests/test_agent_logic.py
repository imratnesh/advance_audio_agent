import pytest
import os
from unittest.mock import MagicMock, patch

from backend.services.agent_service import ConversationalAgent
from backend.services.transcription import transcribe_audio


# --- Unit Tests for Agent Service ---
@pytest.fixture
def agent():
    """Fixture for the ConversationalAgent."""
    # Patch the ChatOllama to avoid actual LLM calls during unit tests
    with patch('backend.services.agent_service.ChatOllama') as MockOllama:
        mock_llm = MagicMock()
        mock_llm.invoke.return_value.content = "This is a mock response."
        MockOllama.return_value = mock_llm
        yield ConversationalAgent(model_name="mock_model")


def test_agent_invocation(agent):
    """Test that the agent can be invoked and returns a mocked response."""
    response = agent.invoke("hello")
    assert response == "This is a mock response."


def test_agent_empty_input(agent):
    """Test agent's behavior with empty input."""
    response = agent.invoke("")
    assert response == "Input text cannot be empty."


# --- Unit Tests for Transcription Service ---
@pytest.fixture
def sample_wav_path():
    """Fixture to provide the path to the sample WAV file."""
    path = "/home/ratnesh/git_cursor_projects/advanced_audio_agent/tests/sample_audio/output.wav"
    if not os.path.exists(path):
        pytest.skip("Sample audio file 'tests/sample_audio/test.wav' not found.")
    return path


def test_transcribe_audio_valid(sample_wav_path): # Use the fixture
    """Test transcription of a valid audio file."""
    # This is an integration test for the transcription logic
    # The expected text depends on your 'test.wav' content.
    # Let's assume it's "hello world".
    transcribed_text = transcribe_audio(sample_wav_path)
    print(transcribed_text)
    assert isinstance(transcribed_text, str)
    # A more robust check for a common phrase in your test audio
    assert "playing soccer" in transcribed_text.lower()


def test_transcribe_audio_file_not_found():
    """Test transcription with a non-existent file path."""
    result = transcribe_audio("non_existent_file.wav")
    assert "Error: Audio file not found." in result




