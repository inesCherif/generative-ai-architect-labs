"""
Vector Store Module (using FAISS)

This module handles:
- Storing document embeddings
- Searching for similar documents
- Saving and loading the vector database

What is FAISS?
- FAISS = Facebook AI Similarity Search
- Extremely fast library for finding similar vectors
- Works locally (no cloud needed!)
- Free and open source

Think of it as a "Google for vectors" - you give it a query vector,
it finds the most similar document vectors instantly!
"""

import faiss
import numpy as np
import pickle
from pathlib import Path
from typing import List, Tuple
from document_loader import Document


class VectorStore:
    """
    Vector database using FAISS for similarity search
    """
    
    def __init__(self, dimension: int):
        """
        Initialize the vector store
        
        Args:
            dimension: The size of each embedding vector (e.g., 384 for MiniLM)
        """
        self.dimension = dimension
        
        # Create a FAISS index
        # We use IndexFlatL2 = exact search using L2 (Euclidean) distance
        # This is simple and accurate, perfect for learning!
        self.index = faiss.IndexFlatL2(dimension)
        
        # Store the actual documents
        # (FAISS only stores vectors, not the original text)
        self.documents: List[Document] = []
        
        print(f"🗄️  Initialized vector store (dimension: {dimension})")
    
    def add_documents(self, documents: List[Document], embeddings: np.ndarray):
        """
        Add documents and their embeddings to the vector store
        
        Args:
            documents: List of Document objects
            embeddings: numpy array of embeddings, shape (num_docs, dimension)
        """
        if len(documents) != len(embeddings):
            raise ValueError("Number of documents must match number of embeddings")
        
        if embeddings.shape[1] != self.dimension:
            raise ValueError(f"Embedding dimension {embeddings.shape[1]} doesn't match index dimension {self.dimension}")
        
        # Convert to float32 (FAISS requirement)
        embeddings_f32 = embeddings.astype('float32')
        
        # Add to FAISS index
        self.index.add(embeddings_f32)
        
        # Store documents
        self.documents.extend(documents)
        
        print(f"➕ Added {len(documents)} documents to vector store")
        print(f"   Total documents: {len(self.documents)}")
        print(f"   Index size: {self.index.ntotal}\n")
    
    def search(self, query_embedding: np.ndarray, top_k: int = 3) -> List[Tuple[Document, float]]:
        """
        Search for similar documents
        
        Args:
            query_embedding: The embedding of the search query
            top_k: Number of results to return
        
        Returns:
            List of (Document, score) tuples, sorted by relevance
            Lower scores = more similar (L2 distance)
        """
        # Ensure query is the right shape
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        # Convert to float32
        query_f32 = query_embedding.astype('float32')
        
        # Search
        # D = distances, I = indices
        distances, indices = self.index.search(query_f32, top_k)
        
        # Get the documents and their scores
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < len(self.documents):  # Make sure index is valid
                doc = self.documents[idx]
                # Convert L2 distance to similarity score (0-1, higher = more similar)
                # We use a simple conversion: similarity = 1 / (1 + distance)
                similarity = 1 / (1 + dist)
                results.append((doc, similarity))
        
        return results
    
    def save(self, path: Path):
        """
        Save the vector store to disk
        
        Args:
            path: Directory path to save the store
        """
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        
        # Save FAISS index
        index_file = path / "faiss.index"
        faiss.write_index(self.index, str(index_file))
        
        # Save documents using pickle
        docs_file = path / "documents.pkl"
        with open(docs_file, 'wb') as f:
            pickle.dump(self.documents, f)
        
        print(f"💾 Saved vector store to {path}")
    
    @classmethod
    def load(cls, path: Path, dimension: int) -> 'VectorStore':
        """
        Load a vector store from disk
        
        Args:
            path: Directory path where the store is saved
            dimension: Embedding dimension
        
        Returns:
            Loaded VectorStore instance
        """
        path = Path(path)
        
        # Load FAISS index
        index_file = path / "faiss.index"
        if not index_file.exists():
            raise FileNotFoundError(f"Index file not found: {index_file}")
        
        # Load documents
        docs_file = path / "documents.pkl"
        if not docs_file.exists():
            raise FileNotFoundError(f"Documents file not found: {docs_file}")
        
        # Create new instance
        store = cls(dimension)
        
        # Load index
        store.index = faiss.read_index(str(index_file))
        
        # Load documents
        with open(docs_file, 'rb') as f:
            store.documents = pickle.load(f)
        
        print(f"📂 Loaded vector store from {path}")
        print(f"   Documents: {len(store.documents)}")
        print(f"   Index size: {store.index.ntotal}\n")
        
        return store
    
    def get_stats(self):
        """Print statistics about the vector store"""
        print("\n" + "="*50)
        print("📊 VECTOR STORE STATISTICS")
        print("="*50)
        print(f"Dimension: {self.dimension}")
        print(f"Total documents: {len(self.documents)}")
        print(f"Index size: {self.index.ntotal}")
        print(f"Index type: {type(self.index).__name__}")
        print("="*50 + "\n")


if __name__ == "__main__":
    """
    Test the vector store
    """
    print("\n🧪 Testing Vector Store\n")
    
    # Create sample documents
    from document_loader import Document
    
    docs = [
        Document("The dog is playing in the park", {"id": 1}),
        Document("A cat is sleeping on the couch", {"id": 2}),
        Document("Machine learning is a subset of AI", {"id": 3}),
        Document("The puppy runs through the grass", {"id": 4}),
        Document("Neural networks are used in deep learning", {"id": 5}),
    ]
    
    # Create fake embeddings (normally you'd use the EmbeddingModel)
    # For testing, we'll create random embeddings
    dimension = 384
    embeddings = np.random.randn(len(docs), dimension).astype('float32')
    
    # Create and populate vector store
    store = VectorStore(dimension)
    store.add_documents(docs, embeddings)
    
    # Test search
    print("🔍 Testing search...")
    query_embedding = np.random.randn(dimension).astype('float32')
    results = store.search(query_embedding, top_k=3)
    
    print("\nTop 3 results:")
    for i, (doc, score) in enumerate(results, 1):
        print(f"{i}. Score: {score:.4f}")
        print(f"   Content: {doc.content[:50]}...")
        print(f"   Metadata: {doc.metadata}\n")
    
    # Test save/load
    print("💾 Testing save/load...")
    test_path = Path("test_vector_db")
    store.save(test_path)
    
    loaded_store = VectorStore.load(test_path, dimension)
    loaded_store.get_stats()
    
    # Cleanup
    import shutil
    shutil.rmtree(test_path)
    print("✅ Test completed!")