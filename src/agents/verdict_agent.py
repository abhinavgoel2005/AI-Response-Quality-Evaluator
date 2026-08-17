from backend.llm import generate_response


class VerdictAgent:

    def __init__(self):

        # -----------------------------
        # Dimension Weights
        # -----------------------------

        self.weights = {
            "relevance": 0.20,
            "accuracy": 0.30,
            "hallucination": 0.25,
            "completeness": 0.25
        }


    # ==========================================
    # CONSOLIDATED SUMMARY GENERATOR
    # ==========================================

    def _generate_summary(
        self,
        relevance_result,
        accuracy_result,
        hallucination_result,
        completeness_result,
        overall_score,
        verdict,
        quality_gate_reasons
    ):

        score_display = (
            f"{overall_score}/10"
            if overall_score is not None
            else "N/A"
        )

        prompt = f"""
You are the Verdict Agent in an AI response quality evaluation system.

Your task is to produce a concise consolidated summary of the evaluation.

Evaluation Results:

Relevance:
Score: {relevance_result.get("score")}
Status: {relevance_result.get("status", "evaluated")}
Reason: {relevance_result.get("reason", "")}

Accuracy:
Score: {accuracy_result.get("score")}
Status: {accuracy_result.get("status", "evaluated")}
Evidence: {accuracy_result.get("evidence", "")}

Hallucination:
Score: {hallucination_result.get("score")}
Status: {hallucination_result.get("status", "evaluated")}
Reason: {hallucination_result.get("reason", "")}
Unsupported Claims:
{hallucination_result.get("unsupported_claims", [])}

Completeness:
Score: {completeness_result.get("score")}
Status: {completeness_result.get("status", "evaluated")}
Reason: {completeness_result.get("reason", "")}
Omissions:
{completeness_result.get("omissions", [])}

Overall Score:
{score_display}

Final Verdict:
{verdict}

Quality Gate Findings:
{quality_gate_reasons}

Write ONE concise paragraph summarizing the overall quality of the AI response.

Requirements:

- Synthesize the evaluation instead of repeating each agent's output.
- Explain the most important strengths and weaknesses.
- Mention unavailable grounding if accuracy or hallucination could not be verified.
- If one or more agents encountered errors, make it clear that the evaluation is incomplete.
- Explain why the final verdict is appropriate.
- Do not treat unavailable dimensions as poor-quality scores.
- Do not use individual agent headings.
- Do not list every score.
- Do not use bullet points.
- Do not repeat the quality gate findings word-for-word.
- Do not introduce factual claims that are not present in the evaluation results.
- Keep the summary between 2 and 4 sentences.
"""

        try:

            summary = generate_response(prompt)

            if summary and summary.strip():

                return summary.strip()

        except Exception as e:

            print("Verdict Summary Error:", e)


        # -----------------------------
        # Fallback Summary
        # -----------------------------

        if overall_score is None:

            return (
                "The response could only be partially evaluated because "
                "one or more quality dimensions were unavailable. "
                "The available results provide limited evidence about "
                "response quality, so a complete overall score could not "
                "be calculated. "
                f"The resulting verdict is {verdict}."
            )

        return (
            "The response was evaluated across the available quality "
            "dimensions. Its final assessment reflects the identified "
            "strengths, weaknesses, and any limitations in grounding "
            "evidence. "
            f"The resulting verdict is {verdict}."
        )


    # ==========================================
    # MAIN VERDICT EVALUATION
    # ==========================================

    def evaluate(
        self,
        relevance_result,
        accuracy_result,
        hallucination_result,
        completeness_result
    ):

        # -----------------------------
        # Extract Scores
        # -----------------------------

        relevance_score = relevance_result.get("score")
        accuracy_score = accuracy_result.get("score")
        hallucination_score = hallucination_result.get("score")
        completeness_score = completeness_result.get("score")

        scores = {
            "relevance": relevance_score,
            "accuracy": accuracy_score,
            "hallucination": hallucination_score,
            "completeness": completeness_score
        }


        # -----------------------------
        # Extract Agent Statuses
        # -----------------------------

        agent_results = {
            "relevance": relevance_result,
            "accuracy": accuracy_result,
            "hallucination": hallucination_result,
            "completeness": completeness_result
        }

        agent_statuses = {
            dimension: result.get("status", "evaluated")
            for dimension, result in agent_results.items()
        }


        # -----------------------------
        # Determine Unavailable Scores
        # -----------------------------

        unavailable_dimensions = [
            dimension
            for dimension, score in scores.items()
            if score is None
        ]

        error_dimensions = [
            dimension
            for dimension, status in agent_statuses.items()
            if status == "error"
        ]

        unverifiable_dimensions = [
            dimension
            for dimension, status in agent_statuses.items()
            if status == "unverifiable"
        ]


        # -----------------------------
        # Available Scores
        # -----------------------------

        available_scores = {
            dimension: score
            for dimension, score in scores.items()
            if score is not None
        }


        # -----------------------------
        # Overall Score
        # -----------------------------

        # The overall weighted score represents all four
        # evaluation dimensions.
        #
        # Therefore, if any agent encountered an actual
        # evaluation error, we do NOT renormalize the
        # remaining dimensions into a misleading /10 score.
        #
        # "unverifiable" is different from "error":
        # it represents a valid evaluation outcome where
        # grounding evidence was unavailable.

        if error_dimensions:

            overall_score = None

        elif len(available_scores) == len(self.weights):

            overall_score = round(
                sum(
                    scores[dimension] * self.weights[dimension]
                    for dimension in self.weights
                ),
                1
            )

        else:

            # One or more dimensions legitimately returned
            # no numeric score (for example, unverifiable).
            #
            # A complete four-dimensional score cannot be
            # calculated without changing its meaning.

            overall_score = None


        # -----------------------------
        # Extract Findings
        # -----------------------------

        unsupported_claims = (
            hallucination_result.get(
                "unsupported_claims",
                []
            )
            or []
        )

        omissions = (
            completeness_result.get(
                "omissions",
                []
            )
            or []
        )


        # -----------------------------
        # Quality Gates
        # -----------------------------

        quality_gate_reasons = []


        # -----------------------------
        # Base Verdict
        # -----------------------------

        if overall_score is None:

            # A clean Pass should never be produced from
            # an incomplete overall evaluation.

            verdict = "Needs Improvement"

        elif overall_score >= 8.0:

            verdict = "Pass"

        elif overall_score >= 5.0:

            verdict = "Needs Improvement"

        else:

            verdict = "Fail"


        # -----------------------------
        # Critical Score Failure
        # -----------------------------

        if (
            available_scores
            and min(available_scores.values()) <= 3
        ):

            verdict = "Fail"

            quality_gate_reasons.append(
                "At least one evaluation dimension "
                "scored 3 or below."
            )


        # -----------------------------
        # Critical Accuracy Failure
        # -----------------------------

        elif (
            accuracy_score is not None
            and accuracy_score <= 4
        ):

            verdict = "Fail"

            quality_gate_reasons.append(
                "Factual accuracy is critically low."
            )


        # -----------------------------
        # Critical Hallucination Failure
        # -----------------------------

        elif (
            hallucination_score is not None
            and hallucination_score <= 4
        ):

            verdict = "Fail"

            quality_gate_reasons.append(
                "The response contains significant "
                "unsupported or contradictory claims."
            )


        else:

            # -------------------------
            # Dimension Below 7
            # -------------------------

            if (
                available_scores
                and min(available_scores.values()) < 7
            ):

                if verdict == "Pass":

                    verdict = "Needs Improvement"

                quality_gate_reasons.append(
                    "At least one evaluation dimension "
                    "scored below 7."
                )


            # -------------------------
            # Unsupported Claims
            # -------------------------

            if unsupported_claims:

                if verdict == "Pass":

                    verdict = "Needs Improvement"

                quality_gate_reasons.append(
                    "Unsupported claims were detected."
                )


            # -------------------------
            # Omissions
            # -------------------------

            if omissions:

                if verdict == "Pass":

                    verdict = "Needs Improvement"

                quality_gate_reasons.append(
                    "The response does not address "
                    "all requested aspects."
                )


        # -----------------------------
        # Evaluation Error Gate
        # -----------------------------

        if error_dimensions:

            if verdict == "Pass":

                verdict = "Needs Improvement"

            quality_gate_reasons.append(
                "Some evaluation dimensions could not "
                "be completed because one or more judge "
                "agents encountered an error."
            )


        # -----------------------------
        # Grounding Availability Gate
        # -----------------------------

        if unverifiable_dimensions:

            if verdict == "Pass":

                verdict = "Needs Improvement"

            quality_gate_reasons.append(
                "Some evaluation dimensions could not "
                "be verified because sufficient grounding "
                "evidence was unavailable."
            )


        # -----------------------------
        # Other Missing Scores
        # -----------------------------

        other_unavailable = [
            dimension
            for dimension in unavailable_dimensions
            if dimension not in error_dimensions
            and dimension not in unverifiable_dimensions
        ]

        if other_unavailable:

            if verdict == "Pass":

                verdict = "Needs Improvement"

            quality_gate_reasons.append(
                "Some evaluation dimensions did not "
                "produce a numeric score."
            )


        # -----------------------------
        # Remove Duplicate Quality Gates
        # -----------------------------

        quality_gate_reasons = list(
            dict.fromkeys(quality_gate_reasons)
        )


        # -----------------------------
        # Generate Deterministic Summary
        # -----------------------------

        summary_parts = []

        if verdict == "Pass":
            summary_parts.append(
                "The AI response demonstrated strong overall quality "
                "across the evaluated dimensions."
            )

        elif verdict == "Needs Improvement":
            summary_parts.append(
                "The AI response was partially satisfactory but has "
                "areas that require improvement."
            )

        else:
            summary_parts.append(
                "The AI response has significant quality issues "
                "that require correction."
            )


        # Hallucination findings
        if hallucination_score is not None:

            if hallucination_score >= 8:
                summary_parts.append(
                    "The response was largely well grounded with "
                    "no significant unsupported claims identified."
                )

            elif hallucination_score >= 5:
                summary_parts.append(
                    "Some unsupported or insufficiently grounded "
                    "claims were identified."
                )

            else:
                summary_parts.append(
                    "Significant unsupported or contradictory claims "
                    "were identified."
                )


        # Accuracy findings
        if accuracy_score is not None and accuracy_score < 7:

            summary_parts.append(
                "Factual accuracy was below the preferred threshold."
            )


        # Completeness findings
        if completeness_score is not None and completeness_score < 7:

            summary_parts.append(
                "The response also omitted some aspects required "
                "for a complete answer."
            )


        # Grounding availability
        if unverifiable_dimensions:

            summary_parts.append(
                "Some dimensions could not be fully verified because "
                "sufficient grounding evidence was unavailable."
            )


        consolidated_summary = " ".join(summary_parts)


        # -----------------------------
        # Return Result
        # -----------------------------

        return {
            "overall_score": overall_score,

            "verdict": verdict,

            "consolidated_summary":
                consolidated_summary,

            # Keep temporarily for compatibility
            # with evaluator.py / existing UI.
            "consolidated_reasoning":
                consolidated_summary,

            "quality_gate_reasons":
                quality_gate_reasons,

            "weights":
                self.weights,

            "unavailable_dimensions":
                unavailable_dimensions,

            "unverifiable_dimensions":
                unverifiable_dimensions,

            "error_dimensions":
                error_dimensions
        }