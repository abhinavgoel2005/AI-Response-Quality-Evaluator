import os

import google.generativeai as genai
from dotenv import load_dotenv


# Load environment variables
load_dotenv()


# Configure Gemini
genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)


# Initialize model
model = genai.GenerativeModel("gemini-2.5-flash")


def generate_response(prompt: str):

    try:

        response = model.generate_content(prompt)

        text = response.text.strip()

        # Remove markdown code block if Gemini adds it
        if text.startswith("```json"):
            text = text.replace("```json", "", 1)

        if text.startswith("```"):
            text = text.replace("```", "", 1)

        if text.endswith("```"):
            text = text[:-3]

        return text.strip()

    except Exception as e:

        return f"ERROR: {str(e)}"