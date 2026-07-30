import json
import os
import faiss

from sentence_transformers import SentenceTransformer


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
# EMBEDDING MODEL
# ==========================================

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)


class KnowledgeRetriever:

    def __init__(self, similarity_threshold=0.35):

        self.documents = []
        self.index = None

        # Minimum similarity required for a document
        # to be treated as relevant evidence.
        self.similarity_threshold = similarity_threshold

        self._load_knowledge_base()
        self._build_index()


    # ==========================================
    # LOAD KNOWLEDGE BASE
    # ==========================================

    def _load_knowledge_base(self):

        """Load documents from knowledge_base.json."""

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

        """
        Generate document embeddings
        and build a FAISS index.
        """

        texts = [

            f"{document['title']}. {document['content']}"

            for document in self.documents
        ]

        embeddings = model.encode(
            texts,
            convert_to_numpy=True
        ).astype("float32")

        # Normalize vectors so inner product
        # behaves as cosine similarity.

        faiss.normalize_L2(embeddings)

        dimension = embeddings.shape[1]

        self.index = faiss.IndexFlatIP(
            dimension
        )

        self.index.add(
            embeddings
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

        """
        Retrieve documents relevant to the question.

        Documents below the similarity threshold
        are rejected instead of being passed to
        evaluation agents as evidence.
        """

        if not question or not question.strip():

            return []


        # Use instance threshold unless caller
        # explicitly provides another one.

        if similarity_threshold is None:

            similarity_threshold = (
                self.similarity_threshold
            )


        # ------------------------------------------
        # Generate query embedding
        # ------------------------------------------

        query_embedding = model.encode(
            [question],
            convert_to_numpy=True
        ).astype("float32")

        faiss.normalize_L2(
            query_embedding
        )


        # ------------------------------------------
        # Search FAISS
        # ------------------------------------------

        top_k = min(
            top_k,
            len(self.documents)
        )

        scores, indices = self.index.search(
            query_embedding,
            top_k
        )


        # ------------------------------------------
        # Filter retrieved documents
        # ------------------------------------------

        results = []

        for score, index in zip(
            scores[0],
            indices[0]
        ):

            if index == -1:

                continue


            score = float(score)


            # Reject weak semantic matches.

            if score < similarity_threshold:

                continue


            document = self.documents[index]


            results.append({

                "id":
                    document["id"],

                "title":
                    document["title"],

                "content":
                    document["content"],

                "similarity_score":
                    score

            })


        return results