from backend.llm import generate_response
from backend.utils import parse_json_response


class HallucinationJudge:

    def evaluate(
        self,
        response,
        reference="",
        retrieved_chunks=None
    ):

        retrieved_chunks = retrieved_chunks or []

        # -----------------------------
        # Prepare Evidence
        # -----------------------------

        rag_evidence = "\n\n".join(
            f"Source {i + 1} - {chunk['title']}:\n"
            f"{chunk['content']}"
            for i, chunk in enumerate(retrieved_chunks)
        )

        has_reference = bool(
            reference and reference.strip()
        )

        has_rag_evidence = bool(
            rag_evidence.strip()
        )

        # -----------------------------
        # No Grounding Available
        # -----------------------------

        if not has_reference and not has_rag_evidence:

            return {
                "score": None,
                "unsupported_claims": [],
                "reason":
                    "No reference answer or sufficiently relevant "
                    "retrieved evidence was available to determine "
                    "whether the response contains unsupported claims."
            }

        reference_text = (
            reference.strip()
            if has_reference
            else "Not provided."
        )

        rag_text = (
            rag_evidence
            if has_rag_evidence
            else "Not available."
        )

        # -----------------------------
        # Prompt
        # -----------------------------

        prompt = f"""
You are a factual grounding evaluator.

Determine whether factual claims in the AI Response are supported by
the Grounding Evidence.

AI Response:
{response}

Grounding Evidence:

Reference Answer:
{reference_text}

Retrieved Evidence:
{rag_text}

IMPORTANT DEFINITION:

A hallucination is a factual claim whose MEANING is contradicted by
the grounding evidence or cannot be supported by the grounding evidence.

Compare MEANING, not wording.

The following MUST NOT be considered hallucinations:

- paraphrases
- synonymous wording
- grammatical differences
- shorter or longer phrasing
- standard abbreviations
- standard acronyms

For example:

"RAG combines information retrieval with generative language models."

and

"Retrieval-Augmented Generation combines information retrieval with
generative language models."

express the SAME factual claim.

Therefore the first statement MUST NOT be marked unsupported when the
second statement is supported by the evidence.

Do not evaluate whether the response is detailed enough.
Do not evaluate completeness.
Do not evaluate relevance.
Do not penalize wording differences.

For each factual claim, ask only:

"Does the available evidence support the factual meaning of this claim?"

If YES:
The claim is supported.

If NO:
The claim is unsupported.

Return ONLY valid JSON:

{{
    "unsupported_claims": [
        "exact unsupported claim"
    ],
    "reason": "Brief explanation based only on factual grounding."
}}

If every factual claim is supported:

{{
    "unsupported_claims": [],
    "reason": "All factual claims are supported by the available grounding evidence."
}}

Do not return a score.
Do not use markdown.
Do not use JSON code fences.
"""

        # -----------------------------
        # Generate Evaluation
        # -----------------------------

        result = generate_response(prompt)

        parsed = parse_json_response(
            result,
            "reason"
        )

        unsupported_claims = parsed.get(
            "unsupported_claims",
            []
        )

        if not isinstance(unsupported_claims, list):
            unsupported_claims = []

        reason = parsed.get(
            "reason",
            ""
        )

        # -----------------------------
        # Deterministic Score
        # -----------------------------

        if not unsupported_claims:

            score = 10

        elif len(unsupported_claims) == 1:

            score = 7

        elif len(unsupported_claims) == 2:

            score = 4

        else:

            score = 2

        # -----------------------------
        # Final Result
        # -----------------------------

        return {
            "score": score,
            "unsupported_claims": unsupported_claims,
            "reason": reason
        }