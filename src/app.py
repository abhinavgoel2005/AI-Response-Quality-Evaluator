from flask import Flask, render_template, request
from backend.evaluator import ResponseEvaluator

app = Flask(__name__)
evaluator = ResponseEvaluator()

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/evaluate", methods=["POST"])
def evaluate():

    question = request.form["question"]
    response = request.form["response"]
    reference = request.form["reference"]

    results = evaluator.evaluate(
    question,
    response,
    reference
    )

    return render_template(
        "index.html",
        question=question,
        response=response,
        reference=reference,
        results=results
    )


if __name__ == "__main__":
    app.run(debug=True)