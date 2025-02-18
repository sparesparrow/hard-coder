"""Vector database operations using ChromaDB."""

import os
from pathlib import Path
from typing import List, Optional, Dict, Any

import chromadb
from chromadb.config import Settings
from pydantic import BaseModel


class SearchResult(BaseModel):
    """Search result from vector database."""
    document: str
    metadata: Dict[str, Any]
    distance: float


class VectorManager:
    """Manages vector database operations."""
    
    def __init__(self, persist_directory: str = "./mcp_context_db"):
        """Initialize vector database manager."""
        self.db = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False
            )
        )
        
    def get_or_create_collection(
        self, name: str, metadata: Optional[Dict[str, Any]] = None
    ) -> chromadb.Collection:
        """Get or create a collection in the vector database."""
        return self.db.get_or_create_collection(
            name=name,
            metadata=metadata or {}
        )
        
    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> None:
        """Add documents to a collection."""
        collection = self.get_or_create_collection(collection_name)
        
        if ids is None:
            # Generate IDs based on document content hash
            import hashlib
            ids = [
                hashlib.sha256(doc.encode()).hexdigest()[:16]
                for doc in documents
            ]
            
        collection.add(
            documents=documents,
            metadatas=metadatas or [{}] * len(documents),
            ids=ids
        )
        
    def search(
        self,
        collection_name: str,
        query: str,
        n_results: int = 5,
        where: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Search for documents similar to query."""
        collection = self.get_or_create_collection(collection_name)
        
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where
        )
        
        search_results = []
        for i in range(len(results["documents"][0])):
            search_results.append(SearchResult(
                document=results["documents"][0][i],
                metadata=results["metadatas"][0][i],
                distance=results["distances"][0][i]
            ))
            
        return search_results
        
    def delete_collection(self, name: str) -> None:
        """Delete a collection from the vector database."""
        self.db.delete_collection(name)
        
    def list_collections(self) -> List[str]:
        """List all collections in the vector database."""
        return [col.name for col in self.db.list_collections()] 