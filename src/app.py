from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/evaluate", methods=["POST"])
def evaluate():

    question = request.form["question"]
    response = request.form["response"]
    reference = request.form["reference"]

    # Placeholder values (Milestone 2 agents will replace these)
    results = {
        "relevance": {
            "score": None,
            "reason": None
        },
        "accuracy": {
            "score": None,
            "reason": None,
            "evidence": None
        },
        "hallucination": {
            "score": None,
            "reason": None,
            "claims": None
        }
    }

    return render_template(
        "index.html",
        question=question,
        response=response,
        reference=reference,
        results=results
    )


if __name__ == "__main__":
    app.run(debug=True)