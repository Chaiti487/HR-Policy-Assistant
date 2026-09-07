import os
from fastapi import FastAPI, UploadFile , File , HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from ingestion import save_uploaded_file
from chunking import create_chunks
from vector_store import VectorStore
from ask import QuestionRequest
from llm import generate_answer

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_POLICY_DIR = os.path.join(BASE_DIR,"sample_policies")

def load_default_policies():

    if not os.path.exists(DEFAULT_POLICY_DIR):
        print("Default policy directory not found.")
        return

    print("Checking default HR policies...")

    indexed_documents = set(
        vector_store.list_documents()
    )

    for filename in os.listdir(DEFAULT_POLICY_DIR):

        if not filename.endswith((".md", ".txt")):
            continue

        if filename in indexed_documents:
            print(f"Already indexed: {filename}")
            continue

        file_path = os.path.join(
            DEFAULT_POLICY_DIR,
            filename
        )

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:
            text = f.read()

        chunks = create_chunks(
            document_name=filename,
            text=text
        )

        vector_store.add_chunks(chunks)

        print(
            f"Indexed default policy: {filename} "
            f"({len(chunks)} chunks)"
        )

    print("Default policy check completed.")


app = FastAPI(
    title="HR Policy Assistent",
    description="An HR Police Assistant using RAG",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://hr-policy-assistant-alpha.vercel.app"
        ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

vector_store = VectorStore()
load_default_policies()

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

@app.get("/")
def home():
    return {
        "message":"HR Policy Assistent API is running!"
    }


@app.get("/health")
def health():
    return {
        "status":"healthy"
    }


#-------------------------------
# ADMIN LOGIN
#-------------------------------

@app.post("/admin/login")
def admin_login(username: str, password: str):

    if username != ADMIN_USERNAME or password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=401,
            detail="Invalid admin username or password."
        )

    return {
        "message": "Admin login successful.",
        "role": "admin"
    }

#-----------------------------
# ADMIN POLICY UPLOAD
#-----------------------------

@app.post("/admin/upload")
async def upload_policies(
    file: UploadFile = File(...)
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file was uploaded."
        )

    extension = os.path.splitext(
        file.filename
    )[1].lower()

    if extension not in {".txt", ".md"}:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.filename}"
        )

    content = await file.read()

    if not content:
        raise HTTPException(
            status_code=400,
            detail="The uploaded file is empty."
        )

    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=400,
            detail=f"{file.filename} must be UTF-8 encoded"
        )

    chunks = create_chunks(
        document_name=file.filename,
        text=text
    )

    vector_store.add_chunks(chunks)

    return {
        "message": "Policy uploaded and indexed successfully.",
        "document": file.filename,
        "chunks": len(chunks)
    }

@app.get("/admin/policies")
async def get_policies():

    return {
        "documents": vector_store.list_documents()
    }
#----------------------------
# EMPLOYEE QUESTION
#---------------------------


@app.post("/ask")
async def ask_question(request: QuestionRequest):

    results = vector_store.search(
        request.question,
        n_results=2
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    print("Retrieved distances:", distances)

    RELEVANCE_THRESHOLD = 0.6

    # No sufficiently relevant policy found
    if not distances or distances[0] > RELEVANCE_THRESHOLD:
        return {
            "question": request.question,
            "answer": (
                "The HR policy does not provide this information. "
                "Please contact HR."
            ),
            "citations": []
        }

    # Combine retrieved policy chunks
    overview_keywords = [
        "main",
        "overview",
        "summary",
        "summarize",
        "what are the",
        "different types",
        "types of"
    ]

    is_overview = any(
        keyword in request.question.lower()
        for keyword in overview_keywords
    )
    context = "\n\n".join(documents)
    if is_overview:
        overview_chunks = vector_store.get_document_chunks(
            metadatas[0]["document_name"]
        )

        documents = [
            chunk["text"]
            for chunk in overview_chunks
        ]

        metadatas = [
            chunk["metadata"]
            for chunk in overview_chunks
        ]

        context = "\n\n".join(documents)
    print("\n===== CONTEXT SENT TO GEMINI =====")
    print(context)
    print("===== END CONTEXT =====\n")

    # Generate grounded answer
    answer = generate_answer(
        question=request.question,
        context=context
    )

    # Detect whether Gemini refused to answer
    answer_lower = answer.lower()

    refusal_phrases = [
        "does not provide this information",
        "does not contain information",
        "does not contain any information",
        "cannot answer",
        "can't answer",
        "unable to answer"
    ]

    is_refusal = any(
        phrase in answer_lower
        for phrase in refusal_phrases
    )

    citations = []

    # Only return citations when Gemini actually answered
    if not is_refusal and metadatas:

        if is_overview:
            for metadata in metadatas:
                citation = {
                    "document": metadata.get("document_name", ""),
                    "section": metadata.get("section", "")
                }

                if citation not in citations:
                    citations.append(citation)

        else:
            citation = {
                "document": metadatas[0].get("document_name", ""),
                "section": metadatas[0].get("section", "")
            }

            citations.append(citation)

    return {
        "question": request.question,
        "answer": answer,
        "citations": citations
    }


@app.delete("/admin/policies/{document_name}")
async def delete_policy(document_name: str):

    documents = vector_store.list_documents()

    if document_name not in documents:
        raise HTTPException(
            status_code=404,
            detail="Policy document not found."
        )

    vector_store.delete_document(document_name)

    return {
        "message": "Policy deleted successfully.",
        "document": document_name
    }