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

    # Assume it's a file-like object or bytes; if it returns a file path, adjust accordingly
    if hasattr(video, "read"):  # file-like
        video_bytes = video.read()
    else:
        video_bytes = video  # If already bytes

    video_base64 = base64.b64encode(video_bytes).decode("utf-8")

    # Use mp4 mimetype if format is mp4. Adjust if format is different.
    return f"data:video/mp4;base64,{video_base64}"
