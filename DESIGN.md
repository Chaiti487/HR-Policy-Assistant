````markdown
# System Design

## 1. Problem

The goal is to build an HR Policy Assistant that can answer employee questions using company HR policy documents.

The system must avoid generating unsupported policy information.

## 2. RAG Approach

The application uses Retrieval-Augmented Generation (RAG).

Instead of sending the entire policy collection directly to the LLM, the system first retrieves relevant policy sections. These sections are then provided to Gemini as context.

### RAG Flow

```text
┌─────────────────────────┐
│    Admin Uploads        │
│    HR Policy Documents  │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│    File Validation      │
│    & Text Extraction    │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│   Section Detection     │
│       & Chunking        │
│   100 words / 20 overlap│
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│      Embeddings         │
│   all-MiniLM-L6-v2      │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│       ChromaDB          │
│ Text + Embeddings +     │
│       Metadata          │
└────────────┬────────────┘
             │
             │ Employee Question
             ↓
┌─────────────────────────┐
│   Question Embedding    │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│   Similarity Search     │
│       Top 3 Chunks      │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│   Relevance Threshold   │
│         Check           │
└───────┬─────────┬───────┘
        │         │
   Relevant     Not Relevant
        │         │
        ↓         ↓
┌──────────────┐  ┌──────────────────────┐
│    Gemini    │  │     Safe Refusal     │
│   Generate   │  │  "Policy does not    │
│    Answer    │  │   provide this..."   │
└──────┬───────┘  └──────────────────────┘
       ↓
┌─────────────────────────┐
│   Answer + Citations    │
│    Document + Section   │
└─────────────────────────┘
````

## 3. High-Level Design (HLD)

### 3.1 System Architecture

The system consists of the following major components:

1. **Employee Portal**

   * Provides the interface for employees to ask HR policy questions.
   * Displays generated answers and policy citations.

2. **Admin Portal**

   * Allows administrators to log in.
   * Allows uploading multiple policy documents.
   * Displays indexed policy documents.
   * Allows administrators to delete policy documents.

3. **FastAPI Backend**

   * Provides REST APIs.
   * Handles document processing and question answering.
   * Connects the frontend with the RAG pipeline.

4. **Document Processing Layer**

   * Validates uploaded files.
   * Extracts text.
   * Detects policy sections.
   * Creates chunks.

5. **Embedding Model**

   * Uses `all-MiniLM-L6-v2`.
   * Converts policy chunks and questions into embeddings.

6. **ChromaDB**

   * Stores embeddings, policy text, and metadata.
   * Performs similarity search.

7. **Gemini**

   * Generates the final answer using retrieved policy context.

### 3.2 HLD Architecture

```text
                    ┌─────────────────────┐
                    │    Employee Portal  │
                    └──────────┬──────────┘
                               │
                               │ Question
                               ↓
                    ┌─────────────────────┐
                    │    FastAPI Backend  │
                    └──────────┬──────────┘
                               │
                               ↓
                    ┌─────────────────────┐
                    │   RAG Pipeline      │
                    └──────────┬──────────┘
                               │
                 ┌─────────────┴─────────────┐
                 ↓                           ↓
        ┌─────────────────┐         ┌─────────────────┐
        │ Sentence        │         │    ChromaDB     │
        │ Transformer     │────────→│ Vector Storage  │
        └─────────────────┘         └────────┬────────┘
                                             │
                                             │ Relevant Chunks
                                             ↓
                                    ┌─────────────────┐
                                    │      Gemini     │
                                    │       LLM       │
                                    └────────┬────────┘
                                             │
                                             ↓
                                    ┌─────────────────┐
                                    │ Answer + Source │
                                    │   Citations     │
                                    └─────────────────┘


                    ┌─────────────────────┐
                    │     Admin Portal    │
                    └──────────┬──────────┘
                               │
                               │ Upload
                               ↓
                    ┌─────────────────────┐
                    │    FastAPI Backend  │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │ Document Processing │
                    └──────────┬──────────┘
                               ↓
                    ┌─────────────────────┐
                    │    ChromaDB         │
                    └─────────────────────┘
```

### 3.3 Data Flow

There are two main flows.

#### Document Ingestion Flow

```text
Admin
  ↓
Upload Policy
  ↓
File Validation
  ↓
Text Extraction
  ↓
Section Detection
  ↓
Chunking
  ↓
Embedding Generation
  ↓
ChromaDB
```

#### Question Answering Flow

```text
Employee Question
  ↓
Question Embedding
  ↓
ChromaDB Similarity Search
  ↓
Top 3 Relevant Chunks
  ↓
Relevance Threshold
  ↓
Gemini
  ↓
Answer
  ↓
Backend-generated Citations
  ↓
Employee Portal
```

## 4. Low-Level Design (LLD)

### 4.1 Backend Modules

The backend is divided into small modules with separate responsibilities.

```text
backend/
│
├── main.py
├── ingestion.py
├── chunking.py
├── vector_store.py
├── llm.py
├── ask.py
└── requirements.txt
```

### 4.2 `main.py`

`main.py` is the main FastAPI application.

Responsibilities:

* Create the FastAPI application
* Configure CORS
* Initialize the vector store
* Load default policies
* Provide API endpoints
* Handle admin operations
* Handle employee questions

Main endpoints:

```text
POST   /admin/login
POST   /admin/upload
GET    /admin/policies
DELETE /admin/policies/{document_name}
POST   /ask
GET    /health
```

### 4.3 `ingestion.py`

Responsible for validating and processing uploaded policy files.

Main responsibilities:

* Validate file name
* Validate file extension
* Read uploaded file
* Decode UTF-8 text
* Check for empty files
* Prepare policy content for indexing

Currently supported formats:

```text
.txt
.md
```

### 4.4 `chunking.py`

Responsible for converting policy text into searchable chunks.

Main functions:

```text
split_into_sections()
split_into_chunks()
create_chunks()
```

The process is:

```text
Policy Text
    ↓
Markdown Heading Detection
    ↓
Policy Sections
    ↓
100 Word Chunks
    ↓
20 Word Overlap
    ↓
Chunk Metadata
```

Each chunk contains:

```text
id
text
document_name
section
chunk_index
```

### 4.5 `vector_store.py`

Responsible for embedding generation and ChromaDB operations.

Main responsibilities:

* Initialize ChromaDB
* Load `all-MiniLM-L6-v2`
* Generate embeddings
* Store policy chunks
* Search similar chunks
* List indexed documents
* Delete policy documents

The vector store uses cosine distance.

```text
Policy Chunk
     ↓
Sentence Transformer
     ↓
Embedding Vector
     ↓
ChromaDB
```

For a question:

```text
Question
   ↓
Embedding
   ↓
ChromaDB Search
   ↓
Top 3 Results
```

### 4.6 `llm.py`

Responsible for communication with Gemini.

The module:

1. Receives the employee question.
2. Receives retrieved policy context.
3. Creates a grounded prompt.
4. Sends the prompt to Gemini.
5. Returns the generated answer.

Gemini is instructed to use only the retrieved policy context.

### 4.7 `ask.py`

Contains the request model used for employee questions.

The employee question is received as:

```json
{
  "question": "What is the minimum password length?"
}
```

The request is then passed to the retrieval and generation pipeline.

### 4.8 Retrieval Logic

The retrieval process is:

```text
Employee Question
       ↓
Generate Question Embedding
       ↓
ChromaDB Similarity Search
       ↓
Retrieve Top 3 Chunks
       ↓
Check Similarity Distance
       ↓
Is Result Relevant?
      / \
    Yes  No
     ↓    ↓
 Gemini  Safe Refusal
```

A relevance threshold is used to reject clearly unrelated questions.

### 4.9 Citation Generation

Citations are generated by the backend rather than Gemini.

The retrieved metadata contains:

```text
document_name
section
chunk_index
```

The backend uses the document name and section to create the citation.

Example:

```json
{
  "document": "it-security-policy.md",
  "section": "2. Accounts and passwords"
}
```

This prevents the LLM from creating false citations.

## 5. Data Model

Each indexed chunk is logically represented as:

```text
Chunk
├── id
├── text
└── metadata
    ├── document_name
    ├── section
    └── chunk_index
```

ChromaDB stores the chunk text, embedding vector, and metadata.

## 6. API Design

### POST /admin/login

Used for administrator authentication.

### POST /admin/upload

Used to upload and index one or more policy documents.

### GET /admin/policies

Returns the list of currently indexed policy documents.

### DELETE /admin/policies/{document_name}

Removes all chunks belonging to the specified policy document.

### POST /ask

Accepts an employee question and returns:

```json
{
  "question": "...",
  "answer": "...",
  "citations": []
}
```

### GET /health

Returns:

```json
{
  "status": "healthy"
}
```

## 7. Error Handling

The system handles common errors such as:

* Empty questions
* Empty uploaded files
* Unsupported file formats
* Invalid UTF-8 files
* Invalid admin credentials
* Missing policy documents
* No relevant policy information
* Temporary Gemini service failures

When relevant policy information cannot be found, the system uses the safe refusal response instead of generating an unsupported answer.

## 8. Security Considerations

The current implementation includes basic administrator login functionality.

The Gemini API key is stored in an environment variable:

```text
GEMINI_API_KEY
```

The `.env` file is excluded from Git using `.gitignore`.

The API key must never be committed to the GitHub repository.

For production, stronger authentication and authorization should be implemented.

## 9. Design Trade-offs

### Local Embeddings

Advantages:

* No additional embedding API cost
* Suitable for a small HR policy collection
* Keeps embedding generation local

### ChromaDB

Advantages:

* Simple setup
* Persistent local storage
* Suitable for a small-to-medium document collection
* Easy semantic similarity search

### Gemini

Advantages:

* Strong natural language generation
* Simple API integration
* Suitable for generating concise policy answers

### Simple Chunking

The current 100-word chunk size and 20-word overlap provide a simple approach suitable for the small policy documents used in this assignment.

For larger documents, more advanced chunking strategies could provide better retrieval quality.

## 10. Future Improvements

Possible future improvements include:

* PDF and DOCX support
* Stronger administrator authentication
* Role-based access control
* Policy versioning
* Better chunking for large documents
* Hybrid keyword + semantic search
* Reranking
* Automated evaluation
* Audit logging
* Production deployment with HTTPS

## 11. Summary

The system follows a simple and explainable architecture:

```text
Admin Upload
     ↓
Process & Chunk
     ↓
Generate Embeddings
     ↓
Store in ChromaDB
     ↓
Employee Question
     ↓
Semantic Retrieval
     ↓
Relevance Check
     ↓
Gemini
     ↓
Grounded Answer
     ↓
Backend-generated Citation
```

The main design principle is:

> Retrieve first → Ground the answer → Generate the response → Cite the source




