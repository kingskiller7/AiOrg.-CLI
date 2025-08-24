from gtts import gTTS
import os

def text_to_speech(text: str, lang: str = 'en') -> str:
    """Converts text to speech and returns the audio file path."""
    tts = gTTS(text=text, lang=lang)
    audio_path = f"{text.replace(' ', '_')}.mp3"
    tts.save(audio_path)
    return audio_path
