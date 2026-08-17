from flask import (
    Flask,
    render_template,
    request,
    send_file
)
import os
import json
from backend.evaluator import ResponseEvaluator
from backend.batch_evaluator import BatchEvaluator
from backend.pdf_report import PDFReportGenerator

# ==========================================
# FLASK APPLICATION
# ==========================================

app = Flask(__name__)

latest_batch_results = None


# ==========================================
# EVALUATORS
# ==========================================

evaluator = None
batch_evaluator = None


def get_evaluator():
    global evaluator

    if evaluator is None:
        evaluator = ResponseEvaluator()

    return evaluator


def get_batch_evaluator():
    global batch_evaluator

    if batch_evaluator is None:
        batch_evaluator = BatchEvaluator()

    return batch_evaluator


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

    results = get_evaluator().evaluate(
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

    global latest_batch_results

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
            get_batch_evaluator().evaluate_csv(
                file
            )
        )

        latest_batch_results = batch_results


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

    analytics_json = json.dumps(
        batch_results["analytics"]
    )

    verdict_json = json.dumps(
        batch_results["verdict_counts"]
    )

    return render_template(
        "index.html",

        active_mode="batch",

        batch_filename=file.filename,

        batch_results=batch_results,

        analytics_json=analytics_json,

        verdict_json=verdict_json
    )

# ==========================================
# DOWNLOAD PDF REPORT
# ==========================================

@app.route("/download-report")

def download_report():

    global latest_batch_results

    if latest_batch_results is None:

        return "No batch evaluation available.", 400

    generator = PDFReportGenerator()

    output_path = os.path.join(
        app.root_path,
        "batch_evaluation_report.pdf"
    )

    generator.generate_report(

        latest_batch_results,

        output_path

    )

    return send_file(

        output_path,

        as_attachment=True,

        download_name="AI_Response_Quality_Report.pdf"

    )

# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(
        debug=True
    )

