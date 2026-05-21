from dotenv import load_dotenv
import os
from openai import AzureOpenAI

load_dotenv()

client = AzureOpenAI(
    api_version="2024-12-01-preview",
    azure_endpoint=os.getenv("AZURE_MODEL_EUROPE_ENDPOINT"),
    api_key=os.getenv("AZURE_EUROPE_KEY"),
)

response = client.chat.completions.create(
    model="gpt-5.4-mini",
    messages=[
        {
            "role": "user",
            "content": "Say hello"
        }
    ],
    temperature=0
)

print(response.choices[0].message.content)
