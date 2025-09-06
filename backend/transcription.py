import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

def transcribe_file(audio_file_path: str) -> str:
    """
    Transcribe an audio file using Groq Whisper API
    
    Args:
        audio_file_path: Path to audio file (WAV, WebM, MP3, etc.)
        
    Returns:
        Transcribed text
        
    Raises:
        Exception: If transcription fails
    """
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
    
    # Groq Whisper supports various audio formats, not just WAV
    supported_formats = ['.wav', '.webm', '.mp3', '.m4a', '.ogg']
    if not any(audio_file_path.lower().endswith(fmt) for fmt in supported_formats):
        raise ValueError(f"Audio format not supported. Supported formats: {', '.join(supported_formats)}")
    
    client = Groq()
    
    with open(audio_file_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=(os.path.basename(audio_file_path), file.read()),
            model="whisper-large-v3-turbo",
            response_format="text",
        )
    
    return transcription.strip()

if __name__ == "__main__":
    test_file = "test_data/sample_food_recording.wav"
    if os.path.exists(test_file):
        try:
            result = transcribe_file(test_file)
            print(f"Transcription: {result}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        print(f"Test file {test_file} not found")