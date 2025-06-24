import wave

try:
    with wave.open('sample_audio/test.wav', 'rb') as wav_file:
        print("Successfully opened WAV file.")
        # You can now work with the file, for example:
        print(f"Channels: {wav_file.getnchannels()}")
        print(f"Sample Width: {wav_file.getsampwidth()}")
        print(f"Frame Rate: {wav_file.getframerate()}")
except FileNotFoundError:
    print("Error: The audio file was not found.")
except wave.Error as e:
    print(f"Error reading WAV file: {e}")
