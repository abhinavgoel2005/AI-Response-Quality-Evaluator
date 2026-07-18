import os

from datetime import datetime


def generate_report(results):

    reports_dir = os.path.join(
        os.path.dirname(__file__),
        "reports"
    )

    os.makedirs(reports_dir, exist_ok=True)

    dataset_name = results[0].get("dataset") or "benchmark"

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    report_filename = (
        f"{dataset_name.lower()}_{timestamp}.txt"
    )

    report_path = os.path.join(
        reports_dir,
        report_filename
    )

    # =====================================================
    # Calculate Statistics
    # =====================================================

    relevance_scores = [
        r["evaluation"]["relevance"]["score"]
        for r in results
    ]

    accuracy_scores = [
        r["evaluation"]["accuracy"]["score"]
        for r in results
    ]

    hallucination_scores = [
        r["evaluation"]["hallucination"]["score"]
        for r in results
    ]

    overall_scores = [
        r["evaluation"]["overall_score"]
        for r in results
    ]

    avg_relevance = sum(relevance_scores) / len(results)

    avg_accuracy = sum(accuracy_scores) / len(results)

    avg_hallucination = (
        sum(hallucination_scores) / len(results)
    )

    avg_overall = sum(overall_scores) / len(results)

    highest = max(overall_scores)

    lowest = min(overall_scores)

    generated_time = datetime.now().strftime(
        "%d-%m-%Y %I:%M %p"
    )

    # =====================================================
    # Write Report
    # =====================================================

    with open(report_path, "w", encoding="utf-8") as report:

        report.write("=" * 70 + "\n")
        report.write("AI RESPONSE QUALITY EVALUATION REPORT\n")
        report.write("=" * 70 + "\n\n")

        report.write(f"Generated On : {generated_time}\n")
        report.write(f"Dataset      : {dataset_name}\n")
        report.write(f"Samples      : {len(results)}\n\n")

        report.write("=" * 70 + "\n")
        report.write("SUMMARY\n")
        report.write("=" * 70 + "\n\n")

        report.write(
            f"Average Relevance Score      : "
            f"{avg_relevance:.2f}/10\n"
        )

        report.write(
            f"Average Accuracy Score       : "
            f"{avg_accuracy:.2f}/10\n"
        )

        report.write(
            f"Average Hallucination Score  : "
            f"{avg_hallucination:.2f}/10\n"
        )

        report.write(
            f"Average Overall Score        : "
            f"{avg_overall:.2f}/10\n\n"
        )

        report.write(
            f"Highest Overall Score        : "
            f"{highest:.2f}\n"
        )

        report.write(
            f"Lowest Overall Score         : "
            f"{lowest:.2f}\n\n"
        )

        # =================================================

        for result in results:

            report.write("=" * 70 + "\n")

            report.write(
                f"Sample ID : {result['id']}\n"
            )

            if result.get("category"):

                report.write(
                    f"Category  : "
                    f"{result['category']}\n"
                )

            report.write("=" * 70 + "\n\n")

            report.write(
                f"Question:\n"
                f"{result['question']}\n\n"
            )

            report.write(
                f"Generated Response:\n"
                f"{result['response']}\n\n"
            )

            report.write(
                f"Reference Answer:\n"
                f"{result['reference']}\n\n"
            )

            report.write("-" * 50 + "\n")
            report.write("RELEVANCE\n")
            report.write("-" * 50 + "\n")

            report.write(
                f"Score : "
                f"{result['evaluation']['relevance']['score']}/10\n\n"
            )

            report.write(
                f"Reason:\n"
                f"{result['evaluation']['relevance']['reason']}\n\n"
            )

            report.write("-" * 50 + "\n")
            report.write("ACCURACY\n")
            report.write("-" * 50 + "\n")

            report.write(
                f"Score : "
                f"{result['evaluation']['accuracy']['score']}/10\n\n"
            )

            report.write(
                f"Evidence:\n"
                f"{result['evaluation']['accuracy']['evidence']}\n\n"
            )

            report.write("-" * 50 + "\n")
            report.write("HALLUCINATION\n")
            report.write("-" * 50 + "\n")

            report.write(
                f"Score : "
                f"{result['evaluation']['hallucination']['score']}/10\n\n"
            )

            report.write(
                f"Reason:\n"
                f"{result['evaluation']['hallucination']['reason']}\n\n"
            )

            report.write(
                "Unsupported Claims:\n"
            )

            unsupported = result["evaluation"][
                "hallucination"
            ]["unsupported_claims"]

            if unsupported:

                for claim in unsupported:

                    report.write(
                        f"  • {claim}\n"
                    )

            else:

                report.write(
                    "  ✓ No unsupported claims detected.\n"
                )

            report.write("\n")

            report.write(
                f"Overall Score : "
                f"{result['evaluation']['overall_score']:.2f}/10\n\n"
            )

    return report_path