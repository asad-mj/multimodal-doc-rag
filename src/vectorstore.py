import os
import chromadb
from typing import List, Dict, Any
from src.schemas import DocumentChunk
from src.config import settings

class VectorStoreManager:
    """Manages document embeddings and similarity search inside ChromaDB."""
    
    def __init__(self, persist_dir: str = settings.CHROMA_PERSIST_DIR):
        os.makedirs(persist_dir, exist_ok=True)
        self.client = chromadb.PersistentClient(path=persist_dir)
        self.collection = self.client.get_or_create_collection(
            name=settings.COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"}
        )

    def add_chunks(self, chunks: List[DocumentChunk]):
        if not chunks:
            return 0
        
        ids = [chunk.chunk_id for chunk in chunks]
        documents = [f"[{chunk.content_type.upper()}]\n{chunk.content}" for chunk in chunks]
        metadatas = [
            {
                "source_document": chunk.source_document,
                "page_number": chunk.page_number,
                "content_type": chunk.content_type
            }
            for chunk in chunks
        ]

        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        return len(chunks)

    def similarity_search(self, query: str, top_k: int = 4) -> List[Dict[str, Any]]:
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            include=["documents", "metadatas", "distances"]
        )

        formatted_results = []
        if results and "documents" in results and results["documents"]:
            docs = results["documents"][0]
            metas = results["metadatas"][0]
            distances = results["distances"][0]

            for doc, meta, dist in zip(docs, metas, distances):
                # Cosine distance to similarity conversion
                similarity = max(0.0, min(1.0, 1.0 - float(dist)))
                formatted_results.append({
                    "content": doc,
                    "metadata": meta,
                    "similarity": round(similarity, 4)
                })

        return formatted_results
