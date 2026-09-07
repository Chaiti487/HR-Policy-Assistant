import os
from google import genai
from google.genai import types
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.embeddings import Embeddings

load_dotenv()

CHROMA_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "chroma_db"
)

COLLECTION_NAME = "hr_policies"
EMBEDDING_MODEL = "gemini-embedding-001"

class GeminiEmbeddings(Embeddings):

    def __init__(self,client):
        self.client = client

    def embed_documents(self, texts):
        response = self.client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=texts,
            config=types.EmbedContentConfig(
                output_dimensionality=768
            )
        )
        return [
            embedding.values
            for embedding in response.embeddings
        ]

    def embed_query(self, text):
        return self.embed_documents([text])[0]


class VectorStore:

    def __init__(self):

        # Gemini client for embeddings
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set.")

        self.client = genai.Client(
            api_key=api_key
        )

        # LangChain embedding wrapper
        self.embedding_function = GeminiEmbeddings(
            self.client
        )

        # LangChain Chroma
        self.vector_store = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=self.embedding_function,
            persist_directory=CHROMA_PATH
        )

        print("Gemini embedding service initialized!")
        print("ChromaDB initialized!")


    def create_embeddings(self, texts):

        if not texts:
            return []

        response = self.client.models.embed_content(
            model=EMBEDDING_MODEL,
            contents=texts,
            config=types.EmbedContentConfig(
                output_dimensionality=768
            )
        )

        return [
            embedding.values
            for embedding in response.embeddings
        ]


    def add_chunks(self, chunks):

        if not chunks:
            return

        documents = [
            chunk["text"]
            for chunk in chunks
        ]

        metadatas = [
            chunk["metadata"]
            for chunk in chunks
        ]

        ids = [
            chunk["id"]
            for chunk in chunks
        ]

        print(
            f"Creating embeddings for {len(documents)} chunks..."
        )

        self.vector_store.add_texts(
            texts=documents,
            metadatas=metadatas,
            ids=ids
        )

        print(
            f"Added {len(documents)} chunks to ChromaDB."
        )


    def delete_document(self, document_name):

        self.vector_store.delete(
            where={
                "document_name": document_name
            }
        )


    def list_documents(self):

        data = self.vector_store.get(
            include=["metadatas"]
        )

        documents = set()

        for metadata in data["metadatas"]:

            if metadata and "document_name" in metadata:

                documents.add(
                    metadata["document_name"]
                )

        return sorted(documents)

    def get_document_chunks(self, document_name):
        data = self.vector_store.get(
            where={"document_name": document_name},
            include=["documents", "metadatas"]
        )

        chunks = []

        for document, metadata in zip(
            data["documents"],
            data["metadatas"]
        ):
            chunks.append({
                "text": document,
                "metadata": metadata
            })

        chunks.sort(
            key=lambda chunk: chunk["metadata"].get(
            "chunk_index", 0
            )
        )

        return chunks


    def search(self, query, n_results=3):

        results = self.vector_store.similarity_search_with_score(
            query,
            k=n_results
        )

        if not results:

            return {
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]]
            }

        documents = []
        metadatas = []
        distances = []

        for document, distance in results:
            documents.append(document.page_content)
            metadatas.append(document.metadata)
            distances.append(distance)

        return {
            "documents": [documents],
            "metadatas": [metadatas],
            "distances": [distances]
        }