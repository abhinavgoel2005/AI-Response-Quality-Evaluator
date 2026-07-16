from backend.evaluator import ResponseEvaluator
from validation.benchmark_data import benchmark_samples


evaluator = ResponseEvaluator()

results = []

for sample in benchmark_samples:

    evaluation = evaluator.evaluate(

        sample["question"],

        sample["response"],

        sample["reference"]

    )

    results.append({

        "id": sample["id"],

        "question": sample["question"],

        "evaluation": evaluation

    })


print(results)