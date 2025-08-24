from moviepy import ImageClip, AudioFileClip
from .text_to_image_tool import text_to_image
from .text_to_speech_tool import text_to_speech

def text_to_video(prompt: str) -> str:
    """Creates a video from a text prompt and returns the video path."""
    image_path = text_to_image(prompt)
    audio_path = text_to_speech(prompt)
    
    image_clip = ImageClip(image_path)
    audio_clip = AudioFileClip(audio_path)
    
    video_clip = image_clip.set_audio(audio_clip)
    video_clip.duration = audio_clip.duration
    
    video_path = f"{prompt.replace(' ', '_')}.mp4"
    video_clip.write_videofile(video_path, fps=24)
    
    return video_path
