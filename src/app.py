from flask import (
    Flask,
    render_template,
    request
)

from backend.evaluator import ResponseEvaluator
from backend.batch_evaluator import BatchEvaluator


# ==========================================
# FLASK APPLICATION
# ==========================================

app = Flask(__name__)


# ==========================================
# EVALUATORS
# ==========================================

evaluator = ResponseEvaluator()

batch_evaluator = BatchEvaluator()


# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():

    return render_template(
        "index.html",
        active_mode="single"
    )


# ==========================================
# SINGLE RESPONSE EVALUATION
# ==========================================

@app.route(
    "/evaluate",
    methods=["POST"]
)
def evaluate():

    # --------------------------------------
    # Get Form Input
    # --------------------------------------

    question = request.form.get(
        "question",
        ""
    )

    response = request.form.get(
        "response",
        ""
    )

    reference = request.form.get(
        "reference",
        ""
    )


    # --------------------------------------
    # Run Evaluation
    # --------------------------------------

    results = evaluator.evaluate(
        question,
        response,
        reference
    )


    # --------------------------------------
    # Render Results
    # --------------------------------------

    return render_template(
        "index.html",

        active_mode="single",

        question=question,
        response=response,
        reference=reference,

        results=results
    )


# ==========================================
# BATCH EVALUATION
# ==========================================

@app.route(
    "/batch-evaluate",
    methods=["POST"]
)
def batch_evaluate():

    # --------------------------------------
    # Get Uploaded CSV
    # --------------------------------------

    file = request.files.get(
        "batch_file"
    )


    # --------------------------------------
    # No File Selected
    # --------------------------------------

    if not file or not file.filename:

        return render_template(
            "index.html",

            active_mode="batch",

            batch_error=(
                "Please select a CSV file "
                "before starting batch evaluation."
            )
        )


    # --------------------------------------
    # Validate File Extension
    # --------------------------------------

    if not file.filename.lower().endswith(
        ".csv"
    ):

        return render_template(
            "index.html",

            active_mode="batch",

            batch_filename=file.filename,

            batch_error=(
                "Invalid file format. "
                "Please upload a CSV file."
            )
        )


    # --------------------------------------
    # Run Batch Evaluation
    # --------------------------------------

    try:

        batch_results = (
            batch_evaluator.evaluate_csv(
                file
            )
        )


    except ValueError as e:

        # Validation errors from BatchEvaluator:
        #
        # - missing columns
        # - empty CSV
        # - invalid encoding
        # - missing question/response header
        # etc.

        return render_template(
            "index.html",

            active_mode="batch",

            batch_filename=file.filename,

            batch_error=str(e)
        )


    except Exception as e:

        print(
            "Batch Evaluation Error:",
            e
        )


        return render_template(
            "index.html",

            active_mode="batch",

            batch_filename=file.filename,

            batch_error=(
                "Batch evaluation could not be "
                "completed at the moment."
            )
        )


    # --------------------------------------
    # Render Batch Results
    # --------------------------------------

    return render_template(
        "index.html",

        active_mode="batch",

        batch_filename=file.filename,

        batch_results=batch_results
    )


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )