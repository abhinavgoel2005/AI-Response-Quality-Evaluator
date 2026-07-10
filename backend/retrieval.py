# -------------------------------------
# Reference Knowledge Base
# -------------------------------------

knowledge_base = [

"""
Artificial Intelligence (AI) is the simulation of human intelligence by machines. It enables computers to learn, reason, solve problems, and make decisions.
""",

"""
Machine Learning (ML) is a subset of Artificial Intelligence that enables computers to learn patterns from data without being explicitly programmed.
""",

"""
Large Language Models (LLMs) are advanced AI models capable of understanding and generating human-like text. However, they may sometimes produce hallucinations.
""",

"""
Hallucination refers to the generation of incorrect or fabricated information by a Large Language Model that is not supported by facts or reference data.
""",

"""
Retrieval-Augmented Generation (RAG) improves response reliability by retrieving relevant information from a trusted knowledge base before generating or evaluating responses.
""",

"""
Sentence embeddings convert textual information into numerical vectors that allow semantic similarity comparison between user queries and stored documents.
""",

"""
FAISS (Facebook AI Similarity Search) is a vector database used for efficient similarity search among high-dimensional embeddings.
""",

"""
Chunking is the process of dividing large documents into smaller meaningful passages to improve retrieval efficiency and response quality.
""",

"""
Common evaluation dimensions for AI-generated responses include Accuracy, Relevance, Completeness, Faithfulness, and Hallucination Detection.
""",

"""
Reference answers provide a trusted source for comparing AI-generated responses and measuring their overall quality.
"""

]


def retrieve(query, k=3):

    query = query.lower()

    # Expand common abbreviations
    query = query.replace("ai", "artificial intelligence")
    query = query.replace("ml", "machine learning")
    query = query.replace("llm", "large language models")
    query = query.replace("rag", "retrieval augmented generation")

    scores = []

    for chunk in knowledge_base:

        score = 0

        for word in query.split():

            if word in chunk.lower():
                score += 1

        scores.append((score, chunk))

    scores.sort(key=lambda x: x[0], reverse=True)

    return [item[1] for item in scores[:k]]