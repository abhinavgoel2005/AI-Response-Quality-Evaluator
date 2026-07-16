from backend.llm import generate_response
from backend.utils import parse_json_response


class RelevanceJudge:

    def evaluate(self, question, response):

        prompt = f"""
You are an expert evaluator of AI responses.

Evaluate ONLY the relevance of the response.

Question:
{question}

AI Response:
{response}

Return ONLY valid JSON.

The JSON format must be:

{{
    "score": number,
    "reason": "short explanation"
}}

Rules:

- Score between 1 and 10.
- Do NOT write markdown.
- Do NOT use ```json.
- Return ONLY JSON.
"""

        result = generate_response(prompt)

        return parse_json_response(
             result,
              "reason"
        )