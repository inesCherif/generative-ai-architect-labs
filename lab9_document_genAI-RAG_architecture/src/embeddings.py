"""
Embeddings Module

This module handles:
- Converting text to numerical vectors (embeddings)
- Using sentence-transformers (local, free, fast!)

What are embeddings?
- Embeddings convert text into lists of numbers
- Similar text = similar numbers
- This enables "semantic search" - finding meaning, not just keywords!

Example:
"dog" → [0.2, 0.8, -0.3, ...]
"puppy" → [0.25, 0.82, -0.28, ...] (similar!)
"car" → [-0.6, 0.1, 0.9, ...] (different!)
"""

from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np


class EmbeddingModel:
    """
    Wrapper for the embedding model
    
    This uses sentence-transformers, which runs locally (no API needed!)
    """
    
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the embedding model
        
        Args:
            model_name: Name of the sentence-transformer model
                       Default is a fast, lightweight model (384 dimensions)
        """
        print(f"🔧 Loading embedding model: {model_name}")
        print("   (This might take a moment on first run...)")
        
        try:
            self.model = SentenceTransformer(model_name)
            self.dimension = self.model.get_sentence_embedding_dimension()
            print(f"✅ Model loaded! Embedding dimension: {self.dimension}\n")
        except Exception as e:
            print(f"❌ Error loading model: {e}")
            raise
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Convert a single text string to an embedding vector
        
        Args:
            text: The text to embed
        
        Returns:
            numpy array of shape (dimension,)
        
        Example:
            >>> embedder = EmbeddingModel()
            >>> vector = embedder.embed_text("Hello world")
            >>> print(vector.shape)
            (384,)
        """
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding
    
    def embed_documents(self, texts: List[str], show_progress: bool = True) -> np.ndarray:
        """
        Convert multiple texts to embeddings (batch processing)
        
        This is more efficient than calling embed_text() multiple times!
        
        Args:
            texts: List of text strings to embed
            show_progress: Whether to show progress bar
        
        Returns:
            numpy array of shape (num_texts, dimension)
        
        Example:
            >>> embedder = EmbeddingModel()
            >>> texts = ["Hello", "World", "AI is cool"]
            >>> vectors = embedder.embed_documents(texts)
            >>> print(vectors.shape)
            (3, 384)
        """
        print(f"🔄 Creating embeddings for {len(texts)} documents...")
        
        embeddings = self.model.encode(
            texts,
            convert_to_numpy=True,
            show_progress_bar=show_progress,
            batch_size=32  # Process 32 documents at a time
        )
        
        print(f"✅ Created embeddings: shape {embeddings.shape}\n")
        return embeddings
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings
        
        Cosine similarity ranges from -1 to 1:
        - 1 = identical
        - 0 = unrelated
        - -1 = opposite
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
        
        Returns:
            Similarity score (0 to 1)
        """
        # Normalize the vectors
        norm1 = embedding1 / np.linalg.norm(embedding1)
        norm2 = embedding2 / np.linalg.norm(embedding2)
        
        # Compute dot product (cosine similarity for normalized vectors)
        similarity = np.dot(norm1, norm2)
        
        return float(similarity)


def test_embeddings():
    """
    Test function to demonstrate embeddings
    """
    print("\n" + "="*60)
    print("🧪 TESTING EMBEDDINGS")
    print("="*60 + "\n")
    
    # Initialize model
    embedder = EmbeddingModel()
    
    # Test texts
    texts = [
        "The dog is playing in the park",
        "A puppy runs through the grass",
        "The car is parked in the garage",
        "What is machine learning?",
        "How does AI work?"
    ]
    
    print("📝 Test texts:")
    for i, text in enumerate(texts, 1):
        print(f"   {i}. {text}")
    print()
    
    # Create embeddings
    embeddings = embedder.embed_documents(texts, show_progress=False)
    
    # Compare similarities
    print("🔍 Similarity Matrix:")
    print("   (1.00 = identical, 0.00 = unrelated)\n")
    
    # Print header
    print("     ", end="")
    for i in range(len(texts)):
        print(f"  #{i+1}  ", end="")
    print()
    
    # Print similarity matrix
    for i in range(len(texts)):
        print(f"#{i+1}  ", end="")
        for j in range(len(texts)):
            sim = embedder.compute_similarity(embeddings[i], embeddings[j])
            print(f" {sim:.2f}  ", end="")
        print(f"  {texts[i][:30]}...")
    
    print("\n💡 Observations:")
    print("   - Texts 1 & 2 (dog/puppy) should have HIGH similarity")
    print("   - Texts 4 & 5 (ML/AI) should have HIGH similarity")
    print("   - Text 3 (car) should have LOW similarity with others")
    print()


if __name__ == "__main__":
    test_embeddings()