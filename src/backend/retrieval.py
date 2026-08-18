import json
import os
import re
import math

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
# OPTIONAL SENTENCE TRANSFORMER
# ==========================================

_model = None
_model_failed = False


def get_model():
    """
    Load Sentence Transformer only when actually needed.
    This prevents Render from loading the model during startup.
    """

    global _model
    global _model_failed

    if _model is not None:
        return _model

    if _model_failed:
        return None

    try:
        # Reduce CPU/thread overhead
        try:
            import torch
            torch.set_num_threads(1)
        except Exception:
            pass

        from sentence_transformers import SentenceTransformer

        print("Loading embedding model...")

        _model = SentenceTransformer(
            "all-MiniLM-L6-v2",
            device="cpu"
        )

        print("Embedding model loaded successfully.")

        return _model

    except Exception as e:
        print("Embedding model unavailable:", e)
        print("Using lightweight retrieval fallback.")

        _model_failed = True
        return None


# ==========================================
# KNOWLEDGE RETRIEVER
# ==========================================

class KnowledgeRetriever:

    def __init__(self, similarity_threshold=0.35):

        self.documents = []

        self.index = None

        self.similarity_threshold = similarity_threshold

        # Do NOT load the transformer model here.
        # Only load the knowledge base.
        self._load_knowledge_base()

        # Model and FAISS index are created lazily.
        self._initialized = False


    # ==========================================
    # LOAD KNOWLEDGE BASE
    # ==========================================

    def _load_knowledge_base(self):

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
    # BUILD FAISS INDEX
    # ==========================================

    def _build_index(self):

        if self._initialized:
            return

        model = get_model()

        if model is None:
            return

        try:

            import faiss

            texts = [
                f"{document['title']}. {document['content']}"
                for document in self.documents
            ]

            embeddings = model.encode(
                texts,
                convert_to_numpy=True,
                batch_size=1,
                show_progress_bar=False
            ).astype("float32")

            faiss.normalize_L2(embeddings)

            dimension = embeddings.shape[1]

            self.index = faiss.IndexFlatIP(
                dimension
            )

            self.index.add(
                embeddings
            )

            self._initialized = True

            print("FAISS index created successfully.")

        except Exception as e:

            print("FAISS initialization failed:", e)

            self.index = None


    # ==========================================
    # LIGHTWEIGHT TOKENIZATION
    # ==========================================

    def _tokenize(self, text):

        text = text.lower()

        return set(
            re.findall(
                r"\b[a-z0-9]+\b",
                text
            )
        )


    # ==========================================
    # LIGHTWEIGHT FALLBACK RETRIEVAL
    # ==========================================

    def _fallback_retrieve(
        self,
        question,
        top_k=3
    ):

        question_tokens = self._tokenize(
            question
        )

        if not question_tokens:
            return []

        scored_documents = []

        for document in self.documents:

            text = (
                str(document.get("title", ""))
                + " "
                + str(document.get("content", ""))
            )

            document_tokens = self._tokenize(
                text
            )

            if not document_tokens:
                continue

            intersection = (
                question_tokens
                & document_tokens
            )

            # Simple Jaccard-style similarity
            union = (
                question_tokens
                | document_tokens
            )

            score = (
                len(intersection)
                / len(union)
                if union
                else 0
            )

            if score > 0:

                scored_documents.append(
                    (
                        score,
                        document
                    )
                )

        scored_documents.sort(
            key=lambda x: x[0],
            reverse=True
        )

        results = []

        for score, document in scored_documents[:top_k]:

            results.append(
                {
                    "id": document.get("id"),
                    "title": document.get("title"),
                    "content": document.get("content"),
                    "score": float(score)
                }
            )

        return results


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
        # Try semantic RAG
        # --------------------------------------

        model = get_model()

        if model is not None:

            try:

                self._build_index()

                if self.index is not None:

                    import faiss

                    query_embedding = model.encode(
                        [question],
                        convert_to_numpy=True,
                        batch_size=1,
                        show_progress_bar=False
                    ).astype("float32")

                    faiss.normalize_L2(
                        query_embedding
                    )

                    top_k = min(
                        top_k,
                        len(self.documents)
                    )

                    scores, indices = (
                        self.index.search(
                            query_embedding,
                            top_k
                        )
                    )

                    results = []

                    for score, index in zip(
                        scores[0],
                        indices[0]
                    ):

                        if index == -1:
                            continue

                        score = float(score)

                        if score < similarity_threshold:
                            continue

                        document = self.documents[index]

                        results.append(
                            {
                                "id": document.get("id"),
                                "title": document.get("title"),
                                "content": document.get("content"),
                                "score": score
                            }
                        )

                    return results

            except Exception as e:

                print(
                    "Semantic retrieval failed:",
                    e
                )

                print(
                    "Switching to lightweight retrieval."
                )

        # --------------------------------------
        # Fallback retrieval
        # --------------------------------------

        return self._fallback_retrieve(
            question,
            top_k
        )