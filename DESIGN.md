# HR Policy Assistant — Design Document

## 1. Overview

The HR Policy Assistant is a Retrieval-Augmented Generation (RAG) application that allows employees to ask questions about company HR policies.

The system retrieves relevant information from uploaded HR policy documents and uses Gemini to generate an answer grounded only in the retrieved policy content.

The application also provides citations showing the document and section used to answer the question.

If the available policy information does not contain an answer, the system safely refuses to answer and asks the employee to contact HR.

---

## 2. High-Level Architecture

```text
                    ┌─────────────────────┐
                    │   Employee / Admin  │
                    │      Frontend       │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │      FastAPI        │
                    │      Backend        │
                    └──────────┬──────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
                 ▼                           ▼
        ┌─────────────────┐         ┌─────────────────┐
        │ Document Upload │         │  Ask Question   │
        └────────┬────────┘         └────────┬────────┘
                 │                           │
                 ▼                           ▼
        ┌─────────────────┐         ┌─────────────────┐
        │ Parse & Chunk   │         │ Gemini Query    │
        │ Documents       │         │ Embedding      │
        └────────┬────────┘         └────────┬────────┘
                 │                           │
                 ▼                           ▼
        ┌─────────────────────────────────────────────┐
        │              ChromaDB                       │
        │         Vector Store / Search               │
        └──────────────────────┬──────────────────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Relevant Policy     │
                    │ Chunks + Metadata   │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ LangChain + Gemini  │
                    │     LLM             │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌─────────────────────┐
                    │ Answer + Citations  │
                    └─────────────────────┘
```

---

## 3. Technology Stack

### Backend

* Python
* FastAPI
* Uvicorn

### RAG / AI

* LangChain
* Gemini
* Gemini Embeddings
* ChromaDB

### Document Processing

* Markdown policy documents
* Text chunking
* Metadata extraction

### Frontend

* HTML
* CSS
* JavaScript

### Deployment

* Render for backend
* Vercel for frontend

---

## 4. RAG Pipeline

The application follows a Retrieval-Augmented Generation architecture.

### Step 1 — Document Upload

An administrator uploads an HR policy document.

The backend:

1. Receives the document.
2. Saves the uploaded file.
3. Extracts its text.
4. Splits the document into smaller chunks.
5. Adds metadata to each chunk.
6. Generates embeddings for the chunks.
7. Stores the embeddings and metadata in ChromaDB.

---

### Step 2 — Text Chunking

Documents are divided into smaller chunks instead of storing the complete document as a single vector.

Each chunk contains metadata such as:

```json
{
  "document_name": "leave-policy.md",
  "section": "2.1 Casual leave (CL)",
  "chunk_index": 2
}
```

This allows the system to identify the exact document and policy section used during retrieval.

---

### Step 3 — Embedding Generation

The system uses Gemini Embeddings to convert policy chunks into numerical vector representations.

The same embedding model is used for employee questions.

This allows the system to compare the semantic similarity between the question and policy chunks.

The current embedding model is:

```text
gemini-embedding-001
```

The embeddings are stored in ChromaDB.

---

## 5. Semantic Retrieval

When an employee asks a question, the question is converted into an embedding.

The application searches ChromaDB for the most semantically similar policy chunks.

The current retrieval configuration returns the top two relevant chunks for a normal question.

A relevance threshold is also applied.

If the retrieved result is not sufficiently relevant, the system does not send unrelated policy information to the LLM.

Instead, it returns:

```text
The HR policy does not provide this information. Please contact HR.
```

This reduces the risk of hallucinated answers.

---

## 6. LangChain Integration

LangChain is used to provide the LLM orchestration layer.

The application uses:

```text
LangChain
    ↓
ChatGoogleGenerativeAI
    ↓
Gemini
```

The Gemini chat model is used to generate the final grounded answer.

The application sends the employee's question together with the retrieved policy context to the LLM.

The LLM is instructed to:

* Use only the provided policy context.
* Not use outside knowledge.
* Answer factual questions only when the context contains the required information.
* Summarize relevant information for overview questions.
* Refuse when the policy does not contain the required information.

The vector database and Gemini embeddings are integrated separately through the application's vector-store layer, while LangChain handles the LLM interaction.

---

## 7. Grounding and Hallucination Control

The system uses multiple layers of protection against hallucination.

### Retrieval threshold

The similarity score is checked before generating an answer.

If the retrieved content is not sufficiently relevant, the request is refused.

### Restricted LLM context

The LLM receives only the retrieved HR policy content.

The prompt explicitly instructs Gemini not to use external knowledge.

### Safe refusal

If the policy does not contain the requested information, the system responds:

```text
The HR policy does not provide this information. Please contact HR.
```

No unsupported information is generated.

---

## 8. Overview Questions

The system distinguishes between normal factual questions and overview questions.

Examples of overview questions:

```text
What are the main types of leave available?
What are the main IT security policies?
What are the different data classifications?
```

For these questions, retrieving only the top few chunks may not provide enough information.

Therefore, when an overview question is detected, the system retrieves all chunks belonging to the relevant document and provides them as context to Gemini.

This allows Gemini to create a more complete summary while remaining grounded in the policy.

---

## 9. Citation Design

The system returns citations separately from the generated answer.

Example:

```json
{
  "question": "What is the minimum password length?",
  "answer": "The minimum password length is 12 characters.",
  "citations": [
    {
      "document": "it-security-policy.md",
      "section": "2. Accounts and passwords"
    }
  ]
}
```

For normal factual questions, the most relevant retrieved policy section is returned.

For overview questions, multiple relevant sections can be returned.

Citations are generated from the metadata stored with the retrieved chunks rather than being invented by the LLM.

---

## 10. API Response Structure

The `/ask` endpoint returns:

```json
{
  "question": "employee question",
  "answer": "grounded answer",
  "citations": [
    {
      "document": "policy document name",
      "section": "policy section"
    }
  ]
}
```

For an unsupported question:

```json
{
  "question": "Can I get a salary advance?",
  "answer": "The HR policy does not provide this information. Please contact HR.",
  "citations": []
}
```

---

## 11. Document Management

The backend maintains the document and vector-store relationship using document metadata.

Each stored chunk contains the document name.

This allows the system to:

* List uploaded documents.
* Delete all chunks belonging to a document.
* Retrieve all chunks belonging to a document.
* Generate citations using document and section metadata.

---

## 12. Why ChromaDB?

ChromaDB is used as the vector database because:

* It is lightweight.
* It is easy to run locally.
* It works well for a small HR policy knowledge base.
* It supports semantic similarity search.
* It stores metadata alongside vectors.
* It integrates easily with LangChain.

For the scale of this assignment, a local vector database is sufficient.

---

## 13. Why Gemini?

Gemini is used for both:

* Embedding generation
* Answer generation

This keeps the AI stack relatively simple.

The embedding model converts policy text and queries into vectors, while the Gemini chat model generates grounded responses.

---

## 14. Failure Handling

The system handles several failure cases.

### No relevant policy

The system refuses to answer.

### LLM refusal

If Gemini determines that the supplied context does not contain the required information, the API returns the refusal response and does not provide citations.

### Empty document

Documents that produce no usable chunks are not indexed.

### Missing API key

The backend checks for the required Gemini API key during initialization.

The API key is stored in an environment variable and is not committed to Git.

---

## 15. Security Considerations

The Gemini API key is stored in:

```text
.env
```

The `.env` file is excluded from Git using `.gitignore`.

Generated ChromaDB data and uploaded documents are also excluded from the Git repository.

The application should not expose the Gemini API key to the frontend.

The current admin authentication is intentionally simple because this project is an assignment prototype. A production system should use proper authentication, authorization, password hashing, session/token management, and audit logging.

---

## 16. Design Decisions and Trade-offs

### Top-k retrieval

The system currently retrieves two chunks for normal questions.

This keeps the context small and reduces unnecessary information being passed to the LLM.

### Overview retrieval

Overview questions use all chunks from the relevant document because a summary may require information from multiple sections.

### Relevance threshold

A similarity threshold is used to prevent unrelated policy chunks from being treated as evidence.

### Metadata-based citations

Citations are generated from retrieved metadata rather than generated by the LLM.

This makes the citations more reliable and explainable.

### LangChain

LangChain is used for LLM integration and orchestration while the application retains control over document processing, retrieval logic, relevance checking, and citation generation.

This provides a balance between using a standard RAG/LLM framework and keeping the application's behavior understandable.

---

## 17. Example End-to-End Flow

Employee asks:

```text
How many casual leave days can be carried forward?
```

The flow is:

```text
Question
   ↓
Gemini Embedding
   ↓
ChromaDB Similarity Search
   ↓
Relevant Leave Policy Chunk
   ↓
Relevance Check
   ↓
LangChain
   ↓
Gemini
   ↓
Grounded Answer
   ↓
Metadata-based Citation
   ↓
JSON Response
```

Result:

```json
{
  "question": "How many casual leave days can be carried forward?",
  "answer": "A maximum of 8 days of unused casual leave may be carried forward to the next calendar year.",
  "citations": [
    {
      "document": "leave-policy.md",
      "section": "4.1 Casual leave carry-forward"
    }
  ]
}
```

---

## 18. Future Improvements

For a production-ready version, the following improvements could be added:

* Proper admin authentication and role-based access control.
* PDF/DOCX document parsing.
* Better chunking strategies based on headings and semantic boundaries.
* Hybrid keyword + semantic retrieval.
* Reranking of retrieved chunks.
* More robust evaluation of retrieval quality.
* Persistent cloud vector database.
* Document versioning.
* Audit logs.
* Rate limiting.
* Automated tests.
* More detailed citation references, such as page numbers.
* Streaming responses.
* Monitoring and observability.


