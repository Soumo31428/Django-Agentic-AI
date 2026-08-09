from google import genai
from decouple import config

client = genai.Client(
    api_key=config("GEMINI_API_KEY")
)

response = client.models.generate_content(
    model=config("GEMINI_MODEL"),
    contents="Explain how AI works in a few words in Engineering Tasks?"
)

print(response.text)