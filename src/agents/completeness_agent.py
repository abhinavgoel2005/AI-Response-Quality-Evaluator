from backend.llm import generate_response
from backend.utils import parse_json_response


class CompletenessJudge:

    def evaluate(self, question, response):

        prompt = f"""
You are an expert evaluator of AI-generated responses.

Evaluate ONLY the completeness of the AI response relative
to what the user's question actually requests.

Question:
{question}

AI Response:
{response}

Determine whether the response addresses all explicit and
reasonably necessary aspects required by the question.

IMPORTANT EVALUATION PRINCIPLES:

1. Judge completeness relative to the user's request, not
   relative to everything that could possibly be said about
   the topic.

2. Do NOT require additional details, examples, benefits,
   limitations, history, causes, applications, or technical
   depth unless:
   - the question explicitly requests them, or
   - they are necessary to answer the question meaningfully.

3. For simple definition questions such as:
   "What is X?"
   a concise and meaningful definition can be fully complete.

4. Do not penalize a response merely for being concise.

5. If the question contains multiple explicit requirements,
   verify each requirement separately.

For example:

Question:
"What is RAG?"

A concise, meaningful definition of RAG may receive a high
completeness score without discussing benefits, limitations,
examples, or architecture.

Question:
"Explain RAG, give two benefits, and mention one limitation."

The response must:
- explain RAG,
- provide two benefits,
- provide one limitation.

Missing any requested component should reduce the score.

Question:
"Compare supervised and unsupervised learning."

The response must meaningfully discuss both concepts and
provide the requested comparison.

Return ONLY valid JSON using this format:

{{
    "score": number,
    "omissions": [
        "specific missing aspect"
    ],
    "reason": "short explanation"
}}

Scoring guidance:

9-10:
All requested aspects are adequately addressed.

7-8:
Mostly complete, with only minor omissions.

4-6:
Partially complete; one or more important requested aspects
are missing.

1-3:
Critically incomplete or fails to meaningfully answer major
parts of the question.

Rules:

- Score must be between 1 and 10.
- List only genuine omissions required by the question.
- Do not invent requirements that the question did not ask for.
- If nothing important is missing, return:
  "omissions": []
- Evaluate completeness only.
- Do not evaluate factual accuracy.
- Do not evaluate hallucinations.
- Do not use markdown.
- Return ONLY JSON.
"""

        result = generate_response(prompt)

        parsed = parse_json_response(
            result,
            "reason"
        )

        parsed.setdefault(
            "omissions",
            []
        )

        parsed.setdefault(
            "reason",
            ""
        )

        return parsed