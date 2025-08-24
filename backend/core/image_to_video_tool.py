from moviepy.editor import ImageClip, concatenate_videoclips

def image_to_video(image_path: str, duration: int = 5) -> str:
    """Creates a video from an image and returns the video path."""
    clip = ImageClip(image_path, duration=duration)
    video_path = f"{image_path.split('.')[0]}.mp4"
    clip.write_videofile(video_path, fps=24)
    return video_path
