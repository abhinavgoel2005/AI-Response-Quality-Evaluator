from backend.utils import parse_json_response

from backend.llm import generate_response


class AccuracyJudge:

    def evaluate(self, question, response, reference):

        prompt = f"""
You are an expert evaluator of AI responses.

Evaluate ONLY factual accuracy.

Question:
{question}

Reference Answer:
{reference}

AI Response:
{response}

Compare the AI response against the reference answer.

Return ONLY valid JSON.

{{
    "score": number,
    "evidence": "Brief explanation"
}}

Rules:

- Score between 1 and 10.
- Do not evaluate relevance.
- Do not evaluate hallucinations.
- Return JSON only.
"""

        result = generate_response(prompt)

        return parse_json_response(
             result,
             "evidence"
        )