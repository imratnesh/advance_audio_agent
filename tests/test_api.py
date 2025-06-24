
import pytest
from fastapi.testclient import TestClient
import os
from httpx import AsyncClient

from backend.main import app

client = TestClient(app)

@pytest.fixture
def sample_wav_path_for_api() -> str:
    """Fixture for the sample WAV file path for API tests."""
    test_dir = os.path.dirname(__file__)
    path = os.path.join(test_dir, 'sample_audio', 'output.wav')

    if not os.path.exists(path):
        pytest.skip("Sample audio file 'tests/sample_audio/output.wav' not found for API test.")
    return path


def test_process_audio_success(sample_wav_path_for_api):
    with open(sample_wav_path_for_api, "rb") as f:
        response = client.post("/process-audio", files={"file": ("test.wav", f, "audio/wav")})
    assert response.status_code == 200
    assert response.headers["content-type"] == "application/json"
    data = response.json()
    assert "transcribed_text" in data
    assert "agent_response" in data
    assert "playing soccer" in data["transcribed_text"].lower()
    assert isinstance(data["agent_response"], str)


@pytest.mark.asyncio
async def test_process_audio_endpoint_invalid_format():
    """Test the /process-audio/ endpoint with an invalid file format."""
    # Simulate a non-wav file
    files = {'file': ('test.txt', b"some text data", 'text/plain')}
    # Use the client fixture to make a POST request
    response = client.post("/process-audio/", files=files)

    assert response.status_code == 400
    assert "Please upload a .wav file" in response.json()["detail"]


@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    """Test the root endpoint."""
    # Use the client fixture to make a GET request
    response = await client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.json()["message"]