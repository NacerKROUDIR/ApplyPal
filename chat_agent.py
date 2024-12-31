from openai import OpenAI
import os
import openai

openai.api_key = os.environ['OPENAI_API_KEY']
# Set OpenAI API key from Streamlit secrets
client = OpenAI()

def call_chat_agent(messages: list):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": m["role"], "content": m["content"]}
            for m in messages
        ],
        stream=True,
    )
    return response