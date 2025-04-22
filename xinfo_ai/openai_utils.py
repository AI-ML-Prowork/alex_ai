# openai_client.py
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
                collected_chunks.append(content)  # Store the collected chunks.....

        self.add_message('assistant', full_reply_content)
        return full_reply_content

    def get_conversation_history(self):
        return self.conversation_history

    def set_conversation_history(self, history):
        self.conversation_history = history




# can add a web seach layer here if needed by Injecting the search results into the system/user prompt.

# def get_response_with_web_search(self, prompt, search_results, model="gpt-4o"):
#     enriched_prompt = f"Here is some live information I found: {search_results}\n\nUser: {prompt}"
#     return self.get_response(enriched_prompt, model=model)
