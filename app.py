from flask import Flask, render_template, request
from backend.retrieval import retrieve

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
def submit():

    question = request.form["question"]
    ai_response = request.form["response"]
    reference = request.form["reference"]

    retrieved_chunks = retrieve(question)

    return render_template(
        "index.html",
        question=question,
        ai_response=ai_response,
        reference=reference,
        retrieved_chunks=retrieved_chunks
    )


if __name__ == "__main__":
    app.run(debug=True)