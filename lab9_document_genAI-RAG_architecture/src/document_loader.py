"""
Document Loader Module

This module handles:
- Loading documents from the data folder
- Splitting documents into smaller chunks
- Preparing text for embedding

Why split documents?
- Embeddings work better on focused chunks
- LLMs have context limits
- More precise retrieval
"""

from pathlib import Path
from typing import List, Dict
import re


class Document:
    """
    Represents a single document or chunk
    
    Attributes:
        content: The actual text
        metadata: Information about the document (filename, chunk number, etc.)
    """
    def __init__(self, content: str, metadata: Dict = None):
        self.content = content
        self.metadata = metadata or {}
    
    def __repr__(self):
        return f"Document(content={self.content[:50]}..., metadata={self.metadata})"


class DocumentLoader:
    """
    Loads and processes documents from files
    """
    
    def __init__(self, data_dir: Path):
        """
        Initialize the document loader
        
        Args:
            data_dir: Path to the directory containing documents
        """
        self.data_dir = Path(data_dir)
        
        if not self.data_dir.exists():
            raise ValueError(f"Data directory not found: {self.data_dir}")
    
    def load_documents(self) -> List[Document]:
        """
        Load all text documents from the data directory
        
        Returns:
            List of Document objects
        """
        documents = []
        
        # Find all .txt files in the data directory
        txt_files = list(self.data_dir.glob("*.txt"))
        
        if not txt_files:
            print(f"⚠️  No .txt files found in {self.data_dir}")
            return documents
        
        print(f"📚 Found {len(txt_files)} documents to load...")
        
        for file_path in txt_files:
            try:
                # Read the file
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Create metadata
                metadata = {
                    'source': file_path.name,
                    'path': str(file_path),
                    'size': len(content)
                }
                
                # Create document object
                doc = Document(content=content, metadata=metadata)
                documents.append(doc)
                
                print(f"  ✓ Loaded: {file_path.name} ({len(content)} characters)")
                
            except Exception as e:
                print(f"  ✗ Error loading {file_path.name}: {e}")
        
        print(f"✅ Successfully loaded {len(documents)} documents\n")
        return documents
    
    def split_documents(self, documents: List[Document], 
                       chunk_size: int = 500, 
                       chunk_overlap: int = 50) -> List[Document]:
        """
        Split documents into smaller chunks
        
        Why? Large documents need to be broken into focused pieces.
        
        Args:
            documents: List of documents to split
            chunk_size: Maximum size of each chunk (in characters)
            chunk_overlap: Overlap between chunks (prevents cutting sentences)
        
        Returns:
            List of document chunks
        """
        chunks = []
        
        print(f"✂️  Splitting documents into chunks...")
        print(f"   Chunk size: {chunk_size} characters")
        print(f"   Overlap: {chunk_overlap} characters\n")
        
        for doc in documents:
            # Split the document into chunks
            text = doc.content
            doc_chunks = []
            
            # Start position in the document
            start = 0
            chunk_num = 0
            
            while start < len(text):
                # End position for this chunk
                end = start + chunk_size
                
                # Get the chunk
                chunk_text = text[start:end]
                
                # Try to break at a sentence boundary (look for '. ' or '\n')
                if end < len(text):
                    # Look for last period or newline in the chunk
                    last_period = chunk_text.rfind('. ')
                    last_newline = chunk_text.rfind('\n')
                    break_point = max(last_period, last_newline)
                    
                    if break_point > chunk_size * 0.5:  # Only break if it's not too early
                        chunk_text = chunk_text[:break_point + 1]
                        end = start + break_point + 1
                
                # Create metadata for this chunk
                chunk_metadata = doc.metadata.copy()
                chunk_metadata['chunk'] = chunk_num
                chunk_metadata['chunk_size'] = len(chunk_text)
                
                # Create the chunk document
                chunk_doc = Document(content=chunk_text.strip(), metadata=chunk_metadata)
                doc_chunks.append(chunk_doc)
                
                # Move to next chunk with overlap
                start = end - chunk_overlap
                chunk_num += 1
            
            chunks.extend(doc_chunks)
            print(f"  {doc.metadata['source']}: {len(doc_chunks)} chunks")
        
        print(f"\n✅ Created {len(chunks)} total chunks from {len(documents)} documents\n")
        return chunks


def clean_text(text: str) -> str:
    """
    Clean and normalize text
    
    This removes extra whitespace, special characters, etc.
    """
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    # Remove leading/trailing whitespace
    text = text.strip()
    return text


if __name__ == "__main__":
    # Test the document loader
    from config import Config
    
    loader = DocumentLoader(Config.DATA_DIR)
    
    # Load documents
    docs = loader.load_documents()
    
    # Split into chunks
    chunks = loader.split_documents(docs, chunk_size=300, chunk_overlap=50)
    
    # Show first chunk
    if chunks:
        print("📄 Example chunk:")
        print("-" * 50)
        print(chunks[0].content)
        print("-" * 50)
        print(f"Metadata: {chunks[0].metadata}")