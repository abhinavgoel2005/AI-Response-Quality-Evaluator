from backend.utils import parse_json_response
from backend.llm import generate_response


class AccuracyJudge:

    def evaluate(self, question, response, reference="", retrieved_chunks=None):

        retrieved_chunks = retrieved_chunks or []

        # Convert retrieved documents into readable evidence for the LLM
        rag_evidence = "\n\n".join(
            f"Source {i + 1} - {chunk['title']}:\n{chunk['content']}"
            for i, chunk in enumerate(retrieved_chunks)
        )

        if not rag_evidence:
            rag_evidence = "No retrieved evidence available."

        if not reference or not reference.strip():
            reference = "No reference answer provided."

        prompt = f"""
You are an expert evaluator of AI responses.

Evaluate ONLY factual accuracy.

Question:
{question}

AI Response:
{response}

Reference Answer:
{reference}

Retrieved Evidence:
{rag_evidence}

Evaluate the factual correctness of the AI response using the available
reference answer and retrieved evidence.

When a reference answer is provided, use it as important evidence.
Use the retrieved evidence as additional grounding.

If no reference answer is provided, evaluate factual accuracy using the
retrieved evidence.

Do not assume facts that are not supported by the available evidence.

Return ONLY valid JSON.

The JSON format must be:

{{
    "score": number,
    "evidence": "Brief explanation of which facts are supported or incorrect"
}}

Rules:

- Score between 1 and 10.
- Evaluate ONLY factual accuracy.
- Do not evaluate relevance.
- Do not separately score hallucinations.
- Base the evaluation on the supplied evidence.
- Do not write markdown.
- Do not use ```json.
- Return ONLY JSON.
"""

        result = generate_response(prompt)

        return parse_json_response(
            result,
            "evidence"
        )