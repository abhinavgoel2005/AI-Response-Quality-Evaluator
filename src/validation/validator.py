from backend.evaluator import ResponseEvaluator
from backend.llm import generate_response

from validation.dataset_loader import load_dataset
from validation.report import generate_report


# ==========================================================
# Validation Configuration
# ==========================================================

#DATASET = "benchmark_data.json"
DATASET = "truthfulqa.json"

SAMPLE_SIZE = 3

#SAMPLING_STRATEGY = "all"
SAMPLING_STRATEGY = "sequential"
# SAMPLING_STRATEGY = "random"


# ==========================================================
# Evaluate a Single Sample
# ==========================================================

def evaluate_sample(evaluator, sample):

    # Use existing response if available
    if "response" in sample:

        response = sample["response"]

    # Otherwise generate a new response using Gemini
    else:

        print("Generating response from Gemini...")

        response = generate_response(
            sample["question"]
        )

    # Evaluate the response
    evaluation = evaluator.evaluate(

        sample["question"],

        response,

        sample["reference"]

    )

    return {

        "id": sample["id"],

        "dataset": sample.get("dataset"),

        "category": sample.get("category"),

        "question": sample["question"],

        "response": response,

        "reference": sample["reference"],

        "evaluation": evaluation

    }


# ==========================================================
# Main Validation Pipeline
# ==========================================================

def main():

    evaluator = ResponseEvaluator()

    samples = load_dataset(

        filename=DATASET,

        sample_size=SAMPLE_SIZE,

        strategy=SAMPLING_STRATEGY

    )

    results = []

    print("=" * 60)
    print("AI RESPONSE QUALITY EVALUATOR")
    print("Validation Started")
    print("=" * 60)

    print(f"Dataset  : {DATASET}")
    print(f"Samples  : {len(samples)}")
    print(f"Strategy : {SAMPLING_STRATEGY}")
    print("=" * 60)

    for index, sample in enumerate(samples, start=1):

        print(
            f"\nEvaluating Sample {index}/{len(samples)} "
            f"(ID: {sample['id']})"
        )

        if sample.get("category"):

            print(f"Category : {sample['category']}")

        result = evaluate_sample(

            evaluator,

            sample

        )

        results.append(result)

        print("Completed ✓")

    report_path = generate_report(results)

    print("\n" + "=" * 60)
    print("Validation Completed Successfully!")
    print("=" * 60)

    print(f"Report generated successfully!")

    print(report_path)

    return results


# ==========================================================
# Entry Point
# ==========================================================

if __name__ == "__main__":

    main()