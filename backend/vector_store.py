# import os
# import chromadb
# from sentence_transformers import SentenceTransformer


# CHROMA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),"chroma_db")

# COLLECTION_NAME = "hr_policies"


# class VectorStore:

#     def __init__(self):

#         # Create/load the chromaDB database
#         self.client = chromadb.PersistentClient(
#             path=CHROMA_PATH
#         )

#         #Create/load our collection
#         self.collection = self.client.get_or_create_collection(
#             name = COLLECTION_NAME,
#             metadata={
#                 "hnsw:space": "cosine"
#             }
#         )

#         # Load the embedding model
#         print("Loading embedding model...")

#         self.embedding_model = SentenceTransformer(
#             "all-MiniLM-L6-v2"
#         )

#         print("Embedding model loaded!")

#     def add_chunks(self, chunks):

#         if not chunks:
#             return

#         documents = []
#         embeddings = []
#         metadatas = []
#         ids = []

#         for chunk in chunks:

#             text = chunk["text"]

#             # Convert text into embedding
#             embedding = self.embedding_model.encode(
#                 text,
#                 normalize_embeddings= True
#             ).tolist()

#             documents.append(text)
#             embeddings.append(embedding)
#             metadatas.append(chunk["metadata"])
#             ids.append(chunk["id"])

#         # Store everything in ChromaDB
#         self.collection.upsert(
#             documents=documents,
#             embeddings=embeddings,
#             metadatas=metadatas,
#             ids=ids
#         )

#     def delete_document(self, document_name):
#         self.collection.delete(
#             where={
#                 "document_name": document_name
#             }
#         )

#     def list_documents(self):
#         data = self.collection.get(
#             include=["metadatas"]
#         )

#         documents = set()

#         for metadata in data["metadatas"]:
#             if metadata and "document_name" in metadata:
#                 documents.add(metadata["document_name"])

#         return sorted(documents)

#     def search(self, query, n_results=3):

#         # Convert question into embedding
#         query_embedding = self.embedding_model.encode(
#             query,
#             normalize_embeddings=True
#         ).tolist()

#         #Check whether database has data
#         total_documents = self.collection.count()

#         if total_documents == 0:

#             return {
#                 "documents": [[]],
#                 "metadatas": [[]],
#                 "distances": [[]]
#             }

#         n_results = min(
#             n_results,
#             total_documents
#         )

#         # Search ChromaDB
#         return self.collection.query(
#             query_embeddings=[query_embedding],
#             n_results=n_results,
#             include=[
#                 "documents",
#                 "metadatas",
#                 "distances"
#             ]
#         )

import os
import chromadb
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

CHROMA_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "chroma_db"
)

COLLECTION_NAME = "hr_policies"
EMBEDDING_MODEL = "gemini-embedding-001"


class VectorStore:

    def __init__(self):

        # Gemini client for embeddings
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set.")

        self.client = genai.Client(
            api_key=api_key
        )

        # ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=CHROMA_PATH
        )

        self.collection = self.chroma_client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={
                "hnsw:space": "cosine"
            }
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

        embeddings = self.create_embeddings(
            documents
        )

        self.collection.upsert(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )

        print(
            f"Added {len(documents)} chunks to ChromaDB."
        )


    def delete_document(self, document_name):

        self.collection.delete(
            where={
                "document_name": document_name
            }
        )


    def list_documents(self):

        data = self.collection.get(
            include=["metadatas"]
        )

        documents = set()

        for metadata in data["metadatas"]:

            if metadata and "document_name" in metadata:

                documents.add(
                    metadata["document_name"]
                )

        return sorted(documents)


    def search(self, query, n_results=3):

        query_embedding = self.create_embeddings(
            [query]
        )[0]

        total_documents = self.collection.count()

        if total_documents == 0:

            return {
                "documents": [[]],
                "metadatas": [[]],
                "distances": [[]]
            }

        n_results = min(
            n_results,
            total_documents
        )

        return self.collection.query(
            query_embeddings=[
                query_embedding
            ],
            n_results=n_results,
            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )