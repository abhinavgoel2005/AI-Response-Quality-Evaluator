# Research

This document summarizes the research carried out for Milestone 1 of the Infosys Springboard Internship Project. The research focuses on understanding modern techniques used to evaluate Large Language Model (LLM) responses and designing an AI-based response evaluation system.

---

# 1. LLM Evaluation Techniques

Large Language Models (LLMs) can generate fluent and context-aware responses, but their outputs are not always accurate or reliable. Therefore, evaluating the quality of AI-generated responses is an important step before deploying LLM-based applications.

Common evaluation parameters include:

- **Accuracy** – Measures whether the generated response is factually correct.
- **Relevance** – Checks whether the response answers the user's question.
- **Completeness** – Determines whether all important information is included.
- **Faithfulness** – Verifies whether the response is supported by the reference context.
- **Fluency** – Evaluates grammar and readability.
- **Hallucination** – Identifies information that is fabricated or unsupported.

These evaluation parameters form the basis of the AI Response Quality Evaluator Agent.

---

# 2. Hallucination Detection Methods

Hallucination refers to the generation of incorrect or fabricated information by an LLM. Even though the response may sound convincing, it may not be supported by factual evidence.

Some common hallucination detection approaches include:

- Comparing responses with trusted reference documents.
- Using Retrieval-Augmented Generation (RAG) to verify factual information.
- Evaluating response consistency using LLM-based evaluation frameworks.
- Measuring faithfulness between retrieved context and generated response.

Hallucination detection is one of the primary objectives of this project.

---

# 3. Retrieval-Augmented Generation (RAG)

Retrieval-Augmented Generation (RAG) combines information retrieval with language generation.

Instead of relying only on the knowledge stored inside an LLM, RAG first retrieves relevant information from a trusted knowledge base and then uses this information during response generation or evaluation.

Typical RAG workflow:

```text
User Query
     │
     ▼
Retriever
     │
     ▼
Relevant Documents
     │
     ▼
LLM
     │
     ▼
Response / Evaluation
```

Using RAG improves factual accuracy and helps reduce hallucinations.

---

# 4. RAGAS

RAGAS (Retrieval-Augmented Generation Assessment) is an open-source evaluation framework designed specifically for RAG applications.

It provides automated metrics such as:

- Faithfulness
- Answer Relevancy
- Context Precision
- Context Recall

These metrics help evaluate whether an LLM response is supported by the retrieved context.

RAGAS will be explored as one of the evaluation frameworks for this project.

---

# 5. TruLens

TruLens is an evaluation and monitoring framework for Large Language Model applications.

It provides tools for:

- Measuring response quality
- Evaluating groundedness
- Tracking application performance
- Monitoring LLM behavior

TruLens helps developers understand how reliable and trustworthy an LLM application is.

---

# 6. Research Summary

Based on the research conducted, the proposed AI Response Quality Evaluator Agent will evaluate AI-generated responses using multiple quality dimensions such as accuracy, relevance, completeness, and hallucination detection. The project will also explore the use of RAG, RAGAS, and TruLens to improve evaluation reliability and explainability.
