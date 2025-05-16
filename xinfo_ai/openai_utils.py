import openai
from django.conf import settings

class OpenAIChatClient:
    def __init__(self):
        openai.api_key = settings.OPENAI_API_KEY
        self.conversation_history = []

    def add_message(self, role, content):
        self.conversation_history.append({'role': role, 'content': content})

    def get_response(self, prompt, model="gpt-4o", max_tokens=3000, temperature=0.7):
        self.add_message('user', prompt)
        messages = [{'role': 'system', 'content': 'You are ChatGPT, a large language model trained by OpenAI.'}]
        messages.extend(self.conversation_history)
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True,
        )

        collected_chunks = []
        full_reply_content = ""

        for chunk in response:
            if 'content' in chunk['choices'][0]['delta']:
                content = chunk['choices'][0]['delta']['content']
                full_reply_content += content
                collected_chunks.append(content)

        self.add_message('assistant', full_reply_content)
        return full_reply_content

    def get_conversation_history(self):
        return self.conversation_history

    def set_conversation_history(self, history):
        self.conversation_history = history

    # ✅ Text to Image using DALL·E 3
    def generate_image(self, prompt, size="1024x1024", quality="standard"):
        response = openai.Image.create(
            model="dall-e-3",
            prompt=prompt,
            size=size,         # options: "1024x1024", "1024x1792", "1792x1024"
            quality=quality,   # "standard" or "hd"
            n=1
        )
        return response["data"][0]["url"]

    # ✅ Image to Image using DALL·E 3 Edit
    def edit_image(self, image_path, mask_path, prompt, size="1024x1024"):
        with open(image_path, "rb") as image_file, open(mask_path, "rb") as mask_file:
            response = openai.Image.create_edit(
                image=image_file,
                mask=mask_file,
                prompt=prompt,
                size=size,
                n=1
            )
        return response["data"][0]["url"]
