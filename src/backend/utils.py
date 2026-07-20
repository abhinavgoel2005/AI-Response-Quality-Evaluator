import json


def parse_json_response(response_text, default_key):
    """
    Safely parses JSON returned by the LLM.
    If parsing fails, returns a default dictionary.
    """

    try:
        return json.loads(response_text)

    except Exception:

        result = {
            "score": 0,
            default_key: (
                "Evaluation could not be completed because the AI service "
                "was unavailable."
            ),
            "_error": response_text
        }

        if default_key == "reason":
            result.setdefault("unsupported_claims", [])

        return result