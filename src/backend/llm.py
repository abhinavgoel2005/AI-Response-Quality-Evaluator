import os

from dotenv import load_dotenv
from groq import Groq


# =========================================================
# ENVIRONMENT CONFIGURATION
# =========================================================

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY was not found. "
        "Please add it to the .env file."
    )


# =========================================================
# GROQ CLIENT
# =========================================================

client = Groq(
    api_key=GROQ_API_KEY
)


# =========================================================
# MODEL CONFIGURATION
# =========================================================

MODEL_NAME = "openai/gpt-oss-20b"

TEMPERATURE = 0.1
MAX_TOKENS = 1024


# =========================================================
# RESPONSE CLEANING
# =========================================================

def clean_response(text: str) -> str:

    if not text:
        return ""

    text = text.strip()

    if text.startswith("```json"):
        text = text[len("```json"):].strip()

    elif text.startswith("```"):
        text = text[3:].strip()

    if text.endswith("```"):
        text = text[:-3].strip()

    return text


# =========================================================
# LLM GENERATION
# =========================================================

def generate_response(prompt: str) -> str:

    if not prompt or not prompt.strip():

        raise ValueError(
            "Prompt cannot be empty."
        )

    try:

        completion = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": prompt.strip()
                }
            ],
            temperature=TEMPERATURE,
            max_tokens=MAX_TOKENS,
            timeout=60.0
        )


        # ---------------------------------
        # Validate Groq Response
        # ---------------------------------

        if (
            not completion.choices
            or not completion.choices[0].message
            or not completion.choices[0].message.content
        ):

            raise ValueError(
                "Groq returned an empty response."
            )


        # ---------------------------------
        # Extract Response
        # ---------------------------------

        text = (
            completion
            .choices[0]
            .message
            .content
        )


        # ---------------------------------
        # Clean Response
        # ---------------------------------

        text = clean_response(text)


        if not text:

            raise ValueError(
                "Groq returned an empty response "
                "after response cleaning."
            )


        return text


    except Exception as e:

        print(
            "Groq LLM Error:",
            e
        )

        raise