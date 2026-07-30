from backend.batch_evaluator import BatchEvaluator


# ==========================================
# SIMPLE FILE WRAPPER
# ==========================================

class TestCSVFile:

    """
    Minimal wrapper that behaves like the
    uploaded file object expected by BatchEvaluator.
    """

    def __init__(self, path):

        self.path = path

        self.filename = path

        self.file = open(
            path,
            "rb"
        )


    def read(self):

        return self.file.read()


    def close(self):

        self.file.close()


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def display_score(agent_result):

    """
    Display a numeric score when available.

    If the agent result is unverifiable or does
    not contain a score, display N/A.
    """

    if not agent_result:

        return "N/A"


    score = agent_result.get("score")


    if score is None:

        return "N/A"


    return score


def display_summary(summary):

    """
    Safely display the Verdict Agent summary.
    """

    if not summary:

        return "No verdict summary available."


    return summary


# ==========================================
# MAIN TEST
# ==========================================

def main():

    print("\n" + "=" * 70)
    print("BATCH EVALUATION TEST")
    print("=" * 70)


    # --------------------------------------
    # Initialize Batch Evaluator
    # --------------------------------------

    batch_evaluator = BatchEvaluator()


    # --------------------------------------
    # Load Test CSV
    # --------------------------------------

    test_file = TestCSVFile(
        "test_batch.csv"
    )


    try:

        result = batch_evaluator.evaluate_csv(
            test_file
        )

    except Exception as e:

        print("\nBatch Evaluation Failed:")
        print(e)

        return

    finally:

        test_file.close()


    # ======================================
    # BATCH SUMMARY
    # ======================================

    print("\n" + "=" * 70)
    print("BATCH EVALUATION SUMMARY")
    print("=" * 70)


    print(
        "\nTotal Rows:",
        result.get(
            "total_rows",
            0
        )
    )


    print(
        "Evaluated Rows:",
        result.get(
            "evaluated_rows",
            0
        )
    )


    print(
        "Successful Rows:",
        result.get(
            "successful_rows",
            0
        )
    )


    print(
        "Partial Rows:",
        result.get(
            "partial_rows",
            0
        )
    )


    print(
        "Failed Rows:",
        result.get(
            "failed_rows",
            0
        )
    )


    print(
        "Rows Used for Aggregate Metrics:",
        result.get(
            "aggregated_rows",
            0
        )
    )


    # --------------------------------------
    # Average Score
    # --------------------------------------

    average_score = result.get(
        "average_score"
    )


    if average_score is None:

        print(
            "Average Score: N/A"
        )

    else:

        print(
            "Average Score:",
            average_score
        )


    # --------------------------------------
    # Verdict Distribution
    # --------------------------------------

    print(
        "Verdict Counts:",
        result.get(
            "verdict_counts",
            {}
        )
    )


    # ======================================
    # INDIVIDUAL RESULTS
    # ======================================

    print("\n" + "=" * 70)
    print("INDIVIDUAL RESULTS")
    print("=" * 70)


    results = result.get(
        "results",
        []
    )


    for item in results:

        print(
            f"\nRow "
            f"{item.get('row_number', '?')}"
        )

        print("-" * 70)


        # ----------------------------------
        # Basic Row Information
        # ----------------------------------

        print(
            "Question:",
            item.get(
                "question",
                ""
            )
        )


        status = item.get(
            "status",
            "unknown"
        )


        print(
            "Status:",
            status.upper()
        )


        # ==================================
        # ERROR ROW
        # ==================================

        if status == "error":

            print(
                "Error:",
                item.get(
                    "error",
                    "Unknown error."
                )
            )

            continue


        # ==================================
        # SUCCESS / PARTIAL ROW
        # ==================================

        evaluation = item.get(
            "evaluation",
            {}
        )


        relevance = evaluation.get(
            "relevance",
            {}
        )


        accuracy = evaluation.get(
            "accuracy",
            {}
        )


        hallucination = evaluation.get(
            "hallucination",
            {}
        )


        completeness = evaluation.get(
            "completeness",
            {}
        )


        # ----------------------------------
        # Agent Scores
        # ----------------------------------

        print(
            "Relevance:",
            display_score(
                relevance
            )
        )


        print(
            "Accuracy:",
            display_score(
                accuracy
            )
        )


        print(
            "Hallucination:",
            display_score(
                hallucination
            )
        )


        print(
            "Completeness:",
            display_score(
                completeness
            )
        )


        # ----------------------------------
        # Overall Score
        # ----------------------------------

        overall_score = evaluation.get(
            "overall_score"
        )


        if overall_score is None:

            print(
                "Overall Score: N/A"
            )

        else:

            print(
                "Overall Score:",
                overall_score
            )


        # ----------------------------------
        # Verdict
        # ----------------------------------

        verdict = evaluation.get(
            "verdict"
        )


        if verdict:

            print(
                "Verdict:",
                verdict
            )

        else:

            print(
                "Verdict: N/A"
            )


        # ----------------------------------
        # Verdict Summary
        # ----------------------------------

        verdict_summary = evaluation.get(
            "consolidated_summary"
        )


        print(
            "Verdict Summary:",
            display_summary(
                verdict_summary
            )
        )


        # ----------------------------------
        # Quality Gates
        # ----------------------------------

        quality_gates = evaluation.get(
            "quality_gate_reasons",
            []
        )


        if quality_gates:

            print(
                "Quality Gates:"
            )


            for gate in quality_gates:

                print(
                    "  -",
                    gate
                )


        else:

            print(
                "Quality Gates: None"
            )


        # ----------------------------------
        # Agent Execution Status
        # ----------------------------------

        print(
            "Agent Statuses:"
        )


        print(
            "  Relevance:",
            relevance.get(
                "status",
                "evaluated"
            )
        )


        print(
            "  Accuracy:",
            accuracy.get(
                "status",
                "evaluated"
            )
        )


        print(
            "  Hallucination:",
            hallucination.get(
                "status",
                "evaluated"
            )
        )


        print(
            "  Completeness:",
            completeness.get(
                "status",
                "evaluated"
            )
        )


    # ======================================
    # TEST COMPLETED
    # ======================================

    print("\n" + "=" * 70)
    print("BATCH TEST COMPLETED")
    print("=" * 70)


# ==========================================
# ENTRY POINT
# ==========================================

if __name__ == "__main__":

    main()