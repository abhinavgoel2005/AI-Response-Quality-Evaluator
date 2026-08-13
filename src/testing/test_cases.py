"""
End-to-End Test Cases

Development of AI Response Validation System
with Hallucination Detection Assistance
"""

import os
import time

from io import BytesIO
from werkzeug.datastructures import FileStorage

from backend.batch_evaluator import BatchEvaluator
from backend.pdf_report import PDFReportGenerator

# ==================================================
# Helper Functions
# ==================================================

def project_root():

    return os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )


def sample_dataset():

    return os.path.join(
        os.path.dirname(__file__),
        "test_batch_extended.csv"
    )


def load_csv():

    csv_path = sample_dataset()

    with open(csv_path, "rb") as f:
        file_data = f.read()

    return FileStorage(
        stream=BytesIO(file_data),
        filename=os.path.basename(csv_path),
        content_type="text/csv"
    )


def sample_small_dataset():

    return os.path.join(
        os.path.dirname(__file__),
        "test_batch_small.csv"
    )


def load_small_csv():

    small_csv_path = sample_small_dataset()

    with open(small_csv_path, "rb") as f:
        file_data = f.read()

    return FileStorage(
        stream=BytesIO(file_data),
        filename=os.path.basename(small_csv_path),
        content_type="text/csv"
    )

# ==================================================
# Test 1
# Batch Evaluation
# ==================================================

def test_batch_evaluation():

    start = time.perf_counter()

    results = get_batch_results()

    execution_time = round(

        time.perf_counter() - start,

        3

    )

    assert results is not None

    assert "results" in results

    assert len(results["results"]) > 0

    return {

        "status": "PASS",

        "execution_time": execution_time,

        "rows_processed": results["total_rows"],

        "successful_rows": results["successful_rows"]

    }

# ==================================================
# Test 2
# Analytics Generation
# ==================================================

def test_analytics_generation():

    results = get_batch_results()

    analytics = results.get(

        "analytics"

    )

    assert analytics is not None

    required_fields = [

        "average_relevance",

        "average_accuracy",

        "average_hallucination",

        "average_completeness",

        "hallucination_frequency",

        "best_dimension",

        "weakest_dimension",

        "quality_trend"

    ]

    for field in required_fields:

        assert field in analytics

    return {

        "status": "PASS",

        "analytics_verified": True

    }

# ==================================================
# Test 3
# Verdict Generation
# ==================================================

def test_verdict_generation():

    results = get_batch_results()

    evaluations = results.get(

        "results",

        []

    )

    verdict_count = 0

    for row in evaluations:

        if row.get("status") != "success":

            continue

        evaluation = row.get(

            "evaluation",

            {}

        )

        assert "verdict" in evaluation

        assert evaluation["verdict"] in [

            "Pass",

            "Needs Improvement",

            "Fail"

        ]

        verdict_count += 1

    assert verdict_count > 0

    return {

        "status": "PASS",

        "verified_verdicts": verdict_count

    }

# ==================================================
# Test 4
# Batch Statistics Validation
# ==================================================

def test_batch_statistics():

    results = get_batch_results()

    required_fields = [

        "total_rows",

        "evaluated_rows",

        "successful_rows",

        "partial_rows",

        "failed_rows",

        "aggregated_rows",

        "average_score",

        "verdict_counts"

    ]

    for field in required_fields:

        assert field in results

    total = (

        results["successful_rows"]

        + results["partial_rows"]

        + results["failed_rows"]

    )

    assert total == results["total_rows"]

    assert results["aggregated_rows"] <= results["evaluated_rows"]

    return {

        "status": "PASS",

        "rows": results["total_rows"],

        "successful": results["successful_rows"],

        "partial": results["partial_rows"],

        "failed": results["failed_rows"]

    }

# ==================================================
# Cached Evaluation
# ==================================================

_cached_results = None


def get_batch_results():
    """
    Evaluate the sample dataset only once.
    All tests reuse these results.
    """

    global _cached_results

    if _cached_results is None:

        evaluator = BatchEvaluator()

        uploaded_file = load_csv()

        try:
            _cached_results = evaluator.evaluate_csv(
                uploaded_file
            )

        finally:
            uploaded_file.close()

    return _cached_results

def get_results():

    return get_batch_results()["results"]


def get_analytics():

    return get_batch_results()["analytics"]

# ==================================================
# Test 5
# PDF Report Generation
# ==================================================

def test_pdf_generation():

    results = get_batch_results()

    generator = PDFReportGenerator()

    start = time.perf_counter()

    output_path = os.path.join(
        os.path.dirname(__file__),
        "test_report.pdf"
    )

    pdf_path = generator.generate_report(
        results,
        output_path
    )

    execution_time = round(

        time.perf_counter() - start,

        3

    )

    assert pdf_path is not None
    assert os.path.exists(pdf_path)
    assert os.path.getsize(pdf_path) > 0

    return {
        "status": "PASS",
        "pdf_size_bytes": os.path.getsize(pdf_path),
        "execution_time": execution_time
    }

# ==================================================
# Test 6
# Hallucination Detection
# ==================================================

def test_hallucination_detection():

    analytics = get_analytics()

    assert "responses_with_hallucinations" in analytics

    assert "responses_without_hallucinations" in analytics

    assert "hallucination_frequency" in analytics

    frequency = analytics["hallucination_frequency"]

    assert 0 <= frequency <= 100

    return {

        "status": "PASS",

        "hallucination_frequency": frequency,

        "responses_with_hallucinations":
            analytics["responses_with_hallucinations"],

        "responses_without_hallucinations":
            analytics["responses_without_hallucinations"]

    }

# ==================================================
# Test 7
# Dashboard Analytics
# ==================================================

def test_dashboard_metrics():

    analytics = get_analytics()

    numeric_fields = [

        "average_relevance",

        "average_accuracy",

        "average_hallucination",

        "average_completeness"

    ]

    for field in numeric_fields:

        value = analytics[field]

        assert value is None or (

            0 <= value <= 10

        )

    assert isinstance(

        analytics["quality_trend"],

        list

    )

    assert isinstance(

        analytics["dimension_trends"],

        dict

    )

    required_dimensions = [

        "relevance",

        "accuracy",

        "hallucination",

        "completeness"

    ]

    for dimension in required_dimensions:

        assert dimension in analytics["dimension_trends"]

    return {

        "status": "PASS",

        "quality_points":

            len(

                analytics["quality_trend"]

            )

    }

# ==================================================
# Test 8
# Missing CSV File Validation
# ==================================================

def test_missing_csv():

    evaluator = BatchEvaluator()

    error_detected = False

    try:

        evaluator.evaluate_csv(None)

    except ValueError as error:

        error_detected = True

        assert "No CSV file was provided" in str(error)

    assert error_detected is True

    return {

        "status": "PASS",

        "validation": "Missing CSV correctly rejected"

    }


# ==================================================
# Test 9
# Invalid File Type Validation
# ==================================================

def test_invalid_file_type():

    evaluator = BatchEvaluator()

    from io import BytesIO

    invalid_file = FileStorage(

        stream=BytesIO(

            b"This is not a CSV file."

        ),

        filename="invalid_file.txt",

        content_type="text/plain"

    )

    error_detected = False

    try:

        evaluator.evaluate_csv(

            invalid_file

        )

    except ValueError as error:

        error_detected = True

        assert "Only CSV files are supported" in str(error)

    finally:

        invalid_file.close()

    assert error_detected is True

    return {

        "status": "PASS",

        "validation":
            "Non-CSV file correctly rejected"

    }


# ==================================================
# Test 10
# Invalid CSV Columns
# ==================================================

def test_invalid_csv_columns():

    evaluator = BatchEvaluator()

    from io import BytesIO

    invalid_csv = (

        "name,email,age\n"
        "Test User,test@example.com,22\n"

    ).encode("utf-8")

    uploaded_file = FileStorage(

        stream=BytesIO(

            invalid_csv

        ),

        filename="invalid_columns.csv",

        content_type="text/csv"

    )

    error_detected = False

    try:

        evaluator.evaluate_csv(

            uploaded_file

        )

    except (ValueError, KeyError) as error:

        error_detected = True

        assert str(error)

    finally:

        uploaded_file.close()

    assert error_detected is True

    return {

        "status": "PASS",

        "validation":
            "CSV with invalid columns correctly rejected"

    }


# ==================================================
# Test 11
# Empty CSV Validation
# ==================================================

def test_empty_csv():

    evaluator = BatchEvaluator()

    from io import BytesIO

    empty_csv = FileStorage(

        stream=BytesIO(b""),

        filename="empty.csv",

        content_type="text/csv"

    )

    error_detected = False

    try:

        evaluator.evaluate_csv(

            empty_csv

        )

    except Exception as error:

        error_detected = True

        assert str(error)

    finally:

        empty_csv.close()

    assert error_detected is True

    return {

        "status": "PASS",

        "validation":
            "Empty CSV correctly rejected"

    }

# ==================================================
# Test 12
# Scoring Consistency Validation
# ==================================================

def test_scoring_consistency():

    evaluator = BatchEvaluator()

    runs = []

    for _ in range(2):

        uploaded_file = load_small_csv()

        result = evaluator.evaluate_csv(

            uploaded_file

        )

        uploaded_file.close()

        runs.append(result)

    first = runs[0]["analytics"]

    first_rows = [
    
            row
    
            for row in runs[0]["results"]
    
            if row["status"] == "success"
    
    ]

    for current in runs[1:]:

        current_rows = [

            row

            for row in current["results"]

            if row["status"] == "success"

        ]

        assert len(first_rows) == len(current_rows)

        for row1, row2 in zip(first_rows, current_rows):

            eval1 = row1["evaluation"]

            eval2 = row2["evaluation"]

            assert (

                eval1["relevance"]["score"]

                == eval2["relevance"]["score"]

            )

            assert (

                eval1["accuracy"]["score"]

                == eval2["accuracy"]["score"]

            )

            assert (

                eval1["hallucination"]["score"]

                == eval2["hallucination"]["score"]

            )

            assert (

                eval1["completeness"]["score"]

                == eval2["completeness"]["score"]

            )

            assert (

                eval1["verdict"]

                == eval2["verdict"]

            )

        # ← Row loop ends here

        analytics = current["analytics"]

        assert (

            analytics["average_relevance"]

            == first["average_relevance"]

        )

        assert (

            analytics["average_accuracy"]

            == first["average_accuracy"]

        )

        assert (

            analytics["average_hallucination"]

            == first["average_hallucination"]

        )

        assert (

            analytics["average_completeness"]

            == first["average_completeness"]

        )

    verdicts_first = [

        row["evaluation"]["verdict"]

        for row in runs[0]["results"]

        if row.get("status") == "success"

    ]

    for current in runs[1:]:

        verdicts_current = [

            row["evaluation"]["verdict"]

            for row in current["results"]

            if row.get("status") == "success"

        ]

        assert verdicts_current == verdicts_first

    return {

        "status": "PASS",

        "runs_compared": 2,

        "consistency": "Verified"

    }

# ==================================================
# Test 13
# Performance Benchmark
# ==================================================

def test_performance():

    evaluator = BatchEvaluator()

    # Use the small dataset for performance testing
    # to avoid unnecessarily processing the large
    # extended dataset.
    uploaded_file = load_small_csv()

    start = time.perf_counter()

    try:

        results = evaluator.evaluate_csv(
            uploaded_file
        )

    finally:

        uploaded_file.close()

    execution_time = round(
        time.perf_counter() - start,
        3
    )

    assert results is not None

    return {
        "status": "PASS",
        "execution_time": execution_time,
        "rows_processed": results["total_rows"],
        "successful_rows": results["successful_rows"],
        "partial_rows": results["partial_rows"],
        "failed_rows": results["failed_rows"],
        "average_score": results["average_score"]
    }

# ==================================================
# Test 14
# Overall Result Validation
# ==================================================

def test_complete_pipeline():

    results = get_batch_results()

    assert "results" in results

    assert "analytics" in results

    assert "verdict_counts" in results

    assert "average_score" in results

    assert "successful_rows" in results

    assert results["successful_rows"] > 0

    return {

        "status": "PASS",

        "pipeline": "Complete"

    }


# ==================================================
# Execute All Tests
# ==================================================

def get_test_suite():

    return TEST_SUITE

# ==================================================
# Complete End-to-End Test Suite
# ==================================================

TEST_SUITE = [

    (
        "Batch Evaluation",
        test_batch_evaluation
    ),

    (
        "Analytics Generation",
        test_analytics_generation
    ),

    (
        "Verdict Generation",
        test_verdict_generation
    ),

    (
        "Batch Statistics",
        test_batch_statistics
    ),

    (
        "PDF Report Generation",
        test_pdf_generation
    ),

    (
        "Hallucination Detection",
        test_hallucination_detection
    ),

    (
        "Dashboard Metrics",
        test_dashboard_metrics
    ),

    (
        "Missing CSV Validation",
        test_missing_csv
    ),

    (
        "Invalid File Type",
        test_invalid_file_type
    ),

    (
        "Invalid CSV Columns",
        test_invalid_csv_columns
    ),

    (
        "Empty CSV Validation",
        test_empty_csv
    ),

    (
        "Scoring Consistency",

        test_scoring_consistency

    ),

    (
        "Performance Benchmark",

        test_performance

    ),

    (
        "Complete Pipeline",

        test_complete_pipeline

    )

]