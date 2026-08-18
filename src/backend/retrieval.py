import json
import os
import re
import math
from collections import Counter


# ==========================================
# PATH CONFIGURATION
# ==========================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

KNOWLEDGE_BASE_PATH = os.path.join(
    BASE_DIR,
    "knowledge_base",
    "knowledge_base.json"
)


# ==========================================
# LIGHTWEIGHT TEXT RETRIEVER
# ==========================================

class KnowledgeRetriever:

    def __init__(self, similarity_threshold=0.05):

        self.documents = []
        self.document_vectors = {}
        self.idf = {}

        self.similarity_threshold = similarity_threshold

        self._load_knowledge_base()
        self._build_index()


    # ==========================================
    # TEXT TOKENIZATION
    # ==========================================

    def _tokenize(self, text):

        if not text:
            return []

        text = text.lower()

        # Keep only words/numbers
        tokens = re.findall(
            r"\b[a-zA-Z0-9]+\b",
            text
        )

        # Remove very common words
        stop_words = {
            "the", "is", "a", "an", "and",
            "or", "of", "to", "in", "on",
            "for", "with", "from", "by",
            "as", "at", "are", "was",
            "were", "be", "been", "this",
            "that", "it", "its", "into",
            "can", "may", "will", "how",
            "what", "which", "who", "why"
        }

        return [
            token
            for token in tokens
            if token not in stop_words
        ]


    # ==========================================
    # LOAD KNOWLEDGE BASE
    # ==========================================

    def _load_knowledge_base(self):

        if not os.path.exists(
            KNOWLEDGE_BASE_PATH
        ):
            raise FileNotFoundError(
                "Knowledge base not found: "
                + KNOWLEDGE_BASE_PATH
            )

        with open(
            KNOWLEDGE_BASE_PATH,
            "r",
            encoding="utf-8"
        ) as file:

            self.documents = json.load(file)

        if not self.documents:

            raise ValueError(
                "Knowledge base is empty."
            )


    # ==========================================
    # BUILD LIGHTWEIGHT INDEX
    # ==========================================

    def _build_index(self):

        document_frequencies = Counter()

        tokenized_documents = []

        # --------------------------------------
        # Tokenize documents
        # --------------------------------------

        for document in self.documents:

            text = (
                str(document.get("title", ""))
                + " "
                + str(document.get("content", ""))
            )

            tokens = self._tokenize(text)

            tokenized_documents.append(tokens)

            unique_tokens = set(tokens)

            for token in unique_tokens:
                document_frequencies[token] += 1


        # --------------------------------------
        # Calculate IDF
        # --------------------------------------

        total_documents = len(
            self.documents
        )

        for token, frequency in document_frequencies.items():

            self.idf[token] = math.log(
                (total_documents + 1)
                / (frequency + 1)
            ) + 1


        # --------------------------------------
        # Build TF-IDF vectors
        # --------------------------------------

        for document, tokens in zip(
            self.documents,
            tokenized_documents
        ):

            term_frequency = Counter(tokens)

            vector = {}

            total_tokens = len(tokens)

            if total_tokens > 0:

                for token, count in term_frequency.items():

                    tf = count / total_tokens

                    vector[token] = (
                        tf * self.idf.get(
                            token,
                            1.0
                        )
                    )

            self.document_vectors[
                document["id"]
            ] = vector


    # ==========================================
    # COSINE SIMILARITY
    # ==========================================

    def _cosine_similarity(
        self,
        query_vector,
        document_vector
    ):

        if not query_vector:
            return 0.0

        if not document_vector:
            return 0.0

        common_tokens = (
            set(query_vector.keys())
            & set(document_vector.keys())
        )

        if not common_tokens:
            return 0.0

        dot_product = sum(
            query_vector[token]
            * document_vector[token]
            for token in common_tokens
        )

        query_norm = math.sqrt(
            sum(
                value * value
                for value in query_vector.values()
            )
        )

        document_norm = math.sqrt(
            sum(
                value * value
                for value in document_vector.values()
            )
        )

        if (
            query_norm == 0
            or document_norm == 0
        ):
            return 0.0

        return (
            dot_product
            / (query_norm * document_norm)
        )


    # ==========================================
    # RETRIEVE DOCUMENTS
    # ==========================================

    def retrieve(
        self,
        question,
        top_k=3,
        similarity_threshold=None
    ):

        if not question or not question.strip():
            return []

        if similarity_threshold is None:

            similarity_threshold = (
                self.similarity_threshold
            )


        # --------------------------------------
        # Create query vector
        # --------------------------------------

        query_tokens = self._tokenize(
            question
        )

        if not query_tokens:
            return []

        query_counts = Counter(
            query_tokens
        )

        total_query_tokens = len(
            query_tokens
        )

        query_vector = {}

        for token, count in query_counts.items():

            tf = (
                count
                / total_query_tokens
            )

            query_vector[token] = (
                tf * self.idf.get(
                    token,
                    1.0
                )
            )


        # --------------------------------------
        # Calculate similarity
        # --------------------------------------

        results = []

        for document in self.documents:

            document_id = document["id"]

            document_vector = (
                self.document_vectors.get(
                    document_id,
                    {}
                )
            )

            score = self._cosine_similarity(
                query_vector,
                document_vector
            )

            if score >= similarity_threshold:

                results.append({

                    "id":
                        document["id"],

                    "title":
                        document["title"],

                    "content":
                        document["content"],

                    "similarity_score":
                        float(score)
                })


        # --------------------------------------
        # Sort by relevance
        # --------------------------------------

        results.sort(
            key=lambda x:
                x["similarity_score"],
            reverse=True
        )


        # --------------------------------------
        # Return top results
        # --------------------------------------

        return results[:top_k]