from agents.relevance_agent import RelevanceJudge
from agents.accuracy_agent import AccuracyJudge
from agents.hallucination_agent import HallucinationJudge


class ResponseEvaluator:

    def __init__(self):

        self.relevance_agent = RelevanceJudge()
        self.accuracy_agent = AccuracyJudge()
        self.hallucination_agent = HallucinationJudge()

    def evaluate(self, question, response, reference):

        # -----------------------------
        # Input Validation
        # -----------------------------

        question = question.strip()
        response = response.strip()
        reference = reference.strip()

        if not question:

            return {

                "relevance": {
                    "score": 0,
                    "reason": "Question cannot be empty."
                },

                "accuracy": {
                    "score": 0,
                    "evidence": "Question cannot be empty."
                },

                "hallucination": {
                    "score": 0,
                    "reason": "Question cannot be empty.",
                    "unsupported_claims": []
                },

                "overall_score": 0
            }

        if not response:

            return {

                "relevance": {
                    "score": 0,
                    "reason": "AI response cannot be empty."
                },

                "accuracy": {
                    "score": 0,
                    "evidence": "AI response cannot be empty."
                },

                "hallucination": {
                    "score": 0,
                    "reason": "AI response cannot be empty.",
                    "unsupported_claims": []
                },

                "overall_score": 0
            }

        # -----------------------------
        # Relevance Agent
        # -----------------------------

        try:

            relevance_result = self.relevance_agent.evaluate(
                question,
                response
            )

        except Exception as e:

             print("Relevance Agent Error:", e)

             relevance_result = {

                "score":0,

                "reason":"Unable to evaluate relevance at the moment."


            }

        # -----------------------------
        # Accuracy Agent
        # -----------------------------

        try:

            accuracy_result = self.accuracy_agent.evaluate(
                question,
                response,
                reference
            )

        except Exception as e:

            print("Accuracy Agent Error:", e)

            accuracy_result = {

                "score":0,

                "evidence":"Unable to evaluate accuracy at the moment."

            }

        # -----------------------------
        # Hallucination Agent
        # -----------------------------

        try:

            hallucination_result = self.hallucination_agent.evaluate(
                response,
                reference
            )

        except Exception as e:

            print("Hallucination Agent Error:", e)

            hallucination_result = {

                "score":0,

                "reason":"Unable to evaluate hallucinations at the moment.",

                "unsupported_claims":[]

            }

        # -----------------------------
        # Overall Score
        # -----------------------------

        overall_score = round(

            (
                relevance_result["score"] +
                accuracy_result["score"] +
                hallucination_result["score"]

            ) / 3,

            1

        )

        return {

            "relevance": relevance_result,

            "accuracy": accuracy_result,

            "hallucination": hallucination_result,

            "overall_score": overall_score

        }