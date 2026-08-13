import csv
import io

from backend.evaluator import ResponseEvaluator


class BatchEvaluator:

    def __init__(self):

        self.evaluator = ResponseEvaluator()


    # ==========================================
    # AGENT HELPERS
    # ==========================================

    def _get_agent_statuses(self, evaluation):

        agent_names = [
            "relevance",
            "accuracy",
            "hallucination",
            "completeness"
        ]

        return {
            agent_name: (
                evaluation
                .get(agent_name, {})
                .get("status", "evaluated")
            )
            for agent_name in agent_names
        }


    def _determine_row_status(self, evaluation):

        """
        Determine whether a row evaluation completed
        successfully, partially, or failed.

        evaluated:
            Agent completed normally.

        unverifiable:
            Agent completed normally, but sufficient
            grounding evidence was unavailable.

        error:
            Agent encountered an actual evaluation error.

        'unverifiable' is therefore NOT considered
        an execution failure.
        """

        statuses = self._get_agent_statuses(
            evaluation
        )

        status_values = list(
            statuses.values()
        )

        error_count = sum(
            status == "error"
            for status in status_values
        )


        # -----------------------------
        # All Agents Failed
        # -----------------------------

        if (
            status_values
            and error_count == len(status_values)
        ):

            return "error"


        # -----------------------------
        # Some Agents Failed
        # -----------------------------

        if error_count > 0:

            return "partial"


        # -----------------------------
        # Evaluation Completed
        # -----------------------------

        # Includes:
        # evaluated
        # unverifiable

        return "success"


    def _build_row_error(
        self,
        evaluation
    ):

        """
        Generate a meaningful error message when
        a row cannot be evaluated successfully.
        """

        statuses = self._get_agent_statuses(
            evaluation
        )

        failed_agents = [
            agent_name
            for agent_name, status
            in statuses.items()
            if status == "error"
        ]


        if len(failed_agents) == len(statuses):

            return (
                "Evaluation could not be completed "
                "because all judge agents failed."
            )


        if failed_agents:

            readable_agents = ", ".join(
                agent.replace("_", " ").title()
                for agent in failed_agents
            )

            return (
                "Evaluation was only partially completed. "
                "The following judge agents encountered "
                f"errors: {readable_agents}."
            )


        return (
            "Evaluation could not be completed "
            "for this row."
        )


    # ==========================================
    # EVALUATE CSV
    # ==========================================

    def evaluate_csv(self, file):

        # -----------------------------
        # Validate File
        # -----------------------------

        if not file or not file.filename:

            raise ValueError(
                "No CSV file was provided."
            )


        if not file.filename.lower().endswith(
            ".csv"
        ):

            raise ValueError(
                "Only CSV files are supported."
            )


        # -----------------------------
        # Read CSV
        # -----------------------------

        try:

            content = file.read().decode(
                "utf-8-sig"
            )

        except UnicodeDecodeError:

            raise ValueError(
                "The CSV file must use UTF-8 encoding."
            )


        if not content.strip():

            raise ValueError(
                "The CSV file is empty."
            )


        reader = csv.DictReader(
            io.StringIO(content)
        )


        # -----------------------------
        # Validate Header
        # -----------------------------

        if not reader.fieldnames:

            raise ValueError(
                "The CSV file does not contain "
                "a header row."
            )


        fieldnames = [
            field.strip().lower()
            for field in reader.fieldnames
            if field
        ]


        required_columns = {
            "question",
            "response"
        }


        missing_columns = (
            required_columns
            - set(fieldnames)
        )


        if missing_columns:

            raise ValueError(
                "Missing required CSV column(s): "
                + ", ".join(
                    sorted(missing_columns)
                )
            )


        # -----------------------------
        # Initialize Batch Statistics
        # -----------------------------

        batch_results = []

        total_rows = 0

        successful_rows = 0

        partial_rows = 0

        failed_rows = 0


        # ==========================================
        # EVALUATE ROWS
        # ==========================================

        for row_number, row in enumerate(
            reader,
            start=1
        ):

            total_rows += 1


            # -------------------------
            # Normalize Column Names
            # -------------------------

            normalized_row = {
                str(key).strip().lower(): value
                for key, value in row.items()
                if key is not None
            }


            # -------------------------
            # Extract Values
            # -------------------------

            question = (
                normalized_row.get(
                    "question",
                    ""
                )
                or ""
            ).strip()


            response = (
                normalized_row.get(
                    "response",
                    ""
                )
                or ""
            ).strip()


            reference = (
                normalized_row.get(
                    "reference",
                    ""
                )
                or ""
            ).strip()


            # -------------------------
            # Validate Row
            # -------------------------

            if not question or not response:

                failed_rows += 1


                batch_results.append({

                    "row_number":
                        row_number,

                    "question":
                        question,

                    "response":
                        response,

                    "reference":
                        reference,

                    "status":
                        "error",

                    "error":
                        "Question and response "
                        "are required."
                })


                continue


            # -------------------------
            # Run Existing Evaluator
            # -------------------------

            try:

                evaluation = (
                    self.evaluator.evaluate(
                        question,
                        response,
                        reference
                    )
                )


                # ---------------------
                # Validate Evaluation
                # ---------------------

                if not isinstance(
                    evaluation,
                    dict
                ):

                    raise ValueError(
                        "Evaluator returned an "
                        "invalid result."
                    )


                # ---------------------
                # Determine Row Status
                # ---------------------

                row_status = (
                    self._determine_row_status(
                        evaluation
                    )
                )


                # ---------------------
                # Update Statistics
                # ---------------------

                if row_status == "success":

                    successful_rows += 1


                elif row_status == "partial":

                    partial_rows += 1


                else:

                    failed_rows += 1


                # ---------------------
                # Build Stored Result
                # ---------------------

                row_result = {

                    "row_number":
                        row_number,

                    "question":
                        question,

                    "response":
                        response,

                    "reference":
                        reference,

                    "status":
                        row_status,

                    "evaluation":
                        evaluation
                }


                # ---------------------
                # Attach Error Message
                # ---------------------

                if row_status == "error":

                    row_result["error"] = (
                        self._build_row_error(
                            evaluation
                        )
                    )


                # Partial rows retain the evaluation
                # and may also expose which agents
                # encountered errors.

                elif row_status == "partial":

                    row_result["warning"] = (
                        self._build_row_error(
                            evaluation
                        )
                    )


                batch_results.append(
                    row_result
                )


            except Exception as e:

                print(
                    f"Batch Row "
                    f"{row_number} Error:",
                    e
                )


                failed_rows += 1


                batch_results.append({

                    "row_number":
                        row_number,

                    "question":
                        question,

                    "response":
                        response,

                    "reference":
                        reference,

                    "status":
                        "error",

                    "error":
                        "Evaluation failed for this row."
                })


        # -----------------------------
        # Empty CSV Check
        # -----------------------------

        if total_rows == 0:

            raise ValueError(
                "The CSV file contains "
                "no evaluation rows."
            )


        # ==========================================
        # AGGREGATE RESULTS
        # ==========================================

        verdict_counts = {
            "Pass": 0,
            "Needs Improvement": 0,
            "Fail": 0
        }


        overall_scores = []
        relevance_scores = []
        accuracy_scores = []
        hallucination_scores = []
        completeness_scores = []

        responses_with_hallucinations = 0
        responses_without_hallucinations = 0

        quality_trend = []

        highest_score = None
        lowest_score = None

        # -----------------------------
        # Dimension Trends
        # -----------------------------

        dimension_trends = {

            "relevance": [],
            "accuracy": [],
            "hallucination": [],
            "completeness": []

        }

        # -----------------------------
        # Aggregate Valid Evaluations
        # -----------------------------

        for item in batch_results:

            # Only fully successful evaluations
            # contribute to aggregate metrics.
            #
            # Partial evaluations are excluded because
            # one or more judge agents encountered an
            # execution error.
            #
            # Error rows contain no complete reliable
            # evaluation.

            if item["status"] != "success":

                continue


            evaluation = item.get(
                "evaluation",
                {}
            )

            # -------------------------
            # Dimension Scores
            # -------------------------

            relevance = (
                evaluation.get("relevance", {})
                .get("score")
            )

            accuracy = (
                evaluation.get("accuracy", {})
                .get("score")
            )

            hallucination = (
                evaluation.get("hallucination", {})
                .get("score")
            )

            completeness = (
                evaluation.get("completeness", {})
                .get("score")
            )

            if isinstance(relevance, (int, float)):

                relevance_scores.append(relevance)

                dimension_trends["relevance"].append(
                    relevance
                )

            if isinstance(accuracy, (int, float)):

                accuracy_scores.append(accuracy)

                dimension_trends["accuracy"].append(
                    accuracy
                )

            if isinstance(hallucination, (int, float)):

                hallucination_scores.append(
                    hallucination
                )

                dimension_trends["hallucination"].append(
                    hallucination
                )

            if isinstance(completeness, (int, float)):

                completeness_scores.append(
                    completeness
                )

                dimension_trends["completeness"].append(
                    completeness
                )

            unsupported_claims = (
                evaluation.get("hallucination", {})
                .get("unsupported_claims", [])
            )

            if unsupported_claims:
                responses_with_hallucinations += 1
            else:
                responses_without_hallucinations += 1
            # -------------------------
            # Verdict Counts
            # -------------------------

            verdict = evaluation.get(
                "verdict"
            )


            if verdict in verdict_counts:

                verdict_counts[verdict] += 1


            # -------------------------
            # Overall Scores
            # -------------------------

            score = evaluation.get(
                "overall_score"
            )


            # Only numeric complete scores
            # contribute to the average.

            if isinstance(
                score,
                (int, float)
            ):

                overall_scores.append(
                    score
                )

                quality_trend.append(score)

                if highest_score is None or score > highest_score:
                    highest_score = score

                if lowest_score is None or score < lowest_score:
                    lowest_score = score
        # -----------------------------
        # Average Overall Score
        # -----------------------------

        if overall_scores:

            average_score = round(
                sum(overall_scores)
                / len(overall_scores),
                1
            )

        else:

            average_score = None


        # -----------------------------
        # Evaluated Row Count
        # -----------------------------

        evaluated_rows = (
            successful_rows
            + partial_rows
        )


        # Aggregated rows should reflect
        # the actual number of rows that
        # contributed a numeric score.

        aggregated_rows = len(
            overall_scores
        )


        def average(values):

            if not values:
                return None

            return round(sum(values) / len(values), 1)


        average_relevance = average(relevance_scores)
        average_accuracy = average(accuracy_scores)
        average_hallucination = average(hallucination_scores)
        average_completeness = average(completeness_scores)

        # -----------------------------
        # Verdict Percentages
        # -----------------------------

        total_verdicts = sum(
            verdict_counts.values()
        )

        if total_verdicts:

            pass_percentage = round(
                verdict_counts["Pass"] * 100
                / total_verdicts,
                1
            )

            needs_improvement_percentage = round(
                verdict_counts["Needs Improvement"] * 100
                / total_verdicts,
                1
            )

            fail_percentage = round(
                verdict_counts["Fail"] * 100
                / total_verdicts,
                1
            )

        else:

            pass_percentage = 0
            needs_improvement_percentage = 0
            fail_percentage = 0


        # -----------------------------
        # Hallucination Frequency
        # -----------------------------

        if aggregated_rows:

            hallucination_frequency = round(
                responses_with_hallucinations
                * 100
                / aggregated_rows,
                1
            )

        else:

            hallucination_frequency = 0


        # -----------------------------
        # Best / Weakest Dimension
        # -----------------------------

        dimension_averages = {

            "Relevance":
                average_relevance,

            "Accuracy":
                average_accuracy,

            "Hallucination":
                average_hallucination,

            "Completeness":
                average_completeness

        }

        valid_dimensions = {

            key: value

            for key, value
            in dimension_averages.items()

            if value is not None

        }

        if valid_dimensions:

            best_dimension = max(
                valid_dimensions,
                key=valid_dimensions.get
            )

            weakest_dimension = min(
                valid_dimensions,
                key=valid_dimensions.get
            )

        else:

            best_dimension = None
            weakest_dimension = None

        # ==========================================
        # RETURN BATCH RESULT
        # ==========================================

        return {

            "total_rows":
                total_rows,

            "evaluated_rows":
                evaluated_rows,

            "successful_rows":
                successful_rows,

            "partial_rows":
                partial_rows,

            "failed_rows":
                failed_rows,

            "aggregated_rows":
                aggregated_rows,

            "average_score":
                average_score,

            "verdict_counts":
                verdict_counts,

            "analytics": {

                "average_relevance":
                    average_relevance,

                "average_accuracy":
                    average_accuracy,

                "average_hallucination":
                    average_hallucination,

                "average_completeness":
                    average_completeness,

                "responses_with_hallucinations":
                    responses_with_hallucinations,

                "responses_without_hallucinations":
                    responses_without_hallucinations,

                "hallucination_frequency":
                    hallucination_frequency,

                "highest_score":
                    highest_score,

                "lowest_score":
                    lowest_score,

                "best_dimension":
                    best_dimension,

                "weakest_dimension":
                    weakest_dimension,

                "quality_trend":
                    quality_trend,

                "dimension_trends":
                    dimension_trends,

                "pass_percentage":
                    pass_percentage,

                "needs_improvement_percentage":
                    needs_improvement_percentage,

                "fail_percentage":
                    fail_percentage

            },

            "results":
                batch_results
        }