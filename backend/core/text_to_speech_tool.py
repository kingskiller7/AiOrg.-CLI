from gtts import gTTS
import os
import json

def text_to_speech(text: str, lang: str = 'en') -> str:
    """Converts text to speech and returns the audio file path."""
    tts = gTTS(text=text, lang=lang)
    audio_path = f"{text.replace(' ', '_')}.mp3"
    tts.save(audio_path)
    return json.dumps({"audio_path": audio_path})
