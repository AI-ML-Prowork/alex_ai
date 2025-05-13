from huggingface_hub import InferenceClient
from xinfo_ai.settings import HF_API_KEY

client = InferenceClient(
    provider="replicate",
    token=HF_API_KEY,
)
model = "black-forest-labs/FLUX.1-dev"

import base64
from io import BytesIO

def generate_image(prompt):
    image = client.text_to_image(prompt, model=model)

    # Convert the PIL image to a base64-encoded string
    buffered = BytesIO()
    image.save(buffered, format="PNG")  # You can keep WebP if you prefer
    image_base64 = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return f"data:image/png;base64,{image_base64}"