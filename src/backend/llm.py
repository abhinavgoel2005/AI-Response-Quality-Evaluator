import os
import time
import re

import google.generativeai as genai
from dotenv import load_dotenv


# ==========================================
# ENVIRONMENT SETUP
# ==========================================

load_dotenv()


# ==========================================
# GEMINI CONFIGURATION
# ==========================================

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "GEMINI_API_KEY was not found. "
        "Please add it to your .env file."
    )


genai.configure(
    api_key=api_key
)


# ==========================================
# MODEL
# ==========================================

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


# ==========================================
# RETRY CONFIGURATION
# ==========================================

# Initial request + 2 retries
MAX_RETRIES = 2

# Used when Gemini does not provide a retry delay.
DEFAULT_RETRY_DELAY = 15

# Prevent unusually long waits from a malformed
# or unexpected retry value.
MAX_RETRY_DELAY = 60


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def _is_rate_limit_error(error):

    """
    Determine whether an exception represents
    a Gemini rate-limit / quota error.
    """

    error_text = str(error).lower()

    indicators = [
        "429",
        "resource_exhausted",
        "resource exhausted",
        "rate limit",
        "quota exceeded",
        "too many requests"
    ]

    return any(
        indicator in error_text
        for indicator in indicators
    )


def _extract_retry_delay(error):

    """
    Extract Gemini's suggested retry delay
    from an error message when available.

    Examples:
        retry_delay { seconds: 20 }
        retry in 19.42s
    """

    error_text = str(error)


    # --------------------------------------
    # Pattern 1:
    # retry_delay { seconds: 20 }
    # --------------------------------------

    match = re.search(
        r"retry_delay\s*\{.*?"
        r"seconds:\s*(\d+)",
        error_text,
        re.IGNORECASE | re.DOTALL
    )

    if match:

        return min(
            int(match.group(1)) + 1,
            MAX_RETRY_DELAY
        )


    # --------------------------------------
    # Pattern 2:
    # Please retry in 19.42s
    # --------------------------------------

    match = re.search(
        r"retry\s+in\s+"
        r"(\d+(?:\.\d+)?)s",
        error_text,
        re.IGNORECASE
    )

    if match:

        delay = float(
            match.group(1)
        )

        # Add a small buffer so we do not
        # retry exactly at the boundary.

        return min(
            delay + 1,
            MAX_RETRY_DELAY
        )


    return None


def _clean_response(text):

    """
    Clean markdown code fences that Gemini
    may add around JSON responses.
    """

    if not text:

        return ""


    text = text.strip()


    if text.startswith("```json"):

        text = text[
            len("```json"):
        ].strip()


    elif text.startswith("```"):

        text = text[
            len("```"):
        ].strip()


    if text.endswith("```"):

        text = text[:-3].strip()


    return text


# ==========================================
# GENERATE RESPONSE
# ==========================================

def generate_response(prompt: str):

    """
    Generate a response using Gemini.

    Rate-limit errors are retried automatically.
    Other errors are raised immediately.
    """

    if not prompt or not prompt.strip():

        raise ValueError(
            "Prompt cannot be empty."
        )


    for attempt in range(
        MAX_RETRIES + 1
    ):

        try:

            response = model.generate_content(
                prompt
            )


            # ----------------------------------
            # Validate Response
            # ----------------------------------

            text = response.text


            if not text:

                raise ValueError(
                    "Gemini returned an empty response."
                )


            return _clean_response(
                text
            )


        except Exception as e:

            # ----------------------------------
            # Non-rate-limit Error
            # ----------------------------------

            if not _is_rate_limit_error(e):

                print(
                    "LLM Error:",
                    e
                )

                raise


            # ----------------------------------
            # Maximum Retries Reached
            # ----------------------------------

            if attempt >= MAX_RETRIES:

                print(
                    "LLM Rate Limit Error: "
                    "maximum retries reached."
                )

                raise


            # ----------------------------------
            # Determine Retry Delay
            # ----------------------------------

            retry_delay = (
                _extract_retry_delay(e)
            )


            if retry_delay is None:

                # Exponential fallback:
                #
                # retry 1 -> 15 seconds
                # retry 2 -> 30 seconds

                retry_delay = min(
                    DEFAULT_RETRY_DELAY
                    * (2 ** attempt),
                    MAX_RETRY_DELAY
                )


            # ----------------------------------
            # Wait Before Retry
            # ----------------------------------

            print(
                "\nGemini rate limit reached."
            )

            print(
                f"Retrying in "
                f"{retry_delay:.1f} seconds..."
            )

            print(
                f"Retry attempt "
                f"{attempt + 1}/{MAX_RETRIES}"
            )


            time.sleep(
                retry_delay
            )


    # Defensive fallback.
    # Normally unreachable.

    raise RuntimeError(
        "Unable to generate an LLM response."
    )