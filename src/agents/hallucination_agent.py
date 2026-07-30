from backend.llm import generate_response
from backend.utils import parse_json_response


class HallucinationJudge:

    def evaluate(self, response, reference="", retrieved_chunks=None):

        retrieved_chunks = retrieved_chunks or []

        rag_evidence = "\n\n".join(
            f"Source {i + 1} - {chunk['title']}:\n{chunk['content']}"
            for i, chunk in enumerate(retrieved_chunks)
        )

        if not rag_evidence:
            rag_evidence = "No retrieved evidence available."

        if not reference or not reference.strip():
            reference = "No reference answer provided."

        prompt = f"""
You are an expert evaluator of AI-generated responses.

Your task is to detect hallucinations.

AI Response:
{response}

Reference Answer:
{reference}

Retrieved Evidence:
{rag_evidence}

Analyze the factual claims in the AI response.

A claim should be considered unsupported if:
- It contradicts the reference answer or retrieved evidence.
- It makes a factual assertion that cannot be supported by the available evidence.

Do NOT flag a claim merely because it is worded differently from the evidence.

When a reference answer is provided, use it as important evidence.
Use the retrieved evidence as additional grounding.

If no reference answer is provided, use the retrieved evidence as the
primary source for hallucination detection.

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
- A higher score means the response is better grounded and contains fewer hallucinations.
- A lower score means the response contains significant unsupported or contradictory claims.
- If every factual claim is supported, return:
  "unsupported_claims": []
- Include the specific unsupported statement whenever possible.
- Evaluate ONLY hallucinations.
- Do NOT evaluate relevance or completeness.
- Do NOT write markdown.
- Do NOT use ```json.
- Return ONLY JSON.
"""

        result = generate_response(prompt)

        parsed = parse_json_response(
            result,
            "reason"
        )

        parsed.setdefault("unsupported_claims", [])
        parsed.setdefault("reason", "")

        return parsed