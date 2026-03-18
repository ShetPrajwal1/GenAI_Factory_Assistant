from faster_whisper import WhisperModel
import os

# Adjust path/model size based on resources. For Mac, "base" or "small" is a good start. 
# You can upgrade to "medium" or "large-v3" if memory permits.
MODEL_SIZE = "base"

print("Loading STT Model...")
# "cpu" with "int8" since Metal support in PyTorch via faster-whisper might not be fully native on all configs out of the box,
# though compute_type="default" or "float32" is best for CPU on Macs.
model = WhisperModel(MODEL_SIZE, device="cpu", compute_type="int8")

def transcribe_audio(audio_path: str) -> str:
    """
    Transcribes an audio file into text using faster-whisper.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found at {audio_path}")
        
    print(f"Transcribing {audio_path}...")
    segments, info = model.transcribe(audio_path, beam_size=5)
    
    transcript = ""
    for segment in segments:
        transcript += segment.text + " "
        
    return transcript.strip()
