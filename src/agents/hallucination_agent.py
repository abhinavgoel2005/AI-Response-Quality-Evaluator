from backend.llm import generate_response
from backend.utils import parse_json_response


class HallucinationJudge:

    def evaluate(self, response, reference):

        prompt = f"""
You are an expert evaluator of AI-generated responses.

Your task is to detect hallucinations.

Reference Information:
{reference}

AI Response:
{response}

Compare every factual statement in the AI response against the reference.

Identify any statements that are NOT supported by the reference.

Return ONLY valid JSON in the following format:

{{
    "score": number,
    "unsupported_claims": [
        "claim 1",
        "claim 2"
    ],
    "reason": "Short explanation"
}}

Rules:

- Score must be between 1 and 10.
- If every statement is supported, return an empty list:
  "unsupported_claims": []

- Do NOT use markdown.
- Do NOT use ```json.
- Return ONLY JSON.
"""

        result = generate_response(prompt)

        parsed = parse_json_response(
            result,
            "reason"
        )

        # Ensure required keys always exist
        parsed.setdefault("unsupported_claims", [])
        parsed.setdefault("reason", "")

        return parsed