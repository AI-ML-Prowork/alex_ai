import base64
from io import BytesIO
from xinfo_ai.settings import HF_API_KEY

from huggingface_hub import InferenceClient

client = InferenceClient(
    provider="fal-ai",
    api_key=HF_API_KEY,
)

def generate_video(prompt):
    video = client.text_to_video(prompt, model="Lightricks/LTX-Video")
    if hasattr(video, "read"):  
        video_bytes = video.read()
    else:
        video_bytes = video
    video_base64 = base64.b64encode(video_bytes).decode("utf-8")
    return f"data:video/mp4;base64,{video_base64}"
