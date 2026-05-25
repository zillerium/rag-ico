from openai import AzureOpenAI
from dotenv import load_dotenv
import os

load_dotenv()

print("ENDPOINT =", os.getenv("AZURE_OPENAI_ENDPOINT"))
print("KEY EXISTS =", bool(os.getenv("AZURE_OPENAI_KEY")))
print("API VERSION =", os.getenv("OPENAI_API_VERSION"))

client = AzureOpenAI(
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version=os.getenv("OPENAI_API_VERSION")
)

response = client.chat.completions.create(
    model="gpt-5.4-mini",
    messages=[
        {
            "role": "user",
            "content": "Say hello"
        }
    ]
)

print(response.choices[0].message.content)
