from backend.llm import generate_response
from backend.utils import parse_json_response


class RelevanceJudge:

    def evaluate(self, question, response):

        # -------------------------------------------------
        # Relevance Evaluation Prompt
        # -------------------------------------------------

        prompt = f"""
You are an expert evaluator of AI-generated responses.

Your task is to evaluate ONLY RELEVANCE.

Question:
{question}

AI Response:
{response}

Definition of relevance:

Relevance measures how directly the AI response addresses the topic,
intent, and request expressed in the question.

Evaluate whether the response is focused on what the user asked about.

IMPORTANT:

Relevance is NOT completeness.

A response may be highly relevant even if it does not fully answer
every part of the question.

For example:

Question:
"Explain RAG and mention two benefits and one limitation."

Response:
"RAG combines information retrieval with generative language models."

This response is relevant because it directly discusses the requested
topic, even though it is incomplete.

Missing requested details should be evaluated by the Completeness Judge,
NOT by the Relevance Judge.

Also:

- Do NOT evaluate factual accuracy.
- Do NOT evaluate hallucinations.
- Do NOT evaluate whether claims are supported by evidence.
- Do NOT penalize a response for being brief.
- Do NOT penalize missing details if the content that is present
  directly addresses the question.
- Do NOT reward additional detail merely because the response is long.

Evaluate whether the content that IS PRESENT is relevant to the question.

Scoring guide:

9-10:
The response directly addresses the question and stays focused on the
requested topic.

7-8:
The response is mostly relevant but contains some unnecessary,
tangential, or weakly related information.

4-6:
The response partially addresses the question but contains substantial
irrelevant or off-topic content.

1-3:
The response barely addresses the question or is mostly unrelated.

Return ONLY valid JSON in this format:

{{
    "score": number,
    "reason": "Brief explanation of how directly the response addresses the question."
}}

Output Rules:

- Score must be between 1 and 10.
- Evaluate ONLY relevance.
- Do NOT discuss completeness.
- Do NOT discuss missing information.
- Do NOT discuss factual accuracy.
- Do NOT discuss hallucinations.
- Do NOT use markdown.
- Do NOT use JSON code fences.
- Return ONLY valid JSON.
"""

        # -------------------------------------------------
        # Generate Evaluation
        # -------------------------------------------------

        result = generate_response(prompt)

        # -------------------------------------------------
        # Parse Response
        # -------------------------------------------------

        parsed = parse_json_response(
            result,
            "reason"
        )

        parsed.setdefault(
            "reason",
            ""
        )

        return parsed