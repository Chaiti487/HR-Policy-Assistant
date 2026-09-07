import chromadb
from sentence_transformers import SentenceTransformer


CHROMA_PATH = "./chroma_db"

COLLECTION_NAME = "hr_policies"


class VectorStore:

    def __init__(self):

        # Create/load the chromaDB database
        self.client = chromadb.PersistentClient(
            path=CHROMA_PATH
        )

        #Create/load our collection
        self.collection = self.client.get_or_create_collection(
            name = COLLECTION_NAME,
            metadata={
                "hnsw:space": "cosine"
            }
        )

        # Load the embedding model
        print("Loading embedding model...")

        self.embedding_model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        print("Embedding model loaded!")

    def add_chunks(self, chunks):

        if not chunks:
            return

        documents = []
        embeddings = []
        metadatas = []
        ids = []

        for chunk in chunks:

            text = chunk["text"]

            # Convert text into embedding
            embedding = self.embedding_model.encode(
                text,
                normalize_embeddings= True
            ).tolist()

            documents.append(text)
            embeddings.append(embedding)
            metadatas.append(chunk["metadata"])
            ids.append(chunk["id"])

        # Store everything in ChromaDB
        self.collection.upsert(
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
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
                documents.add(metadata["document_name"])

        return sorted(documents)

    def search(self, query, n_results=3):

        # Convert question into embedding
        query_embedding = self.embedding_model.encode(
            query,
            normalize_embeddings=True
        ).tolist()

        #Check whether database has data
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

        # Search ChromaDB
        return self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=[
                "documents",
                "metadatas",
                "distances"
            ]
        )

        