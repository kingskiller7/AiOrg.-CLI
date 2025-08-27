from diffusers import StableDiffusionPipeline
import torch
import json

def text_to_image(prompt: str) -> str:
    """Generates an image from a text prompt and returns the image path."""
    model_id = "CompVis/stable-diffusion-v1-4"
    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
    
    if torch.cuda.is_available():
        pipe = pipe.to("cuda")

    image = pipe(prompt).images[0]
    
    image_path = f"{prompt.replace(' ', '_')}.png"
    image.save(image_path)
    
    return json.dumps({"image_path": image_path})
