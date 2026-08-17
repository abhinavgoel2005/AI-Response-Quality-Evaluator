from concurrent.futures import ThreadPoolExecutor, as_completed
from agents.relevance_agent import RelevanceJudge
from agents.accuracy_agent import AccuracyJudge
from agents.hallucination_agent import HallucinationJudge
from agents.completeness_agent import CompletenessJudge
from agents.verdict_agent import VerdictAgent

from backend.retrieval import KnowledgeRetriever


class ResponseEvaluator:

    def __init__(self):

        # -----------------------------
        # Initialize Evaluation Agents
        # -----------------------------

        self.relevance_agent = RelevanceJudge()
        self.accuracy_agent = AccuracyJudge()
        self.hallucination_agent = HallucinationJudge()
        self.completeness_agent = CompletenessJudge()
        self.verdict_agent = VerdictAgent()

        # -----------------------------
        # Initialize RAG Retriever
        # -----------------------------

        self.retriever = KnowledgeRetriever()


    def evaluate(self, question, response, reference=""):

        # -----------------------------
        # Input Validation
        # -----------------------------

        question = question.strip() if question else ""
        response = response.strip() if response else ""
        reference = reference.strip() if reference else ""

        if not question:

            return self._validation_error(
                "Question cannot be empty."
            )

        if not response:

            return self._validation_error(
                "AI response cannot be empty."
            )


        # -----------------------------
        # RAG Retrieval
        # -----------------------------

        try:

            retrieved_chunks = self.retriever.retrieve(
                question,
                top_k=3
            )

        except Exception as e:

            print("Retrieval Error:", e)

            retrieved_chunks = []


        # -----------------------------
        # Determine Grounding State
        # -----------------------------

        has_reference = bool(reference)
        has_rag_evidence = bool(retrieved_chunks)

        grounding_available = (
            has_reference or has_rag_evidence
        )


        # -----------------------------
        # Parallel Evaluation Agents
        # -----------------------------

        def run_relevance():
            try:
                return self.relevance_agent.evaluate(
                    question,
                    response
                )
            except Exception as e:
                print("Relevance Agent Error:", e)

                return {
                    "score": None,
                    "status": "error",
                    "reason":
                        "Relevance evaluation could not be completed."
                }


        def run_accuracy():
            if not grounding_available:
                return {
                    "score": None,
                    "status": "unverifiable",
                    "evidence":
                        "No reference answer or sufficiently relevant "
                        "retrieved evidence was available to verify "
                        "the factual accuracy of this response."
                }

            try:
                return self.accuracy_agent.evaluate(
                    question,
                    response,
                    reference,
                    retrieved_chunks
                )
            except Exception as e:
                print("Accuracy Agent Error:", e)

                return {
                    "score": None,
                    "status": "error",
                    "evidence":
                        "Accuracy evaluation could not be completed."
                }


        def run_hallucination():
            if not grounding_available:
                return {
                    "score": None,
                    "status": "unverifiable",
                    "reason":
                        "No reference answer or sufficiently relevant "
                        "retrieved evidence was available to determine "
                        "whether the response contains unsupported claims.",
                    "unsupported_claims": []
                }

            try:
                return self.hallucination_agent.evaluate(
                    response,
                    reference,
                    retrieved_chunks
                )
            except Exception as e:
                print("Hallucination Agent Error:", e)

                return {
                    "score": None,
                    "status": "error",
                    "reason":
                        "Hallucination evaluation could not be completed.",
                    "unsupported_claims": []
                }


        def run_completeness():
            try:
                return self.completeness_agent.evaluate(
                    question,
                    response
                )
            except Exception as e:
                print("Completeness Agent Error:", e)

                return {
                    "score": None,
                    "status": "error",
                    "omissions": [],
                    "reason":
                        "Completeness evaluation could not be completed."
                }


        # Run independent agents concurrently.
        with ThreadPoolExecutor(max_workers=4) as executor:

            futures = {
                "relevance": executor.submit(run_relevance),
                "accuracy": executor.submit(run_accuracy),
                "hallucination": executor.submit(run_hallucination),
                "completeness": executor.submit(run_completeness)
            }

            relevance_result = futures["relevance"].result()
            accuracy_result = futures["accuracy"].result()
            hallucination_result = futures["hallucination"].result()
            completeness_result = futures["completeness"].result()

        # -----------------------------
        # Verdict Agent
        # -----------------------------

        try:

            verdict_result = self.verdict_agent.evaluate(
                relevance_result,
                accuracy_result,
                hallucination_result,
                completeness_result
            )

        except Exception as e:

            print("Verdict Agent Error:", e)

            verdict_result = {
                "overall_score": None,
                "verdict": "Unavailable",

                "consolidated_summary":
                    "Unable to generate the final verdict "
                    "at the moment.",

                "weights": {},

                "quality_gate_reasons": [
                    "The Verdict Agent encountered an error."
                ]
            }


        # -----------------------------
        # Final Evaluation Result
        # -----------------------------

        return {
            "relevance": relevance_result,
            "accuracy": accuracy_result,
            "hallucination": hallucination_result,
            "completeness": completeness_result,

            "overall_score":
                verdict_result["overall_score"],

            "verdict":
                verdict_result["verdict"],

            "consolidated_summary":
                verdict_result.get(
                    "consolidated_summary",
                    verdict_result.get(
                        "consolidated_reasoning",
                        ""
                    )
                ),

            "quality_gate_reasons":
                verdict_result.get(
                    "quality_gate_reasons",
                    []
                ),

            "weights":
                verdict_result.get(
                    "weights",
                    {}
                ),

            "grounding": {
                "reference_available": has_reference,
                "rag_evidence_available": has_rag_evidence,
                "retrieved_documents": len(
                    retrieved_chunks
                )
            }
        }


    # ==========================================
    # Validation Error Helper
    # ==========================================

    def _validation_error(self, message):

        return {
            "relevance": {
                "score": 0,
                "reason": message
            },

            "accuracy": {
                "score": 0,
                "status": "error",
                "evidence": message
            },

            "hallucination": {
                "score": 0,
                "status": "error",
                "reason": message,
                "unsupported_claims": []
            },

            "completeness": {
                "score": 0,
                "omissions": [],
                "reason": message
            },

            "overall_score": 0,
            "verdict": "Fail",

            "consolidated_reasoning": message,

            "reasoning": {
                "relevance": message,
                "accuracy": message,
                "hallucination": message,
                "completeness": message,
                "verdict_adjustment": message
            },

            "quality_gate_reasons": [
                message
            ],

            "weights": {},

            "grounding": {
                "reference_available": False,
                "rag_evidence_available": False,
                "retrieved_documents": 0
            }
        }