import os
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

response = client.models.generate_content(
    model="gemini-2.5-flash-lite",
    contents="Say hello in Portuguese."
)

print(response.text)
print(f"Tokens used: {response.usage_metadata}")