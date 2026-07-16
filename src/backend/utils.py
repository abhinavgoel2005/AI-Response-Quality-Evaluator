import json


def parse_json_response(response_text, default_key):
    """
    Safely parses JSON returned by the LLM.
    If parsing fails, returns a default dictionary.
    """

    try:
        return json.loads(response_text)

    except Exception:

        return {
            "score": 0,
            default_key: response_text
        }