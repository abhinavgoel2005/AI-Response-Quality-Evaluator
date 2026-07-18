import json
import os

import pandas as pd

def parse_answers(text):

    if not isinstance(text, str):
        return []

    return [
        answer.strip()
        for answer in text.split(";")
        if answer.strip()
    ]

def convert_truthfulqa():

    current_dir = os.path.dirname(__file__)

    raw_path = os.path.join(
        current_dir,
        "datasets",
        "raw",
        "TruthfulQA.csv"
    )

    output_path = os.path.join(
        current_dir,
        "datasets",
        "truthfulqa.json"
    )

    df = pd.read_csv(raw_path)

    output = []

    for index, row in df.iterrows():

        output.append({

            "id": index + 1,

            "dataset": "TruthfulQA",

            "category": row["Category"],

            "question": row["Question"],

            "reference": row["Best Answer"],

            "correct_answers": parse_answers(
                row["Correct Answers"]
            ),

            "incorrect_answers": parse_answers(
                row["Incorrect Answers"]
            )

        })

    with open(output_path, "w", encoding="utf-8") as file:

        json.dump(
            output,
            file,
            indent=4,
            ensure_ascii=False
        )

    print(f"Converted {len(output)} questions.")

    print(output_path)


if __name__ == "__main__":

    convert_truthfulqa()