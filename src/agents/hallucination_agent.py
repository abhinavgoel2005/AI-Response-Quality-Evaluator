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
                "contradicted_claims": [],
                "reason":
                    "No reference answer or sufficiently relevant "
                    "retrieved evidence was available to determine "
                    "whether the response contains unsupported claims.",
                "grounded": None
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

        grounding_context = f"""
        REFERENCE ANSWER:
        {reference_text}

        RETRIEVED EVIDENCE:
        {rag_text}
        """

        # -----------------------------
        # Prompt
        # -----------------------------

        prompt = f"""
You are a factual grounding evaluator for an AI response evaluation system.

Your task is to evaluate whether the factual claims made in the AI Response
are supported by the available Grounding Evidence.

Do NOT evaluate relevance, completeness, writing quality, or style.

==================================================
AI-GENERATED RESPONSE
==================================================

{response}

==================================================
GROUNDING EVIDENCE
==================================================

Reference Answer:
{reference_text}

Retrieved Evidence:
{rag_text}

==================================================
CLAIM EVALUATION RULES
==================================================

For each meaningful factual claim in the AI Response, determine its grounding
status.

1. SUPPORTED
A claim is SUPPORTED when the available evidence supports its factual meaning.

2. UNSUPPORTED
A claim is UNSUPPORTED when the available evidence does not provide enough
information to support or verify the claim.

3. CONTRADICTED
A claim is CONTRADICTED when the available evidence clearly conflicts with
the claim.

IMPORTANT:

Compare MEANING, not exact wording.

Do NOT mark a claim as unsupported merely because:
- it uses different wording
- it is a paraphrase
- it uses synonyms
- the sentence structure is different
- it is shorter or longer
- it uses a standard abbreviation or acronym

For example:

"Overfitting happens when a model memorizes training data and performs poorly
on unseen data."

and

"Overfitting occurs when a model learns the training data too closely and
fails to generalize."

express essentially the same factual meaning and should be considered
SUPPORTED if the evidence supports that meaning.

==================================================
CLAIM SEVERITY
==================================================

For every unsupported or contradicted claim, determine its severity.

MAJOR:
- The claim is central to the answer.
- The claim defines the main concept incorrectly.
- The claim gives an important factual explanation.
- The claim substantially changes the meaning of the answer.
- The claim is a major fabricated or contradictory fact.

MINOR:
- The claim is a small additional detail.
- The claim does not substantially change the main meaning of the answer.
- The claim is a minor unsupported factual addition.

For example:

Question:
"What is cloud computing?"

Response:
"Cloud computing means storing files on Google Drive."

The claim is MAJOR because it gives an incorrect and overly narrow definition
of the main concept.

==================================================
IMPORTANT SCORING GUIDANCE
==================================================

Do NOT assign a hallucination score yourself.

Only identify:
- factual claims
- their grounding status
- their severity

The final hallucination score will be calculated deterministically by the
application.

A perfectly grounded response should contain no unsupported or contradicted
claims.

==================================================
OUTPUT FORMAT
==================================================

Return ONLY valid JSON.

Use exactly this structure:

{{
    "claim_analysis": [
        {{
            "claim": "factual claim from the response",
            "status": "supported | unsupported | contradicted",
            "severity": "major | minor"
        }}
    ],
    "unsupported_claims": [
        "unsupported claim"
    ],
    "contradicted_claims": [
        "contradicted claim"
    ],
    "reason": "Short explanation of the overall grounding quality."
}}

Rules:

- Include meaningful factual claims in claim_analysis.
- Use "supported" for claims whose meaning is supported by the evidence.
- Use "unsupported" when the evidence cannot support the claim.
- Use "contradicted" only when the evidence clearly conflicts with the claim.
- Do not confuse lack of evidence with contradiction.
- Do not penalize valid paraphrasing.
- Mark the central or defining incorrect claim as "major".
- Keep unsupported_claims and contradicted_claims concise.
- Return valid JSON only.
- Do not use markdown.
- Do not use JSON code fences.
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

        contradicted_claims = parsed.get(
            "contradicted_claims",
            []
        )

        if not isinstance(contradicted_claims, list):
            contradicted_claims = []

        reason = parsed.get(
            "reason",
            ""
        )
        # -----------------------------
        # Claim Analysis
        # -----------------------------

        claim_analysis = parsed.get(
            "claim_analysis",
            []
        )

        if not isinstance(claim_analysis, list):
            claim_analysis = []

        contradicted_claims = parsed.get(
            "contradicted_claims",
            []
        )

        if not isinstance(contradicted_claims, list):
            contradicted_claims = []

        # -----------------------------
        # Deterministic Hallucination Score
        # -----------------------------

        major_unsupported = 0
        minor_unsupported = 0
        major_contradicted = 0
        minor_contradicted = 0

        for claim in claim_analysis:

            if not isinstance(claim, dict):
                continue

            status = str(
                claim.get("status", "")
            ).strip().lower()

            severity = str(
                claim.get("severity", "minor")
            ).strip().lower()

            if status == "unsupported":

                if severity == "major":
                    major_unsupported += 1
                else:
                    minor_unsupported += 1

            elif status == "contradicted":

                if severity == "major":
                    major_contradicted += 1
                else:
                    minor_contradicted += 1


        # Start with a perfectly grounded score.
        score = 10

        # Major contradicted claims are the most serious.
        score -= major_contradicted * 7

        # Major unsupported claims significantly reduce grounding quality.
        score -= major_unsupported * 5

        # Minor contradictions are serious, but less damaging.
        score -= minor_contradicted * 3

        # Minor unsupported claims have a smaller impact.
        score -= minor_unsupported * 2

        # Keep score within the valid 0-10 range.
        score = max(0, min(10, score))

        # -----------------------------
        # Final Result
        # -----------------------------

        # Derive claim lists from claim_analysis
        # so that claim_analysis remains the single
        # source of truth for grounding decisions.

        unsupported_claims = [
            claim.get("claim", "")
            for claim in claim_analysis
            if isinstance(claim, dict)
            and str(claim.get("status", "")).strip().lower() == "unsupported"
            and claim.get("claim")
        ]

        contradicted_claims = [
            claim.get("claim", "")
            for claim in claim_analysis
            if isinstance(claim, dict)
            and str(claim.get("status", "")).strip().lower() == "contradicted"
            and claim.get("claim")
        ]

        grounded = (
            len(unsupported_claims) == 0
            and len(contradicted_claims) == 0
        )

        return {
            "score": score,
            "unsupported_claims": unsupported_claims,
            "contradicted_claims": contradicted_claims,
            "claim_analysis": claim_analysis,
            "reason": reason,
            "grounded": grounded
        }