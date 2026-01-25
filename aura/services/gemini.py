from google import genai
from google.genai import types
from django.conf import settings


# Initialize the client
client = genai.Client(api_key=settings.GEMINI_API_KEY)

def generate_response(system_prompt: str, user_message: str) -> str:
    """Generate a response using the new google-genai SDK."""
    
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=user_message,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            thinking_config=types.ThinkingConfig(thinking_level="low")
        )
    )

    return response.text.strip()




